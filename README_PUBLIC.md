# ClearPoint Workforce Agent — public submission README

> This is the sanitized, public-facing README used on the `public-safe-export` branch for challenge
> judging. It contains no ClearPoint Logic proprietary material. For the full canonical README see
> `README.md` on the working branch.

**A net-new ADK + Gemini multi-agent system that helps enterprises hire AI agents into the workforce —
with a passport, a job description, a résumé, and a personnel file at the gate.**

> **Google for Startups AI Agents Challenge — Track 1: Build (Net-New Agents)**

ClearPoint Workforce Agent inspects a candidate AI agent and issues the workforce-management package
an enterprise needs before letting that agent operate: an **Agent Passport** (ID badge), a **Policy
Envelope** (job description), an **AI Bill of Materials** (résumé), a readiness score, Onboarding
Validation Suite findings, an approval card, and an audit-ready **Evidence Bundle** (personnel file) —
ending in a clear decision: **Ready**, **Ready with Conditions**, or **Blocked Pending Remediation**.

**Built with:** ADK (orchestration) · Gemini via Vertex AI (reasoning) · Google Stitch (UI design) ·
Model Context Protocol (secure tools) · Agent Engine / Cloud Run (runtime) · Vertex AI Search / RAG
(grounding) · Cloud Logging & Trace.

**Honest scope:** A net-new Track 1 agent inspired by the ClearPoint Meridian architecture (not a
claim that Meridian is live). Implements the onboarding gate only; continuous attestation is the
roadmap. Artifacts are demo-safe (synthetic fixtures, demo-stub signatures, demo-only readiness score).

See `docs/submission/JUDGE_RUNBOOK.md` for testing access and the demo script.
