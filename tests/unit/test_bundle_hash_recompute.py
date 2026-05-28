"""Bundle-hash integrity: the personnel-file hash must recompute deterministically.

Codex audit finding C1 (2026-05-27): the post-hash mutation of
``approval_card.evidence_bundle_id`` previously broke recompute. This test
locks the contract — for every fixture, the stored bundle_hash must equal
``compute_bundle_hash(bundle)`` over the as-exported bundle.
"""

from __future__ import annotations

import pytest

from cpoa.loader import list_fixture_names, load_manifest_by_name
from cpoa.services import engine
from cpoa.services.hashing import compute_bundle_hash


@pytest.mark.parametrize("fixture_name", list_fixture_names())
def test_bundle_hash_recomputes_for_every_fixture(fixture_name: str) -> None:
    manifest = load_manifest_by_name(fixture_name)
    result = engine.onboard(manifest)
    bundle = result.bundle
    # The stored hash and a fresh recompute must agree exactly. Otherwise the
    # personnel-file integrity claim is false.
    recomputed = compute_bundle_hash(bundle)
    assert bundle.bundle_hash == recomputed, (
        f"bundle_hash drift on {fixture_name}: "
        f"stored={bundle.bundle_hash} recomputed={recomputed}"
    )


@pytest.mark.parametrize("fixture_name", list_fixture_names())
def test_approval_card_evidence_bundle_id_matches_bundle_id(fixture_name: str) -> None:
    """The approval_card.evidence_bundle_id must equal the bundle's bundle_id —
    the audit trail is meaningless otherwise."""
    manifest = load_manifest_by_name(fixture_name)
    result = engine.onboard(manifest)
    assert result.bundle.approval_card.evidence_bundle_id == result.bundle.bundle_id
