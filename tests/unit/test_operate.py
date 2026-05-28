"""Unit tests for Operate (Sentinel) — fleet health, anomaly detection, evidence chain."""

from __future__ import annotations

import pytest

from cpoa.services import manage, operate


@pytest.fixture(autouse=True)
def reset_state() -> None:
    manage.reset_for_tests()


def test_assess_fleet_returns_real_members() -> None:
    snapshot = operate.assess_fleet()[0]
    assert snapshot["summary"]["agents"] > 0
    # Each member has the derived fields populated
    for m in snapshot["members"]:
        assert m["candidate_agent_id"]
        assert m["name"]
        assert m["status"] in {"active", "on_leave", "returning"}
        assert m["risk_tier"]
        assert m["autonomy_level"]
        assert isinstance(m["readiness_score"], int)


def test_blocking_findings_surface_anomaly() -> None:
    """An agent whose intake produced blockers must show the BLOCKER-AT-INTAKE rule."""
    snapshot = operate.assess_fleet()[0]
    members_by_id = {m["candidate_agent_id"]: m for m in snapshot["members"]}
    # prompt_injected_mcp_agent is a known blocker fixture
    target = members_by_id.get("prompt-injected-005")
    if target is None:
        pytest.skip("prompt_injected_mcp_agent fixture not present in this build")
    rules = [a["rule_id"] for a in target["anomalies"]]
    assert "BLOCKER-AT-INTAKE" in rules


def test_summary_aggregates_match_members() -> None:
    snapshot = operate.assess_fleet()[0]
    members = snapshot["members"]
    assert snapshot["summary"]["agents"] == len(members)
    assert snapshot["summary"]["active"] == sum(1 for m in members if m["status"] == "active")
    assert snapshot["summary"]["on_leave"] == sum(1 for m in members if m["status"] == "on_leave")
    assert snapshot["summary"]["agents_with_anomalies"] == sum(1 for m in members if m["anomalies"])
    assert snapshot["summary"]["total_anomalies"] == sum(len(m["anomalies"]) for m in members)


def test_on_leave_status_reflects_manage_state() -> None:
    # Place a fixture agent on leave; the next assessment should see it
    manage.apply_action("safe-research-001", "place_on_leave", {"reason": "review"})
    snapshot = operate.assess_fleet()[0]
    by_id = {m["candidate_agent_id"]: m for m in snapshot["members"]}
    assert by_id["safe-research-001"]["status"] == "on_leave"


def test_record_anomaly_appends_evidence_event_with_chain() -> None:
    first = operate.record_anomaly(
        "safe-research-001",
        rule_id="HIGH-AUTONOMY-HIGH-RISK",
        severity="high",
        summary="autonomy + risk warrants oversight",
    )
    assert first["event"]["event_type"] == "operate.anomaly_detected"
    assert first["event"]["event_hash"].startswith("sha256:")
    assert first["event"]["previous_event_hash"] is None
    # Second anomaly chains to the first
    second = operate.record_anomaly("safe-research-001", "STALE-LEAVE", "medium", "no review")
    assert second["event"]["previous_event_hash"] == first["event"]["event_hash"]
    # Both events appear in the agent's personnel file
    state = manage.get_state("safe-research-001")
    assert len(state.event_log) >= 2
    assert state.event_log[-1]["event_type"] == "operate.anomaly_detected"


def test_high_autonomy_high_risk_fires_for_privileged_admin_agent() -> None:
    """privileged_admin_agent is L3+ with privileged_admin risk tier."""
    snapshot = operate.assess_fleet()[0]
    by_id = {m["candidate_agent_id"]: m for m in snapshot["members"]}
    target = by_id.get("privileged-admin-006") or by_id.get("privileged-admin-001")
    if target is None:
        pytest.skip("privileged_admin fixture not present")
    rules = [a["rule_id"] for a in target["anomalies"]]
    assert "HIGH-AUTONOMY-HIGH-RISK" in rules or "BLOCKER-AT-INTAKE" in rules
