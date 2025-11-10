---
title: Productivity – Ops Checklist
slug: productivity-ops-checklist
tags: [productivity, analytics/internal, style/no-extras, tone/human]
task_type: checklist
model: GPT-5
version: 1.0
owner: ryan.brock
inputs:
  - { name: project_name, type: string, required: true }
  - { name: timeframe, type: string, required: false }
modules:
  - /prompts/_modules/style/no-extras.md
  - /prompts/_modules/tone/human.md
---

# Purpose
Create a clear, minimal checklist to drive execution and follow-through.

# Checklist
- Define objective
- Identify stakeholders
- List milestones and dates
- Risks & mitigations
- Comms plan
- Final review
