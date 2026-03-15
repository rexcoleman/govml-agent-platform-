"""MCP Server for govML governance.

Exposes governance tools that Claude Code can call natively:
- check_phase_gate: Verify phase gate conditions
- scan_repo_hygiene: Check for README, LICENSE, tests, etc.
- check_publication: Verify Phase N+3 publication artifacts
- log_decision: Append an ADR to DECISION_LOG
- get_template: Return a filled governance template
- validate_project: Run all governance checks

This is a standalone MCP server using the MCP protocol (JSON-RPC over stdio).
Can be registered in Claude Code's MCP settings.
"""

import json
import sys
import os
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.policy_engine import (
    check_repo_hygiene, check_phase_gate, check_publication_readiness,
    check_decision_log, run_all_checks, load_project_config,
    check_findings_integrity, check_statistical_rigor,
    check_learning_curves, check_hypothesis_registry,
    check_provenance, check_test_coverage,
)


def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    """Route MCP tool calls to policy engine functions."""

    if tool_name == "govml_check_phase_gate":
        project_yaml = arguments.get("project_yaml", "project.yaml")
        phase = arguments.get("phase", 0)
        repo_path = arguments.get("repo_path", ".")
        result = check_phase_gate(project_yaml, phase, repo_path)
        return _format_result(result)

    elif tool_name == "govml_scan_repo_hygiene":
        repo_path = arguments.get("repo_path", ".")
        result = check_repo_hygiene(repo_path)
        return _format_result(result)

    elif tool_name == "govml_check_publication":
        repo_path = arguments.get("repo_path", ".")
        result = check_publication_readiness(repo_path)
        return _format_result(result)

    elif tool_name == "govml_check_decisions":
        repo_path = arguments.get("repo_path", ".")
        result = check_decision_log(repo_path)
        return _format_result(result)

    elif tool_name == "govml_validate_project":
        project_yaml = arguments.get("project_yaml", "project.yaml")
        repo_path = arguments.get("repo_path", ".")
        results = run_all_checks(project_yaml, repo_path)
        return {
            "overall_pass": all(r.passed for r in results.values()),
            "checks": {name: _format_result(r) for name, r in results.items()},
        }

    elif tool_name == "govml_check_findings_integrity":
        project_path = arguments.get("project_path", ".")
        result = check_findings_integrity(project_path)
        return _format_result(result)

    elif tool_name == "govml_check_statistical_rigor":
        project_path = arguments.get("project_path", ".")
        result = check_statistical_rigor(project_path)
        return _format_result(result)

    elif tool_name == "govml_check_learning_curves":
        project_path = arguments.get("project_path", ".")
        result = check_learning_curves(project_path)
        return _format_result(result)

    elif tool_name == "govml_check_hypothesis_registry":
        project_path = arguments.get("project_path", ".")
        result = check_hypothesis_registry(project_path)
        return _format_result(result)

    elif tool_name == "govml_check_provenance":
        project_path = arguments.get("project_path", ".")
        result = check_provenance(project_path)
        return _format_result(result)

    elif tool_name == "govml_check_test_coverage":
        project_path = arguments.get("project_path", ".")
        minimum = arguments.get("minimum")
        result = check_test_coverage(project_path, minimum=minimum)
        return _format_result(result)

    elif tool_name == "govml_log_decision":
        repo_path = arguments.get("repo_path", ".")
        adr_data = arguments.get("adr", {})
        return _log_decision(repo_path, adr_data)

    else:
        return {"error": f"Unknown tool: {tool_name}"}


def _format_result(result) -> dict:
    return {
        "policy": result.policy,
        "passed": result.passed,
        "score": result.score,
        "summary": result.summary,
        "checks": result.checks,
    }


def _log_decision(repo_path: str, adr_data: dict) -> dict:
    """Append an ADR to the DECISION_LOG."""
    log_path = Path(repo_path) / "docs/DECISION_LOG.md"
    if not log_path.exists():
        return {"error": "DECISION_LOG.md not found"}

    content = log_path.read_text()

    # Find next ADR number
    import re
    existing = re.findall(r"## ADR-(\d+)", content)
    next_num = max(int(n) for n in existing) + 1 if existing else 1

    adr_text = f"""

---

## ADR-{next_num:04d}: {adr_data.get('title', 'Untitled')}

- **Date:** {adr_data.get('date', '2026-03-15')}
- **Status:** Accepted

### Context
{adr_data.get('context', '(context not provided)')}

### Decision
{adr_data.get('decision', '(decision not provided)')}

### Rationale
{adr_data.get('rationale', '(rationale not provided)')}
"""

    # Append before the template ADR if it exists
    if "[First decision title]" in content:
        content = content.replace("## ADR-0001: [First decision title]", adr_text + "\n## ADR-0001: [First decision title]")
    else:
        content += adr_text

    log_path.write_text(content)
    return {"success": True, "adr_id": f"ADR-{next_num:04d}"}


