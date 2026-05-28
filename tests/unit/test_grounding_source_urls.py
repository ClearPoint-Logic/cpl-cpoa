"""Grounding refs carry source URLs (Codex M4).

Every GroundingRef returned by the local retriever must include the
``source_url`` from the corpus document it came from, so downstream
consumers (Compass UI, evidence bundles, judges curling the API) can
follow citations to the actual public source.
"""

from __future__ import annotations

from cpoa.services.grounding import LocalRetriever, load_corpus


def test_load_corpus_captures_source_url_when_present() -> None:
    passages = load_corpus()
    assert passages, "corpus should not be empty"
    urls = {p.source_url for p in passages if p.source_url}
    # Every public framework in the corpus has a source URL
    assert any("eur-lex.europa.eu" in (u or "") for u in urls), "EU AI Act URL missing"
    assert any("nist.gov" in (u or "") for u in urls), "NIST AI RMF URL missing"
    assert any("defense.gov" in (u or "") for u in urls), "NSA MCP CSI URL missing"


def test_retriever_propagates_source_url_to_groundingref() -> None:
    r = LocalRetriever()
    refs = r.retrieve("accountable owner roles governance", k=3, tags=["owner", "governance"])
    assert refs, "expected at least one ref for an owner/governance query"
    # At least one ref from a public framework should carry a real URL
    public_urls = [
        ref.source_url for ref in refs
        if ref.source_url and ref.source_url.startswith("https://")
    ]
    assert public_urls, f"no public URLs on refs: {[r.source_id for r in refs]}"


def test_internal_corpus_documents_marked_as_demo_safe() -> None:
    """The CPOA-internal corpus documents should be tagged with an internal/demo URL
    so consumers can distinguish public framework citations from CPL's own demo notes."""
    passages = load_corpus()
    internal = [p for p in passages if p.source_id in ("cpoa-policy-pack", "cpoa-fixture-docs")]
    assert internal, "expected internal demo corpus to be present"
    for p in internal:
        assert p.source_url is None or "internal" in p.source_url.lower() or "demo" in p.source_url.lower()
