"""FastAPI backend bridging the judge UI (and automation) to the onboarding engine.

Runs the deterministic engine by default (fast, reproducible, no credit spend). The
optional live ADK/Gemini narrative is gated behind Vertex availability. HTTP basic
auth (FR-076) is enforced whenever judge credentials are configured.
"""

from __future__ import annotations

import json
import os
import secrets
import uuid

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from agents.config import fast_model, llm_available
from agents.explanation import narrate_offline
from cpoa.evals import load_expected
from cpoa.loader import REPO_ROOT, list_fixture_names, load_manifest_by_name
from cpoa.schemas import CandidateAgentManifest
from cpoa.services import agent_discovery, engine, govern, manage
from cpoa.services.discovery import run_discovery
from cpoa.services.exports import bundle_to_json, bundle_to_markdown
from cpoa.services.grounding import build_grounding_comparison
from cpoa.services.tracing import span

from .store import get_store

app = FastAPI(title="ClearPoint Onboarding Agent API", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CPOA_CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run store: in-memory (local) or Firestore (durable across scale-to-zero).
store = get_store()

_BASIC = HTTPBasic(auto_error=False)
_USER = os.environ.get("CPOA_JUDGE_BASIC_AUTH_USER")
_PASS = os.environ.get("CPOA_JUDGE_BASIC_AUTH_PASS")


def require_auth(credentials: HTTPBasicCredentials | None = Depends(_BASIC)) -> None:
    """Enforce HTTP basic auth only when judge credentials are configured (FR-076)."""
    if not (_USER and _PASS):
        return
    ok = (
        credentials is not None
        and secrets.compare_digest(credentials.username, _USER)
        and secrets.compare_digest(credentials.password, _PASS)
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid judge credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


def _fixture_stories() -> dict[str, str]:
    doc = json.loads((REPO_ROOT / "corpus" / "cpoa_fixture_docs" / "fixtures.json").read_text())
    stories: dict[str, str] = {}
    for p in doc.get("passages", []):
        stem = p["title"].split(" — ")[0].strip()
        stories[stem] = p["text"]
    return stories


def _serialize_run(run_id: str, result, narrative: dict) -> dict:
    return {
        "run_id": run_id,
        "candidate_agent_id": result.manifest.candidate_agent_id,
        "agent_name": result.manifest.name,
        "decision": result.decision,
        "blockers": result.decision_result.blockers,
        "conditions": result.decision_result.conditions,
        "score": result.score.model_dump(),
        "discovery": result.discovery.model_dump(),
        "passport": result.passport.model_dump(),
        "ai_bom": result.ai_bom.model_dump(),
        "policy": result.policy.model_dump(),
        "validation_run": result.validation_run.model_dump(),
        "approval_card": result.approval_card.model_dump(),
        "evidence_bundle": result.bundle.model_dump(),
        "events": [e.model_dump() for e in result.events],
        "narrative": narrative,
        "candidate_manifest": result.manifest.model_dump(),
    }


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "llm_available": llm_available(), "fixtures": len(list_fixture_names())}


@app.get("/api/fixtures", dependencies=[Depends(require_auth)])
def list_fixtures() -> list[dict]:
    expected = load_expected()
    stories = _fixture_stories()
    out = []
    for name in list_fixture_names():
        m = load_manifest_by_name(name)
        spec = expected.get(name, {})
        out.append({
            "name": name,
            "agent_name": m.name,
            "origin": m.origin,
            "tier": spec.get("tier", "stretch"),
            "expected_decision": spec.get("expected_decision")
            or (spec.get("allowed_decisions") or ["—"])[0],
            "business_story": stories.get(name, ""),
            "tools": [{"name": t.name, "risk_tier": t.risk_tier} for t in m.tools],
            "data_classes": m.data_access.declared_data_classes,
            "autonomy": m.autonomy.level,
        })
    return out


@app.get("/api/fixtures/{name}", dependencies=[Depends(require_auth)])
def get_fixture(name: str) -> dict:
    try:
        return load_manifest_by_name(name).model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"fixture not found: {name}") from exc


