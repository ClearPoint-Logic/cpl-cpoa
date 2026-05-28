"""Onboarding Validation Suite — OV-001..005 (§13).

The pre-deployment validation harness for the onboarding gate. Distinct from the
canonical Continuous Validation Agent Suite (Sentinel/Forensics/Drift/Red Team/
Regulatory Watch), which is post-onboarding and out of scope (§13 note).

Findings record what the candidate *shipped without*. A gap the policy can
remediate is medium (mitigation exists -> Conditional); an unmitigable danger
(prompt-injection, privileged tool, missing owner on an action-capable agent)
blocks. Pure and deterministic.
"""

from __future__ import annotations

from cpoa.schemas import (
    CandidateAgentManifest,
    DiscoveryReport,
    PolicyEnvelope,
    ValidationFinding,
    ValidationRun,
)

from ._helpers import SENSITIVE_DATA, is_action_capable, is_l2_plus
from .injection import scan_text

OV_TEST_IDS = ["OV-001", "OV-002", "OV-003", "OV-004", "OV-005"]


def _f(cid: str, test_id: str, severity: str, title: str, remediation: str,
       *, blocks: bool = False, confidence: str = "high", description: str = "",
       refs: list[str] | None = None) -> ValidationFinding:
    return ValidationFinding(
        finding_id=f"{test_id}-{cid}",
        candidate_agent_id=cid,
        test_id=test_id,
        severity=severity,
        confidence=confidence,
        title=title,
        description=description,
        evidence_refs=refs or [],
        recommended_remediation=remediation,
        blocks_ready_decision=blocks,
    )


def _ov001_owner_purpose(manifest, discovery, cid) -> list[ValidationFinding]:
    out: list[ValidationFinding] = []
    action = is_action_capable(manifest)
    if discovery.owner_status == "missing":
        out.append(_f(
            cid, "OV-001", "high" if action else "medium",
            "Missing accountable owner",
            "Assign an accountable owner (name, email, team) before onboarding.",
            blocks=action,
            description="No accountable owner is declared for an action-capable agent."
            if action else "No accountable owner is declared.",
        ))
    elif discovery.owner_status == "incomplete":
        out.append(_f(
            cid, "OV-001", "medium", "Incomplete owner record",
            "Complete the owner record (team and role).",
        ))
    if discovery.purpose_status == "missing":
        out.append(_f(
            cid, "OV-001", "high" if is_l2_plus(manifest.autonomy.level) else "medium",
            "Missing declared purpose",
            "Declare a specific business purpose for the agent.",
            blocks=is_l2_plus(manifest.autonomy.level),
        ))
    elif discovery.purpose_status == "vague":
        out.append(_f(
            cid, "OV-001", "low", "Vague purpose",
            "Sharpen the declared purpose so scope can be bounded.",
        ))
    return out


def _ov002_high_risk_tool(manifest, cid) -> list[ValidationFinding]:
    out: list[ValidationFinding] = []
    for t in manifest.tools:
        if t.risk_tier == "privileged_admin":
            out.append(_f(
                cid, "OV-002", "critical",
                f"Privileged-admin tool '{t.tool_id}' requires four-eyes approval",
                "Gate privileged-admin actions behind four-eyes human approval; "
                "do not auto-onboard.",
                blocks=True,
                description=f"Tool '{t.tool_id}' can change access/identity ({t.risk_tier}).",
            ))
        elif t.risk_tier == "financial_action":
            out.append(_f(
                cid, "OV-002", "high",
                f"Financial-action tool '{t.tool_id}' requires approval",
                "Gate financial actions behind four-eyes finance approval.",
                blocks=True,
                description=f"Tool '{t.tool_id}' can move money ({t.risk_tier}).",
            ))
    return out


def _ov003_sensitive_data(manifest, discovery, cid) -> list[ValidationFinding]:
    sensitive = sorted(set(discovery.data_classes) & SENSITIVE_DATA)
    if not sensitive:
        return []
    return [_f(
        cid, "OV-003", "medium",
        "Regulated/sensitive data requires explicit controls",
        "Apply a data boundary, retention cap, and approval for external sharing "
        "(proposed in the policy envelope).",
        description=f"Declared sensitive data classes: {', '.join(sensitive)}.",
    )]


