# Acceptance Criteria — §21 dry run

Status against the 28 final-submission criteria. ✅ done · ⏳ pending live verification ·
🧑 human/owner task.

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Track 1 framing explicit | ✅ | README, DEVPOST_DRAFT, UI |
| 2 | README: Meridian not live + net-new | ✅ | README "Honest scope" |
| 3 | README opens with workforce frame | ✅ | README, landing page |
| 4 | Continuous-attestation flag as roadmap | ✅ | README, footer, bundle limitations |
| 5 | ADK / Gemini / Stitch demonstrable | ✅ | `agents/` (ADK+Gemini); Stitch designs in `design/stitch/` drive the UI |
| 6 | MCP tools via real HTTP MCP server | ✅ | `mcp_servers/onboarding_tools/server.py` |
| 7 | MCP passes NSA baseline tests | ✅ | `tests/security/` (19 tests) |
| 8 | Web UI deployed behind basic auth | ✅ | https://cpoa-web-y4zowv3hva-uc.a.run.app (401→200 verified) |
| 9 | UI: zoo, timeline, artifacts, decision, evidence dl, architecture, judge | ✅ | `app/web/app/` routes |
| 10 | 8 fixtures exist; 5 must-ship pass | ✅ | `scripts/run_evals.py` → 5/5, 8/8 |
| 11 | ≥1 Ready | ✅ | safe_research_agent |
| 12 | ≥1 Ready with Conditions | ✅ | healthcare_phi_support_agent |
| 13 | ≥1 Blocked | ✅ | prompt_injected_mcp_agent |
| 14 | Passport exports JSON | ✅ | `exports.export_bundle`, API download |
| 15 | AI BOM exports JSON | ✅ | same |
| 16 | Policy Envelope exports JSON | ✅ | same |
| 17 | Validation findings export JSON | ✅ | same |
| 18 | Evidence bundle exports JSON + Markdown | ✅ | `exports.bundle_to_markdown`, API |
| 19 | Evidence events hash-chained (§11.8) | ✅ | `tests/unit/test_hashing.py` |
| 20 | Local demo from documented commands | ✅ | `scripts/run_demo.py`, README quickstart |
| 21 | Hosted demo works for 5 must-ship | ✅ | verified live: Ready/Blocked/Conditional/Conditional/Blocked |
| 22 | No secrets committed | ✅ | `.gitignore`, `.env.example` only |
| 23 | No private build-pack material | ✅ | `PROPRIETARY.md`, `DATA_AND_IP_BOUNDARY.md` |
| 24 | Devpost copy honest + polished | ✅ | `DEVPOST_DRAFT.md` |
| 25 | Demo video < time, opens workforce frame, shows R/C/B | 🧑 | `VIDEO_SCRIPT.md` (2:00); owner records |
| 26 | Private/public repo requirement verified | 🧑 | rules require a judge-accessible (public) repo; push `public-safe-export` |
| 27 | Schemas cross-walked vs canonical | ✅ | designed as v0.1 of Meridian schemas; deltas noted in code/spec |
| 28 | Grounded comparison in deployed UI citing a public source | ✅ | `/grounding` route (live) + policy grounding chips; cites NSA/NIST/EU sources |

## Remaining before submission (owner tasks)
- ~~Deploy verification (#8, #21)~~ — ✅ done; live at https://cpoa-web-y4zowv3hva-uc.a.run.app
- **JUDGE_RUNBOOK.md**: fill live URL + credentials (auto-generated at deploy).
- **Video** (#25): record per `VIDEO_SCRIPT.md` (hard 2:00).
- **Public repo** (#26): create the judge-accessible public repo / `public-safe-export` branch.
- **Optional polish**: Stitch design exports into `design/stitch/`; dedicated `/grounding` UI panel.
