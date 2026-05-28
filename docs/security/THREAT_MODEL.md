# Threat Model — ClearPoint Onboarding Agent (challenge demo)

Scope: the onboarding gate as deployed for judging. Demo-safe; not a production assurance.

## Trust boundaries
Each is a separate trust zone; data crossing a boundary is validated/untrusted:
1. **Judge browser ↔ Web UI** — HTTP basic auth gates the entire site (`app/web/middleware.ts`).
2. **Web UI ↔ API** — same-origin proxy; API re-enforces basic auth (defense in depth).
3. **API/orchestrator ↔ MCP server** — bearer-token auth + tool-level RBAC (NSA baseline).
4. **MCP server ↔ candidate manifests / tool descriptions** — **untrusted data**; scanned for
   prompt injection; never executed as instructions.
5. **Agents ↔ retrieved corpus** — retrieved snippets are quoted as evidence, not executed.

## Primary threats → controls
| Threat | Control | Evidence |
|---|---|---|
| Unauthenticated access to tools/data | Basic auth (UI+API), MCP bearer auth | `tests/security/test_mcp_auth.py` |
| Over-privileged tool use | Tool-level RBAC by risk tier | same |
| Indirect prompt injection via tool description | Detection + quarantine + output filtering | `tests/security/test_prompt_injection_filter.py`, OV-004 |
| Malformed/hostile payloads | Strict Pydantic schemas, size caps, deny-unknown | `tests/security/test_schema_validation.py` |
| Replay of state-changing calls | Nonce/idempotency + expiry + request hash | `tests/security/test_mcp_replay.py` |
| Tampered evidence | SHA-256 hash chain; mismatch blocks Ready | `tests/unit/test_hashing.py` |
| Unsafe "Ready" on risky agents | Deterministic fail-closed decision (§14) | `tests/unit/test_decisioning.py` |
| Supply-chain (unmaintained MCP) | Dependency-health finding (NSA guidance) | `unmaintained_mcp_server_agent` fixture |

Full control checklist: [`MCP_SECURITY_BASELINE.md`](MCP_SECURITY_BASELINE.md).

## Agent Engine vs Cloud Run (CPOA-D019 / NFR-015)
The canonical **primary** orchestrator runtime is **Agent Engine / Agent Runtime**. For the challenge
demo we run the orchestrator on **Cloud Run** (same API contract, `agents/onboarding_orchestrator`
deployable to Agent Engine unchanged). Rationale: keep credit burn light (pre-authorized budget) and
guarantee a reproducible, deterministic judge demo. The ADK `root_agent` is Agent-Engine-ready
(`agents/run.py` drives it via the ADK Runner); promoting it is a deployment-config change, not a code
change. Documented as the accepted fallback, not a silent gap.

## Egress & least privilege (FR-096/097)
No tool performs arbitrary outbound fetches or shell/file/db access; tools are pure functions over
in-memory data. Cloud Run services run scale-to-zero; the MCP service is deployed
`--no-allow-unauthenticated` (private). A dedicated least-privilege service account is the production
hardening step.

## Data & IP
All inputs are synthetic fixtures; grounded corpus is public (NSA CSI, NIST RMF, EU AI Act). No
customer data, secrets, production scoring weights, or build-pack content. See
[`DATA_AND_IP_BOUNDARY.md`](DATA_AND_IP_BOUNDARY.md) and [`../../PROPRIETARY.md`](../../PROPRIETARY.md).

## Honesty / limitations
Demo-stub signatures (not production attestation); demo-only readiness score (not CAS/ECS); onboarding
recommendation, not certified compliance; onboarding gate only — continuous attestation is roadmap.
