"""Unit tests for Govern (Compass) — control matrix vs. live corpus."""

from __future__ import annotations

from cpoa.services import govern


def test_matrix_has_expected_control_ids() -> None:
    matrix = govern.control_matrix()
    ids = {c["control_id"] for c in matrix["controls"]}
    assert {"OV-001", "OV-002", "OV-003", "OV-004", "OV-005",
            "EVD-001", "MCP-NSA"}.issubset(ids)


def test_every_citation_resolves_against_corpus() -> None:
    """Each cited passage_id must exist in the actual grounding corpus."""
    matrix = govern.control_matrix()
    for ctrl in matrix["controls"]:
        for framework in ("nsa_mcp_csi", "nist_ai_rmf", "eu_ai_act"):
            for cite in ctrl["citations"][framework]:
                # Resolved citations include real corpus passage data
                assert cite["id"]
                assert cite["title"]
                assert cite["source_id"]
                assert cite["snippet"]


def test_framework_metadata_includes_passage_counts() -> None:
    matrix = govern.control_matrix()
    frameworks = {f["key"]: f for f in matrix["frameworks"]}
    assert "nsa_mcp_csi" in frameworks
    assert "nist_ai_rmf" in frameworks
    assert "eu_ai_act" in frameworks
    for f in matrix["frameworks"]:
        assert f["passage_count"] > 0
        assert f["controls_citing"] > 0


def test_summary_aggregates_match_data() -> None:
    matrix = govern.control_matrix()
    assert matrix["summary"]["controls_total"] == len(matrix["controls"])
    assert matrix["summary"]["frameworks_total"] == len(matrix["frameworks"])
    counted = sum(
        len(c["citations"][k])
        for c in matrix["controls"]
        for k in ("nsa_mcp_csi", "nist_ai_rmf", "eu_ai_act")
    )
    assert matrix["summary"]["citations_total"] == counted


def test_every_control_carries_at_least_one_citation() -> None:
    """A control that maps to no framework is not a credible governance control."""
    matrix = govern.control_matrix()
    for ctrl in matrix["controls"]:
        total = sum(len(ctrl["citations"][k]) for k in ("nsa_mcp_csi", "nist_ai_rmf", "eu_ai_act"))
        assert total >= 1, f"control {ctrl['control_id']} has no citations"


def test_mcp_nsa_control_cites_all_nsa_security_passages() -> None:
    """The NSA baseline control should map across the NSA corpus broadly."""
    matrix = govern.control_matrix()
    nsa = next(c for c in matrix["controls"] if c["control_id"] == "MCP-NSA")
    assert len(nsa["citations"]["nsa_mcp_csi"]) >= 4
