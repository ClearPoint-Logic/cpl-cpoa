"""ADK agent definitions (§9.3).

`root_agent` is the working live orchestrator: a Gemini LlmAgent that calls the
deterministic onboarding tool and narrates the result in workforce language. The
explicit six-subagent `SequentialAgent` (build_sequential_orchestrator) mirrors
§9.3 for the architecture story and Agent Engine deployment. Agent construction
makes no network calls; Gemini is only invoked when an agent is actually run.
"""

from __future__ import annotations

from google.adk.agents import LlmAgent, SequentialAgent

from agents import adk_tools, prompts
from agents.config import fast_model


def build_explanation_agent(model: str | None = None) -> LlmAgent:
    return LlmAgent(
        name="explanation_agent",
        model=model or fast_model(),
        description="Explains the onboarding outcome in workforce language and cites grounded sources.",
        instruction=prompts.EXPLANATION_INSTRUCTION,
        tools=[adk_tools.lookup_grounding],
    )


def build_root_agent(model: str | None = None) -> LlmAgent:
    """The default live orchestrator: one deterministic tool + grounding, then narrate."""
    return LlmAgent(
        name="onboarding_orchestrator",
        model=model or fast_model(),
        description="ClearPoint Onboarding Agent — safely onboards AI agents into the workforce.",
        instruction=prompts.ROOT_INSTRUCTION,
        tools=[adk_tools.onboard_candidate_agent, adk_tools.lookup_grounding],
    )


def build_sequential_orchestrator(model: str | None = None) -> SequentialAgent:
    """Explicit six-stage multi-agent decomposition (§9.3), deterministic order."""
    model = model or fast_model()
    discovery = LlmAgent(name="discovery_agent", model=model,
                         description="Normalizes the candidate manifest into a discovery report.",
                         instruction=prompts.DISCOVERY_INSTRUCTION,
                         tools=[adk_tools.inspect_candidate_agent], output_key="discovery_report")
    policy = LlmAgent(name="policy_agent", model=model,
                      description="Proposes the grounded policy envelope (job description).",
                      instruction=prompts.POLICY_INSTRUCTION,
                      tools=[adk_tools.generate_policy_envelope], output_key="policy_envelope")
    validation = LlmAgent(name="validation_agent", model=model,
                          description="Runs the Onboarding Validation Suite OV-001..005.",
                          instruction=prompts.VALIDATION_INSTRUCTION,
                          tools=[adk_tools.run_validation], output_key="validation_run")
    artifact = LlmAgent(name="artifact_agent", model=model,
                        description="Generates Passport, AI BOM, Readiness Score, Approval Card.",
                        instruction=prompts.ARTIFACT_INSTRUCTION,
                        tools=[adk_tools.generate_passport_artifacts], output_key="artifacts")
    evidence = LlmAgent(name="evidence_agent", model=model,
                        description="Assembles the hash-chained evidence bundle (personnel file).",
                        instruction=prompts.EVIDENCE_INSTRUCTION,
                        tools=[adk_tools.assemble_evidence_bundle], output_key="evidence_bundle")
    explanation = LlmAgent(name="explanation_agent", model=model,
                           description="Narrates the outcome in workforce language with citations.",
                           instruction=prompts.EXPLANATION_STAGE_INSTRUCTION,
                           tools=[adk_tools.lookup_grounding])
    return SequentialAgent(
        name="onboarding_orchestrator_sequential",
        description="Discovery → Policy → Validation → Artifacts → Evidence → Explanation.",
        sub_agents=[discovery, policy, validation, artifact, evidence, explanation],
    )


# Module-level root agent for `adk` CLI / Agent Engine discovery.
root_agent = build_root_agent()
