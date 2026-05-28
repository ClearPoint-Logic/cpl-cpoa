# User Journeys — ClearPoint Onboarding Agent

This document maps the named personas who interact with CPOA to the concrete
paths through the product, the artifacts they touch, and the success criterion
for each journey. Every journey runs against the deployed demo at
https://cpoa.clearpointlogic.com (basic-auth credentials in the Devpost
submission), against a local `pytest -q`, or both.

---

## Journey 1 — The Security / Compliance Officer (Sarah)

> **Persona.** Senior staff in InfoSec or Compliance. Technically literate
> across cloud, identity, and AI security. Cares about: provable controls,
> audit trail integrity, regulatory mapping.

**Pre-condition.** Sarah is evaluating CPOA as a candidate AI Workforce
Management onboarding gate for her enterprise.

**Steps.**
1. Open https://cpoa.clearpointlogic.com → land on the home page workforce frame.
2. Navigate to **Pre-Boarding** → click **`prompt_injected_mcp_agent`**.
3. Watch the run pipeline complete; decision lands as **Blocked**.
4. Open the **Background Check** tab → review the OV-004 prompt-injection finding.
5. Open the **Job Description** tab → see the quarantined tool in the policy.
6. Click the **NSA MCP CSI** grounding citation → confirm it points at a
   specific public source passage.
7. Open the **Personnel File** tab → download the Evidence Bundle as PDF.
8. Re-run the file through `python -c 'from cpoa.services.hashing import compute_bundle_hash; ...'`
   to recompute the hash; it matches `bundle_hash` exactly.

**Success.** Sarah confirms a Blocked decision is mechanically defensible:
the finding traces to a public source, the policy is the source of record
for the boundary, and the bundle is tamper-evident.

---

## Journey 2 — The AI Workforce Manager (Marcus)

> **Persona.** Director of an AI Workforce Management function. Coordinates
> agent intake across engineering, security, finance, and legal. Cares about:
> repeatable hiring decisions, ownership clarity, lifecycle visibility.

**Pre-condition.** Marcus is responsible for keeping the agent roster
governed end-to-end, not just at intake.

**Steps.**
1. Open **Workforce** → see three buckets: Discovered / Pre-Boarding / Onboarded.
2. Click **Re-scan directory** → confirm the live A2A scan returns expected counts.
3. Move to **Pre-Boarding** → run `safe_research_agent` → **Ready** (score 100).
4. Run `healthcare_phi_support_agent` → **Ready with Conditions** — review the
   regulated-data conditions in the Job Description tab.
5. Use the **Approval Card** field to confirm the human-in-the-loop hiring
   decision.
6. Back on **Workforce** → click an Onboarded agent → use the HR Console
   actions: **Place on leave** with a reason → verify the new event landed
   on the personnel file.
7. **Return from leave** with a note → verify the chain links correctly.

**Success.** Marcus produces an audit-ready hiring decision and exercises
ongoing lifecycle controls — all writing to one continuous personnel file.

---

## Journey 3 — The Finance / Ops Leader (Priya)

> **Persona.** CFO or VP of Operations. Holds the budget envelope for AI
> spend. Cares about: per-agent spend caps, breach handling, total cost.

**Pre-condition.** Priya needs to verify that every onboarded agent has an
explicit monthly cap with a defined on-breach behavior.

**Steps.**
1. Open **Pre-Boarding** → run `budget_runaway_research_agent`.
2. Open the **Background Check** tab → confirm OV-005 (budget posture) flagged.
3. Open the **Job Description** tab → confirm the `budget_boundary` block
   shows `monthly_usd` and an `on_breach` value (`pause`, `require_approval`,
   or `notify_only`).
4. Open **Talent Development** → confirm the budget-related conditions appear
   as development items the agent must address before promotion.

**Success.** Priya can point at the exact dollar cap, the breach policy, and
the development items required to clear them — for every agent on the roster.

---

## Journey 4 — The Auditor (Jordan)

> **Persona.** External or internal auditor. May be unfamiliar with the
> implementation but cares about: provable invariants, hash integrity,
> regulatory traceability.

