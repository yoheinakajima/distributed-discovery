# AO-0007 owner-gate-required handoff

- **Status:** `owner-gate-required`
- **Issue / draft PR:** #202 / #203
- **Branch:** `codex/treasurebench-ao0006-custody-repair`
- **Execution commit:** `55a7815c77319e7845238126c6045f2e80026165`
- **Corrected committed gate head:** `d85baf015e139fca221fedeea65ec3d70baa67b9`
- **Contract:** `tasks/treasurebench-ao0006-custody-repair.yml`
- **ExecPlan:** `plans/TREASUREBENCH_AO0006_CUSTODY_REPAIR.md`
- **Gate:** `reports/agent-ops/AO-0007-treasurebench-ao0006-custody-diagnostic-owner-gate.yml`
- **Challenge:** `AUTHORIZE AOG-AO-0007-AO0006-CUSTODY-DIAGNOSTIC 55a7815`
- **Decision:** stop before any retained AO-0006 read or detailed private
  diagnostic.
- **Calls / cost / private / scientific:** `0 / USD 0 / none / none`
- **Validation:** pass; 7 focused tests, 580 full tests, Ruff over 332 files,
  MyPy over 197 source files, 51 run manifests, the twenty-class live-mode
  framework, six corruption classes, exact 14-path execution freeze, and live
  generic gate validation without authorization.

The first live validation failed closed because the manifest contained an
incorrectly expanded full execution SHA. No authorization or private access
occurred. The manifest was corrected in a new commit and the complete live
validation passed.

Exact generic owner-gate command:

```sh
make owner-gate GATE=reports/agent-ops/AO-0007-treasurebench-ao0006-custody-diagnostic-owner-gate.yml OWNER_GATE_CHALLENGE='AUTHORIZE AOG-AO-0007-AO0006-CUSTODY-DIAGNOSTIC 55a7815'
```

Exact diagnostic command, permitted once only after that gate succeeds:

```sh
make treasurebench-custody-read-only-diagnostic
```

Exact resume message:

> Resume AO-0007 in this same Codex task from plans/TREASUREBENCH_AO0006_CUSTODY_REPAIR.md using only reports/agent-ops/AO-0007-treasurebench-ao0006-custody-diagnostic-owner-gate.yml and its exact generic authorization. Revalidate the authorization, execution-commit ancestry, current draft-PR head, fixed contract, all protected tree hashes, exact zero caps, prohibitions, and retained output-lock and inventory boundary; then run only make treasurebench-custody-read-only-diagnostic once. On a public-safe pass, permanently close private access, reproduce the exact cause synthetically, implement only the minimum prospective repair, require all twenty live-mode custody conformance classes and corruptions to pass, complete the public-safe AO-0007 closeout, ready and merge PR 203 after checks, verify normal CI/Pages and named public routes, close issue 202, and synchronize main. Stop on any mismatch, inconclusive diagnosis, retained-state change, extra read requirement, provider or credential need, scientific change, release, or submission.
