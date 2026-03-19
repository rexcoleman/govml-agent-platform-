# Hypothesis Registry — govML Agent Platform (FP-08)

> Pre-registered hypotheses with outcomes. This is an infrastructure/tooling
> project, so hypotheses are validated by demonstration and test coverage
> rather than statistical testing.

| ID | Hypothesis | Metric | Threshold | Status | Evidence |
|----|-----------|--------|-----------|--------|----------|
| H-1 | A YAML-driven policy engine can enforce ML project governance checks without manual auditing | Number of automated checks passing on real projects | >=9 distinct check types | DEMONSTRATED | Policy engine implements 9 check types (repo_hygiene, publication_readiness, decision_log, findings_integrity, statistical_rigor, learning_curves, hypothesis_registry, provenance, test_coverage) all automated and callable via both CLI and MCP |
| H-2 | MCP protocol enables Claude Code to invoke governance checks natively during development | Number of MCP tools routable via handle_tool_call | >=11 tools | DEMONSTRATED | 11 MCP tools defined and routable: check_phase_gate, scan_repo_hygiene, check_publication, check_decisions, validate_project, check_findings_integrity, check_statistical_rigor, check_learning_curves, check_hypothesis_registry, check_provenance, check_test_coverage, log_decision |
| H-3 | Governance automation reduces audit cycle time compared to manual review | Proxy: number of checks automatable vs requiring manual intervention | >80% automatable | DEMONSTRATED | 9 of 11 checks are fully automated (82%). Only phase_gate checks with non-file commands require manual verification. Test suite validates all automated paths |

## Lock Commit

`b5284dc` — all hypotheses resolved at this commit.

## Resolution Key

- **DEMONSTRATED**: Directly observable from code behavior and test suite
- **SUPPORTED**: Evidence confirms hypothesis at stated threshold
- **REFUTED**: Evidence contradicts hypothesis
- **PENDING**: Not yet tested
