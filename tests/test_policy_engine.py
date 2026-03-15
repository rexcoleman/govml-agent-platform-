"""Comprehensive tests for govML policy engine and MCP server.

Test categories:
  T1: Policy engine check functions (5 tests)
  T2: MCP server tool routing (5 tests)
  T3: Integration — run checks against real/mock projects (5 tests)
  T4: Edge cases — empty project, missing files, malformed YAML (5 tests)
  T5: ADR logging — log_decision creates valid ADR format (3 tests)
  + Original tests preserved (2 tests)
"""
import json
import sys
import yaml
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.policy_engine import (
    PolicyResult,
    check_repo_hygiene,
    check_publication_readiness,
    check_decision_log,
    check_findings_integrity,
    check_statistical_rigor,
    check_learning_curves,
    check_hypothesis_registry,
    check_provenance,
    check_test_coverage,
    check_phase_gate,
    load_project_config,
)
from src.mcp_server import handle_tool_call


# ============================================================
# T1: Policy engine check functions (5 tests)
# ============================================================

def test_check_repo_hygiene_on_self():
    """T1.1: Repo hygiene check returns 6 checks on own project."""
    result = check_repo_hygiene(".")
    assert len(result.checks) == 6
    assert isinstance(result, PolicyResult)
    license_check = next(c for c in result.checks if c["item"] == "LICENSE")
    assert license_check["pass"] is True


def test_check_publication_readiness_returns_5_checks():
    """T1.2: Publication readiness check returns exactly 5 checks."""
    result = check_publication_readiness(".")
    assert len(result.checks) == 5
    findings_check = next(c for c in result.checks if c["item"] == "FINDINGS.md")
    assert findings_check["pass"] is True


def test_check_decision_log_finds_adrs():
    """T1.3: Decision log check finds existing ADRs."""
    result = check_decision_log(".")
    assert result.checks[0]["pass"] is True  # File exists


def test_check_findings_integrity_on_self():
    """T1.4: Findings integrity check runs on own project."""
    result = check_findings_integrity(".")
    assert isinstance(result, PolicyResult)
    assert len(result.checks) >= 1


def test_check_test_coverage_on_self():
    """T1.5: Test coverage check finds tests in own project."""
    result = check_test_coverage(".", minimum=5)
    assert isinstance(result, PolicyResult)
    # Should find this file at minimum
    assert result.checks[0]["pass"] is True  # tests/ exists


# ============================================================
# T2: MCP server tool routing (5 tests)
# ============================================================

def test_mcp_repo_hygiene():
    """T2.1: MCP routes govml_scan_repo_hygiene correctly."""
    result = handle_tool_call("govml_scan_repo_hygiene", {"repo_path": "."})
    assert "checks" in result
    assert "passed" in result
    assert isinstance(result["checks"], list)


def test_mcp_publication():
    """T2.2: MCP routes govml_check_publication correctly."""
    result = handle_tool_call("govml_check_publication", {"repo_path": "."})
    assert "checks" in result
    assert "passed" in result


def test_mcp_decisions():
    """T2.3: MCP routes govml_check_decisions correctly."""
    result = handle_tool_call("govml_check_decisions", {"repo_path": "."})
    assert "passed" in result


def test_mcp_unknown_tool():
    """T2.4: MCP returns error for unknown tool."""
    result = handle_tool_call("nonexistent_tool", {})
    assert "error" in result


def test_mcp_findings_integrity():
    """T2.5: MCP routes govml_check_findings_integrity correctly."""
    result = handle_tool_call("govml_check_findings_integrity", {"project_path": "."})
    assert "checks" in result
    assert "passed" in result


# ============================================================
# T3: Integration — run checks against mock projects (5 tests)
# ============================================================

def test_full_scan_on_self():
    """T3.1: Full validation scan runs on own project."""
    result = handle_tool_call("govml_validate_project", {
        "project_yaml": "project.yaml",
        "repo_path": ".",
    })
    assert "overall_pass" in result
    assert "checks" in result
    assert isinstance(result["checks"], dict)


def test_learning_curves_check_with_data(tmp_path):
    """T3.2: Learning curves check passes when files exist."""
    (tmp_path / "figures").mkdir()
    (tmp_path / "figures" / "learning_curves.png").write_text("fake")
    (tmp_path / "outputs" / "diagnostics").mkdir(parents=True)
    (tmp_path / "outputs" / "diagnostics" / "learning_curves_seed42.json").write_text("{}")
    result = check_learning_curves(str(tmp_path))
    assert result.passed is True


def test_hypothesis_registry_check_with_data(tmp_path):
    """T3.3: Hypothesis registry check passes with valid registry."""
    registry = """# Hypothesis Registry

| ID | Hypothesis | Metric | Threshold | Status | Evidence |
|----|-----------|--------|-----------|--------|----------|
| H1 | Test hypothesis one | F1 | >0.8 | SUPPORTED | Evidence here |
| H2 | Test hypothesis two | AUC | >0.9 | SUPPORTED | Evidence here |
"""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "HYPOTHESIS_REGISTRY.md").write_text(registry)
    result = check_hypothesis_registry(str(tmp_path))
    assert result.passed is True


