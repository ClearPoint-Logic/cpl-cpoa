"""CPOA §11 data contracts — v0.1 of Meridian's external-facing public schemas."""

from __future__ import annotations

from .agent_passport import (
    AgentPassport,
    ApprovalCard,
    AuditCompleteness,
    PassportOwner,
    PassportPurpose,
    PassportReadinessScore,
    PassportRuntime,
    ScoreComponents,
)
from .ai_bom import (
    AIBOM,
    BomDataEntry,
    BomMemory,
    BomModelEntry,
    BomRuntimeEntry,
    BomToolEntry,
    PromptEntry,
    Provenance,
)
from .candidate_manifest import (
    Autonomy,
    Budget,
    CandidateAgentManifest,
    DataAccess,
    ModelDependency,
    Owner,
    RegistryMetadata,
    Runtime,
    ToolDependency,
)
from .common import CPOABase, utc_now_iso
from .discovery_report import DiscoveryReport
from .evidence import (
    Actor,
    EvidenceBundle,
    EvidenceEvent,
    Signature,
    Subject,
)
from .policy_envelope import (
    ApprovalRule,
    BudgetBoundary,
    DataBoundary,
    GroundingRef,
    KillSwitch,
    MemoryBoundary,
    PolicyEnvelope,
    ProviderBoundary,
    ToolBoundary,
)
from .validation import ValidationFinding, ValidationRun

__all__ = [
    "CPOABase",
    "utc_now_iso",
    # manifest
    "CandidateAgentManifest",
    "Owner",
    "Runtime",
    "ModelDependency",
    "ToolDependency",
    "DataAccess",
    "Autonomy",
    "Budget",
    "RegistryMetadata",
    # discovery
    "DiscoveryReport",
    # passport / score / approval
    "AgentPassport",
    "PassportOwner",
    "PassportPurpose",
    "PassportRuntime",
    "AuditCompleteness",
    "PassportReadinessScore",
    "ScoreComponents",
    "ApprovalCard",
    # ai bom
    "AIBOM",
    "Provenance",
    "BomModelEntry",
    "BomToolEntry",
    "BomDataEntry",
    "BomRuntimeEntry",
    "PromptEntry",
    "BomMemory",
    # policy
    "PolicyEnvelope",
    "ToolBoundary",
    "DataBoundary",
    "ProviderBoundary",
    "BudgetBoundary",
    "MemoryBoundary",
    "ApprovalRule",
    "KillSwitch",
    "GroundingRef",
    # validation
    "ValidationFinding",
    "ValidationRun",
    # evidence
    "EvidenceEvent",
    "EvidenceBundle",
    "Signature",
    "Actor",
    "Subject",
]
