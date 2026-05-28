"""CI gate: every fixture resolves to an allowed decision; must-ship all pass (§18.2)."""

from __future__ import annotations

import pytest

from cpoa.evals import evaluate_fixture, load_expected

EXPECTED = load_expected()


@pytest.mark.parametrize("name", list(EXPECTED.keys()))
def test_fixture_decision(name):
    result = evaluate_fixture(name, EXPECTED[name])
    assert result.ok, f"{name}: {result.reasons} (got {result.decision})"


def test_all_must_ship_pass_and_three_decision_classes_present():
    results = [evaluate_fixture(n, s) for n, s in EXPECTED.items()]
    must = [r for r in results if r.tier == "must_ship"]
    assert all(r.ok for r in must)
    assert len(must) == 5  # AC #10
    decisions = {r.decision for r in results}
    # AC #11-13: at least one Ready, one Conditional, one Blocked across the zoo.
    assert "Ready" in decisions
    assert "Ready with Conditions" in decisions
    assert "Blocked Pending Remediation" in decisions
