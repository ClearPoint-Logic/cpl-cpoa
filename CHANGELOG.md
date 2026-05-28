# Changelog

All notable changes to ClearPoint Workforce Agent are recorded here. The
format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- (next changes go here)

## [0.5.0] — 2026-05-28

The "AI Workforce Management — full lifecycle" release. Adds five new
lifecycle phases on top of the original onboarding gate and lands the
Codex audit fixes.

### Added — lifecycle phases

- **Discover** (`cpoa/services/agent_discovery.py`, `/workforce` Discovered tab)
  — Real HTTPS scan of A2A Agent Cards across a representative directory;
  classifies findings against the governed registry; surfaces unmanaged
  shadow IT with a one-click "Send to Pre-Boarding."
- **Manage / HR Console** (`cpoa/services/manage.py`, `/workforce` Onboarded
  tab) — Real lifecycle actions: Place on Leave, Return, Manager Handoff,
  Role Change. Every action lands a chain-linked evidence event on the
  agent's personnel file.
- **Govern / Compass** (`cpoa/services/govern.py`, `/govern`) — Live control
  matrix mapping every CWA control to specific NSA MCP CSI / NIST AI RMF /
  EU AI Act passages from the grounding corpus.
- **Operate / Sentinel** (`cpoa/services/operate.py`, `/operate`) — Fleet
  health with deterministic anomaly detection over real onboarding + Manage
  signals.
- **Optimize / Talent Development** (`cpoa/services/optimize.py`, `/optimize`)
  — Per-agent development plans; open conditions become career-development
  items; autonomy ladder L0_observe → L5_high_impact_autonomous is the
  promotion track.

### Added — quality & posture

- **Bundle-hash recompute test** parameterized across every fixture in CI
  (`tests/unit/test_bundle_hash_recompute.py`).
- **Production security headers** (`app/web/next.config.mjs`): HSTS, CSP,
  X-Frame-Options, X-Content-Type-Options, Referrer-Policy,
  Permissions-Policy.
- **`/api/health` runtime modes envelope** publishes
  storage_active / storage_degraded / grounding / signing for ops visibility.
- **A2A Agent Card** is now reachable at the public URL
  (`/.well-known/agent.json`); Next.js rewrites + middleware allow-list cover
  the discovery surface unauthenticated.
- **Apache 2.0 LICENSE**, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `CHANGELOG.md`, `DEPLOYMENT.md`, `docs/USER_JOURNEYS.md`.

### Changed

- **`EventType`** extended with `manage.*`, `operate.*` event types.
- **`SignatureType`** extended with `local_hmac` and `kms` (both real
  signing modes; `demo_stub` retained for backward compat).
- **Grounding mode** now driven by `CPOA_GROUNDING_MODE`; previously the
  engine called the local retriever directly regardless of env.
- **Approval card bundle_id** stamped before bundle hashing so the bundle
  hash recomputes deterministically (Codex audit C1).

### Fixed

- **C1 — Evidence bundle hash recompute** (Codex audit).
- **C5 — Credentials removed from public docs** (README, JUDGE_RUNBOOK).
- **H1 — A2A card reachable through web** (middleware + rewrites).
- **M1 — Broken file path references** in ACCEPTANCE + ARCHITECTURE.
- **M2 — Judge page evaluation copy** matched to the 2-minute video cap.

## [0.4.0] — 2026-05-27

Initial submission build for the Google for Startups AI Agents Challenge
2026 (Track 1: Build — Net-New Agents).

### Added

- ADK multi-agent orchestrator with root `LlmAgent` + 6 purpose-built
  subagents (discovery, grounded policy, artifact, validation, evidence,
  explanation).
- NSA MCP security baseline (19 security tests).
- Pre-Boarding roster — 8 candidate-agent fixtures (5 must-ship + 3 stretch).
- Onboarding Validation Suite — 5 fail-closed checks (OV-001..005).
- Vertex AI Search grounding seam + local-corpus fallback.
- A2A protocol surface — Agent Card + task submission.
- Firestore persistence; Cloud Trace observability.
- PDF / Markdown / JSON evidence export.
- Production-grade Next.js + Tailwind UI on Cloud Run.
- Custom domain at cpoa.clearpointlogic.com.
