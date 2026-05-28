"""Unit tests for Optimize (Talent Development) — development plans from real signals."""

from __future__ import annotations

from cpoa.services import optimize


def test_plans_cover_every_fixture() -> None:
    out = optimize.development_plans()
    assert out["summary"]["agents"] == len(out["plans"])
    assert out["summary"]["agents"] > 0


def test_ladder_progression_is_consistent() -> None:
    """next_autonomy should be exactly one rung above current, or None at top."""
    ladder = [
        "L0_observe", "L1_recommend", "L2_draft",
        "L3_execute_with_approval", "L4_bounded_autonomous", "L5_high_impact_autonomous",
    ]
    out = optimize.development_plans()
    for p in out["plans"]:
        current = p["current_autonomy"]
        next_ = p["next_autonomy"]
        if current == ladder[-1]:
            assert next_ is None
        else:
            assert next_ == ladder[ladder.index(current) + 1]


def test_blocked_agents_show_blockers_not_development_items() -> None:
    """Findings that block_ready_decision land in promotion_blockers, not development_items."""
    out = optimize.development_plans()
    for p in out["plans"]:
        # No item should be in both buckets
        item_ids = {i["finding_id"] for i in p["development_items"]}
        blocker_ids = {b["finding_id"] for b in p["promotion_blockers"]}
        assert item_ids.isdisjoint(blocker_ids)


def test_ready_for_promotion_requires_zero_items_and_a_next_rung() -> None:
    out = optimize.development_plans()
    for p in out["plans"]:
        if p["ready_for_promotion"]:
            assert p["next_autonomy"] is not None
            assert len(p["development_items"]) == 0
            assert len(p["promotion_blockers"]) == 0


def test_summary_aggregates_match_plans() -> None:
    out = optimize.development_plans()
    assert out["summary"]["ready_for_promotion"] == sum(
        1 for p in out["plans"] if p["ready_for_promotion"]
    )
    assert out["summary"]["with_development_items"] == sum(
        1 for p in out["plans"] if p["development_items"]
    )
    assert out["summary"]["with_blockers"] == sum(
        1 for p in out["plans"] if p["promotion_blockers"]
    )
