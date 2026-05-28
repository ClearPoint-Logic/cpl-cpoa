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
