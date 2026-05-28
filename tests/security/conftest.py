"""Shared fixtures for MCP security baseline tests (§12.6)."""

from __future__ import annotations

import pytest

from cpoa.loader import load_manifest_by_name
from cpoa.services import discovery as disc_svc
from cpoa.services import policy as pol_svc
from cpoa.services import validation_suite
from mcp_servers.onboarding_tools.security import SecureGateway

TOKEN = "test-secret-token"


@pytest.fixture
def token() -> str:
    return TOKEN


@pytest.fixture
def gateway() -> SecureGateway:
    return SecureGateway(auth_token=TOKEN, require_auth=True)


@pytest.fixture
def manifest_dict() -> dict:
    return load_manifest_by_name("safe_research_agent").model_dump()


@pytest.fixture
def inspect_payload(manifest_dict) -> dict:
    return {"candidate_manifest": manifest_dict, "trace_id": None,
            "session_id": None, "previous_event_hash": None}


@pytest.fixture
def artifacts_payload() -> dict:
    """A valid payload for the write-tier generate_passport_artifacts tool."""
    m = load_manifest_by_name("safe_research_agent")
    disc = disc_svc.run_discovery(m)
    pol = pol_svc.propose_policy(m, disc)
    vr = validation_suite.run_validation_suite(m, disc, pol)
    return {
        "discovery_report": disc.model_dump(),
        "policy_envelope": pol.model_dump(),
        "candidate_manifest": m.model_dump(),
        "validation_run": vr.model_dump(),
        "trace_id": None,
        "session_id": None,
        "previous_event_hash": None,
    }
