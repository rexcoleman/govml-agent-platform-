# Substack Intro — govML Agent Platform

**Subject line:** I built the governance framework my AI uses to govern itself.

**Preview text:** From 60 minutes to 5: what happens when you make governance agent-consumable.

---

I've been building ML projects with govML -- my open-source governance framework -- for 7 projects now. It started as markdown templates. Fill in the blanks, check the boxes, move through phases.

It worked. Setup time dropped from 60 minutes to 10 minutes across three generations of automation.

But then I asked: what if the AI agent could enforce the governance itself?

I built an MCP (Model Context Protocol) server that exposes govML as tool calls. Instead of reading a template and filling placeholders, Claude Code calls `govml_validate_project` and gets structured pass/fail results. Gate checking, repo hygiene, publication readiness -- all automated.

The interesting part isn't the automation. It's the boundary it reveals between what agents should handle and what humans must judge. 6 tasks are agent-safe. 5 require human judgment. Making that boundary explicit is the real governance innovation.

In this post, I'll walk through the MCP architecture, the 4-generation setup time curve, and the meta-lesson: the framework governs the projects, and the projects improve the framework.

[Continue reading...]

---

*This is part of my series on building security and ML infrastructure tools. govML is open source: https://github.com/rexcoleman/govML*
