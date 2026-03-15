"""Tests for govML policy engine."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_repo_hygiene_on_self():
    from src.policy_engine import check_repo_hygiene
    result = check_repo_hygiene(".")
    assert len(result.checks) == 6
    # LICENSE and .gitignore should exist (scaffolded by init_project.sh)
    license_check = next(c for c in result.checks if c["item"] == "LICENSE")
    assert license_check["pass"] is True


def test_publication_readiness():
    from src.policy_engine import check_publication_readiness
    result = check_publication_readiness(".")
    assert len(result.checks) == 5
    # FINDINGS.md should exist now
    findings_check = next(c for c in result.checks if c["item"] == "FINDINGS.md")
    assert findings_check["pass"] is True


def test_decision_log():
    from src.policy_engine import check_decision_log
    result = check_decision_log(".")
    assert result.checks[0]["pass"] is True  # File exists


def test_check_findings_integrity_missing_findings(tmp_path):
    """No FINDINGS.md → fails with descriptive message."""
    from src.policy_engine import check_findings_integrity
    result = check_findings_integrity(str(tmp_path))
    assert result.passed is False
    assert result.checks[0]["pass"] is False
    assert "FINDINGS.md" in result.checks[0]["detail"]


def test_check_statistical_rigor_missing_outputs(tmp_path):
    """No outputs/ directory → fails with descriptive message."""
    from src.policy_engine import check_statistical_rigor
    result = check_statistical_rigor(str(tmp_path))
    assert result.passed is False
    assert result.checks[0]["pass"] is False
    assert "outputs/" in result.checks[0]["detail"]


def test_mcp_tool_call():
    from src.mcp_server import handle_tool_call
    result = handle_tool_call("govml_scan_repo_hygiene", {"repo_path": "."})
    assert "checks" in result
    assert "passed" in result


def test_mcp_unknown_tool():
    from src.mcp_server import handle_tool_call
    result = handle_tool_call("nonexistent_tool", {})
    assert "error" in result
