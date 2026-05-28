# Judge Runbook — ClearPoint Onboarding Agent

> Track 1 (Build, Net-New). Net-new ADK + Gemini multi-agent system. Net-new agent inspired by the
> ClearPoint Meridian architecture — not a claim that Meridian is live.

## Hosted access
- **Judge UI:** https://cpoa-web-y4zowv3hva-uc.a.run.app
- **Login (HTTP basic auth):** `judge` / `MLcdaYGa9XcHihAu`
- **API (direct):** https://cpoa-api-y4zowv3hva-uc.a.run.app (same basic-auth credentials)
- No CLI required — run everything from the **Test Agent Zoo**.

## 3-minute evaluation path
1. Open the UI → you'll be prompted for the basic-auth credentials above.
2. **Home** shows the workforce frame (passport / job description / résumé / personnel file).
3. **Agent Zoo** → run **`safe_research_agent`** → **Ready** (score 100; clean evidence bundle).
4. Run **`prompt_injected_mcp_agent`** → **Blocked** — see the OV-004 prompt-injection finding, the
   quarantined tool in the Policy tab, and the grounded NSA MCP source chip; fail-closed.
5. Run **`healthcare_phi_support_agent`** → **Ready with Conditions** (regulated-data controls).
6. On any run: open the **artifact tabs** (Passport / AI BOM / Policy / Findings / Evidence) and
   **download** the evidence bundle (JSON / Markdown).
7. **Architecture** and **Judge Access** pages summarize the Google stack and limitations.

## Run it locally (reproducible, no cloud)
```bash
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_demo.py --fixture safe_research_agent
python scripts/run_demo.py --fixture prompt_injected_mcp_agent
python scripts/run_evals.py          # 5/5 must-ship, 8/8 all
pytest -q                            # full suite incl. security
```

## What to look for
- **ADK multi-agent**: the run timeline attributes each stage to a subagent (discovery → policy →
  validation → artifacts → evidence → decision).
- **Deterministic gate**: score, caps, and decision are computed in code; Gemini narrates.
- **Secure MCP**: NSA baseline (auth/RBAC/integrity/replay/output-filter/audit) — `tests/security/`.
- **Grounding**: policy/evidence cite specific public sources; `/api/grounding-comparison/<fixture>`
  shows ungrounded-vs-grounded side by side.
- **Honest scope**: demo-stub signatures, demo-only score, onboarding gate only — stated in the
  footer and every evidence bundle.

## Known limitations
See the Judge Access page in the UI and `docs/security/THREAT_MODEL.md`. Orchestrator runs on Cloud
Run (Agent Engine is the documented primary per CPOA-D019/NFR-015); signatures are demo-only;
continuous attestation is roadmap.
