# Devpost Submission Draft — ClearPoint Onboarding Agent

**Track:** Track 1 — Build (Net-New Agents)
**Tagline:** A net-new ADK + Gemini multi-agent system that helps enterprises *hire* AI agents into the workforce — with a passport, a job description, a résumé, and a personnel file at the gate.

## Inspiration
AI agents are joining the enterprise workforce, and most organizations have no repeatable process
to hire them. Humans get an identity, a job description, declared qualifications, a manager, and a
personnel file before they do sensitive work. Agents deserve the same discipline. We treat agents as
workforce, not tooling — and give every new agent the same structured intake a human gets on day one.

## What it does
ClearPoint Onboarding Agent inspects a candidate AI agent (an ADK / Gemini Enterprise / MCP /
registry-style manifest) and generates the workforce-management package required before production
use: an **Agent Passport** (ID badge), **Policy Envelope** (job description & scope of authority),
**AI Bill of Materials** (résumé of declared models/tools/deps), a **Passport Readiness Score**,
**Onboarding Validation Suite** findings, an **approval card**, and an audit-ready **Evidence Bundle**
(the personnel file). It ends in a clear decision — **Ready**, **Ready with Conditions**, or **Blocked
Pending Remediation** — with traceable, hash-chained evidence for security, compliance, finance, and
business owners.

## How we built it
A net-new **ADK** multi-agent workflow (root orchestrator + six subagents: discovery, grounded policy,
artifact, validation, evidence, explanation) reasoning with **Gemini via Vertex AI**. Tools are exposed
through a real **HTTP MCP server** hardened to an NSA-inspired security baseline (auth, RBAC, message
integrity, replay protection, strict schemas, output filtering, audit logging). Grounding uses a curated
public corpus (NSA MCP CSI, NIST AI RMF, EU AI Act) with **Vertex AI Search** and a local retriever
fallback. The judge UI is designed via **Google Stitch** and implemented in **Next.js + Tailwind**,
deployed on **Cloud Run** alongside the API and MCP server. A key design rule: the onboarding **decision
is computed deterministically** (score, caps, blockers); Gemini contributes summaries, rationale, and
explanations — so the gate is reliable and reproducible.

## Challenges we ran into
Keeping scope honest: building a real, demoable agent-onboarding workflow without pretending to ship an
entire AI Workforce Management platform. We narrowed to one production-shaped workflow — the onboarding
gate — with synthetic fixtures and explicit limitations throughout. The second challenge was making
grounded retrieval *authentically* valuable rather than set-dressing; we curated public regulatory and
security guidance and show side-by-side grounded-vs-ungrounded outputs that cite specific sources.

## Accomplishments we're proud of
- Net-new ADK/Gemini agent that onboards *other* agents into the AI workforce.
- Eight fixture agents across safe, missing-owner, regulated-data, budget, prompt-injection,
  privileged-admin, unmaintained-MCP, and grounding-dependent scenarios — **5/5 must-ship decisions
  correct, 8/8 overall**, fully reproducible offline.
- Automated Passport, AI BOM, Policy Envelope, and Evidence Bundle generation with deterministic
  scoring and a tamper-evident hash chain.
- NSA MCP Security Design Baseline implemented and **tested** (19 security tests).
- Fail-closed Onboarding Validation Suite; vendor-neutral data model; Google-aligned UI.

## What we learned
The next wave of agent platforms needs workforce-management agents, not just task agents. The most
powerful framing is HR, not security — every stakeholder already understands a passport, a job
description, a résumé, and a personnel file. And grounded retrieval over public regulatory text is where
multi-agent value becomes visible: the grounded policy agent cites specific source sections a single
ungrounded prompt does not.

## What's next
The onboarding gate is the start, not the end. ClearPoint Logic's differentiated thesis is *continuous
attestation*: after onboarding, governed agents continuously validate the workforce-management layer
itself, producing signed evidence routed through the same trust graph used to govern them. Post-challenge
this becomes a Google-first, vendor-neutral Meridian connector for Gemini Enterprise and the Cloud
Marketplace.

## Technologies used
Google ADK · Gemini (Vertex AI) · Model Context Protocol · Vertex AI Search · Google Stitch ·
Cloud Run · Cloud Build · Next.js + Tailwind · FastAPI · Pydantic.

## Honest scope (stated in the README, UI footer, and every evidence bundle)
Net-new Track 1 agent inspired by the ClearPoint Meridian architecture — not a claim that Meridian is
live. Implements the onboarding gate only; continuous attestation is roadmap. Synthetic fixtures;
demo-stub signatures (not production attestation); demo-only readiness score (not production CAS/ECS).
"Onboarding recommendation," not certified compliance.

## Testing instructions
Public code repository: _(URL in submission)_. Hosted judge UI: _(Cloud Run URL — see
`JUDGE_RUNBOOK.md`)_, gated by HTTP basic auth (credentials in the runbook / submission). Open the Test
Agent Zoo and run any fixture end to end — no CLI required.
