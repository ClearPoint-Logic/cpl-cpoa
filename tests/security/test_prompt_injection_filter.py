"""Output filtering: tool outputs are untrusted; injected content is flagged (FR-094)."""

from __future__ import annotations

from cpoa.loader import load_manifest_by_name
from mcp_servers.onboarding_tools.security import build_context


def test_injected_manifest_output_is_flagged(gateway, token):
    manifest = load_manifest_by_name("prompt_injected_mcp_agent").model_dump()
    payload = {"candidate_manifest": manifest, "trace_id": None,
               "session_id": None, "previous_event_hash": None}
    ctx = build_context(payload, auth_token=token)
    out = gateway.invoke("inspect_candidate_agent", payload, ctx)
    assert "_security_flags" in out
    markers = out["_security_flags"]["prompt_injection_detected"]
    assert any("ignore previous instructions" in m or "bypass policy" in m for m in markers)


def test_clean_manifest_output_not_flagged(gateway, token, inspect_payload):
    ctx = build_context(inspect_payload, auth_token=token)
    out = gateway.invoke("inspect_candidate_agent", inspect_payload, ctx)
    assert "_security_flags" not in out
