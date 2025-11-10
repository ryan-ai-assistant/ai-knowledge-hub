---
title: Analytics – Internal Assessment Summary
slug: analytics-internal-assessment-summary
tags: [analytics/internal, education, style/no-extras, tone/professional]
task_type: analysis_and_summary
model: GPT-5
version: 1.0
owner: ryan.brock
inputs:
  - { name: timeframe, type: string, required: true }
  - { name: dataset_overview, type: string, required: true }
  - { name: key_findings, type: list, required: false }
modules:
  - /prompts/_modules/tone/professional.md
  - /prompts/_modules/style/no-extras.md
---

# Purpose
Summarize assessment outcomes and identify actionable insights for internal teams.

# Instructions
- Provide a concise overview, then 3–5 insights with implications.
- Suggest next steps with owners and deadlines.
