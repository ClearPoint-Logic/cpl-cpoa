"""Schema contract tests (§11) — shape validation, strictness, provenance, JSON export."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

import cpoa.schemas as s


def test_full_manifest_parses():
    m = s.CandidateAgentManifest(
        candidate_agent_id="c",
        name="n",
        origin="google_adk",
        tools=[{"tool_id": "t", "name": "x", "risk_tier": "read_only"}],
    )
    assert m.tools[0].risk_tier == "read_only"
    assert m.autonomy.level == "L0_observe"  # default applied


def test_sparse_manifest_parses_missing_owner_and_purpose():
    # "missing owner" is a discovery finding, not a shape error (FR-004/011).
    m = s.CandidateAgentManifest(candidate_agent_id="c", name="n")
    assert m.owner is None
    assert m.declared_purpose is None


def test_unknown_field_rejected():
    with pytest.raises(ValidationError):
        s.CandidateAgentManifest(candidate_agent_id="c", name="n", bogus=1)


def test_invalid_enum_rejected():
    with pytest.raises(ValidationError):
        s.CandidateAgentManifest(candidate_agent_id="c", name="n", origin="martian")


def test_ai_bom_entries_require_provenance():
    # Every BOM entry must carry source + confidence (§11.4).
    with pytest.raises(ValidationError):
        s.BomModelEntry(model="gemini-2.5-pro")  # missing source/confidence
    e = s.BomModelEntry(source="declared", confidence="high", model="gemini-2.5-pro")
    assert (e.source, e.confidence) == ("declared", "high")


def _all_top_level_artifacts():
    passport = s.AgentPassport(passport_id="p", candidate_agent_id="c", agent_name="n")
    bom = s.AIBOM(ai_bom_id="b", candidate_agent_id="c")
    policy = s.PolicyEnvelope(policy_envelope_id="pe", candidate_agent_id="c")
    score = s.PassportReadinessScore(candidate_agent_id="c")
    vrun = s.ValidationRun(run_id="v", candidate_agent_id="c")
    card = s.ApprovalCard(approval_card_id="ac", candidate_agent_id="c")
    return [passport, bom, policy, score, vrun, card]


def test_all_artifacts_export_json_with_schema_version():
    # AC #14-18: artifacts export as JSON.
    for art in _all_top_level_artifacts():
        d = json.loads(art.model_dump_json())
        assert d["schema_version"].endswith("/v0.1")


@pytest.mark.parametrize(
    "model,version",
    [
        (s.AgentPassport(passport_id="p", candidate_agent_id="c", agent_name="n"), "agent-passport/v0.1"),
        (s.AIBOM(ai_bom_id="b", candidate_agent_id="c"), "ai-bom/v0.1"),
        (s.PolicyEnvelope(policy_envelope_id="pe", candidate_agent_id="c"), "policy-envelope/v0.1"),
        (s.PassportReadinessScore(candidate_agent_id="c"), "passport-readiness-score/v0.1"),
        (s.ValidationFinding(finding_id="f", candidate_agent_id="c", test_id="OV-001", severity="low", title="t"), "validation-finding/v0.1"),
    ],
)
def test_canonical_schema_versions(model, version):
    assert model.schema_version == version


def test_evidence_bundle_honesty_flags():
    bundle = s.EvidenceBundle(
        bundle_id="bn",
        candidate_agent_id="c",
        decision="Ready",
        passport=s.AgentPassport(passport_id="p", candidate_agent_id="c", agent_name="n"),
        ai_bom=s.AIBOM(ai_bom_id="b", candidate_agent_id="c"),
        policy_envelope=s.PolicyEnvelope(policy_envelope_id="pe", candidate_agent_id="c"),
        passport_readiness_score=s.PassportReadinessScore(candidate_agent_id="c"),
        validation_run=s.ValidationRun(run_id="v", candidate_agent_id="c"),
        approval_card=s.ApprovalCard(approval_card_id="ac", candidate_agent_id="c"),
    )
    assert len(bundle.limitations) == 4
    assert bundle.passport.not_anchor_certification is True
    assert bundle.passport_readiness_score.not_production_cas_or_ecs is True


def test_evidence_event_default_signature_is_demo_stub():
    ev = s.EvidenceEvent(
        event_id="e",
        event_type="onboarding.intake.received",
        trace_id="t",
        session_id="se",
        actor=s.Actor(type="system", id="orchestrator"),
        subject=s.Subject(candidate_agent_id="c"),
        payload_hash="sha256:abc",
    )
    assert ev.signature.type == "demo_stub"
    assert "not production" in ev.signature.note
