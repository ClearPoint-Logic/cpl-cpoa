"""Unit tests for the model-output dash sanitizer in agents/run.py.

Live Gemini prose can still emit em/en dashes even though every piece of source
copy is already clean. ``_sanitize_dashes`` is the runtime guard applied at the
model-output chokepoint; these tests pin its behavior so the house style (no
em-dashes) survives free-form generation.
"""

from __future__ import annotations

import pytest

from agents.run import _sanitize_dashes


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # Spaced em-dash used as a clause break -> comma.
        (
            "score, caps, blockers — they are final",
            "score, caps, blockers, they are final",
        ),
        # Multiple clause-break dashes in one string.
        ("Discover — Onboard — Manage", "Discover, Onboard, Manage"),
        # En-dash clause break behaves the same as em-dash.
        ("ready – with conditions", "ready, with conditions"),
        # Whitespace only on the left of the dash.
        ("blocked —remediated", "blocked, remediated"),
        # Whitespace only on the right of the dash.
        ("blocked— remediated", "blocked, remediated"),
        # Bare en-dash range -> hyphen.
        ("4–6 sentences", "4-6 sentences"),
        # Bare em-dash compound -> hyphen.
        ("hash—chained", "hash-chained"),
        # Clean text is untouched.
        ("no dashes here", "no dashes here"),
        # Already-hyphenated text is untouched.
        ("hash-chained, signed", "hash-chained, signed"),
        # Empty string passes through.
        ("", ""),
    ],
)
def test_sanitize_dashes(raw: str, expected: str) -> None:
    assert _sanitize_dashes(raw) == expected


def test_sanitize_dashes_removes_every_em_and_en_dash() -> None:
    sample = "A — B; range 1–3; combo c—d – end"
    out = _sanitize_dashes(sample)
    assert "—" not in out
    assert "–" not in out
    assert out == "A, B; range 1-3; combo c-d, end"
