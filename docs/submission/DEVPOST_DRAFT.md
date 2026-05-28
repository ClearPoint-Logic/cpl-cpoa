# Devpost Submission — ClearPoint Workforce Agent

**Track:** Track 1 — Build (Net-New Agents)
**Tagline:** AI Workforce Management — the first six phases of the lifecycle shipped end-to-end on Google's agent platform (ADK, Gemini on Vertex AI, MCP, Vertex AI Search, A2A, Firestore, Cloud Trace, Cloud Run). Discover, Onboard, Manage, Govern, Operate, Optimize — every layer running on real signals from one hash-chained personnel file.

## Inspiration

AI agents are joining the enterprise workforce, and most organizations have **no repeatable
process to hire them, manage them, audit them, monitor them, or grow them.** Humans get an
identity, a job description, declared qualifications, a hiring manager, a personnel file, a
performance-management process, and a career path. Agents deserve the same discipline.

We treat agents as workforce — not tooling — and ship the **first six phases of AI Workforce
Management** end-to-end: **Discover** the unmanaged agents already running in your environment,
**Onboard** them through a deterministic gate, **Manage** their day-to-day with HR actions that
land hash-chained evidence, **Govern** them against the public regulatory frameworks, **Operate**
them with continuous performance monitoring, and **Optimize** them along an explicit autonomy
ladder.

### How this sits with Google's Gemini Enterprise Agent Platform

Google's Gemini Enterprise Agent Platform (April 2026) ships **Agent Registry**, **Agent
Identity**, **Agent Gateway**, dynamic **AI Bill of Materials**, and **Agent Anomaly Detection**
as platform primitives. CWA is **not** a competing platform — it is the workforce/HR
**application layer** that consumes those primitives. The platform gives you the registry; **CWA
is the HR department that decides who gets hired into it** — and the management surface that
operates the workforce afterwards. The terms *Agent Passport*, *AIBOM*, and *Evidence Bundle* are
now widely used (Cubitrek v0.1, ERC-8004, the open `agent-passport-system` library); what makes
CWA distinct is the **workforce framing applied to the whole lifecycle**, with deterministic
ceremony and a single continuous personnel file.

## What it does

CWA inspects candidate AI agents (ADK / Gemini Enterprise / MCP / registry-style manifests),
shepherds them through onboarding, then manages, governs, monitors, and grows them:

**Onboard — the gate that produces the personnel file**
- **Agent Passport** — identity, owner, trust tier (the **ID badge**)
- **Policy Envelope** — authorized scope of action with caps and conditions (the **job description**)
- **AI Bill of Materials** — declared models, tools, dependencies, and provenance (the **résumé**)
- **Passport Readiness Score** — Day-1 readiness with explicit blockers and conditions
- **Onboarding Validation Suite** — pre-employment screening across five fail-closed checks (OV-001..005)
- **Approval Card** — the human-in-the-loop hiring decision
- **Evidence Bundle** — hash-chained, audit-ready (the **personnel file**)

Decision: **Ready**, **Ready with Conditions**, or **Blocked Pending Remediation**, with
deterministic reasoning and Gemini-authored narrative.

**Discover, Manage, Govern, Operate, Optimize — the rest of the lifecycle**
- **Discover** — real HTTPS scan of A2A Agent Cards across the environment, classified against
  the governed registry. Shadow-IT agents surface as findings with a one-click "Send to
  Pre-Boarding."
- **Manage (HR Console)** — Place on Leave, Return, Manager Handoff, Role Change. Every action
  writes a real hash-chained evidence event into the agent's personnel file.
- **Govern (Compass)** — Live control matrix: every CWA control mapped to specific NSA MCP CSI /
  NIST AI RMF / EU AI Act passages, resolved live against the grounding corpus.
- **Operate (Sentinel)** — Fleet health with deterministic anomaly rules
  (BLOCKER-AT-INTAKE, STALE-LEAVE, HIGH-AUTONOMY-HIGH-RISK, MULTI-CONDITION-AGENT). Anomalies
  write into the same hash chain.
