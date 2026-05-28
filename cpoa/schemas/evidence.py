"""EvidenceEvent (§11.8) and EvidenceBundle (§11.9).

The bundle embeds the fully-typed artifacts so the personnel-file export is
self-contained and hashable over canonical JSON (§11.8 serialization rule).
"""

from __future__ import annotations

from pydantic import Field

from .agent_passport import AgentPassport, ApprovalCard, PassportReadinessScore
from .ai_bom import AIBOM
from .common import ActorType, CPOABase, Decision, EventType, SignatureType, utc_now_iso
from .policy_envelope import PolicyEnvelope
from .validation import ValidationRun

DEMO_SIGNATURE_NOTE = "Demo hash only; not production Anchor signing unless otherwise stated."

DEFAULT_LIMITATIONS = [
    "Challenge demo artifact; not production Anchor certification.",
    "Synthetic inputs unless explicitly noted.",
    "Demo signature is not production cryptographic attestation.",
    "Implements onboarding gate only; continuous attestation (the canonical CPL "
    "post-onboarding layer) is out of scope for this build.",
]


class Signature(CPOABase):
    type: SignatureType = "demo_stub"
    value: str = ""
    note: str = DEMO_SIGNATURE_NOTE


class Actor(CPOABase):
    type: ActorType
    id: str


class Subject(CPOABase):
    candidate_agent_id: str


class EvidenceEvent(CPOABase):
    schema_version: str = "evidence-event/v0.1"
    event_id: str
    event_type: EventType
    timestamp: str = Field(default_factory=utc_now_iso)
    trace_id: str
    session_id: str
    actor: Actor
    subject: Subject
    summary: str = ""
    payload_hash: str
    previous_event_hash: str | None = None
    event_hash: str = ""
    signature: Signature = Field(default_factory=Signature)


class EvidenceBundle(CPOABase):
    schema_version: str = "evidence-bundle/v0.1"
    bundle_id: str
    candidate_agent_id: str
    generated_at: str = Field(default_factory=utc_now_iso)
    decision: Decision
    passport: AgentPassport
    ai_bom: AIBOM
    policy_envelope: PolicyEnvelope
    passport_readiness_score: PassportReadinessScore
    validation_run: ValidationRun
    approval_card: ApprovalCard
    evidence_events: list[EvidenceEvent] = Field(default_factory=list)
    bundle_hash: str = ""
    limitations: list[str] = Field(default_factory=lambda: list(DEFAULT_LIMITATIONS))
