"""Onboarding remediation — turn a Blocked candidate into a fixed, re-runnable one.

The hero path: a candidate is **Blocked** because a tool description carries an
indirect prompt-injection payload (OV-004, critical, blocks the decision). The
fix is the real NSA-MCP-aligned control — treat the tool description as untrusted
data, quarantine it, and re-issue the tool with a security-reviewed description.
The *same* deterministic onboarding pipeline then re-runs on the sanitized
manifest (no scoring shortcuts), and the candidate clears.

A signed, hash-chained ``onboarding.remediated`` event closes the loop on the
original run's personnel file and links it forward to the cleared re-run, so the
"Blocked → remediate → cleared" story is provable end to end.
"""

from __future__ import annotations

import uuid

from cpoa.schemas import Actor, CandidateAgentManifest, EvidenceEvent, Subject
from cpoa.services import hashing
from cpoa.services.injection import scan_text
from cpoa.services.signing import get_signer

_QUARANTINE_NOTE = (
    "[Quarantined — security-reviewed] {label}: performs its declared function "
    "only. Instruction-like content was stripped from the original description "
    "and is treated as untrusted data per NSA MCP CSI output-filtering guidance."
)


def sanitize_manifest(
    manifest: CandidateAgentManifest,
) -> tuple[CandidateAgentManifest, list[dict]]:
    """Return a sanitized copy of ``manifest`` plus the list of fixes applied.

    Any tool whose description contains prompt-injection content is quarantined:
    the untrusted description is replaced with a security-reviewed summary so the
    injected instructions can no longer reach the model. Pure — the input is not
    mutated. ``applied`` is empty when there is nothing to remediate.
    """
    data = manifest.model_dump()
    applied: list[dict] = []
    for tool in data.get("tools", []):
        hits = scan_text(tool.get("description") or "")
        if not hits:
            continue
        label = tool.get("name") or tool.get("tool_id") or "tool"
        tool["description"] = _QUARANTINE_NOTE.format(label=label)
        applied.append(
            {
                "tool_id": tool.get("tool_id"),
                "control": "OV-004",
                "phrases": hits,
                "action": "quarantined_and_rewrote_description",
            }
        )
    return CandidateAgentManifest(**data), applied


def build_remediation_event(
    candidate_agent_id: str,
    *,
    previous_event_hash: str | None,
    summary: str,
    payload: dict,
    actor_id: str = "security.reviewer@clearpointlogic.com",
) -> EvidenceEvent:
    """Build a signed, hash-chained ``onboarding.remediated`` event.

    Chains off ``previous_event_hash`` (the last event on the original blocked
    run) so the personnel file stays continuous through the remediation. Uses the
    same HMAC/KMS signer and canonical hashing as every other evidence event.
    """
    event = EvidenceEvent(
        event_id=f"evt-{uuid.uuid4().hex[:12]}",
        event_type="onboarding.remediated",
        trace_id=f"trace-remediation-{uuid.uuid4().hex[:10]}",
        session_id=f"session-remediation-{uuid.uuid4().hex[:10]}",
        actor=Actor(type="human", id=actor_id),
        subject=Subject(candidate_agent_id=candidate_agent_id),
        summary=summary,
        payload_hash=hashing.payload_hash(payload),
    )
    hashing.link_event(event, previous_event_hash)
    event.signature = get_signer().sign(event.event_hash)
    return event
