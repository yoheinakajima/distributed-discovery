# Fresh TreasureBench pilot stopped and quarantined

AO-0002 stopped at its first public-canary request with decision
`sealed-pilot-quarantined-provider-failure`. The retained ledger records one
direct OpenAI request to `gpt-5.4-2026-03-05`, HTTP 400 class
`schema-or-parameter`, zero reported input and output tokens, and USD 0.00.
The failure was terminal and non-retryable under the registered policy.
Anthropic was not called.

The provider phase is closed. Six retained state and encrypted-response
objects are locked and verified under
`sha256:8102a6c1b6bda003336d5503136dfe29301b04cb8f35e7740edd8d56f0eb3c1d`.
The terminal error envelope was inspected only after lock verification. The
frozen adapter did not retain the provider error body, so the public record
does not assign a narrower cause.

No private task seed, task, answer, task key, answer key, task ciphertext,
answer ciphertext, or custody manifest was created. No private
architecture/model run occurred, so Methods A/B/C, metric-range checks, and
private pairing verification were not run. The repaired synthetic 500-run
rehearsal and all 54 registered corruptions remain passing offline evidence.

The R2 authorization is inactive and preserved in mode-`0600` local history.
The failed campaign and batch are quarantined. Any repair or replacement
requires a separately registered, wholly new batch identity and a new exact
owner gate; no retry, merge, Pages deployment, scientific use, ranking,
package, release, or base campaign is authorized here.
