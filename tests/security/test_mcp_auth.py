"""Authentication, authorization (RBAC), message integrity, and audit logging (§12.6)."""

from __future__ import annotations

import pytest

from mcp_servers.onboarding_tools.security import (
    AuthError,
    AuthzError,
    IntegrityError,
    build_context,
)


def test_rejects_missing_token(gateway, inspect_payload):
    ctx = build_context(inspect_payload, auth_token=None)
    with pytest.raises(AuthError):
        gateway.invoke("inspect_candidate_agent", inspect_payload, ctx)


def test_rejects_wrong_token(gateway, inspect_payload):
    ctx = build_context(inspect_payload, auth_token="not-the-token")
    with pytest.raises(AuthError):
        gateway.invoke("inspect_candidate_agent", inspect_payload, ctx)


def test_accepts_valid_token(gateway, token, inspect_payload):
    ctx = build_context(inspect_payload, auth_token=token)
    out = gateway.invoke("inspect_candidate_agent", inspect_payload, ctx)
    assert "discovery_report" in out


def test_rbac_auditor_denied_write_tool(gateway, token, artifacts_payload):
    ctx = build_context(artifacts_payload, auth_token=token, caller_role="auditor")
    with pytest.raises(AuthzError):
        gateway.invoke("generate_passport_artifacts", artifacts_payload, ctx)


def test_rbac_auditor_allowed_read_tool(gateway, token, inspect_payload):
    ctx = build_context(inspect_payload, auth_token=token, caller_role="auditor")
    out = gateway.invoke("inspect_candidate_agent", inspect_payload, ctx)
    assert "discovery_report" in out


def test_unknown_tool_denied(gateway, token, inspect_payload):
    ctx = build_context(inspect_payload, auth_token=token)
    with pytest.raises(AuthzError):
        gateway.invoke("definitely_not_a_tool", inspect_payload, ctx)


def test_integrity_request_hash_mismatch(gateway, token, inspect_payload):
    ctx = build_context(inspect_payload, auth_token=token)
    ctx.request_hash = "sha256:tampered"
    with pytest.raises(IntegrityError):
        gateway.invoke("inspect_candidate_agent", inspect_payload, ctx)


def test_integrity_expired_request(gateway, token, inspect_payload):
    ctx = build_context(inspect_payload, auth_token=token, ttl_seconds=-1)
    with pytest.raises(IntegrityError):
        gateway.invoke("inspect_candidate_agent", inspect_payload, ctx)


def test_audit_log_records_allow_and_deny(gateway, token, inspect_payload):
    bad = build_context(inspect_payload, auth_token=None)
    with pytest.raises(AuthError):
        gateway.invoke("inspect_candidate_agent", inspect_payload, bad)
    ok = build_context(inspect_payload, auth_token=token)
    gateway.invoke("inspect_candidate_agent", inspect_payload, ok)

    decisions = {r.decision for r in gateway.audit_log}
    assert {"allow", "deny"} <= decisions
    # Every audit record carries identity + trace id + params hash (FR-095).
    assert all(r.identity and r.trace_id and r.params_hash for r in gateway.audit_log)
