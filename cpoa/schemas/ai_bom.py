"""AI Bill of Materials — the agent's "résumé" (§11.4).

Every model/tool/data/memory/runtime entry carries ``source`` + ``confidence``
provenance; self-reported claims are never treated as verified facts (§11.4).
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .common import (
    Confidence,
    CPOABase,
    Criticality,
    DataClass,
    ModelProvider,
    ModelPurpose,
    PromptStorage,
    ProvenanceSource,
    RiskTier,
    SideEffects,
    ToolProtocol,
    utc_now_iso,
)


class Provenance(CPOABase):
    source: ProvenanceSource
    confidence: Confidence


class BomModelEntry(Provenance):
    provider: ModelProvider = "unknown"
    model: str
    purpose: ModelPurpose = "unknown"
    criticality: Criticality = "optional"


class BomToolEntry(Provenance):
    tool_id: str
    name: str
    protocol: ToolProtocol = "unknown"
    risk_tier: RiskTier = "unknown"
    side_effects: SideEffects = "unknown"


class BomDataEntry(Provenance):
    data_class: DataClass
    description: str | None = None


class BomRuntimeEntry(Provenance):
    name: str
    version: str | None = None
    detail: str | None = None


class PromptEntry(CPOABase):
    name: str
    hash: str  # "sha256:..."
    storage: PromptStorage = "not_included"


class BomMemory(CPOABase):
    enabled: bool = False
    retention_days: int | None = None
    data_classes: list[DataClass] = Field(default_factory=list)


class AIBOM(CPOABase):
    schema_version: str = "ai-bom/v0.1"
    ai_bom_id: str
    candidate_agent_id: str
    generated_at: str = Field(default_factory=utc_now_iso)
    models: list[BomModelEntry] = Field(default_factory=list)
    prompts_or_instructions: list[PromptEntry] = Field(default_factory=list)
    tools: list[BomToolEntry] = Field(default_factory=list)
    data_sources: list[BomDataEntry] = Field(default_factory=list)
    memory: BomMemory = Field(default_factory=BomMemory)
    runtime_dependencies: list[BomRuntimeEntry] = Field(default_factory=list)
    registry_metadata: dict[str, Any] = Field(default_factory=dict)
    known_unknowns: list[str] = Field(default_factory=list)
