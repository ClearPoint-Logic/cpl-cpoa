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
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from agents.config import llm_available
from agents.explanation import narrate_offline
from cpoa.evals import load_expected
from cpoa.loader import REPO_ROOT, list_fixture_names, load_manifest_by_name
from cpoa.schemas import CandidateAgentManifest
from cpoa.services import engine
from cpoa.services.discovery import run_discovery
from cpoa.services.exports import bundle_to_json, bundle_to_markdown
from cpoa.services.grounding import build_grounding_comparison

app = FastAPI(title="ClearPoint Onboarding Agent API", version="0.4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CPOA_CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory run store (CPOA_STORAGE_MODE=local). Sufficient for the demo lifetime.
RUNS: dict[str, dict] = {}

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

    result = engine.onboard(manifest)
    run_id = f"run-{uuid.uuid4().hex[:12]}"
    payload = _serialize_run(run_id, result, narrate_offline(result))
    RUNS[run_id] = payload
    return payload


@app.get("/api/runs/{run_id}", dependencies=[Depends(require_auth)])
def get_run(run_id: str) -> dict:
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    return run


@app.get("/api/runs/{run_id}/download/{fmt}", dependencies=[Depends(require_auth)])
def download_bundle(run_id: str, fmt: str) -> Response:
    run = RUNS.get(run_id)
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
    raise HTTPException(status_code=400, detail="fmt must be 'json' or 'md'")


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
        "title": "ClearPoint Onboarding Agent — Google stack",
        "intelligence": "Gemini via Vertex AI",
        "orchestration": "Agent Development Kit (ADK) — root LlmAgent + 6 subagents",
        "tools": "Model Context Protocol (HTTP MCP server, NSA security baseline)",
        "grounding": "Vertex AI Search / RAG with local corpus fallback",
        "runtime": "Agent Engine (orchestrator) + Cloud Run (UI, API, MCP)",
        "observability": "Cloud Logging / Trace + hash-chained evidence",
        "design": "Google Stitch → Next.js + Tailwind with CPL brand tokens",
    }
