# Agent Engine deployment — reference

This directory documents how the **ADK orchestrator agent** in `agents/onboarding_orchestrator/agent.py`
is promoted from the Cloud Run runtime (which is what the contest demo runs)
to **Vertex AI Agent Engine** (the canonical primary per CPOA-D019 / NFR-015).

The current contest deploy uses Cloud Run for the orchestrator because:

1. The deterministic engine and the live ADK path both ship in the same FastAPI service (`cpoa-api` on Cloud Run), keeping the demo reproducible and credit-light.
2. Agent Engine access is enabled per-project; for the challenge build we kept the orchestrator in-process on Cloud Run so the judge eval works in a sub-second deterministic path **and** a 10–30 s live ADK path (POST `/api/runs/adk`) without any extra GCP setup.

Promoting to Agent Engine is a deployment-config change, not a code change. The
`build_root_agent()` and `build_sequential_orchestrator()` in
`agents/onboarding_orchestrator/agent.py` are Agent-Engine-ready as-is.

## Promotion steps (post-contest)

1. **Enable Agent Engine** for the project:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

2. **Stage the agent** as an `agent_engines` resource via the Vertex AI Python SDK:
   ```python
   from vertexai.agent_engines import AgentEngine, AdkApp
   from agents.onboarding_orchestrator.agent import build_root_agent

   AgentEngine.create(
       agent_engine=AdkApp(agent=build_root_agent()),
       display_name="ClearPoint Workforce Agent — onboarding orchestrator",
       requirements=["google-cloud-aiplatform[agent_engines]"],
       extra_packages=["./agents", "./cpoa"],
   )
   ```

3. **Switch the API path** from `agents.run.run_adk_onboarding()` (which uses
   `InMemoryRunner`) to an `AgentEngine` client that invokes the staged
   resource. Same orchestrator code, different runner.

4. **Grant the Cloud Run SA** `roles/aiplatform.user` on the Agent Engine
   resource so the deployed `cpoa-api` can invoke it.

## Why this isn't bundled as runnable code in the contest deploy

Agent Engine creation is an irreversible-ish action that consumes
project-scoped quota and an explicit service-account binding. The contest
demo runs deterministically against Cloud Run, which lets a judge reproduce
every decision in sub-millisecond time. The ADK orchestrator code (the
SequentialAgent + the LlmAgent + the prompts + the per-stage tools) is fully
in-tree and reviewable; the **runtime** is Cloud Run rather than Agent
Engine, with the documented promotion path above.

See `docs/architecture/ARCHITECTURE.md` Components table for the current
orchestrator runtime location, and `docs/security/THREAT_MODEL.md` for the
Cloud-Run-vs-Agent-Engine trust-boundary note.
