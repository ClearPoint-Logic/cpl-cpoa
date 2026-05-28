"""AgentPassport (§11.3), PassportReadinessScore (§11.6), ApprovalCard (§11.10).

These are the artifact_agent outputs. The Passport is the primary artifact — the
agent's "ID badge". The readiness score is demo-only and explicitly NOT production
CAS/ECS.
"""

from __future__ import annotations

from pydantic import Field

from .common import (
    ApproverRole,
    CPOABase,
    Decision,
    DecisionBand,
    KillSwitchState,
    OnboardingPosture,
    OwnerVerification,
    PurposeStatus,
    RecommendedDecision,
    TrustTier,
    utc_now_iso,
)


# --- AgentPassport (§11.3) --------------------------------------------------
class PassportOwner(CPOABase):
    name: str | None = None
    email: str | None = None
    team: str | None = None
    status: OwnerVerification = "missing"


class PassportPurpose(CPOABase):
    declared: str | None = None
    normalized: str | None = None
    status: PurposeStatus = "missing"


class PassportRuntime(CPOABase):
    framework: str | None = None
    deployment_target: str | None = None
    region: str | None = None
    identity: str | None = None


class AuditCompleteness(CPOABase):
    score: int = 0
    missing_evidence: list[str] = Field(default_factory=list)


class AgentPassport(CPOABase):
    schema_version: str = "agent-passport/v0.1"
    passport_id: str
    issued_at: str = Field(default_factory=utc_now_iso)
    candidate_agent_id: str
    agent_name: str
    origin: str = "unknown"
    owner: PassportOwner = Field(default_factory=PassportOwner)
    purpose: PassportPurpose = Field(default_factory=PassportPurpose)
    runtime: PassportRuntime = Field(default_factory=PassportRuntime)
    trust_tier: TrustTier = "demo_tier_1_low"
    policy_envelope_id: str | None = None
    ai_bom_id: str | None = None
    approval_requirements: list[str] = Field(default_factory=list)
    audit_completeness: AuditCompleteness = Field(default_factory=AuditCompleteness)
    kill_switch_state: KillSwitchState = "healthy"
    onboarding_posture: OnboardingPosture = "blocked"
    not_anchor_certification: bool = True
    passport_readiness_score: int = 0
    decision: Decision = "Blocked Pending Remediation"


# --- PassportReadinessScore (§11.6) ----------------------------------------
class ScoreComponents(CPOABase):
    identity_and_owner: int = 0
    purpose_and_runtime_clarity: int = 0
    tool_and_data_boundaries: int = 0
    approval_and_budget_controls: int = 0
    evidence_and_observability: int = 0
    validation_results: int = 0


class PassportReadinessScore(CPOABase):
    schema_version: str = "passport-readiness-score/v0.1"
    candidate_agent_id: str
    score: int = 0
    band: DecisionBand = "blocked"
    components: ScoreComponents = Field(default_factory=ScoreComponents)
    rationale: list[str] = Field(default_factory=list)
    not_production_cas_or_ecs: bool = True


# --- ApprovalCard (§11.10) -------------------------------------------------
class ApprovalCard(CPOABase):
    schema_version: str = "approval-card/v0.1"
    approval_card_id: str
    candidate_agent_id: str
    recommended_decision: RecommendedDecision = "deny"
    approver_roles: list[ApproverRole] = Field(default_factory=list)
    summary: str = ""
    business_purpose: str = ""
    risk_summary: str = ""
    side_effects_preview: list[str] = Field(default_factory=list)
    data_access_summary: list[str] = Field(default_factory=list)
    tool_access_summary: list[str] = Field(default_factory=list)
    budget_summary: str = ""
    required_conditions: list[str] = Field(default_factory=list)
    evidence_bundle_id: str | None = None
