# PUBLICATION PIPELINE — govML Agent-Native Platform

<!-- version: 2.0 -->
<!-- created: 2026-03-15 -->

## 1) Target Venue
- [x] Blog (Hugo canonical)
- [x] Conference: NeurIPS ML Ops Workshop / MLSys
- [x] LinkedIn (govML is the brand)

## 2) Content Identity

| Property | Value |
|----------|-------|
| **Title** | I Built the Governance Framework My AI Uses to Govern Itself |
| **Pillar** | ML Systems Governance (35%) — this IS the pillar |
| **Audience** | P1: ML engineers using AI coding agents. P2: MLOps teams. P3: AI hiring managers. |
| **Thesis** | Governance that isn't machine-readable isn't governance — it's documentation. MCP makes governance a function call. |
| **Shipped** | github.com/rexcoleman/govml-agent-platform |

### Voice Check
| Test | Pass? |
|------|-------|
| References built artifact | [x] MCP server with 6 tools, tested on 7 projects |
| Shows work | [x] Setup time data, tool call results, agent boundary |
| Avoids pundit framing | [x] "My AI Uses to Govern Itself" = meta builder story |
| Architecture diagram | [x] Setup time chart + agent boundary |
| Links to repo | [x] |

## 4) Evidence Inventory

| Claim | Source |
|-------|--------|
| 6 MCP tools implemented | `src/mcp_server.py` TOOL_DEFINITIONS |
| Setup time 60→5 min (90% reduction) | FINDINGS.md §RQ3 |
| 19 hygiene gaps caught | ISS-048 audit |
| 6 agent-safe + 5 human-required | FINDINGS.md §RQ4 |
| 7 projects validated | Self-test output |

## 5) Distribution
- [ ] Hugo, Substack, dev.to, Hashnode, LinkedIn, HN (pending brand infra)
