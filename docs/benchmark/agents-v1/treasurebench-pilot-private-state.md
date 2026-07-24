# TreasureBench Agents v1 pilot private-state contract

The real pilot state root is symbolic:
`XDG_STATE_HOME/distributed-discovery/treasurebench-agents-v1/pilot-v1`.
Repository artifacts must never contain its resolved host path.

Directories are nonsymlink 0700 and files are nonsymlink 0600. Writes use
exclusive creation or atomic same-directory replacement with fsync. Existing
material is never silently overwritten.

The private layout separates `seed`, an operational response/trace key,
`task-key`, `answer-key`, `tasks.ciphertext`, `answers.ciphertext`, the
hash-only custody manifest,
encrypted provider responses, `access-log.jsonl`, `raw-traces/`,
`usage-cost-ledger.jsonl`, provider-stage state, `output-lock.json`,
`unsealed-audit/`, `final-audit-package.ciphertext`, and the redacted summary.
Keys are not stored
beside ciphertext in the final retained package. Each AES-256-GCM object uses
an independent OS-CSPRNG key and nonce and associated data binding campaign,
batch, artifact type, allocation commitment, and schema.

The access, call, cost, output-lock, and unseal logs are append-only and
hash-chained. The original execution identity is immutable. If an
execution-sensitive repair stops the pilot and the owner authorizes a later
descendant checkpoint, the access log records a forward-only transition from
the prior authorization, commit, and tree hash to the replacement
authorization, commit, and tree hash. Stable branch, issue, pull request,
campaign, batch, model, and base-commit identity must remain exact; the
transition is included in the output lock. Agents receive only declared
capability views. Seed, generator internals, answer objects, exact comparators,
evaluator state, and undeclared private signals are inaccessible.

Unsealing refuses until the output-lock manifest is complete and verified.
Cleanup or deletion refuses without a later logged owner deletion
authorization. The encrypted audit package is retained for 365 days after
closeout, including failures and quarantined batches.

Phase A uses a temporary synthetic root and public toy material only. It
creates no real private seed, key, task, answer, or retained private state.
