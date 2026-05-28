"""Run storage backends. Local in-memory by default; Firestore when configured.

CPOA_STORAGE_MODE=firestore makes runs durable across scale-to-zero instances and
shareable by URL. Payloads are stored as a single JSON string to sidestep
Firestore's nested-array restrictions.
"""

from __future__ import annotations

import json
import os


class MemoryStore:
    mode = "local"

    def __init__(self) -> None:
        self._d: dict[str, dict] = {}

    def save(self, run_id: str, payload: dict) -> None:
        self._d[run_id] = payload

    def get(self, run_id: str) -> dict | None:
        return self._d.get(run_id)


class FirestoreStore:
    mode = "firestore"

    def __init__(self, project: str | None = None, collection: str = "cpoa_runs") -> None:
        from google.cloud import firestore

        self._client = firestore.Client(project=project)
        self._collection = collection

    def save(self, run_id: str, payload: dict) -> None:
        self._client.collection(self._collection).document(run_id).set(
            {"json": json.dumps(payload)}
        )

    def get(self, run_id: str) -> dict | None:
        doc = self._client.collection(self._collection).document(run_id).get()
        if not doc.exists:
            return None
        return json.loads(doc.to_dict()["json"])


def get_store():
    """Return the configured run store, falling back to in-memory on any error."""
    if os.environ.get("CPOA_STORAGE_MODE") == "firestore":
        try:
            return FirestoreStore(os.environ.get("GOOGLE_CLOUD_PROJECT"))
        except Exception:  # noqa: BLE001 — fall back so the demo never hard-fails
            return MemoryStore()
    return MemoryStore()