- **Optimize (Talent Development)** — Per-agent development plans. Open conditions become
  career-development items; the autonomy ladder (L0 → L5) is the promotion track.

## How we built it

A net-new multi-agent workflow orchestrated with Google's **Agent Development Kit (ADK)** — a
root `LlmAgent` plus six purpose-built subagents (discovery, grounded policy, artifact,
validation, evidence, explanation) reasoning with **Gemini 3.5 Flash on Vertex AI** (`global`
region). Tools are exposed through a real HTTP **Model Context Protocol (MCP)** server hardened
to the **NSA MCP security baseline** — authentication, RBAC, message integrity, replay
protection, strict schemas, output filtering, and audit logging (verified by 19 security tests).
Grounding is wired to **Vertex AI Search (Discovery Engine)** via the `CPOA_GROUNDING_MODE` env;
the deterministic local-corpus retriever is the offline fallback.

Three services — web, API, MCP — are containerized and deployed on **Cloud Run** via **Cloud
Build**. Runs are persisted in **Firestore** so they survive scale-to-zero. The mode envelope is
surfaced live at `/api/health` so a SecOps reviewer can verify the deployed posture in one curl.
Onboarding emits **Cloud Trace** spans alongside the SHA-256 hash-chained evidence log. The
agent is discoverable to other enterprise agents through the **Agent-to-Agent (A2A) protocol**
at the open URL `/.well-known/agent.json`. Tasks are accepted at `/a2a/v1/message:send`.

A foundational design rule: **the onboarding decision is computed deterministically.** Score,
caps, blockers, and final disposition come from plain Python over Pydantic v2 schemas. Gemini
contributes summaries, rationale, and explanations only. Every fixture's bundle hash is
recomputed in CI, so the personnel-file integrity claim is mechanically defensible.

## Challenges we ran into

Keeping the workforce metaphor honest at every layer. It was tempting to ship Discover/Manage as
mocked dashboards; instead the Discover scanner makes real HTTP calls (against a representative
A2A directory hosted alongside the API), and every Manage action lands a real evidence event in
the same hash chain as the onboarding bundle. The same applies to Operate: anomalies are
deterministic rules over **real signals** (the agent's onboarding outcome and live HR Console
event log), not synthesized metrics.

The second challenge was the integrity-claim posture itself. A prior version of the gate mutated
the approval card *after* the bundle was hashed, breaking recompute on every fixture. The fix
landed before submission: the bundle id is stamped onto the approval card before hashing, and a
parameterized test now runs `compute_bundle_hash(bundle) == bundle.bundle_hash` against all
eight fixtures in CI.

## By the numbers (all measured from the deployed build)

| Metric | Value |
|---|---|
| Deterministic decision latency per onboarding run | **< 5 ms** (sub-second incl. live Gemini narration) |
| Pre-Boarding fixtures deciding correctly | **8 / 8** across 8 production-shaped risk archetypes |
| Fail-closed pre-employment-screening checks | **5** (OV-001..005 covering identity, data, security, budget, supply chain) |
| Live regulatory-citation resolutions in Compass | **29** across **3** frameworks (NSA MCP CSI · NIST AI RMF · EU AI Act) |
| NSA MCP security baseline tests passing | **19 / 19** |
| Total tests (unit, integration, evals, security) | **186** |
| Code coverage | **90 %** |
| AI Workforce Management lifecycle phases shipped | **6 / 7** |
| Production security headers set | **7** |
| Evidence signatures | real **HMAC-SHA256** (`local_hmac` mode); Cloud KMS-ready behind `CPOA_SIGNING_MODE=kms` |

### Enterprise-pilot scenario (illustrative)

For a 200-agent fleet through the gate over a typical month:
- **~800 audit events** (200 onboarding runs + ~600 HR Console lifecycle actions)
- **~3 MB of canonical-JSON evidence**, ~24 KB of hash-chain metadata
- **~3 minutes** reviewer time per agent (intake → Background Check → Approval Card) vs. ~3 days for ad-hoc spreadsheet review
- **Every approved control linked to a specific regulatory passage** at decision time, not retroactively
- **Zero supply-chain blind spots** — Discover crawls the A2A directory continuously, so shadow IT surfaces before, not after, an incident

