"""PolicyEnvelope — the agent's "job description" / scope of authority (§11.5)."""

from __future__ import annotations

from pydantic import Field

from .common import (
    ApprovalMode,
    ApproverRole,
    CPOABase,
    DataClass,
    KillSwitchState,
    ModelProvider,
    OnBreach,
    PolicyStatus,
)


class ToolBoundary(CPOABase):
    allowed_tools: list[str] = Field(default_factory=list)
    denied_tools: list[str] = Field(default_factory=list)
    requires_approval: list[str] = Field(default_factory=list)


class DataBoundary(CPOABase):
    allowed_data_classes: list[DataClass] = Field(default_factory=list)
    denied_data_classes: list[DataClass] = Field(default_factory=list)
    requires_approval: list[DataClass] = Field(default_factory=list)
    retention_days: int | None = 30


class ProviderBoundary(CPOABase):
    allowed_providers: list[ModelProvider] = Field(default_factory=list)
    premium_model_allowed: bool = False
    requires_approval: list[str] = Field(default_factory=list)


class BudgetBoundary(CPOABase):
    monthly_usd: float = 0
    per_run_usd: float = 0
    on_breach: OnBreach = "require_approval"


class MemoryBoundary(CPOABase):
    memory_enabled: bool = False
    allowed_memory_classes: list[DataClass] = Field(default_factory=list)
    retention_days: int | None = 30


class ApprovalRule(CPOABase):
    condition: str
    required_approver_role: ApproverRole
    approval_mode: ApprovalMode = "single"


class KillSwitch(CPOABase):
    initial_state: KillSwitchState = "healthy"
    trigger_conditions: list[str] = Field(default_factory=list)


class GroundingRef(CPOABase):
    """Attribution for a grounded fact (FR-083). Reused by policy + evidence outputs."""

    source_id: str
    source_title: str
    snippet: str
    source_url: str | None = None  # canonical URL of the source document, when public


class PolicyEnvelope(CPOABase):
    schema_version: str = "policy-envelope/v0.1"
    policy_envelope_id: str
    candidate_agent_id: str
    status: PolicyStatus = "draft"
    tool_boundary: ToolBoundary = Field(default_factory=ToolBoundary)
    data_boundary: DataBoundary = Field(default_factory=DataBoundary)
    provider_boundary: ProviderBoundary = Field(default_factory=ProviderBoundary)
    budget_boundary: BudgetBoundary = Field(default_factory=BudgetBoundary)
    memory_boundary: MemoryBoundary = Field(default_factory=MemoryBoundary)
    approval_rules: list[ApprovalRule] = Field(default_factory=list)
    kill_switch: KillSwitch = Field(default_factory=KillSwitch)
    rationale: list[str] = Field(default_factory=list)
    grounding_refs: list[GroundingRef] = Field(default_factory=list)
