# ClearPoint Logic — ClearPoint Onboarding Agent Canonical Specification

**Document:** Challenge Canonical — ClearPoint Onboarding Agent  
**Spec ID:** CPOA-GFS-AIAC-2026-CANONICAL  
**Version:** 0.4 final  
**Date:** May 27, 2026  
**Owner:** Jared Mabry, CEO/CTO  
**Status:** Final — implementation begins on confirmation  
**Classification:** Confidential — internal only; challenge/judge access only through approved private repository or explicitly approved submission package  
**Audience:** ClearPoint Logic founders, build agent/coding agent, challenge judges after sanitization, future Meridian/Anchor implementation reviewers  

**Changes from v0.3:**
- **Fixed §21 acceptance-criteria numbering bug** (duplicate 11–14 in v0.3 renumbered to a clean monotonic sequence).
- **Fixed §27.2 source-of-truth reference** (was "v0.2," now correctly identifies v0.4).
- **Closed CPOA-Q009 (builder identity).** Build team is **Jared Mabry (lead) + Claude Code + Codex operating in parallel workstreams.**
- **Closed CPOA-Q012 (judge-access mechanism).** Canonical default is **HTTP basic auth** with credentials issued in `docs/submission/JUDGE_RUNBOOK.md`. Judge GitHub allowlist remains the private-repo access pattern.
- **Adopted Google Stitch as the UI design pipeline** (new CPOA-D024). Stitch generates the source designs and starter code; the team exports to Next.js + Tailwind with CPL brand tokens applied as overrides. Replaces the bespoke Material 3 Expressive + Neural Expressive direction in v0.3 with a faster, more Google-aligned pipeline.
- **Rebuilt §20 implementation plan as three parallel workstreams** (Stream A: logic/schemas/orchestration; Stream B: MCP/security/grounding/deploy; Stream C: UI/Stitch/submission) instead of sequential days. Day exits are still daily but parallel.
- **Made healthcare fixture deterministic** in §6.3: **Ready with Conditions** (definitively; resolves the "or Blocked depending on fixture" ambiguity in v0.3).
- **Expanded grounded corpus content list** in §7.9 / FR-080 with specific public sources (NSA MCP CSI text, NIST AI RMF subset, EU AI Act selected articles) so the grounded-vs-ungrounded demo in FR-084 is authentically demonstrable rather than self-referential.
- Re-aligned §15 UI section around the Stitch pipeline; simplified the M3 Expressive language to "Stitch-generated Google-aligned aesthetic with CPL brand tokens as overrides."

---

## 0. Source basis and authority

This document is the working source of truth for the Google for Startups AI Agents Challenge implementation of the **ClearPoint Onboarding Agent**. It is not a replacement for the ClearPoint Logic Strategy Brief, Meridian canonicals, Anchor canonicals, Agent Core canonicals, or build pack. It is a challenge-specific canonical that translates the existing ClearPoint Logic strategy into a narrow, executable Track 1 agent build.

When this document conflicts with informal chat, brainstorming notes, or non-canonical challenge notes, this document wins for the contest build. When this document conflicts with the current ClearPoint Logic Strategy Brief or build pack, the current ClearPoint Logic canonicals win. Any post-challenge merge into the main ClearPoint Logic canonical system requires the normal amendment process.

Primary source basis:

1. **ClearPoint Logic Strategy Brief v5.2.4** — AI Workforce Platform thesis, AI Workforce Management category, Meridian lifecycle, Anchor trust fabric, Agent Passport, AI BOM, policy envelope, evidence, Google First / not Google-only strategy, continuous attestation thesis (§6.4.7).
2. **ClearPoint Logic Executive Overview v5.2.4** — current implementation state: specs locked, Phase 0 and Phase 1 live, Phase 2 build-gated, no implementation code started for the main platform.
3. **CPM-MERIDIAN-CANONICAL** — six-phase workforce lifecycle, Govern surface, ECS taxonomy, CAS display, Compass orchestration.
4. **CPL-WORKFORCE-PARALLEL-CANONICAL** — human-employee management parallel and HR-to-AI mapping.
5. **CPL-CONNECTOR-CAPABILITY-MATRIX-CANONICAL** — enforcement confidence taxonomy used as the upstream contract for Passport ECS labeling.
6. **CPL-AUDIT-EVIDENCE-CANONICAL** — hash-chained signed audit event pattern that the demo evidence chain mirrors at v0.1.
7. **Google for Startups AI Agents Challenge Kickoff** — challenge framing, Track 1 / Track 2 / Track 3 structure, Google Agent Platform lifecycle, ADK, Agent Studio, Agent Garden, Agent Runtime, Agent Registry, Agent Identity, Agent Gateway, Agent Evaluation, Agent Observability, Agent Simulation, and Agent Optimizer surfaces.
8. **CPL Brand Guidelines v1.0** — review UI and presentation styling guidance.
9. **Google for Startups AI Agents Challenge Complete Resource Guide 2026** — Track 1 ADK/MCP framing, Agent Platform deployment guidance, grounding/RAG emphasis, and project-submission requirements.
10. **NSA CSI: Model Context Protocol (MCP): Security Design Considerations for AI-Driven Automation, May 2026** — MCP threat model and security-control baseline; also used as part of the grounded corpus in §7.9.
11. **Joint CSI: Careful Adoption of Agentic AI Services, April 2026** — secure design, development, deployment, operation, governance, human oversight, monitoring, and accountability principles for agentic AI.
12. **Google Stitch design and code-generation pipeline** — primary UI design source and starter-code generator for the judge-facing review interface.

---

## 1. Executive summary

The **ClearPoint Onboarding Agent** is a net-new Google ADK / Gemini multi-agent system built for the Google for Startups AI Agents Challenge under **Track 1 — Build**. It ships with a judge-facing Web UI designed in **Google Stitch**, a secure MCP server, grounded policy/evidence retrieval, synthetic test agents, and a Google Cloud deployment path centered on Agent Engine / Agent Runtime plus Cloud Run.

The agent demonstrates one production-shaped ClearPoint Meridian workflow: safely onboarding an AI agent into an enterprise AI workforce. It accepts a candidate agent manifest or Google Agent Registry-style fixture, analyzes the agent's purpose, owner, runtime, model dependencies, MCP tools, data classes, autonomy level, and budget exposure, then produces the workforce-management artifacts an enterprise would need before allowing that agent to operate.

**The workforce-parallel frame is the product hook.** Enterprises hire humans through a repeatable process: identity verification, job description, declared qualifications, manager assignment, personnel file. Agents need the same. The ClearPoint Onboarding Agent issues each candidate agent a **passport** (ID badge), a **policy envelope** (job description and scope of authority), an **AI BOM** (resume of declared models, tools, and dependencies), and an **evidence bundle** (the personnel file that follows it forward) — before it does any work.

The core demo path:

1. A candidate agent enters as an ungoverned or partially governed agent.
2. ClearPoint Onboarding Agent inspects the candidate through ADK orchestration and MCP tools.
3. The agent generates:
   - Agent Passport
   - AI Bill of Materials
   - Policy Envelope
   - Passport Readiness Score
   - Onboarding Validation Suite results
   - Human approval card
   - Audit-style evidence bundle
4. The system issues a clear onboarding decision: **Ready**, **Ready with Conditions**, or **Blocked Pending Remediation**.

The strategic thesis is two sentences:

> Gemini Enterprise and Google Agent Platform help enterprises build, scale, govern, and optimize agents. ClearPoint Onboarding Agent shows how an enterprise can safely *hire* those agents into the AI workforce — with identity, policy, validation, approval, and audit-ready evidence at the gate.

**Continuous attestation flag.** Onboarding is the gate. The full ClearPoint Logic thesis is *continuous* attestation: after the gate, governed agents continuously validate the governance layer itself, producing signed evidence routed through the same trust graph used to govern them. This challenge artifact implements the onboarding gate only. The Continuous Validation Agent Suite (Sentinel, Forensics, Drift, Red Team, Regulatory Watch) is the post-onboarding layer and is out of scope for the challenge build. The README, video, and Devpost copy reference this so the judging panel sees the differentiated thesis without the build pretending to ship it.

**Schemas as v0.1 of Meridian's external schemas.** The data contracts in §11 (CandidateAgentManifest, AgentPassport, AI BOM, PolicyEnvelope, EvidenceEvent, EvidenceBundle) are designed deliberately as the v0.1 public-facing schemas Meridian will eventually expose to BYOA enrollment and partner integration. They mirror CPM-MERIDIAN-CANONICAL §6 surfaces and CPL-CONNECTOR-CAPABILITY-MATRIX-CANONICAL §3 ECS labels at structure level. Post-challenge merge into the canonical system should be a forward-compatible v0.1 → v0.2 evolution, not a redesign.

This is intentionally a **Track 1 net-new agent**, not a Track 3 refactor of live Meridian. Meridian is not live. The challenge artifact is a narrow, buildable agent that borrows from the Meridian / Anchor architecture without claiming the full product is implemented.

---

## 2. Canonical decisions

| ID | Decision | Canonical ruling |
|---|---|---|
| CPOA-D001 | Challenge track | Submit as **Track 1 — Build Net-New Agents**. Track 3 remains a strategic roadmap story only. |
| CPOA-D002 | Product identity | Build **ClearPoint Onboarding Agent**, a net-new workforce-onboarding agent that issues Agent Passport-style artifacts. The agent is named for what it does (onboarding); the Passport is the primary artifact it produces. |
| CPOA-D003 | Relationship to Meridian | The agent is a **Meridian-inspired challenge demonstrator** of the Onboard phase only, not production Meridian and not a claim that Meridian is live. |
| CPOA-D004 | Repository | Start in a **new private challenge repo**, not the main ClearPoint Logic build-pack repo. Prepare a public-safe branch/export if challenge rules require public code. |
| CPOA-D005 | Primary framework | Use **Google ADK** as the agent framework. Python is preferred for speed unless challenge constraints require otherwise. |
| CPOA-D006 | Primary model | Use Gemini through the challenge-approved Google Cloud route. Do not hardcode an unstable model name; configure via environment variable. |
| CPOA-D007 | Tool protocol | Use MCP for the candidate-intake, policy-generation, validation, and evidence-writing tool surfaces. Tools must expose an actual MCP server interface. HTTP MCP is the deployed target; stdio MCP is local-dev fallback only. |
| CPOA-D008 | Deployment target — services | Cloud Run hosts the Web UI, API gateway, and the secure MCP server. |
| CPOA-D009 | Google governance compatibility | Model compatibility with Agent Registry, Agent Identity, and Agent Gateway. Use real APIs only if available; otherwise use faithful synthetic fixtures and adapter interfaces. |
| CPOA-D010 | Evidence signing | Use SHA-256 hash chaining and a demo signature field. Do not claim full Anchor signing, Sigstore, or production-grade cryptographic attestation unless implemented. |
| CPOA-D011 | Scoring | Implement **Passport Readiness Score**, a challenge-safe demo score. Do not expose proprietary CAS/ECS weighting logic. |
| CPOA-D012 | Validation | Implement the **Onboarding Validation Suite (OVS)**, a five-test validation harness that proves the workforce-onboarding gate fails closed in demo scenarios. Do not borrow Sentinel branding. |
| CPOA-D013 | Data | Use synthetic agent manifests, synthetic policy packs, and synthetic audit events. No customer data, no internal secrets, no private build-pack contents. |
| CPOA-D014 | UI | **Build a Web UI as a must-ship surface.** CLI/API remains required for automation and evals, but judging happens through the polished review UI. |
| CPOA-D015 | Submission framing | Use the wording "net-new ADK/Gemini agent inspired by ClearPoint Meridian architecture," not "Meridian has been refactored" or "Meridian is live." |
| CPOA-D016 | Schemas as v0.1 of Meridian external schemas | All data contracts in §11 are designed as v0.1 of the public schemas Meridian will eventually expose. They mirror CPM-MERIDIAN-CANONICAL §6 surfaces and CPL-CONNECTOR-CAPABILITY-MATRIX-CANONICAL §3 ECS labels. |
| CPOA-D017 | Continuous attestation posture | The challenge build implements the onboarding gate only. README, video, and Devpost "what's next" plant the Continuous Attestation thesis flag; no claim that the suite is built. |
| CPOA-D018 | Design language | Google-aligned Material aesthetic produced through the Stitch pipeline; CPL brand tokens applied as overrides. |
| CPOA-D019 | Primary deployment — orchestrator | The ADK orchestrator deploys to **Agent Engine / Agent Runtime** as the primary path. If Agent Engine access is unavailable, the orchestrator runs on Cloud Run with the same API contract and the blocker is documented in `docs/security/THREAT_MODEL.md` and the judge runbook. |
| CPOA-D020 | Grounding and RAG | Policy, Evidence, and Explanation agents must use a grounded corpus via Agent Search / Vertex AI Search or RAG Engine where available, with a local retrieval fallback. Corpus contents are specified in §7.9 / FR-080. |
| CPOA-D021 | MCP security baseline | The MCP server must implement the NSA MCP Security Design Baseline in §12.6 before final submission. |
| CPOA-D022 | Test Agent Zoo | The repo must include a synthetic test-agent library with **five must-ship fixtures and three stretch fixtures**. UI must allow judges to run at least one Ready, one Conditional, and one Blocked case end-to-end. |
| CPOA-D023 | Submission artifacts | Final package includes code, video, architecture diagram, deployed test access, and login/test credentials (HTTP basic auth, credentials in `JUDGE_RUNBOOK.md`) or judge GitHub allowlist for private repo. |
| CPOA-D024 | UI design pipeline | **Google Stitch** is the primary UI design source. Stitch generates the design surfaces (landing, agent zoo gallery, run timeline, artifact panels, decision panel, architecture page, judge access page) and starter Next.js/React + Tailwind code. The team exports from Stitch, applies CPL brand tokens as overrides, and integrates into the `app/web` workspace. This choice is part of the submission story: ADK + Gemini + Stitch is a three-product Google-stack demonstration. |
| CPOA-D025 | Build team | **Jared Mabry (lead) + Claude Code + Codex operating in three parallel workstreams.** Stream A owns logic/schemas/orchestration. Stream B owns MCP/security/grounding/deployment. Stream C owns UI/Stitch pipeline/submission package. Workstream ownership is canonical in §20. |
| CPOA-D026 | Judge access mechanism | **HTTP basic auth** is the canonical default for the deployed Web UI. Credentials live in `docs/submission/JUDGE_RUNBOOK.md`. Judge GitHub allowlist is the canonical access pattern for the private repo. |