@app.post("/api/runs", dependencies=[Depends(require_auth)])
def create_run(body: dict) -> dict:
    """Run onboarding for a fixture name or an inline candidate manifest."""
    if "fixture" in body:
        try:
            manifest = load_manifest_by_name(body["fixture"])
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="fixture not found") from exc
    elif "candidate_manifest" in body:
        try:
            manifest = CandidateAgentManifest(**body["candidate_manifest"])
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=422, detail=f"invalid manifest: {exc}") from exc
    else:
        raise HTTPException(status_code=422, detail="provide 'fixture' or 'candidate_manifest'")

    with span("onboarding", candidate=manifest.candidate_agent_id, origin=manifest.origin) as s:
        result = engine.onboard(manifest)
        if s is not None:
            s.set_attribute("decision", result.decision)
            s.set_attribute("readiness_score", result.score.score)
    run_id = f"run-{uuid.uuid4().hex[:12]}"
    payload = _serialize_run(run_id, result, narrate_offline(result))
    store.save(run_id, payload)
    return payload


@app.get("/api/runs/{run_id}", dependencies=[Depends(require_auth)])
def get_run(run_id: str) -> dict:
    run = store.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    return run


@app.get("/api/runs/{run_id}/download/{fmt}", dependencies=[Depends(require_auth)])
def download_bundle(run_id: str, fmt: str) -> Response:
    run = store.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    from cpoa.schemas import EvidenceBundle

    bundle = EvidenceBundle(**run["evidence_bundle"])
    base = run["candidate_agent_id"]
    if fmt == "json":
        return Response(bundle_to_json(bundle), media_type="application/json",
                        headers={"Content-Disposition": f"attachment; filename={base}.evidence.json"})
    if fmt in ("md", "markdown"):
        return Response(bundle_to_markdown(bundle), media_type="text/markdown",
                        headers={"Content-Disposition": f"attachment; filename={base}.evidence.md"})
    if fmt == "pdf":
        from cpoa.services.pdf_export import bundle_to_pdf

        return Response(bundle_to_pdf(bundle), media_type="application/pdf",
                        headers={"Content-Disposition": f"attachment; filename={base}.evidence.pdf"})
    raise HTTPException(status_code=400, detail="fmt must be 'json', 'md', or 'pdf'")


@app.post("/api/runs/{run_id}/narrate", dependencies=[Depends(require_auth)])
def narrate_run(run_id: str) -> dict:
    """Live Gemini (via Vertex/ADK) narration of a completed run. Decision stays fixed."""
    run = store.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    if not llm_available():
        raise HTTPException(status_code=503, detail="Gemini/Vertex not configured on this deployment")
    facts = {
        "agent_name": run["agent_name"],
        "decision": run["decision"],
        "score": run["score"]["score"],
        "band": run["score"]["band"],
        "blockers": run["blockers"],
        "conditions": run["conditions"],
        "findings": run["narrative"]["findings"],
        "grounded_sources": run["narrative"]["grounded_sources"],
        "workforce_lines": run["narrative"]["workforce_lines"],
    }
    try:
        from agents.run import narrate_facts

        prose = narrate_facts(facts)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Gemini narration failed: {exc}") from exc
    run["narrative"]["narrative"] = prose
    run["narrative"]["source"] = "gemini"
    store.save(run_id, run)
    return {"narrative": prose, "source": "gemini", "model": fast_model()}


@app.get("/api/grounding-comparison/{name}", dependencies=[Depends(require_auth)])
def grounding_comparison(name: str) -> dict:
    try:
        manifest = load_manifest_by_name(name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="fixture not found") from exc
    return build_grounding_comparison(manifest, run_discovery(manifest))


