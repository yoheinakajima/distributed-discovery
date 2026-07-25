# TreasureBench Agents v1 pilot repair registration

Decision:
`register-read-only-provider-and-protocol-adjudication-under-dd010`.

Issue #191 registers a bounded two-track engineering adjudication under DD-010:
provider-error and missingness adjudication plus action-budget
contract-conformance adjudication. The original campaign
`treasurebench-agents-v1-pilot-v1`, batch
`tb-agents-v1-pilot-v1-b01`, output lock
`sha256:1d487723f7587e8e2fa865682e6f6cc473cf2da4967b837dedf3952cddfcbfab`,
and decision `sealed-pilot-quarantined-provider-failure` remain immutable.
This registration cannot retroactively pass or rerun the pilot.

Public evidence records two preserved Anthropic error attempts: one
`transient-provider` and one `schema-or-parameter`. It records two downstream
protocol errors, zero Method A/B disagreements, and zero contamination
findings, but it is insufficient to assign exact causes. Diagnosis therefore
requires a separately owner-authorized read-only gate after the diagnostic
code is committed, pushed, and tree-hashed.

The authoritative public architecture and protocol contracts grant exactly one
final action per required agent and classify an extra action as
protocol-invalid. The pre-repair schema, parser, orchestration, evaluator, and
both metric reconstruction methods did not jointly enforce that rule. Exact
Method A/B agreement therefore cannot establish protocol conformance. Reported
private counts remain unverified leads and are not registered here.

Phase A makes no provider call, reads no credential or retained private state,
and creates no private material. The diagnostic scope is limited to verifying
the original lock and commitments, validating append-only logs, decrypting the
retained final audit package, selecting exactly two error records and their
minimum contexts, and aggregating action cardinalities across exactly 500
retained run traces. It may privately map protocol-invalid final outputs to
downstream metric changes and sensitivity calculations. It may not mutate the
retained state or disclose a task, answer, prompt, output, raw trace, raw
provider body, request identifier, task-level metric, performance table,
ranking, or composite.

This is not DD-023 and creates no claim, scientific run, paper, result,
leaderboard, composite, base-campaign authority, fresh-pilot execution
authority, seed, task, answer, key, custody object, or batch. A fresh sealed
pilot is mandatory after repair but is neither authorized nor executed here;
it requires wholly new identity and private material plus a separate owner
authorization.
