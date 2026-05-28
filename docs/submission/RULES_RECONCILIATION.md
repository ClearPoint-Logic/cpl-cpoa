# Rules Reconciliation — official challenge rules vs. CPOA spec v0.4

**Purpose.** The canonical spec (`docs/canonical/CPOA-GFS-AIAC-2026-CANONICAL.md`) was written before
the official rules PDF was fully parsed. This document records where the **binding official rules**
override the spec. When this document conflicts with the spec, **the official rules win** (they are the
contractual terms of the contest).

Sources: *Google for Startups AI Agents Challenge — Official Eligibility and Rules* (15 pp.) and
*The Complete Resource Guide 2026* (8 pp.).

---

## Binding deltas (must be honored in the build)

| # | Topic | Spec v0.4 says | Official rules say | Action taken |
|---|---|---|---|---|
| 1 | **Demo video length** | "under four minutes"; 4-minute outline (§19, FR-064/065) | **"1–2 minute video… not longer than 2 minutes. If longer, only the first 2 minutes evaluated."** | `VIDEO_SCRIPT.md` re-cut to a **hard 2:00**: workforce frame (~0:20) → one Ready run → one Blocked run → 1-line continuous-attestation flag. FR-064 superseded. |
| 2 | **Code repository visibility** | "Start private with judge GitHub allowlist… prepare sanitized public branch *in case* required" (CPOA-D004, §16.2) | **"The code repository must be public to allow access for judging and testing."** (URL stays private from other startups via Devpost, but the repo must be judge-accessible.) | The **sanitized `public-safe-export` branch is now a primary deliverable**, not a contingency. IP-boundary work (§16.3/§17) is on the critical path. CPOA-Q001 resolved: plan for public. |
| 3 | **Gemini access path** | "challenge-approved Google Cloud route" (CPOA-D006) | **"Gemini on Google AI Studio is not available for credit usage."** Intelligence must be "Gemini API or a third-party LLM deployed exclusively through Vertex AI." | `.env` uses the **Vertex backend** (`GOOGLE_GENAI_USE_VERTEXAI=TRUE` + project/location). No AI Studio API key. CPOA-Q007 resolved: **`gemini-3.5-flash`** for narration (served in the Vertex **`global`** location — verified via live calls; it 404s in regional endpoints), `gemini-2.5-pro` configurable. |
| 4 | **Judging criteria (weights)** | Not specified | **Technical Implementation 30% · Business Case 30% · Innovation & Creativity 20% · Demo & Presentation 20%.** ADK usage explicitly scored under *both* Technical and Demo. | Prioritize a genuinely working ADK multi-agent core + the workforce business case (60% combined). The architecture diagram and an explicit "how we used ADK" section are required for the Demo 20%. |
| 5 | **A2A protocol** | Future-path only (§3.7) | A2A is **mandatory only for Track 3**, not Track 1. | Confirmed: A2A is out of scope for our Track 1 submission. The six-subagent design already satisfies "multi-agent." A2A remains optional stretch. |

## Confirmed / aligned (no change needed)

- **Track choice.** Track 1 (Build, Net-New) — correct. A2A/Marketplace mandates are Track 3 only.
- **New projects only.** "Must be newly created during the Contest Period… not a modification or
  extension of … existing work." The spec's framing ("net-new agent *inspired by* Meridian, not
  Meridian refactored", CPOA-D015) plus the no-build-pack-import IP boundary directly satisfies this.
- **Mandatory technologies.** Gemini (via Vertex) + ADK + Google Cloud deployment (Cloud Run / Agent
  Engine / GKE) — all in the spec.
- **Submission contents.** Text description (summary, tech, data sources, **architecture diagram**,
  learnings) + public repo URL + ≤2-min video + judge testing access with credentials — all covered
  by the spec's submission artifacts (CPOA-D023), with the video-length correction in delta #1.
- **Testing access.** "If private, include login credentials in testing instructions." → HTTP basic
  auth with creds in `JUDGE_RUNBOOK.md` (CPOA-D026) satisfies this.

## Key dates (official rules)

- **Submission deadline: June 5, 2026, 5:00 PM PT** (hard).
- Judging period and winner announcement follow in June (dates stated inconsistently across the rules
  doc; only the submission deadline gates our build).
- Today is the spec's **"Day 0"**; the 9-day plan (§20) maps exactly onto May 27 → June 5 with no slack.

## Open challenge questions still tracked (spec §23)

Resolve via Day-0 email to Dani; proceed under safe defaults if no timely answer:
Agent Engine availability (Q003), Agent Registry API (Q004), Vertex AI Search / RAG availability
(Q010), exact Gemini model under credits (Q007). All have documented fallbacks (Cloud Run, synthetic
fixtures, local retrieval), so none block the core build.
