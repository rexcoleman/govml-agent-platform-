"""YAML-driven policy engine for govML governance enforcement.

Reads project.yaml and checks phase gates, repo hygiene, and publication readiness.
Designed to be called by both CLI and MCP server.
"""

import re
import json
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


def check_findings_integrity(project_path: str) -> PolicyResult:
    """Audit FINDINGS.md claims against raw JSON outputs.

    Checks claim/data reconciliation, claim strength tags, and seed count.
    """
    root = Path(project_path)
    findings_path = root / "FINDINGS.md"
    checks = []

    if not findings_path.exists():
        return PolicyResult(
            policy="findings_integrity",
            passed=False,
            checks=[{"item": "FINDINGS.md exists", "pass": False,
                     "detail": "FINDINGS.md not found in project root"}],
            score="0/3",
        )

    findings_text = findings_path.read_text()

    # --- Extract numbers from FINDINGS.md ---
    number_patterns = re.findall(
        r'\d+\.\d+%?|\d+%|\d+pp|\d{2,}', findings_text
    )
    claim_numbers = set(number_patterns)

    # --- Load all JSON output values ---
    outputs_dir = root / "outputs"
    json_files = list(outputs_dir.rglob("*.json")) if outputs_dir.exists() else []
    json_numbers: set[str] = set()
    for jf in json_files:
        try:
            data = json.loads(jf.read_text())
            _extract_numbers_from_json(data, json_numbers)
        except (json.JSONDecodeError, OSError):
            continue

    # --- Claim/data reconciliation ---
    if claim_numbers:
        matched = sum(1 for n in claim_numbers if n in json_numbers)
        match_ratio = matched / len(claim_numbers)
    else:
        match_ratio = 0.0
    claims_reconciled = match_ratio > 0.80
    checks.append({
        "item": "Claim/data reconciliation (>80%)",
        "pass": claims_reconciled,
        "detail": f"{match_ratio:.0%} of {len(claim_numbers)} numeric claims matched JSON outputs",
    })

    # --- Claim strength tags ---
    tag_pattern = r'\[(DEMONSTRATED|SUGGESTED|PROJECTED|HYPOTHESIZED)\]'
    tags_found = re.findall(tag_pattern, findings_text)
    # Count paragraphs (non-empty lines separated by blanks) as proxy for claims
    paragraphs = [p.strip() for p in findings_text.split('\n\n') if p.strip()]
    claim_sections = max(len(paragraphs), 1)
    tag_ratio = len(tags_found) / claim_sections if claim_sections else 0.0
    tags_sufficient = tag_ratio > 0.80
    checks.append({
        "item": "Claim strength tags (>80% sections tagged)",
        "pass": tags_sufficient,
        "detail": f"{len(tags_found)} tags across {claim_sections} sections ({tag_ratio:.0%})",
    })

    # --- Seed count ---
    seed_files = list(outputs_dir.rglob("*seed*.json")) if outputs_dir.exists() else []
    seed_count = len(seed_files)
    seeds_sufficient = seed_count >= 3
    checks.append({
        "item": "Seed count (≥3)",
        "pass": seeds_sufficient,
        "detail": f"{seed_count} seed files found",
    })

    all_pass = all(c["pass"] for c in checks)
    passed_count = sum(1 for c in checks if c["pass"])
    return PolicyResult(
        policy="findings_integrity",
        passed=all_pass,
        checks=checks,
        score=f"{passed_count}/{len(checks)}",
    )


def _extract_numbers_from_json(data, numbers: set[str]):
    """Recursively extract string representations of numbers from JSON data."""
    if isinstance(data, dict):
        for v in data.values():
            _extract_numbers_from_json(v, numbers)
    elif isinstance(data, list):
        for v in data:
            _extract_numbers_from_json(v, numbers)
    elif isinstance(data, (int, float)):
        # Store multiple representations for matching
        numbers.add(str(data))
        if isinstance(data, float):
            numbers.add(f"{data:.2f}")
            numbers.add(f"{data:.1f}")
            numbers.add(f"{data:.0f}")
            # Percentage representations
            numbers.add(f"{data * 100:.1f}")
            numbers.add(f"{data * 100:.0f}")


