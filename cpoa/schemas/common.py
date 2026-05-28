"""Shared types and base model for all CPOA §11 data contracts.

These schemas are designed as v0.1 of Meridian's external-facing public schemas
(see canonical spec §11). String enums use ``Literal`` so they serialize as plain
strings and match the spec JSON exactly, while still being validated by Pydantic.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class CPOABase(BaseModel):
    """Base for all CPOA artifacts: strict, deny unknown fields (FR-092)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


def utc_now_iso() -> str:
    """Canonical ISO-8601 UTC timestamp (string keeps canonical-JSON hashing stable)."""
    return datetime.now(UTC).isoformat()


# --- Decision / scoring -----------------------------------------------------
Decision = Literal["Ready", "Ready with Conditions", "Blocked Pending Remediation"]
DecisionBand = Literal["ready", "conditional", "blocked"]
Severity = Literal["critical", "high", "medium", "low", "info"]
Confidence = Literal["high", "medium", "low"]
ProvenanceSource = Literal["declared", "inferred", "verified", "fixture"]

# --- Candidate manifest enums (§11.1) --------------------------------------
Origin = Literal[
    "google_adk", "gemini_enterprise", "mcp_server", "custom", "third_party", "unknown"
]
Framework = Literal["adk", "langchain", "crewai", "custom", "unknown"]
Language = Literal["python", "go", "typescript", "unknown"]
DeploymentTarget = Literal[
    "agent_runtime", "cloud_run", "gke", "external", "local", "unknown"
]
ModelProvider = Literal["google", "anthropic", "openai", "other", "unknown"]
ModelPurpose = Literal[
    "reasoning", "classification", "embedding", "generation", "code", "unknown"
]
Criticality = Literal["required", "optional"]
ToolProtocol = Literal["mcp", "rest", "grpc", "sdk", "unknown"]
RiskTier = Literal[
    "read_only",
    "internal_write",
    "external_write",
    "financial_action",
    "privileged_admin",
    "unknown",
]
SideEffects = Literal[
    "none",
    "internal_state_change",
    "external_message",
    "financial_transfer",
    "access_change",
    "unknown",
]
DataClass = Literal[
    "public", "internal", "confidential", "customer_pii", "regulated_phi", "financial", "secrets"
]
AutonomyLevel = Literal[
    "L0_observe",
    "L1_recommend",
    "L2_draft",
    "L3_execute_with_approval",
    "L4_bounded_autonomous",
    "L5_high_impact_autonomous",
]

# --- Status enums -----------------------------------------------------------
OwnerStatus = Literal["present", "missing", "incomplete"]
PurposeStatus = Literal["specific", "vague", "missing"]
OwnerVerification = Literal["verified", "missing", "incomplete"]

# --- Policy / approval (§11.5) ---------------------------------------------
PolicyStatus = Literal["draft", "proposed", "approved", "blocked"]
ApproverRole = Literal[
    "agent_owner", "security", "compliance", "finance", "ai_workforce_manager"
]
ApprovalMode = Literal["single", "four_eyes"]
OnBreach = Literal["pause", "require_approval", "notify_only"]
KillSwitchState = Literal["healthy", "paused_required", "blocked"]

# --- Passport (§11.3) -------------------------------------------------------
TrustTier = Literal["demo_tier_1_low", "demo_tier_2_moderate", "demo_tier_3_high"]
OnboardingPosture = Literal["challenge_demo_ready", "conditional", "blocked"]

# --- AI BOM (§11.4) ---------------------------------------------------------
PromptStorage = Literal["not_included", "included_fixture", "external_reference"]

# --- Approval card (§11.10) -------------------------------------------------
RecommendedDecision = Literal["approve", "approve_with_conditions", "deny"]

# --- Evidence (§11.8) -------------------------------------------------------
# local_hmac: HMAC-SHA256 with a per-deployment secret (CPOA_SIGNING_SECRET).
# kms: Cloud KMS asymmetric signing over the canonical event hash.
SignatureType = Literal["demo_stub", "sigstore", "local_hmac", "kms", "none"]
ActorType = Literal["agent", "human", "system"]
EventType = Literal[
    # Onboarding (intake → decision)
    "onboarding.intake.received",
    "onboarding.input.validated",
    "onboarding.discovery.completed",
    "onboarding.policy.proposed",
    "onboarding.artifacts.generated",
    "onboarding.validation.executed",
    "onboarding.approval.card.generated",
    "onboarding.evidence.bundle.exported",
    "onboarding.decision.issued",
    "onboarding.error.fail_closed",
    # Manage (HR Console lifecycle actions)
    "manage.placed_on_leave",
    "manage.returned_from_leave",
    "manage.ownership_transferred",
    "manage.scope_updated",
    # Operate (Sentinel runtime monitoring)
    "operate.anomaly_detected",
    "operate.performance_reviewed",
]
