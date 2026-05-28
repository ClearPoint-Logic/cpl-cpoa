"""Canonical-JSON hashing + evidence hash-chain tests (§11.8)."""

from __future__ import annotations

import cpoa.schemas as s
from cpoa.services import hashing as h


def _event(event_type: str, summary: str) -> s.EvidenceEvent:
    return s.EvidenceEvent(
        event_id="e-" + event_type,
        event_type=event_type,
        trace_id="tr",
        session_id="se",
        actor=s.Actor(type="agent", id="discovery"),
        subject=s.Subject(candidate_agent_id="c"),
        summary=summary,
        payload_hash=h.payload_hash({"summary": summary}),
    )


def _chain() -> list[s.EvidenceEvent]:
    events: list[s.EvidenceEvent] = []
    prev = None
    for et, sm in [
        ("onboarding.intake.received", "got it"),
        ("onboarding.discovery.completed", "found facts"),
        ("onboarding.decision.issued", "Ready"),
    ]:
        e = _event(et, sm)
        h.link_event(e, prev)
        prev = e.event_hash
        events.append(e)
    return events


def test_canonical_json_is_order_independent():
    assert h.canonical_json({"b": 1, "a": 2}) == h.canonical_json({"a": 2, "b": 1})


def test_sha256_hex_format():
    digest = h.sha256_hex(b"hello")
    assert digest.startswith("sha256:") and len(digest) == len("sha256:") + 64


def test_valid_chain_verifies():
    ok, errors = h.verify_event_chain(_chain())
    assert ok and errors == []


def test_chain_links_previous_hash():
    events = _chain()
    assert events[1].previous_event_hash == events[0].event_hash
    assert events[0].previous_event_hash is None


def test_signature_value_excluded_from_event_hash():
    e = _chain()[0]
    before = h.compute_event_hash(e)
    e.signature.value = "TAMPERED"
    assert h.compute_event_hash(e) == before


def test_tamper_breaks_chain():
    events = _chain()
    events[1].summary = "MALICIOUS EDIT"
    ok, errors = h.verify_event_chain(events)
    assert not ok and errors


def test_bundle_hash_excludes_itself():
    passport = s.AgentPassport(passport_id="p", candidate_agent_id="c", agent_name="n")
    bundle = s.EvidenceBundle(
        bundle_id="bn", candidate_agent_id="c", decision="Ready",
        passport=passport, ai_bom=s.AIBOM(ai_bom_id="b", candidate_agent_id="c"),
        policy_envelope=s.PolicyEnvelope(policy_envelope_id="pe", candidate_agent_id="c"),
        passport_readiness_score=s.PassportReadinessScore(candidate_agent_id="c"),
        validation_run=s.ValidationRun(run_id="v", candidate_agent_id="c"),
        approval_card=s.ApprovalCard(approval_card_id="ac", candidate_agent_id="c"),
    )
    first = h.compute_bundle_hash(bundle)
    bundle.bundle_hash = first
    # Re-hashing with bundle_hash now populated must yield the same value (it is excluded).
    assert h.compute_bundle_hash(bundle) == first
