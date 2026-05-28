"""Grounding / RAG tests (§7.9, FR-080..084)."""

from __future__ import annotations

from cpoa.loader import load_manifest_by_name
from cpoa.services import engine
from cpoa.services.discovery import run_discovery
from cpoa.services.grounding import (
    LocalRetriever,
    build_grounding_comparison,
    load_corpus,
)

REQUIRED_SOURCES = {"nsa-mcp-csi", "nist-ai-rmf", "eu-ai-act", "cpoa-policy-pack", "cpoa-fixture-docs"}


def test_corpus_loads_all_public_sources():
    passages = load_corpus()
    assert REQUIRED_SOURCES <= {p.source_id for p in passages}
    assert len(passages) >= 20


def test_retriever_finds_injection_guidance_from_nsa():
    refs = LocalRetriever().retrieve("instruction-like text in a tool description",
                                     tags=["prompt_injection", "output_filtering"])
    assert refs
    assert any(r.source_id.startswith("nsa-mcp-csi") for r in refs)


def test_retriever_finds_owner_governance_guidance():
    refs = LocalRetriever().retrieve("accountable owner", tags=["owner", "accountability"])
    assert any(r.source_id.startswith("nist-ai-rmf") for r in refs)


def test_healthcare_policy_carries_grounding_refs():
    result = engine.onboard(load_manifest_by_name("healthcare_phi_support_agent"))
    assert result.policy.grounding_refs, "regulated-data agent should have grounded policy refs"
    ids = " ".join(r.source_id for r in result.policy.grounding_refs)
    assert "eu-ai-act" in ids or "nist-ai-rmf" in ids


def test_grounded_vs_ungrounded_comparison_fr084():
    manifest = load_manifest_by_name("grounding_required_policy_agent")
    cmp = build_grounding_comparison(manifest, run_discovery(manifest))
    assert cmp["ungrounded"]["grounding_refs"] == []
    assert len(cmp["grounded"]["grounding_refs"]) >= 1
    # the grounded explanation names at least one specific public source
    assert any(
        src in cmp["grounded"]["explanation"]
        for src in ("eu-ai-act", "nist-ai-rmf", "nsa-mcp-csi")
    )
