"""Vertex AI Search (Discovery Engine) retriever (FR-081).

Active when CPOA_GROUNDING_MODE=vertex_ai_search and a data store is configured;
otherwise grounding.get_retriever() falls back to the local retriever (FR-082).
Provision the data store with scripts/seed_vertex_search.py. discoveryengine is
imported lazily so the dependency is optional for the local-grounding demo.
"""

from __future__ import annotations

import os

from cpoa.schemas import GroundingRef


class VertexSearchRetriever:
    mode = "vertex_ai_search"

    def __init__(self, project: str | None = None, location: str | None = None,
                 datastore: str | None = None) -> None:
        from google.cloud import discoveryengine_v1 as de

        self._de = de
        self.project = project or os.environ["GOOGLE_CLOUD_PROJECT"]
        self.location = location or os.environ.get("CPOA_VERTEX_SEARCH_LOCATION", "global")
        self.datastore = datastore or os.environ["CPOA_VERTEX_SEARCH_DATASTORE"]
        self.client = de.SearchServiceClient()
        self.serving_config = (
            f"projects/{self.project}/locations/{self.location}/collections/"
            f"default_collection/dataStores/{self.datastore}/servingConfigs/default_config"
        )

    def retrieve(self, query: str, k: int = 3, tags: list[str] | None = None) -> list[GroundingRef]:
        request = self._de.SearchRequest(
            serving_config=self.serving_config, query=query, page_size=k
        )
        refs: list[GroundingRef] = []
        for result in self.client.search(request):
            data = dict(result.document.struct_data or {})
            refs.append(GroundingRef(
                source_id=str(data.get("source_id", result.document.id)),
                source_title=str(data.get("source_title", "")),
                snippet=str(data.get("text", "")),
            ))
            if len(refs) >= k:
                break
        return refs
