"""Live ADK execution helpers (Gemini via Vertex). Gated by config.llm_available().

These make real model calls and are exercised at deploy/demo time, not in unit tests.
"""

from __future__ import annotations

import asyncio
import json

from agents.config import fast_model, llm_available
from cpoa.services.engine import OnboardingResult


async def _run_root_async(message: str, model: str | None = None) -> str:  # pragma: no cover
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    from agents.onboarding_orchestrator.agent import build_root_agent

    agent = build_root_agent(model or fast_model())
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


def run_adk_onboarding(manifest_dict: dict, model: str | None = None) -> str:  # pragma: no cover
    """Run the live ADK orchestrator over a candidate manifest; returns its narrative."""
    if not llm_available():
        raise RuntimeError(
            "Gemini/Vertex not configured. Set GOOGLE_GENAI_USE_VERTEXAI=TRUE and "
            "GOOGLE_CLOUD_PROJECT (and authenticate ADC) to run the live ADK path."
        )
    message = (
        "Onboard this candidate agent into the workforce and explain the result:\n"
        + json.dumps(manifest_dict)
    )
    return asyncio.run(_run_root_async(message, model))


def narrate_with_llm(result: OnboardingResult, model: str | None = None) -> str:  # pragma: no cover
    """Ask the Gemini explanation agent to narrate a completed onboarding result."""
    from agents.explanation import narrate_offline

    facts = narrate_offline(result)
    message = (
        "Explain this completed onboarding result in workforce language for a reviewer. "
        "Do not change the decision.\n" + json.dumps(facts)
    )
    return asyncio.run(_run_root_async(message, model))