**Pre-condition.** Jordan is auditing a specific past run from a sample
month.

**Steps.**
1. Open any run via its URL → review the **Multi-agent onboarding workflow**
   rail; each event is attributed to a subagent (discovery / policy /
   validation / artifacts / evidence / explanation) and stamped with a
   `previous_event_hash` linkage.
2. Download the Evidence Bundle as JSON → recompute the hash:
   ```python
   import json
   from cpoa.schemas import EvidenceBundle
   from cpoa.services.hashing import compute_bundle_hash
   bundle = EvidenceBundle(**json.load(open("safe-research-001.evidence.json")))
   assert bundle.bundle_hash == compute_bundle_hash(bundle)
   ```
3. Visit **Compass** → for any OV check Jordan is mapping, click the citation
   to confirm the cited corpus passage actually contains the supporting text.
4. Run `pytest tests/unit/test_bundle_hash_recompute.py -v` → confirm the
   recompute invariant holds for every fixture in CI.

**Success.** Jordan can prove the evidence chain is tamper-evident, the
control matrix is grounded in live corpus passages, and the recompute
invariant is mechanized in CI.

---

## Journey 5 — The Agent Owner (David)

> **Persona.** Engineering or product owner of a specific AI agent. Wants to
> bring his agent online safely and quickly. Cares about: fast feedback,
> clear remediation, automation-friendly APIs.

**Pre-condition.** David has a candidate manifest for a new agent he wants
to deploy. He prefers programmatic submission over UI clicking.

**Steps.**
1. Submit the manifest via A2A:
   ```bash
   curl -sS -u "$U:$P" -X POST https://cpoa.clearpointlogic.com/a2a/v1/message:send \
     -H "Content-Type: application/json" \
     -d '{"message":{"parts":[{"data":{"candidate_manifest":{...}}}]}}'
   ```
2. Inspect the response — an A2A task artifact with the decision, readiness
   score, passport, and evidence bundle hash.
3. If **Blocked** or **Ready with Conditions**, open the run in the UI to see
   the Findings (Background Check) and Conditions (Job Description) in
   full context.
4. Fix the manifest issues, re-submit, get **Ready**.
5. Confirm the agent appears in **Workforce → Onboarded** with the HR Console
   available.

**Success.** David goes from candidate manifest to Ready, programmatically,
in three iterations or fewer, with each iteration producing a hash-chained
audit record.

---

## Journey 6 — The Judge (You)

> **Persona.** Google for Startups AI Agents Challenge 2026 evaluator.
> Three to four minutes per submission; wants to see the product end-to-end.

**Pre-condition.** Hosted UI credentials provided in the Devpost submission's
testing-instructions field.

**Steps.**
1. Open https://cpoa.clearpointlogic.com → enter the basic-auth credentials.
2. **Workforce** → see the shadow-IT problem (Discovered bucket has unmanaged
   agents); click **Re-scan directory** to confirm the scan is real.
3. **Pre-Boarding** → run `safe_research_agent` → **Ready** in under a second.
4. Run `prompt_injected_mcp_agent` → **Blocked**, citing the NSA MCP source.
5. **Compass** → see the live control matrix mapping every CPOA control to
   real regulatory passages.
6. **Sentinel** → see fleet health with deterministic anomalies.
7. **Talent Dev** → see per-agent development plans on the autonomy ladder.
8. Download an Evidence Bundle as PDF — open it, see the hash chain, see the
   cited sources, see the deterministic decision rationale.

**Success.** Judge can verify, in ~3 minutes, that CPOA ships six phases of
the AI Workforce Management lifecycle on Google's agent platform with a
mechanically defensible audit trail.

---

## Local-only journeys (no deployment required)

- `python scripts/run_demo.py --fixture safe_research_agent` — full pipeline
- `python scripts/run_evals.py` — 5/5 must-ship, 8/8 overall
- `pytest -q` — 160+ tests across unit / integration / evals / security
- `ruff check .` — lint
- `cd app/web && npm run build` — matches the deployed build
