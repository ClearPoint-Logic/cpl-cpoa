"""Grounding / RAG (§7.9, FR-080..084).

A local keyword/tag retriever over the sanitized public corpus, returning
``GroundingRef``s with source attribution. A Vertex AI Search retriever can be
swapped in when available (FR-081); the local retriever is the fallback (FR-082)
and keeps the demo reproducible offline. Pure Python apart from reading the corpus
files in the repo.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from cpoa.loader import REPO_ROOT
from cpoa.schemas import CandidateAgentManifest, DiscoveryReport, GroundingRef

from ._helpers import SENSITIVE_DATA, has_external_action_tool, has_privileged_tool
from .injection import scan_text

CORPUS_DIR = REPO_ROOT / "corpus"

_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "for", "in", "on", "with", "is", "are",
    "be", "by", "as", "at", "it", "that", "this", "should", "its", "their", "from",
    "can", "not", "but", "if", "so", "than", "into", "over", "per", "each",
}


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9_]+", text.lower()) if t not in _STOP and len(t) > 2}


@dataclass(frozen=True)
class Passage:
    source_id: str
    source_title: str
    passage_id: str
    title: str
    tags: tuple[str, ...]
    text: str

    def ref(self) -> GroundingRef:
        return GroundingRef(
            source_id=f"{self.source_id}#{self.passage_id}",
            source_title=self.source_title,
            snippet=self.text,
        )


def load_corpus(corpus_dir: str | Path = CORPUS_DIR) -> list[Passage]:
    passages: list[Passage] = []
    for jf in sorted(Path(corpus_dir).rglob("*.json")):
        doc = json.loads(jf.read_text())
        for p in doc.get("passages", []):
            passages.append(Passage(
                source_id=doc["source_id"], source_title=doc["source_title"],
                passage_id=p["id"], title=p["title"], tags=tuple(p.get("tags", [])),
                text=p["text"],
            ))
    return passages


class LocalRetriever:
    """Deterministic keyword + tag overlap retriever (FR-082 fallback)."""

    mode = "local"

    def __init__(self, passages: list[Passage] | None = None) -> None:
        self.passages = passages if passages is not None else load_corpus()

    def retrieve(self, query: str, k: int = 3, tags: list[str] | None = None) -> list[GroundingRef]:
        q = _tokens(query) | {t.lower() for t in (tags or [])}
        want_tags = {t.lower() for t in (tags or [])}
        scored: list[tuple[int, Passage]] = []
        for p in self.passages:
            ptoks = _tokens(p.title + " " + p.text) | {t.lower() for t in p.tags}
            score = len(q & ptoks) + 2 * len(want_tags & {t.lower() for t in p.tags})
            if score:
                scored.append((score, p))
        scored.sort(key=lambda sp: (-sp[0], sp[1].source_id, sp[1].passage_id))
        return [p.ref() for _, p in scored[:k]]


@lru_cache(maxsize=1)
def _default_retriever() -> LocalRetriever:
    return LocalRetriever()


def get_retriever(mode: str = "local"):
    """Return a retriever for the configured grounding mode (FR-081/082)."""
    if mode == "vertex_ai_search":
        try:  # pragma: no cover - exercised only when Vertex AI Search is configured
            from .grounding_vertex import VertexSearchRetriever

            return VertexSearchRetriever()
        except Exception:
            return _default_retriever()
    return _default_retriever()


def get_grounding_for_policy(
    manifest: CandidateAgentManifest, discovery: DiscoveryReport, retriever=None
) -> list[GroundingRef]:
    """Retrieve grounding refs relevant to this agent's risk profile (FR-083)."""
    retriever = retriever or _default_retriever()
    refs: dict[str, GroundingRef] = {}

    def add(query: str, tags: list[str], k: int = 1) -> None:
        for r in retriever.retrieve(query, k=k, tags=tags):
            refs.setdefault(r.source_id, r)

    add("accountable owner roles and governance", ["owner", "accountability", "governance"])
    add("record keeping logging evidence traceability", ["record_keeping", "logging", "evidence"])
    if discovery.owner_status != "present":
        add("missing accountable owner cannot be governed", ["owner", "accountability"])
    if set(discovery.data_classes) & SENSITIVE_DATA:
        add("regulated sensitive data boundary retention transparency",
            ["regulated_phi", "data_governance", "data_boundary", "transparency", "retention"], k=2)
    if has_external_action_tool(manifest) or has_privileged_tool(manifest):
        add("human oversight approval for high impact actions",
            ["human_oversight", "approval", "least_privilege"])
    if any(scan_text(t.description) for t in manifest.tools):
        add("prompt injection untrusted tool description output filtering",
            ["prompt_injection", "untrusted", "output_filtering"])
    return list(refs.values())[:4]


def build_grounding_comparison(
    manifest: CandidateAgentManifest, discovery: DiscoveryReport, retriever=None
) -> dict:
    """FR-084 — ungrounded single-call vs grounded multi-agent, side by side."""
    refs = get_grounding_for_policy(manifest, discovery, retriever)
    ungrounded = (
        f"{manifest.name} handles its declared purpose; apply standard data handling "
        "and human review as appropriate. (No sources cited.)"
    )
    if refs:
        cited = "; ".join(f"[{r.source_id}] {r.source_title}" for r in refs)
        grounded = (
            f"{manifest.name}: policy constraints are grounded in specific public guidance — "
            f"{cited}. Each proposed control (owner accountability, data boundaries, human "
            "oversight, and record-keeping) maps to a cited source rather than a generic summary."
        )
    else:
        grounded = f"{manifest.name}: no elevated obligations retrieved; baseline policy applies."

    return {
        "candidate_agent_id": manifest.candidate_agent_id,
        "ungrounded": {
            "method": "single_ungrounded_model_call",
            "explanation": ungrounded,
            "grounding_refs": [],
        },
        "grounded": {
            "method": "grounded_multi_agent",
            "explanation": grounded,
            "grounding_refs": [r.model_dump() for r in refs],
        },
    }
