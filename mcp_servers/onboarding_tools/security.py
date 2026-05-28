"""NSA MCP Security Design Baseline (§12.6) as a testable gateway.

Controls: authentication (FR-090), tool-level RBAC (FR-091), strict schema/size
validation (FR-092), message integrity — nonce/expiry/request-hash (FR-093),
replay protection, output filtering for prompt-injection (FR-094), and audit
logging (FR-095). Pure Python so tests/security can exercise each control without
a running HTTP server.

Audit-log emission (Codex M5): every audit record is appended to the in-memory
``audit_log`` for in-process inspection AND emitted as a structured JSON log
line via the ``cpoa.mcp.audit`` logger. On Cloud Run this lands in Cloud
Logging as a JSON-payload entry with severity and trace_id ready for
correlation. Local stdio dev sees the same lines on stderr.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass

from cpoa.services import hashing
from cpoa.services.injection import scan_text

from .tools import TOOL_REGISTRY

# Structured audit logger — JSON payloads land in Cloud Logging on Cloud Run.
_audit_logger = logging.getLogger("cpoa.mcp.audit")
if not _audit_logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(message)s"))
    _audit_logger.addHandler(_h)
    _audit_logger.setLevel(logging.INFO)
    _audit_logger.propagate = False


# --- Exceptions (mapped to MCP errors by the server) ---
class MCPSecurityError(Exception):
    code = "security_error"


class AuthError(MCPSecurityError):
    code = "unauthenticated"


class AuthzError(MCPSecurityError):
    code = "forbidden"


class IntegrityError(MCPSecurityError):
    code = "integrity_failed"


class ReplayError(MCPSecurityError):
    code = "replay_detected"


class SchemaError(MCPSecurityError):
    code = "schema_invalid"


# Role -> permitted tool risk tiers (RBAC).
ROLE_TIERS: dict[str, set[str]] = {
    "ai_workforce_manager": {"read_only", "internal_write"},
    "service": {"read_only", "internal_write"},
    "security": {"read_only", "internal_write"},
    "auditor": {"read_only"},
}
# Tiers that require replay protection (idempotency).
WRITE_TIERS = {"internal_write", "external_write", "financial_action", "privileged_admin"}
MAX_PAYLOAD_BYTES = 256 * 1024


@dataclass
class SecurityContext:
    auth_token: str | None = None
    caller_role: str = "service"
    trace_id: str = ""
    session_id: str = ""
    nonce: str = ""
    expires_at: float = 0.0  # epoch seconds; 0 = not set
    request_hash: str = ""


@dataclass
class AuditRecord:
    tool: str
    identity: str
    params_hash: str
    decision: str
    reason: str
    trace_id: str
    nonce: str
    output_hash: str = ""


def build_context(payload: dict, auth_token: str | None, caller_role: str = "service",
                  trace_id: str | None = None, session_id: str | None = None,
                  ttl_seconds: int = 300) -> SecurityContext:
    """Construct a valid, message-bound security context for a payload (used by callers)."""
    return SecurityContext(
        auth_token=auth_token,
        caller_role=caller_role,
        trace_id=trace_id or f"trace-{uuid.uuid4().hex[:12]}",
        session_id=session_id or f"session-{uuid.uuid4().hex[:12]}",
        nonce=uuid.uuid4().hex,
        expires_at=time.time() + ttl_seconds,
        request_hash=hashing.payload_hash(payload),
    )


def _scan_output_for_injection(result: dict) -> list[str]:
    """Treat tool output as untrusted (FR-094): scan serialized output for injection markers."""
    return scan_text(json.dumps(result, default=str))


class SecureGateway:
    """Wraps tool invocation with the NSA baseline controls."""

    def __init__(self, auth_token: str | None, require_auth: bool = True) -> None:
        self.auth_token = auth_token
        self.require_auth = require_auth
        self._seen_nonces: set[str] = set()
        self.audit_log: list[AuditRecord] = []

    def _audit(self, tool: str, ctx: SecurityContext, decision: str, reason: str,
               params_hash: str, output_hash: str = "") -> AuditRecord:
        rec = AuditRecord(tool=tool, identity=ctx.caller_role, params_hash=params_hash,
                          decision=decision, reason=reason, trace_id=ctx.trace_id,
                          nonce=ctx.nonce, output_hash=output_hash)
        self.audit_log.append(rec)
        # Codex M5 — structured emission for Cloud Logging correlation.
        # Cloud Run's logging agent parses JSON stdout and surfaces severity +
        # trace correlation in the Logs Explorer.
        _audit_logger.info(json.dumps({
            **asdict(rec),
            "logger": "cpoa.mcp.audit",
            "severity": "INFO" if decision == "allow" else "WARNING",
            "session_id": ctx.session_id,
        }))
        return rec

    def invoke(self, tool_name: str, payload: dict, ctx: SecurityContext) -> dict:
        params_hash = hashing.payload_hash(payload)

        if tool_name not in TOOL_REGISTRY:
            self._audit(tool_name, ctx, "deny", "unknown_tool", params_hash)
            raise AuthzError(f"unknown tool: {tool_name}")
        fn, tier = TOOL_REGISTRY[tool_name]

        # 1. Authentication (FR-090)
        if self.require_auth and (not ctx.auth_token or ctx.auth_token != self.auth_token):
            self._audit(tool_name, ctx, "deny", "unauthenticated", params_hash)
            raise AuthError("missing or invalid auth token")

        # 2. Authorization / RBAC (FR-091)
        if tier not in ROLE_TIERS.get(ctx.caller_role, set()):
            self._audit(tool_name, ctx, "deny", f"role '{ctx.caller_role}' denied tier '{tier}'",
                        params_hash)
            raise AuthzError(f"role '{ctx.caller_role}' not permitted for tool tier '{tier}'")

        # 3. Message integrity (FR-093): expiry, nonce, request-hash binding
        if self.require_auth:
            if ctx.expires_at and ctx.expires_at < time.time():
                self._audit(tool_name, ctx, "deny", "request_expired", params_hash)
                raise IntegrityError("request expired")
            if not ctx.nonce:
                self._audit(tool_name, ctx, "deny", "missing_nonce", params_hash)
                raise IntegrityError("missing nonce / idempotency key")
            if ctx.request_hash and ctx.request_hash != params_hash:
                self._audit(tool_name, ctx, "deny", "request_hash_mismatch", params_hash)
                raise IntegrityError("request hash does not match payload")

        # 4. Replay protection for write-like tools (FR-093)
        if tier in WRITE_TIERS:
            if ctx.nonce in self._seen_nonces:
                self._audit(tool_name, ctx, "deny", "replayed_nonce", params_hash)
                raise ReplayError("duplicate nonce / idempotency key")
            self._seen_nonces.add(ctx.nonce)

        # 5. Strict schema + size validation (FR-092)
        if len(json.dumps(payload, default=str).encode()) > MAX_PAYLOAD_BYTES:
            self._audit(tool_name, ctx, "deny", "payload_too_large", params_hash)
            raise SchemaError("payload exceeds size limit")

        # 6. Execute (Pydantic strict validation inside the tool -> SchemaError on bad input)
        try:
            result = fn(**payload)
        except MCPSecurityError:
            raise
        except Exception as exc:  # noqa: BLE001
            self._audit(tool_name, ctx, "deny", f"schema_or_exec_error: {exc}", params_hash)
            raise SchemaError(f"invalid input or execution error: {exc}") from exc

        # 7. Output filtering (FR-094): annotate (do not silently strip) injected content
        flagged = _scan_output_for_injection(result)
        if flagged:
            result["_security_flags"] = {"prompt_injection_detected": sorted(set(flagged))}

        # 8. Audit logging (FR-095)
        self._audit(tool_name, ctx, "allow", "ok", params_hash, hashing.payload_hash(result))
        return result
