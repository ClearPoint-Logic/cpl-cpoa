"""Discover phase — integration tests against the FastAPI app.

The demo-fleet card endpoints are exercised end-to-end via TestClient. The
/api/discovery/scan endpoint is verified at the shape/wiring layer — the
scanner's HTTP calls are unit-tested separately with `httpx.MockTransport`
in `tests/unit/test_agent_discovery.py`, which is the right level for the
classification logic. (TestClient runs the FastAPI app in-process and is not
itself reachable via outbound httpx.Client calls.)
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.main import app
from cpoa.services import agent_discovery
from cpoa.services.agent_discovery import DEMO_FLEET, DiscoveredAgent

client = TestClient(app)


def test_demo_fleet_card_round_trip() -> None:
    r = client.get("/api/demo-fleet/safe-research-001/.well-known/agent.json")
    assert r.status_code == 200
    card = r.json()
    assert card["candidate_agent_id"] == "safe-research-001"
    assert card["name"] == "Safe Research Agent"
    # url is decorated by the handler
    assert card["url"].endswith("/api/demo-fleet/safe-research-001/a2a/v1")


def test_demo_fleet_card_unknown_404() -> None:
    r = client.get("/api/demo-fleet/no-such-agent/.well-known/agent.json")
    assert r.status_code == 404


def test_demo_fleet_serves_every_card() -> None:
    """Every entry in DEMO_FLEET should be reachable at its discovery URL."""
    for name in DEMO_FLEET:
        r = client.get(f"/api/demo-fleet/{name}/.well-known/agent.json")
        assert r.status_code == 200, f"missing card: {name}"
        assert r.json()["candidate_agent_id"] == name


def test_discovery_scan_shape_and_default_endpoints(monkeypatch) -> None:
    """When no endpoints are passed, the handler defaults to the demo fleet
    and returns a typed envelope with summary, results, and the honest-scope
    note. The scanner itself is monkey-patched here because TestClient can't
    intercept the scanner's outbound httpx calls."""
    captured: dict = {}

    def fake_scan(endpoints: list[str]) -> list[DiscoveredAgent]:
        captured["endpoints"] = endpoints
        return [
            DiscoveredAgent(
                endpoint=endpoints[0],
                status="known",
                candidate_agent_id="safe-research-001",
                agent_card={"name": "Safe Research Agent"},
                matched_registry_entry={"candidate_agent_id": "safe-research-001"},
            ),
            DiscoveredAgent(
                endpoint=endpoints[1] if len(endpoints) > 1 else "x",
                status="unknown",
                candidate_agent_id="shadow-engagement-bot",
                agent_card={"name": "Shadow Bot"},
            ),
        ]

    monkeypatch.setattr(agent_discovery, "scan_endpoints", fake_scan)

    r = client.post("/api/discovery/scan", json={})
    assert r.status_code == 200
    body = r.json()
    assert body["summary"]["scanned"] == 2
    assert body["summary"]["known"] == 1
    assert body["summary"]["unknown"] == 1
    assert "customer environment" in body["scope"].lower()
    # Default fleet endpoints were synthesized from the request base_url
    assert len(captured["endpoints"]) == len(DEMO_FLEET)
    assert all("/api/demo-fleet/" in e for e in captured["endpoints"])


def test_discovery_scan_passes_through_explicit_endpoints(monkeypatch) -> None:
    captured: dict = {}

    def fake_scan(endpoints: list[str]) -> list[DiscoveredAgent]:
        captured["endpoints"] = endpoints
        return [
            DiscoveredAgent(endpoint=e, status="unreachable", error="HTTP 503")
            for e in endpoints
        ]

    monkeypatch.setattr(agent_discovery, "scan_endpoints", fake_scan)

    explicit = ["https://other.example/a2a", "https://another.example/a2a"]
    r = client.post("/api/discovery/scan", json={"endpoints": explicit})
    assert r.status_code == 200
    assert captured["endpoints"] == explicit
    assert r.json()["summary"]["unreachable"] == 2
