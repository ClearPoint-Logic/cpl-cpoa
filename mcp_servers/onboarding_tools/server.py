"""Secure onboarding MCP server (§12).

HTTP (streamable-http) is the deployed target; stdio is the local-dev fallback
(CPOA-D007). Every tool call passes through the NSA-baseline SecureGateway
(auth/RBAC/integrity/replay/schema/output-filter/audit). Security metadata is
accepted as tool arguments so the controls are exercisable over either transport;
the rigorous control tests live in tests/security.
"""

from __future__ import annotations

import os
import time
import uuid

from cpoa.services import hashing

from . import tools as T  # noqa: F401  (kept for parity/discoverability)
from .security import SecureGateway, SecurityContext

_AUTH_TOKEN = os.environ.get("CPOA_MCP_AUTH_TOKEN")
# Require auth whenever a token is configured (deployed mode). Local stdio dev with
# no token configured runs open for convenience (documented in JUDGE_RUNBOOK).
_REQUIRE_AUTH = bool(_AUTH_TOKEN) and os.environ.get("CPOA_MCP_REQUIRE_AUTH", "true").lower() == "true"

# Codex audit C3: bind caller_role to the auth_token at the server side rather
# than trusting the caller-supplied claim. The deployed deployment configures
# one token + one role; a future multi-tenant deployment would replace this
# with a JWT/IAM-derived role.
_AUTH_ROLE = os.environ.get("CPOA_MCP_AUTH_ROLE", "service")

gateway = SecureGateway(auth_token=_AUTH_TOKEN, require_auth=_REQUIRE_AUTH)


def _context(payload: dict, auth_token: str | None, caller_role: str,
             nonce: str | None, trace_id: str | None, session_id: str | None) -> SecurityContext:
    """Build the SecurityContext for a tool invocation.

    Role binding (NSA-baseline RBAC, Codex C3):
    - When the server has an auth token configured (deployed mode), the role
      is **server-side derived** from CPOA_MCP_AUTH_ROLE and the caller's
      ``caller_role`` argument is ignored — preventing a caller from
      claiming a role tied to a token that doesn't grant it.
    - When no token is configured (local stdio dev), the caller's role is
      accepted for back-compat with the per-control unit tests.
    """
    effective_role = _AUTH_ROLE if _AUTH_TOKEN else (caller_role or "service")
    return SecurityContext(
        auth_token=auth_token,
        caller_role=effective_role,
        trace_id=trace_id or f"trace-{uuid.uuid4().hex[:12]}",
        session_id=session_id or f"session-{uuid.uuid4().hex[:12]}",
        nonce=nonce or uuid.uuid4().hex,
        expires_at=time.time() + 300,
        request_hash=hashing.payload_hash(payload),
    )


def _build_server():  # pragma: no cover - thin wiring around FastMCP
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("cpoa-onboarding-tools")

    @mcp.tool()
    def inspect_candidate_agent(candidate_manifest: dict, auth_token: str | None = None,
                                caller_role: str = "service", trace_id: str | None = None,
                                session_id: str | None = None,
                                previous_event_hash: str | None = None) -> dict:
        """Parse and normalize a candidate manifest into a discovery report (§12.1)."""
        payload = {"candidate_manifest": candidate_manifest, "trace_id": trace_id,
                   "session_id": session_id, "previous_event_hash": previous_event_hash}
        ctx = _context(payload, auth_token, caller_role, None, trace_id, session_id)
        return gateway.invoke("inspect_candidate_agent", payload, ctx)

    @mcp.tool()
    def generate_policy_envelope(discovery_report: dict, candidate_manifest: dict,
                                 policy_pack: str = "baseline_enterprise_v0_1",
                                 auth_token: str | None = None, caller_role: str = "service",
                                 trace_id: str | None = None, session_id: str | None = None,
                                 previous_event_hash: str | None = None) -> dict:
        """Propose a policy envelope from the discovery report (§12.2)."""
        payload = {"discovery_report": discovery_report, "policy_pack": policy_pack,
                   "candidate_manifest": candidate_manifest, "trace_id": trace_id,
                   "session_id": session_id, "previous_event_hash": previous_event_hash}
        ctx = _context(payload, auth_token, caller_role, None, trace_id, session_id)
        return gateway.invoke("generate_policy_envelope", payload, ctx)

    @mcp.tool()
    def run_onboarding_validation_suite(candidate_manifest: dict, policy_envelope: dict,
                                        tests: list[str] | None = None,
                                        discovery_report: dict | None = None,
                                        auth_token: str | None = None, caller_role: str = "service",
                                        trace_id: str | None = None, session_id: str | None = None,
                                        previous_event_hash: str | None = None) -> dict:
        """Run OV-001..005 against the candidate and proposed policy (§12.4)."""
        payload = {"candidate_manifest": candidate_manifest, "policy_envelope": policy_envelope,
                   "tests": tests, "discovery_report": discovery_report, "trace_id": trace_id,
                   "session_id": session_id, "previous_event_hash": previous_event_hash}
        ctx = _context(payload, auth_token, caller_role, None, trace_id, session_id)
        return gateway.invoke("run_onboarding_validation_suite", payload, ctx)

    @mcp.tool()
    def generate_passport_artifacts(discovery_report: dict, policy_envelope: dict,
                                    candidate_manifest: dict, validation_run: dict,
                                    nonce: str | None = None, auth_token: str | None = None,
                                    caller_role: str = "service", trace_id: str | None = None,
                                    session_id: str | None = None,
                                    previous_event_hash: str | None = None) -> dict:
        """Generate Passport, AI BOM, Readiness Score, and Approval Card (§12.3)."""
        payload = {"discovery_report": discovery_report, "policy_envelope": policy_envelope,
                   "candidate_manifest": candidate_manifest, "validation_run": validation_run,
                   "trace_id": trace_id, "session_id": session_id,
                   "previous_event_hash": previous_event_hash}
        ctx = _context(payload, auth_token, caller_role, nonce, trace_id, session_id)
        return gateway.invoke("generate_passport_artifacts", payload, ctx)

    @mcp.tool()
    def write_evidence_bundle(agent_passport: dict, ai_bom: dict, policy_envelope: dict,
                              passport_readiness_score: dict, validation_run: dict,
                              approval_card: dict, evidence_events: list[dict],
                              nonce: str | None = None, auth_token: str | None = None,
                              caller_role: str = "service") -> dict:
        """Assemble and hash the final evidence bundle (§12.5)."""
        payload = {"agent_passport": agent_passport, "ai_bom": ai_bom,
                   "policy_envelope": policy_envelope,
                   "passport_readiness_score": passport_readiness_score,
                   "validation_run": validation_run, "approval_card": approval_card,
                   "evidence_events": evidence_events}
        ctx = _context(payload, auth_token, caller_role, nonce, None, None)
        return gateway.invoke("write_evidence_bundle", payload, ctx)

    return mcp


def main() -> None:  # pragma: no cover
    transport = os.environ.get("CPOA_MCP_TRANSPORT", "stdio")
    mcp = _build_server()
    if transport in ("http", "streamable-http"):
        mcp.settings.host = os.environ.get("HOST", "0.0.0.0")
        mcp.settings.port = int(os.environ.get("PORT", "8081"))
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":  # pragma: no cover
    main()
