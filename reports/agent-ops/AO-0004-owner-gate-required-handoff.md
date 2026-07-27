# AO-0004 owner-gate-required handoff

status: owner-gate-required

issue / draft PR: #198 / #199

branch: `benchmark/treasurebench-provider-schema-conformance`

corrected frozen execution commit: `319bdea525e2bc09feaf481216d3633528158092`

validated R2 manifest / PR head: `055fbebef7e2dd1a335930c353c93d00259fdcda`

task contract: `tasks/treasurebench-provider-schema-conformance.yml`

ExecPlan: `plans/TREASUREBENCH_PROVIDER_SCHEMA_CONFORMANCE.md`

committed gate manifest: `reports/agent-ops/AO-0004-treasurebench-provider-canary-owner-gate-r2.yml`

exact challenge: `AUTHORIZE AOG-AO-0004-PUBLIC-PROVIDER-CANARIES-R2 319bdea`

exact noninteractive owner-gate command:

    make owner-gate GATE=reports/agent-ops/AO-0004-treasurebench-provider-canary-owner-gate-r2.yml OWNER_GATE_CHALLENGE='AUTHORIZE AOG-AO-0004-PUBLIC-PROVIDER-CANARIES-R2 319bdea'

exact committed canary execution command, only after that authorization:

    make treasurebench-provider-schema-canaries

sequence: OpenAI minimal; OpenAI complete; Anthropic minimal; Anthropic complete.

stopping rule: stop immediately on any authorization, credential handling,
privacy, route, model, alias, fallback, schema, safe-error, call-cap, or
spend-cap mismatch, open call intent, or minimal-schema failure. A
complete-schema failure permits exactly the two committed same-provider
bisection schemas in deterministic order within ten calls, USD 1.00 total,
USD 0.50 per provider, and expected aggregate cost below USD 0.10; no ad-hoc
schema edit is allowed and the other provider remains blocked. Declare
conformance only after both complete schemas pass.

exact resume message:

> Resume AO-0004 in this same Codex session, issue #198, branch benchmark/treasurebench-provider-schema-conformance, ExecPlan, and draft PR #199. Use only reports/agent-ops/AO-0004-treasurebench-provider-canary-owner-gate-r2.yml and its exact R2 authorization. Do not use the superseded R1 gate. Re-read current official provider terms; validate the R2 authorization, issue, PR, branch, execution commit, contract hash, every protected tree hash, exact routes and models, zero cumulative calls and spend, and remaining caps. Then run exactly make treasurebench-provider-schema-canaries. Stop immediately on any mismatch, open call intent, cap boundary, or minimal-schema failure. If a complete schema fails, permit only the two frozen same-provider bisection calls in order; do not call the other provider. Declare conformance only if both complete schemas pass. Create no private, scientific, paper, ranking, release, submission, or base-campaign state.

observed activity: zero credential reads, zero provider calls, USD 0 spend, no
private-state access or change, and no scientific-state change. The superseded
R1 gate was never authorized and cannot be consumed.
