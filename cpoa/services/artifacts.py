"""Deterministic artifact builders (§9.3.4): Agent Passport, AI BOM, Approval Card.

The Passport Readiness Score is computed by scoring.py and the decision by
decisioning.py; this module assembles the human-facing artifacts around them.
"""

from __future__ import annotations

from cpoa.schemas import (
    AIBOM,
    AgentPassport,
    ApprovalCard,
    AuditCompleteness,
    BomDataEntry,
    BomMemory,
    BomModelEntry,
    BomRuntimeEntry,
    BomToolEntry,
    CandidateAgentManifest,
    DiscoveryReport,
    PassportOwner,
    PassportPurpose,
    PassportReadinessScore,
    PassportRuntime,
    PolicyEnvelope,
    ValidationRun,
)
from cpoa.schemas.common import Decision

from .decisioning import DecisionResult

_POSTURE = {
    "Ready": "challenge_demo_ready",
    "Ready with Conditions": "conditional",
    "Blocked Pending Remediation": "blocked",
}
_OWNER_VERIFICATION = {"present": "verified", "incomplete": "incomplete", "missing": "missing"}
_RECOMMENDATION = {
    "Ready": "approve",
    "Ready with Conditions": "approve_with_conditions",
    "Blocked Pending Remediation": "deny",
}


def _trust_tier(manifest: CandidateAgentManifest, discovery: DiscoveryReport) -> str:
    tiers = {t.risk_tier for t in manifest.tools}
    data = set(discovery.data_classes)
    if (tiers & {"privileged_admin", "financial_action"}) or (data & {"regulated_phi", "secrets"}):
        return "demo_tier_3_high"
    if (tiers & {"external_write", "internal_write"}) or (
        data & {"customer_pii", "financial", "confidential"}
    ):
        return "demo_tier_2_moderate"
    return "demo_tier_1_low"


def build_ai_bom(manifest: CandidateAgentManifest, discovery: DiscoveryReport) -> AIBOM:
    models = [
        BomModelEntry(
            source="declared", confidence="medium",
            provider=m.provider, model=m.model, purpose=m.purpose, criticality=m.criticality,
        )
        for m in manifest.models
    ]
    tools = [
        BomToolEntry(
            source="declared", confidence="medium",
            tool_id=t.tool_id, name=t.name, protocol=t.protocol,
            risk_tier=t.risk_tier, side_effects=t.side_effects,
        )
        for t in manifest.tools
    ]
    data_sources = [
        BomDataEntry(source="declared", confidence="medium", data_class=dc)
        for dc in manifest.data_access.declared_data_classes
    ]
    runtime_deps = [
        BomRuntimeEntry(
            source="declared", confidence="high",
            name=f"framework:{manifest.runtime.framework}", detail=manifest.runtime.language,
        ),
        BomRuntimeEntry(
            source="declared", confidence="high",
            name=f"deployment:{manifest.runtime.deployment_target}",
            detail=manifest.runtime.region,
        ),
    ]
    known_unknowns: list[str] = ["Agent system prompt / instructions not provided to the BOM."]
    if any(m.provider == "unknown" for m in manifest.models):
        known_unknowns.append("One or more model providers are undeclared.")
    if any(t.risk_tier == "unknown" for t in manifest.tools):
        known_unknowns.append("One or more tool risk tiers are undeclared.")

    return AIBOM(
        ai_bom_id=f"bom-{manifest.candidate_agent_id}",
        candidate_agent_id=manifest.candidate_agent_id,
        models=models,
        tools=tools,
        data_sources=data_sources,
        memory=BomMemory(
            enabled=manifest.data_access.memory_enabled,
            retention_days=manifest.data_access.retention_days,
            data_classes=list(manifest.data_access.declared_data_classes),
        ),
        runtime_dependencies=runtime_deps,
        registry_metadata=manifest.registry_metadata.model_dump() if manifest.registry_metadata else {},
        known_unknowns=known_unknowns,
    )


def build_passport(
    manifest: CandidateAgentManifest,
    discovery: DiscoveryReport,
    policy: PolicyEnvelope,
    score: PassportReadinessScore,
    decision: Decision,
    ai_bom_id: str,
    evidence_complete: bool = True,
) -> AgentPassport:
    owner = manifest.owner
    return AgentPassport(
        passport_id=f"passport-{manifest.candidate_agent_id}",
        candidate_agent_id=manifest.candidate_agent_id,
        agent_name=manifest.name,
        origin=manifest.origin,
        owner=PassportOwner(
            name=owner.name if owner else None,
            email=owner.email if owner else None,
            team=owner.team if owner else None,
            status=_OWNER_VERIFICATION[discovery.owner_status],
        ),
        purpose=PassportPurpose(
            declared=manifest.declared_purpose,
            normalized=manifest.declared_purpose,
            status=discovery.purpose_status,
        ),
        runtime=PassportRuntime(
            framework=manifest.runtime.framework,
            deployment_target=manifest.runtime.deployment_target,
            region=manifest.runtime.region,
            identity=manifest.runtime.service_account_or_identity,
        ),
        trust_tier=_trust_tier(manifest, discovery),
        policy_envelope_id=policy.policy_envelope_id,
        ai_bom_id=ai_bom_id,
        approval_requirements=[r.condition for r in policy.approval_rules],
        audit_completeness=AuditCompleteness(
            score=100 if evidence_complete else 60,
            missing_evidence=[] if evidence_complete else ["evidence_bundle"],
        ),
        kill_switch_state=policy.kill_switch.initial_state,
        onboarding_posture=_POSTURE[decision],
        not_anchor_certification=True,
        passport_readiness_score=score.score,
        decision=decision,
    )


def build_approval_card(
    manifest: CandidateAgentManifest,
    discovery: DiscoveryReport,
    policy: PolicyEnvelope,
    validation_run: ValidationRun,
    decision_result: DecisionResult,
    evidence_bundle_id: str | None = None,
) -> ApprovalCard:
    roles = sorted({r.required_approver_role for r in policy.approval_rules}) or ["ai_workforce_manager"]
    side_effects = sorted(
        {t.side_effects for t in manifest.tools if t.side_effects not in ("none", "unknown")}
    )
    tool_summary = [f"{t.name} ({t.risk_tier})" for t in manifest.tools]
    risk_bits = list(discovery.initial_risk_drivers) or ["no elevated risk drivers detected"]
    conditions = decision_result.conditions or decision_result.blockers

    return ApprovalCard(
        approval_card_id=f"card-{manifest.candidate_agent_id}",
        candidate_agent_id=manifest.candidate_agent_id,
        recommended_decision=_RECOMMENDATION[decision_result.decision],
        approver_roles=roles,
        summary=f"{manifest.name}: {decision_result.decision}.",
        business_purpose=manifest.declared_purpose or "(no purpose declared)",
        risk_summary="; ".join(risk_bits),
        side_effects_preview=side_effects,
        data_access_summary=list(discovery.data_classes),
        tool_access_summary=tool_summary,
        budget_summary=(
            f"${policy.budget_boundary.monthly_usd:g}/mo, "
            f"${policy.budget_boundary.per_run_usd:g}/run, "
            f"on breach: {policy.budget_boundary.on_breach}"
        ),
        required_conditions=conditions,
        evidence_bundle_id=evidence_bundle_id,
    )
