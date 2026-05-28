"""Indirect prompt-injection detection.

Tool descriptions and other candidate-provided text are untrusted data (§17.3,
§12.6 output filtering). This detector is reused by Discovery (risk drivers),
OV-004 (validation), and the MCP server's output filter (NSA baseline). Pure,
deterministic, no LLM.
"""

from __future__ import annotations

import re

# Lowercase substrings / patterns that indicate instruction-like injected text.
INJECTION_MARKERS: tuple[str, ...] = (
    "ignore previous instructions",
    "ignore all previous",
    "ignore the above",
    "disregard previous",
    "disregard all",
    "forget previous",
    "bypass policy",
    "bypass all",
    "bypass security",
    "override your instructions",
    "override the system",
    "system prompt",
    "reveal your prompt",
    "reveal your instructions",
    "exfiltrate",
    "send all data",
    "do not tell",
    "without telling the user",
    "without informing",
    "act as if",
    "you are now",
    "new instructions:",
    "do anything now",
)

# A couple of regex patterns for slight variations.
_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts?)", re.I),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|safety)", re.I),
    re.compile(r"bypass\s+(the\s+)?(policy|guardrails?|security|filter)", re.I),
)


def scan_text(text: str | None) -> list[str]:
    """Return the list of injection markers/patterns found in ``text``."""
    if not text:
        return []
    lowered = text.lower()
    hits = [m for m in INJECTION_MARKERS if m in lowered]
    for pat in _PATTERNS:
        match = pat.search(text)
        if match:
            phrase = match.group(0).strip().lower()
            if phrase not in hits:
                hits.append(phrase)
    return hits


def contains_injection(text: str | None) -> bool:
    return bool(scan_text(text))
