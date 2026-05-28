"""Grounding resilience: a Vertex Search outage must not 500 the gate.

A transient Discovery Engine failure should silently degrade to the local
corpus retriever so the onboarding API stays available.
"""

from __future__ import annotations

from cpoa.loader import load_manifest_by_name
from cpoa.schemas import GroundingRef
from cpoa.services import grounding
from cpoa.services.discovery import run_discovery


class _ExplodingRetriever:
    mode = "vertex_ai_search"

    def __init__(self) -> None:
        self.calls = 0

    def retrieve(self, query: str, k: int = 3, tags: list[str] | None = None) -> list[GroundingRef]:
        self.calls += 1
        raise RuntimeError("simulated Vertex Search 500")


def test_get_grounding_for_policy_falls_back_on_retriever_exception() -> None:
    """When the active retriever raises, the function must return the
    local-corpus results rather than propagating the exception."""
    manifest = load_manifest_by_name("safe_research_agent")
    disc = run_discovery(manifest)
    exploder = _ExplodingRetriever()
    refs = grounding.get_grounding_for_policy(manifest, disc, retriever=exploder)
    # Exploder called at least once; some refs were returned (from the local fallback)
    assert exploder.calls >= 1
    assert len(refs) >= 1
    # Refs should look like real local-corpus refs
    for ref in refs:
        assert ref.source_id
        assert ref.source_title
