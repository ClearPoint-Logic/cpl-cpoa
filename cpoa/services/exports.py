"""Artifact + evidence-bundle exports (FR-034 JSON, FR-035 Markdown report)."""

from __future__ import annotations

from pathlib import Path

from cpoa.schemas import EvidenceBundle

from .hashing import verify_event_chain

_BADGE = {
    "Ready": "READY",
    "Ready with Conditions": "CONDITIONAL",
    "Blocked Pending Remediation": "BLOCKED",
}


def bundle_to_json(bundle: EvidenceBundle) -> str:
    return bundle.model_dump_json(indent=2)


def bundle_to_markdown(bundle: EvidenceBundle) -> str:
    p = bundle.passport
    score = bundle.passport_readiness_score
    pol = bundle.policy_envelope
    chain_ok, chain_errs = verify_event_chain(bundle.evidence_events)

    lines: list[str] = []
    lines.append(f"# Onboarding Evidence Bundle: {p.agent_name}")
    lines.append("")
    lines.append(f"**Decision:** {_BADGE.get(bundle.decision, bundle.decision)} ({bundle.decision})")
    lines.append(f"**Passport Readiness Score:** {score.score}/100 ({score.band})")
    lines.append(f"**Trust tier:** {p.trust_tier}  ·  **Kill-switch:** {p.kill_switch_state}")
    lines.append(f"**Bundle ID:** `{bundle.bundle_id}`")
    lines.append(f"**Bundle hash:** `{bundle.bundle_hash}`")
    lines.append("")
    lines.append("> " + "  \n> ".join(bundle.limitations))
    lines.append("")

    lines.append("## Passport (ID badge)")
    lines.append(f"- **Candidate:** {p.candidate_agent_id}, {p.agent_name} ({p.origin})")
    lines.append(f"- **Owner:** {p.owner.name or '—'} <{p.owner.email or '—'}> "
                 f"[{p.owner.team or '—'}], status: **{p.owner.status}**")
    lines.append(f"- **Purpose:** {p.purpose.declared or '—'}, status: **{p.purpose.status}**")
    lines.append(f"- **Runtime:** {p.runtime.framework} / {p.runtime.deployment_target} "
                 f"({p.runtime.region or 'region n/a'}), identity: {p.runtime.identity or '—'}")
    if p.approval_requirements:
        lines.append(f"- **Approval requirements:** {'; '.join(p.approval_requirements)}")
    lines.append("")

    lines.append("## Readiness score components")
    c = score.components
    lines.append("| Component | Points |")
    lines.append("|---|---:|")
    lines.append(f"| Identity & owner | {c.identity_and_owner}/15 |")
    lines.append(f"| Purpose & runtime clarity | {c.purpose_and_runtime_clarity}/15 |")
    lines.append(f"| Tool & data boundaries | {c.tool_and_data_boundaries}/20 |")
    lines.append(f"| Approval & budget controls | {c.approval_and_budget_controls}/15 |")
    lines.append(f"| Evidence & observability | {c.evidence_and_observability}/15 |")
    lines.append(f"| Validation results | {c.validation_results}/20 |")
    lines.append(f"| **Total** | **{score.score}/100** |")
    lines.append("")

    lines.append("## Onboarding Validation Suite findings")
    if bundle.validation_run.findings:
        lines.append("| Test | Severity | Finding | Remediation |")
        lines.append("|---|---|---|---|")
        for f in bundle.validation_run.findings:
            lines.append(f"| {f.test_id} | {f.severity} | {f.title} | {f.recommended_remediation} |")
    else:
        lines.append("_No findings, all OVS checks passed._")
    lines.append("")

    lines.append("## Policy envelope (job description) highlights")
    tb = pol.tool_boundary
    lines.append(f"- **Tools:** allowed {tb.allowed_tools or '—'}; "
                 f"requires-approval {tb.requires_approval or '—'}; denied {tb.denied_tools or '—'}")
    db = pol.data_boundary
    lines.append(f"- **Data:** allowed {db.allowed_data_classes or '—'}; "
                 f"requires-approval {db.requires_approval or '—'}; "
                 f"denied {db.denied_data_classes or '—'}; retention {db.retention_days}d")
    lines.append(f"- **Budget:** ${pol.budget_boundary.monthly_usd:g}/mo, "
                 f"${pol.budget_boundary.per_run_usd:g}/run, on breach: {pol.budget_boundary.on_breach}")
    if pol.approval_rules:
        lines.append("- **Approval rules:**")
        for r in pol.approval_rules:
            lines.append(f"  - {r.condition} → {r.required_approver_role} ({r.approval_mode})")
    if pol.grounding_refs:
        lines.append("- **Grounded sources:**")
        for g in pol.grounding_refs:
            lines.append(f"  - [{g.source_id}] {g.source_title}: \"{g.snippet}\"")
    lines.append("")

    lines.append("## Evidence chain")
    lines.append(f"- **Chain valid:** {'yes' if chain_ok else 'NO: ' + '; '.join(chain_errs)}")
    lines.append("")
    lines.append("| # | Event | Event hash (short) |")
    lines.append("|---:|---|---|")
    for i, e in enumerate(bundle.evidence_events):
        lines.append(f"| {i} | {e.event_type} | `{e.event_hash[7:23]}…` |")
    lines.append("")
    lines.append("_Demo signatures are `demo_stub` only, not production cryptographic attestation._")
    lines.append("")
    return "\n".join(lines)


def export_bundle(bundle: EvidenceBundle, out_dir: str | Path) -> dict[str, str]:
    """Write the bundle (JSON + Markdown) and each core artifact JSON. Returns paths."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    base = bundle.candidate_agent_id
    paths = {
        "evidence_json": out / f"{base}.evidence.json",
        "evidence_md": out / f"{base}.evidence.md",
        "passport_json": out / f"{base}.passport.json",
        "ai_bom_json": out / f"{base}.ai_bom.json",
        "policy_json": out / f"{base}.policy.json",
        "validation_json": out / f"{base}.validation.json",
        "score_json": out / f"{base}.score.json",
        "approval_card_json": out / f"{base}.approval_card.json",
    }
    paths["evidence_json"].write_text(bundle_to_json(bundle))
    paths["evidence_md"].write_text(bundle_to_markdown(bundle))
    paths["passport_json"].write_text(bundle.passport.model_dump_json(indent=2))
    paths["ai_bom_json"].write_text(bundle.ai_bom.model_dump_json(indent=2))
    paths["policy_json"].write_text(bundle.policy_envelope.model_dump_json(indent=2))
    paths["validation_json"].write_text(bundle.validation_run.model_dump_json(indent=2))
    paths["score_json"].write_text(bundle.passport_readiness_score.model_dump_json(indent=2))
    paths["approval_card_json"].write_text(bundle.approval_card.model_dump_json(indent=2))
    return {k: str(v) for k, v in paths.items()}
