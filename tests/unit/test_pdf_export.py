"""PDF evidence-bundle export tests.

Generates a real PDF for every fixture and verifies the bytes look like a
valid PDF document. Catches regressions in the rendering path that the
JSON/Markdown exports wouldn't surface.
"""

from __future__ import annotations

import pytest

from cpoa.loader import list_fixture_names, load_manifest_by_name
from cpoa.services import engine
from cpoa.services.pdf_export import _ascii, bundle_to_pdf


def test_ascii_helper_handles_none() -> None:
    assert _ascii(None) == ""


def test_ascii_helper_normalizes_common_punctuation() -> None:
    """Codex L2: Unicode punctuation we transliterate to ASCII *before* the
    latin-1 fallback, so judges' copy-pasted content with em-dashes / smart
    quotes / ellipses renders cleanly instead of '?' placeholders."""
    result = _ascii("café — résumé “quoted” it’s 1…2…3")
    assert "?" not in result, f"no '?' placeholders expected, got: {result!r}"
    assert "café" in result and "résumé" in result  # latin-1 accents survive
    assert "-" in result  # em-dash -> ASCII hyphen
    assert '"quoted"' in result  # curly quotes -> straight
    assert "it's" in result  # right single quote -> apostrophe
    assert "1...2...3" in result  # ellipsis -> three dots


def test_ascii_helper_still_replaces_truly_non_latin_scripts() -> None:
    """Non-Latin scripts (CJK, Cyrillic, emoji) still fall through to '?' —
    the punctuation map only covers Western punctuation we can transliterate."""
    result = _ascii("привет 你好 🎉")
    assert "?" in result  # latin-1 can't encode these, replace is fine


@pytest.mark.parametrize("fixture_name", list_fixture_names())
def test_bundle_to_pdf_produces_valid_pdf_bytes(fixture_name: str) -> None:
    manifest = load_manifest_by_name(fixture_name)
    result = engine.onboard(manifest)
    pdf_bytes = bundle_to_pdf(result.bundle)
    # PDF files always start with %PDF-
    assert pdf_bytes.startswith(b"%PDF-"), f"not a PDF document for {fixture_name}"
    # And end with %%EOF
    assert b"%%EOF" in pdf_bytes[-100:], f"missing %%EOF for {fixture_name}"
    # Reasonable size — at least a few KB of metadata + content
    assert len(pdf_bytes) > 1000


def test_bundle_to_pdf_renders_blocked_fixture() -> None:
    """A Blocked fixture's PDF rendering exercises the findings branch."""
    manifest = load_manifest_by_name("prompt_injected_mcp_agent")
    result = engine.onboard(manifest)
    pdf_bytes = bundle_to_pdf(result.bundle)
    # PDF text is FlateDecode-compressed in the stream; we verify the file
    # is structurally valid and large enough to include the findings section.
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1500  # Blocked bundles have more content than clean ones


def test_bundle_to_pdf_renders_ready_clean_path() -> None:
    """A Ready fixture exercises the 'no findings' branch."""
    manifest = load_manifest_by_name("safe_research_agent")
    result = engine.onboard(manifest)
    pdf_bytes = bundle_to_pdf(result.bundle)
    assert pdf_bytes.startswith(b"%PDF-")
    # Confirm /Font references appear (text actually rendered, not just metadata)
    assert b"/Font" in pdf_bytes


def test_bundle_to_pdf_handles_conditional_fixture() -> None:
    """The Ready with Conditions path exercises the findings branch with non-blocking items."""
    manifest = load_manifest_by_name("healthcare_phi_support_agent")
    result = engine.onboard(manifest)
    pdf_bytes = bundle_to_pdf(result.bundle)
    assert pdf_bytes.startswith(b"%PDF-")
    assert b"%%EOF" in pdf_bytes[-100:]
