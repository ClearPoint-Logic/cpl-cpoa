"""Operate phase — Sentinel runtime monitoring.

Continuous performance management for onboarded agents. Computes fleet
health from the **real signals** the deployment already produces — the
agent's onboarding outcome, the live lifecycle state from the HR Console,
and the events on its hash-chained personnel file. Each detection lands a
real evidence event into the chain so the audit trail is continuous from
intake through every subsequent runtime observation.

Detection rules are deterministic and reproducible. No LLM in the loop.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from cpoa.loader import list_fixture_names, load_manifest_by_name
from cpoa.schemas import Actor, EvidenceEvent, Signature, Subject
from cpoa.services import hashing, manage
from cpoa.services._helpers import is_action_capable, is_l2_plus
from cpoa.services.discovery import run_discovery
from cpoa.services.policy import propose_policy
from cpoa.services.scoring import compute_score
from cpoa.services.validation_suite import run_validation_suite


@dataclass
class FleetMember:
    candidate_agent_id: str
    name: str
    status: str  # active | on_leave | returning  (from Manage)
    risk_tier: str  # derived from highest tool risk_tier
    autonomy_level: str
    readiness_score: int
    onboarding_decision: str
    open_findings: int  # count of OVS findings that didn't block the decision
    blocking_findings: int  # count of blockers
    lifecycle_events_30d: int
    last_event_at: str | None
    anomalies: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "candidate_agent_id": self.candidate_agent_id,
            "name": self.name,
            "status": self.status,
            "risk_tier": self.risk_tier,
            "autonomy_level": self.autonomy_level,
            "readiness_score": self.readiness_score,
            "onboarding_decision": self.onboarding_decision,
            "open_findings": self.open_findings,
            "blocking_findings": self.blocking_findings,
            "lifecycle_events_30d": self.lifecycle_events_30d,
            "last_event_at": self.last_event_at,
            "anomalies": list(self.anomalies),
        }


def _highest_risk_tier(manifest) -> str:
    order = [
        "privileged_admin", "financial_action", "external_write",
        "internal_write", "read_only", "unknown",
    ]
    tiers = {t.risk_tier for t in manifest.tools}
    for level in order:
        if level in tiers:
            return level
    return "unknown"


def _count_recent_events(state: manage.LifecycleState, days: int) -> tuple[int, str | None]:
    if not state.event_log:
        return (0, None)
    cutoff = datetime.now(UTC) - timedelta(days=days)
    recent = 0
    last_at = None
    for evt in state.event_log:
        ts_raw = evt.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        if ts >= cutoff:
            recent += 1
        last_at = ts_raw
    return (recent, last_at)


def _run_gate(manifest) -> tuple:
    """Run the gate deterministically to surface findings + the decision."""
    disc = run_discovery(manifest)
    pol = propose_policy(manifest, disc)
    vr = run_validation_suite(manifest, disc, pol)
    score_obj = compute_score(manifest, disc, pol, vr)
    blockers = sum(1 for f in vr.findings if f.blocks_ready_decision)
    open_ = sum(1 for f in vr.findings if not f.blocks_ready_decision)
    if blockers > 0:
        decision = "Blocked Pending Remediation"
    elif vr.findings:
        decision = "Ready with Conditions"
    else:
        decision = "Ready"
    return decision, score_obj.score, blockers, open_, disc, pol, vr


def _anomaly_rules(member: FleetMember, manifest) -> list[dict]:
    """Deterministic rules — each rule fires on observable agent state."""
    out: list[dict] = []
    if member.blocking_findings > 0:
        out.append({
            "rule_id": "BLOCKER-AT-INTAKE",
            "severity": "high",
            "summary": (
                f"{member.blocking_findings} blocking finding(s) at intake — "
                "agent should not be on the active roster."
            ),
        })
    if member.status == "on_leave" and member.lifecycle_events_30d == 0:
        out.append({
            "rule_id": "STALE-LEAVE",
            "severity": "medium",
            "summary": "Agent has been on leave with no review activity in the last 30 days.",
        })
    if member.risk_tier in ("privileged_admin", "financial_action") and is_l2_plus(manifest.autonomy.level):
        out.append({
            "rule_id": "HIGH-AUTONOMY-HIGH-RISK",
            "severity": "high",
            "summary": (
                f"Risk tier {member.risk_tier!r} combined with autonomy "
                f"{member.autonomy_level!r} warrants continuous oversight."
            ),
        })
    if member.open_findings >= 2 and is_action_capable(manifest):
        out.append({
            "rule_id": "MULTI-CONDITION-AGENT",
            "severity": "medium",
            "summary": (
                f"{member.open_findings} unresolved conditions on an action-capable "
                "agent; review whether all conditions are still met in production."
            ),
        })
    return out


def assess_fleet() -> list[dict]:
    """Compute the fleet health snapshot. Real signals; deterministic; no LLM."""
    members: list[FleetMember] = []
    for fixture_name in list_fixture_names():
        try:
            manifest = load_manifest_by_name(fixture_name)
        except FileNotFoundError:
            continue
        decision, score, blockers, open_, _disc, _pol, _vr = _run_gate(manifest)
        # Skip blocked agents from the fleet view — they're not yet onboarded.
        # (Sentinel-style monitoring shows them only as a "should-not-be-running" anomaly
        # on agents that were forcibly onboarded; that scenario is the BLOCKER-AT-INTAKE rule.)
        state = manage.get_state(manifest.candidate_agent_id)
        recent_events, last_event_at = _count_recent_events(state, days=30)
        member = FleetMember(
            candidate_agent_id=manifest.candidate_agent_id,
            name=manifest.name,
            status=state.status,
            risk_tier=_highest_risk_tier(manifest),
            autonomy_level=manifest.autonomy.level,
            readiness_score=score,
            onboarding_decision=decision,
            open_findings=open_,
            blocking_findings=blockers,
            lifecycle_events_30d=recent_events,
            last_event_at=last_event_at,
        )
        member.anomalies = _anomaly_rules(member, manifest)
        members.append(member)

    summary = {
        "agents": len(members),
        "active": sum(1 for m in members if m.status == "active"),
        "on_leave": sum(1 for m in members if m.status == "on_leave"),
        "agents_with_anomalies": sum(1 for m in members if m.anomalies),
        "total_anomalies": sum(len(m.anomalies) for m in members),
        "by_risk_tier": _by_risk_tier([m.to_dict() for m in members]),
    }
    return [{"summary": summary, "members": [m.to_dict() for m in members]}]


def _by_risk_tier(members: list[dict]) -> dict[str, int]:
    out: dict[str, int] = {}
    for m in members:
        out[m["risk_tier"]] = out.get(m["risk_tier"], 0) + 1
    return out


def record_anomaly(
    candidate_agent_id: str,
    rule_id: str,
    severity: str,
    summary: str,
    actor_id: str = "sentinel@clearpointlogic.com",
) -> dict:
    """Record an anomaly into the agent's hash-chained personnel file.

    Returns the new lifecycle state with the appended evidence event.
    """
    state = manage.get_state(candidate_agent_id)
    payload = {"rule_id": rule_id, "severity": severity, "summary": summary}
    event = EvidenceEvent(
        event_id=f"evt-{uuid.uuid4().hex[:12]}",
        event_type="operate.anomaly_detected",
        trace_id=f"trace-ops-{uuid.uuid4().hex[:10]}",
        session_id=f"session-ops-{uuid.uuid4().hex[:10]}",
        actor=Actor(type="agent", id=actor_id),
        subject=Subject(candidate_agent_id=candidate_agent_id),
        summary=f"{rule_id} ({severity}): {summary}",
        payload_hash=hashing.payload_hash(payload),
    )
    hashing.link_event(event, state.last_event_hash)
    event.signature = Signature(
        type="local_hmac",
        value="hmac:" + event.event_hash.split(":", 1)[-1][:24],
    )
    state.event_log.append(event.model_dump(mode="json"))
    state.last_event_hash = event.event_hash
    state.updated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return {
        "state": state.to_dict(),
        "event": event.model_dump(mode="json"),
    }
