# Architecture — ClearPoint Onboarding Agent

Net-new Track 1 agent on the Google stack. The onboarding **decision is deterministic**
(score, caps, blockers, final decision); **Gemini** contributes summaries, rationale, and
explanations only (canonical rule §11.6 / §27.3 #12).

## High-level flow

```
[Judge / Web UI — Stitch-sourced Next.js + Tailwind on Cloud Run]
        |  (HTTP basic auth gates the whole site)
        v
[API gateway — FastAPI on Cloud Run]
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
[Artifact store + hash-chained evidence log]  →  [Cloud Logging / Trace]
```

## Components (as built)

| Component | Path | Notes |
|---|---|---|
| Data contracts (§11) | `cpoa/schemas/` | Strict Pydantic v2; v0.1 of Meridian external schemas |
| Deterministic gate | `cpoa/services/{hashing,scoring,decisioning}.py` | Hash chain §11.8, score §11.6, decision §14 |
| Engine stages | `cpoa/services/{discovery,policy,validation_suite,artifacts,evidence_log,engine}.py` | Fail-closed orchestration §10 |
| Grounding/RAG | `cpoa/services/grounding.py` + `corpus/` | Local retriever + Vertex AI Search seam |
| ADK agents | `agents/` | Root orchestrator + 6 subagents (§9.3); Gemini via Vertex |
| Secure MCP server | `mcp_servers/onboarding_tools/` | 5 tools + NSA baseline (§12.6) |
| API | `app/api/` | FastAPI; basic auth; downloads; grounding comparison |
| Web UI | `app/web/` | Next.js 14 + Tailwind; all §15.2 routes |
| Deploy | `infra/cloudrun/` | Cloud Build + Cloud Run (API, MCP, Web) |

## Google platform mapping (§9.2)

| Need | Surface used | Fallback |
|---|---|---|
| Intelligence | Gemini via Vertex AI | — (rules: AI Studio not eligible for credits) |
| Orchestration | ADK (root LlmAgent + SequentialAgent of 6 subagents) | deterministic engine (offline) |
| Tools | MCP (HTTP server, NSA baseline) | stdio MCP (dev) |
| Grounding/RAG | Vertex AI Search | local corpus retriever |
| Orchestrator runtime | Agent Engine / Agent Runtime (documented primary) | **Cloud Run (running)** — see THREAT_MODEL §Agent Engine |
| UI / API / MCP runtime | Cloud Run | — |
| UI design pipeline | Google Stitch → Next.js + Tailwind | hand-built Tailwind |
| Observability | Cloud Logging / Trace + hash-chained evidence | structured local logs |

## Multi-agent value
A single ungrounded model call gives a generic answer. The grounded multi-agent path retrieves
specific public guidance (NSA MCP CSI, NIST AI RMF, EU AI Act) and attaches `grounding_refs` to the
policy envelope and findings — demonstrated side-by-side via `/api/grounding-comparison` and the
`grounding_required_policy_agent` fixture (FR-084).
