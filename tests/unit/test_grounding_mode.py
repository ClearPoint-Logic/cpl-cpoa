"""Grounding mode resolution: env-driven retriever selection.

The live path must honor CPOA_GROUNDING_MODE so a deployment with Vertex AI
Search configured actually uses it; local fallback must remain deterministic.
"""

from __future__ import annotations

from cpoa.services import grounding


def test_configured_mode_defaults_to_local(monkeypatch) -> None:
    monkeypatch.delenv("CPOA_GROUNDING_MODE", raising=False)
    assert grounding.configured_mode() == "local"


def test_configured_mode_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("CPOA_GROUNDING_MODE", "vertex_ai_search")
    assert grounding.configured_mode() == "vertex_ai_search"


def test_configured_mode_empty_string_becomes_local(monkeypatch) -> None:
    monkeypatch.setenv("CPOA_GROUNDING_MODE", "")
    assert grounding.configured_mode() == "local"


def test_get_retriever_default_local(monkeypatch) -> None:
    monkeypatch.delenv("CPOA_GROUNDING_MODE", raising=False)
    r = grounding.get_retriever()
    assert r.mode == "local"


def test_get_retriever_vertex_falls_back_when_unconfigured(monkeypatch) -> None:
    """If the Vertex client cannot be constructed, the retriever silently
    falls back to local so the gate keeps running."""
    monkeypatch.setenv("CPOA_GROUNDING_MODE", "vertex_ai_search")
    r = grounding.get_retriever()
    # In CI / local dev there's no Discovery Engine datastore, so the import
    # path or constructor will fail and we get the local fallback.
    assert r.mode == "local"


def test_get_grounding_for_policy_uses_env(monkeypatch) -> None:
    """End-to-end: get_grounding_for_policy honors the env without passing a retriever."""
    from cpoa.loader import load_manifest_by_name
    from cpoa.services.discovery import run_discovery

    monkeypatch.setenv("CPOA_GROUNDING_MODE", "local")
    manifest = load_manifest_by_name("safe_research_agent")
    disc = run_discovery(manifest)
    refs = grounding.get_grounding_for_policy(manifest, disc)
    # Local corpus always returns at least one ref for this fixture
    assert len(refs) >= 1


def test_health_surfaces_grounding_and_storage_modes() -> None:
    """The /api/health endpoint must publish the actual modes for ops visibility."""
    from fastapi.testclient import TestClient

    from app.api.main import app

    client = TestClient(app)
    r = client.get("/api/health")
    body = r.json()
    assert body["status"] == "ok"
    assert "modes" in body
    assert "grounding" in body["modes"]
    assert "storage_active" in body["modes"]
    assert "signing" in body["modes"]
