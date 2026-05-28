# Devpost Submission — ClearPoint Onboarding Agent

**Track:** Track 1 — Build (Net-New Agents)
**Tagline:** The AI Workforce Management onboarding gate. Built net-new on Google's agent platform — ADK, Gemini on Vertex AI, MCP, Vertex AI Search, Cloud Run, and the A2A protocol — to hire AI agents the way enterprises hire humans.

## Inspiration

AI agents are joining the enterprise workforce, and most organizations have **no repeatable process
to hire them.** Humans get an identity, a job description, declared qualifications, a hiring
manager, and a personnel file before they touch anything sensitive. Agents deserve the same
discipline. We treat agents as workforce — not tooling — and give every new agent the same
structured intake a human gets on day one. That framing is universal: every security officer,
finance leader, compliance counsel, and business owner already understands a passport, a job
description, a résumé, and a personnel file. **AI Workforce Management** is the category. The
onboarding gate is the entry point.

### How this sits with Google's Gemini Enterprise Agent Platform

Google's Gemini Enterprise Agent Platform (April 2026) ships **Agent Registry**, **Agent
Identity**, **Agent Gateway**, dynamic **AI Bill of Materials**, and **Agent Anomaly Detection** as
platform primitives. ClearPoint Onboarding Agent is **not** a competing platform — it is the
workforce/HR **application layer** that consumes those primitives. The platform gives you the
registry; CPOA is the **HR department that decides who gets hired into it** and produces the
audit-grade evidence the platform expects. The terms *Agent Passport*, *AIBOM*, and *Evidence
Bundle* are now widely used in the agent-governance space (Cubitrek Agent Passport v0.1, ERC-8004,
the open `agent-passport-system` library, EU AI Act audit plugins). What makes CPOA distinct is
the workforce framing: a Pre-Boarding roster, deterministic Ready / Conditional / Blocked
decisions narrated by Gemini, and a hash-chained personnel file produced before the agent's first
day on the job.

## What it does

ClearPoint Onboarding Agent inspects a candidate AI agent (an ADK / Gemini Enterprise / MCP /
registry-style manifest) and generates the workforce-management package required **before** the
agent is permitted to operate in production:

- **Agent Passport** — identity, owner, trust tier (the **ID badge**)
- **Policy Envelope** — authorized scope of action with caps and conditions (the **job description**)
- **AI Bill of Materials** — declared models, tools, dependencies, and provenance (the **résumé**)
- **Passport Readiness Score** — Day-1 readiness with explicit blockers and conditions
- **Onboarding Validation Suite** — pre-employment screening across five fail-closed checks
  (OV-001..005)
- **Approval Card** — the human-in-the-loop hiring decision
- **Evidence Bundle** — hash-chained, audit-ready (the **personnel file**)

It ends in a clear decision — **Ready**, **Ready with Conditions**, or **Blocked Pending
Remediation** — with traceable evidence for security, compliance, finance, and the business
owner.

## How we built it

A net-new multi-agent workflow orchestrated with Google's **Agent Development Kit (ADK)** — a
root `LlmAgent` plus six purpose-built subagents (discovery, grounded policy, artifact,
validation, evidence, explanation) reasoning with **Gemini 3.5 Flash on Vertex AI** (`global`
region). Tools are exposed through a real HTTP **Model Context Protocol (MCP)** server hardened
to the **NSA MCP security baseline** — authentication, RBAC, message integrity, replay
protection, strict schemas, output filtering, and audit logging. Grounding uses a curated public
corpus (NSA MCP CSI, NIST AI RMF, EU AI Act) served through **Vertex AI Search (Discovery
Engine)** with a local retriever as fallback.

The judge UI is designed via **Google Stitch** and implemented in Next.js + Tailwind with
Material 3 tokens. Three services — web, API, MCP — are containerized and deployed on **Cloud
Run** via **Cloud Build**. Runs are persisted in **Firestore** so they survive scale-to-zero.
Onboarding emits **Cloud Trace** spans alongside the hash-chained evidence log. The agent is
discoverable to other enterprise agents through the **Agent-to-Agent (A2A) protocol** at
`/.well-known/agent.json`, with task submission at `/a2a/v1/message:send`.

A foundational design rule: **the onboarding decision is computed deterministically.** Score, caps,
blockers, and final disposition come from plain Python over Pydantic v2 schemas. Gemini contributes
summaries, rationale, and explanations only. The gate is reliable and reproducible by construction
— exactly what an auditor expects from a workforce-management control.

