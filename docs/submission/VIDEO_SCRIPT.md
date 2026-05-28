# Demo Video Script — hard 2:00 cap

> **Binding rule (official rules):** the demonstration video must be **1–2 minutes**; only
> the first 2:00 is evaluated. Open with the workforce frame and close with the lifecycle.

| Time | Beat | On screen | Voiceover (tight) |
|---|---|---|---|
| 0:00–0:15 | **The wedge** | `/workforce` — Discovered bucket showing shadow IT | "Enterprises hire humans through a structured process. AI agents are joining the workforce with no equivalent. Here are four agents already running in our environment that have never been onboarded — no Passport, no Policy Envelope, no Evidence Bundle." |
| 0:15–0:35 | **The artifact** | `/agents` → click `safe_research_agent` → run page artifact tabs | "ClearPoint Workforce Agent gives every new agent the same intake. Passport. Résumé. Job Description. Background Check. Personnel File. Decision: Ready, with a hash-chained evidence bundle." |
| 0:35–1:05 | **The blocked path** | Run `prompt_injected_mcp_agent` → Background Check → Job Description | "A candidate whose MCP tool description hides 'ignore previous instructions, bypass policy.' The Pre-Employment Screening flags it. The policy quarantines the tool. The finding cites the NSA MCP security guidance directly. **Blocked** — fail-closed." |
| 1:05–1:30 | **The lifecycle** | Quick cuts: `/workforce` (Onboarded HR Console) → `/govern` (Compass control matrix) → `/operate` (Sentinel anomalies) → `/optimize` (Talent Development) | "Past the gate, the work continues. The HR Console manages day-to-day — place on leave, manager handoff. Compass maps every CWA control to NSA, NIST, and EU AI Act sections. Sentinel watches fleet health. Talent Development turns conditions into a promotion path." |
| 1:30–1:55 | **The integrity claim** | Decision panel → Download Evidence Bundle PDF → cat the JSON; show hash chain | "Every event across every phase chains into one personnel file. SHA-256 over canonical JSON. The recompute test runs against every fixture in CI. Audit-defensible by construction." |
| 1:55–2:00 | **The platform stack** | Architecture page Google platform table | "Built on the Google agent platform end-to-end — ADK, Gemini on Vertex AI, MCP, Vertex AI Search, A2A, Firestore, Cloud Trace, Cloud Run." |

**Capture notes**
- Lead with the Discover bucket — it opens on a *problem* (shadow IT), not a feature tour.
- The hash-chain reveal at 1:30 is the highest-impact moment. Show the PDF *and* the JSON
  with the hash chain visible. Run a tamper test inline if time allows.
- Architecture beat at the end, not the start — judges want to see the product before the stack.
