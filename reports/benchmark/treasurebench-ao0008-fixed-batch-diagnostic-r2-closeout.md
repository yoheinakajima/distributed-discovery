# AO-0009 aggregate fixed-batch diagnostic R2 closeout

AO-0009 invoked the exact R2 diagnostic once against frozen commit
`fbecbfb89e634967d48931c00e1d8a4fbed81c79`. The read-intent marker consumed
the private-read authority, the bounded read completed, and the authority is
permanently closed. The detailed record remains nonpublic outside Git.

The diagnostic verified the 3,576-object output lock, immutable inventory,
append-only ledgers, complete 3,067-response identity correspondence, unique
2/50/450 trace partition, and all 500 private pairing records. All 450
fixed-full-batch traces authenticated. Retained AO-0008 state was not mutated,
no operational key was retained, and provider calls, credential reads, and
spend were zero.

The public aggregate contains 32 protocol-nonconforming traces and 32
parse/schema-repair exhaustion traces. It contains zero terminal provider
attempts, zero direct or probable contamination traces, zero invalid
final-cardinality traces, and no triggered cap guard. The completion marker
is absent after the otherwise complete 3,016 logical calls and 500 pairings.
This matches the frozen public runner's post-loop aggregate protocol gate and
selects causal class `protocol-contract-nonconformance` with safe actor
`evaluated-agent`.

The evidence-determined AO-0009 outcome is
`agent-protocol-policy-decision-required`. AO-0009 does not silently
normalize, retry, credit, or otherwise repair protocol-invalid evaluated-agent
outputs. Any change to that policy requires a separate explicit owner
decision and prospective task. Any future private evaluation requires wholly
new identities, task registration, execution freeze, and owner gate.

AO-0008 remains permanently quarantined. This is redacted engineering
diagnosis only. It creates no task-level metric, performance comparison,
ranking, scientific run, claim, paper result, release, submission, or
base-campaign authority, and it does not register v4.
