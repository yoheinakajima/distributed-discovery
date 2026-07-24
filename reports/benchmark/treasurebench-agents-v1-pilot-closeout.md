# TreasureBench Agents v1 sealed-pilot closeout

The fixed 50-task TreasureBench Agents v1 sealed engineering pilot completed
its provider phase, output lock, post-lock unsealing, independent verification,
and redacted safety audit. Its predeclared outcome is
`sealed-pilot-quarantined-provider-failure`.

This is non-inferential DD-010 instrument-engineering evidence. It is not a
scientific evaluation, provider comparison, model ranking, leaderboard, paper
result, immutable scientific run, or claim.

## Redacted execution record

- Exact direct models: OpenAI `gpt-5.4-2026-03-05` and Anthropic
  `claude-sonnet-4-6`.
- Fixed scope: 50 tasks, five families, five architectures, and 500 private
  architecture/model runs.
- Ledger: 3,037 attempts, 3,035 successes, and two preserved Anthropic errors.
- Error classes: one recovered `transient-provider` attempt and one terminal
  `schema-or-parameter` attempt.
- Usage: 2,004,503 input tokens and 392,889 output tokens.
- Cost: USD 11.5702435 total; OpenAI USD 4.1798125 and Anthropic USD 7.390431.
- Reconstructed protocol errors: two.

The errors are preserved rather than retried after closeout, replaced, tuned
away, or hidden. They require the quarantined-provider outcome and prohibit
base-campaign registration readiness.

## Lock, verification, and safety

The provider phase closed before unsealing. The output lock covers 3,545
encrypted provider outputs, encrypted traces, custody objects and commitments,
hash-chained usage/cost and access ledgers, authorization transitions,
provider-stage state, errors, and costs:

`sha256:1d487723f7587e8e2fa865682e6f6cc473cf2da4967b837dedf3952cddfcbfab`

The public lock record was committed and pushed before unsealing. The complete
inventory then reverified against the lock. Post-lock Method A and independent
Method B agree with zero disagreements across all 500 runs. Direct/probable
contamination findings are zero. All 76 registered corruptions reject,
redaction passes, the private-leak scan passes, and costs reconcile exactly.
The encrypted final audit package is retained for 365 days.

## Public boundary

No task text, answer, seed, key, raw prompt, raw output, raw trace, task-level
metric, ranking, composite, or inferential statement is published. The
ciphertext and seed commitments remain the only public custody identifiers.

No DD-023, study, claim, scientific run, paper result, package, arXiv or journal
action, leaderboard, or base-campaign authority is created. Any future
instrument repair or rerun requires separate registration and explicit owner
authorization; this closeout grants none.
