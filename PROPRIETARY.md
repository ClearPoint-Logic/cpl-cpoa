# Proprietary boundary & IP notice

This repository is **ClearPoint Logic confidential**. It is a challenge-specific build for the Google
for Startups AI Agents Challenge. Access is limited to ClearPoint Logic founders, the build agents,
and challenge judges through an approved access path (private-repo allowlist or the sanitized
`public-safe-export` branch with HTTP basic-auth judge access).

## What this repo MAY contain (challenge-safe)

- The challenge canonical spec (`docs/canonical/`).
- Synthetic candidate manifests, a demo policy pack, and synthetic registry fixtures.
- Demo-safe artifact generation: Agent Passport, AI BOM, Policy Envelope, Evidence Bundle.
- The **Passport Readiness Score** (demo-only; flagged `not_production_cas_or_ecs: true`).
- `demo_stub` evidence signatures (clearly labeled non-production).
- A grounded corpus assembled **only** from public sources (NSA MCP CSI, NIST AI RMF subset, EU AI
  Act selected articles) plus CWA's own demo content, with per-excerpt attribution.
- ADK agent code, the secure MCP server, Stitch design exports, eval harness, deployment config.

## What this repo MUST NOT contain (protected)

- The main ClearPoint Logic build pack or non-public canonicals.
- Internal strategy-brief source files, roadmap, or pricing/margin details.
- Production **CAS/ECS** scoring weights or tuning logic.
- Anchor signing-key design or production cryptographic attestation internals.
- Continuous Validation Agent Suite implementation details (Sentinel, Forensics, Drift, Red Team,
  Regulatory Watch).
- Customer data, production telemetry, secrets, or credentials.

## Honesty rules (enforced in code & docs)

- Continuous attestation is referenced as **roadmap only**; nothing claims the suite is built.
- Evidence bundles carry explicit `limitations`.
- Docs distinguish the demo onboarding gate from production Meridian/Anchor capabilities.

See `docs/security/DATA_AND_IP_BOUNDARY.md` for the operational checklist.
