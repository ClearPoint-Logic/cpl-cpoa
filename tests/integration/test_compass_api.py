"""Regression tests for Compass advisor accessibility.

Compass must speak plain business language: neither its answer prose nor its
suggested-action labels may leak raw run/candidate IDs, page paths (e.g.
``/runs/...``), machine test codes (e.g. ``OV-003``), or internal
infrastructure/protocol names (Cloud Trace, Firestore, MCP, A2A, Vertex …).

In the test environment ``llm_available()`` is False, so ``/api/compass/ask``
returns the deterministic grounded answer (``source == "deterministic"``). That
is exactly the surface a judge sees when Gemini is unavailable — and the surface
that previously leaked codes and paths to a non-technical reader.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.main import _compass_facts, _friendly_page, app

client = TestClient(app)

# A fixture that lands a "Ready with Conditions" decision with one finding (OV-003)
# — enough to exercise the finding/lifecycle prose without being blocked.
FIXTURE = "healthcare_phi_support_agent"

# Substrings that must never appear in user-facing Compass prose. None of these
# are substrings of ordinary words used in the advisor copy, so a plain
# case-insensitive membership check is safe.
FORBIDDEN_INFRA = [
    "cloud trace", "firestore", "cloud run", "bigquery", "kubernetes",
    "grpc", "vertex", "gemini", "mcp", "a2a", "adk", "kubeflow",
]


@pytest.fixture(scope="module")
def run() -> dict:
    """Create one onboarding run and reuse it across the module (keeps us well
    under the per-IP rate limits the live endpoints enforce)."""
    r = client.post("/api/runs", json={"fixture": FIXTURE})
    assert r.status_code == 200, r.text
    return r.json()


def _assert_clean(text: str, *, run_id: str, candidate_id: str) -> None:
    """Fail if any machine identifier, path, code, or infra name leaked."""
    assert "/runs" not in text, f"leaked a page path: {text!r}"
    assert run_id not in text, f"leaked the run id: {text!r}"
    assert candidate_id not in text, f"leaked the candidate id: {text!r}"
    assert "OV-003" not in text, f"leaked a machine test code: {text!r}"
    low = text.lower()
    for term in FORBIDDEN_INFRA:
        assert term not in low, f"leaked infra/protocol term {term!r}: {text!r}"


def _ask(message: str, run: dict) -> dict:
    rid = run["run_id"]
    r = client.post(
        "/api/compass/ask",
        json={"message": message, "context": {"run_id": rid, "page": f"/runs/{rid}"}},
    )
    assert r.status_code == 200, r.text
    return r.json()


# --- Answer prose ----------------------------------------------------------


def test_general_answer_has_no_paths_codes_or_infra(run: dict) -> None:
    body = _ask("How is this agent doing?", run)
    assert body["source"] == "deterministic"  # no live Gemini in tests
    answer = body["answer"]
    assert answer.strip()
    _assert_clean(answer, run_id=run["run_id"], candidate_id=run["candidate_agent_id"])


def test_explain_finding_answer_is_clean_and_helpful(run: dict) -> None:
    # The explain-finding action asks about a finding by its human title.
    top = run["validation_run"]["findings"][0]
    body = _ask(f'Explain the finding "{top["title"]}" in plain language and how to resolve it.', run)
    answer = body["answer"]
    _assert_clean(answer, run_id=run["run_id"], candidate_id=run["candidate_agent_id"])
    # Leads with the human title and gives a remediation, not a test code.
    assert top["title"] in answer
    assert "How to resolve it" in answer


def test_no_run_answer_is_clean_capabilities_blurb() -> None:
    r = client.post("/api/compass/ask", json={"message": "What can you do?", "context": {}})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["source"] == "deterministic"
    assert "Compass" in body["answer"]
    assert "/runs" not in body["answer"]


# --- Suggested actions -----------------------------------------------------


def test_suggested_action_labels_are_plain_language(run: dict) -> None:
    body = _ask("What should I do next?", run)
    actions = body["suggested_actions"]
    assert actions
    for a in actions:
        # Only human-readable text fields — href/candidate_id carry plumbing by design.
        for field in ("label", "description", "prompt"):
            if a.get(field):
                _assert_clean(a[field], run_id=run["run_id"], candidate_id=run["candidate_agent_id"])
    explain = next((a for a in actions if a["id"] == "explain_finding"), None)
    assert explain is not None
    assert explain["label"].startswith("Explain:")  # friendly title, not a code


# --- Grounding facts (what we hand the model) ------------------------------


def test_compass_facts_carry_no_identifiers_or_stack(run: dict) -> None:
    rid = run["run_id"]
    facts, loaded = _compass_facts({"run_id": rid, "page": f"/runs/{rid}"})
    assert loaded is not None
    # Friendly screen name, never a raw path.
    assert facts["current_screen"] == "the agent's onboarding profile"
    # No machine identifiers or infra inventory anywhere at the top level.
    assert "candidate_agent_id" not in facts
    assert "stack" not in facts
    agent = facts["agent"]
    assert "candidate_agent_id" not in agent
    # Findings are reduced to severity + title only (no test_id machine codes).
    for f in agent["findings"]:
        assert set(f.keys()) == {"severity", "title"}


# --- Friendly page mapping -------------------------------------------------


@pytest.mark.parametrize(
    "page,expected",
    [
        ("/runs/run-abc123", "the agent's onboarding profile"),
        ("run", "the agent's onboarding profile"),
        ("/compliance", "Compliance"),
        ("/operate", "Operate"),
        ("/agents", "Pre-Boarding"),
        (None, "the platform"),
        ("/totally/unknown/path", "the platform"),
    ],
)
def test_friendly_page_never_leaks_a_path(page: str | None, expected: str) -> None:
    resolved = _friendly_page(page)
    assert resolved == expected
    assert "/" not in resolved  # a friendly name is never a path
