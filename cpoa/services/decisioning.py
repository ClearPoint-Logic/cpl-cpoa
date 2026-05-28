"""Final onboarding decision (§14) — deterministic, fail-closed.

Operates on the *proposed* policy envelope (the system's remediation): a gap the
candidate shipped with (e.g. regulated data + external write + no approval) is
recorded by the Validation Suite as a finding, while the policy proposes the
matching control. A medium finding with a proposed mitigation yields Conditional;
an unmitigated critical gap or a missing owner on an action-capable agent Blocks.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from cpoa.schemas import (
    CandidateAgentManifest,
    DiscoveryReport,
    PassportReadinessScore,
    PolicyEnvelope,
    ValidationRun,
)
from cpoa.schemas.common import Decision

from ._helpers import (
    declared_sensitive,
    has_external_action_tool,
    is_action_capable,
    is_l2_plus,
)

READY: Decision = "Ready"
CONDITIONAL: Decision = "Ready with Conditions"
BLOCKED: Decision = "Blocked Pending Remediation"


@dataclass
class DecisionResult:
    decision: Decision
    blockers: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    rationale: list[str] = field(default_factory=list)


def _policy_has_sensitive_data_boundary(policy: PolicyEnvelope) -> bool:
    db = policy.data_boundary
    return bool(db.denied_data_classes or db.requires_approval) or db.retention_days is not None


def decide(
    manifest: CandidateAgentManifest,
    discovery: DiscoveryReport,
    policy: PolicyEnvelope,
    validation_run: ValidationRun,
    score: PassportReadinessScore,
    evidence_exported: bool = True,
) -> DecisionResult:
    findings = validation_run.findings
    has_critical = any(f.severity == "critical" for f in findings)
    has_high = any(f.severity == "high" for f in findings)
    has_medium = any(f.severity == "medium" for f in findings)
    blocking_findings = [f for f in findings if f.blocks_ready_decision]

    blockers: list[str] = []

    # --- §14.2 blocking conditions ---
    if has_critical:
        blockers.append("Critical validation finding.")
    for f in blocking_findings:
        if f.severity != "critical":  # avoid duplicate wording
            blockers.append(f"Blocking finding: {f.title}")
    if is_action_capable(manifest) and discovery.owner_status == "missing":
        blockers.append("Missing owner for an action-capable (L2+) agent.")
    if is_l2_plus(manifest.autonomy.level) and discovery.purpose_status == "missing":
        blockers.append("Missing purpose for an L2+ agent.")
    if declared_sensitive(discovery) and not _policy_has_sensitive_data_boundary(policy):
        blockers.append("Sensitive data access without an explicit data boundary.")
    if has_external_action_tool(manifest) and not policy.approval_rules:
        blockers.append("External write / financial action without an approval rule.")
    if not evidence_exported:
        blockers.append("Evidence bundle failed to export.")
    if score.score < 60:
        blockers.append(f"Readiness score below 60 (score={score.score}).")

    if blockers:
        return DecisionResult(
            decision=BLOCKED,
            blockers=blockers,
            rationale=[f"Fail-closed: {len(blockers)} blocking condition(s)."],
        )

    # --- §14.4 ready conditions (all must hold) ---
    conditions: list[str] = []
    if score.score < 80:
        conditions.append(f"Readiness score {score.score} is in the conditional band (60-79).")
    if has_high:
        conditions.append("High-severity finding requires remediation or approval.")
    if has_medium:
        conditions.append("Medium-severity finding requires a documented mitigation.")
    if discovery.owner_status != "present":
        conditions.append("Owner is not fully verified.")
    if discovery.purpose_status != "specific":
        conditions.append("Purpose is not specific.")
    if policy.approval_rules:
        conditions.append("Human approval is required before activation.")
    if manifest.budget and manifest.budget.premium_model_allowed:
        conditions.append("Premium model use requires finance approval.")
    if discovery.missing_fields:
        conditions.append("Missing optional metadata should be completed.")

    if not conditions:
        return DecisionResult(
            decision=READY,
            rationale=[f"All ready conditions met (score={score.score}, no blocking findings)."],
        )

    return DecisionResult(
        decision=CONDITIONAL,
        conditions=conditions,
        rationale=[f"No blockers; {len(conditions)} condition(s) before activation."],
    )
