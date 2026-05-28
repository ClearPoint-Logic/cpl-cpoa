"""Onboarding orchestrator engine (§9.3.1, §10) — deterministic, fail-closed.

Chains the workflow of §10.4 and emits a hash-chained evidence event at every
stage. Runs with no LLM and no network so the CLI and evals are reproducible
(NFR-001/007). The ADK orchestrator and MCP tools wrap these same functions and
add Gemini-authored prose. If any stage raises, the run fails closed to Blocked
Pending Remediation (§10.3 / §27.3 #11).
"""

from __future__ import annotations

from dataclasses import dataclass

from cpoa.schemas import (
    AIBOM,
    AgentPassport,
    ApprovalCard,
    CandidateAgentManifest,
    DiscoveryReport,
    EvidenceBundle,
    EvidenceEvent,
    GroundingRef,
    KillSwitch,
    PassportReadinessScore,
    PolicyEnvelope,
    ValidationFinding,
    ValidationRun,
)

from .artifacts import build_ai_bom, build_approval_card, build_passport
from .decisioning import DecisionResult, decide
from .discovery import run_discovery
from .evidence_log import EvidenceLog, build_bundle
from .grounding import get_grounding_for_policy
from .policy import propose_policy
from .scoring import compute_score
from .tracing import span
from .validation_suite import run_validation_suite

BLOCKED = "Blocked Pending Remediation"


@dataclass
class OnboardingResult:
    manifest: CandidateAgentManifest
    discovery: DiscoveryReport
    policy: PolicyEnvelope
    validation_run: ValidationRun
    score: PassportReadinessScore
    decision_result: DecisionResult
    passport: AgentPassport
    ai_bom: AIBOM
    approval_card: ApprovalCard
    bundle: EvidenceBundle
    events: list[EvidenceEvent]

    @property
    def decision(self) -> str:
        return self.decision_result.decision


def onboard(
    manifest: CandidateAgentManifest,
    policy_pack: str = "baseline_enterprise_v0_1",
    grounding_refs: list[GroundingRef] | None = None,
    signature_mode: str = "stub",
) -> OnboardingResult:
    cid = manifest.candidate_agent_id
    log = EvidenceLog(candidate_agent_id=cid, signature_mode=signature_mode)
    log.emit("onboarding.intake.received", f"Received candidate '{manifest.name}'.", manifest,
             actor_type="system")
    log.emit("onboarding.input.validated", "Manifest shape validated.",
             {"candidate_agent_id": cid}, actor_type="system")
    try:
        with span("cpoa.discovery", candidate=cid):
            discovery = run_discovery(manifest)
        log.emit("onboarding.discovery.completed", discovery.summary, discovery,
                 actor_id="discovery_agent")

        with span("cpoa.policy", candidate=cid):
            refs = grounding_refs if grounding_refs is not None else get_grounding_for_policy(
                manifest, discovery
            )
            policy = propose_policy(manifest, discovery, policy_pack, refs)
        log.emit(
            "onboarding.policy.proposed",
            f"Proposed {len(policy.approval_rules)} approval rule(s); "
            f"kill-switch {policy.kill_switch.initial_state}.",
            policy, actor_id="policy_agent",
        )

        with span("cpoa.validation", candidate=cid):
            validation_run = run_validation_suite(manifest, discovery, policy)
        log.emit("onboarding.validation.executed", validation_run.summary, validation_run,
                 actor_id="validation_agent")

        with span("cpoa.scoring_and_decision", candidate=cid) as s:
            score = compute_score(manifest, discovery, policy, validation_run, evidence_exported=True)
            decision_result = decide(
                manifest, discovery, policy, validation_run, score, evidence_exported=True
            )
            if s is not None:
                s.set_attribute("readiness_score", score.score)
                s.set_attribute("decision", decision_result.decision)

        with span("cpoa.artifacts", candidate=cid):
            ai_bom = build_ai_bom(manifest, discovery)
            passport = build_passport(
                manifest, discovery, policy, score, decision_result.decision, ai_bom.ai_bom_id
            )
        log.emit(
            "onboarding.artifacts.generated",
            f"Passport {passport.passport_id}; readiness {score.score} ({score.band}).",
            {"passport_id": passport.passport_id, "ai_bom_id": ai_bom.ai_bom_id, "score": score.score},
            actor_id="artifact_agent",
        )

        approval_card = build_approval_card(manifest, discovery, policy, validation_run, decision_result)
        log.emit("onboarding.approval.card.generated", approval_card.summary, approval_card,
                 actor_id="artifact_agent")

        log.emit(
            "onboarding.decision.issued", f"Decision: {decision_result.decision}.",
            {"decision": decision_result.decision, "blockers": decision_result.blockers,
             "conditions": decision_result.conditions},
        )

        # Stamp the bundle_id onto the approval_card BEFORE hashing the bundle.
        # The approval_card is a field inside the bundle, so any post-hash mutation
        # would invalidate compute_bundle_hash(bundle).
        from cpoa.services.evidence_log import new_bundle_id
        bundle_id = new_bundle_id(passport.candidate_agent_id)
        approval_card.evidence_bundle_id = bundle_id

        with span("cpoa.evidence_bundle", candidate=cid):
            bundle = build_bundle(
                decision_result.decision, passport, ai_bom, policy, score, validation_run,
                approval_card, list(log.events),
                bundle_id=bundle_id,
            )
        log.emit("onboarding.evidence.bundle.exported",
                 f"Exported evidence bundle {bundle.bundle_id}.",
                 {"bundle_id": bundle.bundle_id, "bundle_hash": bundle.bundle_hash})

        return OnboardingResult(
            manifest, discovery, policy, validation_run, score, decision_result,
            passport, ai_bom, approval_card, bundle, list(log.events),
        )
    except Exception as exc:  # noqa: BLE001 — fail closed on any stage failure
        log.emit("onboarding.error.fail_closed",
                 f"Pipeline error: {type(exc).__name__}: {exc}", {"error": str(exc)},
                 actor_type="system")
        return _fail_closed_result(manifest, log, f"{type(exc).__name__}: {exc}")


