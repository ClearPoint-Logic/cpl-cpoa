# ClearPoint Onboarding Agent

**AI Workforce Management — the first six phases shipped end-to-end on Google's agent platform.** ClearPoint Onboarding Agent (CPOA) hires AI agents the way enterprises hire humans, then keeps managing them: discover the unmanaged ones running in your environment, onboard them through a deterministic gate, manage their day-to-day lifecycle, govern them against the public regulatory frameworks, monitor them in production, and grow them along an explicit autonomy ladder.

> **Google for Startups AI Agents Challenge — Track 1: Build (Net-New Agents)**

**▶ Live judge demo:** [https://cpoa.clearpointlogic.com](https://cpoa.clearpointlogic.com).
Testing credentials are provided privately in the Devpost submission's testing-instructions
field; see [`docs/submission/JUDGE_RUNBOOK.md`](docs/submission/JUDGE_RUNBOOK.md) for the
end-to-end evaluation path. No CLI required.

---

## The workforce frame

Every enterprise has a hiring process for humans: an identity check, a job description, declared
qualifications, a hiring manager, and a personnel file. AI agents are joining the workforce — and
most organizations have **no equivalent process** for them.

CPOA gives every new agent the same structured intake **before it does any work**, and then keeps
managing them across the rest of the lifecycle:

| Human onboarding | AI-agent equivalent | Artifact issued |
|---|---|---|
| ID badge | Identity, owner, and trust tier | **Agent Passport** |
| Job description | Authorized scope of action | **Policy Envelope** |
| Résumé | Declared models, tools, dependencies | **AI Bill of Materials** |
| Personnel file | The record that follows it forward | **Evidence Bundle** |

## The AI Workforce Management lifecycle — all six phases shipped

| Phase | What it does | Module | UI |
|---|---|---|---|
| **Discover** | Real HTTPS crawl of A2A Agent Cards. Classifies findings against the governed registry; surfaces unmanaged shadow IT. | `cpoa/services/agent_discovery.py` | `/workforce` → Discovered |
| **Onboard** | Six-stage gate: Discovery → Grounded Policy → Artifact → Validation → Evidence → Explanation. Deterministic Ready / Conditional / Blocked decision. Gemini narrates. | `cpoa/services/engine.py` + `agents/` | `/agents` (Pre-Boarding) |
| **Manage** (HR Console) | Day-to-day actions: place on leave, return, manager handoff, role change. Each action appends a real hash-chained evidence event to the agent's personnel file. | `cpoa/services/manage.py` | `/workforce` → Onboarded |
| **Govern** (Compass) | Live control mapping: every enforced control (OV-001..005, MCP NSA baseline, hash-chained evidence) mapped to specific NSA MCP CSI / NIST AI RMF / EU AI Act passages from the live corpus. | `cpoa/services/govern.py` | `/govern` |
| **Operate** (Sentinel) | Fleet health across the active roster. Deterministic anomaly detection (BLOCKER-AT-INTAKE, STALE-LEAVE, HIGH-AUTONOMY-HIGH-RISK, MULTI-CONDITION-AGENT). Anomalies write into the chain. | `cpoa/services/operate.py` | `/operate` |
| **Optimize** (Talent Development) | Per-agent development plans — open conditions become career-development items; the autonomy ladder (L0_observe → L5_high_impact_autonomous) is the promotion track. | `cpoa/services/optimize.py` | `/optimize` |

The same hash-chained personnel file accumulates events across every phase. Discovery findings,
the original onboarding bundle, Manage actions, and Operate anomalies all chain into one
continuous, tamper-evident record.

## Built on Google's agent platform

| Layer | Google product |
|---|---|
| Multi-agent orchestration | **Agent Development Kit (ADK)** — root `LlmAgent` + 6 subagents |
| Reasoning | **Gemini 3.5 Flash on Vertex AI** (region: `global`) |
| Tool surface | **Model Context Protocol (MCP)** — hardened to the NSA MCP security baseline |
| Grounding | **Vertex AI Search** (Discovery Engine) — env-driven, with deterministic local fallback |
| Interoperability | **Agent-to-Agent (A2A)** protocol — open Agent Card at `/.well-known/agent.json` |
| Persistence | **Firestore** — durable runs across scale-to-zero |
| Observability | **Cloud Trace** spans alongside a SHA-256 hash-chained evidence log |
| Runtime | **Cloud Run** (3 services: web, API, MCP) deployed via **Cloud Build** |
| Design | **Google Stitch** → Next.js + Tailwind, Material 3 tokens |

The onboarding decision — score, caps, blockers, final disposition — is computed deterministically
in plain Python from §11 schemas. **Gemini contributes summaries, rationale, and explanations
only.** The gate is reliable, reproducible, and audit-defensible by construction.

## By the numbers

Every figure below is measurable from the deployed build — not aspiration.

| Metric | Value |
|---|---|
| Deterministic decision latency per onboarding run | **< 5 ms** (CLI; sub-second incl. live Gemini narration) |
| Pre-Boarding fixtures deciding correctly | **8 / 8** across 8 production-shaped risk archetypes |
| Fail-closed pre-employment-screening checks | **5** (OV-001..005) |
| Live regulatory-citation resolutions in Compass | **29** across **3** frameworks (NSA MCP CSI + NIST AI RMF + EU AI Act) |
| NSA MCP security baseline tests passing | **19 / 19** (auth, RBAC, integrity, replay, output filter, audit) |
| Total tests (unit, integration, evals, security) | **186** |
| Code coverage | **90 %** |
| AI Workforce Management lifecycle phases shipped | **6 / 7** |
| Production security headers set | **7** (HSTS, CSP, X-Frame-Options, Permissions-Policy, Referrer-Policy, nosniff, dns-prefetch off) |
| Evidence signature mode | **`local_hmac`** (real HMAC-SHA256) — `kms` env-flag ready |
| Cloud KMS-ready signing | **yes** — `CPOA_SIGNING_MODE=kms` + `CPOA_SIGNING_KEY=...` |

### Enterprise-pilot scenario (illustrative)

For a 200-agent fleet through the gate over a typical month:
- **Decisions:** ~200 onboarding runs + ~600 lifecycle actions (Manage HR Console) ≈ 800 audit events
- **Audit footprint:** ~3 MB of canonical-JSON evidence; ~24 KB of hash-chain metadata
- **Reviewer time-to-decision:** ~3 minutes per agent (intake → Background Check → Approval Card) vs. ~3 days for ad-hoc spreadsheet review
- **Regulatory traceability:** every approved control linked to a specific NSA / NIST / EU AI Act passage at decision time, not retroactively

## How this sits with Google's Gemini Enterprise Agent Platform

Google's Gemini Enterprise Agent Platform (April 2026) ships **Agent Registry**, **Agent
Identity**, **Agent Gateway**, dynamic **AI Bill of Materials**, and **Agent Anomaly Detection**
as platform primitives. CPOA is the workforce/HR **application layer** that consumes those
primitives. The platform gives you the registry; **CPOA is the HR department that decides who
gets hired into it** — and the management surface that operates the workforce afterwards.

## What ships in this repository

- A net-new ADK multi-agent workflow with six purpose-built subagents (discovery, grounded
  policy, artifact, validation, evidence, explanation) under a root `LlmAgent`
- A real HTTP MCP server with auth, RBAC, message integrity, replay protection, strict schemas,
  output filtering, and audit logging — **19 security tests** pass
- A **Pre-Boarding roster** of eight candidate agents covering safe intake, missing governance,
  regulated data, budget exposure, prompt injection, privileged admin, unmaintained MCP, and
  grounding-dependent scenarios — **5/5 must-ship decisions correct, 8/8 overall**, fully
  reproducible offline
- **Pre-employment screening** via the Onboarding Validation Suite — five fail-closed checks
  (OV-001..005) across identity, governance, regulated data, security posture, and supply chain
- A live **A2A directory crawl** with five representative agent cards hosted at
  `/api/demo-fleet/<name>/.well-known/agent.json` so the scan exercises real network paths
- An **HR Console** with real lifecycle actions (place on leave / return / manager handoff /
  role change) — every action lands an evidence event
- A live **control-mapping matrix** (Compass) — every CPOA control mapped to specific NSA /
  NIST / EU AI Act passages, resolved live against the grounding corpus
- A **fleet-health Sentinel** with deterministic anomaly rules — derives live signals from
  onboarding outcomes and the HR Console event log
- A **Talent Development** view turning open conditions into per-agent career-development items
- Tamper-evident SHA-256 hash chain over canonical JSON for every Evidence Bundle (the personnel
  file) — every event in the run is verifiable; **recompute test runs against every fixture in CI**
- A2A discoverability so other enterprise agents can invoke onboarding as a skill
- Production security headers — HSTS, CSP, X-Frame-Options, Permissions-Policy, Referrer-Policy
- Cloud Run deployment, custom domain, judge-gated UI, PDF / Markdown / JSON evidence export

## Honest scope

CPOA is **newly created during the contest period** and meets the contest's net-new requirement.
What stays caveat-worthy in any production:

- **Synthetic candidate fixtures.** We don't have customer agents on the Pre-Boarding roster yet.
- **A representative A2A directory** is hosted alongside the API so the Discover scan exercises
  real network paths. In a customer deployment the scanner points at the enterprise inventory
  APIs (Agent Engine catalog, Cloud Run service inventory, A2A directory services) — same code.
- **Continuous attestation across every running interaction** is the next layer; the lifecycle
  shipped here covers six of the seven Workforce Management phases.

The Passport Readiness Score is a **deterministic, reproducible, audit-grade measure**. The
hash-chained evidence is tamper-evident with a recompute test that runs against every fixture in
CI. The MCP server passes the NSA-baseline security tests. Nothing about the gate ceremony is
demo-grade.

## Repository layout

```
cpoa/            Schemas (§11 data contracts) + deterministic services
  schemas/         Pydantic v2 strict contracts (Passport, AI BOM, Policy, Validation, Evidence)
  services/        engine, discovery, policy, validation_suite, scoring, decisioning, evidence_log,
                   agent_discovery (Discover), manage (Manage), govern (Compass), operate (Sentinel),
                   optimize (Talent Dev), grounding, hashing, exports, tracing
agents/          ADK orchestrator + six subagents
mcp_servers/     Secure HTTP MCP server (NSA security baseline)
app/             FastAPI backend (app/api) + Next.js judge UI (app/web)
fixtures/        Pre-Boarding roster (8 candidate manifests), policy pack, registry fixture
corpus/          Grounded corpus (NSA MCP CSI, NIST AI RMF, EU AI Act) + attribution
tests/           unit / integration / evals / security  (160+ tests)
scripts/         run_demo.py (CLI), eval + Vertex AI Search seed scripts
infra/           Cloud Run Dockerfiles + Agent Engine deploy config
docs/            architecture, security, submission
```

## Quickstart

```bash
# 1. Environment
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in GCP project + Vertex settings

# 2. Run the gate on a fixture (CLI)
python scripts/run_demo.py --candidate fixtures/candidates/safe_research_agent.json
python scripts/run_demo.py --candidate fixtures/candidates/prompt_injected_mcp_agent.json

# 3. Tests + lint
pytest -q                  # full suite (unit / integration / evals / security)
ruff check .
```

> Gemini runs **via Vertex AI** (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`). Per the official challenge
> rules, Gemini on Google AI Studio is not eligible for challenge credits.

## Documentation

- **Architecture:** [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md)
- **Judge runbook:** [`docs/submission/JUDGE_RUNBOOK.md`](docs/submission/JUDGE_RUNBOOK.md)
- **Rules reconciliation:** [`docs/submission/RULES_RECONCILIATION.md`](docs/submission/RULES_RECONCILIATION.md)
- **Devpost draft:** [`docs/submission/DEVPOST_DRAFT.md`](docs/submission/DEVPOST_DRAFT.md)

## Status

Shipped and live at [cpoa.clearpointlogic.com](https://cpoa.clearpointlogic.com) for the
**June 5, 2026** submission. Built by **Jared Mabry, ClearPoint Logic** with Claude Code.
