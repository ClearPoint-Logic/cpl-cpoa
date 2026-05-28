#!/usr/bin/env python3
"""Run the fixture-decision evals and print a table (§18). Non-zero exit if must-ship fails.

    python scripts/run_evals.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cpoa.evals import run_all, summarize  # noqa: E402


def main() -> int:
    results = run_all()
    width = max(len(r.fixture) for r in results)
    print(f"{'FIXTURE':<{width}}  {'TIER':<9}  {'DECISION':<26}  RESULT")
    print("-" * (width + 50))
    for r in results:
        status = "PASS" if r.ok else "FAIL: " + "; ".join(r.reasons)
        print(f"{r.fixture:<{width}}  {r.tier:<9}  {r.decision:<26}  {status}")

    s = summarize(results)
    print("-" * (width + 50))
    print(f"Must-ship: {s['must_ship_pass']}/{s['must_ship_total']}   "
          f"All fixtures: {s['all_pass']}/{s['all_total']}")

    return 0 if s["must_ship_pass"] == s["must_ship_total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
