"""ADK FunctionTools — the deterministic engine exposed to the Gemini orchestrator.

The tools compute everything deterministically (the decision is never the LLM's to
make, per §27.3 #12). The LlmAgent's job is to sequence tool calls and narrate the
result in workforce language, citing grounded sources.
"""

from __future__ import annotations

from cpoa.schemas import CandidateAgentManifest, DiscoveryReport, PolicyEnvelope, ValidationRun
from cpoa.services import artifacts as artifacts_svc
from cpoa.services import engine
from cpoa.services.decisioning import decide
from cpoa.services.discovery import run_discovery
from cpoa.services.grounding import LocalRetriever, get_grounding_for_policy
from cpoa.services.policy import propose_policy
from cpoa.services.scoring import compute_score
from cpoa.services.validation_suite import run_validation_suite


def onboard_candidate_agent(candidate_manifest: dict) -> dict:
    """Run the full deterministic onboarding workflow on a candidate agent manifest.

    Returns the onboarding decision, Passport Readiness Score, validation findings,
    owner/purpose status, trust tier, approval requirements, grounded sources, and
    the evidence bundle id. Use this to evaluate a candidate, then explain the result.

    Args:
        candidate_manifest: the candidate agent manifest (candidate-agent-manifest/v0.1).
    """
    manifest = CandidateAgentManifest(**candidate_manifest)
    result = engine.onboard(manifest)
    return {
        "decision": result.decision,
        "passport_readiness_score": result.score.score,
        "band": result.score.band,
        "blockers": result.decision_result.blockers,
        "conditions": result.decision_result.conditions,
        "findings": [
            {"test_id": f.test_id, "severity": f.severity, "title": f.title,
             "remediation": f.recommended_remediation}
            for f in result.validation_run.findings
        ],
        "owner_status": result.discovery.owner_status,
        "purpose_status": result.discovery.purpose_status,
        "trust_tier": result.passport.trust_tier,
        "kill_switch_state": result.passport.kill_switch_state,
        "approval_requirements": result.passport.approval_requirements,
        "grounding_refs": [
            {"source_id": g.source_id, "source_title": g.source_title}
            for g in result.policy.grounding_refs
        ],
        "evidence_bundle_id": result.bundle.bundle_id,
        "evidence_bundle_hash": result.bundle.bundle_hash,
    }


def lookup_grounding(topic: str) -> dict:
    """Look up grounded policy/security guidance from the public corpus.

    Sources: NSA MCP CSI, NIST AI RMF, EU AI Act, and CPOA's demo policy pack.

    Args:
        topic: what to look up, e.g. "regulated data retention" or "prompt injection".
    """
    refs = LocalRetriever().retrieve(topic, k=3)
    return {"sources": [
        {"source_id": r.source_id, "source_title": r.source_title, "snippet": r.snippet}
        for r in refs
    ]}


# --- Granular per-stage tools (step-by-step orchestration / MCP parity) ---
def inspect_candidate_agent(candidate_manifest: dict) -> dict:
    """Parse and normalize a candidate manifest into a discovery report (§12.1)."""
    return run_discovery(CandidateAgentManifest(**candidate_manifest)).model_dump()


def generate_policy_envelope(candidate_manifest: dict, discovery_report: dict) -> dict:
    """Propose a policy envelope (job description) from the discovery report (§12.2)."""
    manifest = CandidateAgentManifest(**candidate_manifest)
    discovery = DiscoveryReport(**discovery_report)
    refs = get_grounding_for_policy(manifest, discovery)
    return propose_policy(manifest, discovery, grounding_refs=refs).model_dump()


def run_validation(candidate_manifest: dict, discovery_report: dict, policy_envelope: dict) -> dict:
    """Run the Onboarding Validation Suite OV-001..005 (§12.4)."""
    return run_validation_suite(
        CandidateAgentManifest(**candidate_manifest),
        DiscoveryReport(**discovery_report),
        PolicyEnvelope(**policy_envelope),
    ).model_dump()


def generate_passport_artifacts(candidate_manifest: dict, discovery_report: dict,
                                policy_envelope: dict, validation_run: dict) -> dict:
    """Generate Passport, AI BOM, Readiness Score, and Approval Card (§12.3)."""
    manifest = CandidateAgentManifest(**candidate_manifest)
    discovery = DiscoveryReport(**discovery_report)
    policy = PolicyEnvelope(**policy_envelope)
    vrun = ValidationRun(**validation_run)
    score = compute_score(manifest, discovery, policy, vrun)
    decision = decide(manifest, discovery, policy, vrun, score)
    ai_bom = artifacts_svc.build_ai_bom(manifest, discovery)
    passport = artifacts_svc.build_passport(manifest, discovery, policy, score,
                                            decision.decision, ai_bom.ai_bom_id)
    card = artifacts_svc.build_approval_card(manifest, discovery, policy, vrun, decision)
    return {
        "agent_passport": passport.model_dump(),
        "ai_bom": ai_bom.model_dump(),
        "passport_readiness_score": score.model_dump(),
        "approval_card": card.model_dump(),
        "decision": decision.decision,
    }


def assemble_evidence_bundle(agent_passport: dict, ai_bom: dict, policy_envelope: dict,
                             passport_readiness_score: dict, validation_run: dict,
                             approval_card: dict) -> dict:
    """Assemble and hash the final evidence bundle — the personnel file (§12.5)."""
    from cpoa.schemas import (
        AIBOM,
        AgentPassport,
        ApprovalCard,
        PassportReadinessScore,
    )
    from cpoa.services.evidence_log import build_bundle

    passport = AgentPassport(**agent_passport)
    bundle = build_bundle(
        passport.decision, passport, AIBOM(**ai_bom), PolicyEnvelope(**policy_envelope),
        PassportReadinessScore(**passport_readiness_score), ValidationRun(**validation_run),
        ApprovalCard(**approval_card), [],
    )
    return {"evidence_bundle_id": bundle.bundle_id, "bundle_hash": bundle.bundle_hash}
