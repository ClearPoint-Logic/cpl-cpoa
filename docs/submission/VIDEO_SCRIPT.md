# Demo Video Script — hard 2:00 cap

> **Binding rule (official rules):** the demonstration video must be **1–2 minutes**; only
> the first 2:00 is evaluated. Open with the workforce frame and close with the lifecycle.

> **Vocabulary (locked — keep consistent across video, Devpost, and the diagram):** the four
> artifacts are the **Agent Passport**, **Policy Envelope**, **AI Bill of Materials**, and
> **Evidence Bundle**. Lead with the six **phases** — Discover · Onboard · Manage · Govern ·
> Operate · Optimize — as the primary names; product/menu names (Hire, Compass, Sentinel,
> Talent Development) are secondary color, never the primary label.

| Time | Beat | On screen | Voiceover (tight) |
|---|---|---|---|
| 0:00–0:15 | **The wedge** | `/workforce` — Discovered bucket showing shadow IT | "Enterprises hire humans through a structured process. AI agents are joining the workforce with no equivalent. Here are four agents already running in our environment that have never been onboarded — no Agent Passport, no Policy Envelope, no AI Bill of Materials, no Evidence Bundle." |
| 0:15–0:35 | **The artifact** | `/agents` → click `safe_research_agent` → run page artifact tabs | "ClearPoint Workforce Agent issues every new agent the four things a human hire gets: an Agent Passport for identity, a Policy Envelope for its job description, an AI Bill of Materials for its résumé of models and tools, and an Evidence Bundle for its personnel file. Decision: Ready — with the whole bundle hash-chained." |
| 0:35–1:05 | **The blocked path** | Run `prompt_injected_mcp_agent` → Background Check → Job Description | "A candidate whose MCP tool description hides 'ignore previous instructions, bypass policy.' The Pre-Employment Screening flags it. The policy quarantines the tool. The finding cites the NSA MCP security guidance directly. **Blocked** — fail-closed." |
| 1:05–1:30 | **The lifecycle** | Quick cuts: `/workforce` (Onboarded HR Console) → `/govern` (Compass control matrix) → `/operate` (Sentinel anomalies) → `/optimize` (Talent Development) | "Past the gate, the work continues across four more phases. Manage runs day-to-day in the HR Console — place on leave, manager handoff. Govern maps every control to NSA, NIST, and EU AI Act sections. Operate watches fleet health. Optimize turns open conditions into an autonomy-ladder promotion path." |
| 1:30–1:55 | **The integrity claim** | Decision panel → Download Evidence Bundle PDF → cat the JSON; show hash chain | "Every event across every phase chains into one personnel file. SHA-256 over canonical JSON. The recompute test runs against every fixture in CI. Audit-defensible by construction." |
| 1:55–2:00 | **The platform stack** | Architecture page Google platform table | "Built on the Google agent platform end-to-end — ADK, Gemini on Vertex AI, MCP, Vertex AI Search, A2A, Firestore, Cloud Trace, Cloud Run." |

**Capture notes**
- Lead with the Discover bucket — it opens on a *problem* (shadow IT), not a feature tour.
- The hash-chain reveal at 1:30 is the highest-impact moment. Show the PDF *and* the JSON
  with the hash chain visible. Run a tamper test inline if time allows.
- Architecture beat at the end, not the start — judges want to see the product before the stack.
