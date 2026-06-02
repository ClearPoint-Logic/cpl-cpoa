# CLAUDE.md

@AGENTS.md

ClearPoint CPOA's agent operating instructions live in `AGENTS.md`; read it first. This file exists so Claude Code sessions resolve the same instructions.

<!-- BEGIN CLEARPOINT LOGIC CLAUDE AGENTIC ADDENDUM -->
## Claude Code Addendum

Start by reading `AGENTS.md`, then the Linear issue and the CPL Linear operating model in `clearpointlogic/docs/CPL-LINEAR-SOURCE-OF-TRUTH.md` when available.

Claude-specific workflow:
- Use Linear cycles as the execution cadence, milestones as phase/wave/release structure, and blocked-by edges as dependency order.
- Preserve human-owned agent delegation. An agent can contribute, but the human assignee remains accountable for high-risk completion.
- Use plan mode before production, billing, auth/security, data migration, DNS, credential, permissions, external integration, MCP-mutating, or destructive changes.
- Preserve the suggestion-first Linear workflow. Propose labels, assignee, status, project, cycle, estimate, and related links before applying unless the operator explicitly asks.
- Use Code Intelligence or repo search to cite likely files before broad implementation. Code Intelligence is enabled for CPL's canonical GitHub/code-access surface first.
- Use only the existing Agent MCP allowlist from this repo context: GitHub, Slack, and Sentry. Do not enable new MCP servers, broader repo access, or external connectors without explicit approval.
- Final handoff must include Linear issue, branch/PR, files changed, validation run, tests skipped, remaining risk, and next owner action.
<!-- END CLEARPOINT LOGIC CLAUDE AGENTIC ADDENDUM -->
