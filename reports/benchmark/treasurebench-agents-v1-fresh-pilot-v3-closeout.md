# TreasureBench fresh pilot v3 stopped and quarantined

AO-0008 passed both direct-provider public canaries, created wholly fresh
custody, passed its private prefix, and then stopped during the fixed full
batch with decision `fresh-pilot-v3-quarantined-engineering-only`. The
failure is recorded only as the registered public-safe class
`fixed-full-batch-failure`.

The provider phase made 3,067 calls, used 2,304,303 input tokens and 444,085
output tokens, and cost USD 13.1861145: OpenAI USD 4.5952575 and Anthropic
USD 8.590857. These totals remained below the 5,200-call, USD 25 total,
USD 10 OpenAI, and USD 15 Anthropic hard caps.

Provider calls stopped, the provider phase closed, and 3,576 retained objects
were verified under output lock
`sha256:e52055b08ca3a8acb1cfb6ac608c6e601f3c618352900f92bf91c5ffc4718dbb`.
No call followed the lock and no material was unsealed.

The partial private batch is not evaluated or published. Methods A, B, and C,
task-level metrics, pairings, and performance comparisons were not produced
after quarantine because the answer and retained outputs were not unsealed.
The accepted offline 50-task/500-pairing rehearsal and all 71 registered
corruption rejections remain engineering validation of the frozen instrument,
not evidence from this quarantined batch.

No task text, answer, seed, key, prompt, output, raw trace, task-level metric,
performance comparison, ranking, or composite is public. AO-0008 creates no
DD-023, claim, scientific run, paper result, release, submission, or base
campaign. The v3 campaign and batch cannot be retried, repaired, reopened,
reused, rescored, spliced, executed, or reauthorized.
