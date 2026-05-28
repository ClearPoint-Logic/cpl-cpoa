"""Evidence writer (§9.3.6): hash-chained event log + bundle assembly + exports.

Implements the §11.8 serialization rule via cpoa.services.hashing. Signatures
are real — HMAC-SHA256 by default (local_hmac mode) or Cloud KMS asymmetric
signing when ``CPOA_SIGNING_MODE=kms`` is configured. See ``signing.py``.
"""

from __future__ import annotations

import uuid

from cpoa.schemas import (
    AIBOM,
    Actor,
    AgentPassport,
    ApprovalCard,
    EvidenceBundle,
    EvidenceEvent,
    PassportReadinessScore,
    PolicyEnvelope,
    Subject,
    ValidationRun,
)
from cpoa.schemas.common import Decision

from . import hashing
from .signing import Signer, get_signer


class EvidenceLog:
    """Append-only hash-chained event log for one onboarding run."""

    def __init__(self, candidate_agent_id: str, trace_id: str | None = None,
                 session_id: str | None = None, signature_mode: str | None = None,
                 signer: Signer | None = None) -> None:
        self.candidate_agent_id = candidate_agent_id
        self.trace_id = trace_id or f"trace-{uuid.uuid4().hex[:12]}"
        self.session_id = session_id or f"session-{uuid.uuid4().hex[:12]}"
        # Real signer by default (HMAC-SHA256 with the deployment secret).
        # signature_mode is preserved for back-compat but ignored in favor of
        # the env-configured signer unless an explicit signer is injected.
        self.signature_mode = signature_mode  # informational
        self.signer = signer or get_signer()
        self.events: list[EvidenceEvent] = []

    def emit(self, event_type: str, summary: str, payload: object,
             actor_id: str = "onboarding_orchestrator", actor_type: str = "agent") -> EvidenceEvent:
        prev = self.events[-1].event_hash if self.events else None
        event = EvidenceEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            event_type=event_type,  # validated against EventType literal by the schema
            trace_id=self.trace_id,
            session_id=self.session_id,
            actor=Actor(type=actor_type, id=actor_id),
            subject=Subject(candidate_agent_id=self.candidate_agent_id),
            summary=summary,
            payload_hash=hashing.payload_hash(payload),
        )
        hashing.link_event(event, prev)
        event.signature = self.signer.sign(event.event_hash)
        self.events.append(event)
        return event


def new_bundle_id(candidate_agent_id: str) -> str:
    """Predictable bundle id factory — callers that need to stamp the id into the
    approval_card before hashing the bundle must use this so the hash recomputes."""
    return f"bundle-{candidate_agent_id}-{uuid.uuid4().hex[:8]}"


def build_bundle(
    decision: Decision,
    passport: AgentPassport,
    ai_bom: AIBOM,
    policy: PolicyEnvelope,
    score: PassportReadinessScore,
    validation_run: ValidationRun,
    approval_card: ApprovalCard,
    events: list[EvidenceEvent],
    *,
    bundle_id: str | None = None,
) -> EvidenceBundle:
    """Assemble + hash the personnel-file bundle.

    Pass ``bundle_id`` when the caller has already stamped that id onto a
    field that is *inside* the bundle (e.g. ``approval_card.evidence_bundle_id``);
    otherwise a fresh id is minted here. The computed ``bundle_hash`` is
    over the canonical-JSON serialization of the final bundle — verifiable
    by any consumer that runs ``compute_bundle_hash`` against the same payload.
    """
    bundle = EvidenceBundle(
        bundle_id=bundle_id or new_bundle_id(passport.candidate_agent_id),
        candidate_agent_id=passport.candidate_agent_id,
        decision=decision,
        passport=passport,
        ai_bom=ai_bom,
        policy_envelope=policy,
        passport_readiness_score=score,
        validation_run=validation_run,
        approval_card=approval_card,
        evidence_events=list(events),
    )
    bundle.bundle_hash = hashing.compute_bundle_hash(bundle)
    return bundle
