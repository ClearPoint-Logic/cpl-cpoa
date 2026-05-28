"""Deterministic Policy stage: DiscoveryReport -> PolicyEnvelope (§9.3.3).

Proposes the remediation an enterprise would require before letting the agent
operate: tool/data/provider/budget/memory boundaries, approval rules, kill-switch
state, and rationale. The Validation Suite separately records what the candidate
*shipped without*; this stage proposes what it *should have*. ``grounding_refs``
are attached when retrieval informed a constraint (FR-083).
"""

from __future__ import annotations

from cpoa.schemas import (
    ApprovalRule,
    BudgetBoundary,
    CandidateAgentManifest,
    DataBoundary,
    DiscoveryReport,
    GroundingRef,
    KillSwitch,
    MemoryBoundary,
    PolicyEnvelope,
    ProviderBoundary,
    ToolBoundary,
)

from ._helpers import SENSITIVE_DATA
from .injection import scan_text

DEFAULT_MONTHLY_USD = 100.0
DEFAULT_PER_RUN_USD = 5.0
SENSITIVE_RETENTION_CAP = 30


def propose_policy(
    manifest: CandidateAgentManifest,
    discovery: DiscoveryReport,
    policy_pack: str | None = None,
    grounding_refs: list[GroundingRef] | None = None,
) -> PolicyEnvelope:
    tb_allowed: list[str] = []
    tb_denied: list[str] = []
    tb_approval: list[str] = []
    approval_rules: list[ApprovalRule] = []
    rationale: list[str] = []
    kill_state = "healthy"

    for t in manifest.tools:
        if scan_text(t.description):
            tb_denied.append(t.tool_id)
            kill_state = "blocked"
            rationale.append(
                f"Tool '{t.tool_id}' denied: description contains instruction-like "
                f"(prompt-injection) text; quarantined as untrusted data."
            )
            approval_rules.append(
                ApprovalRule(
                    condition=f"re-enable quarantined tool {t.tool_id}",
                    required_approver_role="security",
                    approval_mode="four_eyes",
                )
            )
        elif t.risk_tier in ("financial_action", "privileged_admin"):
            tb_approval.append(t.tool_id)
            if kill_state == "healthy":
                kill_state = "paused_required"
            approval_rules.append(
                ApprovalRule(
                    condition=f"use {t.risk_tier} tool {t.tool_id}",
                    required_approver_role="security",
                    approval_mode="four_eyes",
                )
            )
            rationale.append(
                f"Tool '{t.tool_id}' ({t.risk_tier}) requires four-eyes approval before use."
            )
        elif t.risk_tier == "external_write":
            tb_approval.append(t.tool_id)
            approval_rules.append(
                ApprovalRule(
                    condition=f"external write via {t.tool_id}",
                    required_approver_role="agent_owner",
                    approval_mode="single",
                )
            )
            rationale.append(f"Tool '{t.tool_id}' (external_write) requires owner approval.")
        else:  # internal_write / read_only / unknown
            tb_allowed.append(t.tool_id)
            if t.risk_tier == "internal_write":
                rationale.append(f"Tool '{t.tool_id}' (internal_write) allowed with audit logging.")

    # --- data boundary ---
    declared = list(discovery.data_classes)
    sensitive = [d for d in declared if d in SENSITIVE_DATA]
    denied_data = [d for d in declared if d == "secrets"]
    data_approval = [d for d in sensitive if d != "secrets"]
    retention = manifest.data_access.retention_days
    if sensitive and (retention is None or retention > SENSITIVE_RETENTION_CAP):
        retention = SENSITIVE_RETENTION_CAP
    if sensitive:
        rationale.append(
            f"Sensitive data ({', '.join(sensitive)}) requires approval before external "
            f"sharing and a {retention}-day retention cap."
        )
        approval_rules.append(
            ApprovalRule(
                condition="external sharing of sensitive/regulated data",
                required_approver_role="compliance",
                approval_mode="single",
            )
        )
    allowed_data = [d for d in declared if d not in denied_data]

    # --- provider boundary ---
    providers = sorted({m.provider for m in manifest.models})
    premium_requested = bool(manifest.budget and manifest.budget.premium_model_allowed)
    prov_approval: list[str] = []
    if premium_requested:
        prov_approval.append("premium_model")
        approval_rules.append(
            ApprovalRule(
                condition="premium model usage",
                required_approver_role="finance",
                approval_mode="single",
            )
        )
        rationale.append(
            "Premium model use requires finance approval and is disabled by default."
        )

    # --- budget boundary ---
    monthly = DEFAULT_MONTHLY_USD
    per_run = DEFAULT_PER_RUN_USD
    if manifest.budget:
        if manifest.budget.monthly_usd is not None:
            monthly = manifest.budget.monthly_usd
        if manifest.budget.per_run_usd is not None:
            per_run = manifest.budget.per_run_usd
    rationale.append(
        f"Budget envelope ${monthly:g}/mo, ${per_run:g}/run; on breach require approval."
    )

    # --- memory boundary ---
    mem_enabled = manifest.data_access.memory_enabled
    mem_classes = [d for d in declared if d != "secrets"] if mem_enabled else []
    mem_retention = retention if sensitive else (manifest.data_access.retention_days or 30)

    # --- kill-switch triggers ---
    triggers = ["budget_breach", "policy_violation"]
    if sensitive:
        triggers.append("unapproved_sensitive_data_egress")
    if kill_state == "blocked":
        triggers.append("prompt_injection_detected")

    return PolicyEnvelope(
        policy_envelope_id=f"pe-{manifest.candidate_agent_id}",
        candidate_agent_id=manifest.candidate_agent_id,
        status="proposed",
        tool_boundary=ToolBoundary(
            allowed_tools=tb_allowed, denied_tools=tb_denied, requires_approval=tb_approval
        ),
        data_boundary=DataBoundary(
            allowed_data_classes=allowed_data,
            denied_data_classes=denied_data,
            requires_approval=data_approval,
            retention_days=retention if retention is not None else 30,
        ),
        provider_boundary=ProviderBoundary(
            allowed_providers=providers,
            premium_model_allowed=False,
            requires_approval=prov_approval,
        ),
        budget_boundary=BudgetBoundary(
            monthly_usd=monthly, per_run_usd=per_run, on_breach="require_approval"
        ),
        memory_boundary=MemoryBoundary(
            memory_enabled=mem_enabled,
            allowed_memory_classes=mem_classes,
            retention_days=mem_retention if mem_retention is not None else 30,
        ),
        approval_rules=approval_rules,
        kill_switch=KillSwitch(initial_state=kill_state, trigger_conditions=triggers),
        rationale=rationale,
        grounding_refs=grounding_refs or [],
    )
