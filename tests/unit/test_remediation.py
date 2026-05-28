"""Unit tests for the onboarding remediation service (prompt-injection hero).

Covers the pure sanitizer (quarantine the injected tool description, no input
mutation) and the signed, hash-chained ``onboarding.remediated`` event builder.
"""

from __future__ import annotations

from cpoa.loader import load_manifest_by_name
from cpoa.services import remediation
from cpoa.services.injection import scan_text


def test_sanitize_quarantines_injected_tool_description() -> None:
    manifest = load_manifest_by_name("prompt_injected_mcp_agent")
    original_desc = manifest.tools[0].description
    assert scan_text(original_desc), "fixture should carry an injection payload"

    sanitized, applied = remediation.sanitize_manifest(manifest)

    # The injected instructions are gone from the sanitized copy …
    assert scan_text(sanitized.tools[0].description) == []
    assert "Quarantined" in sanitized.tools[0].description
    # … and the original manifest is untouched (pure function).
    assert manifest.tools[0].description == original_desc
    # The applied record names the control + the exact phrases stripped.
    assert len(applied) == 1
    assert applied[0]["control"] == "OV-004"
    assert applied[0]["tool_id"] == "record_tool"
    assert "ignore previous instructions" in applied[0]["phrases"]


def test_sanitize_clean_manifest_is_a_noop() -> None:
    manifest = load_manifest_by_name("safe_research_agent")
    sanitized, applied = remediation.sanitize_manifest(manifest)
    assert applied == []
    assert sanitized.model_dump() == manifest.model_dump()


def test_remediation_event_is_signed_and_chained() -> None:
    event = remediation.build_remediation_event(
        "prompt-injected-005",
        previous_event_hash="prevhash123",
        summary="re-screened clean",
        payload={"re_run_id": "run-abc", "new_decision": "Ready"},
    )
    assert event.event_type == "onboarding.remediated"
    assert event.previous_event_hash == "prevhash123"
    assert event.event_hash  # canonical hash computed
    assert event.signature.value.startswith("hmac-sha256:")
    assert event.subject.candidate_agent_id == "prompt-injected-005"
