"""Integration tests for the HR Console lifecycle endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from cpoa.services import manage

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state() -> None:
    manage.reset_for_tests()


def test_get_workforce_state_creates_default() -> None:
    r = client.get("/api/workforce/agent-1/state")
    assert r.status_code == 200
    assert r.json()["status"] == "active"


def test_apply_place_on_leave_and_return() -> None:
    r1 = client.post(
        "/api/workforce/agent-1/action",
        json={"action": "place_on_leave", "payload": {"reason": "model refresh"}},
    )
    assert r1.status_code == 200
    body = r1.json()
    assert body["state"]["status"] == "on_leave"
    assert body["event"]["event_type"] == "manage.placed_on_leave"

    r2 = client.post(
        "/api/workforce/agent-1/action",
        json={"action": "return_from_leave", "payload": {"reason": "refresh complete"}},
    )
    assert r2.status_code == 200
    second = r2.json()
    assert second["state"]["status"] == "active"
    # Chain integrity across requests
    assert second["event"]["previous_event_hash"] == body["event"]["event_hash"]


def test_unknown_action_rejected() -> None:
    r = client.post(
        "/api/workforce/agent-1/action",
        json={"action": "delete_agent", "payload": {}},
    )
    assert r.status_code == 422


def test_invalid_transition_returns_422() -> None:
    r = client.post(
        "/api/workforce/agent-1/action",
        json={"action": "return_from_leave", "payload": {}},
    )
    assert r.status_code == 422
    assert "cannot return_from_leave" in r.json()["detail"]


def test_manager_handoff_round_trip() -> None:
    r = client.post(
        "/api/workforce/agent-1/action",
        json={
            "action": "manager_handoff",
            "payload": {"new_owner_email": "owner2@example.com"},
            "actor_id": "director@example.com",
        },
    )
    assert r.status_code == 200
    state = r.json()["state"]
    assert state["owner_email"] == "owner2@example.com"
    # State is reflected in subsequent GET
    g = client.get("/api/workforce/agent-1/state")
    assert g.json()["owner_email"] == "owner2@example.com"


def test_list_workforce_states_shows_every_tracked_agent() -> None:
    client.post("/api/workforce/a/action", json={"action": "place_on_leave", "payload": {"reason": "x"}})
    client.post("/api/workforce/b/action", json={"action": "manager_handoff",
                                                 "payload": {"new_owner_email": "x@y"}})
    r = client.get("/api/workforce/states")
    assert r.status_code == 200
    ids = {s["candidate_agent_id"] for s in r.json()}
    assert ids == {"a", "b"}


# --- Lifecycle continuation endpoints (Manage → Govern → Operate → Optimize) ---
# Regression for the live 500: advancing any phase must return 200, not blow up
# constructing the EvidenceEvent with an unknown event_type.


@pytest.mark.parametrize(
    "phase,event_type",
    [
        ("manage", "manage.activated"),
        ("govern", "govern.controls_attested"),
        ("operate", "operate.performance_reviewed"),
        ("optimize", "optimize.development_plan_accepted"),
    ],
)
def test_advance_lifecycle_phase_returns_200(phase: str, event_type: str) -> None:
    r = client.post("/api/workforce/agent-1/advance", json={"phase": phase})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["event"]["event_type"] == event_type
    assert body["event"]["signature"]["value"].startswith("hmac-sha256:")


def test_advance_lifecycle_rejects_unknown_phase() -> None:
    r = client.post("/api/workforce/agent-1/advance", json={"phase": "bogus"})
    assert r.status_code == 422


def test_run_full_lifecycle_advances_every_phase() -> None:
    r = client.post("/api/workforce/agent-1/run-lifecycle", json={})
    assert r.status_code == 200, r.text
    body = r.json()
    phases = [e["phase"] for e in body["events"]]
    assert phases == manage.PHASE_ORDER
    # Re-running is idempotent: every phase already attested, so no new events.
    r2 = client.post("/api/workforce/agent-1/run-lifecycle", json={})
    assert r2.status_code == 200
    assert r2.json()["events"] == []


# --- Lifecycle detail (rich per-phase cards on the run page) -----------------


def test_lifecycle_detail_has_all_four_phases() -> None:
    r = client.get("/api/workforce/safe-research-001/lifecycle-detail")
    assert r.status_code == 200, r.text
    body = r.json()
    for phase in ("manage", "govern", "operate", "optimize"):
        assert phase in body
        assert body[phase]["status"] in ("pass", "flagged")
    # Govern detail is the live control matrix summary.
    assert body["govern"]["controls"] == 7
    assert body["govern"]["frameworks"] == 3
    assert len(body["govern"]["control_list"]) == 7


def test_lifecycle_detail_with_run_populates_manage_card() -> None:
    run = client.post("/api/runs", json={"fixture": "safe_research_agent"}).json()
    r = client.get(
        f"/api/workforce/{run['candidate_agent_id']}/lifecycle-detail",
        params={"run_id": run["run_id"]},
    )
    assert r.status_code == 200, r.text
    mng = r.json()["manage"]
    # Real placement data flows from the manifest/passport, not a script.
    assert mng["manager_name"] == "Dana Lee"
    assert mng["team"] == "Research"
    assert mng["autonomy"] == "L1_recommend"
    # A clean agent passes Operate (no anomalies) and Optimize (no blockers).
    body = r.json()
    assert body["operate"]["status"] == "pass"
    assert body["optimize"]["status"] == "pass"


def test_lifecycle_detail_flags_blocked_agent() -> None:
    r = client.get("/api/workforce/privileged-admin-006/lifecycle-detail")
    assert r.status_code == 200, r.text
    body = r.json()
    # A blocked, high-autonomy/high-risk agent is flagged by Sentinel and held
    # back from promotion — the sad-path signals the demo leans on.
    assert body["operate"]["status"] == "flagged"
    assert len(body["operate"]["anomalies"]) >= 1
    assert body["optimize"]["status"] == "flagged"
    assert len(body["optimize"]["promotion_blockers"]) >= 1


# --- Per-phase remediation (Phase 3): resolve a flagged item, watch it flip ---


def test_remediate_govern_gap_flips_status_to_pass() -> None:
    run = client.post("/api/runs", json={"fixture": "budget_runaway_research_agent"}).json()
    cid, rid = run["candidate_agent_id"], run["run_id"]

    # A Conditional agent shows a flagged Govern control gap.
    before = client.get(f"/api/workforce/{cid}/lifecycle-detail", params={"run_id": rid}).json()
    assert before["govern"]["status"] == "flagged"
    gap = before["govern"]["gaps"][0]
    assert gap["resolved"] is False

    # Attesting the control writes a real signed, hash-chained remediation event.
    r = client.post(
        f"/api/workforce/{cid}/remediate",
        json={
            "phase": "govern",
            "ref_id": gap["control_id"],
            "title": gap["control_name"],
            "summary": "Control attested with compensating guardrail",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["event"]["event_type"] == "govern.gap_remediated"
    assert body["event"]["signature"]["value"].startswith("hmac-sha256:")
    assert body["state"]["remediations"][0]["ref_id"] == gap["control_id"]

    # The same deterministic gate now reads the ledger and reports the gap closed.
    after = client.get(f"/api/workforce/{cid}/lifecycle-detail", params={"run_id": rid}).json()
    assert after["govern"]["status"] == "pass"
    assert after["govern"]["gaps"][0]["resolved"] is True


def test_remediate_optimize_item_marks_ready_for_promotion() -> None:
    run = client.post("/api/runs", json={"fixture": "budget_runaway_research_agent"}).json()
    cid, rid = run["candidate_agent_id"], run["run_id"]

    before = client.get(f"/api/workforce/{cid}/lifecycle-detail", params={"run_id": rid}).json()
    assert before["optimize"]["status"] == "flagged"
    item = before["optimize"]["development_items"][0]

    r = client.post(
        f"/api/workforce/{cid}/remediate",
        json={"phase": "optimize", "ref_id": item["finding_id"], "title": item["title"]},
    )
    assert r.status_code == 200, r.text
    assert r.json()["event"]["event_type"] == "optimize.item_resolved"

    after = client.get(f"/api/workforce/{cid}/lifecycle-detail", params={"run_id": rid}).json()
    assert after["optimize"]["status"] == "pass"
    assert after["optimize"]["development_items"][0]["resolved"] is True


def test_remediate_rejects_unknown_phase_and_missing_ref() -> None:
    assert (
        client.post("/api/workforce/agent-1/remediate", json={"phase": "manage", "ref_id": "x"}).status_code
        == 422
    )
    assert (
        client.post("/api/workforce/agent-1/remediate", json={"phase": "govern"}).status_code == 422
    )


# --- Demo reset: wipe lifecycle state back to pristine -----------------------


def test_demo_reset_clears_all_lifecycle_state() -> None:
    # Seed lifecycle state two ways: a Manage action and a full lifecycle run.
    client.post("/api/workforce/a/action", json={"action": "place_on_leave", "payload": {"reason": "x"}})
    client.post("/api/workforce/b/run-lifecycle", json={})
    assert len(client.get("/api/workforce/states").json()) == 2

    # Reset wipes every tracked agent and reports how many were cleared.
    r = client.post("/api/demo/reset")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "reset"
    assert body["cleared"] == 2

    # The HR Console is empty; a fresh read re-derives the default active state.
    assert client.get("/api/workforce/states").json() == []
    assert client.get("/api/workforce/a/state").json()["status"] == "active"


def test_demo_reset_restores_flagged_govern_gap() -> None:
    """The headline demo loop: resolving a Govern gap flips it to pass; Reset
    must bring the flagged gap back so the demo can be re-run from scratch."""
    run = client.post("/api/runs", json={"fixture": "budget_runaway_research_agent"}).json()
    cid, rid = run["candidate_agent_id"], run["run_id"]

    gap = client.get(
        f"/api/workforce/{cid}/lifecycle-detail", params={"run_id": rid}
    ).json()["govern"]["gaps"][0]
    client.post(
        f"/api/workforce/{cid}/remediate",
        json={"phase": "govern", "ref_id": gap["control_id"], "title": gap["control_name"]},
    )
    resolved = client.get(
        f"/api/workforce/{cid}/lifecycle-detail", params={"run_id": rid}
    ).json()
    assert resolved["govern"]["status"] == "pass"

    assert client.post("/api/demo/reset").status_code == 200

    pristine = client.get(
        f"/api/workforce/{cid}/lifecycle-detail", params={"run_id": rid}
    ).json()
    assert pristine["govern"]["status"] == "flagged"
    assert pristine["govern"]["gaps"][0]["resolved"] is False