@app.get("/api/architecture")
def architecture() -> dict:
    return {
        "title": "ClearPoint Onboarding Agent — built on Google's agent platform",
        "intelligence": "Gemini 3.5 Flash on Vertex AI (region: global)",
        "orchestration": "Agent Development Kit (ADK) — root LlmAgent + six subagents",
        "tools": "Model Context Protocol (HTTP MCP server, NSA MCP security baseline)",
        "grounding": "Vertex AI Search (Discovery Engine) with local-corpus fallback",
        "interoperability": "Agent-to-Agent (A2A) protocol — Agent Card at /.well-known/agent.json",
        "persistence": "Firestore for durable runs across scale-to-zero",
        "runtime": "Cloud Run (web, API, MCP) deployed via Cloud Build",
        "observability": "Cloud Trace spans + SHA-256 hash-chained evidence",
        "design": "Google Stitch → Next.js + Tailwind with Material 3 tokens",
    }


# --- A2A protocol surface (Agent-to-Agent interoperability) -----------------
_A2A_CARD = {
    "name": "ClearPoint Onboarding Agent",
    "description": (
        "The AI Workforce Management onboarding gate. Inspects a candidate AI agent manifest and "
        "issues an Agent Passport, Policy Envelope, AI Bill of Materials, and a hash-chained "
        "Evidence Bundle, with a deterministic Ready / Ready with Conditions / Blocked Pending "
        "Remediation decision."
    ),
    "version": "0.4.0",
    "protocolVersion": "0.2.0",
    "capabilities": {"streaming": False, "pushNotifications": False},
    "defaultInputModes": ["application/json", "text/plain"],
    "defaultOutputModes": ["application/json", "text/plain"],
    "skills": [
        {
            "id": "onboard_agent",
            "name": "Onboard a candidate AI agent",
            "description": "Return an audit-ready onboarding decision and the workforce-management "
                           "artifacts (Passport, Policy Envelope, AI BOM, Evidence Bundle) for a "
                           "candidate agent manifest.",
            "tags": ["governance", "onboarding", "workforce", "ai-bom", "policy", "evidence"],
            "examples": ["Onboard this agent manifest and tell me if it is Ready, Conditional, or Blocked."],
        }
    ],
    "securitySchemes": {"basic": {"type": "http", "scheme": "basic"}},
    "security": [{"basic": []}],
}


@app.get("/.well-known/agent.json")
def a2a_agent_card(request: Request) -> dict:
    """A2A Agent Card — open for discovery by other enterprise agents."""
    base = str(request.base_url).rstrip("/")
    return {**_A2A_CARD, "url": f"{base}/a2a/v1"}


@app.post("/a2a/v1/message:send", dependencies=[Depends(require_auth)])
def a2a_message_send(body: dict) -> dict:
    """A2A message endpoint: accept a candidate manifest, return an onboarding task result."""
    message = body.get("message") or {}
    manifest_data = None
    for part in message.get("parts", []):
        data = part.get("data") or {}
        if isinstance(data, dict) and data.get("candidate_manifest"):
            manifest_data = data["candidate_manifest"]
            break
    if not manifest_data:
        raise HTTPException(status_code=422,
                            detail="provide message.parts[].data.candidate_manifest")
    try:
        manifest = CandidateAgentManifest(**manifest_data)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=f"invalid manifest: {exc}") from exc

    result = engine.onboard(manifest)
    run_id = f"run-{uuid.uuid4().hex[:12]}"
    store.save(run_id, _serialize_run(run_id, result, narrate_offline(result)))
    summary = f"{result.manifest.name}: {result.decision} (readiness {result.score.score}/100)."
    return {
        "task": {
            "id": run_id,
            "status": {"state": "completed"},
            "artifacts": [
                {
                    "name": "onboarding-decision",
                    "parts": [
                        {"kind": "text", "text": summary},
                        {"kind": "data", "data": {
                            "decision": result.decision,
                            "passport_readiness_score": result.score.score,
                            "passport": result.passport.model_dump(),
                            "evidence_bundle_id": result.bundle.bundle_id,
                            "evidence_bundle_hash": result.bundle.bundle_hash,
                        }},
                    ],
                }
            ],
        }
    }


