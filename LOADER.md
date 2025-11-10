# Loader Behavior (Mode C: Act & Assemble)

1) Identify intent (template vs prompt), then retrieve by tags/slug.
2) Load referenced modules from `prompts/_modules/` (tone, structure, style).
3) Fill placeholders like `{district_name}`, `{timeframe}`, `{audience}`, `{resources}`.
4) Produce final artifact in markdown unless otherwise requested.

**Selection Rules**
- Prefer items whose `tags` match the user request.
- Use `related:` to include frameworks/extra modules.
- If multiple match, summarize choices and pick the best fit.

**Style Guardrails**
- No emojis.
- No em dashes (use commas or semicolons).
- Avoid AI-ish filler phrases. Respect `style/no-extras`.
