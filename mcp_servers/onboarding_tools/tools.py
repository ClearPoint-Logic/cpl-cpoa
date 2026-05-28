"""The five onboarding MCP tools (§12.1–12.5).

Each tool wraps a deterministic engine stage and returns plain dicts plus a
hash-chained evidence event. The candidate manifest is threaded through as
context where a stage needs the raw declared facts (the §12 minimal contracts
are preserved; manifest is an additive context input). No LLM, no network.
"""

from __future__ import annotations

import uuid

from cpoa.schemas import (
    Actor,
    CandidateAgentManifest,
    DiscoveryReport,
    EvidenceEvent,
    PolicyEnvelope,
    Signature,
    Subject,
    ValidationRun,
)
from cpoa.services import artifacts as artifacts_svc
from cpoa.services import hashing
from cpoa.services.decisioning import decide
from cpoa.services.discovery import run_discovery
from cpoa.services.evidence_log import build_bundle
from cpoa.services.policy import propose_policy
from cpoa.services.scoring import compute_score
from cpoa.services.validation_suite import OV_TEST_IDS, run_validation_suite


def _evidence_event(event_type: str, summary: str, payload: object, candidate_agent_id: str,
                    trace_id: str | None, session_id: str | None,
                    previous_event_hash: str | None, actor_id: str) -> EvidenceEvent:
    ev = EvidenceEvent(
        event_id=f"evt-{uuid.uuid4().hex[:12]}",
        event_type=event_type,
        trace_id=trace_id or f"trace-{uuid.uuid4().hex[:12]}",
        session_id=session_id or f"session-{uuid.uuid4().hex[:12]}",
        actor=Actor(type="agent", id=actor_id),
        subject=Subject(candidate_agent_id=candidate_agent_id),
        summary=summary,
        payload_hash=hashing.payload_hash(payload),
    )
    hashing.link_event(ev, previous_event_hash)
    ev.signature = Signature(type="demo_stub", value="demo:" + ev.event_hash.split(":", 1)[-1][:24])
    return ev


def inspect_candidate_agent(candidate_manifest: dict, *, trace_id: str | None = None,
                            session_id: str | None = None,
                            previous_event_hash: str | None = None) -> dict:
    """§12.1 — parse and normalize a candidate manifest into a DiscoveryReport."""
    manifest = CandidateAgentManifest(**candidate_manifest)
    report = run_discovery(manifest)
    ev = _evidence_event("onboarding.discovery.completed", report.summary, report,
                         manifest.candidate_agent_id, trace_id, session_id,
                         previous_event_hash, "discovery_agent")
    return {"discovery_report": report.model_dump(), "evidence_event": ev.model_dump()}


def generate_policy_envelope(discovery_report: dict, policy_pack: str = "baseline_enterprise_v0_1",
                             *, candidate_manifest: dict, trace_id: str | None = None,
                             session_id: str | None = None,
                             previous_event_hash: str | None = None) -> dict:
    """§12.2 — propose a PolicyEnvelope from the discovery report."""
    manifest = CandidateAgentManifest(**candidate_manifest)
    discovery = DiscoveryReport(**discovery_report)
    policy = propose_policy(manifest, discovery, policy_pack)
    ev = _evidence_event(
        "onboarding.policy.proposed",
        f"Proposed {len(policy.approval_rules)} approval rule(s); "
        f"kill-switch {policy.kill_switch.initial_state}.",
        policy, manifest.candidate_agent_id, trace_id, session_id,
        previous_event_hash, "policy_agent",
    )
    return {"policy_envelope": policy.model_dump(), "evidence_event": ev.model_dump()}


