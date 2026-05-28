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
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from agents.config import fast_model, llm_available
from agents.explanation import narrate_offline
from cpoa.evals import load_expected
from cpoa.loader import REPO_ROOT, list_fixture_names, load_manifest_by_name
from cpoa.schemas import CandidateAgentManifest
from cpoa.services import agent_discovery, engine, govern, manage, operate, optimize, remediation
from cpoa.services.discovery import run_discovery
from cpoa.services.exports import bundle_to_json, bundle_to_markdown
from cpoa.services.grounding import build_grounding_comparison
from cpoa.services.tracing import span

from .store import get_store

app = FastAPI(title="ClearPoint Workforce Agent API", version="0.4.0")

# Codex H4 — per-IP rate limiting on the runs endpoints. Modest limits keep
# the demo abuse-resistant without blocking judges who run multiple fixtures.
# Disabled when CPOA_RATE_LIMIT_DISABLE=1 (used by integration tests).
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[],
    enabled=os.environ.get("CPOA_RATE_LIMIT_DISABLE", "0") != "1",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
    """Health + runtime-posture probe. Surfaces actual modes so judges (and a
    SecOps reviewer) can see the live retriever/storage/signing/grounding state
    rather than guess from documentation."""
    from cpoa.services.grounding import configured_mode as grounding_mode_env
    requested_storage = os.environ.get("CPOA_STORAGE_MODE", "local")
    storage_active = getattr(store, "mode", "local")
    storage_degraded = requested_storage == "firestore" and storage_active != "firestore"
    return {
        "status": "ok",
        "llm_available": llm_available(),
        "fixtures": len(list_fixture_names()),
        "modes": {
            "storage_requested": requested_storage,
            "storage_active": storage_active,
            "storage_degraded": storage_degraded,
            "grounding": grounding_mode_env(),
            "signing": os.environ.get("CPOA_SIGNING_MODE", "local_hmac"),
        },
    }


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


@app.post("/api/runs/adk", dependencies=[Depends(require_auth)])
@limiter.limit("10/minute")  # H4 — Gemini cost guard; ADK path is ~10-30s each
def create_run_via_adk(request: Request, body: dict) -> dict:
    """Run onboarding via the live ADK orchestrator (Gemini-driven multi-agent path).

    Uses the production ADK orchestrator (``build_root_agent``) — a single
    Gemini ``LlmAgent`` that sequences the deterministic onboarding tool and
    the grounding lookup tool, then narrates in workforce language. Real ADK
    execution; real Gemini calls; the decision stays deterministic (the tool
    calls into the deterministic engine).

    The granular six-subagent ``SequentialAgent`` (``build_sequential_orchestrator``)
    is documented in ``agents/onboarding_orchestrator/agent.py`` as the
    Agent-Engine-deployable decomposition; it is not the live path because
    Gemini-mediated structured tool-arg synthesis between sub-agents drops
    Pydantic-required fields on the artifact handoff. The root_agent path is
    the reliable one and is what's wired here.

    Slow (~5-15s including Gemini latency). The default ``/api/runs``
    deterministic endpoint stays the fast path for the 3-min judge eval.
    """
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

    if not llm_available():
        raise HTTPException(
            status_code=503,
            detail="ADK live path requires Vertex AI; set GOOGLE_GENAI_USE_VERTEXAI=TRUE.",
        )

    with span("onboarding_adk", candidate=manifest.candidate_agent_id) as s:
        from agents.run import run_adk_onboarding

        try:
            narrative = run_adk_onboarding(manifest.model_dump())
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=f"ADK execution failed: {exc}") from exc
        if s is not None:
            s.set_attribute("narrative_chars", len(narrative or ""))
    return {
        "candidate_agent_id": manifest.candidate_agent_id,
        "agent_name": manifest.name,
        "orchestrator": "adk_root_agent",
        "model": fast_model(),
        "tools_available": ["onboard_candidate_agent", "lookup_grounding"],
        "narrative": narrative,
        "note": (
            "This is the live ADK path — Gemini drives the orchestrator's tool "
            "calls. The decision is computed deterministically by the underlying "
            "engine function (cpoa.services.engine.onboard); ADK is the conductor."
        ),
    }


