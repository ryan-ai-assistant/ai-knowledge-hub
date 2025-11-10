---
title: Template – Session Recap
tags: [templates/session-recap, communication/district, tone/human, style/no-extras]
version: 1.0
owner: ryan.brock
inputs:
  - { name: event_name, type: string, required: true }
  - { name: timeframe, type: string, required: true }
  - { name: highlights, type: list, required: true }
  - { name: next_steps, type: list, required: true }
---

# {event_name} — Recap ({timeframe})

## Highlights
{highlights}

## Next Steps
{next_steps}
