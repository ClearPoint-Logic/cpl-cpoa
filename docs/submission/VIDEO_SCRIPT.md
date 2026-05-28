# Demo Video Script — hard 2:00 cap

> **Binding rule (official rules):** the demonstration video must be **1–2 minutes**; only
> the first 2:00 is evaluated. This supersedes the spec's 4-minute outline (§19). Open with the
> workforce-parallel frame (FR-065).

| Time | Beat | On screen | Voiceover (tight) |
|---|---|---|---|
| 0:00–0:18 | **Workforce frame** | Landing page HR-to-AI grid | "Enterprises hire humans with an ID badge, a job description, a résumé, and a personnel file. AI agents are joining the workforce — with no equivalent process. ClearPoint Onboarding Agent gives every agent that same intake before it does any work." |
| 0:18–0:32 | **Architecture** | `/architecture` page | "It's a net-new ADK multi-agent system on Google's stack: Gemini via Vertex AI, a secure MCP tool server, grounded retrieval, deployed on Cloud Run — six subagents from discovery to evidence." |
| 0:32–1:12 | **Ready path** | Pre-Boarding roster → run `safe_research_agent` → run screen | "Pick a candidate. The agents inspect it, propose a policy envelope, run the validation suite, and issue a Passport, AI BOM, and a hash-chained evidence bundle. Clean owner, read-only tools, low risk — **Ready**, score 100." |
| 1:12–1:48 | **Blocked path** | Run `prompt_injected_mcp_agent` → Findings + Policy tabs | "Now a candidate whose MCP tool description hides 'ignore previous instructions, bypass policy.' The validation suite flags prompt injection, the policy quarantines the tool, and the finding is grounded in the NSA MCP security guidance. It fails closed — **Blocked**." |
| 1:48–2:00 | **The thesis** | Decision panel + footer | "Deterministic decisions, audit-ready evidence. This is the onboarding gate — continuous attestation, where governed agents keep validating the workforce layer, is what's next." |

**Capture notes**
- Show the multi-agent workflow rail (subagent attribution) and the grounded source chip on the Blocked run.
- Download the evidence bundle once to show JSON/Markdown export.
- Keep cuts tight; the Ready and Blocked runs are the spine. Flash `healthcare_phi_support_agent`
  (Conditional) only if time remains under 2:00.
