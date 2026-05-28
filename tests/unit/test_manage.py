"""Unit tests for the Manage phase (HR Console lifecycle actions).

Verifies every action emits a real hash-chained evidence event, state
transitions are guarded, and the per-agent event log links event_hashes
correctly through previous_event_hash.
"""

from __future__ import annotations

import json

import pytest

from cpoa.services import manage


@pytest.fixture(autouse=True)
def reset_state() -> None:
    manage.reset_for_tests()


def test_get_state_creates_default_active() -> None:
    state = manage.get_state("safe-research-001")
    assert state.status == "active"
    assert state.owner_email is None
    assert state.event_log == []
    assert state.last_event_hash is None


def test_place_on_leave_transitions_and_emits_event() -> None:
    result = manage.apply_action(
        "safe-research-001",
        "place_on_leave",
        {"reason": "model upgrade pending review"},
        actor_id="manager@example.com",
    )
    assert result["state"]["status"] == "on_leave"
    event = result["event"]
    assert event["event_type"] == "manage.placed_on_leave"
    assert event["event_hash"].startswith("sha256:")
    assert event["actor"]["id"] == "manager@example.com"
    assert event["previous_event_hash"] is None


def test_return_from_leave_chains_to_previous_event() -> None:
    manage.apply_action("x", "place_on_leave", {"reason": "investigation"})
    second = manage.apply_action("x", "return_from_leave", {"reason": "investigation complete"})
    state = second["state"]
    assert state["status"] == "active"
    # The second event chains to the first
    first_hash = state["event_log"][0]["event_hash"]
    second_event = second["event"]
    assert second_event["previous_event_hash"] == first_hash


def test_invalid_transition_raises() -> None:
    # Cannot return from leave when active
    with pytest.raises(ValueError, match="cannot return_from_leave"):
        manage.apply_action("x", "return_from_leave", {})


def test_double_place_on_leave_blocked() -> None:
    manage.apply_action("x", "place_on_leave", {"reason": "first"})
    with pytest.raises(ValueError, match="cannot place_on_leave"):
        manage.apply_action("x", "place_on_leave", {"reason": "again"})


def test_manager_handoff_requires_new_owner() -> None:
    with pytest.raises(ValueError, match="manager_handoff requires new_owner_email"):
        manage.apply_action("x", "manager_handoff", {})


def test_manager_handoff_updates_owner() -> None:
    result = manage.apply_action(
        "x",
        "manager_handoff",
        {"new_owner_email": "newowner@example.com"},
        actor_id="director@example.com",
    )
    assert result["state"]["owner_email"] == "newowner@example.com"
    assert result["event"]["event_type"] == "manage.ownership_transferred"
    assert "newowner@example.com" in result["event"]["summary"]


def test_role_change_requires_scope_changes() -> None:
    with pytest.raises(ValueError, match="role_change requires scope_changes"):
        manage.apply_action("x", "role_change", {})


def test_role_change_emits_scope_updated_event() -> None:
    result = manage.apply_action(
        "x",
        "role_change",
        {"scope_changes": {"allowed_tools": ["new_tool"], "budget_monthly_usd": 200}},
    )
    assert result["event"]["event_type"] == "manage.scope_updated"
    assert "allowed_tools" in result["event"]["summary"]


def test_unknown_action_raises() -> None:
    with pytest.raises(ValueError, match="unknown action"):
        manage.apply_action("x", "not_a_real_action", {})  # type: ignore[arg-type]


def test_event_log_accumulates_in_order() -> None:
    manage.apply_action("x", "place_on_leave", {"reason": "review"})
    manage.apply_action("x", "return_from_leave", {"reason": "approved"})
    manage.apply_action("x", "manager_handoff", {"new_owner_email": "next@example.com"})
    state = manage.get_state("x")
    assert len(state.event_log) == 3
    assert [e["event_type"] for e in state.event_log] == [
        "manage.placed_on_leave",
        "manage.returned_from_leave",
        "manage.ownership_transferred",
    ]
    # Hash chain links each event to the previous
    prev = None
    for evt in state.event_log:
        assert evt["previous_event_hash"] == prev
        prev = evt["event_hash"]


def test_list_states_returns_every_tracked_agent() -> None:
    manage.apply_action("agent-a", "place_on_leave", {"reason": "one"})
    manage.apply_action("agent-b", "manager_handoff", {"new_owner_email": "x@y"})
    states = manage.list_states()
    assert {s["candidate_agent_id"] for s in states} == {"agent-a", "agent-b"}


def test_event_signature_is_real_hmac() -> None:
    result = manage.apply_action("x", "place_on_leave", {"reason": "r"})
    event = result["event"]
    assert event["signature"]["type"] == "local_hmac"
    # Real HMAC-SHA256 signature (64 hex chars after the "hmac-sha256:" prefix)
    assert event["signature"]["value"].startswith("hmac-sha256:")
    assert len(event["signature"]["value"].removeprefix("hmac-sha256:")) == 64


# --- Post-onboarding lifecycle continuation (Manage → Govern → Operate → Optimize) ---
#
# Regression guard: each phase event_type MUST be a member of the EventType
# Literal in cpoa.schemas.common, or EvidenceEvent construction raises a
# pydantic ValidationError at runtime (which surfaced as a 500 on /advance).


