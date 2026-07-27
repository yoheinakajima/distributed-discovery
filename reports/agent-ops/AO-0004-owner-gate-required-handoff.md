# AO-0004 stop-by-policy handoff

status: `stop-by-policy`

issue / draft PR: #198 / #199

branch: `benchmark/treasurebench-provider-schema-conformance`

frozen execution commit: `1048c502b205346fef70b06c76975b6ff06b0241`

authorized PR head: `3f4cd54ea724d40cdaae129e8c383700f1f10cdf`

public outcome commit: `fe0377c988b9154cfe9ad906c4025a1e9ec92f22`

outcome record:
`reports/agent-ops/AO-0004-public-provider-canary-outcome.yml`

ledger:
`reports/benchmark/treasurebench-provider-schema-canaries/AO-0004-public-engineering-ledger.jsonl`

final decision:
`stopped-complete-schema-failure-after-fixed-bisection`

Conformance was not declared.

## Calls

| # | Canary | Provider | Role | Status | Input | Output | Cost USD |
|---:|---|---|---|---|---:|---:|---:|
| 1 | `openai-minimal-known-valid` | OpenAI | minimal | success | 66 | 16 | 0.000405 |
| 2 | `openai-treasurebench-complete` | OpenAI | complete | success | 465 | 109 | 0.0027975 |
| 3 | `anthropic-minimal-known-valid` | Anthropic | minimal | success | 188 | 8 | 0.000684 |
| 4 | `anthropic-treasurebench-complete` | Anthropic | complete | invalid | 884 | 128 | 0.004572 |
| 5 | `anthropic-bisection-action-cardinality` | Anthropic | bisection | success | 261 | 12 | 0.000963 |
| 6 | `anthropic-bisection-identity-envelope` | Anthropic | bisection | success | 244 | 17 | 0.000987 |

Totals: six calls; 2,108 input tokens; 290 output tokens; 2,398 total
tokens; USD 0.0104085. OpenAI cost USD 0.0032025; Anthropic cost USD
0.007206.

Frozen bisection ran: yes, exactly two Anthropic calls in the committed order.

The complete Anthropic response returned HTTP 200 but failed local
complete-output validation. Its only retained diagnostic is
`sha256:00fb2714029c9ea950ea278d8b6549216f549c106d6f80fd03f096be142f9e35`.
All other calls retained the safe `none` error classification. No raw output
or raw error body was retained for the invalid response, so the exact defect
remains unresolved beyond this bounded diagnosis.

All six schema fingerprints, output hashes, token counts, costs, safe errors,
and stopping decisions are in the outcome record and hash-chained ledger.
The ledger validates with zero open call intents.

Credentials were loaded only from repository-root `.env.txt`, with only
`OPENAI_API_KEY` and `ANTHROPIC_API_KEY` requested. Selected credential sets
and adapter secrets were cleared after every provider attempt and in final
cleanup. No unrelated credential was returned, transmitted, or retained.

Private and scientific state remained unchanged. No campaign, task, seed,
answer, key, ciphertext, custody object, private run, claim, scientific run,
evidence, proof, paper, ranking, release, submission, or base-campaign state
was created or changed.

## Exact next owner action

Do not rerun R3 and do not repair execution-sensitive code under its
authorization.

The owner must choose one of two separately authorized paths:

1. Accept the stopped public-provider non-conformance and separately register
   and authorize a public closeout/PR-merge gate; or
2. Direct a repaired execution freeze and new exact owner gate before any
   further provider call.

The current task contract authorizes neither PR merge nor Pages deployment.
There is no currently authorized closeout, merge, issue-closure, Pages, or
further-provider command.