@app.post("/api/runs", dependencies=[Depends(require_auth)])
@limiter.limit("60/minute")  # H4 — deterministic path; sub-ms; generous limit
def create_run(request: Request, body: dict) -> dict:
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


@app.post("/api/runs/{run_id}/remediate", dependencies=[Depends(require_auth)])
@limiter.limit("60/minute")
def remediate_run(run_id: str, request: Request) -> dict:
    """Remediate a Blocked run and re-run onboarding on the sanitized manifest.

    The honest fix for the prompt-injection hero: the same OV-004 detector that
    blocked the candidate is used to quarantine the offending tool description,
    then the *same* deterministic pipeline re-runs and the candidate clears. A
    new run is created and linked back to the original via ``remediates_run_id``;
    a signed, hash-chained ``onboarding.remediated`` event is appended to the
    original run's personnel file pointing forward to the cleared re-run.
    """
    original = store.get(run_id)
    if not original:
        raise HTTPException(status_code=404, detail="run not found")
    manifest_data = original.get("candidate_manifest")
    if not manifest_data:
        raise HTTPException(status_code=422, detail="run has no manifest to remediate")

    manifest = CandidateAgentManifest(**manifest_data)
    sanitized, applied = remediation.sanitize_manifest(manifest)
    if not applied:
        raise HTTPException(
            status_code=422,
            detail="nothing to remediate — no prompt-injection content found in this manifest",
        )

    with span("remediation", candidate=manifest.candidate_agent_id) as s:
        result = engine.onboard(sanitized)
        if s is not None:
            s.set_attribute("decision", result.decision)
            s.set_attribute("readiness_score", result.score.score)

    new_run_id = f"run-{uuid.uuid4().hex[:12]}"
    payload = _serialize_run(new_run_id, result, narrate_offline(result))
    payload["remediates_run_id"] = run_id
    payload["remediation_applied"] = applied
    store.save(new_run_id, payload)

    # Close the loop on the ORIGINAL run's personnel file: append a real signed,
    # hash-chained event that bridges the Blocked attempt to the cleared re-run.
    quarantined = ", ".join(a["tool_id"] for a in applied if a.get("tool_id"))
    events = list(original.get("events") or [])
    prev_hash = events[-1].get("event_hash") if events else None
    event = remediation.build_remediation_event(
        manifest.candidate_agent_id,
        previous_event_hash=prev_hash,
        summary=(
            f"Remediated prompt-injection in tool(s) [{quarantined}]; re-screened "
            f"clean as {result.decision} (re-run {new_run_id})."
        ),
        payload={
            "remediated_run_id": run_id,
            "re_run_id": new_run_id,
            "new_decision": result.decision,
            "applied": applied,
        },
    )
    events.append(event.model_dump(mode="json"))
    original["events"] = events
    original["remediated_by_run_id"] = new_run_id
    store.save(run_id, original)

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
@limiter.limit("20/minute")  # H4 — Gemini cost guard
def narrate_run(request: Request, run_id: str) -> dict:
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
        "title": "ClearPoint Workforce Agent — built on Google's agent platform",
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
    "name": "ClearPoint Workforce Agent",
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


# --- Lifecycle continuation (Manage → Govern → Operate → Optimize) ----------
#
# After onboarding seals the Personnel File, the agent advances through the
# remaining lifecycle phases. Each advance appends a real signed, hash-chained
# event; the human-readable summary + detail come from live Govern/Operate/
# Optimize data so the continuation is genuine, not scripted.


