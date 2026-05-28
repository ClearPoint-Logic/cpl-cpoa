# ClearPoint Onboarding Agent

**The AI Workforce Management onboarding gate. Built net-new on Google's agent platform — Agent Development Kit, Gemini on Vertex AI, the Model Context Protocol, Vertex AI Search, Cloud Run, and the Agent-to-Agent (A2A) protocol — to hire AI agents the way enterprises hire humans: with an ID badge, a job description, a résumé, and a personnel file before the first day on the job.**

> **Google for Startups AI Agents Challenge — Track 1: Build (Net-New Agents)**

**▶ Live judge demo:** [https://cpoa.clearpointlogic.com](https://cpoa.clearpointlogic.com) — basic auth `judge` / `MLcdaYGa9XcHihAu`
(see [`docs/submission/JUDGE_RUNBOOK.md`](docs/submission/JUDGE_RUNBOOK.md)). No CLI required.

---

## The workforce frame

Every enterprise has a hiring process for humans: an identity check, a job description, declared
qualifications, a hiring manager, and a personnel file. AI agents are joining the workforce — and
most organizations have **no equivalent process** for them.

ClearPoint Onboarding Agent is the AI Workforce Management onboarding gate. It gives every new
agent the same structured intake **before it does any work**:

| Human onboarding | AI-agent equivalent | Artifact issued |
|---|---|---|
| ID badge | Identity, owner, and trust tier | **Agent Passport** |
| Job description | Authorized scope of action | **Policy Envelope** |
| Résumé | Declared models, tools, dependencies | **AI Bill of Materials** |
| Personnel file | The record that follows it forward | **Evidence Bundle** |

It inspects a candidate agent manifest, runs a multi-agent workflow (discovery → grounded policy →
artifacts → validation → evidence), and ends in a clear decision — **Ready**, **Ready with
Conditions**, or **Blocked Pending Remediation** — with traceable, hash-chained evidence for
security, compliance, finance, and the business owner.

## Built on Google's agent platform

| Layer | Google product |
|---|---|
| Multi-agent orchestration | **Agent Development Kit (ADK)** — root `LlmAgent` + 6 subagents |
| Reasoning | **Gemini 3.5 Flash on Vertex AI** (region: `global`) |
| Tool surface | **Model Context Protocol (MCP)** — hardened to the NSA MCP security baseline |
| Grounding | **Vertex AI Search** (Discovery Engine) with a local-corpus fallback |
| Interoperability | **Agent-to-Agent (A2A)** protocol — Agent Card at `/.well-known/agent.json` |
| Persistence | **Firestore** for durable runs across scale-to-zero |
| Observability | **Cloud Trace** spans alongside a hash-chained evidence log |
| Runtime | **Cloud Run** (3 services: web, API, MCP) deployed via **Cloud Build** |
| Design | **Google Stitch** → Next.js + Tailwind, with Material 3 tokens |

The onboarding decision — score, caps, blockers, final disposition — is computed deterministically
in plain Python from §11 schemas. **Gemini contributes summaries, rationale, and explanations
only.** The gate is reliable, reproducible, and audit-defensible by construction.

## What ships in this repository

- A net-new ADK multi-agent workflow with six purpose-built subagents
- A real HTTP MCP server with auth, RBAC, message integrity, replay protection, strict schemas,
  output filtering, and audit logging — **19 security tests** pass
- Eight candidate-agent fixtures spanning safe intake, missing governance, regulated data, budget
  exposure, prompt injection, privileged admin, unmaintained MCP, and grounding-dependent
  scenarios — **5/5 must-ship decisions correct, 8/8 overall**, fully reproducible offline
- Tamper-evident SHA-256 hash chain over canonical JSON for every evidence bundle
- A2A discoverability so other enterprise agents can invoke onboarding as a skill
- Cloud Run deployment, custom domain, judge-gated UI, PDF / Markdown / JSON evidence export

## Honest scope (please read)

- This is a **net-new Track 1 agent inspired by the ClearPoint Meridian architecture**. It is **not**
  a claim that Meridian is live, and it is **not** a refactor of an existing product.
- It implements the **onboarding gate only** — one phase of the AI Workforce Management lifecycle.
  ClearPoint Logic's differentiated thesis — *continuous attestation*, where governed agents
  continuously validate the workforce-management layer itself — is the **roadmap**, not a built
  feature here.
- Artifacts are **demo-safe**: synthetic fixtures, `demo_stub` signatures (not production
  cryptographic attestation), and a **Passport Readiness Score** that is explicitly **not** the
  proprietary production scoring system.

## Repository layout

```
cpoa/            Schemas (§11 data contracts) + deterministic services (hashing, scoring, decisioning)
agents/          ADK orchestrator + six subagents (discovery, policy, artifact, validation, evidence, explanation)
mcp_servers/     Secure HTTP MCP server exposing the onboarding tools
app/             FastAPI backend (app/api) + Next.js judge UI (app/web)
fixtures/        Pre-Boarding roster (8 candidate manifests), policy pack, registry fixture
corpus/          Grounded corpus (public sources: NSA MCP CSI, NIST AI RMF, EU AI Act) + attribution
tests/           unit / integration / evals / security
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
