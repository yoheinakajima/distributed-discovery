# AO-0004 R4 owner gate required

Status: `owner-gate-required`

Issue: `#198`

Draft PR: `#199`

Branch: `benchmark/treasurebench-provider-schema-conformance`

Frozen R4 execution commit:
`dcd89bca5daa54386df163439a010583c30134ec`

Current validated PR head:
`366d03400765535705f0a8849678f2ecfd0189ad`

R4 gate:
`reports/agent-ops/AO-0004-treasurebench-provider-canary-owner-gate-r4.yml`

Fresh R4 ledger:
`reports/benchmark/treasurebench-provider-schema-canaries/AO-0004-public-engineering-ledger-r4.jsonl`

Required challenge:

    AUTHORIZE AOG-AO-0004-PUBLIC-PROVIDER-CANARIES-R4 dcd89bc

Exact noninteractive owner-gate command:

    make owner-gate \
      GATE=reports/agent-ops/AO-0004-treasurebench-provider-canary-owner-gate-r4.yml \
      OWNER_GATE_CHALLENGE='AUTHORIZE AOG-AO-0004-PUBLIC-PROVIDER-CANARIES-R4 dcd89bc'

After that exact authorization succeeds, the committed execution command is:

    make treasurebench-provider-schema-canaries

Exact resume message:

> Resume AO-0004 in this same Codex session, issue #198, branch benchmark/treasurebench-provider-schema-conformance, ExecPlan, and draft PR #199. Use only reports/agent-ops/AO-0004-treasurebench-provider-canary-owner-gate-r4.yml and its exact R4 authorization. Do not use, reactivate, append, or mutate R1, R2, or consumed R3 gates, authorizations, ledgers, or outcomes. Re-read current official provider terms; validate the R4 authorization, issue, PR, branch, execution commit, contract hash, every protected tree hash, exact repository-root .env.txt source and two-name allowlist, direct routes and pinned models, zero R4 calls and spend, fresh R4 ledger state, 256-token ceilings, fixed diagnostics, and remaining caps. Then run exactly make treasurebench-provider-schema-canaries. Stop immediately on any mismatch, open call intent, cap boundary, credential-source violation, unsafe diagnostic, or minimal-schema failure. If a complete schema fails, permit only the two frozen same-provider bisection calls in order; do not call the other provider. Declare conformance only if both R4 complete schemas pass. Create no private, scientific, paper, ranking, release, submission, or base-campaign state.

R4 remains at zero calls and USD 0. R3 remains terminal and byte-identical:
gate `650b179a…dcb0`, ledger `687ea038…4be`, outcome `f55bc579…b0d`.
The worst projected R4 path is six calls and USD 0.041893; hard caps remain
ten calls, USD 1.00 total, and USD 0.50 per provider.

PR merge, issue closure, and Pages deployment require separate owner
authorization and are not permitted by this gate.
