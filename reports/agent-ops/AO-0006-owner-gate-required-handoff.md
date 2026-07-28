# AO-0006 owner-gate-required handoff

- **Status:** `owner-gate-required`
- **Issue / draft PR:** #200 / #201
- **Branch:** `benchmark/treasurebench-agents-v1-fresh-pilot-v2`
- **Execution commit:** `10aa645d6687816b943625dbcdf1801968287b41`
- **Committed gate head:** `5b27fd060338f8d62ec715d2e21e48850915087f`
- **Contract:** `tasks/treasurebench-agents-v1-fresh-pilot-v2.yml`
- **ExecPlan:** `plans/TREASUREBENCH_AGENTS_V1_FRESH_PILOT_V2.md`
- **Campaign / batch:** `treasurebench-agents-v1-repair-confirmation-v2` /
  `tb-agents-v1-repair-confirmation-v2-b01`
- **Budget:** USD 11.51 expected, USD 15 conservative, USD 25 hard;
  OpenAI USD 10, Anthropic USD 15; 3,016 normal and 5,200 maximum calls.
- **Gate:** `reports/agent-ops/AO-0006-treasurebench-fresh-pilot-v2-owner-gate.yml`
- **Challenge:** `AUTHORIZE AOG-AO-0006-FRESH-PILOT-V2 10aa645`
- **Decision:** stop before credentials, prior private state, real seed or
  custody, providers, spend, output unsealing, or live execution.
- **AO-0006 calls / cost / private / scientific:** `0 / USD 0 / none / none`
- **Validation:** pass; 50 synthetic tasks, 500 runs, 3,014 matrix turns, 500
  pairings, 69 corruptions, 526 tests, Ruff, MyPy, exact 21-path execution
  freeze, and live generic gate validation with no authorization.

Exact generic owner-gate command:

```sh
make owner-gate GATE=reports/agent-ops/AO-0006-treasurebench-fresh-pilot-v2-owner-gate.yml OWNER_GATE_CHALLENGE='AUTHORIZE AOG-AO-0006-FRESH-PILOT-V2 10aa645'
```

Exact live command, permitted only after that gate succeeds:

```sh
make treasurebench-fresh-pilot-v2-live
```

Exact resume message:

> Resume AO-0006 in this same Codex session from plans/TREASUREBENCH_AGENTS_V1_FRESH_PILOT_V2.md using only reports/agent-ops/AO-0006-treasurebench-fresh-pilot-v2-owner-gate.yml and its exact generic authorization. Re-audit current official provider availability, parameters, retention, errors, retries, and pricing; validate the authorization, execution commit, current draft-PR ancestry, contract, all execution-tree hashes, identities, zero cumulative state, and caps; then run only make treasurebench-fresh-pilot-v2-live one staged transition at a time, committing required public-safe custody and output-lock commitments before the next stage. Stop and quarantine the entire batch on any mismatch or prospective acceptance failure. Create no scientific, paper, ranking, release, submission, or base-campaign artifact.
