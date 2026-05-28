"""MCP audit log emission to the structured logger (Codex M5).

Every audit record must be emitted as a JSON line via the
``cpoa.mcp.audit`` logger so Cloud Run forwards it to Cloud Logging with
severity + trace correlation.
"""

from __future__ import annotations

import json
import logging

from mcp_servers.onboarding_tools.security import (
    SecureGateway,
    build_context,
)


class _CaptureHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record.getMessage())


def test_audit_emit_writes_structured_json_payload() -> None:
    """The audit logger writes a JSON payload that Cloud Run's logging agent
    surfaces as a structured log entry with severity + trace_id ready for
    correlation in the Logs Explorer."""
    audit_logger = logging.getLogger("cpoa.mcp.audit")
    handler = _CaptureHandler()
    audit_logger.addHandler(handler)
    try:
        gw = SecureGateway(auth_token="t", require_auth=False)
        ctx = build_context({"x": 1}, auth_token="t", caller_role="service")
        try:
            gw.invoke("definitely_not_a_tool", {"x": 1}, ctx)
        except Exception:
            pass  # expected — we're testing the audit side effect
    finally:
        audit_logger.removeHandler(handler)

    assert handler.records, "expected at least one cpoa.mcp.audit emission"
    payload = json.loads(handler.records[0])
    assert payload["logger"] == "cpoa.mcp.audit"
    assert payload["tool"] == "definitely_not_a_tool"
    assert payload["decision"] == "deny"
    assert payload["severity"] == "WARNING"
    assert payload["trace_id"]
    assert payload["session_id"]


def test_in_memory_audit_log_still_populated() -> None:
    """The in-memory audit_log list (used by tests / in-process inspection)
    still works alongside the structured emission — both run on every audit."""
    gw = SecureGateway(auth_token="t", require_auth=False)
    ctx = build_context({"y": 2}, auth_token="t", caller_role="service")
    try:
        gw.invoke("definitely_not_a_tool", {"y": 2}, ctx)
    except Exception:
        pass
    assert len(gw.audit_log) >= 1
    assert gw.audit_log[-1].decision == "deny"
    assert gw.audit_log[-1].reason == "unknown_tool"
