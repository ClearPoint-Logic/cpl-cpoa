"""Unit tests for the Discover phase scanner.

The HTTP layer is mocked via httpx.MockTransport so the assertions exercise the
real classification logic (known/unknown/unreachable/invalid) and the candidate-
id extraction without depending on the live demo-fleet endpoints.
"""

from __future__ import annotations

import json

import httpx

from cpoa.services import agent_discovery
from cpoa.services.agent_discovery import (
    DiscoveredAgent,
    _classify,
    _extract_candidate_id,
    fetch_agent_card,
    scan_endpoints,
)


def test_extract_candidate_id_prefers_explicit() -> None:
    assert _extract_candidate_id({"candidate_agent_id": "abc", "id": "xyz"}) == "abc"


def test_extract_candidate_id_falls_back_to_id() -> None:
    assert _extract_candidate_id({"id": "shadow-bot"}) == "shadow-bot"


def test_extract_candidate_id_slugifies_name() -> None:
    assert _extract_candidate_id({"name": "Shadow Bot"}) == "shadow-bot"


def test_extract_candidate_id_returns_none_when_unknown() -> None:
    assert _extract_candidate_id({}) is None


def test_classify_known_against_registry() -> None:
    card = {"candidate_agent_id": "safe-research-001", "name": "Safe Research Agent"}
    registry = {"safe-research-001": {"candidate_agent_id": "safe-research-001"}}
    status, cid, entry = _classify(card, registry)
    assert status == "known"
    assert cid == "safe-research-001"
    assert entry is not None


def test_classify_unknown_when_not_in_registry() -> None:
    card = {"candidate_agent_id": "shadow-bot", "name": "Shadow Bot"}
    status, cid, entry = _classify(card, {})
    assert status == "unknown"
    assert cid == "shadow-bot"
    assert entry is None


def test_classify_invalid_when_no_id_extractable() -> None:
    status, cid, entry = _classify({}, {})
    assert status == "invalid"
    assert cid is None


def test_fetch_agent_card_success() -> None:
    card = {"candidate_agent_id": "x", "name": "X"}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/.well-known/agent.json")
        return httpx.Response(200, json=card)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = fetch_agent_card("https://example.test", client=client)
    assert result.status == "pending"  # classify happens at scan time
    assert result.agent_card == card
    assert result.error is None


def test_fetch_agent_card_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = fetch_agent_card("https://example.test", client=client)
    assert result.status == "unreachable"
    assert "HTTP 503" in (result.error or "")


def test_fetch_agent_card_invalid_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = fetch_agent_card("https://example.test", client=client)
    assert result.status == "invalid"


def test_fetch_agent_card_request_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = fetch_agent_card("https://example.test", client=client)
    assert result.status == "unreachable"
    assert "connection refused" in (result.error or "")


def test_scan_endpoints_mixed_results(monkeypatch) -> None:
    """End-to-end scan with mixed known/unknown/unreachable endpoints."""
    cards = {
        "https://known.test/.well-known/agent.json": {
            "candidate_agent_id": "safe-research-001",
            "name": "Safe Research Agent",
        },
        "https://shadow.test/.well-known/agent.json": {
            "candidate_agent_id": "shadow-engagement-bot",
            "name": "Shadow Bot",
        },
    }

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url in cards:
            return httpx.Response(200, json=cards[url])
        if "unreachable" in url:
            raise httpx.ConnectError("nope")
        return httpx.Response(404)

    # Patch the module-level Client constructor so scan_endpoints uses our transport.
    real_client_cls = httpx.Client

    def make_client(*args, **kwargs):
        return real_client_cls(*args, transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(agent_discovery.httpx, "Client", make_client)

    endpoints = ["https://known.test", "https://shadow.test", "https://unreachable.test"]
    results = scan_endpoints(endpoints)

    by_endpoint = {r.endpoint: r for r in results}
    assert by_endpoint["https://known.test"].status == "known"
    assert by_endpoint["https://known.test"].matched_registry_entry is not None
    assert by_endpoint["https://shadow.test"].status == "unknown"
    assert by_endpoint["https://shadow.test"].candidate_agent_id == "shadow-engagement-bot"
    assert by_endpoint["https://unreachable.test"].status == "unreachable"


def test_demo_fleet_endpoints_built_from_base() -> None:
    endpoints = agent_discovery.demo_fleet_endpoints("https://cpoa.example/")
    # Trailing slash trimmed, every name in the fleet represented.
    assert all(e.startswith("https://cpoa.example/api/demo-fleet/") for e in endpoints)
    assert len(endpoints) == len(agent_discovery.DEMO_FLEET)


def test_demo_fleet_card_lookup() -> None:
    assert agent_discovery.demo_fleet_card("safe-research-001") is not None
    assert agent_discovery.demo_fleet_card("does-not-exist") is None


def test_is_known_uses_real_registry() -> None:
    # safe-research-001 is in fixtures/registry/google_agent_registry_fixture.json
    assert agent_discovery.is_known("safe-research-001") is True
    assert agent_discovery.is_known("shadow-engagement-bot") is False


def test_discovered_agent_to_dict_round_trips() -> None:
    da = DiscoveredAgent(endpoint="https://x", status="known", agent_card={"a": 1})
    d = da.to_dict()
    assert d["endpoint"] == "https://x"
    assert d["status"] == "known"
    assert d["agent_card"] == {"a": 1}
    # round trip through JSON to confirm dataclass-as-dict is serializable
    assert json.loads(json.dumps(d))["status"] == "known"
