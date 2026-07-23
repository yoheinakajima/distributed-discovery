# DiscoveryBench Agents v1 prospectus

This is the exact next registration prospectus. The registration-only design
is paired with `plans/DISCOVERYBENCH_AGENTS_V1_GATE.md`. It asks:

> Do real software-agent teams exhibit the duplication, source concentration,
> shared-clue over-attention, consensus collapse, and portfolio-recovery
> failures predicted by exact Distributed Discovery tasks?

The initial task families are common-source acquisition, one-reader versus
broadcast attention, point versus shortlist sharing, consensus collapse versus
portfolio recovery, and threshold-team formation.

Registration must freeze the benchmark and task-generator versions, provider,
model identifier and snapshot date, system and user prompts, agent count and
identity, communication topology and message budget, memory and tool policies,
temperature and top-p, seed and retry policy, stopping rule, context limits,
cost cap, timeout, raw-trace format, and safety/redaction policy.

Contamination controls require a committed generator before evaluation, hidden
parameters or private seeds, provider/model version freeze before holdout
generation, sealed answer keys, multiple independently generated holdout
batches, no public task IDs or exact public wording in holdout prompts,
contamination probes, isomorphism checks, and delayed release of generator,
seeds, and answers after all runs lock unless provider safety prevents a trace
component. Public tasks are calibration or prompt-debugging material only.

The future registration must include more than one model family and, where
feasible, a reproducible local or open-weight baseline. It authorizes no
universal ranking and no default composite score. Primary metrics are group
discovery, distinct-action coverage, duplication, planner regret,
private-baseline regret, recovery-budget attainment, source diversity,
communication-induced action compression, distance from best and worst
registered equilibria, invalid-action rate, protocol compliance, and
operational cost and token use.

Any future evidence is software-agent evidence, not human or organizational
evidence. It remains provider-version-, model-snapshot-, prompt-architecture-,
topology-, and sampling-specific. It supports no leaderboard or provider
quality endorsement.

Registration must stop if contamination cannot be bounded, versions cannot be
frozen and reported, cost is not authorized, raw traces cannot be preserved
safely, public answer leakage solves the task, metrics cannot distinguish
reasoning from memorization, materially different model families cannot be
compared, or the evaluation reduces to generic benchmark accuracy.

No model or provider was called, no cost was incurred, no agent team was run,
and no study ID, trace, result, or private seed exists. The next session must
write `plans/DISCOVERYBENCH_AGENTS_V1_REGISTRATION.md` only after re-auditing
the repository and freezing the registration.

Exact next command: `git status --short --branch`

Exact next file: `plans/DISCOVERYBENCH_AGENTS_V1_REGISTRATION.md`
