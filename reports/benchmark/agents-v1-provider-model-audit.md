# DiscoveryBench Agents v1 provider/model audit

Audit date: 2026-07-23. Status: candidate audit only; no selection, call,
download, credential use, or cost.

## Result

The registration clears the provider-snapshot stop with two distinct cloud
families that expose fixed model identifiers and one revision-pinned open
candidate:

- OpenAI `gpt-5.4-2026-03-05`;
- Anthropic `claude-sonnet-4-6`; and
- Mistral AI
  `mistralai/Mistral-Small-3.1-24B-Instruct-2503@68faf511d618ef198fef186659617cfd2eb8e33a`.

Google `gemini-2.5-pro` is retained as an audited reserve and is not currently
execution-eligible because Google's official description says stable model
names *usually* do not change rather than guaranteeing an immutable snapshot.
The moving alias `gemini-pro-latest` is prohibited.

Distinct provider names do not prove architectural, statistical, training-data,
or epistemic independence. A future campaign must report model-family contrasts
as descriptive paired contrasts, not independent replications.

## Official-source findings

OpenAI's model page lists the dated GPT-5.4 snapshot, structured outputs, the
1.05M context window, and the dated prices used in the cost envelope. OpenAI's
enterprise privacy page says API data are not used for training by default and
may be retained for up to 30 days absent an eligible zero-data-retention
arrangement.

Anthropic documents that `claude-sonnet-4-6` is itself a pinned model ID even
without a date. Anthropic also warns that serving infrastructure and sampling
logic can change around fixed weights. Structured outputs are supported, and
the dated price used here is $3/MTok input and $15/MTok output. Any future
execution must verify organization-level retention and current model lifecycle.

Google documents `gemini-2.5-pro` as a stable production name and distinguishes
stable names from hot-swapped `latest` aliases. That is not strong enough for
this instrument's immutable-snapshot gate, so the candidate is blocked pending
a stronger version guarantee and retention check.

Mistral's official model card documents Apache-2.0 licensing, native JSON
output/function calling, 128k context, 24B parameters, and local resource
requirements. The audited Hugging Face revision is a metadata reference only;
no model files were downloaded. A future implementation must independently
record every weight-file hash, engine/container version, hardware, and seed.

## Reproducibility and eligibility

Snapshot identity is necessary but insufficient. The future execution manifest
must also freeze endpoint, structured-output mode, prompt/schema hashes,
sampling and reasoning controls, retry policy, region/service tier, SDK/API
versions, and retention configuration. A schema-only compatibility check may
disqualify a candidate; it may not silently substitute a moving alias.

No candidate is authorized by this audit. Eligibility means only that a later,
separately approved implementation may consider it.
