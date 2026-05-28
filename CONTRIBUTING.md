# Contributing to ClearPoint Workforce Agent

Thanks for considering a contribution. This document captures the conventions
the repo follows so changes land cleanly.

## Code of conduct

Participation is governed by [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
Concerns can be reported to **security@clearpointlogic.com**.

## Reporting security issues

Please **do not file public issues** for security vulnerabilities. See
[`docs/security/SECURITY.md`](docs/security/SECURITY.md) for the responsible
disclosure path.

## Development setup

```bash
# Python (3.13 required for the runtime; tests run under 3.13)
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt   # runtime + dev tooling (ruff, pytest, coverage)

# Web UI (Node 20 LTS)
cd app/web && npm install
```

Copy `.env.example` to `.env` and populate the GCP project + Vertex AI
settings before running the live narration path. The deterministic engine
runs offline with no env required.

## Running locally

```bash
# Run the gate on a fixture (CLI)
python scripts/run_demo.py --fixture safe_research_agent
python scripts/run_demo.py --fixture prompt_injected_mcp_agent

# Eval the whole roster
python scripts/run_evals.py            # 5/5 must-ship, 8/8 overall

# API + UI (in two terminals)
uvicorn app.api.main:app --reload --port 8080
cd app/web && npm run dev
```

## Tests

The full suite runs locally in well under a second:

```bash
pytest -q                              # unit / integration / evals / security (160+ tests)
ruff check .                           # lint (zero warnings policy)
cd app/web && npm run build            # Next.js build (matches CI)
```

CI runs the Python suite on every PR. Lint, schema validation, the fixture
evals, and the MCP security tests must all pass before review.

## Branch + PR conventions

- Branches: `feat/<short-slug>`, `fix/<short-slug>`, `chore/<short-slug>`,
  `docs/<short-slug>`.
- One concern per PR. Squash-merge to `main`.
- PR title is the headline change. PR body explains *what* and *why*, lists
  files touched, and notes verification (lint + tests + build).
- CI must be green. CodeRabbit review is non-blocking but read.

## Commit messages

Match the style already in the history:

```
<subject line — imperative, ≤72 chars>

<short paragraph: what changed and why>

- <bullet for each notable file or behavior change>
- ...

Verified: ruff clean; pytest N passed; npm run build clean.

Co-Authored-By: <attribution line if applicable>
```

## Schema-change protocol

The `cpoa/schemas/` package is the §11 data contract. Changes there require:

1. A backward-compatibility analysis in the PR body (does this break any
   downstream consumer that parses bundles?).
2. A note in `CHANGELOG.md` under "Unreleased."
3. Tests in `tests/unit/test_schemas.py` covering the new field/literal.
4. A re-run of `pytest tests/unit/test_bundle_hash_recompute.py` against
   every fixture (the hash-chain integrity test catches accidental
   serialization drift).

## Style notes

- Python: ruff defaults; `from __future__ import annotations` at the top of
  every module; type hints on public functions.
- TypeScript / React: function components; Tailwind utility classes; Material
  3 surface tokens (`text-on-surface`, `bg-surface-container-lowest`, etc.);
  prefer `Link` from `next/link` over raw `<a>`.
- Comments earn their place. Document *why*, not *what*.
