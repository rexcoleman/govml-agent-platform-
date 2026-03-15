# PROJECT BRIEF — govML Agent-Native Governance Platform

<!-- version: 1.0 -->
<!-- created: 2026-03-15 -->

> **Authority:** Tier 1 (highest)

---

## 1) Thesis Statement

**AI coding agents (Claude Code, Cursor, Copilot) need machine-readable governance — not markdown templates humans read. By building an MCP server that exposes govML policies as tool calls, agents can enforce phase gates, check decisions, and fill templates programmatically. This turns govML from a template library into an agent-native governance platform.**

---

## 2) Research Questions

| # | Question | How | Success Criteria |
|---|----------|-----|-----------------|
| RQ1 | Can govML governance be exposed as MCP tool calls? | Build an MCP server with tools: `check_phase_gate`, `get_template`, `log_decision`, `validate_config`. Test with Claude Code. | MCP server runs, Claude Code can call ≥4 governance tools |
| RQ2 | Can YAML-driven policies replace human-read markdown for gate enforcement? | Define policies in project.yaml that the policy engine checks automatically (e.g., "Phase 0 requires README, LICENSE, tests"). | Policy engine validates ≥5 gate conditions from YAML |
| RQ3 | Does agent-native governance reduce project setup time? | Compare: manual template filling (FP-01 baseline ~30min) vs MCP-assisted filling (target <5min). | ≥50% reduction in setup time |
| RQ4 | What governance decisions should agents make vs humans? | Classify: agent-safe (template filling, gate checking, config validation) vs human-required (thesis, RQ design, finding interpretation). | Clear boundary with ≥5 agent-safe + ≥5 human-required items |

---

## 3) Scope

### In Scope
- MCP server exposing govML governance as tool calls
- YAML-driven policy engine for phase gate enforcement
- Automated template filling from project.yaml
- Decision logging API (agents can log ADRs programmatically)
- Integration test: scaffold a new project using only MCP tools

### Out of Scope
- Modifying existing govML templates (use as-is)
- Building a web UI (CLI + MCP only)
- Multi-user governance (single-developer focus)

### Stretch Goals
- npm package for MCP server distribution
- Claude Code CLAUDE.md auto-configuration from MCP
- Governance dashboard (Streamlit) showing project health across repos

---

## 4) Technical Approach

### Architecture

```
Claude Code / AI Agent
    │
    ├── MCP Tool Calls
    │     check_phase_gate(project_yaml, phase)    → pass/fail + missing items
    │     get_template(profile, template_name)      → filled template content
    │     log_decision(project, adr_data)           → appends to DECISION_LOG
    │     validate_config(project_yaml)             → schema validation result
    │     scan_repo_hygiene(repo_path)              → README/LICENSE/tests check
    │     get_publication_checklist(project)         → Phase N+3 status
    │
    ├── Policy Engine (reads project.yaml)
    │     phase_gates.yaml     → conditions per phase
    │     repo_hygiene.yaml    → required files
    │     publication.yaml     → Phase N+3 checklist
    │
    └── govML Templates (read-only)
          templates/core/*.tmpl.md
          templates/management/*.tmpl.md
          templates/publishing/*.tmpl.md
          profiles/*.txt
```

---

## 5) Skill Cluster Targets

| Cluster | Current | Target | How |
|---------|---------|--------|-----|
| **L** | L4-adj | **L5** | Infrastructure used by other AI builders |
| **P** | P3-adj | **P4** | MCP server = product with Claude Code users |
| **V** | V1 | **V2+** | govML IS the brand |
| **D** | D4 | D4+ | Agent governance boundary documentation |
| **S** | S4-adj | S4 | Supply chain governance for agent dependencies |

---

## 6) Definition of Done

- [ ] MCP server with ≥4 governance tools
- [ ] Policy engine validates ≥5 gate conditions from YAML
- [ ] Integration test: scaffold project via MCP tools
- [ ] Agent-safe vs human-required boundary documented
- [ ] Code on GitHub
- [ ] FINDINGS.md
- [ ] DECISION_LOG with ADRs
- [ ] Blog draft + figures + conference abstract
- [ ] PUBLICATION_PIPELINE filled
- [ ] LESSONS_LEARNED updated
