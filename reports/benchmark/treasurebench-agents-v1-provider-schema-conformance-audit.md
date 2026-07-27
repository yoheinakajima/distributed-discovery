# TreasureBench Agents v1 provider-schema conformance audit

AO-0004 completed the corrected public-only offline diagnosis and repair
boundary. No credential was read, no provider was called, no private state was
accessed, and spend remains USD 0.

## Bounded diagnosis

The deterministic reconstruction uses the same third public calibration
fixture, lexicographically first agent, provider-native smoke prompt, final
round, model, request parameters, and canonical action schema as the terminal
public canary. Its byte hash is
`sha256:514f96178acb48f54d4f4ad5f66d4131b4109298f5b88b4e01f130b038978fe8`.

For the pinned standard snapshot `gpt-5.4-2026-03-05`, the current OpenAI
documentation lists array `minItems` and `maxItems` as supported. Their
additional exclusion applies to fine-tuned models and does not apply here.
The reconstructed schema's `maxLength` and `uniqueItems` are outside the
documented standard-model subset.

The historical HTTP 400 cause remains unresolved. It is consistent with one
or both of those omitted constraints or another parameter or schema-complexity
interaction, but the original raw error body was intentionally not retained
and this task has made no replacement call. This audit does not attribute the
failure to `minItems` or `maxItems`, does not claim that all four historical
keywords were unsupported, and does not identify a first rejected keyword.

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

The canonical action contract is unchanged. The OpenAI compiler retains
`minItems: 1` and `maxItems: 1` in the complete final-action transport schema,
and omits only `maxLength` and `uniqueItems`. The Anthropic compiler continues
to omit only constraints outside that transport's subset.
Provider-independent post-parse validation independently enforces message
length, proposal cardinality, uniqueness, exact final cardinality, action and
source vocabulary, and all identity fields. Existing orchestration still
enforces exactly one final record per required agent, keeps non-final
proposals out of final scoring, runs Method C before metrics, and checks
metric ranges.

Offline linting rejects unsupported keywords, incomplete `required` arrays,
missing `additionalProperties: false`, malformed empty nested objects, and
schema drift before a paid call. Safe provider errors retain only status,
normalized type/code/parameter, retry eligibility, and a bounded message hash.

## Credential-ingress boundary

The exact Make command now uses the repository's strict, nonexecuting dotenv
parser directly against repository-root `.env.txt`; it never sources or
executes that file. Live mode first validates the exact R3 authorization,
issue, PR, branch, execution commit, contract and protected trees, then the
append-only ledger sequence and open-intent state, then the exact next call and
both projected-cost guards. Only after those checks may it inspect credential
file metadata and parse the file.

The loader requires a regular non-symlink with no group or world permission
bits and returns only `OPENAI_API_KEY` and `ANTHROPIC_API_KEY`. Every other
name and value is discarded from the returned object and cannot enter a
request, representation, ledger, safe error, or trace. The two selected values
are cleared immediately after each call and again in cleanup. All repair tests
use synthetic credential files or injected mappings; the protected real file
was not read.

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

The committed runner sequence is fixed as minimal OpenAI, complete OpenAI,
minimal Anthropic, complete Anthropic. A minimal failure stops immediately. A
complete-schema failure permits exactly two precommitted same-provider
bisection schemas, in deterministic order, within the ten-call and spend caps;
the other provider remains blocked. No ad-hoc schema edits are allowed after a
failure. Conformance cannot be declared until both complete schemas pass.
AO-0004 now proceeds only to the credential-ingress execution freeze and R3
owner-gate handoff; it must stop before credential-file access or provider
calls.
