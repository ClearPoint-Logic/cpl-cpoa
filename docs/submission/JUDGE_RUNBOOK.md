# Judge Runbook — ClearPoint Onboarding Agent

> Track 1 (Build, Net-New). The AI Workforce Management onboarding gate, built net-new on Google's
> agent platform (ADK, Gemini on Vertex AI, MCP, Vertex AI Search, Cloud Run, A2A). Net-new agent
> inspired by the ClearPoint Meridian architecture — not a claim that Meridian is live.

## Hosted access
- **Judge UI:** [https://cpoa.clearpointlogic.com](https://cpoa.clearpointlogic.com)
- **Login (HTTP basic auth):** credentials provided privately in the Devpost
  submission's testing-instructions field (not committed to this public repo).
- **API (direct):** behind the same hostname; identical basic-auth credentials.
- **A2A Agent Card:** `/.well-known/agent.json` (open for discovery — no auth required).
- No CLI required — every fixture runs from the **Pre-Boarding** roster.

## 3-minute evaluation path
1. Open the UI → you'll be prompted for the basic-auth credentials above.
2. **Home** shows the workforce frame (passport / job description / résumé / personnel file) and
   the Google platform stack.
3. **Pre-Boarding** → run **`safe_research_agent`** → **Ready** (score 100; clean evidence bundle).
4. Run **`prompt_injected_mcp_agent`** → **Blocked** — see the OV-004 prompt-injection finding in
   the **Background Check** tab, the quarantined tool in the **Job Description** tab, and the
   grounded NSA MCP source citation; fail-closed.
5. Run **`healthcare_phi_support_agent`** → **Ready with Conditions** (regulated-data controls).
6. On any run: open the **artifact tabs** — **Passport** (ID badge), **Résumé** (AI BOM),
   **Job Description** (Policy Envelope), **Background Check** (Validation findings),
   **Personnel File** (Evidence Bundle) — and **download** the bundle (JSON / Markdown / PDF).
7. **Architecture** and **Judge Access** pages summarize the Google platform mapping and the
   honest-scope limitations.

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
- **ADK multi-agent:** the run timeline attributes each stage to a subagent (discovery → policy →
  validation → artifacts → evidence → decision).
- **Deterministic gate:** score, caps, blockers, and decision are computed in code from §11
  schemas; Gemini 3.5 Flash on Vertex AI narrates.
- **Secure MCP:** NSA MCP security baseline (auth, RBAC, integrity, replay, output filtering,
  audit) — verified by 19 security tests in `tests/security/`.
- **Vertex AI Search grounding:** policy and evidence cite specific public sources;
  `/grounding` shows ungrounded-vs-grounded side by side.
- **A2A interoperability:** Agent Card at `/.well-known/agent.json`; tasks at
  `/a2a/v1/message:send`.
- **Firestore persistence + Cloud Trace observability:** runs survive scale-to-zero; spans flow
  alongside the SHA-256 hash-chained evidence log.
- **Honest scope:** demo-stub signatures, demonstration-grade score, onboarding gate only —
  stated in the footer and every evidence bundle.

## Known limitations
See the Judge Access page in the UI and `docs/security/THREAT_MODEL.md`. The orchestrator runs on
Cloud Run (Agent Engine is the documented primary per CPOA-D019 / NFR-015); signatures are
demo-only; continuous attestation is the AI Workforce Management roadmap.
