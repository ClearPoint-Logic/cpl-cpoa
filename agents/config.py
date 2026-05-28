"""ADK/Gemini configuration (Vertex backend per challenge rules).

Gemini runs via Vertex AI (GOOGLE_GENAI_USE_VERTEXAI=TRUE) — AI Studio is not
eligible for challenge credits. Cost-light default model is gemini-2.5-flash.
"""

from __future__ import annotations

import os

DEFAULT_FAST_MODEL = "gemini-2.5-flash"
DEFAULT_PRO_MODEL = "gemini-2.5-pro"


def fast_model() -> str:
    return os.environ.get("CPL_GEMINI_MODEL_FAST") or DEFAULT_FAST_MODEL


def pro_model() -> str:
    return os.environ.get("CPL_GEMINI_MODEL") or DEFAULT_PRO_MODEL


def vertex_enabled() -> bool:
    return os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").upper() in ("1", "TRUE", "YES")


def llm_available() -> bool:
    """True when a live Gemini call could succeed (Vertex configured with a project)."""
    return vertex_enabled() and bool(os.environ.get("GOOGLE_CLOUD_PROJECT"))


def vertex_search_datastore() -> str | None:
    return os.environ.get("CPOA_VERTEX_SEARCH_DATASTORE") or None