def check_statistical_rigor(project_path: str) -> PolicyResult:
    """Check statistical methodology: seeds, CIs, baselines, hyperparameters, data type."""
    root = Path(project_path)
    checks = []

    # --- Seed count from output filenames ---
    outputs_dir = root / "outputs"
    if not outputs_dir.exists():
        return PolicyResult(
            policy="statistical_rigor",
            passed=False,
            checks=[{"item": "outputs/ directory exists", "pass": False,
                     "detail": "No outputs/ directory found in project root"}],
            score="0/3",
        )

    seed_files = list(outputs_dir.rglob("*seed*.json"))
    # Extract unique seed identifiers from filenames
    unique_seeds: set[str] = set()
    for sf in seed_files:
        match = re.search(r'seed[_-]?(\d+)', sf.name, re.IGNORECASE)
        if match:
            unique_seeds.add(match.group(1))
    seed_count = len(unique_seeds)
    seeds_ok = seed_count >= 3
    checks.append({
        "item": "Unique seeds (≥3)",
        "pass": seeds_ok,
        "detail": f"{seed_count} unique seeds found",
    })

    # --- Read FINDINGS.md for statistical checks ---
    findings_path = root / "FINDINGS.md"
    findings_text = findings_path.read_text() if findings_path.exists() else ""

    # Confidence intervals
    has_ci = bool(re.search(r'\bCI\b|confidence interval|±', findings_text))
    checks.append({
        "item": "Confidence intervals reported",
        "pass": has_ci,
        "detail": "Found CI/confidence interval/± mention" if has_ci else "No confidence intervals found in FINDINGS.md",
    })

    # Baselines
    has_baselines = bool(re.search(r'\bbaseline\b', findings_text, re.IGNORECASE))
    checks.append({
        "item": "Baselines mentioned",
        "pass": has_baselines,
        "detail": "Baseline comparison found" if has_baselines else "No baseline mention in FINDINGS.md",
    })

    # --- Hyperparameter search (any project file) ---
    hp_pattern = re.compile(r'hyperparameter|grid.search|random.search', re.IGNORECASE)
    has_hp = bool(hp_pattern.search(findings_text))
    if not has_hp:
        for py_file in root.rglob("*.py"):
            try:
                if hp_pattern.search(py_file.read_text()):
                    has_hp = True
                    break
            except OSError:
                continue
    checks.append({
        "item": "Hyperparameter search documented",
        "pass": has_hp,
        "detail": "Hyperparameter search found" if has_hp else "No hyperparameter search documentation found",
    })

    # --- Data type from project.yaml ---
    project_yaml = root / "project.yaml"
    data_type = None
    if project_yaml.exists():
        try:
            config = yaml.safe_load(project_yaml.read_text())
            data_type = config.get("data_type")
        except (yaml.YAMLError, OSError):
            pass
    checks.append({
        "item": "data_type declared in project.yaml",
        "pass": data_type is not None,
        "detail": f"data_type={data_type}" if data_type else "No data_type field in project.yaml",
    })

    # Pass criteria: seeds >= 3 AND has_ci AND has_baselines
    all_pass = seeds_ok and has_ci and has_baselines
    passed_count = sum(1 for c in checks if c["pass"])
    return PolicyResult(
        policy="statistical_rigor",
        passed=all_pass,
        checks=checks,
        score=f"{passed_count}/{len(checks)}",
    )


def check_learning_curves(project_path: str) -> PolicyResult:
    """Check that learning curve figures exist and were generated from data."""
    root = Path(project_path)
    checks = []

    # Check for figures/learning_curves.png OR figures/lc_*.png
    figures_dir = root / "figures"
    has_figure = False
    if figures_dir.exists():
        has_figure = (
            (figures_dir / "learning_curves.png").exists()
            or any(figures_dir.glob("lc_*.png"))
        )
    checks.append({
        "item": "Learning curve figure exists",
        "pass": has_figure,
        "detail": "Found in figures/" if has_figure else "No learning_curves.png or lc_*.png in figures/",
    })

    # Check for outputs/diagnostics/learning_curves_*.json source data
    diag_dir = root / "outputs" / "diagnostics"
    has_source = False
    if diag_dir.exists():
        has_source = any(diag_dir.glob("learning_curves_*.json"))
    checks.append({
        "item": "Learning curve source data exists",
        "pass": has_source,
        "detail": "Found in outputs/diagnostics/" if has_source else "No learning_curves_*.json in outputs/diagnostics/",
    })

    all_pass = all(c["pass"] for c in checks)
    return PolicyResult(
        policy="learning_curves",
        passed=all_pass,
        checks=checks,
        score=f"{sum(1 for c in checks if c['pass'])}/{len(checks)}",
    )