# --- Discover phase (AI Workforce Management lifecycle) ---------------------
# Real HTTP crawl of A2A Agent Cards; classification against the governed
# registry surfaces unmanaged agents. The demo fleet is hosted here so the
# scanner makes real network calls but lands on data we control.


@app.get("/api/demo-fleet/{name}/.well-known/agent.json")
def demo_fleet_agent_card(name: str, request: Request) -> dict:
    """Serve a representative A2A Agent Card from the local directory.

    Public on purpose: A2A Agent Cards are a discovery surface and must be
    fetchable without credentials. The scanner walks these endpoints over the
    public network exactly as it would a real enterprise inventory.
    """
    card = agent_discovery.demo_fleet_card(name)
    if not card:
        raise HTTPException(status_code=404, detail="agent not found in directory")
    base = str(request.base_url).rstrip("/")
    return {**card, "url": f"{base}/api/demo-fleet/{name}/a2a/v1"}


@app.post("/api/discovery/scan", dependencies=[Depends(require_auth)])
def discovery_scan(body: dict | None = None, request: Request = None) -> dict:
    """Crawl a list of A2A endpoints and classify each finding.

    Body: `{ "endpoints"?: [str] }`. Omit to scan the demo fleet.
    """
    body = body or {}
    endpoints = body.get("endpoints")
    if not endpoints:
        base = str(request.base_url).rstrip("/") if request else "http://localhost:8080"
        endpoints = agent_discovery.demo_fleet_endpoints(base)
    results = agent_discovery.scan_endpoints(list(endpoints))
    summary = {
        "scanned": len(results),
        "known": sum(1 for r in results if r.status == "known"),
        "unknown": sum(1 for r in results if r.status == "unknown"),
        "unreachable": sum(1 for r in results if r.status == "unreachable"),
        "invalid": sum(1 for r in results if r.status == "invalid"),
    }
    return {
        "summary": summary,
        "results": [r.to_dict() for r in results],
        "scope": (
            "A representative A2A directory is served from this deployment so the scan "
            "exercises real network paths. The same scanner walks enterprise inventory "
            "APIs (Agent Engine catalog, Cloud Run service inventory, A2A directory "
            "services) when pointed at a customer environment."
        ),
    }


# --- Manage phase (the HR Console) ------------------------------------------
# Day-to-day lifecycle actions on onboarded agents. Each action appends a real
# hash-chained evidence event to the agent's management log.

_ALLOWED_ACTIONS = {"place_on_leave", "return_from_leave", "manager_handoff", "role_change"}


@app.get("/api/workforce/{candidate_id}/state", dependencies=[Depends(require_auth)])
def get_workforce_state(candidate_id: str) -> dict:
    """Return the current lifecycle state + event log for one agent."""
    return manage.get_state(candidate_id).to_dict()


@app.post("/api/workforce/{candidate_id}/action", dependencies=[Depends(require_auth)])
def apply_workforce_action(candidate_id: str, body: dict) -> dict:
    """Apply a lifecycle action (place_on_leave / return_from_leave /
    manager_handoff / role_change) to an onboarded agent. Appends a
    hash-chained evidence event; returns the new state and the event."""
    action = body.get("action")
    if action not in _ALLOWED_ACTIONS:
        raise HTTPException(status_code=422, detail=f"action must be one of {sorted(_ALLOWED_ACTIONS)}")
    payload = body.get("payload") or {}
    actor_id = body.get("actor_id") or "hr.console@clearpointlogic.com"
    try:
        return manage.apply_action(candidate_id, action, payload, actor_id=actor_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/workforce/states", dependencies=[Depends(require_auth)])
def list_workforce_states() -> list[dict]:
    """Return every agent currently tracked by the HR Console."""
    return manage.list_states()


# --- Govern phase (Compass control mapping) ---------------------------------


@app.get("/api/govern/controls")
def govern_controls() -> dict:
    """Live control matrix: each enforced control mapped to NSA MCP CSI /
    NIST AI RMF / EU AI Act passages from the grounding corpus."""
    return govern.control_matrix()
