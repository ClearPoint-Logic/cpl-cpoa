# Judge Runbook — ClearPoint Onboarding Agent

> Track 1 (Build, Net-New). The first six phases of AI Workforce Management — Discover, Onboard,
> Manage, Govern, Operate, Optimize — shipped end-to-end on Google's agent platform
> (ADK, Gemini on Vertex AI, MCP, Vertex AI Search, A2A, Firestore, Cloud Trace, Cloud Run).

## Hosted access
- **Judge UI:** [https://cpoa.clearpointlogic.com](https://cpoa.clearpointlogic.com)
- **Login (HTTP basic auth):** credentials are provided privately in the Devpost submission's
  testing-instructions field (not committed to this public repo).
- **A2A Agent Card:** [`/.well-known/agent.json`](https://cpoa.clearpointlogic.com/.well-known/agent.json)
  is open and unauthenticated (A2A discovery convention).
- **Health probe:** [`/api/health`](https://cpoa.clearpointlogic.com/api/health) is open and
  publishes the live runtime modes (storage / grounding / signing).
- No CLI required — every fixture runs from the **Pre-Boarding** roster.

## 4-minute evaluation path

1. **Workforce** tab → the live census. Three buckets:
   - **Discovered** — shadow-IT agents found via a real HTTPS scan of A2A Agent Cards
   - **Pre-Boarding** — candidates awaiting the gate
   - **Onboarded** — governed agents with HR Console action buttons inline

2. **Pre-Boarding** tab → run **`safe_research_agent`** → **Ready** (score 100; clean evidence
   bundle). Open the tabs: Passport · Résumé (AI BOM) · Job Description (Policy) · Background
   Check (OVS findings) · Personnel File (hash-chained evidence; download as JSON / Markdown / PDF).

3. Run **`prompt_injected_mcp_agent`** → **Blocked** — see the OV-004 prompt-injection finding,
   the quarantined tool in the Job Description tab, and the grounded NSA MCP source citation;
   fail-closed.

4. Run **`healthcare_phi_support_agent`** → **Ready with Conditions** (regulated-data controls).

5. **Compass** tab → the live control matrix. Every CPOA control (OV-001..005, MCP NSA baseline,
   hash-chained evidence) mapped to specific NSA MCP CSI / NIST AI RMF / EU AI Act passages.
   Citations resolve **live** against the same corpus the grounded policy agent uses.

6. **Sentinel** tab → fleet health across the active roster. Deterministic anomaly detection
   over real signals (onboarding outcome + HR Console event log).

7. **Talent Dev** tab → per-agent career-development plans. Open conditions become development
   items; the autonomy ladder (L0_observe → L5_high_impact_autonomous) is the promotion track.

## Run it locally (reproducible, no cloud)

```bash
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_demo.py --fixture safe_research_agent
python scripts/run_demo.py --fixture prompt_injected_mcp_agent
python scripts/run_evals.py          # 5/5 must-ship, 8/8 all
pytest -q                            # full suite (160+ tests, incl. security + bundle-hash)
```

## What to look for

- **Six lifecycle phases on one personnel file.** Discover findings, Onboard events, Manage
  actions, and Operate anomalies all chain into the same hash-chained record per agent.
- **ADK multi-agent:** the run timeline attributes each onboarding stage to a subagent
  (discovery → policy → validation → artifacts → evidence → decision).
- **Deterministic gate:** score, caps, blockers, and decision are computed in code from §11
  schemas; Gemini 3.5 Flash on Vertex AI narrates only.
- **Bundle-hash integrity:** the recompute test runs against every fixture in CI; the
  `bundle_hash` is verifiable.
- **Secure MCP:** NSA MCP security baseline (auth, RBAC, integrity, replay, output filtering,
  audit) — 19 security tests in `tests/security/`.
- **Vertex AI Search grounding:** policy and evidence cite specific public sources; `/grounding`
  shows ungrounded-vs-grounded side by side. The mode is published live at `/api/health`.
- **A2A interoperability:** open Agent Card at `/.well-known/agent.json`; tasks at
  `/a2a/v1/message:send`.
- **Firestore persistence + Cloud Trace observability:** runs survive scale-to-zero; spans flow
  alongside the SHA-256 hash-chained evidence log.
- **Production security headers:** HSTS, CSP, X-Frame-Options, Permissions-Policy,
  Referrer-Policy — visible in any browser inspector.

## Known limitations

See the Judge Access page in the UI. The orchestrator runs on Cloud Run; signatures use the
`local_hmac` mode by default (a real HMAC, not a placeholder), with a `kms` mode flag ready for
Cloud KMS asymmetric signing in a customer deployment. Continuous attestation across every
running interaction (the seventh AI Workforce Management phase) is the documented roadmap.
