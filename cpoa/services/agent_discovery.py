"""Agent Discovery — the *Discover* phase of the AI Workforce Management lifecycle.

Scans a list of HTTPS endpoints for A2A Agent Cards (the standard `/.well-known/agent.json`
discoverable surface defined by the Agent-to-Agent protocol), compares each found agent
against the governed registry, and surfaces *unmanaged* agents that are operating without
having passed the Onboarding gate.

A representative A2A directory is served from this same API (see
`/api/demo-fleet/<name>/.well-known/agent.json`) so the scan exercises real network paths
end-to-end. In a customer deployment the same scanner walks the enterprise inventory APIs
(Agent Engine catalog, Cloud Run service inventory, A2A directory services) — the
classification and reporting code is identical; only the endpoint source changes.

Design rule (mirrors the rest of CPOA): this is deterministic. No LLM in the loop.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

import httpx

from cpoa.loader import REPO_ROOT

_REGISTRY_FIXTURE = REPO_ROOT / "fixtures" / "registry" / "google_agent_registry_fixture.json"
_TIMEOUT_SECONDS = 4.0


@dataclass
class DiscoveredAgent:
    """A single result from the directory scan."""

    endpoint: str
    status: str  # "known" | "unknown" | "unreachable" | "invalid"
    agent_card: dict | None = None
    candidate_agent_id: str | None = None  # populated when card declares one
    matched_registry_entry: dict | None = None  # populated when status == "known"
    error: str | None = None
    grounding_refs: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _load_governed_registry() -> dict[str, dict]:
    """Return the registry keyed by candidate_agent_id."""
    if not _REGISTRY_FIXTURE.exists():
        return {}
    raw = json.loads(_REGISTRY_FIXTURE.read_text())
    return {entry["candidate_agent_id"]: entry for entry in raw.get("agents", [])}


def _extract_candidate_id(card: dict) -> str | None:
    """Pull the candidate_agent_id from an A2A agent card, defensively.

    Different deployments stamp the id in different shapes. We accept:
    - `card["candidate_agent_id"]` (CPOA-native)
    - `card["id"]` (some directory services)
    - `card["name"]` slugified as a fallback (last resort)
    """
    cid = card.get("candidate_agent_id") or card.get("id")
    if cid:
        return str(cid)
    name = card.get("name")
    if name:
        return str(name).lower().replace(" ", "-").replace("/", "-")
    return None


def _classify(card: dict, registry: dict[str, dict]) -> tuple[str, str | None, dict | None]:
    """Classify a fetched card against the governed registry.

    Returns (status, candidate_agent_id, matched_registry_entry).
    """
    cid = _extract_candidate_id(card)
    if not cid:
        return ("invalid", None, None)
    entry = registry.get(cid)
    if entry:
        return ("known", cid, entry)
    return ("unknown", cid, None)


def fetch_agent_card(endpoint: str, *, client: httpx.Client | None = None) -> DiscoveredAgent:
    """Fetch one A2A agent card with a real HTTP call.

    `endpoint` is the *base* URL (no trailing slash). We append
    ``/.well-known/agent.json`` ourselves — that's the A2A discovery convention.
    """
    url = endpoint.rstrip("/") + "/.well-known/agent.json"
    owns_client = client is None
    client = client or httpx.Client(timeout=_TIMEOUT_SECONDS, follow_redirects=True)
    try:
        try:
            r = client.get(url)
        except httpx.RequestError as exc:
            return DiscoveredAgent(endpoint=endpoint, status="unreachable", error=str(exc))
        if r.status_code >= 400:
            return DiscoveredAgent(
                endpoint=endpoint,
                status="unreachable",
                error=f"HTTP {r.status_code}",
            )
        try:
            card = r.json()
        except json.JSONDecodeError as exc:
            return DiscoveredAgent(endpoint=endpoint, status="invalid", error=f"JSON parse: {exc}")
        if not isinstance(card, dict):
            return DiscoveredAgent(endpoint=endpoint, status="invalid", error="agent card not an object")
        return DiscoveredAgent(endpoint=endpoint, agent_card=card, status="pending")
    finally:
        if owns_client:
            client.close()


def scan_endpoints(endpoints: list[str]) -> list[DiscoveredAgent]:
    """Scan a list of A2A endpoints; return one DiscoveredAgent per endpoint.

    Each endpoint is fetched in turn (a small fleet is fine here; for a real
    enterprise inventory, this would parallelize via httpx.AsyncClient).
    """
    registry = _load_governed_registry()
    results: list[DiscoveredAgent] = []
    with httpx.Client(timeout=_TIMEOUT_SECONDS, follow_redirects=True) as client:
        for endpoint in endpoints:
            result = fetch_agent_card(endpoint, client=client)
            if result.status == "pending" and result.agent_card is not None:
                status, cid, entry = _classify(result.agent_card, registry)
                result.status = status
                result.candidate_agent_id = cid
                result.matched_registry_entry = entry
            results.append(result)
    return results


# --- Representative A2A directory -------------------------------------------
# A representative set of A2A agent cards we host directly so the discovery
# scanner makes real HTTP calls against a known surface. Each card models a
# realistic enterprise A2A agent shape. Three are unmanaged (will surface as
# findings against the governed registry); two appear in the registry.

DEMO_FLEET: dict[str, dict] = {
    # Known / governed — appears in fixtures/registry/google_agent_registry_fixture.json
    "safe-research-001": {
        "name": "Safe Research Agent",
        "candidate_agent_id": "safe-research-001",
        "description": "Search public web sources and summarize findings for analysts.",
        "version": "1.0.0",
        "protocolVersion": "0.2.0",
        "capabilities": {"streaming": False, "pushNotifications": False},
        "defaultInputModes": ["application/json", "text/plain"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "skills": [
            {
                "id": "research_summarize",
                "name": "Research and summarize",
                "description": "Search public web sources, return a cited summary.",
                "tags": ["research", "summarize"],
            }
        ],
        "metadata": {"owner": "dana@example.com", "team": "Research", "deployment": "cloud_run"},
    },
    # Unmanaged — shadow IT, the scary group
    "shadow-engagement-bot": {
        "name": "Customer Engagement Bot",
        "candidate_agent_id": "shadow-engagement-bot",
        "description": "Drafts and sends customer follow-up messages from the marketing team.",
        "version": "0.3.0",
        "protocolVersion": "0.2.0",
        "capabilities": {"streaming": True, "pushNotifications": True},
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json"],
        "skills": [
            {
                "id": "outbound_email",
                "name": "Draft and send outbound email",
                "description": "Composes and sends marketing emails via the corporate SMTP relay.",
                "tags": ["marketing", "email", "outbound"],
            }
        ],
        "metadata": {
            "owner": "unknown",
            "team": "marketing-experimental",
            "deployment": "cloud_run",
            "first_seen": "2026-04-12",
        },
    },
    "unmanaged-marketing-helper": {
        "name": "Marketing Content Helper",
        "candidate_agent_id": "unmanaged-marketing-helper",
        "description": "Generates blog drafts and social copy for the marketing site.",
        "version": "0.1.0-alpha",
        "protocolVersion": "0.2.0",
        "capabilities": {"streaming": False, "pushNotifications": False},
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "skills": [
            {
                "id": "content_draft",
                "name": "Draft marketing copy",
                "description": "Produce draft copy for blog posts and social media.",
                "tags": ["marketing", "content"],
            }
        ],
        "metadata": {
            "owner": "unknown",
            "team": "marketing",
            "deployment": "vercel-personal",
            "first_seen": "2026-03-28",
        },
    },
    "rogue-finance-extract": {
        "name": "Finance Data Extractor",
        "candidate_agent_id": "rogue-finance-extract",
        "description": "Pulls journal entries from the accounting system into a personal spreadsheet.",
        "version": "0.0.4",
        "protocolVersion": "0.2.0",
        "capabilities": {"streaming": False, "pushNotifications": False},
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json"],
        "skills": [
            {
                "id": "ledger_export",
                "name": "Export ledger entries",
                "description": "Reads accounting journal entries and exports to CSV.",
                "tags": ["finance", "export", "regulated_data"],
            }
        ],
        "metadata": {
            "owner": "unknown",
            "team": "finance-ops",
            "deployment": "developer-laptop",
            "first_seen": "2026-05-04",
        },
    },
    # Known / governed
    "healthcare-phi-003": {
        "name": "Healthcare Support Agent",
        "candidate_agent_id": "healthcare-phi-003",
        "description": "Tier-1 support agent for clinical operations queries.",
        "version": "1.2.0",
        "protocolVersion": "0.2.0",
        "capabilities": {"streaming": False, "pushNotifications": False},
        "defaultInputModes": ["application/json", "text/plain"],
        "defaultOutputModes": ["application/json", "text/plain"],
        "skills": [
            {
                "id": "support_triage",
                "name": "Support triage",
                "description": "Triages clinical-ops support tickets with PHI controls.",
                "tags": ["support", "healthcare", "phi"],
            }
        ],
        "metadata": {"owner": "pat@example.com", "team": "Clinical Operations"},
    },
}


def demo_fleet_endpoints(base_url: str) -> list[str]:
    """Build the list of endpoints the scanner will visit when given no overrides."""
    base = base_url.rstrip("/")
    return [f"{base}/api/demo-fleet/{name}" for name in DEMO_FLEET]


def demo_fleet_card(name: str) -> dict | None:
    """Lookup helper for the HTTP handler that serves the demo cards."""
    return DEMO_FLEET.get(name)


def is_known(candidate_agent_id: str) -> bool:
    return candidate_agent_id in _load_governed_registry()
