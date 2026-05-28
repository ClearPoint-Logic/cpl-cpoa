# Architecture — ClearPoint Onboarding Agent

AI Workforce Management — the first six phases of the lifecycle shipped end-to-end on Google's
agent platform. The onboarding decision is **deterministic** (score, caps, blockers, final
disposition); **Gemini 3.5 Flash on Vertex AI** contributes summaries, rationale, and
explanations only. Every phase writes into the same hash-chained personnel file.

## The full lifecycle

```
[Web UI (Next.js on Cloud Run, Material 3 tokens)] — single hostname, basic-auth gated
        │
        ▼
[API gateway — FastAPI on Cloud Run, A2A surface at /.well-known/agent.json (open)]
        │
        ├──► Discover  (agent_discovery)        — real HTTPS scan of A2A Agent Cards
        ├──► Onboard   (engine + ADK subagents) — six-stage gate; deterministic decision
        ├──► Manage    (manage)                  — HR Console actions; chain-linked events
        ├──► Govern    (govern)                  — Compass live control matrix vs. corpus
        ├──► Operate   (operate)                 — Sentinel fleet health + anomaly rules
        └──► Optimize  (optimize)                — Talent Dev development plans

                                ┌─────────────────────────────────┐
        Common signals          │  Firestore run store            │
        chained into            │  SHA-256 hash-chained events    │
        one personnel           │  Cloud Trace spans              │
        file per agent          │  Vertex AI Search grounding     │
                                │  MCP server (NSA baseline)      │
                                └─────────────────────────────────┘
```

## Components (as built)

| Component | Path | Notes |
|---|---|---|
| Data contracts (§11) | `cpoa/schemas/` | Strict Pydantic v2 (`extra="forbid"`) |
| Deterministic gate | `cpoa/services/{hashing,scoring,decisioning}.py` | Hash chain §11.8, score §11.6, decision §14 |
| Onboarding engine | `cpoa/services/engine.py` | Fail-closed; emits chain-linked evidence |
| Discover phase | `cpoa/services/agent_discovery.py` | Real httpx scan; classify against governed registry |
| Manage phase | `cpoa/services/manage.py` | HR Console lifecycle actions; chain-linked events |
| Govern phase | `cpoa/services/govern.py` | Compass control matrix; live citations vs. corpus |
| Operate phase | `cpoa/services/operate.py` | Sentinel anomaly rules over real onboarding + Manage signals |
| Optimize phase | `cpoa/services/optimize.py` | Talent Dev plans; autonomy ladder as promotion track |
| Grounding / RAG | `cpoa/services/grounding.py` + `corpus/` | Vertex AI Search via env; local fallback |
| ADK agents | `agents/` | Root orchestrator + 6 subagents; Gemini 3.5 Flash via Vertex AI |
| Secure MCP server | `mcp_servers/onboarding_tools/` | 5 tools + NSA MCP security baseline |
| API | `app/api/` | FastAPI; basic auth (UI), open A2A; per-phase endpoints |
| Web UI | `app/web/` | Next.js 14 + Tailwind + Material 3 tokens |
| Persistence | `app/api/store.py` | In-memory (dev) + Firestore (`CPOA_STORAGE_MODE=firestore`) |
| Observability | `cpoa/services/tracing.py` | OpenTelemetry → Cloud Trace |
| Deploy | `infra/cloudrun/` | Cloud Build + Cloud Run (web, API, MCP) |

## Google platform mapping

| Capability | Google product | Fallback |
|---|---|---|
| Reasoning | **Gemini 3.5 Flash on Vertex AI** (region: `global`) | — (rules: AI Studio not eligible for credits) |
| Multi-agent orchestration | **Agent Development Kit (ADK)** — root `LlmAgent` + 6 subagents | deterministic engine (offline) |
| Tool surface | **Model Context Protocol (MCP)** — HTTP server, NSA security baseline | stdio MCP (dev) |
| Grounding / RAG | **Vertex AI Search** (Discovery Engine) — env-driven via `CPOA_GROUNDING_MODE` | local-corpus retriever |
| Interoperability | **Agent-to-Agent (A2A)** protocol — open Agent Card at `/.well-known/agent.json` | — |
| Persistence | **Firestore** — durable across scale-to-zero | in-memory run store (dev) |
| Web / API / MCP runtime | **Cloud Run** — deployed via **Cloud Build** | — |
| Design system | **Google Stitch** → Next.js + Tailwind + Material 3 tokens | hand-built Tailwind |
| Observability | **Cloud Trace** spans + hash-chained evidence | structured local logs |

## Multi-agent value

A single ungrounded model call gives a generic answer. The grounded multi-agent path retrieves
specific public guidance (NSA MCP CSI, NIST AI RMF, EU AI Act) and attaches `grounding_refs` to
the policy envelope and findings — demonstrated side-by-side via `/api/grounding-comparison`
and the `grounding_required_policy_agent` fixture. The Compass page (`/govern`) renders the
**reverse mapping** — every CPOA control to specific corpus passages — resolved live so a
corpus update flows into the matrix on next request.

## Integrity claim — defensible by construction

Every evidence event includes a `previous_event_hash` linkage; the `bundle_hash` is computed
over the canonical-JSON serialization of the final bundle. A parameterized test
(`tests/unit/test_bundle_hash_recompute.py`) runs `compute_bundle_hash(bundle) == bundle.bundle_hash`
against every fixture in CI. The `approval_card.evidence_bundle_id` must equal the bundle's
`bundle_id`. If either invariant breaks, CI fails.
