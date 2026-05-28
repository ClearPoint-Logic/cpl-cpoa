"""Fixture loading helpers (CLI, evals, MCP, API all share these)."""

from __future__ import annotations

import json
from pathlib import Path

from cpoa.schemas import CandidateAgentManifest

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "fixtures" / "candidates"


def load_manifest(path: str | Path) -> CandidateAgentManifest:
    """Load and validate a candidate manifest JSON file."""
    data = json.loads(Path(path).read_text())
    return CandidateAgentManifest(**data)


def load_manifest_by_name(name: str) -> CandidateAgentManifest:
    """Load a fixture by stem name, e.g. 'safe_research_agent'."""
    stem = name[:-5] if name.endswith(".json") else name
    return load_manifest(FIXTURES_DIR / f"{stem}.json")


def list_fixture_names() -> list[str]:
    return sorted(p.stem for p in FIXTURES_DIR.glob("*.json"))
