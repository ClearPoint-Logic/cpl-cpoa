"""Manage phase — the HR Console.

Day-to-day lifecycle actions on onboarded agents. Each action writes a real
hash-chained evidence event (using the same event chain rules as Onboarding)
so the personnel file stays continuous from intake through every subsequent
status change.

Actions are workforce-framed:

- **Place on leave** (pause)        → ``agent_placed_on_leave``
- **Return from leave** (resume)    → ``agent_returned_from_leave``
- **Manager handoff** (transfer)    → ``ownership_transferred``
- **Role change** (scope update)    → ``scope_updated``

State is held in a small lifecycle store keyed by ``candidate_agent_id``;
events are appended to a per-agent log so the chain is verifiable. In a
customer deployment this would be the same Firestore that holds the
onboarding runs; for the demo we keep an in-memory layer with a Firestore
adapter ready behind the same interface.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

from cpoa.schemas import Actor, EvidenceEvent, Subject
from cpoa.services import hashing
from cpoa.services.signing import get_signer

LifecycleStatus = Literal["active", "on_leave", "returning"]

Action = Literal[
    "place_on_leave",
    "return_from_leave",
    "manager_handoff",
    "role_change",
]

# Map workforce-framed action keys to the canonical evidence event_type that
# lands in the hash chain. The event_type strings are stable for downstream
# consumers (audit pipelines, evidence verifiers).
_ACTION_EVENT_TYPE: dict[str, str] = {
    "place_on_leave": "manage.placed_on_leave",
    "return_from_leave": "manage.returned_from_leave",
    "manager_handoff": "manage.ownership_transferred",
    "role_change": "manage.scope_updated",
}


@dataclass
class LifecycleState:
    """Current management state of one onboarded agent."""

    candidate_agent_id: str
    status: LifecycleStatus = "active"
    owner_email: str | None = None
    notes: str = ""
    updated_at: str = ""
    event_log: list[dict] = field(default_factory=list)
    last_event_hash: str | None = None
    # Remediation ledger: per-phase records of flagged items a human resolved.
    # Each entry: {phase, ref_id, title, summary, event_id, actor, resolved_at}.
    remediations: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "candidate_agent_id": self.candidate_agent_id,
            "status": self.status,
            "owner_email": self.owner_email,
            "notes": self.notes,
            "updated_at": self.updated_at,
            "event_log": list(self.event_log),
            "last_event_hash": self.last_event_hash,
            "remediations": list(self.remediations),
        }

    @classmethod
    def from_dict(cls, d: dict) -> LifecycleState:
        """Rehydrate a state from its stored form (the inverse of ``to_dict``)."""
        return cls(
            candidate_agent_id=d["candidate_agent_id"],
            status=d.get("status", "active"),
            owner_email=d.get("owner_email"),
            notes=d.get("notes", ""),
            updated_at=d.get("updated_at", ""),
            event_log=list(d.get("event_log") or []),
            last_event_hash=d.get("last_event_hash"),
            remediations=list(d.get("remediations") or []),
        )


# Lifecycle store. In-memory by default (also the test path); Firestore when
# CPOA_STORAGE_MODE=firestore, so the per-agent personnel file (status, owner,
# event chain, remediation ledger) survives Cloud Run scale-to-zero cold starts.
# Both backends speak the same get/save/all/clear interface over plain dicts
# (LifecycleState.to_dict / from_dict handle (de)serialization), mirroring the
# run store in app/api/store.py.


class _MemoryLifecycleStore:
    """In-memory lifecycle store — the default and the test path."""

    mode = "local"

    def __init__(self) -> None:
        self._d: dict[str, dict] = {}

    def get(self, candidate_agent_id: str) -> dict | None:
        return self._d.get(candidate_agent_id)

    def save(self, candidate_agent_id: str, payload: dict) -> None:
        self._d[candidate_agent_id] = payload

    def all(self) -> list[dict]:
        return list(self._d.values())

    def clear(self) -> None:
        self._d.clear()


class _FirestoreLifecycleStore:
    """Firestore-backed lifecycle store: one document per agent holding the
    state as a single JSON string (sidesteps Firestore's nested-array limits —
    the event log is a list of dicts), so the personnel file is durable across
    scale-to-zero instances."""

    mode = "firestore"

    def __init__(self, project: str | None = None, collection: str = "cpoa_lifecycle") -> None:
        from google.cloud import firestore

        self._client = firestore.Client(project=project)
        self._collection = collection

    def get(self, candidate_agent_id: str) -> dict | None:
        doc = self._client.collection(self._collection).document(candidate_agent_id).get()
        if not doc.exists:
            return None
        return json.loads(doc.to_dict()["json"])

    def save(self, candidate_agent_id: str, payload: dict) -> None:
        self._client.collection(self._collection).document(candidate_agent_id).set(
            {"json": json.dumps(payload)}
        )

    def all(self) -> list[dict]:
        return [json.loads(d.to_dict()["json"]) for d in self._client.collection(self._collection).stream()]

    def clear(self) -> None:
        for d in self._client.collection(self._collection).stream():
            d.reference.delete()


def _make_store():
    """Build the configured lifecycle store, falling back to in-memory on any
    error so the demo never hard-fails on a Firestore hiccup."""
    if os.environ.get("CPOA_STORAGE_MODE") == "firestore":
        try:
            return _FirestoreLifecycleStore(os.environ.get("GOOGLE_CLOUD_PROJECT"))
        except Exception:  # noqa: BLE001 — fall back so the demo never hard-fails
            return _MemoryLifecycleStore()
    return _MemoryLifecycleStore()


_store: _MemoryLifecycleStore | _FirestoreLifecycleStore | None = None


def _get_store() -> _MemoryLifecycleStore | _FirestoreLifecycleStore:
    global _store
    if _store is None:
        _store = _make_store()
    return _store


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def get_state(candidate_agent_id: str) -> LifecycleState:
    """Load one agent's lifecycle state, or a fresh default if none exists yet.

    A never-touched agent returns a default ``active`` state that is *not*
    persisted — only real actions (apply_action / advance_phase /
    record_remediation) write to the store.
    """
    raw = _get_store().get(candidate_agent_id)
    if raw is None:
        return LifecycleState(candidate_agent_id=candidate_agent_id, updated_at=_now_iso())
    return LifecycleState.from_dict(raw)


def _save(state: LifecycleState) -> None:
    """Persist a state back to the configured store."""
    _get_store().save(state.candidate_agent_id, state.to_dict())


def save_state(state: LifecycleState) -> None:
    """Persist a caller-mutated state (e.g. Operate appending an anomaly event).

    Other services load a state via ``get_state``, append to its hash chain, then
    call this to write it back — required now that the store hands out detached
    copies rather than a shared in-memory reference.
    """
    _save(state)


def reset_for_tests() -> None:
    """Reset the lifecycle store; tests call this in setup.

    Drops the cached store so the next access re-reads ``CPOA_STORAGE_MODE``
    (tests run in-memory) and starts from a clean slate.
    """
    global _store
    _store = None


def _validate_transition(state: LifecycleState, action: Action) -> str | None:
    """Return an error message if the action isn't valid from the current status."""
    if action == "place_on_leave" and state.status != "active":
        return f"cannot place_on_leave from status '{state.status}'"
    if action == "return_from_leave" and state.status != "on_leave":
        return f"cannot return_from_leave from status '{state.status}'"
    return None


