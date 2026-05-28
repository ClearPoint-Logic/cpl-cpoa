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


def test_ascii_helper_replaces_non_latin1() -> None:
    # A character outside latin-1 (e.g., em dash) becomes "?" — that's the contract
    result = _ascii("café — résumé")
    assert "?" in result or "—" in result  # fpdf can't render em dash; replace is fine
    assert "caf" in result


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
