# LinkedIn Post — govML Agent Platform

**Governance that isn't machine-readable isn't governance. It's documentation.**

I've been using govML -- my open-source ML governance framework -- across 7 projects. 32 templates, 7 profiles, 8 generators. It works. Projects scaffold in 10 minutes instead of 60.

But the templates are markdown files that a human reads and fills. AI coding agents don't read markdown. They call tools.

So I built an MCP server that exposes govML governance as 6 tool calls:
- check_phase_gate: verify phase conditions
- scan_repo_hygiene: README, LICENSE, tests
- check_publication: blog draft, figures, abstract
- validate_project: run ALL checks at once

Instead of "read the playbook and check the boxes," the agent calls govml_validate_project and gets structured pass/fail results in JSON.

The real insight isn't the automation. It's the boundary it makes explicit:

AGENT handles: template filling, gate checking, config validation, repo hygiene, ADR formatting, publication checklists.

HUMAN handles: thesis formulation, research question design, finding interpretation, tradeoff judgment, blog voice.

6 agent-safe + 5 human-required = clear boundary.

Setup time across 4 generations:
- FP-01 manual: 60 min
- FP-05 with govML --fill: 30 min
- FP-03 with blog-track: 10 min
- FP-08 with MCP: <5 min (projected)

83% reduction, measured across real projects.

Open source: https://github.com/rexcoleman/govml-agent-platform

#MCP #AIGovernance #MLOps #DeveloperTools #AIEngineering
