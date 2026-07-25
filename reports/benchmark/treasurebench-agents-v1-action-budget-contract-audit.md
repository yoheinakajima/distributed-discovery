# TreasureBench Agents v1 action-budget contract audit

Status: `public-contract-defect-established-private-prevalence-pending`.

This DD-010 engineering audit is part of issue #191. It creates no study,
claim, scientific run, or pilot authority. The original
`treasurebench-agents-v1-pilot-v1` closeout remains immutable as
`sealed-pilot-quarantined-provider-failure`.

## Authoritative contract

`team-architectures.yml` grants one final action per agent in every registered
agent architecture. `agent-protocol.yml` classifies an extra action and a
missing agent action as protocol-invalid. Those two records establish the
final-action budget independently of any observed pilot output.

The frozen pilot instrument did not enforce that contract end to end:

- the static structured-output schema allowed an `actions` array of length
  one through six without a final-round condition;
- the live provider schema set no action-array cardinality bound;
- the prompt exposed the vocabulary but not the final cardinality;
- the parser enforced nonempty, unique, in-vocabulary actions but did not
  enforce exactly one final action;
- orchestration accepted a schema-valid multi-action final record;
- Method A flattened every submitted final action before scoring;
- Method B independently flattened the same lists, so A/B agreement could
  preserve the shared semantic defect;
- trace hashing protected retained bytes but did not establish protocol
  conformance;
- invalid-action rate counted missing final records only, and protocol
  compliance depended only on recorded orchestration errors;
- metric verification did not reject coverage or other registered proportions
  outside their declared ranges.

No private prevalence or performance figure is recorded here. Reported
private counts remain diagnostic leads until reproduced under the exact
read-only gate.

## Prospective repair

The repaired contract represents non-final action arrays explicitly as
one-to-six proposal candidates that are not scored. A final action array must
contain exactly one action. The static and live schemas, prompt, parser, and
orchestration enforce this independently.

Methods A and B now give no credit to an over-budget final output and apply the
registered conservative invalid-output treatment. Invalid-action rate counts
missing, duplicated, over-budget, and otherwise invalid required final
outputs. Protocol compliance requires an independent Method C pass.

Method C imports neither Method A nor Method B semantics. Before performance
interpretation it verifies final records and actions, vocabulary, architecture
information and action rights, round and message limits, source and tool
rights, comparator/action capacity, final-action extraction, and metric ranges.
Corruptions C25-C28 cover multiple final actions, coverage above one, parser
defense omission, and a shared Method A/B semantic defect.

The frozen wording did not distinguish non-final candidate lists clearly
enough to assign their historical status without interpretation. The private
diagnostic therefore records definitive final violations separately from an
all-round conservative sensitivity. Future execution uses the explicit
proposal/final distinction above.

## Private gate and next run

After the diagnostic tree is committed and pushed, the owner-created gate may
verify the original lock and custody, inspect exactly 500 retained private run
traces, reproduce aggregate cardinalities and downstream sensitivity, and
diagnose the two provider errors. Detailed task, model, architecture, and
performance results remain private.

Regardless of the provider-error policy decision, the original pilot cannot
establish instrument readiness. A wholly new sealed pilot is mandatory after
repair, with new campaign and batch IDs, seed, tasks, answer key, keys, and
custody. Issue #191 does not authorize that execution.