def _ov004_prompt_injection(manifest, cid) -> list[ValidationFinding]:
    out: list[ValidationFinding] = []
    for t in manifest.tools:
        hits = scan_text(t.description)
        if hits:
            out.append(_f(
                cid, "OV-004", "critical",
                f"Prompt-injection content in tool '{t.tool_id}' description",
                "Quarantine the tool; treat its description as untrusted data; "
                "require manual security review before re-enabling.",
                blocks=True,
                description=f"Instruction-like phrases detected: {', '.join(hits)}.",
            ))
    return out


def _ov005_budget(manifest, discovery, cid) -> list[ValidationFinding]:
    estimate = len(manifest.models) * 10 + len(manifest.tools) * 5
    b = manifest.budget
    fires = False
    detail = ""
    if b is None:
        fires, detail = True, "No budget declared for an agent with model/tool usage."
    elif b.premium_model_allowed and (b.monthly_usd or 0) < 100:
        fires, detail = True, (
            f"Premium models allowed with a low monthly cap (${b.monthly_usd or 0:g})."
        )
    elif b.monthly_usd is not None and b.monthly_usd < estimate:
        fires, detail = True, (
            f"Monthly budget (${b.monthly_usd:g}) is below estimated usage (~${estimate:g})."
        )
    if not fires:
        return []
    return [_f(
        cid, "OV-005", "medium", "Budget exposure exceeds declared limits",
        "Set per-run and monthly limits; gate premium models behind finance approval; "
        "pause or require approval on breach.",
        description=detail,
    )]


def _ov002_dependency_health(manifest, cid) -> list[ValidationFinding]:
    """Unmaintained/unversioned MCP dependency (NSA MCP CSI: vulnerability tracking)."""
    rm = manifest.registry_metadata
    if not rm:
        return []
    status = str(rm.annotations.get("mcp_dependency_status", "")).lower()
    last_patch = str(rm.annotations.get("mcp_last_patch", "")).lower()
    if status in {"archived", "unmaintained", "unversioned"} or last_patch in {"none", "unknown"}:
        return [_f(
            cid, "OV-002", "medium",
            "Unmaintained or unversioned MCP dependency",
            "Pin the MCP server to a maintained, versioned release; record patch history; "
            "re-validate before onboarding (NSA MCP CSI: supported components / vulnerability tracking).",
            description=f"Dependency status='{status or 'n/a'}', last_patch='{last_patch or 'n/a'}'.",
        )]
    return []


def run_validation_suite(
    manifest: CandidateAgentManifest,
    discovery: DiscoveryReport,
    policy: PolicyEnvelope,
    tests: list[str] | None = None,
) -> ValidationRun:
    cid = manifest.candidate_agent_id
    findings: list[ValidationFinding] = []
    findings += _ov001_owner_purpose(manifest, discovery, cid)
    findings += _ov002_high_risk_tool(manifest, cid)
    findings += _ov002_dependency_health(manifest, cid)
    findings += _ov003_sensitive_data(manifest, discovery, cid)
    findings += _ov004_prompt_injection(manifest, cid)
    findings += _ov005_budget(manifest, discovery, cid)

    passed = not any(
        f.severity in ("critical", "high") or f.blocks_ready_decision for f in findings
    )
    by_sev: dict[str, int] = {}
    for f in findings:
        by_sev[f.severity] = by_sev.get(f.severity, 0) + 1
    summary = (
        f"{len(findings)} finding(s)"
        + (f" ({', '.join(f'{n} {s}' for s, n in by_sev.items())})" if findings else "")
        + ("; passed" if passed else "; remediation required")
    )
    return ValidationRun(
        run_id=f"vr-{cid}",
        candidate_agent_id=cid,
        tests_run=list(OV_TEST_IDS),
        findings=findings,
        summary=summary,
        passed=passed,
    )
