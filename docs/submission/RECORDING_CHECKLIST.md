# Recording & Submission Checklist (Track 1)

Record-time actions from the demo reviews (Britton + Vilesh) that can't be "fixed in code."
Companion to `VIDEO_SCRIPT.md`. Code-fixable findings are already handled in PR #31.

## Before you hit record

- [ ] **Kill the cold-start tax.** Redeploy with warm instances:
      `CPOA_MIN_INSTANCES=1 bash infra/cloudrun/deploy.sh` (the deploy script now takes this
      lever; default stays 0 for cost). If you can't redeploy, hit the judge URL + an onboarding
      run + open Compass ~60s before recording so every Cloud Run service is warm.
- [ ] **Confirm the cut is ≤ 2:00.** Only the first 2:00 is evaluated (`VIDEO_SCRIPT.md` is built to this).
- [ ] **Vocabulary is locked** (see the note at the top of `VIDEO_SCRIPT.md`): four artifacts =
      Agent Passport / Policy Envelope / AI Bill of Materials / Evidence Bundle; lead with the six
      phase names, product names (Compass/Sentinel/Talent Development) as secondary color only.

## While recording

- [ ] **Open Compass from *inside* a run**, not from the gallery. The run page passes full run
      context to Compass (it answers grounded on that run); the global/gallery button has no run to
      ground on and will sound generic. (No code change — it already works this way.)
- [ ] **Put the architecture diagram on screen** for the closing beat (rubric criterion #4 names it;
      it shows 3 Google-stack mandates at once). `/architecture` renders the visual diagram + table.
- [ ] **Don't linger on the raw `*.run.app` hostname** on the Discover/Roster cards. It's the real
      endpoint (honest), just not pretty — keep the camera moving, or front it with a custom domain
      (see "Optional, infra" below).
- [ ] **Resolve the Optimize flag on-camera.** The lifecycle ends on a FLAGGED Talent-Development
      item by design — click **Complete item** to show closure rather than ending on an open flag.
      (We deliberately did *not* hide it in code: the flag → resolve beat shows governance working.)

## Two open decisions (your call)

- [ ] **A2A endpoint auth.** The Agent Card now advertises `basic` auth **only when judge creds are
      configured** (PR #31), so card and enforcement stay consistent. For a governance product the
      stronger posture is to actually enforce it: deploy the API with
      `CPOA_JUDGE_BASIC_AUTH_USER/PASS` set (the deploy script already does this) so `require_auth`
      enforces on `/a2a/v1/*`. Decide: enforce in prod, or leave the A2A surface intentionally open.
- [ ] **Grounding self-reference.** `cpoa-fixture-docs` appears among grounding sources alongside
      NIST / EU AI Act. It's **test-enforced** (`tests/integration/test_grounding.py`), so it's
      intentional. Only drop it if you want grounding to read as purely external authority — and
      update that test if you do.

## Optional, infra (not blocking)

- [ ] **Custom domain** in front of the `*.run.app` API/web hosts for a cleaner judge URL and to
      retire the exposed Cloud Run hostname.

## Parked — Track 3 only (not for the June 5 Track 1 submission)

- A2A **inbound** demo beat (another agent calls our onboarding skill and gets a signed verdict).
- Full **monetization / Marketplace-readiness** narrative. *(The buyer persona + one-line business
  model are already folded into `DEVPOST_DRAFT.md` for the Track 1 Business Case.)*
