"""YAML-driven policy engine for govML governance enforcement.

Reads project.yaml and checks phase gates, repo hygiene, and publication readiness.
Designed to be called by both CLI and MCP server.
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class PolicyResult:
    """Result of a policy check."""
    policy: str
    passed: bool
    checks: list[dict] = field(default_factory=list)
    score: str = ""  # e.g., "4/5"

    @property
    def summary(self) -> str:
        passed = sum(1 for c in self.checks if c["pass"])
        return f"{passed}/{len(self.checks)} checks passed"


def load_project_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def check_repo_hygiene(repo_path: str) -> PolicyResult:
    """ISS-048: Check for README, LICENSE, pyproject.toml, environment.yml, .gitignore, tests/."""
    root = Path(repo_path)
    required = {
        "README.md": "Project documentation for GitHub visitors",
        "LICENSE": "Open-source license (MIT recommended)",
        "pyproject.toml": "Python packaging metadata",
        "environment.yml": "Conda environment specification",
        ".gitignore": "Git ignore rules",
    }

    checks = []
    for filename, purpose in required.items():
        exists = (root / filename).exists()
        checks.append({"item": filename, "purpose": purpose, "pass": exists})

    # tests/ directory with at least one file
    test_dir = root / "tests"
    has_tests = test_dir.exists() and any(test_dir.glob("test_*.py"))
    checks.append({"item": "tests/test_*.py", "purpose": "At least one test file", "pass": has_tests})

    all_pass = all(c["pass"] for c in checks)
    return PolicyResult(
        policy="repo_hygiene",
        passed=all_pass,
        checks=checks,
        score=f"{sum(1 for c in checks if c['pass'])}/{len(checks)}",
    )


def check_phase_gate(project_yaml: str, phase: int, repo_path: str = ".") -> PolicyResult:
    """Check if a specific phase gate's conditions are met."""
    config = load_project_config(project_yaml)
    phases = config.get("phases", [])

    if phase >= len(phases):
        return PolicyResult(policy=f"phase_{phase}", passed=False,
                           checks=[{"item": "phase_exists", "pass": False, "detail": f"Phase {phase} not defined"}])

    phase_def = phases[phase]
    checks = []

    for check in phase_def.get("checks", []):
        command = check.get("command", "")
        description = check.get("description", "")

        # For file existence checks, we can verify
        if command.startswith("test -f "):
            filepath = command.replace("test -f ", "")
            exists = (Path(repo_path) / filepath).exists()
            checks.append({"item": description, "command": command, "pass": exists})
        elif command.startswith("bash scripts/verify_env.sh"):
            # Check if script exists
            exists = (Path(repo_path) / "scripts/verify_env.sh").exists()
            checks.append({"item": description, "command": command, "pass": exists,
                          "detail": "Script exists (run manually to verify)"})
        elif command.startswith("git remote"):
            import subprocess
            try:
                result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True, cwd=repo_path)
                has_remote = "origin" in result.stdout
                checks.append({"item": description, "command": command, "pass": has_remote})
            except Exception:
                checks.append({"item": description, "command": command, "pass": False})
        else:
            # Can't auto-check — mark as manual
            checks.append({"item": description, "command": command, "pass": None,
                          "detail": "Requires manual verification"})

    verifiable = [c for c in checks if c["pass"] is not None]
    all_pass = all(c["pass"] for c in verifiable) if verifiable else False

    return PolicyResult(
        policy=f"phase_{phase}_{phase_def.get('name', '')}",
        passed=all_pass,
        checks=checks,
        score=f"{sum(1 for c in verifiable if c['pass'])}/{len(verifiable)} verifiable",
    )


def check_publication_readiness(repo_path: str) -> PolicyResult:
    """ISS-044 Phase N+3: Check publication artifacts exist."""
    root = Path(repo_path)
    checks = [
        {"item": "FINDINGS.md", "pass": (root / "FINDINGS.md").exists()},
        {"item": "blog/draft.md", "pass": (root / "blog/draft.md").exists()},
        {"item": "blog/conference_abstract.md", "pass": (root / "blog/conference_abstract.md").exists()},
        {"item": "blog/images/ (≥1 figure)", "pass": any((root / "blog/images").glob("*.png")) if (root / "blog/images").exists() else False},
        {"item": "PUBLICATION_PIPELINE (0 placeholders)",
         "pass": _count_placeholders(root / "docs/PUBLICATION_PIPELINE.md") == 0},
    ]

    all_pass = all(c["pass"] for c in checks)
    return PolicyResult(
        policy="publication_readiness",
        passed=all_pass,
        checks=checks,
        score=f"{sum(1 for c in checks if c['pass'])}/{len(checks)}",
    )


def check_decision_log(repo_path: str) -> PolicyResult:
    """Check DECISION_LOG has at least 1 ADR."""
    root = Path(repo_path)
    decision_log = root / "docs/DECISION_LOG.md"

    if not decision_log.exists():
        return PolicyResult(policy="decision_log", passed=False,
                           checks=[{"item": "DECISION_LOG.md exists", "pass": False}])

    content = decision_log.read_text()
    adr_count = content.count("## ADR-")
    # Subtract the template ADR if it still has placeholder text
    if "First decision title" in content:
        adr_count = max(0, adr_count - 1)

    checks = [
        {"item": "DECISION_LOG.md exists", "pass": True},
        {"item": f"≥1 ADR recorded ({adr_count} found)", "pass": adr_count >= 1},
    ]

    return PolicyResult(policy="decision_log", passed=all(c["pass"] for c in checks), checks=checks)


def _count_placeholders(filepath: Path) -> int:
    if not filepath.exists():
        return 999  # Missing file = not filled
    content = filepath.read_text()
    return content.count("{{") + content.count("PLACEHOLDER")


def run_all_checks(project_yaml: str, repo_path: str = ".") -> dict[str, PolicyResult]:
    """Run all governance policy checks on a project."""
    results = {
        "repo_hygiene": check_repo_hygiene(repo_path),
        "publication": check_publication_readiness(repo_path),
        "decision_log": check_decision_log(repo_path),
    }

    # Check all defined phases
    config = load_project_config(project_yaml)
    for i, phase in enumerate(config.get("phases", [])):
        results[f"phase_{i}"] = check_phase_gate(project_yaml, i, repo_path)

    return results
