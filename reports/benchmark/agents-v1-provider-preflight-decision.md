# DiscoveryBench Agents v1 provider-preflight decision

Issue #175 completed the authorized public-only provider preflight and
engineering calibration. The final decision is
`all-required-providers-ready-public-calibration-complete`.

Direct OpenAI `gpt-5.4-2026-03-05` and direct Anthropic
`claude-sonnet-4-6` both passed provider-native structured-output smoke tests,
one tiny public end-to-end task, and the complete registered public calibration
of ten tasks across five architectures. Each route completed 50 public cases.
Method A and the independent Method B agree, protocol compliance passes, and
the contamination probes are clear.

The OpenAI calibration used 294 calls, 132,000 input tokens, 32,975 output
tokens, and USD 0.8246250. The Anthropic calibration used 296 calls, 257,281
input tokens, 43,808 output tokens, and USD 1.428963. Including every preserved
failed and passing preflight attempt, the cumulative ledger is 607 calls and
USD 2.311758000 against the USD 20 authorization cap, leaving USD
17.688242000.

The optional OpenRouter routes are not campaign substitutes. The exact
Google-hosted Gemini endpoint was rejected under the frozen data-denial, ZDR,
required-parameter, and no-fallback policy. The discovered Mistral endpoint did
not support the required structured-output parameter. OpenRouter therefore
contributes neither direct-gateway diversity nor the registered local/open
baseline.

All retained artifacts are public operational engineering records, not
scientific evidence. No private task, seed, answer, holdout, custody material,
sealed pilot, base campaign, provider ranking, leaderboard, composite score, or
paper action was created. The next gate is a separately registered and
owner-authorized sealed engineering pilot; this decision does not authorize it.
