# TreasureBench Agents v1 pilot repair adjudication

Status: `complete-redacted-engineering-adjudication`.

This DD-010 record closes issue #191's diagnostic question without changing
the original decision
`sealed-pilot-quarantined-provider-failure`. It is an instrument-engineering
adjudication, not a scientific result, model comparison, or performance
report.

## Read-only evidence gate

The owner authorization was active, unrevoked, nonsynthetic, and bound to
draft PR #192, commit
`6f38609d69c41efba890e6a1ab5fe6ece398c536`, and diagnostic-tree hash
`sha256:92eef223eb141a192de30e111a2eece10279127d3ce68eb41d124b5776ae1697`.
The original campaign, batch, execution commit, output lock, seed commitment,
task-ciphertext commitment, and answer-ciphertext commitment all matched.

The exact authorized command verified the 3,545-object output lock, custody
commitments, both append-only logs, provider-phase closure, and the final
encrypted audit package. It selected exactly two error records and their two
minimum contexts and inspected exactly 500 retained run traces. Locked bytes
rehash to the original commitment, the retained metadata snapshot is unchanged,
and no retained write path was invoked. Provider calls, credential reads,
spend, and new private generation were zero.

## Redacted provider-error finding

The `transient-provider` event is
`provider-service-recovered`: the identical frozen call recovered within its
attempt bound and did not create a terminal run.

The `schema-or-parameter` event is `unknown-terminal`. The minimum retained
evidence proves a terminal missing run but cannot distinguish an invalid
request, exact-route capability rejection, provider-side structured-output
rejection, returned-output nonconformance, or a local adapter/parser cause.
The correct result is evidence insufficiency; no cause-specific provider patch
is justified.

The terminal event accounts for one frozen protocol-invalid run. The recovered
event accounts for none. Because the frozen verifier counted invalid runs once
and the final audit recorded two, the other reconstructed protocol error is a
separate downstream failure.

## Redacted action-budget finding

The independent reconstruction found:

- 137 runs with invalid final cardinality;
- 266 invalid final agent outputs, including 265 over-budget outputs;
- 547 multiple-action outputs across all rounds, of which 282 are non-final
  proposal lists;
- 138 metric records whose legacy values changed when credited extra actions
  were removed conservatively; and
- 57 legacy coverage values outside the registered proportion range.

The affected component set spans discovery, coverage, duplication, regret,
recovery, source diversity, compression, equilibrium-distance,
invalid-action, and protocol-compliance records. Counts by family,
architecture, route, provider, and round were independently reproduced but
remain private, as do record mappings, metric values, sensitivity
calculations, and every performance result.

## Repair and disposition

The prospective instrument now enforces exactly one final action per required
agent through the static and live schemas, prompt, parser, orchestration,
Methods A and B, an independent Method C contract verifier, and registered
metric-range checks. Non-final lists are explicitly one-to-six proposal
candidates and never scored as final actions. The future provider record adds
a normalized, redacted error envelope with transport-versus-provider-response
locus, HTTP status, and retry eligibility; it stores no raw provider body.

The prospective policy permits at most two transport attempts for the same
idempotent request and one schema-only repair. It permits zero terminal
failures, zero protocol-invalid runs, and zero incomplete pairings. Any such
failure quarantines the entire sealed batch; successful records may be kept
for private engineering diagnosis but cannot be spliced into a replacement or
used for partial performance publication.

The repaired 50-case public rehearsal passes, Method A and Method B agree,
Method C passes, and all 28 instrument corruptions reject under stable hash
`sha256:d13d925886b96015812ffd79e59faa89e2672a0efe7774652e3436b0c8c70d75`.

The final decision is
`instrument-repaired-fresh-sealed-pilot-required`. Any evaluation must use a
wholly new campaign, batch, seed, tasks, answers, keys, and custody under a
separate authorization. This issue authorizes no provider call, fresh private
material, fresh pilot, or base campaign.

## Repository closeout

PR #192 passed its head check and squash-merged as
`4fb4ef83ac39c11dcbe43bf21a8904d89b12246b`. Post-merge main CI run
30141694976 and Pages run 30141694979 passed on that exact commit. The live
TreasureBench Agents v1 page, redacted evaluation JSON, and program route each
returned HTTP 200 with fresh-pilot and base-campaign authorization still
false. Issue #191 closed as completed and main synchronized.
