# DiscoveryBench Agents v1 evaluation provider audit

Accessed 2026-07-23 from official provider/model sources only. This is a dated
eligibility observation, not provider validation or authorization.

OpenAI `gpt-5.4-2026-03-05` remains an available dated snapshot. Its official
page reports a 1.05M-token context, 128k maximum output, structured outputs,
and $2.50/$0.25/$15 per MTok input/cached-input/output. It is not listed in the
official deprecation table on the access date. The API data-control page says
API data are not used for training by default and the relevant endpoints
normally have 30-day abuse-monitoring retention, subject to verified account
controls.

Anthropic `claude-sonnet-4-6` remains active. Anthropic explicitly documents
dateless 4.6-generation IDs as pinned snapshots, lists retirement no sooner
than 2027-02-17, and reports $3/$0.30/$15 per MTok input/cache-read/output plus
half-price batch processing. Standard API inputs and outputs are normally
deleted within 30 days, subject to the exact account agreement.

Google `gemini-2.5-pro` remains a stable production name with structured
outputs and 1,048,576-token input context, but the stable-name convention is
not accepted as an immutable snapshot guarantee. It remains a blocked reserve.

Mistral Small 3.1 remains available at exact revision
`68faf511d618ef198fef186659617cfd2eb8e33a` under Apache-2.0. The repository
tree is about 96.1 GB. Mistral states it can run on one RTX 4090 or a Mac with
32 GB RAM; no weights were downloaded.

The pilot freezes the two exact cloud identifiers. Neither provider name nor
model family is treated as statistically independent evidence. Account access,
retention, region, rate limits, and authorization must still pass immediately
before execution. Newer model generations are not silently substituted.
