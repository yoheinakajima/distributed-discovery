# Fresh pilot provider audit

Recorded `2026-07-27T02:04:22Z` for `AO-0002`. This was an official-document
audit only: no credential, provider API, private object, or spend was used.

The exact eligible routes remain direct OpenAI Responses with
`gpt-5.4-2026-03-05` and direct Anthropic Messages with
`claude-sonnet-4-6`. Both exact IDs remain officially listed and both support
strict JSON-schema structured output. Standard direct prices are USD 2.50/M
input and USD 15/M output for OpenAI, and USD 3/M input and USD 15/M output
for Anthropic.

OpenAI `store: false` is required, but it does not itself confer Zero Data
Retention; default abuse-monitoring retention may be up to 30 days. Anthropic
documents no default prompt/output retention for the direct API, while a
structured-output schema may be cached for up to 24 hours and exceptional
legal or flagged handling may apply. Neither route is treated as ZDR.

The runtime may make at most two total transport attempts for the identical
idempotent request and at most one schema-only repair. Provider SDK retry
defaults are not additive. Aliases, fallbacks, batch APIs, regional premiums,
provider-managed tools, and route substitution remain excluded. Official
terms must be checked again at resume because they can change after this
freeze.

The machine-readable companion records the exact official source URLs,
retention qualifications, error classes, prices, and decisions.
