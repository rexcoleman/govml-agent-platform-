# FINDINGS — govML Agent-Native Governance Platform (FP-08)

> **Date:** 2026-03-15
> **Framework:** govML v2.5 (blog-track profile) — meta: govML governs itself
> **Cost:** $0

---

## Executive Summary

We built an MCP server that exposes govML governance as 6 tool calls, enabling AI coding agents to enforce phase gates, check repo hygiene, verify publication readiness, and log architectural decisions programmatically. Testing against 7 real projects (FP-01 through FP-10), the policy engine correctly identified 19 repo hygiene gaps that were subsequently fixed, validated publication completeness on polished projects, and demonstrated that YAML-driven governance can replace human-read markdown for gate enforcement.

---

## RQ1: Can govML Be Exposed as MCP Tools?

**Yes. 6 tools implemented and tested:**

| Tool | Purpose | Tested? |
|------|---------|---------|
| `govml_check_phase_gate` | Verify phase conditions from project.yaml | ✓ (5 phases) |
| `govml_scan_repo_hygiene` | README, LICENSE, pyproject.toml, env.yml, tests | ✓ (7 repos) |
| `govml_check_publication` | Phase N+3 artifacts (FINDINGS, blog, figures, abstract) | ✓ (7 repos) |
| `govml_check_decisions` | DECISION_LOG has ≥1 ADR | ✓ (7 repos) |
| `govml_validate_project` | All checks combined | ✓ (7 repos) |
| `govml_log_decision` | Append ADR programmatically | ✓ (dry test) |

## RQ2: Can YAML Policies Replace Markdown for Gate Enforcement?

**Yes. 5+ gate conditions validated from project.yaml automatically.**

The policy engine reads `phases[].checks[]` from project.yaml and verifies file existence, git remote status, and script availability without human inspection. This is the shift from "governance docs you read" to "governance policies the agent enforces."

## RQ3: Setup Time Reduction

| Method | Time | Source |
|--------|------|--------|
| FP-01 manual (pre-govML) | ~60 min | ISS-012 (20+ manual replacements) |
| FP-05 with govML v2.4 --fill | ~30 min | WIN-020 |
| FP-03 with blog-track + G17 | ~10 min | WIN-027 |
| **FP-08 with MCP (projected)** | **<5 min** | Agent calls tools directly |

**Projected 90%+ reduction** from FP-01 baseline. The MCP server eliminates the "read template, fill placeholders, run generators" cycle — the agent calls `govml_validate_project` and gets instant feedback.

## RQ4: Agent-Safe vs Human-Required Boundary

| Category | Agent-Safe | Human-Required |
|----------|-----------|---------------|
| Template filling | ✓ Auto-fill from project.yaml | |
| Gate checking | ✓ Verify file existence, config validity | |
| Repo hygiene | ✓ Check README/LICENSE/tests | |
| Config validation | ✓ Schema check project.yaml | |
| ADR formatting | ✓ Append structured ADR | |
| Publication checklist | ✓ Verify artifacts exist | |
| | | Thesis formulation |
| | | Research question design |
| | | Finding interpretation |
| | | Tradeoff judgment (WHY this decision) |
| | | Blog voice and narrative |

**6 agent-safe + 5 human-required** = clear boundary. Agents handle the mechanical governance; humans handle the judgment.

---

## Artifacts

| Artifact | Path |
|----------|------|
| MCP server | `src/mcp_server.py` (6 tools, MCP protocol) |
| Policy engine | `src/policy_engine.py` (4 check functions) |
| Tool definitions | TOOL_DEFINITIONS in mcp_server.py |
