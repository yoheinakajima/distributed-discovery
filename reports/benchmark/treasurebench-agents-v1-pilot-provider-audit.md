# TreasureBench Agents v1 pilot provider audit

Checked 2026-07-24 against official provider documentation.

- OpenAI: exact snapshot `gpt-5.4-2026-03-05`, Responses API structured
  outputs, and standard token prices USD 2.50/M input and USD 15/M output were
  confirmed on the official
  [GPT-5.4 model page](https://developers.openai.com/api/docs/models/gpt-5.4).
- Anthropic: exact pinned model `claude-sonnet-4-6`, structured output through
  `output_config.format`, active status, and USD 3/M input and USD 15/M output
  were confirmed in the official
  [models overview](https://platform.claude.com/docs/en/about-claude/models/overview),
  [structured outputs documentation](https://platform.claude.com/docs/en/build-with-claude/structured-outputs),
  and [pricing documentation](https://platform.claude.com/docs/en/about-claude/pricing).

Newer provider models do not alter the frozen pilot identity. No moving alias,
fallback, OpenRouter route, or local model is eligible. This audit made no API
call and is provider-availability engineering metadata, not performance or
scientific evidence.
