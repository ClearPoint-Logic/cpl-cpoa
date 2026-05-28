"""Import-time smoke tests.

Covers module-level statements (imports, constants, helper definitions) in
files whose runtime paths require live network/model calls that we don't
exercise in unit tests. These tests don't validate behavior — they just
guarantee the module loads cleanly and its module-level side effects are
exercised.
"""

from __future__ import annotations


def test_agents_run_module_imports_cleanly() -> None:
    """agents/run.py holds the live Gemini narration entrypoints. The
    network-calling functions are pragma: no cover; this asserts the module
    itself loads (catches accidental import-time crashes)."""
    from agents import run

    # Public surface exists and is callable
    assert callable(run.narrate_facts)
    assert callable(run.narrate_with_llm)
    assert callable(run.run_adk_onboarding)


def test_mcp_server_module_imports_cleanly() -> None:
    """mcp_servers/onboarding_tools/server.py wires the FastMCP server. The
    server-building function is pragma: no cover; this exercises the module-
    level gateway construction + the _context helper."""
    from mcp_servers.onboarding_tools import server

    # SecureGateway is constructed at module load
    assert server.gateway is not None
    # _context produces a SecurityContext given typical inputs
    ctx = server._context(
        payload={"a": 1},
        auth_token="token",
        caller_role="service",
        nonce="abc",
        trace_id=None,
        session_id=None,
    )
    assert ctx.caller_role == "service"
    assert ctx.auth_token == "token"
    assert ctx.nonce == "abc"
    # trace_id and session_id should be auto-generated when None
    assert ctx.trace_id.startswith("trace-")
    assert ctx.session_id.startswith("session-")


def test_mcp_server_context_defaults_role_when_empty() -> None:
    from mcp_servers.onboarding_tools import server

    ctx = server._context(
        payload={},
        auth_token=None,
        caller_role="",
        nonce=None,
        trace_id="trace-x",
        session_id="session-x",
    )
    assert ctx.caller_role == "service"  # falls back from empty string