def test_statistical_rigor_with_seeds(tmp_path):
    """T3.4: Statistical rigor check counts unique seeds."""
    (tmp_path / "outputs").mkdir()
    for seed in [42, 123, 456]:
        (tmp_path / "outputs" / f"results_seed{seed}.json").write_text('{"f1": 0.85}')
    (tmp_path / "FINDINGS.md").write_text(
        "Results with 95% CI and baseline comparison.\n"
        "Confidence interval: [0.82, 0.88]\n"
    )
    (tmp_path / "project.yaml").write_text("data_type: synthetic\n")
    result = check_statistical_rigor(str(tmp_path))
    seed_check = result.checks[0]
    assert seed_check["pass"] is True


def test_provenance_check_with_files(tmp_path):
    """T3.5: Provenance check passes with all required files."""
    prov = tmp_path / "provenance"
    prov.mkdir()
    (prov / "config_resolved.yaml").write_text("seed: 42\n")
    (prov / "versions.txt").write_text("python 3.11\n")
    (prov / "output_manifest.json").write_text('{"files": []}\n')
    (prov / "git_info.txt").write_text("abc123\n")
    result = check_provenance(str(tmp_path))
    assert result.passed is True


# ============================================================
# T4: Edge cases (5 tests)
# ============================================================

def test_check_findings_integrity_missing_findings(tmp_path):
    """T4.1: No FINDINGS.md returns descriptive failure."""
    result = check_findings_integrity(str(tmp_path))
    assert result.passed is False
    assert result.checks[0]["pass"] is False
    assert "FINDINGS.md" in result.checks[0]["detail"]


def test_check_statistical_rigor_missing_outputs(tmp_path):
    """T4.2: No outputs/ directory returns descriptive failure."""
    result = check_statistical_rigor(str(tmp_path))
    assert result.passed is False
    assert result.checks[0]["pass"] is False
    assert "outputs/" in result.checks[0]["detail"]


def test_check_learning_curves_missing(tmp_path):
    """T4.3: No figures returns failure."""
    result = check_learning_curves(str(tmp_path))
    assert result.passed is False
    assert any("figure" in c["item"].lower() for c in result.checks)


def test_check_hypothesis_registry_missing(tmp_path):
    """T4.4: No registry returns failure."""
    result = check_hypothesis_registry(str(tmp_path))
    assert result.passed is False
    assert result.checks[0]["pass"] is False


def test_check_test_coverage_empty(tmp_path):
    """T4.5: No tests/ directory returns failure."""
    result = check_test_coverage(str(tmp_path))
    assert result.passed is False
    assert result.checks[0]["pass"] is False


# ============================================================
# T5: ADR logging (3 tests)
# ============================================================

def test_log_decision_creates_adr(tmp_path):
    """T5.1: log_decision appends valid ADR to decision log."""
    docs = tmp_path / "docs"
    docs.mkdir()
    log_path = docs / "DECISION_LOG.md"
    log_path.write_text("# Decision Log\n\n## ADR-0001: [First decision title]\n")

    result = handle_tool_call("govml_log_decision", {
        "repo_path": str(tmp_path),
        "adr": {
            "title": "Test Decision",
            "decision": "We decided to test this",
            "context": "Testing ADR creation",
            "rationale": "Because tests are good",
        },
    })
    assert result["success"] is True
    assert "ADR-" in result["adr_id"]

    content = log_path.read_text()
    assert "Test Decision" in content
    assert "We decided to test this" in content


def test_log_decision_missing_log(tmp_path):
    """T5.2: log_decision fails gracefully when no decision log exists."""
    result = handle_tool_call("govml_log_decision", {
        "repo_path": str(tmp_path),
        "adr": {"title": "Test", "decision": "Test"},
    })
    assert "error" in result


def test_log_decision_increments_number(tmp_path):
    """T5.3: log_decision increments ADR number correctly."""
    docs = tmp_path / "docs"
    docs.mkdir()
    log_path = docs / "DECISION_LOG.md"
    log_path.write_text("# Decision Log\n\n## ADR-0003: Previous decision\n")

    result = handle_tool_call("govml_log_decision", {
        "repo_path": str(tmp_path),
        "adr": {"title": "Next Decision", "decision": "Incremented"},
    })
    assert result["success"] is True
    assert result["adr_id"] == "ADR-0004"


# ============================================================
# Additional coverage tests
# ============================================================

def test_check_provenance_missing(tmp_path):
    """Provenance check fails with all files missing."""
    result = check_provenance(str(tmp_path))
    assert result.passed is False
    assert len(result.checks) == 4
    assert all(c["pass"] is False for c in result.checks)


def test_policy_result_summary():
    """PolicyResult.summary computes correctly."""
    result = PolicyResult(
        policy="test",
        passed=True,
        checks=[
            {"item": "a", "pass": True},
            {"item": "b", "pass": False},
            {"item": "c", "pass": True},
        ],
    )
    assert result.summary == "2/3 checks passed"
