"""Live ADK execution helpers (Gemini via Vertex). Gated by config.llm_available().

These make real model calls and are exercised at deploy/demo time, not in unit tests.
"""

from __future__ import annotations

import asyncio
import json

from agents.config import fast_model, llm_available
from cpoa.services.engine import OnboardingResult


async def _run_agent_async(agent, message: str) -> str:  # pragma: no cover
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    runner = InMemoryRunner(agent=agent, app_name="cpoa")
    session = await runner.session_service.create_session(app_name="cpoa", user_id="judge")
    content = types.Content(role="user", parts=[types.Part(text=message)])
    final_text = ""
    async for event in runner.run_async(user_id="judge", session_id=session.id,
                                         new_message=content):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    final_text = part.text
    return final_text


def _explanation_agent(model: str | None = None):  # pragma: no cover
    """A tool-less Gemini agent for a single clean narration call (cheap, reliable)."""
    from google.adk.agents import LlmAgent

    from agents import prompts

    return LlmAgent(
        name="explanation_agent",
        model=model or fast_model(),
        description="Narrates a completed onboarding result in workforce language.",
        instruction=prompts.EXPLANATION_INSTRUCTION,
    )


def narrate_facts(facts: dict, model: str | None = None) -> str:  # pragma: no cover
    """Single live Gemini call: narrate the provided (deterministic) facts. Decision is fixed."""
    if not llm_available():
        raise RuntimeError("Gemini/Vertex not configured (GOOGLE_GENAI_USE_VERTEXAI + project).")
    message = (
        "Explain this completed onboarding result in workforce language for a reviewer in 4-6 "
        "sentences. Do NOT change the decision, score, or findings — they are final.\n"
        + json.dumps(facts)
    )
    return asyncio.run(_run_agent_async(_explanation_agent(model), message))


def narrate_with_llm(result: OnboardingResult, model: str | None = None) -> str:  # pragma: no cover
    from agents.explanation import narrate_offline

    return narrate_facts(narrate_offline(result), model)


def run_adk_onboarding(manifest_dict: dict, model: str | None = None) -> str:  # pragma: no cover
    """Run the full live ADK orchestrator over a candidate manifest; returns its narrative."""
    if not llm_available():
        raise RuntimeError("Gemini/Vertex not configured (GOOGLE_GENAI_USE_VERTEXAI + project).")
    from agents.onboarding_orchestrator.agent import build_root_agent

    message = (
        "Onboard this candidate agent into the workforce and explain the result:\n"
        + json.dumps(manifest_dict)
    )
    return asyncio.run(_run_agent_async(build_root_agent(model or fast_model()), message))
