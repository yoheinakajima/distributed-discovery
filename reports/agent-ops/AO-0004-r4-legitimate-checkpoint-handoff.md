# AO-0004 R4 conformance checkpoint

Status: `legitimate-checkpoint`

R4 completed at frozen execution commit
`dcd89bca5daa54386df163439a010583c30134ec` under gate
`AOG-AO-0004-PUBLIC-PROVIDER-CANARIES-R4`.

All four ordered canaries passed:

1. OpenAI minimal: `success`, 66 input and 16 output tokens, USD 0.000405.
2. OpenAI complete: `success`, 465 input and 108 output tokens, USD 0.0027825.
3. Anthropic minimal: `success`, 188 input and 8 output tokens, USD 0.000684.
4. Anthropic complete: `success`, 884 input and 143 output tokens, USD 0.004797.

Both complete outputs passed the transport schema and the provider-independent
semantic action contract, including exactly one final action. Frozen bisection
did not run. The terminal decision is
`conformance-pass-both-complete-schemas`.

Total: four calls, 1,603 input tokens, 275 output tokens, 1,878 tokens, and USD
0.0086685. OpenAI cost USD 0.0031875; Anthropic cost USD 0.005481.

The R4 public ledger is
`reports/benchmark/treasurebench-provider-schema-canaries/AO-0004-public-engineering-ledger-r4.jsonl`
at
`sha256:057e23edb9f3f6e92ee2881ed6cef125f5252fdf5777483f504be6e371efa91d`.
Its nine records form a valid safe hash chain with no open intent. Credentials
and adapter secrets were cleared. Private and scientific state remained
unchanged.

R3 remains byte-identical: gate `650b179a…dcb0`, ledger `687ea038…4be`, and
outcome `f55bc579…b0d`.

R4 is consumed and does not authorize a rerun, repair, PR state change, merge,
issue closure, CI action, or Pages deployment. If the owner wants AO-0004
closed and draft PR #199 merged, the exact next owner action is to direct
registration and authorization of a separate public-only AO-0004 closeout and
PR-merge gate. There is no authorized next command under R4.
