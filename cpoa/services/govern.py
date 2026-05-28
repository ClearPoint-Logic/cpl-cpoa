"""Govern phase — Compass control mapping.

Renders the live mapping between CPOA's enforced controls (Onboarding
Validation Suite checks + Policy Envelope primitives) and the public
regulatory + security frameworks the deployment is grounded in (NSA MCP
CSI, NIST AI RMF, EU AI Act).

The mapping is sourced from the actual grounding corpus that ships in this
repository — every cited passage is fetched live (no separate metadata
table), so a corpus update flows into the matrix on next request.
"""

from __future__ import annotations

import json
from functools import lru_cache

from cpoa.loader import REPO_ROOT

_CORPUS_FILES = {
    "nsa_mcp_csi": REPO_ROOT / "corpus" / "nsa_mcp_csi" / "nsa_mcp_csi.json",
    "nist_ai_rmf": REPO_ROOT / "corpus" / "nist_ai_rmf_subset" / "nist_ai_rmf.json",
    "eu_ai_act": REPO_ROOT / "corpus" / "eu_ai_act_articles" / "eu_ai_act.json",
}

# Each control names the artifact/test it enforces, with the corpus passage IDs
# it satisfies in each framework. The mapping is curated against the actual
# corpus and the OVS implementation in cpoa/services/validation_suite.py.
_CONTROL_MAP: list[dict] = [
    {
        "control_id": "OV-001",
        "name": "Accountable owner & purpose",
        "category": "Identity",
        "summary": "Every onboarded agent must have a named, reachable accountable "
                   "owner and a specific declared purpose. Missing or generic owner "
                   "data on an action-capable agent blocks the gate.",
        "enforces": ["Passport identity, Owner verification"],
        "nsa_mcp_csi": [],
        "nist_ai_rmf": ["nist-govern-accountability"],
        "eu_ai_act": ["eu-art14-oversight"],
    },
    {
        "control_id": "OV-002",
        "name": "Tool risk tier & boundary",
        "category": "Authorization",
        "summary": "Tools above read-only require an approval rule; financial and "
                   "privileged-admin tools require four-eyes. Boundary mismatches "
                   "with declared autonomy raise findings.",
        "enforces": ["Policy Envelope tool boundary, approval rules"],
        "nsa_mcp_csi": ["nsa-auth", "nsa-least-privilege"],
        "nist_ai_rmf": ["nist-manage-controls"],
        "eu_ai_act": ["eu-art14-oversight"],
    },
    {
        "control_id": "OV-003",
        "name": "Regulated data handling",
        "category": "Data governance",
        "summary": "Declared regulated data classes (PHI, PII, financial) force "
                   "explicit retention caps, memory disclosures, and a compliance "
                   "approver on the route.",
        "enforces": ["AI BOM data classes, Policy Envelope approver"],
        "nsa_mcp_csi": [],
        "nist_ai_rmf": ["nist-map-context", "nist-manage-controls"],
        "eu_ai_act": ["eu-art10-data", "eu-art13-transparency"],
    },
    {
        "control_id": "OV-004",
        "name": "Prompt-injection & supply-chain",
        "category": "Security posture",
        "summary": "Tool descriptions and MCP server metadata are scanned for "
                   "injection content. Unmaintained or untrusted MCP servers are "
                   "flagged. Both can block the gate.",
        "enforces": ["Findings: injection scanner, MCP supply-chain"],
        "nsa_mcp_csi": ["nsa-untrusted-input", "nsa-supply-chain", "nsa-validation"],
        "nist_ai_rmf": ["nist-measure-validation"],
        "eu_ai_act": ["eu-art9-risk"],
    },
    {
        "control_id": "OV-005",
        "name": "Budget & kill-switch posture",
        "category": "Operational safety",
        "summary": "Every onboarded agent must declare a monthly spend cap with a "
                   "specified on-breach behavior and a healthy kill-switch state. "
                   "Missing or unsafe values raise findings.",
        "enforces": ["Policy Envelope budget, kill_switch_state"],
        "nsa_mcp_csi": [],
        "nist_ai_rmf": ["nist-manage-controls"],
        "eu_ai_act": ["eu-art9-risk", "eu-art14-oversight"],
    },
    {
        "control_id": "EVD-001",
        "name": "Hash-chained personnel file",
        "category": "Audit",
        "summary": "Every onboarding run produces an Evidence Bundle whose events "
                   "are SHA-256 hash-chained over canonical JSON. Tamper-evident "
                   "by construction.",
        "enforces": ["Evidence Bundle, EvidenceEvent chain"],
        "nsa_mcp_csi": ["nsa-audit", "nsa-integrity-replay"],
        "nist_ai_rmf": ["nist-govern-accountability"],
        "eu_ai_act": ["eu-art12-logging"],
    },
    {
        "control_id": "MCP-NSA",
        "name": "Secure MCP server baseline",
        "category": "Security posture",
        "summary": "The MCP server implements the NSA security baseline: "
                   "authentication, RBAC, message integrity + replay protection, "
                   "strict schema validation, output filtering, and audit "
                   "logging — verified by 19 security tests.",
        "enforces": ["mcp_servers/onboarding_tools/security.py"],
        "nsa_mcp_csi": ["nsa-auth", "nsa-validation", "nsa-integrity-replay",
                        "nsa-untrusted-input", "nsa-audit"],
        "nist_ai_rmf": ["nist-measure-validation"],
        "eu_ai_act": ["eu-art12-logging"],
    },
]


