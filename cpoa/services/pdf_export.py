"""PDF evidence-bundle export (FR-035 'PDF-style report'). Pure-Python via fpdf2."""

from __future__ import annotations

from cpoa.schemas import EvidenceBundle

_BADGE = {
    "Ready": (16, 133, 87),
    "Ready with Conditions": (180, 83, 9),
    "Blocked Pending Remediation": (185, 28, 28),
}


def _ascii(s: str | None) -> str:
    return (s or "").encode("latin-1", "replace").decode("latin-1")


def bundle_to_pdf(bundle: EvidenceBundle) -> bytes:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    p = bundle.passport
    score = bundle.passport_readiness_score
    pdf = FPDF()
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()

    def cell(text: str, h: float = 5.0) -> None:
        pdf.multi_cell(0, h, _ascii(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def head(text: str) -> None:
        pdf.set_font("Helvetica", "B", 12)
        cell(text, 7)
        pdf.set_font("Helvetica", "", 10)

    pdf.set_font("Helvetica", "B", 16)
    cell(f"Onboarding Evidence Bundle - {p.agent_name}", 9)
    r, g, b = _BADGE.get(bundle.decision, (31, 38, 43))
    pdf.set_text_color(r, g, b)
    pdf.set_font("Helvetica", "B", 12)
    cell(f"{bundle.decision}  |  Readiness {score.score}/100 ({score.band})", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(1)

    head("Passport (ID badge)")
    cell(f"Candidate: {p.candidate_agent_id} ({p.origin})")
    cell(f"Owner: {p.owner.name or '-'} <{p.owner.email or '-'}> [{p.owner.status}]")
    cell(f"Purpose: {p.purpose.declared or '-'} [{p.purpose.status}]")
    cell(f"Trust tier: {p.trust_tier}  |  Kill-switch: {p.kill_switch_state}")
    if p.approval_requirements:
        cell("Approvals required: " + "; ".join(p.approval_requirements))
    pdf.ln(1)

    head("Onboarding Validation Suite")
    if bundle.validation_run.findings:
        for f in bundle.validation_run.findings:
            cell(f"[{f.severity.upper()}] {f.test_id}  {f.title}")
            cell(f"    -> {f.recommended_remediation}")
    else:
        cell("No findings - all checks passed.")
    pdf.ln(1)

    head("Evidence chain")
    cell(f"Bundle: {bundle.bundle_id}")
    cell(f"Hash: {bundle.bundle_hash}")
    for i, e in enumerate(bundle.evidence_events):
        cell(f"{i}. {e.event_type}  ({e.event_hash[7:23]}...)")
    pdf.ln(1)

    head("Limitations")
    for lim in bundle.limitations:
        cell("- " + lim)

    return bytes(pdf.output())
