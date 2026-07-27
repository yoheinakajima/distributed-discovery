# TreasureBench Agents v1 provider-schema conformance audit

AO-0004 completed the public-only offline diagnosis and repair boundary. No
credential was read, no provider was called, no private state was accessed,
and spend remains USD 0.

## Bounded diagnosis

The deterministic reconstruction uses the same third public calibration
fixture, lexicographically first agent, provider-native smoke prompt, final
round, model, request parameters, and canonical action schema as the terminal
public canary. Its byte hash is
`sha256:514f96178acb48f54d4f4ad5f66d4131b4109298f5b88b4e01f130b038978fe8`.

The reconstructed OpenAI schema contains four documented unsupported strict
constraints: `maxLength`, `minItems`, `maxItems`, and `uniqueItems`. That is a
bounded diagnosis, not a claim about which keyword the provider named first:
the original raw error body was intentionally not retained, and this task has
not made a replacement call.

The request route and outer shape remain supported: GPT-5.4 lists
`gpt-5.4-2026-03-05` as its current snapshot with Responses and Structured
Outputs; the current Responses OpenAPI accepts `text.format`, `store`, and
`reasoning`; and strict JSON-schema output uses `text.format` with
`type: json_schema`. OpenAI requires every object property to appear in
`required` and `additionalProperties: false` at each object.

Anthropic currently uses `output_config.format`, requires no beta header, and
lists `claude-sonnet-4-6` as a canonical pinned dateless snapshot rather than
an alias. Its structured-output subset supports `minItems` only at 0 or 1 and
does not support the canonical contract's `maxLength`, `maxItems`, or
`uniqueItems`.

## Repair boundary

The canonical action contract is unchanged. Separate OpenAI and Anthropic
compilers remove only unsupported transport keywords. Provider-independent
post-parse validation still enforces message length, proposal cardinality,
uniqueness, exact final cardinality, action and source vocabulary, and all
identity fields. Existing orchestration still enforces exactly one final
record per required agent, keeps non-final proposals out of final scoring,
runs Method C before metrics, and checks metric ranges.

Offline linting rejects unsupported keywords, incomplete `required` arrays,
missing `additionalProperties: false`, malformed empty nested objects, and
schema drift before a paid call. Safe provider errors retain only status,
normalized type/code/parameter, retry eligibility, and a bounded message hash.

## Current official terms

- OpenAI standard GPT-5.4 pricing remains USD 2.50/M input and USD 15/M
  output. `store: false` disables Responses application-state storage but does
  not imply Zero Data Retention; default abuse-monitoring retention may be up
  to 30 days.
- Anthropic standard Sonnet 4.6 pricing remains USD 3/M input and USD 15/M
  output. Structured-output prompts and outputs are not stored, while the
  schema can be cached for up to 24 hours; documented legal or flagged-safety
  exceptions remain.
- Neither adapter relies on SDK retries. Schema/parameter failures are
  terminal; only registered transient classes are retry eligible.

Official sources: [OpenAI GPT-5.4](https://developers.openai.com/api/docs/models/gpt-5.4),
[OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs),
[OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data),
[OpenAI errors](https://developers.openai.com/api/docs/guides/error-codes),
[OpenAI pricing](https://developers.openai.com/api/docs/pricing),
[Anthropic model IDs](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions),
[Anthropic structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs),
[Anthropic retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention),
[Anthropic errors](https://platform.claude.com/docs/en/api/errors), and
[Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing).

## Stop

The mock matrix is fixed as minimal OpenAI, complete OpenAI, minimal
Anthropic, complete Anthropic. A complete-schema failure may trigger only
bounded same-provider schema bisection within the later exact owner gate.
Conformance cannot be declared until both complete schemas pass. AO-0004 now
proceeds only to the exact execution freeze and generic owner-gate handoff; it
must stop before credentials or provider calls.