## Challenges we ran into

Keeping scope honest. Building an authentic, production-shaped agent onboarding workflow without
pretending to ship an entire AI Workforce Management platform took disciplined narrowing. We
chose one phase — the onboarding gate — and made it real: 19 security tests over the MCP
baseline, eight production-shaped fixtures, deterministic decisioning, tamper-evident evidence,
custom domain, observability, A2A interoperability, and live Gemini narration. The second
challenge was making grounded retrieval *authentically* valuable rather than set-dressing; we
curated public regulatory and security guidance and show side-by-side grounded-vs-ungrounded
outputs that cite specific source sections.

## Accomplishments we're proud of

- A net-new ADK / Gemini agent that **onboards other agents** into the AI workforce — a category
  most organizations haven't yet named.
- **Eight candidate agents on the Pre-Boarding roster** across safe, missing-owner, regulated-data,
  budget, prompt-injection, privileged-admin, unmaintained-MCP, and grounding-dependent scenarios —
  **5/5 must-ship decisions correct, 8/8 overall**, fully reproducible offline.
- Automated Passport, AI BOM, Policy Envelope, and Evidence Bundle generation with **deterministic
  scoring** and a **SHA-256 hash chain over canonical JSON** — every event is tamper-evident.
- **Onboarding Validation Suite — five fail-closed pre-employment screening checks** (OV-001..005)
  spanning identity, governance, regulated data, security posture, and supply chain.
- **Six purpose-built ADK subagents** (discovery, grounded policy, artifact, validation, evidence,
  explanation) under a root `LlmAgent` — at or above the multi-agent depth of prior ADK-hackathon
  winners.
- **NSA MCP security baseline** implemented and **tested** — 19 security tests pass across auth,
  RBAC, message integrity, replay protection, output filtering, and audit logging.
- **Sub-second deterministic decision** on every fixture; live Gemini narration on demand.
- Live on a **custom domain** at [cpoa.clearpointlogic.com](https://cpoa.clearpointlogic.com),
  judge-gated, with PDF / Markdown / JSON evidence export and real Cloud Trace spans.
- **A2A-discoverable** — peer enterprise agents can call onboarding as a skill.

## What we learned

The next wave of agent platforms needs **workforce-management agents**, not just task agents. The
most powerful framing is HR, not security — every stakeholder already understands a passport, a
job description, a résumé, and a personnel file. Grounded retrieval over public regulatory text
is where multi-agent value becomes visible: the grounded policy agent cites specific source
sections a single ungrounded prompt does not. And deterministic decisioning with Gemini-narrated
rationale is the right division of labor for any control surface that must be reliable and
explainable.

## What's next

The onboarding gate is the start, not the end. ClearPoint Logic's differentiated thesis is
**continuous attestation**: after onboarding, governed agents continuously validate the
workforce-management layer itself, producing signed evidence routed through the same trust graph
used to govern them. Post-challenge this becomes a Google-first, vendor-neutral Meridian
connector for Gemini Enterprise and the Google Cloud Marketplace.

## Technologies used

**Agent Development Kit (ADK)** · **Gemini 3.5 Flash on Vertex AI** · **Model Context Protocol
(MCP)** · **Vertex AI Search (Discovery Engine)** · **Google Stitch** · **Cloud Run** · **Cloud
Build** · **Firestore** · **Cloud Trace** · **Agent-to-Agent (A2A) protocol** · Next.js +
Tailwind · FastAPI · Pydantic v2.

## Honest scope (stated in the README, UI footer, and every evidence bundle)

Net-new Track 1 agent inspired by the ClearPoint Meridian architecture — not a claim that
Meridian is live. Implements the onboarding gate only; continuous attestation is roadmap.
Synthetic fixtures; `demo_stub` signatures (not production attestation); Passport Readiness Score
is demonstration-grade and not the proprietary production scoring system. "Onboarding
recommendation," not certified compliance.

## Testing instructions

Public code repository linked in the submission. Hosted judge UI at
[cpoa.clearpointlogic.com](https://cpoa.clearpointlogic.com), gated by HTTP basic auth
(credentials in `JUDGE_RUNBOOK.md` and on the submission form). Open the **Pre-Boarding** roster
and run any fixture end-to-end — no CLI required. Evidence bundles export as JSON, Markdown, and PDF.
