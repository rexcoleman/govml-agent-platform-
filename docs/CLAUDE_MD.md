# govML Agent-Native Governance Platform — Claude Code Context

> **govML v2.5** | Profile: blog-track (blog-track)

## Project Purpose

I Built the Governance Framework My AI Uses to Govern Itself

- **Context:** Self-directed research (govML Agent-Native Governance Platform)
- **Profile:** blog-track
- **Python:** 3.11 | **Env:** govml-platform
- **Brand pillar:** ML Systems Governance
- **Workload type:** io_bound

## Authority Hierarchy

| Tier | Source | Path |
|------|--------|------|
| 1 (highest) | Project Brief | `docs/PROJECT_BRIEF.md` |
| 2 | — | No external FAQ |
| 3 | Advisory methodology | `None` |
| Contracts | Governance docs | `docs/*.md` |

## Current Phase

**Phase:** 0 — Environment & Setup

### Phase Progression

| Phase | Name | Status |
|-------|------|--------|
| 0 | Phase 0 — Environment & Design | **CURRENT** |
| 1 | Phase 1 — MCP Server | Not started |
| 2 | Phase 2 — Policy Engine | Not started |
| 3 | Phase 3 — Findings & Publication | Not started |
| 4 | Phase 4 — Publication Artifacts | Not started |

## Experiment Summary

Seeds: [42]

- **mcp_server:** policy_reader, gate_checker, template_filler
- **policy_engine:** yaml_policies, gate_enforcement

## Key Files

| File | Purpose |
|------|---------|
| `docs/PROJECT_BRIEF.md` | **READ FIRST** — thesis, RQs, scope |
| `docs/PUBLICATION_PIPELINE.md` | Blog post governance + distribution |
| `docs/DECISION_LOG.md` | All tradeoff decisions (mandatory at every phase gate) |
| `config/base.yaml` | Experiment configuration |

## AI Division of Labor

### Permitted
- **Claude Code:** Build the MCP server and policy engine. Meta: Claude Code building the tool that governs Claude Code.
  - Prohibited: Must not modify existing govML templates without CONTRACT_CHANGE. Must not auto-approve phase gates.

### Prohibited (all projects)
- Modifying PROJECT_BRIEF thesis or research questions
- Writing interpretation/analysis prose (human insight)

## Conventions

- **Seeds:** [42]
- **Smoke test first:** `--sample-frac 0.01` or `--dry-run` before full runs
- **Decisions:** Log in DECISION_LOG at every phase gate (mandatory per v2.5)
- **Commit early:** Phase 0a scaffold → commit → Phase 0b research → commit
