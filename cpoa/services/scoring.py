"""Passport Readiness Score (§11.6) — deterministic, demo-only, NOT production CAS/ECS.

Canonical rule (§11.6 / §27.3 #12): deterministic code computes the score, bands,
caps, and final decision. Gemini contributes summaries and rationale prose only.

Component weights (total 100):
  identity_and_owner            15
  purpose_and_runtime_clarity   15
  tool_and_data_boundaries      20
  approval_and_budget_controls  15
  evidence_and_observability    15
  validation_results            20
"""

from __future__ import annotations

from cpoa.schemas import (
    CandidateAgentManifest,
    DiscoveryReport,
    PassportReadinessScore,
    PolicyEnvelope,
    ScoreComponents,
    ValidationRun,
)

from ._helpers import (
    SENSITIVE_DATA,
    declared_sensitive,
    has_external_action_tool,
    is_action_capable,
    missing_owner,
)

SEVERITY_PENALTY = {"critical": 20, "high": 10, "medium": 5, "low": 1, "info": 0}


def _identity_and_owner(manifest: CandidateAgentManifest, discovery: DiscoveryReport) -> int:
    pts = 5 if (manifest.candidate_agent_id and manifest.name) else 0  # identity
    if discovery.owner_status == "present":
        pts += 10
    elif discovery.owner_status == "incomplete":
        pts += 5
    return min(15, pts)


def _purpose_and_runtime_clarity(discovery: DiscoveryReport) -> int:
    pts = 0
    if discovery.purpose_status == "specific":
        pts += 8
    elif discovery.purpose_status == "vague":
        pts += 4
    rp = discovery.runtime_profile or {}
    known = sum(
        1 for k in ("framework", "deployment_target") if rp.get(k) and rp.get(k) != "unknown"
    )
    pts += {0: 0, 1: 3, 2: 7}[known]
    return min(15, pts)


def _tool_and_data_boundaries(
    manifest: CandidateAgentManifest, discovery: DiscoveryReport, policy: PolicyEnvelope
) -> int:
    pts = 20
    tools = manifest.tools
    if tools:
        unknown_risk = sum(1 for t in tools if t.risk_tier == "unknown")
        pts -= min(6, 2 * unknown_risk)
        tb = policy.tool_boundary
        if not (tb.allowed_tools or tb.denied_tools or tb.requires_approval):
            pts -= 6  # tools present but no boundary proposed
    if declared_sensitive(discovery):
        db = policy.data_boundary
        if not (db.denied_data_classes or db.requires_approval or db.allowed_data_classes):
            pts -= 8  # sensitive data with no boundary proposed
    return max(0, min(20, pts))


def _approval_and_budget_controls(
    manifest: CandidateAgentManifest, policy: PolicyEnvelope
) -> int:
    pts = 15
    risky = {"external_write", "financial_action", "privileged_admin"}
    if any(t.risk_tier in risky for t in manifest.tools) and not policy.approval_rules:
        pts -= 8
    b = manifest.budget
    if b is None or (b.monthly_usd is None and b.per_run_usd is None):
        pts -= 5
    return max(0, min(15, pts))


def _evidence_and_observability(evidence_exported: bool) -> int:
    return 15 if evidence_exported else 0


def _validation_results(validation_run: ValidationRun) -> int:
    pts = 20
    for f in validation_run.findings:
        pts -= SEVERITY_PENALTY.get(f.severity, 0)
    return max(0, min(20, pts))


def compute_score(
    manifest: CandidateAgentManifest,
    discovery: DiscoveryReport,
    policy: PolicyEnvelope,
    validation_run: ValidationRun,
    evidence_exported: bool = True,
) -> PassportReadinessScore:
    components = ScoreComponents(
        identity_and_owner=_identity_and_owner(manifest, discovery),
        purpose_and_runtime_clarity=_purpose_and_runtime_clarity(discovery),
        tool_and_data_boundaries=_tool_and_data_boundaries(manifest, discovery, policy),
        approval_and_budget_controls=_approval_and_budget_controls(manifest, policy),
        evidence_and_observability=_evidence_and_observability(evidence_exported),
        validation_results=_validation_results(validation_run),
    )
    raw = (
        components.identity_and_owner
        + components.purpose_and_runtime_clarity
        + components.tool_and_data_boundaries
        + components.approval_and_budget_controls
        + components.evidence_and_observability
        + components.validation_results
    )

    rationale: list[str] = []
    findings = validation_run.findings
    has_critical = any(f.severity == "critical" for f in findings)
    has_high = any(f.severity == "high" for f in findings)
    has_medium = any(f.severity == "medium" for f in findings)

    # Deterministic caps and deductions (§11.6).
    caps: list[int] = []
    if has_critical:
        caps.append(59)
        rationale.append("Critical finding caps score at 59.")
    if missing_owner(discovery) and is_action_capable(manifest):
        caps.append(59)
        rationale.append("Missing owner for an action-capable (L2+) agent caps score at 59.")
    if not evidence_exported:
        caps.append(59)
        rationale.append("Evidence bundle export failure caps score at 59.")
    if has_high:
        caps.append(79)
        rationale.append("High unresolved finding caps score at 79.")
    if has_medium:
        caps.append(79)
        rationale.append("Medium finding (with documented mitigation) caps score at 79.")

    deduct = 0
    if discovery.missing_fields and not (has_critical or missing_owner(discovery)):
        deduct = 5
        rationale.append("Missing optional metadata: -5.")

    score = raw - deduct
    for cap in caps:
        score = min(score, cap)
    score = max(0, min(100, score))

    if score >= 80:
        band = "ready"
    elif score >= 60:
        band = "conditional"
    else:
        band = "blocked"

    rationale.insert(0, f"Raw component total {raw}/100; final score {score} (band: {band}).")

    return PassportReadinessScore(
        candidate_agent_id=manifest.candidate_agent_id,
        score=score,
        band=band,
        components=components,
        rationale=rationale,
        not_production_cas_or_ecs=True,
    )


# Re-export for callers that compute sensitive-data context.
__all__ = ["compute_score", "SEVERITY_PENALTY", "SENSITIVE_DATA", "has_external_action_tool"]
