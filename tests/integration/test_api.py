"""FastAPI backend tests (run via TestClient; deterministic, no live LLM)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_fixtures_returns_all_eight():
    r = client.get("/api/fixtures")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 8
    names = {f["name"] for f in data}
    assert "safe_research_agent" in names
    safe = next(f for f in data if f["name"] == "safe_research_agent")
    assert safe["business_story"] and safe["tier"] == "must_ship"


def test_create_and_fetch_run_ready():
    r = client.post("/api/runs", json={"fixture": "safe_research_agent"})
    assert r.status_code == 200
    run = r.json()
    assert run["decision"] == "Ready"
    assert run["score"]["score"] >= 80
    assert run["narrative"]["source"] == "deterministic"
    # fetch it back
    got = client.get(f"/api/runs/{run['run_id']}")
    assert got.status_code == 200
    assert got.json()["run_id"] == run["run_id"]


def test_create_run_blocked_prompt_injection():
    r = client.post("/api/runs", json={"fixture": "prompt_injected_mcp_agent"})
    run = r.json()
    assert run["decision"] == "Blocked Pending Remediation"
    assert any(f["test_id"] == "OV-004" for f in run["validation_run"]["findings"])


def test_download_bundle_json_and_md():
    run = client.post("/api/runs", json={"fixture": "healthcare_phi_support_agent"}).json()
    rid = run["run_id"]
    rj = client.get(f"/api/runs/{rid}/download/json")
    assert rj.status_code == 200 and "agent-passport/v0.1" in rj.text
    rm = client.get(f"/api/runs/{rid}/download/md")
    assert rm.status_code == 200 and "Onboarding Evidence Bundle" in rm.text


def test_grounding_comparison_endpoint():
    r = client.get("/api/grounding-comparison/grounding_required_policy_agent")
    assert r.status_code == 200
    data = r.json()
    assert data["ungrounded"]["grounding_refs"] == []
    assert len(data["grounded"]["grounding_refs"]) >= 1


def test_invalid_manifest_422():
    r = client.post("/api/runs", json={"candidate_manifest": {"name": "no id"}})
    assert r.status_code == 422
