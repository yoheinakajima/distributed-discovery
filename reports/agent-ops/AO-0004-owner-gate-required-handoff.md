# AO-0004 owner-gate-required handoff

status: owner-gate-required

issue / draft PR: #198 / #199

branch: `benchmark/treasurebench-provider-schema-conformance`

corrected frozen execution commit: `1048c502b205346fef70b06c76975b6ff06b0241`

validated R3 manifest / PR head: `218db832f834748c1db5d001a310b314454ac719`

task contract: `tasks/treasurebench-provider-schema-conformance.yml`

ExecPlan: `plans/TREASUREBENCH_PROVIDER_SCHEMA_CONFORMANCE.md`

committed gate manifest: `reports/agent-ops/AO-0004-treasurebench-provider-canary-owner-gate-r3.yml`

exact challenge: `AUTHORIZE AOG-AO-0004-PUBLIC-PROVIDER-CANARIES-R3 1048c50`

exact noninteractive owner-gate command:

    make owner-gate GATE=reports/agent-ops/AO-0004-treasurebench-provider-canary-owner-gate-r3.yml OWNER_GATE_CHALLENGE='AUTHORIZE AOG-AO-0004-PUBLIC-PROVIDER-CANARIES-R3 1048c50'

exact committed canary execution command, only after that authorization:

    make treasurebench-provider-schema-canaries

sequence: OpenAI minimal; OpenAI complete; Anthropic minimal; Anthropic complete.

credential ingress: only after R3 authorization plus issue, PR, branch,
execution commit, contract, protected-tree, ledger-next-state, and
projected-cap checks, read only repository-root `.env.txt` with the strict
nonexecuting parser, requesting only `OPENAI_API_KEY` and
`ANTHROPIC_API_KEY`. Do not source, execute, interpolate, use process
environment ingress, or retain values. Clear the exact set and adapter secret
after every provider attempt and again during cleanup.

stopping rule: stop immediately on any authorization, credential handling,
privacy, route, model, alias, fallback, schema, safe-error, call-cap, or
spend-cap mismatch, open call intent, or minimal-schema failure. A
complete-schema failure permits exactly the two committed same-provider
bisection schemas in deterministic order within ten calls, USD 1.00 total,
USD 0.50 per provider, and expected aggregate cost below USD 0.10; no ad-hoc
schema edit is allowed and the other provider remains blocked. Declare
conformance only after both complete schemas pass.

exact resume message:

> Resume AO-0004 in this same Codex session, issue #198, branch benchmark/treasurebench-provider-schema-conformance, ExecPlan, and draft PR #199. Use only reports/agent-ops/AO-0004-treasurebench-provider-canary-owner-gate-r3.yml and its exact R3 authorization. Do not use either superseded gate. Re-read current official provider terms; validate the R3 authorization, issue, PR, branch, execution commit, contract hash, every protected tree hash, exact repository-root .env.txt credential source and two-name allowlist, exact routes and models, zero cumulative calls and spend, ledger state, and remaining caps. Then run exactly make treasurebench-provider-schema-canaries. Stop immediately on any mismatch, open call intent, cap boundary, credential-source violation, or minimal-schema failure. If a complete schema fails, permit only the two frozen same-provider bisection calls in order; do not call the other provider. Declare conformance only if both complete schemas pass. Create no private, scientific, paper, ranking, release, submission, or base-campaign state.

observed activity: zero reads of the real `.env.txt`, credentials, or either
authorization path; zero provider calls; USD 0 spend; no private-state access
or change; and no scientific-state change. The superseded R1 and R2 gates were
never authorized and cannot be consumed.