def run_onboarding_validation_suite(candidate_manifest: dict, policy_envelope: dict,
                                    tests: list[str] | None = None, *,
                                    discovery_report: dict | None = None,
                                    trace_id: str | None = None, session_id: str | None = None,
                                    previous_event_hash: str | None = None) -> dict:
    """§12.4 — run OV-001..005 against the candidate and proposed policy."""
    manifest = CandidateAgentManifest(**candidate_manifest)
    policy = PolicyEnvelope(**policy_envelope)
    discovery = DiscoveryReport(**discovery_report) if discovery_report else run_discovery(manifest)
    vrun = run_validation_suite(manifest, discovery, policy, tests or list(OV_TEST_IDS))
    ev = _evidence_event("onboarding.validation.executed", vrun.summary, vrun,
                         manifest.candidate_agent_id, trace_id, session_id,
                         previous_event_hash, "validation_agent")
    return {
        "validation_run": vrun.model_dump(),
        "findings": [f.model_dump() for f in vrun.findings],
        "evidence_event": ev.model_dump(),
    }


def generate_passport_artifacts(discovery_report: dict, policy_envelope: dict, *,
                                candidate_manifest: dict, validation_run: dict,
                                trace_id: str | None = None, session_id: str | None = None,
                                previous_event_hash: str | None = None) -> dict:
    """§12.3 — generate Passport, AI BOM, Readiness Score, and Approval Card."""
    manifest = CandidateAgentManifest(**candidate_manifest)
    discovery = DiscoveryReport(**discovery_report)
    policy = PolicyEnvelope(**policy_envelope)
    vrun = ValidationRun(**validation_run)

    score = compute_score(manifest, discovery, policy, vrun, evidence_exported=True)
    decision_result = decide(manifest, discovery, policy, vrun, score, evidence_exported=True)
    ai_bom = artifacts_svc.build_ai_bom(manifest, discovery)
    passport = artifacts_svc.build_passport(
        manifest, discovery, policy, score, decision_result.decision, ai_bom.ai_bom_id
    )
    card = artifacts_svc.build_approval_card(manifest, discovery, policy, vrun, decision_result)
    ev = _evidence_event(
        "onboarding.artifacts.generated",
        f"Passport {passport.passport_id}; readiness {score.score} ({score.band}).",
        {"passport_id": passport.passport_id, "score": score.score},
        manifest.candidate_agent_id, trace_id, session_id, previous_event_hash, "artifact_agent",
    )
    return {
        "agent_passport": passport.model_dump(),
        "ai_bom": ai_bom.model_dump(),
        "passport_readiness_score": score.model_dump(),
        "approval_card": card.model_dump(),
        "decision": decision_result.decision,
        "blockers": decision_result.blockers,
        "conditions": decision_result.conditions,
        "evidence_event": ev.model_dump(),
    }


def write_evidence_bundle(agent_passport: dict, ai_bom: dict, policy_envelope: dict,
                          passport_readiness_score: dict, validation_run: dict,
                          approval_card: dict, evidence_events: list[dict]) -> dict:
    """§12.5 — assemble and hash the final evidence bundle."""
    from cpoa.schemas import (
        AIBOM,
        AgentPassport,
        ApprovalCard,
        PassportReadinessScore,
    )

    passport = AgentPassport(**agent_passport)
    bundle = build_bundle(
        decision=passport.decision,
        passport=passport,
        ai_bom=AIBOM(**ai_bom),
        policy=PolicyEnvelope(**policy_envelope),
        score=PassportReadinessScore(**passport_readiness_score),
        validation_run=ValidationRun(**validation_run),
        approval_card=ApprovalCard(**approval_card),
        events=[EvidenceEvent(**e) for e in evidence_events],
    )
    return {
        "evidence_bundle": bundle.model_dump(),
        "bundle_id": bundle.bundle_id,
        "bundle_hash": bundle.bundle_hash,
    }


# Tool registry: name -> (callable, risk tier for RBAC). Write-like tools require
# higher privilege and replay protection.
TOOL_REGISTRY = {
    "inspect_candidate_agent": (inspect_candidate_agent, "read_only"),
    "generate_policy_envelope": (generate_policy_envelope, "read_only"),
    "run_onboarding_validation_suite": (run_onboarding_validation_suite, "read_only"),
    "generate_passport_artifacts": (generate_passport_artifacts, "internal_write"),
    "write_evidence_bundle": (write_evidence_bundle, "internal_write"),
}
