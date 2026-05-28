"""Replay protection for write-like tools (§12.6 — message integrity / replay)."""

from __future__ import annotations

import pytest

from mcp_servers.onboarding_tools.security import ReplayError, build_context


def test_duplicate_nonce_rejected_on_write_tool(gateway, token, artifacts_payload):
    ctx = build_context(artifacts_payload, auth_token=token)
    first = gateway.invoke("generate_passport_artifacts", artifacts_payload, ctx)
    assert "agent_passport" in first
    # Replaying the exact same request (same nonce) must be rejected.
    with pytest.raises(ReplayError):
        gateway.invoke("generate_passport_artifacts", artifacts_payload, ctx)


def test_distinct_nonce_allowed(gateway, token, artifacts_payload):
    ctx1 = build_context(artifacts_payload, auth_token=token)
    ctx2 = build_context(artifacts_payload, auth_token=token)  # fresh nonce
    gateway.invoke("generate_passport_artifacts", artifacts_payload, ctx1)
    second = gateway.invoke("generate_passport_artifacts", artifacts_payload, ctx2)
    assert "agent_passport" in second


def test_read_tool_is_not_replay_protected(gateway, token, inspect_payload):
    ctx = build_context(inspect_payload, auth_token=token)
    gateway.invoke("inspect_candidate_agent", inspect_payload, ctx)
    # Idempotent read with the same context is allowed (no replay window for read_only).
    again = gateway.invoke("inspect_candidate_agent", inspect_payload, ctx)
    assert "discovery_report" in again