def _fail_closed_result(
    manifest: CandidateAgentManifest, log: EvidenceLog, reason: str
) -> OnboardingResult:
    cid = manifest.candidate_agent_id
    discovery = DiscoveryReport(
        candidate_agent_id=cid, summary=f"fail-closed: {reason}",
        owner_status="missing", purpose_status="missing",
    )
    policy = PolicyEnvelope(
        policy_envelope_id=f"pe-{cid}", candidate_agent_id=cid, status="blocked",
        kill_switch=KillSwitch(initial_state="blocked"),
    )
    finding = ValidationFinding(
        finding_id=f"FAILCLOSED-{cid}", candidate_agent_id=cid, test_id="OV-000",
        severity="critical", title="Onboarding pipeline failed", description=reason,
        recommended_remediation="Resolve the error and re-run; the gate failed closed.",
        blocks_ready_decision=True,
    )
    validation_run = ValidationRun(
        run_id=f"vr-{cid}", candidate_agent_id=cid, tests_run=[], findings=[finding],
        summary="fail-closed", passed=False,
    )
    score = PassportReadinessScore(
        candidate_agent_id=cid, score=0, band="blocked", rationale=[f"Fail-closed: {reason}"]
    )
    decision_result = DecisionResult(
        decision=BLOCKED, blockers=[f"Pipeline failure: {reason}"],
        rationale=["Fail-closed per §10.3."],
    )
    ai_bom = AIBOM(ai_bom_id=f"bom-{cid}", candidate_agent_id=cid)
    passport = build_passport(manifest, discovery, policy, score, BLOCKED, ai_bom.ai_bom_id,
                              evidence_complete=False)
    approval_card = build_approval_card(manifest, discovery, policy, validation_run, decision_result)
    bundle = build_bundle(BLOCKED, passport, ai_bom, policy, score, validation_run,
                          approval_card, list(log.events))
    return OnboardingResult(
        manifest, discovery, policy, validation_run, score, decision_result,
        passport, ai_bom, approval_card, bundle, list(log.events),
    )
