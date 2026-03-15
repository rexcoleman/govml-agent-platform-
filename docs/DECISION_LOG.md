# DECISION LOG

<!-- version: 2.0 -->
<!-- created: 2026-02-20 -->
<!-- last_validated_against: CS_7641_Machine_Learning_OL_Report -->

> **Authority Hierarchy**
>
> | Priority | Document | Role |
> |----------|----------|------|
> | Tier 1 | `{{TIER1_DOC}}` | Primary spec — highest authority |
> | Tier 2 | `{{TIER2_DOC}}` | Clarifications — cannot override Tier 1 |
> | Tier 3 | `{{TIER3_DOC}}` | Advisory only — non-binding if inconsistent with Tier 1/2 |
> | Contract | This document | Implementation detail — subordinate to all tiers above |
>
> **Conflict rule:** When a higher-tier document and this contract disagree, the higher tier wins.
> Update this contract via `CONTRACT_CHANGE` or align implementation to the higher tier.

### Companion Contracts

**Upstream (this contract depends on):**
- None — decisions may reference any contract but have no structural dependency.

**Downstream (depends on this contract):**
- See [CHANGELOG](CHANGELOG.tmpl.md) for CONTRACT_CHANGE entries triggered by decisions (cross-reference ADR IDs)
- See [RISK_REGISTER](RISK_REGISTER.tmpl.md) for risk entries mitigated by decisions
- See [IMPLEMENTATION_PLAYBOOK](IMPLEMENTATION_PLAYBOOK.tmpl.md) §5 for change control procedure referencing ADR entries

## Purpose

This log records architectural and methodological decisions for the **govML Agent-Native Governance Platform** project using a lightweight ADR (Architecture Decision Record) format. Each decision captures the context, alternatives, rationale, and consequences so that future changes are informed rather than accidental.

**Relationship to CHANGELOG:** When a decision triggers a `CONTRACT_CHANGE` commit, the change MUST also be logged in CHANGELOG with a cross-reference to the ADR ID.

---

## When to Create an ADR

Create a new ADR when:
- A decision affects multiple contracts or specs
- A decision resolves an ambiguity in authority documents
- A decision involves tradeoffs that future contributors need to understand
- A `CONTRACT_CHANGE` commit is triggered by a methodological choice
- A risk mitigation strategy is selected from multiple options

Do NOT create an ADR for routine implementation choices that follow directly from a single contract requirement with no alternatives.

---

## Status Lifecycle

```
Proposed → Accepted → [Superseded by ADR-YYYY]
```

- **Proposed:** Under discussion; not yet binding.
- **Accepted:** Binding; implementation may proceed.
- **Superseded:** Replaced by a newer ADR. MUST cite the superseding ADR ID. Do NOT delete superseded entries.

---

## Decision Record Template

Copy this block for each new decision:

```markdown
## ADR-XXXX: [Short title]

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by ADR-YYYY

### Context
[Problem statement and constraints. Cite authority documents by tier and section.]

### Decision
[The chosen approach. Be specific enough that someone can implement it without ambiguity.]

### Alternatives Considered

| Option | Description | Verdict | Reason |
|--------|-------------|---------|--------|
| A (chosen) | [approach] | **Accepted** | [why best] |
| B | [approach] | Rejected | [why not] |
| C | [approach] | Rejected | [why not] |

### Rationale
[Why this approach is best given the project constraints. Cite authority documents.]

### Consequences
[Tradeoffs and risks. Reference RISK_REGISTER entries if applicable.]

### Contracts Affected

| Contract | Section | Change Required |
|----------|---------|----------------|
| [contract name] | §N | [what changes] |

### Evidence Plan

| Validation | Command / Artifact | Expected Result |
|------------|-------------------|-----------------|
| [what to verify] | [command or file path] | [pass criteria] |
```

---

## Decisions

*(Record decisions below. Number sequentially: ADR-0001, ADR-0002, etc.)*

---

## ADR-0001: MCP protocol over REST API for governance tool exposure

- **Date:** 2026-03-15
- **Status:** Accepted

### Decision
Implement governance tools as MCP server (JSON-RPC over stdio) rather than REST API. MCP integrates natively with Claude Code via settings.json — no HTTP server to manage.

### Rationale
Claude Code, Cursor, and other AI coding tools support MCP natively. REST would require running a server. MCP starts on demand via stdio. Lower complexity, direct integration, no port management.

---

## ADR-0002: Policy engine reads project.yaml, not governance markdown

- **Date:** 2026-03-15
- **Status:** Accepted

### Decision
Phase gate conditions, repo hygiene requirements, and publication checklists are validated from project.yaml and file system state — not by parsing governance markdown templates.

### Rationale
Markdown parsing is fragile and template-dependent. project.yaml is structured, machine-readable, and already the single source of truth for generators (G1-G17). Extending it for policy enforcement is natural. The markdown docs remain as human-readable documentation; the YAML drives enforcement.
