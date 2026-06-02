# AGENTS.md - ClearPoint CPOA

Agent operating instructions for the `cpl-cpoa` repo.

Read `README.md`, `CONTRIBUTING.md`, deployment docs, and the Linear issue before making changes. Preserve existing Python, app, agent, MCP, and infrastructure boundaries discovered in those files.

<!-- BEGIN CLEARPOINT LOGIC LINEAR AGENTIC OPERATING CONTRACT -->
## ClearPoint Logic Linear Agentic Operating Contract

Last updated: 2026-06-02

Linear is the source of truth for work state. Canonical specs and repo docs remain the source of truth for product scope and architecture. Before work, read the Linear issue, comments, project or initiative context, labels, linked PRs/diffs, attachments, relevant repo docs, and the CPL Linear operating model in `clearpointlogic/docs/CPL-LINEAR-SOURCE-OF-TRUTH.md` when available.

Operating rules:
- Use native Linear cycles as the execution cadence. Default to the current 2-week team cycle for active implementation/review work. Cycles are focus and accountability, not product scope or dependency order.
- Use project milestones for phase, wave, release, and launch-gate structure. Use blocked-by edges for predecessor/successor dependencies.
- Keep one human accountable. Linear/Codex/Claude/other agents may be delegated contributors, but the human assignee owns completion, approval, and risk acceptance.
- Use Code Intelligence for repo-aware answers and cite repo/file paths, PRs, commits, tests, skipped checks, and confidence. Code Intelligence is enabled for CPL's canonical GitHub/code-access surface first.
- Suggest before applying changes to labels, assignee, priority, project, cycle, estimate, related/duplicate links, or status unless the operator explicitly asks for mutation.
- Ask for explicit human approval before production, billing, auth/security, DNS, credential, destructive data, permissions, external integration, customer-impacting, or MCP-powered mutating actions.
- Triage Intelligence and agent automations may enrich issues, draft comments/checklists, investigate likely code paths, and propose property changes. Low-risk auto-apply is allowed only when templates or deterministic rules make the result unambiguous.
- Agent MCP is enabled in admin allowlist mode for GitHub, Slack, and Sentry. Datadog/Better Stack are not active unless installed and explicitly allowlisted; Stripe and production-adjacent servers require documented read/write scope and approval rules.
- Use `Needs Human Review` for ambiguous or risky decisions and `Needs Handover` when context must transfer before another owner or agent can continue. Clear either only after human acceptance or a complete handoff.
- Treat Linear Asks and Customer Requests as structured intake, not permission for risky action. Email Asks and intake templates are enabled; Slack Asks requires OAuth authorization before it is active. Customer Requests should rank real customer impact without inventing demand, and CPL/internal domains are excluded from customer creation.
- Draft weekly portfolio/project updates in Linear first with health, progress, blockers, risks, next actions, and asks; broadcast only through approved Slack channels.

Active Linear Agent skills:
- Weekly Portfolio Health Review
- Cycle Risk Scan
- Agent-Ready Issue Audit
- Handover Completeness Check
- Release Gate Review
- Canon Drift Reconciliation
- Production Change Approval Brief
- Customer/Ask Impact Review
- Agent Delegation Review
- MCP Access Review

Local workflow:
1. Start from the Linear issue identifier and create a branch that includes it when possible.
2. Confirm the issue is agent-ready. If the goal, acceptance criteria, repo paths, approval boundary, or validation plan is missing, propose the missing context instead of guessing.
3. Keep implementation scoped and cite files/tests in updates.
4. Keep Linear current when status changes, PRs open/merge, scope changes, validation completes, or human review is needed.
5. Before handoff or closure, include issue ID, branch/PR, files changed, validation run, tests skipped, remaining risk, and next owner action.

Team routing for this repo: ClearPoint Ops / OPS is the default routing owner for CPOA operations-agent and workplace automation work; route security-sensitive work to ClearPoint SecOps / SECOPS and shared platform substrate to ClearPoint Anchor Core / CPC. High-risk changes include MCP server behavior, credentials, deployment, customer/internal data handling, automation writes, and any agent action that mutates external systems.
<!-- END CLEARPOINT LOGIC LINEAR AGENTIC OPERATING CONTRACT -->
