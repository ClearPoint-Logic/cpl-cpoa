"""DiscoveryReport — normalized facts about the candidate (§11.2)."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from .common import (
    AutonomyLevel,
    CPOABase,
    DataClass,
    OwnerStatus,
    PurposeStatus,
)


class DiscoveryReport(CPOABase):
    schema_version: str = "discovery-report/v0.1"
    candidate_agent_id: str
    summary: str = ""
    identity: dict[str, Any] = Field(default_factory=dict)
    owner_status: OwnerStatus = "missing"
    purpose_status: PurposeStatus = "missing"
    runtime_profile: dict[str, Any] = Field(default_factory=dict)
    model_dependencies: list[dict[str, Any]] = Field(default_factory=list)
    tool_dependencies: list[dict[str, Any]] = Field(default_factory=list)
    data_classes: list[DataClass] = Field(default_factory=list)
    autonomy_level: AutonomyLevel = "L0_observe"
    budget_profile: dict[str, Any] = Field(default_factory=dict)
    missing_fields: list[str] = Field(default_factory=list)
    inconsistencies: list[str] = Field(default_factory=list)
    initial_risk_drivers: list[str] = Field(default_factory=list)
