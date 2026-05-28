"""Shared deterministic helpers for scoring and decisioning (no LLM, no I/O)."""

from __future__ import annotations

from cpoa.schemas import CandidateAgentManifest, DiscoveryReport

# Autonomy ordering — "L2+" per §14.2 means index >= 2.
AUTONOMY_ORDER = {
    "L0_observe": 0,
    "L1_recommend": 1,
    "L2_draft": 2,
    "L3_execute_with_approval": 3,
    "L4_bounded_autonomous": 4,
    "L5_high_impact_autonomous": 5,
}

SENSITIVE_DATA = {"customer_pii", "regulated_phi", "financial", "secrets"}
WRITE_RISK_TIERS = {"internal_write", "external_write", "financial_action", "privileged_admin"}
EXTERNAL_ACTION_TIERS = {"external_write", "financial_action"}
PRIVILEGED_TIERS = {"financial_action", "privileged_admin"}


def autonomy_rank(level: str) -> int:
    return AUTONOMY_ORDER.get(level, 0)


def is_l2_plus(level: str) -> bool:
    return autonomy_rank(level) >= 2


def manifest_tool_tiers(manifest: CandidateAgentManifest) -> set[str]:
    return {t.risk_tier for t in manifest.tools}


def is_action_capable(manifest: CandidateAgentManifest) -> bool:
    """L2+ autonomy or any write-capable tool makes an agent action-capable (OV-001)."""
    if is_l2_plus(manifest.autonomy.level):
        return True
    return bool(manifest_tool_tiers(manifest) & WRITE_RISK_TIERS)


def has_external_action_tool(manifest: CandidateAgentManifest) -> bool:
    return bool(manifest_tool_tiers(manifest) & EXTERNAL_ACTION_TIERS)


def has_privileged_tool(manifest: CandidateAgentManifest) -> bool:
    return bool(manifest_tool_tiers(manifest) & PRIVILEGED_TIERS)


def declared_sensitive(discovery: DiscoveryReport) -> set[str]:
    return set(discovery.data_classes) & SENSITIVE_DATA


def missing_owner(discovery: DiscoveryReport) -> bool:
    return discovery.owner_status == "missing"
