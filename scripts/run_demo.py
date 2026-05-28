#!/usr/bin/env python3
"""CLI demo runner (§15.7) — run the onboarding workflow on a candidate manifest.

    python scripts/run_demo.py --candidate fixtures/candidates/safe_research_agent.json
    python scripts/run_demo.py --fixture prompt_injected_mcp_agent
    python scripts/run_demo.py --list
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cpoa.loader import FIXTURES_DIR, list_fixture_names, load_manifest  # noqa: E402
from cpoa.services import engine  # noqa: E402
from cpoa.services.exports import export_bundle  # noqa: E402
from cpoa.services.hashing import verify_event_chain  # noqa: E402

BADGE = {
    "Ready": "[ READY ]",
    "Ready with Conditions": "[ CONDITIONAL ]",
    "Blocked Pending Remediation": "[ BLOCKED ]",
}


def _hr(title: str) -> None:
    print(f"\n\033[1m{title}\033[0m")
    print("-" * len(title))


def run(manifest_path: Path, out_dir: str) -> str:
    manifest = load_manifest(manifest_path)
    result = engine.onboard(manifest)
    d = result.discovery

    _hr("Candidate")
    print(f"  {manifest.name}  ({manifest.candidate_agent_id}, origin={manifest.origin})")
    owner = manifest.owner
    print(f"  Owner:    {(owner.name + ' <' + (owner.email or '') + '>') if owner else 'MISSING'}"
          f"  [{d.owner_status}]")
    print(f"  Purpose:  {manifest.declared_purpose or 'MISSING'}  [{d.purpose_status}]")
    print(f"  Autonomy: {manifest.autonomy.level}")
    print(f"  Tools:    {', '.join(f'{t.name}({t.risk_tier})' for t in manifest.tools) or 'none'}")
    print(f"  Data:     {', '.join(manifest.data_access.declared_data_classes) or 'none'}")

    _hr("Workflow (hash-chained evidence)")
    for e in result.events:
        print(f"  • {e.event_type:<38} {e.summary}")

    _hr("Onboarding Validation Suite")
    if result.validation_run.findings:
        for f in result.validation_run.findings:
            flag = " (blocks Ready)" if f.blocks_ready_decision else ""
            print(f"  [{f.severity.upper():<8}] {f.test_id}  {f.title}{flag}")
            print(f"             ↳ {f.recommended_remediation}")
    else:
        print("  No findings — all checks passed.")

    score = result.score
    _hr("Decision")
    print(f"  {BADGE.get(result.decision, result.decision)}  {result.decision}")
    print(f"  Passport Readiness Score: {score.score}/100 ({score.band})")
    for b in result.decision_result.blockers:
        print(f"   ⛔ blocker:   {b}")
    for c in result.decision_result.conditions:
        print(f"   • condition: {c}")

    chain_ok, _ = verify_event_chain(result.events)
    paths = export_bundle(result.bundle, Path(out_dir) / manifest.candidate_agent_id)
    _hr("Artifacts")
    print(f"  Evidence hash chain valid: {'yes' if chain_ok else 'NO'}")
    print(f"  Bundle hash: {result.bundle.bundle_hash}")
    for key, p in paths.items():
        print(f"  {key:<20} {p}")
    return result.decision


def main() -> int:
    ap = argparse.ArgumentParser(description="ClearPoint Onboarding Agent — CLI demo")
    ap.add_argument("--candidate", help="path to a candidate manifest JSON")
    ap.add_argument("--fixture", help="fixture name, e.g. safe_research_agent")
    ap.add_argument("--out", default="artifacts/runs", help="output directory for artifacts")
    ap.add_argument("--list", action="store_true", help="list available fixtures")
    args = ap.parse_args()

    if args.list:
        print("Available fixtures:")
        for name in list_fixture_names():
            print(f"  - {name}")
        return 0

    if args.candidate:
        path = Path(args.candidate)
    elif args.fixture:
        path = FIXTURES_DIR / f"{args.fixture}.json"
    else:
        ap.error("provide --candidate <path>, --fixture <name>, or --list")

    if not path.exists():
        print(f"error: manifest not found: {path}", file=sys.stderr)
        return 2

    run(path, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
