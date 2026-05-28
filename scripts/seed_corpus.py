#!/usr/bin/env python3
"""Validate the grounding corpus and write the FR-084 grounded-vs-ungrounded fixture.

    python scripts/seed_corpus.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cpoa.loader import REPO_ROOT, load_manifest_by_name  # noqa: E402
from cpoa.services.discovery import run_discovery  # noqa: E402
from cpoa.services.grounding import build_grounding_comparison, load_corpus  # noqa: E402


def main() -> int:
    passages = load_corpus()
    by_source = Counter(p.source_id for p in passages)
    print(f"Corpus: {len(passages)} passages")
    for src, n in sorted(by_source.items()):
        print(f"  - {src}: {n}")

    # FR-084: store the grounded-vs-ungrounded comparison as a fixture.
    manifest = load_manifest_by_name("grounding_required_policy_agent")
    comparison = build_grounding_comparison(manifest, run_discovery(manifest))
    out_dir = REPO_ROOT / "fixtures" / "comparisons"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "grounding_demo.json"
    out_path.write_text(json.dumps(comparison, indent=2))
    print(f"\nWrote {out_path}")
    print(f"  ungrounded citations: {len(comparison['ungrounded']['grounding_refs'])}")
    print(f"  grounded   citations: {len(comparison['grounded']['grounding_refs'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
