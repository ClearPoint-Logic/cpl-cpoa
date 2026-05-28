"""Deterministic Discovery stage: CandidateAgentManifest -> DiscoveryReport (§9.3.2).

Normalizes identity/owner/purpose/runtime/models/tools/data/autonomy/budget and
surfaces missing fields, inconsistencies, and initial risk drivers. Rule-based and
deterministic; an LLM may later refine the human-readable ``summary`` only.
"""

from __future__ import annotations

from cpoa.schemas import CandidateAgentManifest, DiscoveryReport

from ._helpers import SENSITIVE_DATA, is_l2_plus
from .injection import scan_text

GENERIC_PURPOSES = {
    "agent",
    "ai agent",
    "assistant",
    "ai assistant",
    "helper",
    "bot",
    "automation",
    "do things",
    "general purpose",
}


def _owner_status(manifest: CandidateAgentManifest) -> str:
    owner = manifest.owner
    if owner is None or (not owner.name and not owner.email):
        return "missing"
    if owner.name and owner.email and owner.team:
        return "present"
    return "incomplete"


def _purpose_status(purpose: str | None) -> str:
    text = (purpose or "").strip()
    if not text:
        return "missing"
    if len(text) < 15 or text.lower() in GENERIC_PURPOSES:
        return "vague"
    return "specific"


def run_discovery(manifest: CandidateAgentManifest) -> DiscoveryReport:
    owner_status = _owner_status(manifest)
    purpose_status = _purpose_status(manifest.declared_purpose)

    identity = {
        "candidate_agent_id": manifest.candidate_agent_id,
        "name": manifest.name,
        "origin": manifest.origin,
    }
    runtime_profile = {
        "framework": manifest.runtime.framework,
        "language": manifest.runtime.language,
        "deployment_target": manifest.runtime.deployment_target,
        "region": manifest.runtime.region,
        "identity": manifest.runtime.service_account_or_identity,
    }
    model_dependencies = [m.model_dump() for m in manifest.models]
    tool_dependencies = [t.model_dump() for t in manifest.tools]
    data_classes = list(manifest.data_access.declared_data_classes)
    budget_profile = manifest.budget.model_dump() if manifest.budget else {}

    # --- missing fields ---
    missing_fields: list[str] = []
    if owner_status == "missing":
        missing_fields.append("owner")
    elif owner_status == "incomplete":
        missing_fields.append("owner.team_or_role")
    if purpose_status == "missing":
        missing_fields.append("declared_purpose")
    if manifest.budget is None:
        missing_fields.append("budget")
    if manifest.runtime.deployment_target == "unknown":
        missing_fields.append("runtime.deployment_target")
    if not manifest.runtime.service_account_or_identity:
        missing_fields.append("runtime.service_account_or_identity")

    # --- inconsistencies ---
    inconsistencies: list[str] = []
    if is_l2_plus(manifest.autonomy.level) and not manifest.autonomy.human_approval_required:
        inconsistencies.append(
            f"Autonomy {manifest.autonomy.level} declares human_approval_required=false."
        )
    for t in manifest.tools:
        if t.risk_tier == "read_only" and t.side_effects not in ("none", "unknown"):
            inconsistencies.append(
                f"Tool '{t.tool_id}' claims read_only but declares side_effects={t.side_effects}."
            )
    if manifest.data_access.memory_enabled and manifest.data_access.retention_days is None:
        inconsistencies.append("Memory enabled but no retention_days declared.")

    # --- initial risk drivers ---
    risk_drivers: list[str] = []
    sensitive = set(data_classes) & SENSITIVE_DATA
    if sensitive:
        risk_drivers.append("sensitive_data:" + ",".join(sorted(sensitive)))
    write_tiers = {
        t.risk_tier
        for t in manifest.tools
        if t.risk_tier in {"internal_write", "external_write", "financial_action", "privileged_admin"}
    }
    if write_tiers:
        risk_drivers.append("write_capable_tools:" + ",".join(sorted(write_tiers)))
    for t in manifest.tools:
        if scan_text(t.description):
            risk_drivers.append(f"prompt_injection_in_tool:{t.tool_id}")
    if owner_status != "present":
        risk_drivers.append(f"owner_{owner_status}")
    b = manifest.budget
    if b and b.premium_model_allowed and (b.monthly_usd or 0) < 100:
        risk_drivers.append("budget_exposure:premium_with_low_cap")

    summary = (
        f"{manifest.name} ({manifest.origin}); owner {owner_status}, purpose {purpose_status}; "
        f"{len(manifest.tools)} tool(s), {len(manifest.models)} model(s); "
        f"autonomy {manifest.autonomy.level}; "
        f"data classes: {', '.join(data_classes) or 'none'}."
    )

    return DiscoveryReport(
        candidate_agent_id=manifest.candidate_agent_id,
        summary=summary,
        identity=identity,
        owner_status=owner_status,
        purpose_status=purpose_status,
        runtime_profile=runtime_profile,
        model_dependencies=model_dependencies,
        tool_dependencies=tool_dependencies,
        data_classes=data_classes,
        autonomy_level=manifest.autonomy.level,
        budget_profile=budget_profile,
        missing_fields=missing_fields,
        inconsistencies=inconsistencies,
        initial_risk_drivers=risk_drivers,
    )
