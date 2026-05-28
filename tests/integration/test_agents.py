"""ADK agent layer (§9.3) — construction + tools + offline narration, no live calls."""

from __future__ import annotations

from agents import adk_tools
from agents.explanation import narrate_offline
from agents.onboarding_orchestrator.agent import (
    build_root_agent,
    build_sequential_orchestrator,
    root_agent,
)
from cpoa.loader import load_manifest_by_name
from cpoa.services import engine


def test_root_agent_builds_with_two_tools():
    agent = build_root_agent()
    assert agent.name == "onboarding_orchestrator"
    assert len(agent.tools) == 2


def test_module_level_root_agent_present_for_agent_engine():
    assert root_agent.name == "onboarding_orchestrator"


def test_sequential_orchestrator_mirrors_six_subagents():
    seq = build_sequential_orchestrator()
    names = [sa.name for sa in seq.sub_agents]
    assert names == [
        "discovery_agent", "policy_agent", "validation_agent",
        "artifact_agent", "evidence_agent", "explanation_agent",
    ]


def test_onboard_tool_runs_deterministic_pipeline():
    out = adk_tools.onboard_candidate_agent(load_manifest_by_name("safe_research_agent").model_dump())
    assert out["decision"] == "Ready"
    assert out["passport_readiness_score"] >= 80
    assert out["evidence_bundle_hash"].startswith("sha256:")


def test_lookup_grounding_tool_cites_nsa():
    out = adk_tools.lookup_grounding("prompt injection in a tool description")
    assert out["sources"]
    assert any(s["source_id"].startswith("nsa-mcp-csi") for s in out["sources"])


def test_narrate_offline_uses_workforce_frame():
    result = engine.onboard(load_manifest_by_name("prompt_injected_mcp_agent"))
    narrative = narrate_offline(result)
    assert narrative["decision"] == "Blocked Pending Remediation"
    assert narrative["source"] == "deterministic"
    assert any("ID badge" in line for line in narrative["workforce_lines"])
    assert narrative["findings"]