## Accomplishments we're proud of

- **The full lifecycle, end-to-end, in one repo.** Six of seven AI Workforce Management phases
  shipped — Discover, Onboard, Manage, Govern, Operate, Optimize — each running on real signals,
  each writing into the same hash-chained personnel file.
- **186 tests pass; 90% coverage; bundle hash recomputes on every fixture in CI** — the audit-integrity claim
  is mechanically defensible, not just narrated.
- **Eight candidate agents on the Pre-Boarding roster** across safe, missing-owner,
  regulated-data, budget, prompt-injection, privileged-admin, unmaintained-MCP, and
  grounding-dependent scenarios — **5/5 must-ship decisions correct, 8/8 overall**, fully
  reproducible offline.
- **NSA MCP security baseline** implemented and **tested** — 19 security tests pass across auth,
  RBAC, message integrity, replay protection, output filtering, and audit logging.
- **Sub-second deterministic decision** on every fixture; live Gemini narration on demand.
- **Live on a custom domain** at [cwa.clearpointlogic.com](https://cwa.clearpointlogic.com),
  judge-gated, with production security headers (HSTS, CSP, X-Frame-Options, Permissions-Policy),
  PDF / Markdown / JSON evidence export, and real Cloud Trace spans.
- **A2A-discoverable** at the open URL — peer enterprise agents can call onboarding as a skill.

## What we learned

The next wave of agent platforms needs **workforce-management agents**, not just task agents.
The most powerful framing is HR, not security — every stakeholder already understands a passport,
a job description, a résumé, a personnel file, an HR Console, a compliance officer, a
performance-management cycle, and a career path. Grounded retrieval over public regulatory text
is where multi-agent value becomes visible: the grounded policy agent cites specific source
sections a single ungrounded prompt does not. And deterministic decisioning with Gemini-narrated
rationale is the right division of labor for any control surface that must be reliable and
explainable at the same time.

## What's next

Continuous attestation — the seventh phase. After onboarding, governed agents continuously
validate the workforce-management layer itself, producing signed evidence routed through the
same trust graph used to govern them. Post-challenge this becomes a Google-first, vendor-neutral
connector for Gemini Enterprise and the Google Cloud Marketplace.

## Technologies used

**Agent Development Kit (ADK)** · **Gemini 3.5 Flash on Vertex AI** · **Model Context Protocol
(MCP)** · **Vertex AI Search (Discovery Engine)** · **Google Stitch** · **Cloud Run** · **Cloud
Build** · **Firestore** · **Cloud Trace** · **Agent-to-Agent (A2A) protocol** · Next.js +
Tailwind (Material 3) · FastAPI · Pydantic v2.

## Honest scope

CWA is newly created during the contest period and meets the contest's net-new requirement.
What stays caveat-worthy in any production:

- **Synthetic candidate fixtures.** We don't have customer agents on the Pre-Boarding roster yet.
- **A representative A2A directory** is hosted alongside the API so the Discover scan exercises
  real network paths. In a customer deployment the scanner points at enterprise inventory APIs
  (Agent Engine catalog, Cloud Run service inventory, A2A directory services) — same code.
- **Continuous attestation across every running interaction** is the next layer; six of the
  seven AI Workforce Management phases ship here.

The Passport Readiness Score is a deterministic, reproducible, audit-grade measure. The
hash-chained evidence is tamper-evident with a recompute test that runs against every fixture in
CI. The MCP server passes the NSA-baseline security tests.

## Testing instructions

Public code repository linked in the submission. Hosted judge UI at
[cwa.clearpointlogic.com](https://cwa.clearpointlogic.com), gated by HTTP basic auth
(credentials provided privately in this submission's testing-instructions field). Open the
**Workforce** tab to see the lifecycle census, then **Pre-Boarding** to run any fixture
end-to-end — no CLI required. Evidence bundles export as JSON, Markdown, and PDF.
