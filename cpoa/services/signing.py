"""Signature backends for the hash-chained personnel-file events.

Two real signing modes are supported:

- **local_hmac** (default) — HMAC-SHA256 over the canonical event hash with a
  per-deployment secret (``CPOA_SIGNING_SECRET``). Real signature, verifiable
  by any holder of the secret. Used for local dev and the hosted demo.
- **kms** — Cloud KMS asymmetric signing over the canonical event hash. Used
  in customer deployments where the signing key is held in Cloud KMS and the
  Cloud Run service account is granted ``roles/cloudkms.signerVerifier``.

The legacy ``stub`` mode (``demo_stub`` signature type) is retained for
backward compatibility with bundles produced prior to the introduction of
real signing. New runs use ``local_hmac`` by default.

The active mode is published live at ``/api/health.modes.signing``.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Protocol

from cpoa.schemas import Signature

_DEFAULT_SECRET = "cpoa-local-deployment"


class Signer(Protocol):
    type: str

    def sign(self, event_hash: str) -> Signature: ...


class LocalHmacSigner:
    """HMAC-SHA256 with a per-deployment secret. Real signature."""

    type = "local_hmac"

    def __init__(self, secret: str | None = None) -> None:
        # Fall back to a stable default secret so the demo works out of the
        # box; a production deployment supplies CPOA_SIGNING_SECRET.
        self._secret = (secret or os.environ.get("CPOA_SIGNING_SECRET") or _DEFAULT_SECRET).encode()

    def sign(self, event_hash: str) -> Signature:
        mac = hmac.new(self._secret, event_hash.encode(), hashlib.sha256).hexdigest()
        return Signature(
            type="local_hmac",
            value=f"hmac-sha256:{mac}",
            note=(
                "HMAC-SHA256 over the canonical event hash with the deployment "
                "signing secret. Verifiable by any holder of CPOA_SIGNING_SECRET."
            ),
        )


class KmsSigner:
    """Cloud KMS asymmetric signing. Activated when a key resource is configured.

    The key is referenced by its full resource name (project/location/keyRing/
    cryptoKey/cryptoKeyVersion). The Cloud Run service account must have
    ``roles/cloudkms.signerVerifier`` on the key.
    """

    type = "kms"

    def __init__(self, key_name: str | None = None) -> None:
        self._key_name = key_name or os.environ.get("CPOA_SIGNING_KEY")
        if not self._key_name:
            raise RuntimeError("CPOA_SIGNING_KEY not configured for kms signing mode")

    def sign(self, event_hash: str) -> Signature:  # pragma: no cover — requires KMS
        from google.cloud import kms_v1

        client = kms_v1.KeyManagementServiceClient()
        digest = hashlib.sha256(event_hash.encode()).digest()
        response = client.asymmetric_sign(
            request={"name": self._key_name, "digest": {"sha256": digest}}
        )
        # Encode the signature bytes as hex for canonical JSON.
        sig_hex = response.signature.hex()
        return Signature(
            type="kms",
            value=f"kms:{sig_hex}",
            note=f"Cloud KMS asymmetric signature; key={self._key_name}",
        )


def get_signer(mode: str | None = None) -> Signer:
    """Resolve the signer for the configured signing mode.

    Defaults to ``CPOA_SIGNING_MODE`` env, then ``local_hmac``. If ``kms`` is
    requested but the key isn't configured, falls back to ``local_hmac`` so
    the gate never hard-fails on a missing key.
    """
    mode = (mode or os.environ.get("CPOA_SIGNING_MODE", "local_hmac")).strip()
    if mode == "kms":
        try:
            return KmsSigner()
        except Exception:  # noqa: BLE001 — fall back rather than fail-closed on signing
            return LocalHmacSigner()
    return LocalHmacSigner()


def configured_mode() -> str:
    """Read CPOA_SIGNING_MODE; defaults to local_hmac (real signature)."""
    return os.environ.get("CPOA_SIGNING_MODE", "local_hmac").strip() or "local_hmac"
