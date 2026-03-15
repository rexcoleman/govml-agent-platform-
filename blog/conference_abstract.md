# Conference Abstract — NeurIPS ML Ops Workshop / MLSys

## Title
From Templates to Tool Calls: Making ML Governance Agent-Consumable

## Abstract (250 words)

ML project governance frameworks traditionally consist of human-readable documents: checklists, templates, and decision logs. As AI coding agents (Claude Code, Cursor, Copilot) become primary development tools, governance must evolve from documents humans read to policies agents enforce.

We present govML, an open-source ML governance framework (32 templates, 7 profiles, 8 generators), and its evolution into an MCP (Model Context Protocol) server that exposes governance as 6 tool calls. AI agents can verify phase gates, check repository hygiene, validate publication readiness, and log architectural decisions programmatically.

Testing across 7 ML projects spanning AI security, vulnerability prediction, cryptographic analysis, and financial fraud detection, we demonstrate: (1) automated repo hygiene checking caught 19 engineering quality gaps that governance documents missed; (2) project setup time decreased from ~60 minutes (manual) to <10 minutes (agent-assisted) across four framework generations; (3) a clear agent-safe vs. human-required boundary emerges — agents handle 6 mechanical governance tasks while humans retain 5 judgment-dependent tasks (thesis design, finding interpretation, tradeoff decisions, narrative voice, research question formulation).

The key insight is that governance documentation alone doesn't prevent quality drift — only enforcement does. Traditional governance governs research methodology but not engineering quality (README, LICENSE, tests). Agent-consumable governance can enforce both by making policy checks a function call that runs before every commit.

Framework and MCP server are open source.

## Keywords
ML governance, MCP, AI agents, reproducibility, phase gates, decision records, MLOps

## Bio
Rex Coleman is an MS Computer Science student (Machine Learning) at Georgia Tech. Previously 15 years in cybersecurity (FireEye/Mandiant). CFA charterholder. Creator of govML.
