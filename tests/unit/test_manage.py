"""Unit tests for the Manage phase (HR Console lifecycle actions).

Verifies every action emits a real hash-chained evidence event, state
transitions are guarded, and the per-agent event log links event_hashes
correctly through previous_event_hash.
"""

from __future__ import annotations

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
