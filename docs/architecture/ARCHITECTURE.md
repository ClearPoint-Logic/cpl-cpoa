# Architecture — ClearPoint Onboarding Agent

The AI Workforce Management onboarding gate, built net-new on Google's agent platform. The
onboarding **decision is deterministic** (score, caps, blockers, final disposition); **Gemini 3.5
Flash on Vertex AI** contributes summaries, rationale, and explanations only (canonical rule §11.6
/ §27.3 #12).

## High-level flow

```
[Judge / Web UI — Stitch-sourced Next.js + Tailwind on Cloud Run]
        |  (HTTP basic auth gates the whole site)
        v
[API gateway — FastAPI on Cloud Run; A2A surface at /.well-known/agent.json]
        |
        v
[Onboarding orchestrator — ADK root LlmAgent + 6 subagents]
   discovery → grounded policy → artifact → validation → evidence → explanation
        |                         |
        |  (grounding/RAG)        |  (tools)
        v                         v
[Vertex AI Search / local corpus] [Secure MCP server on Cloud Run]
                                   inspect · policy · validation · artifacts · evidence
        |
        v
[Firestore run store] + [SHA-256 hash-chained evidence log] → [Cloud Trace]
```

## Components (as built)

| Component | Path | Notes |
|---|---|---|
| Data contracts (§11) | `cpoa/schemas/` | Strict Pydantic v2 (`extra="forbid"`); v0.1 of Meridian external schemas |
| Deterministic gate | `cpoa/services/{hashing,scoring,decisioning}.py` | Hash chain §11.8, score §11.6, decision §14 |
| Engine stages | `cpoa/services/{discovery,policy,validation_suite,artifacts,evidence_log,engine}.py` | Fail-closed orchestration §10 |
| Grounding / RAG | `cpoa/services/grounding.py` + `corpus/` | Local retriever + Vertex AI Search seam |
| ADK agents | `agents/` | Root orchestrator + 6 subagents (§9.3); Gemini 3.5 Flash via Vertex AI |
| Secure MCP server | `mcp_servers/onboarding_tools/` | 5 tools + NSA MCP security baseline (§12.6) |
| API | `app/api/` | FastAPI; basic auth; A2A; downloads; grounding comparison |
| Web UI | `app/web/` | Next.js 14 + Tailwind + Material 3 tokens; all §15.2 routes |
| Persistence | `app/api/store.py` | In-memory (dev) + Firestore (`CPOA_STORAGE_MODE=firestore`) |
| Observability | `cpoa/services/tracing.py` | OpenTelemetry → Cloud Trace |
| Deploy | `infra/cloudrun/` | Cloud Build + Cloud Run (Web, API, MCP) |

## Google platform mapping (§9.2)

| Capability | Google product | Fallback |
|---|---|---|
| Reasoning | **Gemini 3.5 Flash on Vertex AI** (region: `global`) | — (rules: AI Studio not eligible for credits) |
| Multi-agent orchestration | **Agent Development Kit (ADK)** — root LlmAgent + SequentialAgent of 6 subagents | deterministic engine (offline) |
| Tool surface | **Model Context Protocol (MCP)** — HTTP server, NSA security baseline | stdio MCP (dev) |
| Grounding / RAG | **Vertex AI Search** (Discovery Engine) | local-corpus retriever |
| Interoperability | **Agent-to-Agent (A2A)** protocol — Agent Card at `/.well-known/agent.json` | — |
| Persistence | **Firestore** — durable runs across scale-to-zero | in-memory run store (dev) |
| Orchestrator runtime | **Agent Engine / Agent Runtime** (documented primary) | **Cloud Run (running)** — see THREAT_MODEL §Agent Engine |
| Web / API / MCP runtime | **Cloud Run** — deployed via **Cloud Build** | — |
| Design system | **Google Stitch** → Next.js + Tailwind with Material 3 tokens | hand-built Tailwind |
| Observability | **Cloud Trace** spans + hash-chained evidence | structured local logs |

## Multi-agent value

A single ungrounded model call gives a generic answer. The grounded multi-agent path retrieves
specific public guidance (NSA MCP CSI, NIST AI RMF, EU AI Act) and attaches `grounding_refs` to
the policy envelope and findings — demonstrated side-by-side via `/api/grounding-comparison` and
the `grounding_required_policy_agent` fixture (FR-084).
