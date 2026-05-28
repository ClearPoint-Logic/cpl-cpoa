# Security Policy — ClearPoint Onboarding Agent

## Reporting a vulnerability

If you have discovered a security issue in CPOA, please **do not file a public
issue.** Email **security@clearpointlogic.com** with:

- A description of the issue and its impact.
- Steps to reproduce (ideally a minimal proof of concept).
- Your assessment of severity.
- Whether you've published or disclosed elsewhere.

We aim to acknowledge reports within two business days and to provide a remediation
plan within five. We do not currently run a paid bug-bounty program; we will
credit reporters in `CHANGELOG.md` and in the release notes for the fix unless you
ask us not to.

## Supported versions

| Version | Supported |
|---|---|
| 0.5.x   | ✅ Active |
| 0.4.x   | ✅ Submission release; security fixes only |
| < 0.4   | ❌ |

## Threat model

The full threat model lives at [`THREAT_MODEL.md`](THREAT_MODEL.md).

## Defense in depth — what's enforced today

CPOA layers controls so a single failure does not compromise the system.

### Network + transport

- **TLS** — Google-managed certificate via Cloud Run domain mapping; auto-rotated.
- **HSTS** — `max-age=31536000; includeSubDomains` (no `preload`, keeping the
  domain reversible).
- **HTTP → HTTPS redirect** — Google Frontend redirects HTTP to HTTPS.

### Authentication + authorization

- **HTTP basic auth** gates the judge UI (`app/web/middleware.ts`). The auth
  check uses constant-time comparison via the FastAPI `secrets.compare_digest`
  on the API side.
- **A2A Agent Card** at `/.well-known/agent.json` is intentionally open —
  this is the A2A discovery convention. State-changing A2A endpoints
  (`/a2a/v1/message:send`) require the basic-auth credential.
- **MCP server** uses a bearer token (`CPOA_MCP_AUTH_TOKEN`) plus per-tool
  RBAC (role check, expiry, nonce, request-hash validation). 19 security
  tests verify the controls.

### Browser-side hardening

The following response headers are set on every web response (`app/web/next.config.mjs`):

| Header | Value |
|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `Content-Security-Policy` | tight defaults; `frame-ancestors 'none'`; `form-action 'self'`; `base-uri 'self'` |
| `X-Frame-Options` | `DENY` |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), interest-cohort=(), payment=(), usb=()` |
| `X-DNS-Prefetch-Control` | `off` |

### Application controls

- **Strict schemas** — every §11 contract uses Pydantic v2 with
  `extra="forbid"`. Unknown fields are rejected on the wire.
- **Deterministic decisioning** — score, caps, blockers, and the final
  Ready / Conditional / Blocked decision are pure Python. Gemini contributes
  prose only, so the audit trail is reproducible.
- **Fail-closed pipeline** — any stage failure routes to
  `Blocked Pending Remediation` with a fail-closed evidence event.
- **Prompt-injection scanning** — `cpoa/services/injection.py` scans tool
  descriptions and outputs for instruction-like content; the validation
  suite blocks on detection.
- **Hash-chained evidence** — every event includes `previous_event_hash`;
  the bundle hash is computed over canonical-JSON serialization. A
  parameterized recompute test runs against every fixture in CI.

### Data handling

- **No customer PII in the repo.** Fixtures are synthetic and labeled.
- **`.env` is gitignored.** Credentials and secrets live in environment
  variables on Cloud Run, never in committed files.
- **Firestore** is the run store in production. Run payloads are stored as a
  single JSON string per document to sidestep nested-array restrictions.
- **No logs of credentials.** The API rejects credentials silently and
  responds with `401 Unauthorized`; nothing about the supplied value is
  echoed back or logged.

## Signing modes

| Mode | Use | What it is |
|---|---|---|
| `local_hmac` (default) | local + demo | HMAC-SHA256 with a per-deployment secret; real signature, verifiable by any holder of the secret |
| `kms` (env-flagged) | production | Cloud KMS asymmetric signing over the canonical event hash; verifiable with `cosign` or `gcloud kms verify` |

The signing mode is published live at `/api/health` under `modes.signing`.

## Dependency management

`requirements.txt` is pinned. Renovate or Dependabot integration is
documented as roadmap; in the interim, dependency updates are reviewed PR
by PR with security-relevant changes called out in the PR body.

## Incident response

In the event of a confirmed compromise:

1. **Revoke** — rotate `CPOA_JUDGE_BASIC_AUTH_PASS`, `CPOA_MCP_AUTH_TOKEN`,
   and any KMS key versions used for signing. Update the live Cloud Run
   service env.
2. **Quarantine** — if a Manage / Operate event chain has been written into
   Firestore by an attacker, mark the offending agent records and preserve
   for forensics.
3. **Disclose** — coordinated disclosure to affected parties within five
   business days, per the reporting policy above.
4. **Postmortem** — root cause + remediation summary published in
   `CHANGELOG.md` under the relevant release.