def _emit(
    state: LifecycleState,
    event_type: str,
    summary: str,
    payload: dict,
    actor_id: str,
) -> EvidenceEvent:
    event = EvidenceEvent(
        event_id=f"evt-{uuid.uuid4().hex[:12]}",
        event_type=event_type,
        trace_id=f"trace-mgmt-{uuid.uuid4().hex[:10]}",
        session_id=f"session-mgmt-{uuid.uuid4().hex[:10]}",
        actor=Actor(type="human", id=actor_id),
        subject=Subject(candidate_agent_id=state.candidate_agent_id),
        summary=summary,
        payload_hash=hashing.payload_hash(payload),
    )
    hashing.link_event(event, state.last_event_hash)
    # Real signature — HMAC-SHA256 by default, KMS when CPOA_SIGNING_MODE=kms.
    event.signature = get_signer().sign(event.event_hash)
    return event


def apply_action(
    candidate_agent_id: str,
    action: Action,
    payload: dict,
    *,
    actor_id: str = "hr.console@clearpointlogic.com",
) -> dict:
    """Apply a workforce action; append an evidence event; return the new state.

    Raises ``ValueError`` if the action is not valid from the current status.
    """
    if action not in _ACTION_EVENT_TYPE:
        raise ValueError(f"unknown action: {action}")

    state = get_state(candidate_agent_id)
    err = _validate_transition(state, action)
    if err:
        raise ValueError(err)

    event_type = _ACTION_EVENT_TYPE[action]
    reason = payload.get("reason") or ""
    new_owner = payload.get("new_owner_email")
    scope_changes = payload.get("scope_changes") or {}

    if action == "place_on_leave":
        state.status = "on_leave"
        summary = f"Placed on leave: {reason or '(no reason given)'}"
    elif action == "return_from_leave":
        state.status = "active"
        summary = f"Returned from leave: {reason or '(no reason given)'}"
    elif action == "manager_handoff":
        if not new_owner:
            raise ValueError("manager_handoff requires new_owner_email")
        old_owner = state.owner_email or "(unset)"
        state.owner_email = new_owner
        summary = f"Manager handoff: {old_owner} → {new_owner}"
    elif action == "role_change":
        if not scope_changes:
            raise ValueError("role_change requires scope_changes")
        summary = f"Role change: {', '.join(scope_changes.keys())}"
    else:  # pragma: no cover — guarded above
        raise ValueError(f"unhandled action: {action}")

    event = _emit(
        state=state,
        event_type=event_type,
        summary=summary,
        payload={"action": action, **payload},
        actor_id=actor_id,
    )

    event_dict = event.model_dump(mode="json")
    state.event_log.append(event_dict)
    state.last_event_hash = event.event_hash
    state.notes = (reason or state.notes)[:240]
    state.updated_at = _now_iso()
    _save(state)

    return {
        "state": state.to_dict(),
        "event": event_dict,
    }


