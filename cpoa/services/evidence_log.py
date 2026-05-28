"""Evidence writer (§9.3.6): hash-chained event log + bundle assembly + exports.

Implements the §11.8 serialization rule via cpoa.services.hashing. Demo signatures
are clearly labeled (`demo_stub`), never claimed as production attestation.
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
    Signature,
    Subject,
    ValidationRun,
)
from cpoa.schemas.common import Decision

from . import hashing


class EvidenceLog:
    """Append-only hash-chained event log for one onboarding run."""

    def __init__(self, candidate_agent_id: str, trace_id: str | None = None,
                 session_id: str | None = None, signature_mode: str = "stub") -> None:
        self.candidate_agent_id = candidate_agent_id
        self.trace_id = trace_id or f"trace-{uuid.uuid4().hex[:12]}"
        self.session_id = session_id or f"session-{uuid.uuid4().hex[:12]}"
        self.signature_mode = signature_mode
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
        # Demo-only signature over the (already computed) event hash. Clearly labeled.
        if self.signature_mode == "stub":
            event.signature = Signature(
                type="demo_stub",
                value="demo:" + event.event_hash.split(":", 1)[-1][:24],
            )
        self.events.append(event)
        return event


def build_bundle(
    decision: Decision,
    passport: AgentPassport,
    ai_bom: AIBOM,
    policy: PolicyEnvelope,
    score: PassportReadinessScore,
    validation_run: ValidationRun,
    approval_card: ApprovalCard,
    events: list[EvidenceEvent],
) -> EvidenceBundle:
    bundle = EvidenceBundle(
        bundle_id=f"bundle-{passport.candidate_agent_id}-{uuid.uuid4().hex[:8]}",
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