---

## 3. Challenge positioning

### 3.1 Official submission title

**ClearPoint Onboarding Agent for Gemini Enterprise**

### 3.2 Short title

**ClearPoint Onboarding Agent**

### 3.3 Tagline

**A net-new ADK multi-agent system that helps enterprises hire AI agents into the workforce — with a passport, a job description, a resume, and a personnel file at the gate.**

### 3.4 One-paragraph Devpost description

ClearPoint Onboarding Agent is a Gemini / ADK-powered multi-agent workforce-onboarding system that helps enterprises safely hire other AI agents into the AI workforce through a judge-facing Web UI designed in Google Stitch. It inspects a candidate ADK, Gemini Enterprise, MCP, or registry-style agent manifest; identifies owner, purpose, runtime, model dependencies, tools, data access, autonomy level, and budget exposure; then issues an Agent Passport (the agent's ID badge), Policy Envelope (its job description and scope of authority), AI Bill of Materials (its resume of declared dependencies), Passport Readiness Score, Onboarding Validation Suite findings, approval card, and audit-ready evidence bundle (the personnel file that follows it forward). The result is a clear onboarding decision — Ready, Ready with Conditions, or Blocked Pending Remediation — with traceable evidence for security, compliance, finance, and business owners.

### 3.5 Strategic narrative

Enterprises are no longer asking whether they will use agents. They are asking how to put them to work safely.

**The frame is workforce, not tooling.** Every enterprise has a hiring process for humans: identity check, job description, declared qualifications, manager assignment, personnel file. AI agents are joining the workforce — and most organizations have no equivalent process for them.

Every new agent creates the same questions a hiring manager would ask:

- Who owns this agent?
- What is its job?
- What tools can it call?
- What data can it access?
- What model and provider dependencies does it carry?
- What can it spend?
- What requires human approval?
- What evidence proves it behaved correctly?
- When should it be paused or retired?

The ClearPoint Onboarding Agent turns those questions into an autonomous onboarding workflow. Before an agent can act, it receives a passport, policy envelope, AI BOM, validation record, approval status, and evidence bundle — the same structured intake a human gets on day one.

**The onboarding gate is the start, not the end.** ClearPoint Logic's differentiated thesis is *continuous attestation*: after onboarding, governed agents continuously validate the workforce-management layer itself, producing signed evidence routed through the same trust graph used to govern them. This challenge artifact implements the gate. The post-gate continuous attestation layer is the roadmap.

### 3.6 Track 1 fit

The ClearPoint Onboarding Agent qualifies as Track 1 because:

1. It is net-new code for the challenge.
2. It is an agent, not only a dashboard or report generator.
3. It uses ADK and Gemini.
4. It uses tool calls and an MCP server.
5. It autonomously performs multi-step work: intake, discovery, risk classification, artifact generation, validation, approval-card generation, and evidence export.
6. It targets a complex business problem with measurable enterprise value.
7. It does not rely on Meridian being live.

### 3.7 Track 3 relationship

Track 3 remains the roadmap story: a future Meridian workforce-management connector for Google Cloud Marketplace and Gemini Enterprise. The challenge submission should not be framed as Track 3 unless Google explicitly confirms eligibility. The Track 1 submission may include a "future path" section explaining how this agent could evolve into a Gemini Enterprise / Marketplace-ready Meridian connector.

Canonical wording:

> This Track 1 agent is a production-shaped prototype of one Meridian workflow: onboarding and attesting AI agents at the workforce gate. It is not a claim that Meridian is live; it is the first net-new Meridian-shaped workflow built on Google's stack.

---

## 4. Product boundary

### 4.1 What the product is

ClearPoint Onboarding Agent is a challenge-specific autonomous workforce-onboarding agent. It performs a bounded workflow:

1. Accept a candidate agent description.
2. Discover workforce-relevant facts.
3. Identify missing or risky metadata.
4. Generate workforce-management artifacts (Passport, AI BOM, Policy Envelope).
5. Run Onboarding Validation Suite checks.
6. Generate human approval card.
7. Emit evidence events.
8. Export an evidence bundle.
9. Recommend onboarding status.

### 4.2 What the product is not

ClearPoint Onboarding Agent is not:

- Production Meridian.
- A full Anchor implementation.
- A full Agent Core implementation.
- A full Continuous Validation Agent Suite (Sentinel, Forensics, Drift, Red Team, Regulatory Watch).
- A production connector to every vendor registry.
- A claim that CPL has live customer tenants on Meridian.
- A public standard for AI workforce management.
- A replacement for Google Agent Platform, Gemini Enterprise, Agent Registry, Agent Identity, or Agent Gateway.
- A customer data processor.
- A production compliance guarantee.

### 4.3 Product principle

The product must show ClearPoint's differentiated point of view without exposing or overbuilding the core platform.

Show:

- Workforce framing (hire, not deploy).
- HR-to-AI artifact parallel (passport, policy envelope, AI BOM, evidence bundle).
- Agent Passport artifact.
- AI BOM artifact.
- Policy envelope artifact.
- Approval and evidence flow.
- Google-native implementation path (ADK + Gemini + Stitch + Agent Engine + Cloud Run).
- Vendor-neutral data model.
- Continuous attestation thesis flag (as the post-onboarding roadmap, not as a built feature).

Do not show:

- Proprietary CAS/ECS production weights.
- Anchor signing key design.
- Internal build-pack contents.
- Non-public customer data.
- Private strategy details unnecessary for judging.
- Claims that live Meridian functionality exists.
- Claims that the Continuous Validation Agent Suite is implemented.

---

## 5. Personas

### 5.1 Primary persona — AI Workforce Manager

The AI Workforce Manager is responsible for knowing which agents operate across the enterprise, what they are allowed to do, and whether they are safe to run. They need a fast, repeatable way to onboard agents without manually reading code, manifests, docs, tool schemas, and policy documents.

Success for this persona:

- Can submit a candidate agent and get a clear onboarding recommendation.
- Can see missing metadata and risk drivers.
- Can review the proposed policy envelope.
- Can route the agent for approval.

### 5.2 Security / Compliance Officer

The Security or Compliance Officer needs defensible evidence. They care about data classes, tool boundaries, human approval requirements, audit completeness, and whether the agent can be reconstructed during an investigation.

Success for this persona:

- Can see risky tools, sensitive data access, and missing controls.
- Can review validation findings.
- Can export an evidence bundle.
- Can verify that a blocked agent failed closed.

### 5.3 Agent Owner

The Agent Owner is the business-line owner of a candidate agent. They may not operate a workforce-management console every day, but they must own the agent's purpose, approve scoped actions, and accept or remediate risk.

Success for this persona:

- Gets a simple approval card.
- Understands what the agent does.
- Understands why approval is needed.
- Can distinguish "ready" from "needs remediation."

### 5.4 Auditor

The Auditor needs a read-only package showing what was known, what was decided, who approved it, and what evidence backs the decision.

Success for this persona:

- Receives a structured evidence bundle.
- Can trace findings to events.
- Can see the AI BOM, policy envelope, validation results, and approval status.

### 5.5 Google Challenge Judge

The judge needs to understand the business case, see the agent act autonomously, understand the Google technology usage, and watch a crisp demo.

Success for this persona:

- Sees ADK / Gemini / MCP / Stitch in action.
- Sees business value in under four minutes.
- Sees a clear path from prototype to production.
- Sees a novel workforce-onboarding pattern, not a generic workflow bot.
- Sees the workforce-parallel frame as the differentiator.

---

## 6. Core use cases

### 6.1 Use Case A — Safe read-only research agent

**Scenario:** A research assistant agent can search public sources and summarize information. It has no write tools and no sensitive data access.

Expected result:

- Passport generated.
- AI BOM generated.
- Low-risk policy envelope generated.
- Validation passes.
- Decision: **Ready**.

### 6.2 Use Case B — CRM write-agent with missing owner

**Scenario:** A sales operations agent can read and update CRM records but no accountable owner is declared.

Expected result:

- Passport generated with missing owner flagged.
- AI BOM generated.
- Policy envelope requires owner assignment and approval for CRM writes.
- Validation catches missing owner.
- Decision: **Blocked Pending Remediation**.

### 6.3 Use Case C — PHI / regulated-data support agent

**Scenario:** A healthcare support agent may handle regulated health data and interact with ticketing tools. The fixture declares an owner, declares a specific purpose, declares regulated_phi data classes, and declares one external_write tool (ticket creation) with no approval rule attached.

Expected result:

- Passport generated.
- AI BOM generated.
- High-risk data classification recorded.
- Policy envelope requires stricter access, human approval for external sharing, short retention, and elevated evidence requirements.
- Validation finding: regulated data without approval rule (medium severity, with mitigation path).
- Decision: **Ready with Conditions**.

This fixture is the canonical Conditional example for the must-ship gallery. The Blocked variant is covered by `crm_write_missing_owner` and `prompt_injected_mcp_agent`.

### 6.4 Use Case D — Budget runaway research agent

**Scenario:** A deep research agent can call multiple models and tools. Its declared monthly budget is low relative to tool/model use.

Expected result:

- Passport generated.
- AI BOM generated.
- Budget exposure flagged.
- Policy envelope adds per-run and monthly limits.
- Validation simulates budget threshold breach.
- Decision: **Ready with Conditions**.

### 6.5 Use Case E — Prompt-injected MCP tool manifest

**Scenario:** A candidate agent declares an MCP tool whose description contains prompt-injection payload ("ignore previous instructions," "bypass policy," etc.).

Expected result:

- Discovery flags suspicious tool metadata.
- Validation catches prompt-injection risk.
- Policy envelope denies or quarantines the tool.
- Evidence bundle includes the finding.
- Decision: **Blocked Pending Remediation**.

### 6.6 Test Agent Zoo overview

The challenge repo must include a **Test Agent Zoo**: synthetic candidate agents that judges can run through the web UI and CLI. Each fixture must include a candidate manifest, expected decision, expected findings, sample MCP tool metadata, and short business story.

Must-ship fixtures:

| Fixture | Business story | Expected decision | Primary behavior demonstrated |
|---|---|---|---|
| `safe_research_agent.json` | Public-market research assistant with read-only search/summarization tools. | Ready | Clean onboarding path with low-risk tool boundaries. |
| `crm_write_missing_owner.json` | Sales ops agent that can update CRM records but lacks an accountable owner. | Blocked Pending Remediation | Missing owner fails closed for L2+ / write-capable agents. |
| `healthcare_phi_support_agent.json` | Healthcare support agent with regulated-data exposure and ticketing workflow. | Ready with Conditions | Regulated data boundary, retention, approval, and evidence requirements. |
| `budget_runaway_research_agent.json` | Deep research agent with expensive model/tool chain and weak spend limits. | Ready with Conditions | Budget envelope, premium model gating, and finance approval. |
| `prompt_injected_mcp_agent.json` | MCP tool manifest includes instruction-like malicious text. | Blocked Pending Remediation | Output filtering, indirect prompt-injection detection, and tool quarantine. |

Stretch fixtures:

| Fixture | Business story | Expected decision | Primary behavior demonstrated |
|---|---|---|---|
| `privileged_admin_agent.json` | IT automation agent can modify access groups or service accounts. | Blocked Pending Remediation | Privileged tool boundary and four-eyes approval requirement. |
| `unmaintained_mcp_server_agent.json` | Agent depends on archived or unversioned MCP server. | Ready with Conditions or Blocked | Dependency/version/patch-history finding (NSA MCP guidance demonstration). |
| `grounding_required_policy_agent.json` | Agent has ambiguous regulatory obligations that require policy retrieval. | Ready with Conditions | Grounding/RAG changes the quality of policy classification and explanation. |

The Web UI must expose the Test Agent Zoo as a selectable gallery. Judges should be able to choose a fixture, run onboarding, view the workflow, inspect artifacts, and download the evidence bundle without touching the CLI.

---

## 7. Functional requirements

### 7.1 Intake requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| CPOA-FR-001 | Accept candidate agent manifest | System accepts JSON manifest through CLI, API, or UI. |
| CPOA-FR-002 | Accept Google Agent Registry-style fixture | System accepts registry-style metadata fixture even if real API access is unavailable. |
| CPOA-FR-003 | Accept MCP tool metadata | System parses MCP-style tool declarations from fixture or tool server. |
| CPOA-FR-004 | Validate manifest shape | Invalid manifests return clear errors and remediation hints. |
| CPOA-FR-005 | Preserve raw input | Evidence bundle includes hash of raw submitted manifest. |

### 7.2 Discovery requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| CPOA-FR-010 | Extract agent identity | Candidate ID, name, origin, runtime, and framework are extracted. |
| CPOA-FR-011 | Extract owner and purpose | Owner and declared purpose are extracted; missing values are findings. |
| CPOA-FR-012 | Extract model dependencies | Model/provider dependencies are normalized into AI BOM entries. |
| CPOA-FR-013 | Extract tool dependencies | MCP/API/tool dependencies are normalized into AI BOM entries. |
| CPOA-FR-014 | Extract data classes | Declared and inferred data classes are captured. |
| CPOA-FR-015 | Extract autonomy level | Agent is classified by allowed action level. |
| CPOA-FR-016 | Extract budget exposure | Declared budget and estimated tool/model cost risk are captured. |

### 7.3 Policy requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| CPOA-FR-020 | Generate policy envelope | System creates a draft envelope with tool, data, provider, budget, memory, approval, and kill-switch fields. |
| CPOA-FR-021 | Deny unsafe defaults | Missing owner, high-risk tools, or sensitive data access cannot produce unconditional Ready. |
| CPOA-FR-022 | Require human approval | High-impact writes, external communication, regulated data, or budget escalation require approval. |
| CPOA-FR-023 | Produce remediation hints | Findings include concrete remediation guidance. |
| CPOA-FR-024 | Preserve policy rationale | Policy envelope includes rationale for each major constraint. |

### 7.4 Artifact requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| CPOA-FR-030 | Generate Agent Passport | Passport contains identity, origin, owner, provider/runtime, trust tier, policy reference, AI BOM reference, approval requirements, audit completeness, kill-switch state, and onboarding posture. |
| CPOA-FR-031 | Generate AI BOM | AI BOM lists model, prompt, tool, data, memory, runtime, framework, registry, and external dependencies with `source` and `confidence` provenance fields per §11.4. |
| CPOA-FR-032 | Generate approval card | Approval card summarizes purpose, risk, side effects, costs, findings, and recommended action. |
| CPOA-FR-033 | Generate evidence bundle | Evidence bundle includes passport, AI BOM, policy envelope, score, validation results, approval card, event log, and hashes. |
| CPOA-FR-034 | Export JSON | All artifacts export as JSON. |
| CPOA-FR-035 | Export human-readable report | System exports Markdown or PDF-style report. Markdown is minimum viable. |

### 7.5 Validation requirements (Onboarding Validation Suite)

| ID | Requirement | Acceptance criteria |
|---|---|---|
| CPOA-FR-040 | Run Onboarding Validation Suite | System executes all five OV-001 through OV-005 tests per candidate. |
| CPOA-FR-041 | Validate missing owner/purpose | Missing owner or weak purpose creates finding. |
| CPOA-FR-042 | Validate tool boundary | Unapproved tool attempt creates finding. |
| CPOA-FR-043 | Validate sensitive data handling | Regulated data without approval or retention policy creates finding. |
| CPOA-FR-044 | Validate prompt-injection risk | Instruction-like tool metadata creates finding. |
| CPOA-FR-045 | Validate budget boundary | Budget breach simulation creates finding. |

### 7.6 Evidence requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| CPOA-FR-050 | Emit evidence events | Every workflow stage emits a structured event. |
| CPOA-FR-051 | Hash-chain events | Events include current hash and previous-event hash per the canonical serialization rule in §11.8. |
| CPOA-FR-052 | Trace execution | Events include trace/session IDs. |
| CPOA-FR-053 | Label demo signing honestly | Signature field is clearly marked demo-only unless real signing is implemented. |
| CPOA-FR-054 | Preserve replay context | Evidence bundle contains enough structured context to understand decision rationale. |

### 7.7 Demo requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| CPOA-FR-060 | Run local demo | One command runs the full demo with fixtures. |
| CPOA-FR-061 | Run deployed demo | Hosted demo runs on Cloud Run (UI + API + MCP) and Agent Engine (orchestrator), with Cloud Run fallback for orchestrator if Agent Engine is unavailable. |
| CPOA-FR-062 | Show agent trace | Demo shows reasoning/tool workflow at a safe level without exposing hidden prompts or secrets. |
| CPOA-FR-063 | Show pass and fail cases | Demo includes at least one Ready, one Conditional, and one Blocked candidate. |
| CPOA-FR-064 | Finish in under four minutes | Demo video can show full workflow in judging-friendly time. |
| CPOA-FR-065 | Open with workforce-parallel frame | Demo video's first 25 seconds use the HR-to-AI grid (passport / job description / resume / personnel file), not a generic problem statement. |

### 7.8 Web UI requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| CPOA-FR-070 | Ship judge-facing Web UI | A deployed URL lets judges run the onboarding workflow without using CLI. |
| CPOA-FR-071 | Expose Test Agent Zoo | UI includes fixture gallery with Ready, Conditional, and Blocked examples. |
| CPOA-FR-072 | Show multi-agent orchestration | UI displays workflow stage timeline and subagent contributions: Discovery, Policy, Passport, Validation, Evidence. |
| CPOA-FR-073 | Show grounded evidence | UI distinguishes model-generated summary from grounded retrieved sources/policy excerpts. |
| CPOA-FR-074 | Show artifacts | UI renders Passport, AI BOM, Policy Envelope, Approval Card, Validation Findings, and Evidence Bundle. |
| CPOA-FR-075 | Download artifacts | UI provides JSON and Markdown download links for generated artifacts. |
| CPOA-FR-076 | Provide testing access | Hosted build uses HTTP basic auth with credentials documented in `JUDGE_RUNBOOK.md`. |
| CPOA-FR-077 | Support architecture view | UI includes an architecture page that explains Google stack usage (ADK, Gemini, Stitch, MCP, Agent Engine, Cloud Run, optional Agent Search). |
| CPOA-FR-078 | Preserve accessibility | UI meets basic contrast, keyboard navigation, focus, and reduced-motion requirements. |
| CPOA-FR-079 | Use Stitch-sourced designs | Every required route originates from a Stitch design checked into `design/stitch/` and exported to `app/web/src`. |

### 7.9 Grounding and RAG requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| CPOA-FR-080 | Create grounded corpus | Repo or deployment includes a sanitized corpus assembled from public sources: selected NSA MCP CSI excerpts, NIST AI RMF subset (govern/measure/manage functions relevant to agent deployment), EU AI Act selected articles (transparency, human oversight, record-keeping), CPOA's own policy pack, schema definitions, and fixture documentation. Source attribution is preserved per excerpt. |
| CPOA-FR-081 | Use Google grounding where available | Agent Search / Vertex AI Search or RAG Engine is used if access is available in challenge project. |
| CPOA-FR-082 | Provide retrieval fallback | Local/custom retriever can run same demo when Google grounding access is unavailable. |
| CPOA-FR-083 | Attribute grounded facts | Policy and Evidence outputs include `grounding_refs` with source IDs, source titles, and short snippets. |
| CPOA-FR-084 | Demonstrate multi-agent grounded value | The demo includes a side-by-side example: a Policy/Evidence finding produced by an ungrounded single Gemini call versus the grounded multi-agent path. The grounded path cites a specific public source (e.g., NSA MCP CSI section) for the finding. Both runs are stored as fixtures and rendered in the UI. |

### 7.10 Secure MCP requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| CPOA-FR-090 | Authenticate MCP calls | MCP server rejects unauthenticated requests in deployed mode. |
| CPOA-FR-091 | Authorize by tool and role | Tool execution checks caller role, session, fixture scope, and tool risk tier. |
| CPOA-FR-092 | Validate schemas strictly | All tool inputs and outputs validate against Pydantic/JSON Schema with size limits and deny-by-default unknown fields. |
| CPOA-FR-093 | Bind messages to context | MCP requests include trace/session ID, nonce/idempotency key, expiration timestamp, and request hash. |
| CPOA-FR-094 | Filter chained outputs | Every tool output is treated as untrusted input before being passed to the next agent. |
| CPOA-FR-095 | Log security telemetry | MCP logs identities, parameters, tool IDs, hashes, decisions, denials, and anomaly flags. |
| CPOA-FR-096 | Restrict egress | Deployed MCP server uses explicit allowlist for outbound network access where feasible. |
| CPOA-FR-097 | Sandbox risky tools | Any tool execution that could access filesystem, shell, database, or external API runs with least privilege and explicit runtime constraints. |

---

## 8. Non-functional requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| CPOA-NFR-001 | Reproducibility | Clean checkout can run fixtures locally with documented setup. |
| CPOA-NFR-002 | Judge friendliness | README includes architecture, setup, demo script, and known limitations. |
| CPOA-NFR-003 | Security hygiene | No secrets committed. `.env.example` only. Secret scanning enabled if available. |
| CPOA-NFR-004 | IP protection | Main CPL build pack and proprietary internals are not copied into repo. |
| CPOA-NFR-005 | Honesty | Docs clearly distinguish demo artifacts from production Anchor/Meridian capabilities and clearly distinguish the onboarding gate from continuous attestation (which is roadmap, not implemented). |
| CPOA-NFR-006 | Portability | Adapter pattern separates Google-specific ingestion from neutral Passport data model. |
| CPOA-NFR-007 | Fast path | Core workflow should run without requiring real Agent Registry access. |
| CPOA-NFR-008 | Graceful degradation | If Agent Engine, Agent Registry, Agent Search, or Evaluation is unavailable, Cloud Run + fixtures + local retrieval + local eval remain valid. |
| CPOA-NFR-009 | Accessibility | UI meets WCAG-aligned basics: contrast, keyboard navigation, focus visibility, reduced motion. |
| CPOA-NFR-010 | Cost control | Stay within $500 challenge credits. If credit burn exceeds 40% by Day 5, scale back eval frequency and reduce premium-model calls. |
| CPOA-NFR-011 | Schema canonicality | Data contracts in §11 do not drift from CPM-MERIDIAN-CANONICAL §6 and CPL-CONNECTOR-CAPABILITY-MATRIX-CANONICAL §3 structure unless explicitly justified inline. |
| CPOA-NFR-012 | UI polish | Web UI ships as a Stitch-sourced experience with CPL brand tokens applied; no raw Swagger or unstyled JSON dump as primary judging surface. |
| CPOA-NFR-013 | Design discipline | Motion and color must clarify state and risk; avoid decorative animation that obscures evidence or accessibility. |
| CPOA-NFR-014 | NSA MCP posture | MCP implementation must include a documented control checklist mapped to §12.6. |
| CPOA-NFR-015 | Agent Engine attempt | Agent Engine / Agent Runtime deployment is the primary path; if not possible, document blocker and use Cloud Run fallback with same API contract. |

---

## 9. Architecture

### 9.1 High-level architecture

```text
[Judge / Founder / Builder]
        |
        v
[Web UI — Stitch-sourced Next.js/React on Cloud Run]
        |
        |-- Test Agent Zoo gallery
        |-- Onboarding run timeline
        |-- Artifact review panels
        |-- Evidence bundle download
        |-- Architecture / testing access page
        |
        v
[API Gateway / Web Backend on Cloud Run]
        |
        v
[ClearPoint Onboarding Agent — ADK Orchestrator on Agent Engine / Agent Runtime]
        |
        |-- Discovery Subagent
        |-- Grounded Policy Subagent
        |-- Passport Artifact Subagent
        |-- Onboarding Validation Subagent
        |-- Evidence Writer Subagent
        |-- Explanation / Demo Narrator Subagent
        |
        |       (grounding/RAG)
        |-----------------------------> [Agent Search / Vertex AI Search or RAG Engine]
        |                               [Local retrieval fallback]
        |
        v
[Secure MCP Server on Cloud Run]
        |
        |-- inspect_candidate_agent
        |-- generate_policy_envelope
        |-- generate_passport_artifacts
        |-- run_onboarding_validation_suite
        |-- write_evidence_bundle
        |
        v
[Artifact Store + Evidence Log]
        |
        |-- Agent Passport JSON
        |-- AI BOM JSON
        |-- Policy Envelope JSON
        |-- Validation Findings JSON
        |-- Approval Card JSON / Markdown
        |-- Evidence Bundle JSON / Markdown
        |
        v
[Cloud Logging / Trace / Optional Agent Observability]
```

### 9.2 Google platform mapping

| Product need | Preferred Google surface | Fallback |
|---|---|---|
| Agent framework | ADK Python | ADK-compatible local orchestration wrapper |
| Model | Gemini via Vertex AI / Agent Platform | Challenge-approved Gemini endpoint |
| UI design source | Google Stitch (designs + starter code) | Hand-built Tailwind/shadcn components from CPL brand tokens |
| Orchestrator deployment | Agent Engine / Agent Runtime | Cloud Run fallback if Agent Engine access is blocked |
| Tool protocol | Secure HTTP MCP server on Cloud Run | Local stdio MCP server in dev only |
| Agent metadata | Agent Registry if available | Synthetic registry fixture matching documented concepts |
| Identity concept | Agent Identity if available | Synthetic identity field + adapter placeholder |
| Gateway concept | Agent Gateway if available | Policy envelope + simulated gateway decision |
| Observability | Cloud Logging / Cloud Trace / Agent Observability | Structured local logs + trace IDs |
| Evaluation | Agent Evaluation / Simulation if available | Local deterministic eval harness |
| Web UI runtime | Next.js/React on Cloud Run with CPL brand tokens | Static build on Cloud Run or Firebase Hosting if needed |
| Grounding/RAG | Agent Search / Vertex AI Search or Agent Platform RAG Engine | Local/custom retrieval over sanitized corpus |
| Artifact storage | Firestore or Cloud SQL | Local filesystem JSON for demo |

### 9.3 Agent architecture

The ClearPoint Onboarding Agent should be implemented as a small multi-agent system, not a single monolithic prompt.

#### 9.3.1 Orchestrator — `onboarding_orchestrator`

Responsibilities:

- Own the workflow state machine.
- Validate candidate input.
- Delegate to subagents/tools.
- Resolve conflicts between findings.
- Produce final onboarding decision.
- Ensure every stage emits evidence.

Inputs:

- Candidate manifest.
- Optional registry fixture.
- Optional MCP tool metadata.
- Optional policy pack.

Outputs:

- Final decision.
- Artifact bundle.
- Evidence bundle.

#### 9.3.2 Discovery subagent — `discovery_agent`

Responsibilities:

- Parse candidate manifest.
- Normalize identity, owner, purpose, runtime, model, tools, data classes, memory, autonomy, budget, and registry metadata.
- Identify missing fields.
- Identify inconsistent fields.

Outputs:

- `DiscoveryReport`.
- Evidence event: `onboarding.discovery.completed`.

#### 9.3.3 Policy subagent — `policy_agent`

Responsibilities:

- Map discovered attributes into policy requirements.
- Propose tool boundaries.
- Propose data boundaries.
- Propose provider/model boundaries.
- Propose budget boundaries.
- Propose approval requirements.
- Propose kill-switch state.
- Cite grounding sources where retrieval informed the proposal.

Outputs:

- `PolicyEnvelope` (with `grounding_refs`).
- Evidence event: `onboarding.policy.proposed`.

#### 9.3.4 Passport artifact subagent — `artifact_agent`

Responsibilities:

- Generate Agent Passport.
- Generate AI BOM.
- Generate Passport Readiness Score.
- Generate approval card.

Outputs:

- `AgentPassport`.
- `AIBOM`.
- `PassportReadinessScore`.
- `ApprovalCard`.
- Evidence event: `onboarding.artifacts.generated`.

#### 9.3.5 Onboarding Validation subagent — `validation_agent`

Responsibilities:

- Execute deterministic Onboarding Validation Suite scenarios.
- Evaluate candidate against missing owner/purpose, tool boundary, sensitive data, prompt-injection, and budget tests.
- Produce findings with severity, confidence, and remediation.

Outputs:

- `ValidationRun`.
- Evidence event: `onboarding.validation.executed`.

Note: This subagent implements the *onboarding gate*. It is not Sentinel, Forensics, Drift, Red Team, or Regulatory Watch — those are the canonical Continuous Validation Agent Suite that runs post-onboarding and is out of scope for this challenge build.

#### 9.3.6 Evidence writer subagent — `evidence_agent`

Responsibilities:

- Write hash-chained evidence events per §11.8 canonical serialization rule.
- Assemble evidence bundle.
- Export JSON and Markdown.
- Label demo-only signing honestly.

Outputs:

- `EvidenceEvent[]`.
- `EvidenceBundle`.
- Evidence event: `onboarding.evidence.bundle.exported`.

#### 9.3.7 Explanation / demo narrator subagent — `explanation_agent`

Responsibilities:

- Produce judge-facing explanations for the Web UI without exposing hidden chain-of-thought.
- Translate findings into workforce language: ID badge, job description, resume, personnel file, manager approval.
- Cite grounded policy and MCP-security references where available.
- Generate concise artifact summaries for the UI and video.

Outputs:

- `RunNarrative`.
- `GroundedExplanation`.
- Evidence event: `onboarding.explanation.generated`.

---

## 10. Workflow state machine

### 10.1 States

```text
RECEIVED
  -> INPUT_VALIDATED
  -> DISCOVERY_COMPLETED
  -> POLICY_PROPOSED
  -> ARTIFACTS_GENERATED
  -> VALIDATION_COMPLETED
  -> APPROVAL_CARD_GENERATED
  -> EVIDENCE_BUNDLE_EXPORTED
  -> DECISION_ISSUED
```

### 10.2 Terminal decisions

| Decision | Meaning | Required conditions |
|---|---|---|
| Ready | Agent can be onboarded under proposed policy. | No critical findings; score ≥80; owner and purpose present; validation passes or only low findings. |
| Ready with Conditions | Agent can be onboarded only after human approval or policy constraints. | No unresolved critical findings; score 60–79 or medium/high findings with clear mitigations. |
| Blocked Pending Remediation | Agent must not be onboarded yet. | Critical finding, missing owner for action-capable agent, unsafe tool boundary, sensitive data without policy, prompt-injection failure, or score <60. |

### 10.3 Fail-closed behavior

The system fails closed. If discovery, policy generation, validation, or evidence writing fails, the agent cannot receive Ready. The final decision must be **Blocked Pending Remediation** or **Needs Manual Review**.

### 10.4 Workflow pseudocode

```python
def onboard_candidate_agent(candidate_manifest):
    event("onboarding.intake.received", candidate_manifest.hash)

    validated_input = validate_manifest(candidate_manifest)
    event("onboarding.input.validated", validated_input.summary)

    discovery = discovery_agent.run(validated_input)
    event("onboarding.discovery.completed", discovery.summary)

    policy = policy_agent.run(discovery)
    event("onboarding.policy.proposed", policy.summary)

    artifacts = artifact_agent.run(discovery, policy)
    event("onboarding.artifacts.generated", artifacts.summary)

    validation = validation_agent.run(discovery, policy, artifacts)
    event("onboarding.validation.executed", validation.summary)

    approval_card = artifact_agent.generate_approval_card(discovery, policy, validation)
    event("onboarding.approval.card.generated", approval_card.summary)

    evidence_bundle = evidence_agent.export(discovery, policy, artifacts, validation, approval_card)
    event("onboarding.evidence.bundle.exported", evidence_bundle.hash)

    decision = decide(discovery, policy, validation, artifacts.score)
    event("onboarding.decision.issued", decision)

    return decision, evidence_bundle
```

---

## 11. Data contracts

**Canonicality note.** The schemas below are designed as **v0.1 of Meridian's external-facing public schemas**. They are intentionally upstream-compatible with CPM-MERIDIAN-CANONICAL §6 (Govern surface artifact shape), CPL-CONNECTOR-CAPABILITY-MATRIX-CANONICAL §3 (ECS taxonomy), CPL-AUDIT-EVIDENCE-CANONICAL (hash-chained signed event pattern), and CPL-WORKFORCE-PARALLEL-CANONICAL (passport/policy/AI BOM artifact roles). Post-challenge merge into the main canonical system should be a forward-compatible v0.1 → v0.2 evolution. Any field renamings, deletions, or semantic changes from these contracts must be justified inline before implementation.

### 11.1 CandidateAgentManifest

```json
{
  "schema_version": "candidate-agent-manifest/v0.1",
  "candidate_agent_id": "string",
  "name": "string",
  "origin": "google_adk | gemini_enterprise | mcp_server | custom | third_party | unknown",
  "declared_purpose": "string",
  "owner": {
    "name": "string",
    "email": "string",
    "team": "string",
    "role": "string"
  },
  "runtime": {
    "framework": "adk | langchain | crewai | custom | unknown",
    "language": "python | go | typescript | unknown",
    "deployment_target": "agent_runtime | cloud_run | gke | external | local | unknown",
    "region": "string",
    "service_account_or_identity": "string"
  },
  "models": [
    {
      "provider": "google | anthropic | openai | other | unknown",
      "model": "string",
      "purpose": "reasoning | classification | embedding | generation | code | unknown",
      "criticality": "required | optional"
    }
  ],
  "tools": [
    {
      "tool_id": "string",
      "name": "string",
      "protocol": "mcp | rest | grpc | sdk | unknown",
      "description": "string",
      "risk_tier": "read_only | internal_write | external_write | financial_action | privileged_admin | unknown",
      "auth_scope": "string",
      "side_effects": "none | internal_state_change | external_message | financial_transfer | access_change | unknown"
    }
  ],
  "data_access": {
    "declared_data_classes": ["public", "internal", "confidential", "customer_pii", "regulated_phi", "financial", "secrets"],
    "memory_enabled": true,
    "retention_days": 30
  },
  "autonomy": {
    "level": "L0_observe | L1_recommend | L2_draft | L3_execute_with_approval | L4_bounded_autonomous | L5_high_impact_autonomous",
    "human_approval_required": true
  },
  "budget": {
    "monthly_usd": 500,
    "per_run_usd": 5,
    "premium_model_allowed": false
  },
  "registry_metadata": {
    "registry_source": "google_agent_registry_fixture | manual | none",
    "version": "string",
    "capabilities": ["string"],
    "annotations": {}
  }
}
```

### 11.2 DiscoveryReport

```json
{
  "schema_version": "discovery-report/v0.1",
  "candidate_agent_id": "string",
  "summary": "string",
  "identity": {},
  "owner_status": "present | missing | incomplete",
  "purpose_status": "specific | vague | missing",
  "runtime_profile": {},
  "model_dependencies": [],
  "tool_dependencies": [],
  "data_classes": [],
  "autonomy_level": "string",
  "budget_profile": {},
  "missing_fields": [],
  "inconsistencies": [],
  "initial_risk_drivers": []
}
```

### 11.3 AgentPassport

The Agent Passport is the primary output artifact. It is challenge-safe and Meridian-inspired. In the workforce-parallel frame, this is the agent's **ID badge**.

```json
{
  "schema_version": "agent-passport/v0.1",
  "passport_id": "string",
  "issued_at": "ISO-8601 timestamp",
  "candidate_agent_id": "string",
  "agent_name": "string",
  "origin": "string",
  "owner": {
    "name": "string",
    "email": "string",
    "team": "string",
    "status": "verified | missing | incomplete"
  },
  "purpose": {
    "declared": "string",
    "normalized": "string",
    "status": "specific | vague | missing"
  },
  "runtime": {
    "framework": "string",
    "deployment_target": "string",
    "region": "string",
    "identity": "string"
  },
  "trust_tier": "demo_tier_1_low | demo_tier_2_moderate | demo_tier_3_high",
  "policy_envelope_id": "string",
  "ai_bom_id": "string",
  "approval_requirements": [],
  "audit_completeness": {
    "score": 0,
    "missing_evidence": []
  },
  "kill_switch_state": "healthy | paused_required | blocked",
  "onboarding_posture": "challenge_demo_ready | conditional | blocked",
  "not_anchor_certification": true,
  "passport_readiness_score": 0,
  "decision": "Ready | Ready with Conditions | Blocked Pending Remediation"
}
```

### 11.4 AI Bill of Materials

In the workforce-parallel frame, this is the agent's **resume** — its declared models, prompts, tools, data, memory, runtime, and dependencies.

```json
{
  "schema_version": "ai-bom/v0.1",
  "ai_bom_id": "string",
  "candidate_agent_id": "string",
  "generated_at": "ISO-8601 timestamp",
  "models": [],
  "prompts_or_instructions": [
    {
      "name": "string",
      "hash": "sha256:string",
      "storage": "not_included | included_fixture | external_reference"
    }
  ],
  "tools": [],
  "data_sources": [],
  "memory": {
    "enabled": true,
    "retention_days": 30,
    "data_classes": []
  },
  "runtime_dependencies": [],
  "registry_metadata": {},
  "known_unknowns": []
}
```

Every AI BOM model, tool, data, memory, and runtime dependency entry must include:

```json
{
  "source": "declared | inferred | verified | fixture",
  "confidence": "high | medium | low"
}
```

Self-reported dependency claims must not be treated as verified facts.

### 11.5 PolicyEnvelope

In the workforce-parallel frame, this is the agent's **job description** — what it is authorized to do, with whom, with which resources, under what budget, with what approvals required.

```json
{
  "schema_version": "policy-envelope/v0.1",
  "policy_envelope_id": "string",
  "candidate_agent_id": "string",
  "status": "draft | proposed | approved | blocked",
  "tool_boundary": {
    "allowed_tools": [],
    "denied_tools": [],
    "requires_approval": []
  },
  "data_boundary": {
    "allowed_data_classes": [],
    "denied_data_classes": [],
    "requires_approval": [],
    "retention_days": 30
  },
  "provider_boundary": {
    "allowed_providers": [],
    "premium_model_allowed": false,
    "requires_approval": []
  },
  "budget_boundary": {
    "monthly_usd": 0,
    "per_run_usd": 0,
    "on_breach": "pause | require_approval | notify_only"
  },
  "memory_boundary": {
    "memory_enabled": true,
    "allowed_memory_classes": [],
    "retention_days": 30
  },
  "approval_rules": [
    {
      "condition": "string",
      "required_approver_role": "agent_owner | security | compliance | finance | ai_workforce_manager",
      "approval_mode": "single | four_eyes"
    }
  ],
  "kill_switch": {
    "initial_state": "healthy | paused_required | blocked",
    "trigger_conditions": []
  },
  "rationale": [],
  "grounding_refs": [
    {
      "source_id": "string",
      "source_title": "string",
      "snippet": "string"
    }
  ]
}
```

### 11.6 PassportReadinessScore

This score is challenge-safe and demo-only. It is **not** production CAS/ECS — those are proprietary CPL scoring systems defined in CPL-CONTINUOUS-ATTESTATION-SCORE-CANONICAL and CPL-CONNECTOR-CAPABILITY-MATRIX-CANONICAL and are deliberately out of scope.

```json
{
  "schema_version": "passport-readiness-score/v0.1",
  "candidate_agent_id": "string",
  "score": 0,
  "band": "ready | conditional | blocked",
  "components": {
    "identity_and_owner": 0,
    "purpose_and_runtime_clarity": 0,
    "tool_and_data_boundaries": 0,
    "approval_and_budget_controls": 0,
    "evidence_and_observability": 0,
    "validation_results": 0
  },
  "rationale": [],
  "not_production_cas_or_ecs": true
}
```

Score bands:

| Score | Band | Default decision |
|---:|---|---|
| 80–100 | Ready | Ready if no critical findings. |
| 60–79 | Conditional | Ready with Conditions. |
| 0–59 | Blocked | Blocked Pending Remediation. |

Component weights for challenge demo:

| Component | Points |
|---|---:|
| Identity and owner | 15 |
| Purpose and runtime clarity | 15 |
| Tool and data boundaries | 20 |
| Approval and budget controls | 15 |
| Evidence and observability | 15 |
| Validation results | 20 |
| **Total** | **100** |

Deterministic caps and deductions:

| Condition | Score behavior |
|---|---|
| Critical finding | Cap at 59 |
| Missing owner for L2+ agent | Cap at 59 |
| Evidence bundle export failure | Cap at 59 |
| High unresolved finding | Cap at 79 |
| Medium finding with documented mitigation | Cap at 79 |
| Missing optional metadata only | Deduct 5–10 points |
| Low/info findings only | No cap |

Canonical rule: Gemini may generate summaries, rationale, and explanations. Deterministic code computes score, bands, blockers, and final decision.

### 11.7 ValidationFinding

```json
{
  "schema_version": "validation-finding/v0.1",
  "finding_id": "string",
  "candidate_agent_id": "string",
  "test_id": "string",
  "severity": "critical | high | medium | low | info",
  "confidence": "high | medium | low",
  "title": "string",
  "description": "string",
  "evidence_refs": [],
  "recommended_remediation": "string",
  "blocks_ready_decision": true
}
```

### 11.8 EvidenceEvent

```json
{
  "schema_version": "evidence-event/v0.1",
  "event_id": "string",
  "event_type": "onboarding.intake.received",
  "timestamp": "ISO-8601 timestamp",
  "trace_id": "string",
  "session_id": "string",
  "actor": {
    "type": "agent | human | system",
    "id": "string"
  },
  "subject": {
    "candidate_agent_id": "string"
  },
  "summary": "string",
  "payload_hash": "sha256:string",
  "previous_event_hash": "sha256:string | null",
  "event_hash": "sha256:string",
  "signature": {
    "type": "demo_stub | sigstore | none",
    "value": "string",
    "note": "Demo hash only; not production Anchor signing unless otherwise stated."
  }
}
```

Canonical serialization rule:

- Event hashes are computed over canonical JSON using sorted keys, compact separators, UTF-8 encoding, and exclusion of mutable fields such as `signature.value`.
- Bundle hashes exclude `bundle_hash` itself.
- Artifact hashes are computed over each artifact's canonical JSON representation.
- Any mismatch in event-hash validation blocks a Ready decision.

Canonical event types:

- `onboarding.intake.received`
- `onboarding.input.validated`
- `onboarding.discovery.completed`
- `onboarding.policy.proposed`
- `onboarding.artifacts.generated`
- `onboarding.validation.executed`
- `onboarding.approval.card.generated`
- `onboarding.evidence.bundle.exported`
- `onboarding.decision.issued`
- `onboarding.error.fail_closed`

### 11.9 EvidenceBundle

In the workforce-parallel frame, this is the agent's **personnel file** at hire — the structured record that follows it forward through its operating life.

```json
{
  "schema_version": "evidence-bundle/v0.1",
  "bundle_id": "string",
  "candidate_agent_id": "string",
  "generated_at": "ISO-8601 timestamp",
  "decision": "Ready | Ready with Conditions | Blocked Pending Remediation",
  "passport": {},
  "ai_bom": {},
  "policy_envelope": {},
  "passport_readiness_score": {},
  "validation_run": {},
  "approval_card": {},
  "evidence_events": [],
  "bundle_hash": "sha256:string",
  "limitations": [
    "Challenge demo artifact; not production Anchor certification.",
    "Synthetic inputs unless explicitly noted.",
    "Demo signature is not production cryptographic attestation.",
    "Implements onboarding gate only; continuous attestation (the canonical CPL post-onboarding layer) is out of scope for this build."
  ]
}
```

### 11.10 ApprovalCard

```json
{
  "schema_version": "approval-card/v0.1",
  "approval_card_id": "string",
  "candidate_agent_id": "string",
  "recommended_decision": "approve | approve_with_conditions | deny",
  "approver_roles": [],
  "summary": "string",
  "business_purpose": "string",
  "risk_summary": "string",
  "side_effects_preview": [],
  "data_access_summary": [],
  "tool_access_summary": [],
  "budget_summary": "string",
  "required_conditions": [],
  "evidence_bundle_id": "string"
}
```

---

## 12. MCP tool surface

The challenge artifact exposes MCP-compatible tools through an actual MCP server. HTTP MCP is the deployed target; stdio MCP is local-dev fallback only. Judges who know MCP will care about this distinction.

### 12.1 `inspect_candidate_agent`

Purpose: Parse and normalize candidate manifest.

Input:

```json
{ "candidate_manifest": {} }
```

Output:

```json
{ "discovery_report": {}, "evidence_event": {} }
```

### 12.2 `generate_policy_envelope`

Purpose: Create policy envelope from discovery report.

Input:

```json
{
  "discovery_report": {},
  "policy_pack": "baseline_enterprise_v0_1"
}
```

Output:

```json
{ "policy_envelope": {}, "evidence_event": {} }
```

### 12.3 `generate_passport_artifacts`

Purpose: Generate Agent Passport, AI BOM, Passport Readiness Score, and approval card.

Input:

```json
{
  "discovery_report": {},
  "policy_envelope": {}
}
```

Output:

```json
{
  "agent_passport": {},
  "ai_bom": {},
  "passport_readiness_score": {},
  "approval_card": {},
  "evidence_event": {}
}
```

### 12.4 `run_onboarding_validation_suite`

Purpose: Execute Onboarding Validation Suite tests.

Input:

```json
{
  "candidate_manifest": {},
  "policy_envelope": {},
  "tests": ["missing_owner", "tool_boundary", "sensitive_data", "prompt_injection", "budget_boundary"]
}
```

Output:

```json
{
  "validation_run": {},
  "findings": [],
  "evidence_event": {}
}
```

### 12.5 `write_evidence_bundle`

Purpose: Export the final evidence bundle.

Input:

```json
{
  "agent_passport": {},
  "ai_bom": {},
  "policy_envelope": {},
  "passport_readiness_score": {},
  "validation_run": {},
  "approval_card": {},
  "evidence_events": []
}
```

Output:

```json
{
  "evidence_bundle": {},
  "bundle_path": "string",
  "bundle_hash": "sha256:string"
}
```

### 12.6 NSA MCP Security Design Baseline

The MCP server is part of the product story. ClearPoint Onboarding Agent demonstrates what a careful enterprise MCP onboarding surface looks like.

Minimum baseline controls:

| Control | Implementation requirement | Demo evidence |
|---|---|---|
| Supported components | Use maintained MCP SDK/server implementation where possible; pin versions; document dependencies. | `SECURITY.md`, dependency lockfile, vulnerability-scan notes. |
| Trust boundaries | Treat UI, orchestrator, MCP server, tools, candidate manifests, and retrieved documents as separate trust zones. | Architecture diagram + threat notes. |
| Origin verification | Dynamic tool discovery is disabled by default or allowed only from signed/fixture-approved origins. | Denied dynamic discovery finding in logs. |
| Authentication | Deployed MCP server rejects unauthenticated requests. | Negative test in `tests/security`. |
| Authorization | Tool-level RBAC checks caller, candidate, fixture, session, and risk tier. | Tool denial event. |
| Parameter validation | Strict schemas, max sizes, allowed enums, deny unknown fields, context checks. | Schema test and malformed-input test. |
| Egress control | Outbound access allowlisted; no arbitrary fetch from candidate-provided URL. | Egress config or documented Cloud Run allowlist/fallback. |
| Sandboxing / least privilege | No shell/file/network access unless explicitly required; risky tools run with constrained service account and runtime. | Service account/IAM notes. |
| Message integrity | Requests include trace ID, session ID, nonce/idempotency key, expiration, and request hash; optional demo signature. | Evidence event with message metadata. |
| Replay protection | Duplicate nonce/idempotency key is rejected for write-like tools. | Replay test. |
| Output filtering | Every tool/model output is untrusted before downstream use; detect prompt-injection/toolchain pivot phrases. | Prompt-injection fixture showing quarantine. |
| Audit logging | Log exact tool ID, parameters hash, identity, decision, denial reason, output hash, trace ID. | Cloud Logging or local structured log sample. |
| Vulnerability tracking | Maintain MCP dependency inventory, version, patch history, known issues. | `docs/security/MCP_SECURITY_BASELINE.md`. |
| Discovery/scanning posture | Document how unauthorized/unhardened MCP servers would be detected in production; demo can simulate finding. | Stretch fixture `unmaintained_mcp_server_agent.json`. |

For challenge honesty, the implementation may use demo signatures and local fixtures, but the design must make the production hardening path obvious.

---

## 13. Validation specification — Onboarding Validation Suite

The Onboarding Validation Suite (OVS) is the pre-deployment validation harness for the onboarding gate. It is intentionally distinct from the canonical Continuous Validation Agent Suite (Sentinel, Forensics, Drift, Red Team, Regulatory Watch), which runs post-onboarding and is out of scope for this challenge build.

### 13.1 Test OV-001 — Missing owner / purpose

Purpose: Ensure an agent cannot be marked Ready without accountable ownership and a concrete purpose.

Inputs: Candidate manifest with missing owner or vague purpose.

Pass condition: System emits finding; reduces readiness score; requires remediation or approval.

Blocking rule: Action-capable agents with no owner are Blocked Pending Remediation.

### 13.2 Test OV-002 — Unapproved high-risk tool

Purpose: Ensure risky tools cannot be used without explicit policy and approval.

Inputs: Candidate manifest with `external_write`, `financial_action`, or `privileged_admin` tool; policy envelope without matching approval rule.

Pass condition: System emits high or critical finding; recommends deny or approve with conditions.

Blocking rule: Privileged admin or financial action with no approval rule is Blocked.

### 13.3 Test OV-003 — Sensitive data without boundary

Purpose: Ensure sensitive data access has explicit boundaries.

Inputs: Candidate manifest with `customer_pii`, `regulated_phi`, `financial`, or `secrets`; missing retention or approval rule.

Pass condition: System emits finding; policy envelope adds data boundary and approval requirements.

Blocking rule: Regulated data + external write + no approval is Blocked.

### 13.4 Test OV-004 — Prompt-injected tool description

Purpose: Ensure instruction-like text in tool metadata is treated as data, not instructions.

Inputs: MCP tool description containing "ignore previous instructions," "bypass policy," or similar payload.

Pass condition: System flags prompt-injection risk; tool is denied or quarantined pending review.

Blocking rule: Prompt-injected privileged tool is Blocked.

### 13.5 Test OV-005 — Budget boundary breach

Purpose: Ensure the agent cannot exceed declared cost boundaries without action.

Inputs: Candidate manifest with low budget and high estimated model/tool usage.

Pass condition: System flags budget risk; policy envelope proposes per-run and monthly limits.

Blocking rule: If budget boundary is missing entirely for a high-volume agent, Ready is not permitted.

---

## 14. Decision algorithm

### 14.1 Inputs

- Discovery report.
- Policy envelope.
- Passport readiness score.
- Validation findings.
- Evidence completeness.

### 14.2 Blocking conditions

Return **Blocked Pending Remediation** if any condition is true:

- Critical validation finding.
- Missing owner for any L2+ agent.
- Missing purpose for any L2+ agent.
- Sensitive data access without explicit data boundary.
- External write or financial action without approval rule.
- Prompt-injected privileged tool.
- Evidence bundle failed to export.
- Score below 60.

### 14.3 Conditional conditions

Return **Ready with Conditions** if no blocking condition exists and any condition is true:

- Score between 60 and 79.
- Medium/high non-critical finding.
- Missing optional metadata.
- Budget risk needs approval.
- Premium model use requires finance approval.
- Human approval is required before activation.

### 14.4 Ready conditions

Return **Ready** only if all are true:

- Score ≥80.
- No critical or high unresolved findings.
- Owner present.
- Purpose specific.
- Policy envelope complete.
- Evidence bundle exported.
- Validation passed or only low/info findings.

---

## 15. User experience

### 15.1 Canonical UI decision

The Web UI is a must-ship product surface. CLI/API remains required for local runs, evals, and reproducibility, but the judge-facing story depends on a live, polished review interface.

Canonical rule:

> The contest demo is not a terminal demo with a decorative wrapper. It is a workforce-onboarding review experience that happens to be powered by ADK, Gemini, MCP, grounding/RAG, Stitch, and Google Cloud.

### 15.2 Required Web UI information architecture

Required routes:

| Route | Purpose |
|---|---|
| `/` | Landing page with workforce-parallel frame and Start Onboarding CTA. |
| `/agents` | Test Agent Zoo gallery with fixture cards. |
| `/runs/new` | Manifest upload / fixture selection / start workflow. |
| `/runs/:run_id` | Live onboarding run timeline and stage-by-stage results. |
| `/runs/:run_id/passport` | Agent Passport review. |
| `/runs/:run_id/bom` | AI BOM review. |
| `/runs/:run_id/policy` | Policy Envelope review (with grounding source chips). |
| `/runs/:run_id/validation` | Onboarding Validation Suite findings. |
| `/runs/:run_id/evidence` | Evidence bundle, event chain, hashes, downloads. |
| `/architecture` | Challenge architecture diagram and Google-stack mapping. |
| `/judge` | Testing access instructions, fixture shortcuts, demo script, known limitations. |

### 15.3 Required UI layout

Primary run screen has four persistent regions:

1. **Candidate card** — agent name, owner, purpose, runtime, autonomy, data classes, tools.
2. **Workflow rail** — Discovery → Policy → Passport → Validation → Approval → Evidence → Decision.
3. **Artifact workspace** — active artifact panel with tabs for Passport, AI BOM, Policy, Findings, Evidence.
4. **Decision panel** — readiness score, decision badge, top blockers/conditions, download links.

The UI must make multi-agent collaboration visible without exposing hidden prompts or chain-of-thought. Show stage ownership, inputs/outputs, tool calls, and grounded references; do not show private model reasoning.

### 15.4 Stitch design pipeline

The UI is sourced through Google Stitch. Stitch is the design surface; Next.js + Tailwind is the runtime.

Pipeline:

1. **Stitch design pass** — Generate designs in Stitch for each required route in §15.2. Iterate until layout, hierarchy, and motion read as intentional. Keep designs in `design/stitch/` (export files, screenshots, or share links).
2. **Code export** — Use Stitch's code export (Next.js / React / Tailwind) as the starting point for `app/web`.
3. **CPL brand override** — Apply CPL brand tokens (§15.6) as Tailwind theme overrides. Stitch's defaults are replaced where they conflict with CPL primary blue, charcoal, and typography choices.
4. **Component reconciliation** — Where Stitch output and shadcn/ui patterns disagree, prefer shadcn for accessibility-critical components (dialog, dropdown, focus traps); keep Stitch output for layout, hero, cards, and artifact panels.
5. **Motion** — Use Stitch's motion suggestions where they exist; otherwise use Framer Motion fades and slides for stage transitions. Reduced-motion override is required.

The Stitch pipeline replaces the bespoke Material 3 Expressive specification that appeared in v0.3. The pipeline is part of the submission story: Stitch is the third Google product in the stack alongside ADK and Gemini.

### 15.5 CPL brand integration

CPL brand authority remains:

- Primary blue: `#0B65FC`.
- Charcoal: `#1F262B`.
- Secondary accents: aqua `#43CFDF`, orange `#F59E0B`, gray `#CFD2D3`.
- Headings: Lexend if available, system sans-serif fallback.
- Body: Inter if available, system sans-serif fallback.
- Do not embed proprietary font files.
- Logo usage follows CPL Brand Guidelines.

CPL brand tokens override Stitch defaults wherever the two conflict.

### 15.6 Decision badges

| Decision | Badge text | UI guidance |
|---|---|---|
| Ready | Ready | Positive but not over-celebratory. |
| Ready with Conditions | Conditional | Highlight required approval or remediation before activation. |
| Blocked Pending Remediation | Blocked | Show top blockers and remediation immediately. |

Do not imply legal/compliance approval. Use "onboarding recommendation," not "certified compliant."

### 15.7 Minimum CLI interface

The CLI remains required for reproducibility:

```bash
python scripts/run_demo.py --candidate fixtures/candidates/safe_research_agent.json
python scripts/run_demo.py --candidate fixtures/candidates/prompt_injected_mcp_agent.json
```

The command prints:

- Candidate name.
- Workflow stage progress.
- Findings.
- Decision.
- Paths to generated artifacts.

### 15.8 Web UI implementation floor

The Web UI floor is:

- Deployed URL.
- HTTP basic auth with credentials in `JUDGE_RUNBOOK.md`.
- Test Agent Zoo gallery (8 fixtures: 5 must-ship + 3 stretch).
- Run workflow for at least 5 must-ship fixtures end-to-end.
- Render all core artifacts (Passport, AI BOM, Policy Envelope, Findings, Evidence Bundle).
- Download JSON/Markdown evidence bundle.
- Architecture page.
- Judge access page.
- Clean loading/error/blocked states.

A CLI-only final submission is not acceptable.

---

## 16. Repository strategy

### 16.1 Repository name

Preferred:

```text
clearpoint-onboarding-agent-challenge
```

### 16.2 Repository visibility

Start private with judge GitHub allowlist as canonical access pattern. Prepare a sanitized public branch in parallel in case rules require it.

### 16.3 Repo boundary

The challenge repo must not be the main ClearPoint Logic platform repo. It is isolated, disposable, and challenge-specific.

Allowed to include: this canonical spec; sanitized README; synthetic fixtures; demo policy pack; agent code; MCP tool code; Stitch design exports; local eval harness; deployment config; Devpost assets.

Not allowed to include: main CPL build pack; internal strategy brief source files; private roadmap or pricing spreadsheets; production signing key details; customer data; secrets or credentials; proprietary CAS/ECS tuning logic.

### 16.4 Proposed repo layout

```text
clearpoint-onboarding-agent-challenge/
  README.md
  README_PUBLIC.md
  PROPRIETARY.md
  .env.example
  .gitignore
  pyproject.toml

  docs/
    canonical/
      CPOA-GFS-AIAC-2026-CANONICAL.md
    architecture/
      ARCHITECTURE.md
      DEMO_FLOW.md
      GOOGLE_STACK_MAPPING.md
      ARCHITECTURE_DIAGRAM.md
    design/
      UI_CANONICAL.md
      STITCH_PIPELINE_NOTES.md
    submission/
      DEVPOST_DRAFT.md
      VIDEO_SCRIPT.md
      JUDGE_RUNBOOK.md
    security/
      SECURITY.md
      DATA_AND_IP_BOUNDARY.md
      MCP_SECURITY_BASELINE.md
      THREAT_MODEL.md

  design/
    stitch/
      landing/
      agents/
      runs/
      architecture/
      judge/

  corpus/
    nsa_mcp_csi/
    nist_ai_rmf_subset/
    eu_ai_act_articles/
    cpoa_policy_pack/
    cpoa_fixture_docs/

  agents/
    onboarding_orchestrator/
      agent.py
      prompts.py
      state.py
    discovery_agent/
      agent.py
    policy_agent/
      agent.py
    artifact_agent/
      agent.py
    validation_agent/
      agent.py
    evidence_agent/
      agent.py
    explanation_agent/
      agent.py

  mcp_servers/
    onboarding_tools/
      server.py
      tools.py
      schemas.py

  app/
    api/
      main.py
      routes.py
    web/
      package.json
      next.config.js
      tailwind.config.js
      src/
        app/
        components/
        lib/
        styles/

  cpoa/
    schemas/
      candidate_manifest.py
      discovery_report.py
      agent_passport.py
      ai_bom.py
      policy_envelope.py
      validation.py
      evidence.py
    services/
      scoring.py
      decisioning.py
      hashing.py
      exports.py
      grounding.py

  fixtures/
    candidates/
      safe_research_agent.json
      crm_write_missing_owner.json
      healthcare_phi_support_agent.json
      budget_runaway_research_agent.json
      prompt_injected_mcp_agent.json
      privileged_admin_agent.json
      unmaintained_mcp_server_agent.json
      grounding_required_policy_agent.json
    policy_packs/
      baseline_enterprise_v0_1.json
    registry/
      google_agent_registry_fixture.json

  tests/
    unit/
    integration/
    evals/
      expected_decisions.yaml
      run_evals.py
    security/
      test_mcp_auth.py
      test_mcp_replay.py
      test_prompt_injection_filter.py
      test_schema_validation.py

  scripts/
    run_demo.py
    export_bundle.py
    seed_fixtures.py
    seed_corpus.py

  infra/
    cloudrun/
      Dockerfile.api
      Dockerfile.mcp
      Dockerfile.web
      service.yaml
    agent_engine/
      deploy.yaml
    terraform_optional/

  .github/
    workflows/
      ci.yml
```

### 16.5 Branching and CI

- `main` protected.
- PR required before merge.
- CI runs lint, unit tests, schema validation, fixture evals, MCP security tests.
- Secret scanning enabled if available.
- `.env` ignored.

Branches:

- `main`
- `stream-a-logic`
- `stream-b-mcp-deploy`
- `stream-c-ui-submission`
- `submission-cut`
- `public-safe-export` (created from `submission-cut` if public repo is required).

Stream branches let Claude Code and Codex work in parallel without merge conflicts.

---

## 17. Security, privacy, and IP boundary

### 17.1 Secrets

No secrets in repo. Use environment variables:

```text
GOOGLE_CLOUD_PROJECT=
GOOGLE_CLOUD_LOCATION=
CPL_GEMINI_MODEL=
GOOGLE_APPLICATION_CREDENTIALS=
CPOA_STORAGE_MODE=local|firestore|cloudsql
CPOA_DEMO_SIGNATURE_MODE=stub|sigstore
CPOA_JUDGE_BASIC_AUTH_USER=
CPOA_JUDGE_BASIC_AUTH_PASS=
```

### 17.2 Data classification

All default fixtures are synthetic. No real customer data. No internal production telemetry. No private repository content from main CPL unless explicitly sanitized. Grounded corpus sources are all public (NSA CSI, NIST RMF, EU AI Act, CPOA's own demo content).

### 17.3 Prompt safety

- Do not expose hidden chain-of-thought.
- Do not store raw model reasoning in evidence bundles.
- Store structured rationale and trace summaries only.
- Treat candidate tool descriptions as untrusted data.
- Treat prompt-like content inside manifests as untrusted data.

### 17.4 Evidence honesty

The evidence bundle must include limitations:

- Challenge demo.
- Synthetic data unless otherwise stated.
- Demo signature unless real cryptographic signing is implemented.
- Not production Anchor certification.
- Not legal compliance advice.
- Implements onboarding gate only; continuous attestation is out of scope.

### 17.5 IP protection

Protect:

- Production CAS/ECS logic.
- Anchor signing infrastructure.
- Internal build pack and non-public canonicals.
- Commercially sensitive pricing and margin details.
- Customer-specific data or artifacts.
- Continuous Validation Agent Suite implementation details (Sentinel, Forensics, Drift, Red Team, Regulatory Watch).

Show:

- High-level concept of passport, policy, AI BOM, validation, evidence.
- Demo-safe readiness scoring.
- Google-native agent implementation.
- The workforce-parallel frame and HR-to-AI grid.

---

## 18. Evaluation plan

### 18.1 Local deterministic evals

Every fixture has an expected decision.

```yaml
safe_research_agent:
  expected_decision: Ready
  must_not_have_findings: [critical, high]

crm_write_missing_owner:
  expected_decision: Blocked Pending Remediation
  must_have_findings: [missing_owner]

healthcare_phi_support_agent:
  expected_decision: Ready with Conditions
  must_have_findings: [regulated_data_controls]

budget_runaway_research_agent:
  expected_decision: Ready with Conditions
  must_have_findings: [budget_boundary]

prompt_injected_mcp_agent:
  expected_decision: Blocked Pending Remediation
  must_have_findings: [prompt_injection]
```

### 18.2 Metrics

| Metric | Target |
|---|---:|
| Fixture decision accuracy (must-ship) | 5/5 |
| Artifact schema validation | 100% |
| Evidence event hash-chain validation | 100% |
| Required artifact export | 100% |
| Web UI fixture run success | 5/5 must-ship fixtures |
| MCP security tests | Pass auth, authorization, replay, schema, and prompt-injection tests |
| Grounding reference coverage | Policy/Evidence outputs include grounding refs for relevant findings |
| Local demo run time | <2 minutes |
| Video demo workflow | <4 minutes |

### 18.3 Optional Google-native evaluation

If available, use Agent Evaluation / Simulation / Observability to show:

- Trace for one successful candidate.
- Trace for one blocked candidate.
- Evaluation result for fixture set.
- Failure analysis from prompt-injection or missing-owner scenario.

If unavailable, local eval harness is sufficient.

---

## 19. Demo script

### 19.1 Four-minute video outline

**0:00–0:25 — The workforce frame (HR-to-AI grid)**

> "Every enterprise has a hiring process for humans: identity check, job description, declared qualifications, manager, personnel file. Agents are joining the workforce — and most organizations have no equivalent process for them.
>
> ClearPoint Onboarding Agent gives every new agent the same intake. A passport — its ID badge. A policy envelope — its job description. An AI BOM — its resume. An evidence bundle — its personnel file. Before it does any work."

Visual: side-by-side grid. Left column shows a human onboarding form (ID badge, job description, resume, manager, personnel file). Right column shows the AI agent equivalent (Passport, Policy Envelope, AI BOM, Owner, Evidence Bundle). Arrows connect each pair.

**0:25–0:55 — Architecture**

Show the Stitch-sourced Web UI, ADK orchestrator on Agent Engine / Agent Runtime, secure MCP server on Cloud Run, Gemini, grounding/RAG corpus, candidate manifest input, artifact and evidence outputs, Cloud Logging / Trace. Mention the six-subagent breakdown (Discovery, Grounded Policy, Artifact, Validation, Evidence, Explanation).

**0:55–2:15 — Successful onboarding (Use Case A)**

Open the Web UI, select `safe_research_agent` from the Test Agent Zoo, and run the workflow. Show discovery → grounded policy → passport, AI BOM, policy envelope generated → Onboarding Validation Suite passes → evidence bundle exported → **Ready** decision.

**2:15–3:20 — Blocked onboarding (Use Case E)**

Select `prompt_injected_mcp_agent` in the Web UI. Show findings, MCP-security rationale citing the NSA CSI excerpt in the grounded corpus, policy denial, **Blocked Pending Remediation** decision, evidence event trail. Emphasize fail-closed behavior.

**3:20–3:50 — Business case**

Tie to AI Workforce Management: security, compliance, finance, audit, ownership. Name the personas (AI Workforce Manager, Security/Compliance Officer, Agent Owner, Auditor) and what each gets from the workflow.

**3:50–4:00 — Continuous attestation flag and future path**

> "This is the onboarding gate. The next layer — continuous attestation, where governed agents validate the workforce-management layer itself — is the roadmap. ClearPoint Onboarding Agent is a Track 1 net-new agent today; a Meridian connector for Gemini Enterprise tomorrow."

### 19.2 Demo fixture order

1. `safe_research_agent.json` — Ready path
2. `prompt_injected_mcp_agent.json` — Blocked path
3. Optional quick flash of evidence bundle for `healthcare_phi_support_agent.json` (Conditional)

---

## 20. Implementation plan — parallel workstreams

Build runs as three parallel workstreams over nine days. Stream A owns logic/schemas/orchestration. Stream B owns MCP/security/grounding/deployment. Stream C owns UI/Stitch/submission. Each stream has its own branch (§16.5). Jared (lead) keeps cadence across all three; Claude Code and Codex execute within their assigned streams.

### 20.1 Workstream ownership

| Stream | Owner agent | Branch | Scope |
|---|---|---|---|
| A — Logic | Jared + Claude Code | `stream-a-logic` | Schemas (cross-walked); orchestrator; six subagents; Validation Suite; deterministic scoring; decision algorithm; evidence event chain; eight fixtures; local eval harness; CLI. |
| B — MCP / Security / Deploy | Jared + Claude Code | `stream-b-mcp-deploy` | HTTP MCP server; NSA baseline controls; MCP security tests; grounded corpus assembly; RAG (Agent Search or local); Agent Engine deployment; Cloud Run deployment of API + MCP + Web UI; observability. |
| C — UI / Submission | Jared + Codex + Stitch | `stream-c-ui-submission` | Stitch designs for all routes; Next.js + Tailwind implementation; CPL brand override; basic auth wiring; architecture page; judge runbook; demo video; Devpost draft; screenshots. |

Jared is shared across all three streams as integrator and decision-maker. Claude Code anchors Streams A and B (Python + infra). Codex anchors Stream C (TypeScript / Next.js / front-end polish). Stitch produces design source.

### 20.2 Day 0 — Decisions locked and repos seeded

- Send challenge-contact email to Dani (open questions in §23).
- Create private repo `clearpoint-onboarding-agent-challenge` with the four stream branches.
- Add this canonical spec at `docs/canonical/CPOA-GFS-AIAC-2026-CANONICAL.md`.
- Stream A (Claude Code): Scaffold ADK project, Python project, schemas directory.
- Stream B (Claude Code): Scaffold MCP server skeleton, Cloud Run Dockerfiles, GCP project setup.
- Stream C (Jared + Codex + Stitch): Start Stitch design iterations for landing, agents gallery, run timeline.

Exit criteria: Repo exists; four branches exist; Stitch first-pass designs for landing + agents gallery exist; ADK and MCP scaffolds boot locally.

### 20.3 Day 1 — Foundations

- Stream A: Pydantic schemas (cross-walked against CPM-MERIDIAN-CANONICAL §6 and CPL-CONNECTOR-CAPABILITY-MATRIX-CANONICAL §3 before writing). Hash helper. Canonical event serialization implemented and tested.
- Stream B: MCP server with auth, schema validation, trace/session/nonce metadata, structured logging. Begin NSA baseline implementation. Cloud Run service.yaml for API and MCP.
- Stream C: Stitch designs for `/runs/:run_id`, artifact panels, decision panel. Next.js project scaffolded with Tailwind + CPL brand tokens. Stitch code export pulled into `app/web/src` for landing and agents routes.

Exit criteria: Schemas pass tests; MCP server boots locally with auth and schema validation; Next.js dev server renders landing + agents from Stitch.

### 20.4 Day 2 — Discovery and Policy

- Stream A: `discovery_agent`, `policy_agent` subagents implemented. Discovery extracts identity/owner/purpose/runtime/models/tools/data/autonomy/budget. Policy maps discovery → envelope draft. First three must-ship fixtures (`safe_research_agent`, `crm_write_missing_owner`, `healthcare_phi_support_agent`).
- Stream B: Grounded corpus seeded from public sources (NSA MCP CSI, NIST AI RMF subset, EU AI Act articles, CPOA policy pack). Local retriever implemented. Attempt Agent Search / Vertex AI Search integration; document blocker if unavailable.
- Stream C: Stitch designs for policy, validation, evidence, architecture routes. Implement run timeline component. Wire up artifact tabs.

Exit criteria: Discovery and Policy produce expected output on `safe_research_agent`; corpus retriever returns grounded snippets with attribution; UI renders all four artifact tabs on a stub run.

### 20.5 Day 3 — Artifacts, Validation, Decision

- Stream A: `artifact_agent` produces Passport + AI BOM + Score + Approval Card. `validation_agent` runs OV-001 through OV-005. Decision algorithm with deterministic caps. Two more must-ship fixtures (`budget_runaway_research_agent`, `prompt_injected_mcp_agent`).
- Stream B: NSA MCP baseline controls completed (origin verification, RBAC, replay protection, output filtering, sandboxing, audit logging). MCP security tests in `tests/security`.
- Stream C: Decision panel + readiness score visualization. Evidence bundle download wired to API.

Exit criteria: All five must-ship fixtures route through orchestrator end-to-end and produce expected decisions; MCP security tests pass; UI renders decision badges correctly.

### 20.6 Day 4 — Evidence chain and Explanation

- Stream A: `evidence_agent` with hash-chained events per §11.8. Evidence bundle export (JSON + Markdown). `explanation_agent` produces workforce-language narratives and grounded citations.
- Stream B: First Agent Engine deployment attempt for orchestrator. If Agent Engine accessible, deploy and verify; otherwise document blocker and pivot orchestrator to Cloud Run with same API contract. Cloud Logging + trace IDs flowing.
- Stream C: Grounded source chips rendered in policy and evidence views. Architecture page populated with Google stack diagram. Judge access page draft.

Exit criteria: Evidence chain validates; bundle exports correctly; orchestrator deployed somewhere (Agent Engine or Cloud Run) with logs flowing; UI shows grounding sources on findings.

### 20.7 Day 5 — Integration and three stretch fixtures

- Stream A: Three stretch fixtures (`privileged_admin_agent`, `unmaintained_mcp_server_agent`, `grounding_required_policy_agent`) added. Eval harness with `expected_decisions.yaml` covering all eight. CLI demo polished.
- Stream B: Side-by-side grounded-vs-ungrounded comparison fixture (FR-084) wired in. MCP security checklist mapped to `docs/security/MCP_SECURITY_BASELINE.md`.
- Stream C: All required routes deployed to Cloud Run with basic auth. End-to-end run through `safe_research_agent` works from UI to deployed orchestrator.

Exit criteria: All eight fixtures pass expected decisions; end-to-end deployed run works; eval harness green; grounding comparison demonstrable in UI.

### 20.8 Day 6 — Hardening and judge surfaces

- Stream A: Re-run full eval suite. Fix any deterministic-scoring edge cases. Verify hash-chain validation across all fixtures.
- Stream B: Vulnerability scan on dependencies. Final Agent Engine vs Cloud Run decision documented. Threat model written.
- Stream C: Judge runbook complete (basic auth creds, fixture shortcuts, demo script, known limitations, architecture summary). Architecture diagram rendered. Accessibility pass (contrast, keyboard, focus, reduced motion).

Exit criteria: Eight-fixture eval green; threat model written; judge runbook complete; accessibility pass clean.

### 20.9 Day 7 — Video and Devpost

- Jared: Record demo video using §19.1 outline. Two fixtures shown in detail; one fixture flashed.
- Stream C (Codex): Capture screenshots from deployed UI. Finalize Devpost draft using §22. Compose submission package preview.
- Stream A (Claude Code): Run final eval pass on a clean container. Confirm CI green.

Exit criteria: Video recorded; Devpost draft ready; clean-clone test passes; CI green.

### 20.10 Day 8 — Submission hardening and dry run

- Clean clone of `submission-cut` branch on a fresh machine.
- Run local CLI demo.
- Run hosted UI demo end-to-end through all five must-ship fixtures.
- Verify no secrets, no build-pack content, no proprietary scoring weights leaked.
- Confirm public-safe export branch is ready if needed.
- Final cross-walk of §11 schemas against canonical sources; deltas documented inline.

Exit criteria: Clean clone runs locally; hosted demo runs through five fixtures end-to-end; all submission acceptance criteria in §21 verified.

### 20.11 Day 9 — Submit

- Submit Devpost package before June 5, 2026, 5:00 PM PT.
- Tag repo `v0.4-submission`.
- Archive deployed environment configuration for post-submission review.

---

## 21. Acceptance criteria for final submission

The submission is ready only when all are true:

1. Track 1 framing is explicit.
2. README states Meridian is not live and this is a net-new challenge agent.
3. README opens with the workforce-parallel frame, not a generic problem statement.
4. README includes the continuous-attestation flag as the post-onboarding roadmap.
5. ADK / Gemini / Stitch usage is demonstrable.
6. MCP-compatible tools are implemented via an actual HTTP MCP server interface.
7. MCP server passes the NSA-inspired security baseline tests for auth, authorization, schema validation, replay protection, output filtering, and audit logging.
8. Web UI is deployed and judge-usable behind HTTP basic auth (credentials in `JUDGE_RUNBOOK.md`).
9. Web UI includes Test Agent Zoo, run timeline, artifact panels, decision panel, evidence download, architecture page, and judge access page.
10. All eight fixtures (5 must-ship + 3 stretch) exist; all five must-ship pass expected decisions.
11. At least one fixture returns Ready.
12. At least one fixture returns Ready with Conditions.
13. At least one fixture returns Blocked Pending Remediation.
14. Agent Passport exports as JSON.
15. AI BOM exports as JSON.
16. Policy Envelope exports as JSON.
17. Validation findings export as JSON.
18. Evidence bundle exports as JSON and Markdown.
19. Evidence events are hash-chained per §11.8 canonical serialization.
20. Demo can be run locally from documented commands.
21. Hosted demo works end-to-end for all five must-ship fixtures.
22. No secrets are committed.
23. No private CPL build-pack material is committed.
24. Devpost copy is honest and polished.
25. Demo video is under time, opens with the workforce-parallel frame, and shows Ready, Conditional, and Blocked behavior.
26. Private/public repo requirement verified before final submission.
27. All schemas in §11 cross-walked against CPM-MERIDIAN-CANONICAL §6 and CPL-CONNECTOR-CAPABILITY-MATRIX-CANONICAL §3 with any deltas noted.
28. Grounded comparison example (FR-084) exists in the deployed UI and cites at least one specific public source (NSA CSI, NIST RMF, or EU AI Act).

---

## 22. Devpost draft content

### 22.1 Inspiration

AI agents are joining the enterprise workforce, and most organizations have no repeatable process to hire them. Humans get an identity, a job description, declared qualifications, a manager, and a personnel file before they do sensitive work. AI agents deserve the same discipline. ClearPoint Onboarding Agent treats agents as workforce, not tooling — and gives every new agent the same structured intake a human gets on day one.

### 22.2 What it does

ClearPoint Onboarding Agent inspects a candidate AI agent and generates the workforce-management package required before production use: Agent Passport (the agent's ID badge), Policy Envelope (its job description and scope of authority), AI BOM (its resume of models and dependencies), readiness score, Onboarding Validation Suite findings, approval card, and audit-ready evidence bundle (the personnel file that follows the agent forward).

### 22.3 How we built it

Built as a net-new ADK/Gemini multi-agent workflow with an HTTP MCP server exposing tools for candidate inspection, policy generation, artifact generation, validation, and evidence writing. Designed in Google Stitch and implemented in Next.js + Tailwind for the judge-facing Web UI. Deployed on Google Cloud with Agent Engine for the orchestrator (Cloud Run fallback documented), Cloud Run for the Web UI / API / MCP server, and Cloud Logging + Trace for observability. Grounding via the Google grounding stack with a local retrieval fallback. Designed to align with Google Agent Platform concepts — Agent Registry, Agent Identity, Agent Gateway, Agent Evaluation, Agent Observability — while remaining portable through a neutral Passport data model designed as v0.1 of public-facing workforce-management schemas. The submission demonstrates three Google products working together: ADK, Gemini, and Stitch.

### 22.4 Challenges we ran into

The hardest challenge was keeping scope honest: building a real, demoable agent-onboarding workflow without pretending to ship the entire AI Workforce Management platform. We narrowed to one production-shaped workflow — the onboarding gate — and used synthetic fixtures with explicit limitations throughout. The second hardest challenge was demonstrating grounded retrieval value authentically rather than as set-dressing; we solved that by curating a corpus of public regulatory and security guidance (NSA MCP CSI, NIST AI RMF, EU AI Act) and showing side-by-side grounded versus ungrounded outputs.

### 22.5 Accomplishments

- Net-new ADK/Gemini agent that onboards other agents into the AI workforce.
- Eight fixture agents across safe, risky, regulated, budget, prompt-injection, privileged-admin, unmaintained-MCP, and grounding-dependent scenarios.
- Automated Agent Passport, AI BOM, Policy Envelope, and Evidence Bundle generation with deterministic scoring and hash-chained evidence.
- NSA MCP Security Design Baseline implemented and tested.
- Fail-closed Onboarding Validation Suite.
- Vendor-neutral data model usable beyond Google Cloud.
- Google-aligned Web UI designed in Stitch.
- Clear path to Gemini Enterprise / Google Cloud Marketplace readiness.

### 22.6 What we learned

The next wave of agent platforms needs workforce-management agents, not just task agents. The same AI stack used to build autonomous systems can also help enterprises reason about whether those systems are ready to act. The most powerful framing is HR, not security — every stakeholder already understands what a passport, a job description, a resume, and a personnel file are for. And grounded retrieval over public regulatory text is where multi-agent value becomes visible: the grounded policy agent cites specific source sections that a single ungrounded prompt does not.

### 22.7 What's next

The onboarding gate is the start, not the end. ClearPoint Logic's differentiated thesis is *continuous attestation*: after onboarding, governed agents continuously validate the workforce-management layer itself, producing signed evidence routed through the same trust graph used to govern them. Post-challenge, ClearPoint Onboarding Agent becomes a candidate workflow inside Meridian — a Google-first, vendor-neutral workforce-management connector that onboards Gemini Enterprise agents, MCP servers, and third-party agents into one AI workforce. Continuous attestation, the Continuous Validation Agent Suite, and cross-vendor workforce governance are the next layers.

---

## 23. Open questions before build starts

**Day 0 escalation.** Send the challenge-contact email below on Day 0. If no answer arrives by noon Day 1, proceed under safe defaults and document assumptions in `docs/submission/JUDGE_RUNBOOK.md`.

| ID | Question | Owner | Required before | Status |
|---|---|---|---|---|
| CPOA-Q001 | Do official rules allow private repos shared with judges? | Jared / Dani | Day 1 repo creation | Open |
| CPOA-Q002 | Are ADK, Gemini, and MCP the mandatory technologies, or are additional technologies mandatory? | Jared / Dani | Day 1 scope lock | Open |
| CPOA-Q003 | Is Agent Engine / Agent Runtime available to challenge participants? | Build owner | Day 4 deployment | Open |
| CPOA-Q004 | Is Agent Registry API access available? | Build owner | Day 2 adapter design | Open |
| CPOA-Q005 | Can Track 1 submissions receive Gemini Enterprise / Marketplace follow-up opportunities? | Jared / Dani | Devpost wording | Open |
| CPOA-Q006 | Should the challenge repo live under the ClearPoint org or a founder-owned private repo? | Founders | Day 0 repo creation | Open |
| CPOA-Q007 | Which exact Gemini model should be used under challenge credits? | Build owner | Day 1 env setup | Open |
| CPOA-Q008 | Should video show UI or CLI-first workflow? | Founders | Day 7 polish | Resolved — UI-first per CPOA-D014 |
| CPOA-Q009 | Who is the named builder? | Founders | Day 0 | **Resolved — Jared + Claude Code + Codex in parallel streams (CPOA-D025)** |
| CPOA-Q010 | Is Agent Search / Vertex AI Search or RAG Engine available? | Build owner | Day 2 grounding design | Open |
| CPOA-Q011 | Cost burn within $500 credit budget? | Jared / Build owner | Day 5 mid-check | Monitor per CPOA-NFR-010 |
| CPOA-Q012 | Judge-access authentication mechanism? | Jared | Day 5 deployment | **Resolved — HTTP basic auth, credentials in JUDGE_RUNBOOK.md (CPOA-D026)** |

Suggested challenge-contact email (Day 0):

> Hi Dani — we're preparing a Track 1 net-new ADK/Gemini agent submission. A few quick rule clarifications: Are private GitHub repos allowed if judges are granted access? Is one project locked to one track, or can Track 1 projects be considered for Gemini Enterprise / Marketplace follow-up? Are Agent Registry, Agent Identity, Agent Gateway, Agent Engine / Agent Runtime, Agent Search, Agent Evaluation, and Agent Observability available to challenge participants, or should we use compatible fixtures/fallbacks where access is not enabled? Finally, can you confirm the exact mandatory technologies for Track 1 submissions?

---

## 24. Risks and mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Private repo not allowed | High | Maintain sanitized public-safe export branch from Day 0. |
| Agent Engine / Agent Registry access unavailable | Medium | Cloud Run fallback for orchestrator with same API contract; fixture-based registry compatibility. Document blocker in threat model. |
| Agent Search / RAG Engine access unavailable | Medium | Local retriever over corpus; same `grounding_refs` schema either way. |
| Scope creep into full Meridian | High | Keep product boundary fixed to onboarding workflow only. Stream owners reject scope expansion to other phases. |
| Overclaiming production readiness | High | Use explicit limitations in README, Devpost, and evidence bundle. |
| Overclaiming continuous attestation | High | Continuous attestation referenced only as future/roadmap; no claims that any Continuous Validation Suite agent is implemented. |
| Exposing proprietary IP | High | Do not import main build pack; use demo scoring and synthetic fixtures. |
| Demo too complex | Medium | Show two fixtures in video: Ready and Blocked. Flash Conditional briefly. |
| LLM nondeterminism affects evals | Low | Deterministic code computes score, caps, and final decision per §11.6; Gemini contributes summaries only. |
| Stream collisions on shared files | Medium | Stream branches isolate work; Jared owns merge conflicts at end of each day. |
| Stitch output diverges from CPL brand | Medium | Apply CPL brand tokens as Tailwind overrides on Day 1; review Stitch output every day before integrating. |
| Cost overrun on $500 credits | Medium | Monitor at Day 5; throttle eval frequency if burn exceeds 40%. |
| Schema drift from canonical | Medium | Day 1 cross-walk against CPM-MERIDIAN-CANONICAL §6 and CPL-CONNECTOR-CAPABILITY-MATRIX-CANONICAL §3; deltas justified inline. |
| MCP security scope too large | Medium | Implement NSA-inspired baseline with tests; simulated controls documented honestly. |
| Founder bandwidth as integrator | High | Jared is shared across all three streams as integrator-of-record; reserve 90 minutes/day for cross-stream sync and decisions. |

---

## 25. Glossary

**ADK** — Agent Development Kit. Google's agent development framework used for the challenge build.

**Agent Engine / Agent Runtime** — Google's managed runtime for ADK orchestrators. Primary deployment target for the CPOA orchestrator.

**Agent Passport** — A per-agent identity and workforce-management record. In the workforce-parallel frame, the agent's ID badge. In this challenge, a demo-safe artifact inspired by ClearPoint Anchor / Meridian architecture.

**AI BOM** — AI Bill of Materials. Structured inventory of models, prompts, tools, data sources, memory, runtime, and dependencies used by an agent. In the workforce-parallel frame, the agent's resume.

**Candidate agent** — The agent being inspected and onboarded by ClearPoint Onboarding Agent.

**ClearPoint Onboarding Agent (CPOA)** — The net-new Track 1 challenge agent specified in this document. The agent that performs onboarding. Not to be confused with the Agent Passport, which is the artifact the agent issues.

**Continuous Attestation** — ClearPoint Logic's canonical post-onboarding thesis: governed agents continuously validate the workforce-management layer itself. Implemented by the canonical Continuous Validation Agent Suite. **Out of scope for this challenge build** — referenced as the post-onboarding roadmap only.

**Continuous Validation Agent Suite** — The canonical CPL set of five post-onboarding agents (Sentinel, Forensics, Drift, Red Team, Regulatory Watch). Not implemented in this challenge.

**Evidence bundle** — Export containing Agent Passport, AI BOM, policy envelope, readiness score, validation findings, approval card, and evidence events. In the workforce-parallel frame, the agent's personnel file at hire.

**MCP** — Model Context Protocol. Used as the tool server protocol for candidate inspection, policy generation, validation, and evidence writing.

**Onboarding Validation Suite (OVS)** — Challenge-safe pre-deployment validation harness. Distinct from the canonical Continuous Validation Agent Suite.

**Passport Readiness Score** — Demo-only 0–100 score used for the challenge. Not production CAS/ECS.

**Policy envelope** — Runtime workforce-management boundary: tools, data, provider/model use, budget, memory, approval, and kill-switch rules. In the workforce-parallel frame, the agent's job description and scope of authority.

**Stitch** — Google's AI-powered UI design and code-generation tool. Source of the Web UI designs and starter code for CPOA's judge-facing review interface.

**Stream A / Stream B / Stream C** — The three parallel build workstreams per §20.1. A is logic, B is MCP/security/deploy, C is UI/submission.

**Track 1** — Google for Startups AI Agents Challenge track for building net-new agents.

---

## 26. Final canonical positioning sentence

> ClearPoint Onboarding Agent is a net-new ADK/Gemini agent that helps enterprises hire AI agents into the workforce by issuing a passport, AI BOM, policy envelope, validation record, approval card, and evidence bundle at the gate — with continuous attestation as the roadmap.

---

## 27. Implementation prompt

This section is the canonical context block handed to the coding agents (Claude Code and Codex) on Day 0. It is loaded into both sessions; each agent works only within its assigned workstream per §20.1.

### 27.1 Role and scope

You are implementing the ClearPoint Onboarding Agent (CPOA), a Track 1 submission for the Google for Startups AI Agents Challenge. You are working in an isolated challenge repo at `clearpoint-onboarding-agent-challenge`. You must not import, reference, or modify anything from the main ClearPoint Logic build pack. You must not implement any feature of the production Meridian, Anchor, or Agent Core platforms beyond what this spec authorizes.

The build runs as three parallel workstreams. Identify your assignment from §20.1 and work only within it. Coordinate cross-stream changes through Jared as integrator.

### 27.2 Authoritative source

CPOA-GFS-AIAC-2026-CANONICAL **v0.4** (this document) is your source of truth for the challenge build. When this document conflicts with other CPL canonicals, this document wins for the contest implementation. When you find a gap, file a question against the §23 Open Questions table and proceed under safe defaults documented in `docs/submission/JUDGE_RUNBOOK.md`.

### 27.3 Hard constraints

1. **Workforce framing.** Use workforce-parallel language (hire, passport, job description, resume, personnel file) consistently. Do not use "governance platform" or "governance agent" as standalone descriptors.
2. **No overclaim of continuous attestation.** Continuous attestation is the roadmap, not implemented. Reference only as future state.
3. **No overclaim of Anchor signing.** Use `demo_stub` signatures with explicit labels.
4. **No overclaim of production CAS/ECS.** Use Passport Readiness Score with the `not_production_cas_or_ecs: true` flag.
5. **Web UI is mandatory.** Build and deploy the judge-facing Web UI. Source designs from Google Stitch and export to Next.js + Tailwind. Apply CPL brand tokens as overrides.
6. **Stitch is the design pipeline.** Every required route originates from a Stitch design checked into `design/stitch/`.
7. **Schema canonicality.** All schemas in §11 cross-walked against CPM-MERIDIAN-CANONICAL §6 and CPL-CONNECTOR-CAPABILITY-MATRIX-CANONICAL §3 on Day 1 before implementation. Document any deltas inline.
8. **MCP server, not MCP-shaped local functions.** Tools must be exposed via an actual MCP server interface. HTTP MCP is the deployed target; stdio MCP is local-dev fallback only.
9. **NSA MCP security baseline.** Implement §12.6 controls or mark them explicitly simulated with tests/docs.
10. **Grounding/RAG.** Implement grounding via Agent Search / Vertex AI Search / RAG Engine if available; otherwise local retrieval fallback. Corpus contents per FR-080.
11. **Fail-closed.** If any workflow stage fails, the final decision must be Blocked Pending Remediation or Needs Manual Review.
12. **Deterministic gate decision.** Per §11.6, deterministic code computes score, caps, blockers, and final decision. Gemini contributes only summaries, rationale, and explanations.
13. **IP protection.** Do not import main CPL canonicals into the challenge repo. Do not import the build pack. Do not embed proprietary scoring weights.
14. **Stream discipline.** Work only within your assigned stream (§20.1). Cross-stream changes require Jared's integration step.

### 27.4 Build order

Follow §20 day-by-day parallel-workstream plan exactly. Send Day 0 question-resolution email, then proceed under safe defaults if no timely answer arrives. Do not begin Day 3 (artifacts/validation/decision) on Stream A before Day 2 (discovery/policy) is complete. Do not drop the Web UI; cut optional polish, advanced animations, or nonessential Agent Registry integration first.

### 27.5 Acceptance criteria

Apply §21 acceptance criteria as the gate. Submission is ready only when all 28 criteria are true.

### 27.6 When in doubt

When you encounter ambiguity, prefer the more conservative interpretation:

- Prefer narrower scope over broader scope.
- Prefer explicit limitations over implicit claims.
- Prefer canonical schemas over invented ones.
- Prefer fail-closed over fail-open.
- Prefer demo-honest labels over impressive-sounding labels.
- Prefer the deterministic code path over the LLM path for decisions.

### 27.7 What to escalate

Escalate to Jared (integrator) before proceeding if:

- A required Google API (Agent Engine, Agent Registry, Agent Search) is unavailable and the fallback materially weakens the demo.
- A canonical schema cross-walk reveals a delta that requires a CPM-MERIDIAN-CANONICAL amendment.
- A stream's daily exit criteria slip by more than 24 hours.
- Any acceptance criterion in §21 becomes infeasible within the window.
- Stitch output and CPL brand tokens conflict in a way that cannot be resolved by override.
- Credit burn exceeds 40% of $500 by Day 5.

---

*End of CPOA-GFS-AIAC-2026-CANONICAL v0.4 final.*
