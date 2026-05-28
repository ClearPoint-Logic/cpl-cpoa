"""Optimize phase — Talent Development.

Per-agent development plans derived from real signals: the open conditions
from the Onboarding Validation Suite become the agent's "career
development items"; the autonomy level → next-level path comes from the
declared autonomy ladder; cost projection comes from the declared monthly
spend cap.

Deterministic. No LLM. Updating an agent's fixture flows into its plan.
"""

from __future__ import annotations

from cpoa.loader import list_fixture_names, load_manifest_by_name
from cpoa.services.discovery import run_discovery
from cpoa.services.policy import propose_policy
from cpoa.services.validation_suite import run_validation_suite

# Autonomy ladder rungs (canonical ordering).
_LADDER = [
    "L0_observe",
    "L1_recommend",
    "L2_draft",
    "L3_execute_with_approval",
    "L4_bounded_autonomous",
    "L5_high_impact_autonomous",
]


def _next_rung(level: str) -> str | None:
    if level not in _LADDER:
        return None
    i = _LADDER.index(level)
    return _LADDER[i + 1] if i + 1 < len(_LADDER) else None


def development_plans() -> dict:
    plans: list[dict] = []
    for name in list_fixture_names():
        try:
            manifest = load_manifest_by_name(name)
        except FileNotFoundError:
            continue
        disc = run_discovery(manifest)
        pol = propose_policy(manifest, disc)
        vr = run_validation_suite(manifest, disc, pol)
        development_items = [
            {
                "finding_id": f.finding_id,
                "title": f.title,
                "severity": f.severity,
                "remediation": f.recommended_remediation,
                "blocks_promotion": f.blocks_ready_decision,
            }
            for f in vr.findings
            if not f.blocks_ready_decision
        ]
        next_rung = _next_rung(manifest.autonomy.level)
        plans.append({
            "candidate_agent_id": manifest.candidate_agent_id,
            "name": manifest.name,
            "current_autonomy": manifest.autonomy.level,
            "next_autonomy": next_rung,
            "tools": [t.name for t in manifest.tools],
            "monthly_budget_usd": manifest.budget.monthly_usd if manifest.budget else None,
            "development_items": development_items,
            "promotion_blockers": [
                {
                    "finding_id": f.finding_id,
                    "title": f.title,
                    "severity": f.severity,
                    "remediation": f.recommended_remediation,
                }
                for f in vr.findings
                if f.blocks_ready_decision
            ],
            "ready_for_promotion": (
                next_rung is not None
                and not any(f.blocks_ready_decision for f in vr.findings)
                and len(development_items) == 0
            ),
        })
    summary = {
        "agents": len(plans),
        "ready_for_promotion": sum(1 for p in plans if p["ready_for_promotion"]),
        "with_development_items": sum(1 for p in plans if p["development_items"]),
        "with_blockers": sum(1 for p in plans if p["promotion_blockers"]),
    }
    return {"summary": summary, "plans": plans}
