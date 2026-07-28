# TreasureBench fresh pilot v2 stopped and quarantined

AO-0006 completed its two direct-provider public canaries, then stopped at
custody creation with decision
`fresh-pilot-v2-quarantined-engineering-only`. The two successful canary calls
used 1,349 input tokens and 253 output tokens and cost USD 0.0076095: OpenAI
USD 0.0027975 and Anthropic USD 0.004812. No private architecture/model run
occurred.

The failure is recorded only as the registered public-safe class
`custody-creation-failure`. Provider calls stopped immediately. The provider
phase is closed, and eight safely lockable objects are preserved under output
lock
`sha256:127a9c796459c7627f6fd90b92ef1587ad0f6b1910b4ff255c2ceb976f3ab25f`.
No call followed the lock and no material was unsealed.

A new OS-CSPRNG seed and task and answer keys were created in the retained
private state, but no task ciphertext, answer ciphertext, or custody manifest
was created. The selected OpenAI and Anthropic credential values were cleared;
no unrelated configured credential was returned or transmitted.

Methods A, B, and C, metric-range checks, and private pairing verification
were not run because the private batch never began. The accepted offline
50-task/500-run rehearsal and all 69 registered corruption rejections remain
engineering validation of the frozen instrument, not evidence from this
quarantined batch.

No task text, answer, seed, key, prompt, output, raw trace, task-level metric,
performance comparison, ranking, or composite is public. AO-0006 creates no
DD-023, claim, scientific run, paper result, release, submission, or base
campaign. The v2 campaign and batch cannot be retried, repaired, reopened,
reused, rescored, spliced, executed, or reauthorized.
