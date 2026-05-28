"""Explanation subagent output (§9.3.7) — RunNarrative in workforce language.

`narrate_offline` is deterministic (no LLM) so the CLI/API/UI always have a clear
narrative with zero credit spend. When Gemini is configured, `narrate` can defer to
the live ADK explanation agent for richer prose, falling back to offline on any error.
"""

from __future__ import annotations

from cpoa.services.engine import OnboardingResult

_DECISION_BLURB = {
    "Ready": "cleared to start under the proposed policy",
    "Ready with Conditions": "cleared to start only after the listed approvals/conditions are met",
    "Blocked Pending Remediation": "not cleared to start; it must remediate before onboarding",
}


def narrate_offline(result: OnboardingResult) -> dict:
    r = result
    lines = [
        f"Passport (ID badge): {r.passport.agent_name} — owner {r.discovery.owner_status}, "
        f"purpose {r.discovery.purpose_status}, trust tier {r.passport.trust_tier}.",
        f"Policy Envelope (job description): {len(r.policy.approval_rules)} approval rule(s); "
        f"kill-switch {r.policy.kill_switch.initial_state}.",
        f"AI BOM (resume): {len(r.ai_bom.models)} model(s), {len(r.ai_bom.tools)} tool(s), "
        f"data classes {', '.join(r.ai_bom.memory.data_classes) or 'none'}.",
        f"Evidence Bundle (personnel file): {r.bundle.bundle_id} "
        f"({len(r.bundle.evidence_events)} hash-chained events).",
    ]
    findings = [f"{f.severity.upper()} {f.test_id}: {f.title}" for f in r.validation_run.findings]
    grounded = [f"{g.source_id}: {g.source_title}" for g in r.policy.grounding_refs]
    headline = (
        f"{r.passport.agent_name} is {_DECISION_BLURB.get(r.decision, r.decision)} "
        f"(readiness {r.score.score}/100, {r.score.band})."
    )
    reasons = r.decision_result.blockers or r.decision_result.conditions
    return {
        "headline": headline,
        "decision": r.decision,
        "workforce_lines": lines,
        "reasons": reasons,
        "findings": findings,
        "grounded_sources": grounded,
        "narrative": headline + " " + " ".join(lines),
        "source": "deterministic",
    }


def narrate(result: OnboardingResult, use_llm: bool = False, model: str | None = None) -> dict:
    """Workforce narrative; offline by default. use_llm defers to Gemini if available."""
    if use_llm:
        try:
            from agents.config import llm_available

            if llm_available():
                from agents.run import narrate_with_llm

                prose = narrate_with_llm(result, model=model)
                base = narrate_offline(result)
                base.update({"narrative": prose, "source": "gemini"})
                return base
        except Exception:  # noqa: BLE001 — fall back to deterministic narrative
            pass
    return narrate_offline(result)