@lru_cache(maxsize=1)
def _passages_index() -> dict[str, dict]:
    """Flat lookup: passage_id -> {id, title, text, tags, source_id, source_title}."""
    out: dict[str, dict] = {}
    for framework_key, path in _CORPUS_FILES.items():
        doc = json.loads(path.read_text())
        source_id = doc.get("source_id", framework_key)
        source_title = doc.get("source_title", framework_key)
        for p in doc.get("passages", []):
            out[p["id"]] = {
                **p,
                "framework": framework_key,
                "source_id": source_id,
                "source_title": source_title,
            }
    return out


def _resolve(ids: list[str]) -> list[dict]:
    idx = _passages_index()
    return [
        {
            "id": pid,
            "title": idx[pid]["title"],
            "snippet": idx[pid]["text"][:240],
            "source_id": idx[pid]["source_id"],
            "source_title": idx[pid]["source_title"],
        }
        for pid in ids
        if pid in idx
    ]


def control_matrix() -> dict:
    """Return the live control matrix with citations resolved against the corpus."""
    controls = []
    for ctrl in _CONTROL_MAP:
        controls.append({
            "control_id": ctrl["control_id"],
            "name": ctrl["name"],
            "category": ctrl["category"],
            "summary": ctrl["summary"],
            "enforces": ctrl["enforces"],
            "citations": {
                "nsa_mcp_csi": _resolve(ctrl["nsa_mcp_csi"]),
                "nist_ai_rmf": _resolve(ctrl["nist_ai_rmf"]),
                "eu_ai_act": _resolve(ctrl["eu_ai_act"]),
            },
        })
    # Framework coverage summary: how many controls cite each framework
    coverage = {
        "nsa_mcp_csi": sum(1 for c in _CONTROL_MAP if c["nsa_mcp_csi"]),
        "nist_ai_rmf": sum(1 for c in _CONTROL_MAP if c["nist_ai_rmf"]),
        "eu_ai_act": sum(1 for c in _CONTROL_MAP if c["eu_ai_act"]),
    }
    frameworks = []
    for key, path in _CORPUS_FILES.items():
        doc = json.loads(path.read_text())
        frameworks.append({
            "key": key,
            "source_id": doc.get("source_id", key),
            "source_title": doc.get("source_title", key),
            "source_url": doc.get("source_url"),
            "passage_count": len(doc.get("passages", [])),
            "controls_citing": coverage[key],
        })
    return {
        "controls": controls,
        "frameworks": frameworks,
        "summary": {
            "controls_total": len(controls),
            "frameworks_total": len(frameworks),
            "citations_total": sum(
                len(c["citations"][k])
                for c in controls
                for k in ("nsa_mcp_csi", "nist_ai_rmf", "eu_ai_act")
            ),
        },
    }
