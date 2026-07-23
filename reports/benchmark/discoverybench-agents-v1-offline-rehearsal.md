# DiscoveryBench Agents v1 offline rehearsal

Status: pass. Classification: public conformance only; not scientific or
performance evidence.

`make agents-v1-dry-run` exercised 10 public calibration tasks across all five
registered architectures for 50 deterministic cases. It used two
communication rounds, the one-retry structured-output rule, exact-rational
Method A evaluation, independent Method B reconstruction, raw/redacted/audit
traces, AES-256-GCM public toy custody, contamination fixtures, the zero-spend
batch guard, and all 24 registered corruptions.

Method B reported zero disagreements and all 24 corruptions were rejected. The
stable semantic rehearsal hash is
`sha256:d3410ff04bb73dcae929c3abc4cf289d58d6830f2a5ab50ca53764bef4af2c59`.
The rehearsal made 294 deterministic mock-adapter calls and accounted for
28,224 mock tokens; these are conformance counters, not provider/model calls.
One local acceptance invocation took 0.33 seconds, observed a maximum resident
set size of 33,193,984 bytes, and rendered 23,528 bytes with SHA-256
`044304e965dc349222b622f947db9a3fff0693cd3de17ca38257f580592de3dd`.
Those runtime and memory values are environment-specific acceptance
observations, not benchmark evidence.

Provider calls, model invocations, model downloads, network calls, and external
cost were all zero. No private seed, holdout, key, answer material, provider
trace, scientific claim, immutable run, or performance result was created.
