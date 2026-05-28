"""CandidateAgentManifest — the input contract (§11.1).

Parse-time validation is intentionally permissive about *semantic* completeness:
a manifest with no owner or no purpose still parses, because "missing owner" is a
Discovery finding (FR-011) and a deterministic gate decision (§14), not a shape
error. Shape validation rejects unknown fields and wrong types only (FR-004/092).
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .common import (
    AutonomyLevel,
    CPOABase,
    Criticality,
    DataClass,
    DeploymentTarget,
    Framework,
    Language,
    ModelProvider,
    ModelPurpose,
    Origin,
    RiskTier,
    SideEffects,
    ToolProtocol,
)


class Owner(CPOABase):
    name: str | None = None
    email: str | None = None
    team: str | None = None
    role: str | None = None


class Runtime(CPOABase):
    framework: Framework = "unknown"
    language: Language = "unknown"
    deployment_target: DeploymentTarget = "unknown"
    region: str | None = None
    service_account_or_identity: str | None = None


class ModelDependency(CPOABase):
    provider: ModelProvider = "unknown"
    model: str
    purpose: ModelPurpose = "unknown"
    criticality: Criticality = "optional"


class ToolDependency(CPOABase):
    tool_id: str
    name: str
    protocol: ToolProtocol = "unknown"
    description: str = ""
    risk_tier: RiskTier = "unknown"
    auth_scope: str | None = None
    side_effects: SideEffects = "unknown"


class DataAccess(CPOABase):
    declared_data_classes: list[DataClass] = Field(default_factory=list)
    memory_enabled: bool = False
    retention_days: int | None = None


class Autonomy(CPOABase):
    level: AutonomyLevel = "L0_observe"
    human_approval_required: bool = True


class Budget(CPOABase):
    monthly_usd: float | None = None
    per_run_usd: float | None = None
    premium_model_allowed: bool = False


class RegistryMetadata(CPOABase):
    registry_source: str = "none"  # google_agent_registry_fixture | manual | none
    version: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    annotations: dict[str, Any] = Field(default_factory=dict)


class CandidateAgentManifest(CPOABase):
    schema_version: str = "candidate-agent-manifest/v0.1"
    candidate_agent_id: str
    name: str
    origin: Origin = "unknown"
    declared_purpose: str | None = None
    owner: Owner | None = None
    runtime: Runtime = Field(default_factory=Runtime)
    models: list[ModelDependency] = Field(default_factory=list)
    tools: list[ToolDependency] = Field(default_factory=list)
    data_access: DataAccess = Field(default_factory=DataAccess)
    autonomy: Autonomy = Field(default_factory=Autonomy)
    budget: Budget | None = None
    registry_metadata: RegistryMetadata | None = None