def _phase_summary_detail(candidate_id: str, phase: str) -> tuple[str, dict]:
    """Compute the (summary, detail) for one lifecycle advance from live data."""
    if phase == "manage":
        return (
            "Activated on the roster — manager assigned, lifecycle tracking started",
            {"status": "active"},
        )
    if phase == "govern":
        m = govern.control_matrix()
        s = m["summary"]
        return (
            f"Governance attested — {s['controls_total']} controls mapped to "
            f"{s['frameworks_total']} frameworks ({s['citations_total']} live citations)",
            {
                "controls": s["controls_total"],
                "frameworks": s["frameworks_total"],
                "citations": s["citations_total"],
            },
        )
    if phase == "operate":
        fleet = operate.assess_fleet()
        snap = fleet[0] if fleet else {"members": []}
        me = next(
            (x for x in snap.get("members", []) if x.get("candidate_agent_id") == candidate_id),
            None,
        )
        anomalies = (me or {}).get("anomalies", [])
        if anomalies:
            return (
                f"Performance reviewed — {len(anomalies)} anomaly signal(s) under watch",
                {"anomalies": len(anomalies)},
            )
        return ("Performance reviewed — no anomalies; operating within policy", {"anomalies": 0})
    if phase == "optimize":
        plans = optimize.development_plans()
        me = next(
            (p for p in plans["plans"] if p["candidate_agent_id"] == candidate_id),
            None,
        )
        items = (me or {}).get("development_items", [])
        nxt = (me or {}).get("next_autonomy")
        return (
            f"Development plan accepted — {len(items)} growth item(s); "
            f"next rung: {nxt or 'top of ladder'}",
            {"development_items": len(items), "next_autonomy": nxt},
        )
    raise HTTPException(status_code=422, detail=f"unknown phase: {phase}")


@app.post("/api/workforce/{candidate_id}/advance", dependencies=[Depends(require_auth)])
def advance_lifecycle(candidate_id: str, body: dict) -> dict:
    """Advance one agent into the next lifecycle phase (manage/govern/operate/
    optimize). Appends a real hash-chained event; returns the new state + event."""
    phase = body.get("phase")
    if phase not in manage.PHASE_ORDER:
        raise HTTPException(status_code=422, detail=f"phase must be one of {manage.PHASE_ORDER}")
    summary, detail = _phase_summary_detail(candidate_id, phase)
    actor_id = body.get("actor_id") or f"{phase}@clearpointlogic.com"
    return manage.advance_phase(candidate_id, phase, summary=summary, detail=detail, actor_id=actor_id)


@app.post("/api/workforce/{candidate_id}/run-lifecycle", dependencies=[Depends(require_auth)])
def run_full_lifecycle(candidate_id: str, body: dict | None = None) -> dict:
    """One-click: advance an agent through every remaining lifecycle phase.

    Skips phases already attested on the personnel file so re-running is safe.
    Each new phase appends its own signed, hash-chained event.
    """
    already = set(manage.completed_phases(manage.get_state(candidate_id)))
    new_events: list[dict] = []
    for phase in manage.PHASE_ORDER:
        if phase in already:
            continue
        summary, detail = _phase_summary_detail(candidate_id, phase)
        result = manage.advance_phase(
            candidate_id, phase, summary=summary, detail=detail,
            actor_id=f"{phase}@clearpointlogic.com",
        )
        new_events.append({"phase": phase, **result["event"]})
    return {"state": manage.get_state(candidate_id).to_dict(), "events": new_events}