@pytest.mark.parametrize("phase", manage.PHASE_ORDER)
def test_advance_phase_emits_valid_event_type(phase: str) -> None:
    """Advancing any lifecycle phase must construct a schema-valid event.

    This is the regression test for the lifecycle-advance 500: before the
    EventType Literal included manage.activated / govern.controls_attested /
    optimize.development_plan_accepted, this raised ValidationError.
    """
    result = manage.advance_phase(
        "lifecycle-001",
        phase,
        summary=f"{phase} advanced",
        detail={"phase": phase},
        actor_id=f"{phase}@example.com",
    )
    assert result["phase"] == phase
    event = result["event"]
    assert event["event_type"] == manage._PHASE_EVENT_TYPE[phase]
    assert event["event_hash"].startswith("sha256:")
    assert event["signature"]["value"].startswith("hmac-sha256:")


def test_advance_phase_rejects_unknown_phase() -> None:
    with pytest.raises(ValueError, match="unknown phase"):
        manage.advance_phase("x", "bogus", summary="s", detail={}, actor_id="a@b")


def test_run_full_lifecycle_chains_all_four_phases() -> None:
    """Advancing every phase in order yields a continuous hash chain and all
    four phases reported complete."""
    state = manage.get_state("lifecycle-002")
    assert manage.completed_phases(state) == []
    for phase in manage.PHASE_ORDER:
        manage.advance_phase(
            "lifecycle-002", phase,
            summary=f"{phase} advanced", detail={"phase": phase},
            actor_id=f"{phase}@example.com",
        )
    state = manage.get_state("lifecycle-002")
    assert manage.completed_phases(state) == manage.PHASE_ORDER
    assert [e["event_type"] for e in state.event_log] == [
        "manage.activated",
        "govern.controls_attested",
        "operate.performance_reviewed",
        "optimize.development_plan_accepted",
    ]
    # Hash chain links each event to the previous.
    prev = None
    for evt in state.event_log:
        assert evt["previous_event_hash"] == prev
        prev = evt["event_hash"]


# --- Lifecycle store: in-memory default + durable (Firestore) persistence -----
#
# The store hands out *detached* copies (it serializes through to_dict /
# from_dict), so callers that mutate a loaded state must write it back with
# save_state. This is the contract operate.record_anomaly relies on, and the
# mechanism that lets per-phase Resolve + advance events survive a Cloud Run
# cold start when CPOA_STORAGE_MODE=firestore.


def test_state_dict_round_trip_is_lossless() -> None:
    manage.apply_action("round-trip", "place_on_leave", {"reason": "review"})
    d = manage.get_state("round-trip").to_dict()
    assert manage.LifecycleState.from_dict(d).to_dict() == d


def test_get_state_returns_detached_copy_requiring_explicit_save() -> None:
    # A loaded state mutated in place does NOT persist on its own …
    scratch = manage.get_state("detach")
    scratch.notes = "scratch"
    assert manage.get_state("detach").notes == ""
    # … but save_state writes it back (the contract operate.record_anomaly uses).
    durable = manage.get_state("detach")
    durable.notes = "persisted"
    manage.save_state(durable)
    assert manage.get_state("detach").notes == "persisted"


def test_default_storage_mode_is_in_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CPOA_STORAGE_MODE", raising=False)
    store = manage._make_store()
    assert isinstance(store, manage._MemoryLifecycleStore)
    assert store.mode == "local"


def test_firestore_unavailable_falls_back_to_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    """A Firestore init failure must degrade to in-memory, never hard-fail."""
    monkeypatch.setenv("CPOA_STORAGE_MODE", "firestore")

    def boom(self, *a: object, **k: object) -> None:
        raise RuntimeError("no firestore credentials in CI")

    monkeypatch.setattr(manage._FirestoreLifecycleStore, "__init__", boom)
    store = manage._make_store()
    assert isinstance(store, manage._MemoryLifecycleStore)


def test_durable_store_survives_cold_start(monkeypatch: pytest.MonkeyPatch) -> None:
    """With a durable backend, the personnel file (status + hash chain) is intact
    after the in-process store instance is dropped — i.e. a Cloud Run cold start."""
    backing: dict[str, str] = {}  # the durable layer (stands in for Firestore docs)

    class _FakeDurableStore:
        mode = "firestore"

        def get(self, cid: str) -> dict | None:
            raw = backing.get(cid)
            return json.loads(raw) if raw else None

        def save(self, cid: str, payload: dict) -> None:
            backing[cid] = json.dumps(payload)

        def all(self) -> list[dict]:
            return [json.loads(v) for v in backing.values()]

        def clear(self) -> None:
            backing.clear()

    monkeypatch.setattr(manage, "_make_store", lambda: _FakeDurableStore())
    manage.reset_for_tests()  # drop cached store so the patched factory is used

    manage.apply_action("cold-start", "place_on_leave", {"reason": "review"})
    manage.advance_phase(
        "cold-start", "govern", summary="attested", detail={"controls": 1}, actor_id="g@x"
    )

    # Cold start: drop the in-process instance. A durable backend keeps the data.
    manage._store = None
    state = manage.get_state("cold-start")
    assert state.status == "on_leave"
    assert [e["event_type"] for e in state.event_log] == [
        "manage.placed_on_leave",
        "govern.controls_attested",
    ]
    # The hash chain stays linked across the reload.
    assert state.event_log[1]["previous_event_hash"] == state.event_log[0]["event_hash"]
