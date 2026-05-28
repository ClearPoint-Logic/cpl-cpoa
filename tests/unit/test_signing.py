"""Signing backends — real HMAC by default, KMS env-flagged."""

from __future__ import annotations

import hashlib
import hmac

from cpoa.services import signing


def test_local_hmac_signer_produces_real_hmac() -> None:
    signer = signing.LocalHmacSigner(secret="test-secret")
    sig = signer.sign("sha256:abc123")
    assert sig.type == "local_hmac"
    assert sig.value.startswith("hmac-sha256:")
    # Verify the HMAC value matches what `hmac` produces directly
    expected = hmac.new(b"test-secret", b"sha256:abc123", hashlib.sha256).hexdigest()
    assert sig.value == f"hmac-sha256:{expected}"


def test_local_hmac_signer_uses_env_secret(monkeypatch) -> None:
    monkeypatch.setenv("CPOA_SIGNING_SECRET", "env-secret")
    signer = signing.LocalHmacSigner()
    sig = signer.sign("sha256:abc")
    expected = hmac.new(b"env-secret", b"sha256:abc", hashlib.sha256).hexdigest()
    assert sig.value == f"hmac-sha256:{expected}"


def test_local_hmac_signer_falls_back_to_default(monkeypatch) -> None:
    monkeypatch.delenv("CPOA_SIGNING_SECRET", raising=False)
    signer = signing.LocalHmacSigner()
    sig = signer.sign("sha256:xyz")
    # Stable default works; signature is real
    assert sig.value.startswith("hmac-sha256:")


def test_get_signer_defaults_to_local_hmac(monkeypatch) -> None:
    monkeypatch.delenv("CPOA_SIGNING_MODE", raising=False)
    s = signing.get_signer()
    assert s.type == "local_hmac"


def test_get_signer_kms_falls_back_when_unconfigured(monkeypatch) -> None:
    """If CPOA_SIGNING_KEY isn't set, KMS signer construction raises and
    get_signer() falls back to local_hmac so the gate never hard-fails."""
    monkeypatch.setenv("CPOA_SIGNING_MODE", "kms")
    monkeypatch.delenv("CPOA_SIGNING_KEY", raising=False)
    s = signing.get_signer()
    assert s.type == "local_hmac"


def test_configured_mode_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("CPOA_SIGNING_MODE", "kms")
    assert signing.configured_mode() == "kms"


def test_configured_mode_default(monkeypatch) -> None:
    monkeypatch.delenv("CPOA_SIGNING_MODE", raising=False)
    assert signing.configured_mode() == "local_hmac"


def test_kms_signer_construction_requires_key() -> None:
    import pytest

    with pytest.raises(RuntimeError, match="CPOA_SIGNING_KEY"):
        signing.KmsSigner()


def test_signatures_verify_with_holder_of_secret() -> None:
    """Demonstrate that a third party with the secret can verify the sig."""
    signer = signing.LocalHmacSigner(secret="shared")
    event_hash = "sha256:deadbeef"
    sig = signer.sign(event_hash)
    sig_value = sig.value.removeprefix("hmac-sha256:")
    expected = hmac.new(b"shared", event_hash.encode(), hashlib.sha256).hexdigest()
    assert hmac.compare_digest(sig_value, expected)
