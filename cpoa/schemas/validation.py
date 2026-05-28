"""Onboarding Validation Suite outputs (§11.7)."""

from __future__ import annotations

from pydantic import Field

from .common import Confidence, CPOABase, Severity, utc_now_iso


class ValidationFinding(CPOABase):
    schema_version: str = "validation-finding/v0.1"
    finding_id: str
    candidate_agent_id: str
    test_id: str  # OV-001 .. OV-005
    severity: Severity
    confidence: Confidence = "high"
    title: str
    description: str = ""
    evidence_refs: list[str] = Field(default_factory=list)
    recommended_remediation: str = ""
    blocks_ready_decision: bool = False


class ValidationRun(CPOABase):
    schema_version: str = "validation-run/v0.1"
    run_id: str
    candidate_agent_id: str
    executed_at: str = Field(default_factory=utc_now_iso)
    tests_run: list[str] = Field(default_factory=list)
    findings: list[ValidationFinding] = Field(default_factory=list)
    summary: str = ""
    passed: bool = False
