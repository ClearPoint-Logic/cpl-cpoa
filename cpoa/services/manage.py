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

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

from cpoa.schemas import Actor, EvidenceEvent, Signature, Subject
from cpoa.services import hashing

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

    def to_dict(self) -> dict:
        return {
            "candidate_agent_id": self.candidate_agent_id,
            "status": self.status,
            "owner_email": self.owner_email,
            "notes": self.notes,
            "updated_at": self.updated_at,
            "event_log": list(self.event_log),
            "last_event_hash": self.last_event_hash,
        }


# In-memory store. The same interface is used by tests; production swaps in a
# Firestore-backed implementation behind the same get/save calls.
_STATE: dict[str, LifecycleState] = {}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def get_state(candidate_agent_id: str) -> LifecycleState:
    state = _STATE.get(candidate_agent_id)
    if state is None:
        state = LifecycleState(candidate_agent_id=candidate_agent_id, updated_at=_now_iso())
        _STATE[candidate_agent_id] = state
    return state


def reset_for_tests() -> None:
    """Clear the in-memory state; tests call this in setup."""
    _STATE.clear()


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
    # The signature here uses the same Signature schema as Onboarding events.
    # A real KMS-backed signer can be wired here behind a CPOA_SIGNING_MODE flag.
    event.signature = Signature(
        type="local_hmac",
        value="hmac:" + event.event_hash.split(":", 1)[-1][:24],
    )
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

    return {
        "state": state.to_dict(),
        "event": event_dict,
    }


def list_states() -> list[dict]:
    return [s.to_dict() for s in _STATE.values()]
