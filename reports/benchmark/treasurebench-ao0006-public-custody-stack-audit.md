# AO-0007 public custody-stack audit

Status: `public-source-causal-candidate-not-private-adjudication`

Task: `AO-0007`

Source task: `AO-0006`

Audited execution commit:
`d210b0653677859c79a1fb87d871aaf45f4a81d4`

## Permanent boundary

Campaign `treasurebench-agents-v1-repair-confirmation-v2`, batch
`tb-agents-v1-repair-confirmation-v2-b01`, terminal decision
`fresh-pilot-v2-quarantined-engineering-only`, and output lock
`sha256:127a9c796459c7627f6fd90b92ef1587ad0f6b1910b4ff255c2ceb976f3ab25f`
remain immutable. This audit reads tracked public source and public closeout
records only. It does not read an authorization, credential, private path, or
retained AO-0006 object.

## Production ordering at the frozen commit

The custody stage in
`src/distributed_discovery/benchmark/agents_v1/fresh_pilot_v2_live.py`
performs these operations in order:

1. load or create an OS-CSPRNG seed, task key, and answer key;
2. call the v2 `generate_tasks` private path;
3. derive task and answer payloads;
4. seal and persist task ciphertext;
5. seal and persist answer ciphertext;
6. construct and persist the custody manifest;
7. append the custody-created access event and mark the stage complete.

The public closeout reports that step 1 completed while no task ciphertext,
answer ciphertext, custody manifest, custody-created access event, or private
run exists. This bounds the failure to the call beginning at step 2 and ending
before the first ciphertext persistence at step 4.

## Public-source causal candidate

At the exact execution commit, v2 `generate_tasks` creates a
`GenerationPermit` whose campaign ID is
`treasurebench-agents-v1-repair-confirmation-v2` and calls
`generate_instance` with `public_fixture=False`.

At the same commit, `generate_instance` admits private generation only when
the permit campaign is one of:

- `treasurebench-agents-v1-pilot-v1`;
- `treasurebench-agents-v1-repair-confirmation-v1`.

The v2 campaign is absent. Therefore the first v2 private `generate_instance`
call deterministically reaches the fail-closed
`private generation is disabled` rejection before task serialization,
encryption, nonce generation, associated-data construction, ciphertext
persistence, commitment construction, or manifest construction.

This is a causal candidate from public source, not yet the final AO-0007
diagnosis. The bounded retained-state diagnostic must independently verify the
output lock, exact inventory, stage record, minimum surrounding events,
presence metadata for the seed and two keys, absence of task/answer
ciphertexts and the custody manifest, and retained-state immutability before
AO-0007 may classify the exact root cause.

## Rehearsal gap

The synthetic v2 long-session rehearsal invokes the same `_custody` function
with `synthetic=True`. That changes `public_fixture` to true and supplies no
private authorization, so `generate_instance` bypasses the private campaign
permit check. The rehearsal therefore exercises downstream task construction,
encryption, persistence, commitments, and manifest behavior without exercising
the production private-generation admission decision that failed live.

A live-mode-equivalent synthetic conformance command must use synthetic
nonsecret material while keeping `public_fixture=False` and the production v2
permit, call order, persistence functions, and reload path.

## Additional prospective conformance gaps

The shared `atomic_private_write` implementation creates a mode-`0600`
temporary file, fsyncs it, and replaces the target. It refuses an existing
symlink but does not provide exclusive create semantics and overwrites an
existing regular target. The current `_load_or_create_sealed` resume path
verifies ciphertext and associated-data hashes but does not independently
prove that an existing sealed object decrypts to the newly requested value.

These are prospective conformance findings, not claims about the exact
AO-0006 failure. The registered conformance framework must test exclusive
creation, duplicate mismatch refusal, interrupted writes, symlinks, modes,
reload, wrong keys, corrupted ciphertext, and an independent verifier before
any future private pilot can be considered.

## Public-safe conclusion

The tracked code supplies a deterministic candidate at
`private task generation / campaign-permit validation`, and the coarse public
retention shape is consistent with that candidate. Exact adjudication remains
owner-gated. No repair is applied before that diagnostic.
