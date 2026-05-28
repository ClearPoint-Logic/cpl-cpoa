# ClearPoint Onboarding Agent

**A net-new ADK + Gemini multi-agent system that helps enterprises *hire* AI agents into the workforce — with a passport, a job description, a résumé, and a personnel file at the gate.**

> **Google for Startups AI Agents Challenge — Track 1: Build (Net-New Agents)**

**▶ Live judge demo:** https://cpoa-web-y4zowv3hva-uc.a.run.app — basic auth `judge` / `MLcdaYGa9XcHihAu`
(see [`docs/submission/JUDGE_RUNBOOK.md`](docs/submission/JUDGE_RUNBOOK.md)). No CLI required.

---

## The workforce frame

Every enterprise has a hiring process for humans: an identity check, a job description, declared
qualifications, a manager, and a personnel file. AI agents are joining the workforce — and most
organizations have **no equivalent process** for them.

ClearPoint Onboarding Agent gives every new agent the same structured intake **before it does any
work**:

| Human onboarding | AI-agent equivalent | Artifact issued |
|---|---|---|
| ID badge | Identity & trust record | **Agent Passport** |
| Job description | Authorized scope of action | **Policy Envelope** |
| Résumé | Declared models, tools, dependencies | **AI Bill of Materials** |
| Personnel file | The record that follows it forward | **Evidence Bundle** |

It inspects a candidate agent manifest, runs a multi-agent workflow (discovery → grounded policy →
artifacts → validation → evidence), and ends in a clear decision: **Ready**, **Ready with
Conditions**, or **Blocked Pending Remediation** — with traceable evidence for security, compliance,
finance, and business owners.

## Honest scope (please read)

- This is a **net-new Track 1 agent inspired by the ClearPoint Meridian architecture**. It is **not**
  a claim that Meridian is live, and it is **not** a refactor of an existing product.
- It implements the **onboarding gate only**. ClearPoint Logic's differentiated thesis —
  *continuous attestation*, where governed agents continuously validate the workforce-management
  layer itself — is the **roadmap**, not a built feature here.
- Artifacts are **demo-safe**: synthetic fixtures, `demo_stub` signatures (not production
  cryptographic attestation), and a **Passport Readiness Score** that is explicitly **not** the
  proprietary production scoring system.

## Google stack

**ADK** (multi-agent orchestration) · **Gemini via Vertex AI** (reasoning) · **Google Stitch** (UI
design source) · **Model Context Protocol** (secure tool surface) · **Agent Engine / Cloud Run**
(runtime) · **Vertex AI Search / RAG** (grounding, with local fallback) · **Cloud Logging & Trace**
(observability).

The deterministic gate decision (score, caps, blockers, final decision) is computed by plain Python;
Gemini contributes summaries, rationale, and explanations only.

## Repository layout

```
cpoa/            Schemas (§11 data contracts) + deterministic services (hashing, scoring, decisioning)
agents/          ADK orchestrator + six subagents (discovery, policy, artifact, validation, evidence, explanation)
mcp_servers/     Secure HTTP MCP server exposing the 5 onboarding tools
app/             FastAPI backend (app/api) + Next.js judge UI (app/web)
fixtures/        Test Agent Zoo (8 candidate manifests), policy pack, registry fixture
corpus/          Grounded corpus (public sources: NSA MCP CSI, NIST AI RMF, EU AI Act) + attribution
tests/           unit / integration / evals / security
scripts/         run_demo.py (CLI), eval + seed scripts
infra/           Cloud Run Dockerfiles + Agent Engine deploy config
docs/            canonical spec, architecture, design, security, submission
```

## Quickstart

```bash
# 1. Environment
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in GCP project + Vertex settings

# 2. Run the demo on a fixture (CLI)
python scripts/run_demo.py --candidate fixtures/candidates/safe_research_agent.json
python scripts/run_demo.py --candidate fixtures/candidates/prompt_injected_mcp_agent.json
```

> Gemini runs **via Vertex AI** (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`). Per the official challenge rules,
> Gemini on Google AI Studio is not eligible for challenge credits.

## Documentation

- **Canonical spec:** [`docs/canonical/CPOA-GFS-AIAC-2026-CANONICAL.md`](docs/canonical/CPOA-GFS-AIAC-2026-CANONICAL.md)
- **Rules reconciliation (binding deltas):** [`docs/submission/RULES_RECONCILIATION.md`](docs/submission/RULES_RECONCILIATION.md)
- **Architecture:** `docs/architecture/ARCHITECTURE.md` _(in progress)_
- **Judge runbook:** `docs/submission/JUDGE_RUNBOOK.md` _(in progress)_

## Status

🚧 **Active build** toward the submission deadline of **June 5, 2026, 5:00 PM PT**. Built by Jared
Mabry (ClearPoint Logic) with Claude Code. See the task list and `docs/` for current state.
