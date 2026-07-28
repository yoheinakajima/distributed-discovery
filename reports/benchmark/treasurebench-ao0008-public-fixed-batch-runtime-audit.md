# AO-0009 public AO-0008 fixed-batch runtime audit

Status: `public-source-causal-candidates-not-private-adjudication`

This audit reads only tracked source and public AO-0008 closeout records. It
does not resolve the retained private root, load an authorization or
credential, read an encrypted object, make a provider call, or spend.

## Permanent source boundary

AO-0008, campaign `treasurebench-agents-v1-repair-confirmation-v3`, batch
`tb-agents-v1-repair-confirmation-v3-b01`, execution commit
`0f9d82bb50cbb334bea47e24448831faf0cdbed8`, fixed-full-batch quarantine, all
recorded operational totals, and output lock
`sha256:e52055b08ca3a8acb1cfb6ac608c6e601f3c618352900f92bf91c5ffc4718dbb`
remain immutable.

The public closeout supplies 3,576 locked objects and 3,067 actual provider
attempts. The frozen runtime's lock inventory always includes seven fixed
objects: task ciphertext, answer ciphertext, custody manifest, execution
identity, access ledger, usage/cost ledger, and provider-stage state. It also
includes one encrypted provider-response object per durable attempt and one
encrypted trace per completed canary or architecture/model pairing. Thus the
public counts are arithmetically consistent with 3,067 response objects and
502 trace objects. Arithmetic consistency is not proof that every required
pairing exists or that a particular output caused the failure.

## Provider attempt and ledger control flow

`ResumablePilotAdapter` derives a logical call key from provider, exact model,
task commitment, agent, round, schema-repair flag, final-required flag, and
prompt hash. Each transport attempt is encrypted before its hash-chained
`provider-call` record is appended. The registered transport policy permits at
most two attempts for timeout, transient transport, invalid provider JSON,
rate-limit, or transient-provider classes. Nonretryable errors return
immediately.

The ledger records attempt number, logical call key, provider, model, status,
usage, cost, safe error class, and schema-repair flag. It does not record raw
output or task content. A selected logical call can therefore be bounded and
its encrypted response objects located without decrypting unrelated objects.

## Pairing and trace control flow

The private prefix contains five tasks and therefore 50 architecture/model
pairings. The remaining fixed batch contains 45 tasks and therefore 450
pairings. `PilotBatchRunner.run_stage` iterates model, task, and architecture;
after each architecture run it checks the protocol, accumulates counters, and
persists one encrypted trace. It raises on Method disagreement, metric range,
contamination, or the conservative protocol gate after the loops.

AO-0008 ran the fixed batch with metrics disabled and
`reject_protocol_errors=True`. Consequently public source admits, but does not
establish, this candidate: all 450 full-batch traces may exist while an
aggregate protocol exception prevents the caller from appending
`fresh-fixed-full-batch-complete` and setting
`fixed_full_batch_complete=true`. The bounded diagnostic must independently
test exact trace domains, errors, exception context, and state.

## Quarantine and lock control flow

Any fixed-full-batch exception is caught by the long-session wrapper and
mapped only to the coarse registered class `fixed-full-batch-failure`. The
quarantine path sets `quarantined=true`, records the stage and coarse class,
appends `batch-quarantine`, closes the provider phase, collects every safely
lockable object, creates and verifies the output lock, and performs no unseal.
The detailed Python exception type and message are not persisted separately.

This means the coarse public class cannot distinguish provider terminal,
returned-output parsing, evaluated-agent protocol, trace persistence, ledger,
pairing, or completion bookkeeping. The diagnostic must not invent a missing
exception record.

## Frozen bounded diagnostic design

The allowlist is frozen in
`reports/benchmark/treasurebench-ao0008-fixed-batch-diagnostic-allowlist.yml`.
It permits five fixed operational records, structural envelope metadata for
exactly 3,067 encrypted responses and 502 encrypted traces, one selected
logical call, at most two preceding and two following attempt/orchestration
records, at most two directly corresponding response objects, one directly
corresponding trace object, and one transient 32-byte operational key.

The diagnostic must return `unknown-within-retained-evidence` when the one
bounded context cannot establish causality. It must not broaden the read,
infer cause from the call-count difference, or register v4.