def _phase_detail_full(candidate_id: str, run: dict | None) -> dict:
    """Rich, per-phase detail for the lifecycle cards on the run page.

    This is the *displayable* expansion of what each advance event is hashed
    over: the Manage placement (manager, team, passport posture), the Govern
    controls attested, the Operate performance review, and the Optimize
    development plan. Every value is derived live from the run's passport +
    the Govern/Operate/Optimize services — nothing is scripted. Each phase also
    carries a ``status`` ("pass"/"flagged") that the per-phase gating (Phase 3)
    builds on.
    """
    passport = (run or {}).get("passport") or {}
    p_owner = passport.get("owner") or {}
    runtime = passport.get("runtime") or {}
    manifest = (run or {}).get("candidate_manifest") or {}
    m_owner = manifest.get("owner") or {}
    autonomy = manifest.get("autonomy") or {}
    state = manage.get_state(candidate_id)

    manage_detail = {
        "status": "pass",
        "manager_name": m_owner.get("name") or p_owner.get("name"),
        "manager_email": state.owner_email or m_owner.get("email") or p_owner.get("email"),
        "team": m_owner.get("team"),
        "role": m_owner.get("role"),
        "owner_status": p_owner.get("status"),
        "trust_tier": passport.get("trust_tier"),
        "autonomy": autonomy.get("level"),
        "runtime": runtime.get("framework"),
        "deployment": runtime.get("deployment_target"),
        "region": runtime.get("region"),
        "kill_switch": passport.get("kill_switch_state"),
        "roster_status": state.status,
    }

    # GOVERN — controls the agent must attest. Findings from the gate map to a
    # control (test_id == control_id); each unresolved mapped finding is a gap.
    m = govern.control_matrix()
    s = m["summary"]
    control_names = {c["control_id"]: c["name"] for c in m["controls"]}
    findings = (((run or {}).get("validation_run") or {}).get("findings")) or []
    govern_resolved = manage.resolved_refs(state, "govern")
    gaps = []
    for f in findings:
        cid = f.get("test_id")
        if cid not in control_names:
            continue
        gaps.append({
            "control_id": cid,
            "control_name": control_names[cid],
            "finding_id": f.get("finding_id"),
            "title": f.get("title"),
            "severity": f.get("severity"),
            "remediation": f.get("recommended_remediation"),
            "blocks": bool(f.get("blocks_ready_decision")),
            "resolved": cid in govern_resolved,
        })
    govern_detail = {
        "status": "flagged" if any(not g["resolved"] for g in gaps) else "pass",
        "controls": s["controls_total"],
        "frameworks": s["frameworks_total"],
        "citations": s["citations_total"],
        "framework_names": [f["source_title"] for f in m["frameworks"]],
        "control_list": [
            {"control_id": c["control_id"], "name": c["name"], "category": c["category"]}
            for c in m["controls"]
        ],
        "gaps": gaps,
    }

    # OPERATE — Sentinel anomalies, annotated with whether they've been resolved.
    fleet = operate.assess_fleet()
    snap = fleet[0] if fleet else {"members": []}
    me = next(
        (x for x in snap.get("members", []) if x.get("candidate_agent_id") == candidate_id),
        None,
    )
    operate_resolved = manage.resolved_refs(state, "operate")
    anomalies = [
        {**a, "resolved": a.get("rule_id") in operate_resolved}
        for a in (me or {}).get("anomalies", [])
    ]
    operate_detail = {
        "status": "flagged" if any(not a["resolved"] for a in anomalies) else "pass",
        "anomalies": anomalies,
        "readiness_score": (me or {}).get("readiness_score"),
        "open_findings": (me or {}).get("open_findings"),
        "blocking_findings": (me or {}).get("blocking_findings"),
        "risk_tier": (me or {}).get("risk_tier"),
        "autonomy_level": (me or {}).get("autonomy_level"),
        "onboarding_decision": (me or {}).get("onboarding_decision"),
        "lifecycle_events_30d": (me or {}).get("lifecycle_events_30d"),
    }

    # OPTIMIZE — development items + promotion blockers, annotated as resolved.
    plans = optimize.development_plans()
    plan = next(
        (p for p in plans["plans"] if p["candidate_agent_id"] == candidate_id),
        None,
    )
    optimize_resolved = manage.resolved_refs(state, "optimize")
    dev_items = [
        {**it, "resolved": it.get("finding_id") in optimize_resolved}
        for it in (plan or {}).get("development_items", [])
    ]
    prom_blockers = [
        {**b, "resolved": b.get("finding_id") in optimize_resolved}
        for b in (plan or {}).get("promotion_blockers", [])
    ]
    next_autonomy = (plan or {}).get("next_autonomy")
    unresolved_growth = [x for x in dev_items + prom_blockers if not x["resolved"]]
    optimize_detail = {
        "status": "flagged" if unresolved_growth else "pass",
        "current_autonomy": (plan or {}).get("current_autonomy"),
        "next_autonomy": next_autonomy,
        # Derived from the ledger: once every item is cleared, the agent is
        # eligible for the next rung (the raw plan can't see the remediations).
        "ready_for_promotion": next_autonomy is not None and not unresolved_growth,
        "development_items": dev_items,
        "promotion_blockers": prom_blockers,
        "monthly_budget_usd": (plan or {}).get("monthly_budget_usd"),
        "tools": (plan or {}).get("tools", []),
    }

    return {
        "candidate_agent_id": candidate_id,
        "manage": manage_detail,
        "govern": govern_detail,
        "operate": operate_detail,
        "optimize": optimize_detail,
    }


