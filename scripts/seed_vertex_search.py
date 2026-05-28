#!/usr/bin/env python3
"""Provision a Vertex AI Search (Discovery Engine) data store from the local corpus (FR-081).

Creates a data store and imports each corpus passage as a document with structured
fields (source_id, source_title, text, tags). After indexing (a few minutes), set:
    CPOA_GROUNDING_MODE=vertex_ai_search
    CPOA_VERTEX_SEARCH_DATASTORE=<datastore id>
and the agent grounds via Vertex AI Search instead of the local retriever.

    python scripts/seed_vertex_search.py [--datastore cpoa-corpus]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cpoa.loader import REPO_ROOT  # noqa: E402
from cpoa.services.grounding import load_corpus  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=None)
    ap.add_argument("--datastore", default="cpoa-corpus")
    ap.add_argument("--location", default="global")
    args = ap.parse_args()

    import os

    from google.api_core.client_options import ClientOptions
    from google.cloud import discoveryengine_v1 as de

    project = args.project or os.environ.get("GOOGLE_CLOUD_PROJECT", "clearpoint-operations-agent")
    parent = f"projects/{project}/locations/{args.location}/collections/default_collection"
    opts = ClientOptions(api_endpoint=f"{args.location}-discoveryengine.googleapis.com"
                         if args.location != "global" else None)

    ds_client = de.DataStoreServiceClient(client_options=opts)
    print(f"Creating data store '{args.datastore}' in {parent} ...")
    try:
        op = ds_client.create_data_store(
            parent=parent,
            data_store_id=args.datastore,
            data_store=de.DataStore(
                display_name="CPOA grounded corpus",
                industry_vertical=de.IndustryVertical.GENERIC,
                solution_types=[de.SolutionType.SOLUTION_TYPE_SEARCH],
                content_config=de.DataStore.ContentConfig.NO_CONTENT,
            ),
        )
        op.result(timeout=300)
        print("  data store created.")
    except Exception as exc:  # noqa: BLE001
        print(f"  (create skipped/failed: {exc})")

    doc_client = de.DocumentServiceClient(client_options=opts)
    branch = f"{parent}/dataStores/{args.datastore}/branches/default_branch"
    passages = load_corpus(REPO_ROOT / "corpus")
    print(f"Importing {len(passages)} passages ...")
    docs = [
        de.Document(
            id=f"{p.source_id}_{p.passage_id}".replace("#", "_"),
            struct_data=_struct({
                "source_id": f"{p.source_id}#{p.passage_id}",
                "source_title": p.source_title,
                "title": p.title,
                "text": p.text,
                "tags": list(p.tags),
            }),
        )
        for p in passages
    ]
    op = doc_client.import_documents(
        request=de.ImportDocumentsRequest(
            parent=branch,
            inline_source=de.ImportDocumentsRequest.InlineSource(documents=docs),
            reconciliation_mode=de.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
        )
    )
    print("  import started; indexing completes asynchronously (a few minutes).")
    print(f"\nThen set: CPOA_GROUNDING_MODE=vertex_ai_search  CPOA_VERTEX_SEARCH_DATASTORE={args.datastore}")
    return 0


def _struct(d: dict):
    from google.protobuf import struct_pb2

    s = struct_pb2.Struct()
    s.update(d)
    return s


if __name__ == "__main__":
    raise SystemExit(main())