def check_hypothesis_registry(project_path: str) -> PolicyResult:
    """Check that hypotheses are pre-registered and resolved."""
    root = Path(project_path)
    checks = []

    # Look for HYPOTHESIS_REGISTRY.md or docs/HYPOTHESIS_REGISTRY.md
    registry_path = None
    for candidate in [root / "HYPOTHESIS_REGISTRY.md", root / "docs/HYPOTHESIS_REGISTRY.md"]:
        if candidate.exists():
            registry_path = candidate
            break

    if registry_path is None:
        return PolicyResult(
            policy="hypothesis_registry",
            passed=False,
            checks=[{"item": "HYPOTHESIS_REGISTRY.md exists", "pass": False,
                     "detail": "Not found in project root or docs/"}],
            score="0/2",
        )

    content = registry_path.read_text()
    checks.append({"item": "HYPOTHESIS_REGISTRY.md exists", "pass": True})

    # Parse for hypothesis table rows (lines starting with | H or | HYP or containing hypothesis IDs)
    hyp_rows = re.findall(r'^\|.*(?:H\d+|HYP-?\d+).*\|', content, re.MULTILINE)
    hyp_count = len(hyp_rows)
    checks.append({
        "item": f"≥2 hypotheses registered ({hyp_count} found)",
        "pass": hyp_count >= 2,
        "detail": f"{hyp_count} hypothesis rows found",
    })

    # Check all resolved (no PENDING)
    pending_rows = [r for r in hyp_rows if "PENDING" in r.upper()]
    all_resolved = len(pending_rows) == 0 and hyp_count >= 2
    checks.append({
        "item": "All hypotheses resolved (no PENDING)",
        "pass": all_resolved,
        "detail": f"{len(pending_rows)} PENDING" if pending_rows else "All resolved",
    })

    all_pass = all(c["pass"] for c in checks)
    return PolicyResult(
        policy="hypothesis_registry",
        passed=all_pass,
        checks=checks,
        score=f"{sum(1 for c in checks if c['pass'])}/{len(checks)}",
    )


def check_provenance(project_path: str) -> PolicyResult:
    """Check reproducibility artifacts exist."""
    root = Path(project_path)
    required_files = [
        "provenance/config_resolved.yaml",
        "provenance/versions.txt",
        "provenance/output_manifest.json",
        "provenance/git_info.txt",
    ]
    checks = []

    for relpath in required_files:
        # Accept in provenance/ subdirectory or project root
        in_subdir = (root / relpath).exists()
        filename = Path(relpath).name
        in_root = (root / filename).exists()
        found = in_subdir or in_root
        checks.append({
            "item": relpath,
            "pass": found,
            "detail": f"Found at {'provenance/' if in_subdir else 'root' if in_root else 'MISSING'}",
        })

    all_pass = all(c["pass"] for c in checks)
    return PolicyResult(
        policy="provenance",
        passed=all_pass,
        checks=checks,
        score=f"{sum(1 for c in checks if c['pass'])}/{len(checks)}",
    )


def check_test_coverage(project_path: str, minimum: int | None = None) -> PolicyResult:
    """Count tests and check minimum tiers."""
    root = Path(project_path)
    checks = []

    # Find tests/ directory
    test_dir = root / "tests"
    if not test_dir.exists():
        return PolicyResult(
            policy="test_coverage",
            passed=False,
            checks=[{"item": "tests/ directory exists", "pass": False,
                     "detail": "No tests/ directory found"}],
            score="0/2",
        )

    checks.append({"item": "tests/ directory exists", "pass": True})

    # Count files matching test_*.py
    test_files = list(test_dir.glob("test_*.py"))
    file_count = len(test_files)

    # Count functions matching def test_ in those files
    func_count = 0
    for tf in test_files:
        try:
            content = tf.read_text()
            func_count += len(re.findall(r'^\s*def test_', content, re.MULTILINE))
        except OSError:
            continue

    # Determine threshold from project.yaml profile or parameter
    if minimum is not None:
        threshold = minimum
    else:
        threshold = 25  # default: blog-track
        project_yaml = root / "project.yaml"
        if project_yaml.exists():
            try:
                config = yaml.safe_load(project_yaml.read_text())
                profile = config.get("profile", "")
                if "publication" in str(profile).lower():
                    threshold = 50
            except (yaml.YAMLError, OSError):
                pass

    meets_threshold = func_count >= threshold
    checks.append({
        "item": f"≥{threshold} test functions ({func_count} found in {file_count} files)",
        "pass": meets_threshold,
        "detail": f"{func_count} test functions in {file_count} files (threshold: {threshold})",
    })

    all_pass = all(c["pass"] for c in checks)
    return PolicyResult(
        policy="test_coverage",
        passed=all_pass,
        checks=checks,
        score=f"{sum(1 for c in checks if c['pass'])}/{len(checks)}",
    )


def run_all_checks(project_yaml: str, repo_path: str = ".") -> dict[str, PolicyResult]:
    """Run all governance policy checks on a project."""
    results = {
        "repo_hygiene": check_repo_hygiene(repo_path),
        "publication": check_publication_readiness(repo_path),
        "decision_log": check_decision_log(repo_path),
        "findings_integrity": check_findings_integrity(repo_path),
        "statistical_rigor": check_statistical_rigor(repo_path),
        "learning_curves": check_learning_curves(repo_path),
        "hypothesis_registry": check_hypothesis_registry(repo_path),
        "provenance": check_provenance(repo_path),
        "test_coverage": check_test_coverage(repo_path),
    }

    # Check all defined phases
    config = load_project_config(project_yaml)
    for i, phase in enumerate(config.get("phases", [])):
        results[f"phase_{i}"] = check_phase_gate(project_yaml, i, repo_path)

    return results