# --- Post-onboarding lifecycle phases ---------------------------------------
#
# Beyond the day-to-day Manage actions above, an onboarded agent advances through
# the remaining AI Workforce Management phases — Manage → Govern → Operate →
# Optimize. Each advance appends a *real* signed, hash-chained event to the same
# personnel file, so the chain is continuous from intake all the way through the
# lifecycle (no faked transitions). The human-readable summary + detail payload
# are computed by the caller (API layer) from live Govern/Operate/Optimize data
# so this module stays dependency-free.

_PHASE_EVENT_TYPE: dict[str, str] = {
    "manage": "manage.activated",
    "govern": "govern.controls_attested",
    "operate": "operate.performance_reviewed",
    "optimize": "optimize.development_plan_accepted",
}

# Canonical advance order for the "run full lifecycle" shortcut.
PHASE_ORDER: list[str] = ["manage", "govern", "operate", "optimize"]


def completed_phases(state: LifecycleState) -> list[str]:
    """Phases already attested on this agent's personnel file (by event_type)."""
    seen = {e.get("event_type") for e in state.event_log}
    return [phase for phase, et in _PHASE_EVENT_TYPE.items() if et in seen]


# Per-phase remediation event types. Recording a remediation appends one of
# these signed events to the personnel file and writes the ledger entry that
# flips a flagged lifecycle card back to "passed".
_REMEDIATION_EVENT_TYPE: dict[str, str] = {
    "govern": "govern.gap_remediated",
    "operate": "operate.anomaly_resolved",
    "optimize": "optimize.item_resolved",
}


def resolved_refs(state: LifecycleState, phase: str) -> set[str]:
    """Ref-ids already remediated for ``phase`` (control_id / rule_id / finding_id)."""
    return {
        r["ref_id"]
        for r in state.remediations
        if r.get("phase") == phase and r.get("ref_id")
    }


def record_remediation(
    candidate_agent_id: str,
    phase: str,
    ref_id: str,
    *,
    title: str,
    summary: str,
    actor_id: str = "workforce.manager@clearpointlogic.com",
) -> dict:
    """Resolve a flagged lifecycle item (a Govern gap, Operate anomaly, or
    Optimize development item).

    Appends a signed, hash-chained remediation event and writes a ledger entry
    so the per-phase gating recomputes the item as resolved. Raises
    ``ValueError`` for unknown phases.
    """
    if phase not in _REMEDIATION_EVENT_TYPE:
        raise ValueError(
            f"unknown phase: {phase} (expected one of {sorted(_REMEDIATION_EVENT_TYPE)})"
        )

    state = get_state(candidate_agent_id)
    event = _emit(
        state=state,
        event_type=_REMEDIATION_EVENT_TYPE[phase],
        summary=summary,
        payload={"phase": phase, "ref_id": ref_id, "title": title},
        actor_id=actor_id,
    )
    event_dict = event.model_dump(mode="json")
    state.event_log.append(event_dict)
    state.last_event_hash = event.event_hash
    resolved_at = _now_iso()
    state.remediations.append({
        "phase": phase,
        "ref_id": ref_id,
        "title": title,
        "summary": summary,
        "event_id": event.event_id,
        "actor": actor_id,
        "resolved_at": resolved_at,
    })
    state.updated_at = resolved_at
    _save(state)

    return {"state": state.to_dict(), "event": event_dict}


def advance_phase(
    candidate_agent_id: str,
    phase: str,
    *,
    summary: str,
    detail: dict,
    actor_id: str,
) -> dict:
    """Advance one onboarded agent into the given lifecycle phase.

    Appends a signed, hash-chained ``<phase>`` event to the personnel file and
    returns the new state + the event. Raises ``ValueError`` for unknown phases.
    """
    if phase not in _PHASE_EVENT_TYPE:
        raise ValueError(f"unknown phase: {phase} (expected one of {PHASE_ORDER})")

    state = get_state(candidate_agent_id)
    event = _emit(
        state=state,
        event_type=_PHASE_EVENT_TYPE[phase],
        summary=summary,
        payload={"phase": phase, **detail},
        actor_id=actor_id,
    )
    event_dict = event.model_dump(mode="json")
    state.event_log.append(event_dict)
    state.last_event_hash = event.event_hash
    state.updated_at = _now_iso()
    _save(state)

    return {"state": state.to_dict(), "event": event_dict, "phase": phase}


def list_states() -> list[dict]:
    return list(_get_store().all())
