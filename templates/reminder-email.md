---
title: Template – Reminder Email (External)
tags: [templates/reminder-email, communication/district, communication/internal/email, tone/human, style/no-extras]
version: 1.0
owner: ryan.brock
inputs:
  - { name: audience, type: string, required: true }
  - { name: event_name, type: string, required: true }
  - { name: session_date, type: date, required: true }
  - { name: logistics, type: list, required: false }
  - { name: resources, type: list, required: false }
---

Subject: Reminder — {event_name} on {session_date}

Hello {audience},

This is a brief reminder for {event_name} on {session_date}.
Key details:
- {logistics}

Resources:
{resources}

Thank you,
Ryan
