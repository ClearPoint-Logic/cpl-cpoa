# Security overview

- **Secrets:** none in the repo. Configuration via environment variables; see `.env.example`.
  `.env`, key files, and credentials are git-ignored.
- **MCP server:** hardened to the NSA MCP Security Design Baseline — see
  [`MCP_SECURITY_BASELINE.md`](MCP_SECURITY_BASELINE.md). Controls are tested in `tests/security/`.
- **Judge access:** HTTP basic auth gates the deployed UI and API (credentials in
  `../submission/JUDGE_RUNBOOK.md`).
- **Evidence integrity:** SHA-256 hash-chained events (§11.8); any mismatch blocks a Ready decision.
- **Fail-closed:** if any stage fails, the decision is Blocked Pending Remediation (§10.3).
- **Threat model:** [`THREAT_MODEL.md`](THREAT_MODEL.md).
- **Dependencies:** pinned in `requirements.txt` / `app/web/package-lock.json`; enable secret scanning
  and Dependabot on the repository host.
- **Reporting:** this is a challenge demo; for production concerns contact ClearPoint Logic.
