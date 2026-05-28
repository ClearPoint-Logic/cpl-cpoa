"""Strict schema + size validation (FR-092 — deny unknown fields, enums, size limits)."""

from __future__ import annotations

import pytest

from mcp_servers.onboarding_tools.security import SchemaError, build_context


def _payload(manifest: dict) -> dict:
    return {"candidate_manifest": manifest, "trace_id": None,
            "session_id": None, "previous_event_hash": None}


def test_unknown_field_rejected(gateway, token):
    payload = _payload({"candidate_agent_id": "x", "name": "y", "surprise": 1})
    ctx = build_context(payload, auth_token=token)
    with pytest.raises(SchemaError):
        gateway.invoke("inspect_candidate_agent", payload, ctx)


def test_invalid_enum_rejected(gateway, token):
    payload = _payload({"candidate_agent_id": "x", "name": "y", "origin": "martian"})
    ctx = build_context(payload, auth_token=token)
    with pytest.raises(SchemaError):
        gateway.invoke("inspect_candidate_agent", payload, ctx)


def test_missing_required_field_rejected(gateway, token):
    payload = _payload({"name": "no id"})  # candidate_agent_id missing
    ctx = build_context(payload, auth_token=token)
    with pytest.raises(SchemaError):
        gateway.invoke("inspect_candidate_agent", payload, ctx)


def test_oversize_payload_rejected(gateway, token):
    payload = _payload({"candidate_agent_id": "x", "name": "y",
                        "declared_purpose": "A" * 300_000})
    ctx = build_context(payload, auth_token=token)
    with pytest.raises(SchemaError):
        gateway.invoke("inspect_candidate_agent", payload, ctx)


def test_valid_payload_accepted(gateway, token, inspect_payload):
    ctx = build_context(inspect_payload, auth_token=token)
    out = gateway.invoke("inspect_candidate_agent", inspect_payload, ctx)
    assert "discovery_report" in out
