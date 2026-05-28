"""Deterministic fixture-decision evals (§18). Shared by scripts/run_evals.py and CI."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from cpoa.loader import REPO_ROOT, load_manifest_by_name
from cpoa.services import engine

EXPECTED_PATH = REPO_ROOT / "tests" / "evals" / "expected_decisions.yaml"


@dataclass
class EvalResult:
    fixture: str
    tier: str
    decision: str
    allowed: list[str]
    finding_tests: list[str]
    ok: bool
    reasons: list[str] = field(default_factory=list)


def load_expected(path: str | Path = EXPECTED_PATH) -> dict:
    return yaml.safe_load(Path(path).read_text())


def evaluate_fixture(name: str, spec: dict) -> EvalResult:
    manifest = load_manifest_by_name(name)
    result = engine.onboard(manifest)
    decision = result.decision
    finding_tests = sorted({f.test_id for f in result.validation_run.findings})
    severities = {f.severity for f in result.validation_run.findings}

    allowed = spec.get("allowed_decisions") or [spec["expected_decision"]]
    reasons: list[str] = []
    if decision not in allowed:
        reasons.append(f"decision {decision!r} not in {allowed}")
    for t in spec.get("must_have_tests", []):
        if t not in finding_tests:
            reasons.append(f"missing required finding {t}")
    for sev in spec.get("must_not_have_severities", []):
        if sev in severities:
            reasons.append(f"unexpected {sev}-severity finding")
    # Always verify the hash chain validates (AC #19).
    from cpoa.services.hashing import verify_event_chain

    chain_ok, chain_errs = verify_event_chain(result.events)
    if not chain_ok:
        reasons.append("invalid evidence hash chain: " + "; ".join(chain_errs))

    return EvalResult(
        fixture=name,
        tier=spec.get("tier", "stretch"),
        decision=decision,
        allowed=allowed,
        finding_tests=finding_tests,
        ok=not reasons,
        reasons=reasons,
    )


def run_all(expected: dict | None = None) -> list[EvalResult]:
    expected = expected or load_expected()
    return [evaluate_fixture(name, spec) for name, spec in expected.items()]


def summarize(results: list[EvalResult]) -> dict:
    must = [r for r in results if r.tier == "must_ship"]
    return {
        "must_ship_pass": sum(r.ok for r in must),
        "must_ship_total": len(must),
        "all_pass": sum(r.ok for r in results),
        "all_total": len(results),
    }