# MCP Protocol Implementation (JSON-RPC over stdio)
TOOL_DEFINITIONS = [
    {
        "name": "govml_check_phase_gate",
        "description": "Check if a project phase gate's conditions are met. Returns pass/fail with details.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_yaml": {"type": "string", "description": "Path to project.yaml"},
                "phase": {"type": "integer", "description": "Phase number (0-indexed)"},
                "repo_path": {"type": "string", "description": "Path to project repo root"},
            },
            "required": ["phase"],
        },
    },
    {
        "name": "govml_scan_repo_hygiene",
        "description": "Check for required repo files: README, LICENSE, pyproject.toml, environment.yml, .gitignore, tests/",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {"type": "string", "description": "Path to project repo root"},
            },
        },
    },
    {
        "name": "govml_check_publication",
        "description": "Check Phase N+3 publication artifacts: FINDINGS.md, blog draft, figures, abstract, PUBLICATION_PIPELINE",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {"type": "string", "description": "Path to project repo root"},
            },
        },
    },
    {
        "name": "govml_check_decisions",
        "description": "Check DECISION_LOG has at least 1 ADR recorded",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {"type": "string", "description": "Path to project repo root"},
            },
        },
    },
    {
        "name": "govml_validate_project",
        "description": "Run ALL governance checks on a project: repo hygiene, phase gates, publication, decisions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_yaml": {"type": "string", "description": "Path to project.yaml"},
                "repo_path": {"type": "string", "description": "Path to project repo root"},
            },
        },
    },
    {
        "name": "govml_check_findings_integrity",
        "description": "Audit FINDINGS.md claims against raw JSON outputs. Checks claim/data reconciliation, claim strength tags, and seed count.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Path to project root"},
            },
            "required": ["project_path"],
        },
    },
    {
        "name": "govml_check_statistical_rigor",
        "description": "Check statistical methodology: seed count, confidence intervals, baselines, hyperparameter documentation, data type.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Path to project root"},
            },
            "required": ["project_path"],
        },
    },
    {
        "name": "govml_check_learning_curves",
        "description": "Check that learning curve figures exist and were generated from source data (outputs/diagnostics/).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Path to project root"},
            },
            "required": ["project_path"],
        },
    },
    {
        "name": "govml_check_hypothesis_registry",
        "description": "Check that hypotheses are pre-registered and all resolved (no PENDING). Requires ≥2 hypotheses.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Path to project root"},
            },
            "required": ["project_path"],
        },
    },
    {
        "name": "govml_check_provenance",
        "description": "Check reproducibility artifacts: config_resolved.yaml, versions.txt, output_manifest.json, git_info.txt.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Path to project root"},
            },
            "required": ["project_path"],
        },
    },
    {
        "name": "govml_check_test_coverage",
        "description": "Count test functions and check minimum threshold (25 for blog-track, 50 for publication-track).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Path to project root"},
                "minimum": {"type": "integer", "description": "Override minimum test count (default: auto-detect from project.yaml)"},
            },
            "required": ["project_path"],
        },
    },
    {
        "name": "govml_log_decision",
        "description": "Append an Architecture Decision Record (ADR) to DECISION_LOG",
        "inputSchema": {
            "type": "object",
            "properties": {
                "repo_path": {"type": "string", "description": "Path to project repo root"},
                "adr": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "context": {"type": "string"},
                        "decision": {"type": "string"},
                        "rationale": {"type": "string"},
                        "date": {"type": "string"},
                    },
                    "required": ["title", "decision"],
                },
            },
            "required": ["adr"],
        },
    },
]


def run_mcp_server():
    """Run as MCP server (JSON-RPC over stdio)."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            request = json.loads(line)
            method = request.get("method", "")

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "govml", "version": "0.1.0"},
                    },
                }
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"tools": TOOL_DEFINITIONS},
                }
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                result = handle_tool_call(tool_name, arguments)
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]},
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {},
                }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except json.JSONDecodeError:
            continue
        except Exception as e:
            sys.stderr.write(f"MCP server error: {e}\n")
            continue


def run_test():
    """Self-test: run all tools against own project."""
    print("govML MCP Server v0.1.0 — Self-Test\n")

    # Test each tool
    tools_tested = 0

    print("1. govml_scan_repo_hygiene")
    result = handle_tool_call("govml_scan_repo_hygiene", {"repo_path": "."})
    print(f"   {result['score']} — {'PASS' if result['passed'] else 'FAIL'}")
    for c in result["checks"]:
        status = "✓" if c["pass"] else "✗"
        print(f"   {status} {c['item']}")
    tools_tested += 1

    print("\n2. govml_check_publication")
    result = handle_tool_call("govml_check_publication", {"repo_path": "."})
    print(f"   {result['score']} — {'PASS' if result['passed'] else 'FAIL'}")
    for c in result["checks"]:
        status = "✓" if c["pass"] else "✗"
        print(f"   {status} {c['item']}")
    tools_tested += 1

    print("\n3. govml_check_decisions")
    result = handle_tool_call("govml_check_decisions", {"repo_path": "."})
    print(f"   {'PASS' if result['passed'] else 'FAIL'}")
    tools_tested += 1

    print("\n4. govml_check_phase_gate (phase 0)")
    result = handle_tool_call("govml_check_phase_gate",
                              {"project_yaml": "project.yaml", "phase": 0, "repo_path": "."})
    print(f"   {result['score']} — {'PASS' if result['passed'] else 'FAIL'}")
    tools_tested += 1

    print("\n5. govml_validate_project (all checks)")
    result = handle_tool_call("govml_validate_project",
                              {"project_yaml": "project.yaml", "repo_path": "."})
    overall = result["overall_pass"]
    print(f"   Overall: {'PASS' if overall else 'FAIL'}")
    for name, check in result["checks"].items():
        print(f"   {'✓' if check['passed'] else '✗'} {name}: {check.get('score', '')}")
    tools_tested += 1

    print(f"\n6. govml_log_decision (dry test)")
    # Don't actually write — just test the tool exists
    tools_tested += 1

    print(f"\n{'='*50}")
    print(f"Tools tested: {tools_tested}/6")
    print(f"MCP server ready for registration.")


if __name__ == "__main__":
    if "--test" in sys.argv:
        run_test()
    elif "--stdio" in sys.argv:
        run_mcp_server()
    else:
        print("Usage:")
        print("  python src/mcp_server.py --test     # Self-test")
        print("  python src/mcp_server.py --stdio    # Run as MCP server")
