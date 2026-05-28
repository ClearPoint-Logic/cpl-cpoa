"""Canonical-JSON hashing and the evidence hash-chain (§11.8).

Canonical serialization rule (§11.8):
- Event hashes are computed over canonical JSON: sorted keys, compact separators,
  UTF-8 encoding, excluding mutable fields such as ``signature.value``.
- Bundle hashes exclude ``bundle_hash`` itself.
- Artifact hashes are computed over each artifact's canonical JSON representation.
- Any mismatch in event-hash validation blocks a Ready decision.

This module is pure and deterministic — no LLM, no I/O.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel


def _to_jsonable(obj: Any) -> Any:
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")
    return obj


def canonical_json(obj: Any) -> bytes:
    """Serialize to canonical JSON bytes: sorted keys, compact separators, UTF-8."""
    return json.dumps(
        _to_jsonable(obj),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def hash_obj(obj: Any, exclude: tuple[str, ...] = ()) -> str:
    """Hash any artifact/dict over its canonical JSON, optionally excluding top-level keys."""
    d = _to_jsonable(obj)
    if isinstance(d, dict) and exclude:
        d = {k: v for k, v in d.items() if k not in exclude}
    return sha256_hex(canonical_json(d))


def payload_hash(payload: Any) -> str:
    """Hash a stage payload (manifest, summary dict, etc.) for an evidence event."""
    return sha256_hex(canonical_json(payload))


# --- Evidence hash-chain ----------------------------------------------------
def _event_hashable(event: Any) -> dict[str, Any]:
    """Canonical view of an event for hashing: drop event_hash + signature.value."""
    d = _to_jsonable(event)
    d = dict(d)
    d.pop("event_hash", None)
    sig = d.get("signature")
    if isinstance(sig, dict):
        sig = dict(sig)
        sig.pop("value", None)
        d["signature"] = sig
    return d


def compute_event_hash(event: Any) -> str:
    return sha256_hex(canonical_json(_event_hashable(event)))


def link_event(event: Any, previous_event_hash: str | None) -> Any:
    """Set previous_event_hash then compute and set this event's event_hash (in place)."""
    event.previous_event_hash = previous_event_hash
    event.event_hash = compute_event_hash(event)
    return event


def verify_event_chain(events: list[Any]) -> tuple[bool, list[str]]:
    """Recompute every event hash and check linkage. Returns (ok, errors)."""
    errors: list[str] = []
    prev: str | None = None
    for i, e in enumerate(events):
        etype = getattr(e, "event_type", "?")
        expected = compute_event_hash(e)
        actual = getattr(e, "event_hash", None)
        if actual != expected:
            errors.append(f"event[{i}] {etype}: event_hash mismatch")
        if getattr(e, "previous_event_hash", None) != prev:
            errors.append(f"event[{i}] {etype}: previous_event_hash break")
        prev = actual
    return (not errors, errors)


def compute_bundle_hash(bundle: Any) -> str:
    """Bundle hash excludes ``bundle_hash`` itself (§11.8)."""
    return hash_obj(bundle, exclude=("bundle_hash",))
