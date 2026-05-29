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


# --- Compass: in-platform advisor -------------------------------------------

_COMPASS_INSTRUCTION = (
    "You are Compass, the in-platform advisor for the ClearPoint Workforce Agent — a platform "
    "that onboards and manages AI agents the way an enterprise hires and manages people. You "
    "help the user understand the current screen, interpret onboarding decisions, findings, "
    "scope (the agent's 'job description'), and the six-phase agent lifecycle (Discover, "
    "Onboard, Manage, Govern, Operate, Optimize).\n\n"
    "WRITE FOR A NON-TECHNICAL BUSINESS READER — an HR or operations manager, not an engineer. "
    "Use plain workforce language. Be warm, clear, and brief.\n\n"
    "NEVER expose internal technical details in your answer. Specifically, do NOT mention or "
    "print: web addresses or URLs; page routes or file paths (anything with a slash, e.g. "
    "'/runs/...'); run IDs, candidate IDs, or other machine identifiers; or internal "
    "infrastructure and product names (for example Cloud Run, Firestore, Cloud Trace, BigQuery, "
    "Vertex, Gemini, MCP, A2A, ADK, Kubernetes, gRPC). Refer to screens by their friendly names "
    "(Pre-Boarding, the agent's profile, Compliance, Architecture, Operate, Talent Development) "
    "and refer to an agent by its name, never its ID.\n\n"
    "Format: concise, well-structured Markdown — short paragraphs, **bold** for key terms, and "
    "bullet lists where they help. No headings, no code blocks, no backticks. Keep answers under "
    "~150 words. Ground every claim in the provided context facts. The decision, score, and "
    "findings are final and deterministic: never change or invent them."
)


def _compass_agent(model: str | None = None):  # pragma: no cover
    """A tool-less Gemini agent for a single Compass advisory turn."""
    from google.adk.agents import LlmAgent

    return LlmAgent(
        name="compass_agent",
        model=model or fast_model(),
        description="In-platform advisor for the ClearPoint Workforce Agent.",
        instruction=_COMPASS_INSTRUCTION,
    )


def compass_answer(message: str, facts: dict, model: str | None = None) -> str:  # pragma: no cover
    """Single live Gemini call: Compass answers a question grounded in the given facts."""
    if not llm_available():
        raise RuntimeError("Gemini/Vertex not configured (GOOGLE_GENAI_USE_VERTEXAI + project).")
    prompt = (
        "Answer the user's question for the current platform context. Use Markdown and stay "
        "under ~150 words. The context facts below are authoritative — do not contradict or "
        "restate them verbatim, synthesize a helpful answer.\n\nCONTEXT FACTS:\n"
        + json.dumps(facts)
        + "\n\nUSER QUESTION:\n"
        + message
    )
    return asyncio.run(_run_agent_async(_compass_agent(model), prompt))


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


async def _run_sequential_async(agent, message: str) -> dict:  # pragma: no cover
    """Walk the SequentialAgent end-to-end; return the ordered sub-agent transcript + final state."""
    from google.adk.runners import InMemoryRunner
    from google.genai import types

    runner = InMemoryRunner(agent=agent, app_name="cpoa")
    session = await runner.session_service.create_session(app_name="cpoa", user_id="judge")
    content = types.Content(role="user", parts=[types.Part(text=message)])
    transcript: list[dict] = []
    async for event in runner.run_async(user_id="judge", session_id=session.id,
                                         new_message=content):
        author = getattr(event, "author", None) or "unknown"
        text_parts: list[str] = []
        tool_calls: list[str] = []
        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    text_parts.append(part.text)
                if getattr(part, "function_call", None):
                    tool_calls.append(part.function_call.name)
                if getattr(part, "function_response", None):
                    tool_calls.append(f"{part.function_response.name}:result")
        if text_parts or tool_calls:
            transcript.append({
                "subagent": author,
                "text": " ".join(text_parts).strip() if text_parts else "",
                "tool_calls": tool_calls,
            })
    final_session = await runner.session_service.get_session(
        app_name="cpoa", user_id="judge", session_id=session.id
    )
    final_state = dict(final_session.state) if final_session and final_session.state else {}
    # Pull just the keyed sub-agent outputs (not internal scratch keys)
    keyed = {
        k: v for k, v in final_state.items()
        if k in {"discovery_report", "policy_envelope", "validation_run",
                 "artifacts", "evidence_bundle"}
    }
    return {"transcript": transcript, "final_state": keyed}


def run_sequential_adk_onboarding(manifest_dict: dict, model: str | None = None) -> dict:  # pragma: no cover
    """Run the explicit six-subagent SequentialAgent over the manifest; return the
    ordered subagent transcript + accumulated state.

    This exercises the real ADK multi-agent path — each sub-agent makes its own
    Gemini call and emits its keyed output. The decision remains deterministic
    (each sub-agent's tool calls into the deterministic engine functions); ADK
    is the orchestrator, not the decider.
    """
    if not llm_available():
        raise RuntimeError("Gemini/Vertex not configured (GOOGLE_GENAI_USE_VERTEXAI + project).")
    from agents.onboarding_orchestrator.agent import build_sequential_orchestrator

    agent = build_sequential_orchestrator(model or fast_model())
    message = (
        "Onboard this candidate agent step-by-step through the six-subagent pipeline. "
        "Each subagent must call its tool with the prior subagent's output from session "
        "state. Candidate manifest:\n" + json.dumps(manifest_dict)
    )
    return asyncio.run(_run_sequential_async(agent, message))