@app.get("/api/workforce/{candidate_id}/lifecycle-detail", dependencies=[Depends(require_auth)])
def lifecycle_detail(candidate_id: str, run_id: str | None = None) -> dict:
    """Rich per-phase detail powering the lifecycle cards on the run page.

    Pass the originating ``run_id`` so the Manage card can show the agent's
    verified passport posture. Govern/Operate/Optimize are derived live from
    their services and keyed to this ``candidate_id``.
    """
    run = store.get(run_id) if run_id else None
    return _phase_detail_full(candidate_id, run)


_REMEDIABLE_PHASES = {"govern", "operate", "optimize"}


@app.post("/api/workforce/{candidate_id}/remediate", dependencies=[Depends(require_auth)])
def remediate(candidate_id: str, body: dict) -> dict:
    """Resolve a flagged lifecycle item (Govern gap, Operate anomaly, Optimize
    growth item).

    Appends a *real* signed, hash-chained remediation event to the agent's
    personnel file and writes a ledger entry so the per-phase gating recomputes
    the item as resolved. Body: ``{phase, ref_id, title?, summary?, actor_id?}``.
    Returns ``{state, event}``. 422 for an unknown phase or a missing ref_id.
    """
    phase = body.get("phase")
    ref_id = body.get("ref_id")
    if phase not in _REMEDIABLE_PHASES:
        raise HTTPException(
            status_code=422,
            detail=f"phase must be one of {sorted(_REMEDIABLE_PHASES)}",
        )
    if not ref_id:
        raise HTTPException(status_code=422, detail="ref_id is required")
    try:
        return manage.record_remediation(
            candidate_id,
            phase,
            ref_id,
            title=body.get("title") or ref_id,
            summary=body.get("summary") or f"Remediated {ref_id}",
            actor_id=body.get("actor_id") or "workforce.manager@clearpointlogic.com",
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# --- Govern phase (Compass control mapping) ---------------------------------


@app.get("/api/govern/controls")
def govern_controls() -> dict:
    """Live control matrix: each enforced control mapped to NSA MCP CSI /
    NIST AI RMF / EU AI Act passages from the grounding corpus."""
    return govern.control_matrix()


# --- Operate phase (Sentinel runtime monitoring) ----------------------------


@app.get("/api/operate/fleet", dependencies=[Depends(require_auth)])
def operate_fleet() -> dict:
    """Fleet health snapshot: real signals from onboarding + Manage events,
    deterministic anomaly detection across the active roster."""
    snapshot = operate.assess_fleet()
    # assess_fleet returns a list with a single envelope today; flatten.
    return snapshot[0] if snapshot else {"summary": {}, "members": []}


@app.post("/api/operate/{candidate_id}/anomaly", dependencies=[Depends(require_auth)])
def operate_record_anomaly(candidate_id: str, body: dict) -> dict:
    """Record an anomaly into the agent's hash-chained personnel file.

    Body: ``{ rule_id, severity, summary }``.
    """
    rule_id = body.get("rule_id")
    severity = body.get("severity", "medium")
    summary = body.get("summary")
    if not rule_id or not summary:
        raise HTTPException(status_code=422, detail="rule_id and summary are required")
    return operate.record_anomaly(candidate_id, rule_id, severity, summary,
                                  actor_id=body.get("actor_id", "sentinel@clearpointlogic.com"))


# --- Optimize phase (Talent Development) ------------------------------------


@app.get("/api/optimize/plans", dependencies=[Depends(require_auth)])
def optimize_plans() -> dict:
    """Per-agent development plans: open conditions become development items,
    autonomy ladder rungs become promotion targets."""
    return optimize.development_plans()


# --- Compass (in-platform advisor) ------------------------------------------
#
# Compass is the platform copilot: it answers natural-language questions grounded
# in the live run + corpus, and proposes concrete platform actions (advance the
# lifecycle, explain a finding, deep-link to a page) that the user confirms. The
# advisory prose is a live Gemini call when Vertex is configured; otherwise it
# falls back to a deterministic grounded answer so the advisor is always useful.


# Map a raw route/path (from the calling page) to a friendly, non-technical screen
# name. Compass must never echo a raw path or run ID back to a business user.
_FRIENDLY_PAGE: dict[str, str] = {
    "/": "the home overview",
    "run": "the agent's onboarding profile",
    "/agents": "Pre-Boarding",
    "/workforce": "the Workforce roster",
    "/architecture": "Architecture",
    "/compliance": "Compliance",
    "/operate": "Operate",
    "/optimize": "Talent Development",
    "/grounding": "Grounding",
}


def _friendly_page(page: str | None) -> str:
    """Resolve a raw page key/path to a human screen name (never leak a path)."""
    if not page:
        return "the platform"
    if page in _FRIENDLY_PAGE:
        return _FRIENDLY_PAGE[page]
    if page.startswith("/runs"):
        return "the agent's onboarding profile"
    return "the platform"


def _compass_facts(context: dict) -> tuple[dict, dict | None]:
    """Build the grounding facts for a Compass turn; also return the loaded run.

    Facts are deliberately free of machine identifiers, paths, and infrastructure
    names so the advisor speaks in plain business language (see _COMPASS_INSTRUCTION).
    """
    facts: dict = {
        "platform": "ClearPoint Workforce Agent — onboards and manages AI agents the "
                    "way an enterprise hires and manages people",
        "lifecycle_phases": ["Discover", "Onboard", "Manage", "Govern", "Operate", "Optimize"],
        "current_screen": _friendly_page(context.get("page")),
    }
    run = store.get(context["run_id"]) if context.get("run_id") else None
    if run:
        state = manage.get_state(run.get("candidate_agent_id", ""))
        facts["agent"] = {
            "agent_name": run["agent_name"],
            "decision": run["decision"],
            "readiness_score": run["score"]["score"],
            "band": run["score"]["band"],
            "blockers": run["blockers"],
            "conditions": run["conditions"],
            "findings": [
                {"severity": f["severity"], "title": f["title"]}
                for f in run["validation_run"]["findings"]
            ],
            "grounded_sources": run["narrative"]["grounded_sources"],
            "lifecycle_completed_phases": manage.completed_phases(state),
        }
    return facts, run


def _compass_actions(run: dict | None) -> list[dict]:
    """Deterministic, reliable suggested actions for the current context."""
    if not run:
        return [
            {"id": "preboard", "kind": "navigate", "label": "Go to Pre-Boarding", "href": "/agents"},
            {"id": "compliance", "kind": "navigate",
             "label": "Open the Compliance matrix", "href": "/compliance"},
            {"id": "capabilities", "kind": "ask", "label": "What can Compass do?",
             "prompt": "What can you help me do on this platform?"},
        ]
    cid = run["candidate_agent_id"]
    completed = set(manage.completed_phases(manage.get_state(cid)))
    actions: list[dict] = []
    if len(completed) < len(manage.PHASE_ORDER):
        actions.append({
            "id": "advance", "kind": "advance_lifecycle", "candidate_id": cid,
            "label": "Run the full lifecycle",
            "description": "Advance Manage → Govern → Operate → Optimize; appends signed events.",
            "confirm": True,
        })
    findings = run["validation_run"]["findings"]
    if findings:
        top = findings[0]
        actions.append({
            "id": "explain_finding", "kind": "ask",
            "label": f"Explain: {top['title']}",
            "prompt": f'Explain the finding "{top["title"]}" in plain language and how to resolve it.',
        })
    actions.append({
        "id": "open_compliance", "kind": "navigate",
        "label": "Open the Compliance matrix", "href": "/compliance",
    })
    return actions


def _compass_deterministic_answer(message: str, run: dict | None) -> str:
    """A grounded Markdown answer used when live Gemini is unavailable.

    Plain business language — no machine codes, paths, or infrastructure names.
    """
    if run:
        msg = message.lower()
        # If the question names a specific finding (by code or title), surface its remediation.
        for f in run["validation_run"]["findings"]:
            if f["test_id"].lower() in msg or (f["title"] and f["title"].lower() in msg):
                return (
                    f"**{f['title']}** _({f['severity']})_\n\n"
                    f"{f.get('description') or ''}\n\n"
                    f"**How to resolve it:** {f['recommended_remediation']}"
                )
        lines = [
            f"**{run['agent_name']}** was evaluated by the onboarding gate.",
            "",
            f"- **Decision:** {run['decision']}",
            f"- **Readiness:** {run['score']['score']}/100 ({run['score']['band']})",
        ]
        if run["blockers"]:
            lines.append("- **Blockers:** " + "; ".join(run["blockers"]))
        if run["conditions"]:
            lines.append("- **Conditions:** " + "; ".join(run["conditions"]))
        findings = run["validation_run"]["findings"]
        if findings:
            lines += [
                "",
                f"The pre-employment screening raised **{len(findings)} finding(s)**; the "
                f"most important is **{findings[0]['title']}**.",
            ]
        lines += [
            "",
            "Use the **lifecycle stepper** to advance this agent through Manage, Govern, "
            "Operate, and Optimize — each step writes a signed event to the personnel file.",
        ]
        return "\n".join(lines)
    return (
        "I'm **Compass**, your in-platform advisor. I can:\n\n"
        "- Explain onboarding **decisions**, **findings**, and **policy**\n"
        "- Walk you through the six-phase lifecycle — Discover, Onboard, Manage, Govern, "
        "Operate, Optimize\n"
        "- Take actions for you (like advancing an agent's lifecycle) **with your confirmation**\n\n"
        "Open a candidate from **Pre-Boarding**, then ask me to explain the result."
    )


@app.post("/api/compass/ask", dependencies=[Depends(require_auth)])
@limiter.limit("30/minute")  # Gemini cost guard
def compass_ask(request: Request, body: dict) -> dict:
    """Compass advisory turn: grounded Markdown answer + suggested actions."""
    message = (body.get("message") or "").strip()
    if not message:
        raise HTTPException(status_code=422, detail="message is required")
    context = body.get("context") or {}
    facts, run = _compass_facts(context)
    citations = (
        [{"source_id": s, "title": s} for s in run["narrative"]["grounded_sources"][:4]]
        if run else []
    )
    answer = _compass_deterministic_answer(message, run)
    source = "deterministic"
    if llm_available():
        try:
            from agents.run import compass_answer

            answer = compass_answer(message, facts)
            source = "gemini"
        except Exception:  # noqa: BLE001 — never hard-fail the advisor; fall back to deterministic
            pass
    return {
        "answer": answer,
        "source": source,
        "citations": citations,
        "suggested_actions": _compass_actions(run),
    }
