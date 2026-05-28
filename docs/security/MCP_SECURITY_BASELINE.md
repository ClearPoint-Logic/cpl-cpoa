# MCP Security Baseline — control checklist (§12.6 / NFR-014)

The onboarding MCP server demonstrates a carefully-hardened enterprise MCP surface,
mapped to the **NSA CSI: Model Context Protocol — Security Design Considerations**
and the joint CSI on agentic AI. Controls are implemented in
[`mcp_servers/onboarding_tools/security.py`](../../mcp_servers/onboarding_tools/security.py)
as a `SecureGateway` that every tool call passes through, and proven by
[`tests/security/`](../../tests/security).

> **Honesty note:** This is a challenge demo. Signatures are `demo_stub`; some
> controls (egress allowlist, sandboxing) are documented as the production path and
> enforced at deploy time via Cloud Run config rather than in code. Nothing here
> claims production Anchor attestation.

| # | NSA baseline control | Requirement | Implementation | Test evidence |
|---|---|---|---|---|
| 1 | Supported components | Maintained SDK, pinned versions | `mcp` SDK (FastMCP), pinned in `requirements.txt`; deps vuln-scanned | `requirements.txt` lockfile |
| 2 | Trust boundaries | Separate UI / orchestrator / MCP / tools / candidate data | Candidate manifests + tool descriptions treated as untrusted data; gateway is the boundary | `test_prompt_injection_filter.py` |
| 3 | Origin verification | No unsanctioned dynamic tool discovery | Fixed 5-tool `TOOL_REGISTRY`; unknown tools denied | `test_mcp_auth.py::test_unknown_tool_denied` |
| 4 | **Authentication** (FR-090) | Reject unauthenticated requests | Bearer token check in deployed mode (`CPOA_MCP_AUTH_TOKEN`) | `test_mcp_auth.py` (missing/wrong/valid token) |
| 5 | **Authorization / RBAC** (FR-091) | Tool-level role + risk-tier checks | `ROLE_TIERS` maps caller role → permitted tool tiers | `test_mcp_auth.py` (auditor denied write, allowed read) |
| 6 | **Parameter validation** (FR-092) | Strict schema, enums, size, deny unknown | Pydantic `extra="forbid"` in tools + 256 KB size cap | `test_schema_validation.py` (unknown field, bad enum, missing required, oversize) |
| 7 | **Message integrity** (FR-093) | trace/session id, nonce, expiry, request hash | `SecurityContext` carries all; gateway verifies hash binding + expiry | `test_mcp_auth.py` (hash mismatch, expired) |
| 8 | **Replay protection** | Duplicate idempotency key rejected for writes | Per-gateway nonce store; write-tier tools reject seen nonces | `test_mcp_replay.py` |
| 9 | **Output filtering** (FR-094) | Tool output is untrusted before downstream use | Outputs scanned for injection markers; flagged via `_security_flags` | `test_prompt_injection_filter.py` |
| 10 | **Audit logging** (FR-095) | Log tool id, params hash, identity, decision, reason, output hash, trace id | `AuditRecord` per call (allow + deny) | `test_mcp_auth.py::test_audit_log_records_allow_and_deny` |
| 11 | Egress control (FR-096) | Allowlisted outbound; no fetch from candidate URLs | No tool performs arbitrary fetch; enforced at deploy via Cloud Run egress settings | deploy config (Stream B) |
| 12 | Sandboxing / least privilege (FR-097) | No shell/file/db unless required; constrained SA | Tools are pure functions over in-memory data; dedicated least-privilege service account at deploy | IAM notes (Stream B) |
| 13 | Vulnerability tracking | MCP dependency inventory + patch history | Documented here; demonstrated by the `unmaintained_mcp_server_agent` fixture (OV-002 dependency finding) | `tests/evals` (stretch fixture) |
| 14 | Discovery/scanning posture | Detect unhardened MCP servers | Simulated by the unmaintained-MCP stretch fixture + NSA-cited remediation | `fixtures/candidates/unmaintained_mcp_server_agent.json` |

**Transports:** HTTP (streamable-http) is the deployed target; stdio is local-dev
fallback only (CPOA-D007). Auth is required whenever `CPOA_MCP_AUTH_TOKEN` is set.

**Run locally:**
```bash
# stdio (dev)
python -m mcp_servers.onboarding_tools.server
# http (deployed target)
CPOA_MCP_TRANSPORT=http CPOA_MCP_AUTH_TOKEN=... PORT=8081 python -m mcp_servers.onboarding_tools.server
```
