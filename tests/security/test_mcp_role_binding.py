"""MCP HTTP role binding (Codex C3 — NSA baseline tightening).

When the server is configured with a token + role, the caller's ``caller_role``
argument must be ignored in favor of the server-side mapping. A client cannot
claim a role tied to a token they don't hold.
"""

from __future__ import annotations

from mcp_servers.onboarding_tools import server


def test_caller_role_ignored_when_server_token_configured(monkeypatch) -> None:
    """A client claim of 'auditor' is overridden by the env-configured 'service' role."""
    monkeypatch.setattr(server, "_AUTH_TOKEN", "server-token")
    monkeypatch.setattr(server, "_AUTH_ROLE", "service")
    ctx = server._context(
        payload={"x": 1},
        auth_token="server-token",
        caller_role="auditor",  # client claims something different
        nonce=None,
        trace_id=None,
        session_id=None,
    )
    assert ctx.caller_role == "service"  # server-derived, not client-claimed


def test_caller_role_accepted_when_no_server_token(monkeypatch) -> None:
    """Local dev with no token configured still accepts the caller's role."""
    monkeypatch.setattr(server, "_AUTH_TOKEN", None)
    ctx = server._context(
        payload={"x": 1},
        auth_token=None,
        caller_role="auditor",
        nonce=None,
        trace_id=None,
        session_id=None,
    )
    assert ctx.caller_role == "auditor"


def test_role_defaults_to_service_when_only_token_configured(monkeypatch) -> None:
    """If a token is configured and the default role is unchanged, role defaults to service."""
    monkeypatch.setattr(server, "_AUTH_TOKEN", "server-token")
    monkeypatch.setattr(server, "_AUTH_ROLE", "service")
    ctx = server._context(
        payload={},
        auth_token="server-token",
        caller_role="admin",
        nonce=None,
        trace_id=None,
        session_id=None,
    )
    assert ctx.caller_role == "service"


def test_client_cannot_escalate_via_caller_role_claim(monkeypatch) -> None:
    """Even with a valid token, the client cannot claim a role tied to a higher
    tier than the server has bound to that token."""
    monkeypatch.setattr(server, "_AUTH_TOKEN", "server-token")
    monkeypatch.setattr(server, "_AUTH_ROLE", "auditor")
    ctx = server._context(
        payload={},
        auth_token="server-token",
        caller_role="ai_workforce_manager",  # would grant internal_write
        nonce=None,
        trace_id=None,
        session_id=None,
    )
    # Role is auditor (read_only only), regardless of the claim
    assert ctx.caller_role == "auditor"
