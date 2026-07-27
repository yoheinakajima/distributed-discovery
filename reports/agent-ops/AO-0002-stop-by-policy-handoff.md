# AO-0002 Agent Operations handoff

- Status: `stop-by-policy`
- Decision: `sealed-pilot-quarantined-provider-failure`
- Issue / draft PR: #196 / #197
- Branch: `benchmark/treasurebench-agents-v1-fresh-pilot`
- Frozen execution commit:
  `fe313602df7f4e8ffac1a1a02c2b3a83f3c72943`
- Redacted closeout commit:
  `514fc8d662e56a844015200e36825954dedf3a33`
- Calls / tokens / cost: 1 OpenAI, 0 Anthropic; 0 input, 0 output;
  USD 0.00
- Terminal result: OpenAI HTTP 400 `schema-or-parameter`; no retry
- Custody: operational key and encrypted terminal record only; no task seed,
  tasks, answers, task/answer keys, task/answer ciphertexts, or custody
  manifest
- Output lock:
  `sha256:8102a6c1b6bda003336d5503136dfe29301b04cb8f35e7740edd8d56f0eb3c1d`
- Methods A/B/C and metric ranges: not run because no private run occurred
- Contamination: not evaluable because no provider output was returned
- Synthetic validation: 500 runs and 54/54 corruptions pass
- Authority: no scientific, ranking, package, release, merge, Pages, or base
  campaign action

No command is authorized for this quarantined campaign or batch. A future
repair requires a separately registered new identity and exact owner gate.
