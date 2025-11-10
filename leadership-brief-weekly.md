---
title: Leadership Brief – Weekly Status
slug: leadership-brief-weekly
tags: [communication/district, templates/meeting-summary, tone/lisa-damour, style/no-extras]
audience: district_leadership
task_type: summary_and_recommendations
model: GPT-5
version: 1.0
owner: ryan.brock
inputs:
  - { name: district_name, type: string, required: true }
  - { name: timeframe, type: string, required: true }
  - { name: key_metrics, type: table, required: false }
modules:
  - /prompts/_modules/tone/lisa-damour.md
  - /prompts/_modules/structure/meeting-recap.md
  - /prompts/_modules/style/no-extras.md
related:
  - /frameworks/implementation-success.md
---

# Purpose
Produce a board-ready weekly brief summarizing progress, risks, and actions.

# Instructions
1) Use the referenced tone, structure, and style modules.
2) Include Status (R/Y/G), Wins, Risks (with mitigations), Next actions (owner and due).

# Output format
- 1 page, headings: Status, Highlights, Risks & Mitigations, Next 5 Actions
