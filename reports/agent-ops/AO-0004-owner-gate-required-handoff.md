# AO-0004 owner-gate-required handoff

status: owner-gate-required

issue / draft PR: #198 / #199

branch: `benchmark/treasurebench-provider-schema-conformance`

exact execution commit: `5f1d4b6bdb0d5fce5b4cbfc11f6aceadd910c2c3`

task contract: `tasks/treasurebench-provider-schema-conformance.yml`

ExecPlan: `plans/TREASUREBENCH_PROVIDER_SCHEMA_CONFORMANCE.md`

committed gate manifest: `reports/agent-ops/AO-0004-treasurebench-provider-canary-owner-gate.yml`

exact challenge: `AUTHORIZE AOG-AO-0004-PUBLIC-PROVIDER-CANARIES 5f1d4b6`

exact command:

    make owner-gate GATE=reports/agent-ops/AO-0004-treasurebench-provider-canary-owner-gate.yml OWNER_GATE_CHALLENGE='AUTHORIZE AOG-AO-0004-PUBLIC-PROVIDER-CANARIES 5f1d4b6'

sequence: OpenAI minimal; OpenAI complete; Anthropic minimal; Anthropic complete.

stopping rule: stop immediately on any authorization, credential handling,
privacy, route, model, alias, fallback, schema, safe-error, call-cap, or
spend-cap mismatch, or on a minimal-schema failure. A complete-schema failure
permits only bounded same-provider schema bisection within ten calls, USD 1.00
total, USD 0.50 per provider, and expected aggregate cost below USD 0.10; do
not call the other provider until resolved. Declare conformance only after
both complete schemas pass.

exact resume message:

> Resume AO-0004 at M5 using reports/agent-ops/AO-0004-treasurebench-provider-canary-owner-gate.yml after the owner creates its exact generic authorization. Re-read current official provider terms; validate the authorization, fixed contract, frozen execution commit, PR ancestry, every protected tree, exact direct routes and models, safe credential handling, zero cumulative calls and spend, and remaining caps. Then run OpenAI minimal, OpenAI complete, Anthropic minimal, and Anthropic complete in order. Stop immediately on any mismatch or minimal failure. If a complete schema fails, permit only bounded same-provider schema bisection within ten total calls, USD 1.00 total, USD 0.50 per provider, and expected aggregate cost below USD 0.10; do not call the other provider until resolved. Declare conformance only if both complete schemas pass. Create no private, scientific, paper, ranking, release, submission, or base-campaign state.

observed activity: zero provider calls, USD 0 spend, no credential access, no
private-state change, and no scientific-state change.
