#!/usr/bin/env bash
set -euo pipefail
echo "=== FP-08: govML Agent Platform — Reproduction ==="

echo "1. Install dependencies"
pip install -e . 2>/dev/null || pip install -r requirements.txt 2>/dev/null || echo "No requirements.txt — dependencies in pyproject.toml"

echo "2. Run tests"
python -m pytest tests/ -v

echo "3. Generate figures"
python scripts/make_report_figures.py

echo "4. Verify MCP server loads"
python -c "from src.mcp_server import TOOL_DEFINITIONS; print(f'{len(TOOL_DEFINITIONS)} MCP tools defined')"

echo "5. Run policy engine checks"
python -c "from src.policy_engine import PolicyEngine; e = PolicyEngine('.'); print('Policy engine loaded')"

echo "=== Reproduction complete ==="
echo "Outputs: outputs/figures/, blog/images/"
