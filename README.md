# govML Agent-Native Governance Platform

MCP server that turns [govML](https://github.com/rexcoleman/govML) from a template library into agent-consumable governance. AI coding agents can enforce phase gates, check repo hygiene, and log decisions through tool calls.

## Quick Start

```bash
git clone https://github.com/rexcoleman/govml-agent-platform.git
cd govml-agent-platform
conda env create -f environment.yml
conda activate govml-platform

# Self-test (runs all 6 tools against this project)
python src/mcp_server.py --test

# Validate any project
python -c "
from src.mcp_server import handle_tool_call
result = handle_tool_call('govml_validate_project', {
    'project_yaml': '/path/to/project.yaml',
    'repo_path': '/path/to/repo'
})
print(result)
"
```

## MCP Tools

| Tool | What It Does |
|------|-------------|
| `govml_check_phase_gate` | Verify phase gate conditions from project.yaml |
| `govml_scan_repo_hygiene` | Check README, LICENSE, pyproject.toml, tests, etc. |
| `govml_check_publication` | Verify blog draft, figures, abstract, PUBLICATION_PIPELINE |
| `govml_check_decisions` | Verify DECISION_LOG has ≥1 ADR |
| `govml_validate_project` | Run ALL checks at once |
| `govml_log_decision` | Append an ADR to DECISION_LOG programmatically |

## Claude Code Integration

Add to `.claude/settings.local.json`:

```json
{
  "mcpServers": {
    "govml": {
      "command": "python",
      "args": ["/path/to/govml-agent-platform/src/mcp_server.py", "--stdio"]
    }
  }
}
```

## Project Governance

Built with [govML](https://github.com/rexcoleman/govML) v2.5 (blog-track profile). Meta: govML governs itself.

## License

MIT
