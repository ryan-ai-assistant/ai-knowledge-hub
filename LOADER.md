# Loader Behavior for ChatGPT (Mode C: Act & Assemble)

When the user asks for an artifact (e.g., "Write an external meeting summary for Pender County, this week"),
the assistant should:

1. Identify **intent** (template vs. freeform prompt).
2. Retrieve the most relevant **template** and/or **prompt** by tags and/or slug.
3. Load referenced **modules** from `prompts/_modules/` (tone, structure, style, disclaimers).
4. Fill **placeholders** in the prompt or template using user-provided inputs and context.
5. Produce the final artifact in the requested format (markdown by default).

### Selection Rules
- Prefer items whose `tags` match the user request's domain and audience.
- Use `related:` metadata to include relevant frameworks or modules.
- If multiple candidates match, summarize options and choose the best fit.

### Tone & Style
- Respect `tone/*` and `style/*` modules whenever referenced.
- Never add emojis.
- Never use em dashes; use commas or semicolons instead.
- Follow banned-phrases guidance in `prompts/_modules/style/no-extras.md`.

### Placeholders
Replace variables like `{district_name}`, `{timeframe}`, `{audience}`, `{metric}`. If not provided, ask for the missing minimal set of inputs.

### Output
- Produce clean, concise, professional output.
- Mirror any `Output format` section from the prompt/template.
