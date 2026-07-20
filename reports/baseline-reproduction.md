# Canonical baseline reproduction — DD-000

**Status:** completed against upstream commit `5025cc8e8f2f8ca015dff2066f08f81ad5715a51` (MIT). Evidence run: `20260720T190336Z_DD-000_32dd1c32_217c602fa0`.

## Execution

`make reproduce-baseline` synchronized the exact packages in `integrations/shared-discovery-paradox/upstream-requirements.lock`, ran the upstream `verify_shared_discovery_v8_6.py`, captured stdout/stderr, regenerated CSVs and figures, parsed the canonical block, and validated prompt-provided rounded sanity checks. The script exited zero and printed `All v8.6 checks passed.` The manifest records that the research worktree was dirty because M1 code/configuration preceded its milestone commit.

Two earlier run directories are retained as operational negative results. In both, the upstream verifier completed and its research checks passed, but post-run package metadata collection failed; neither is claim evidence.

## Canonical values

| Quantity | Full displayed value | Evidence status | Claim |
|---|---:|---|---|
| Blind coordinated discovery | 0.500000000000 | independent rational formula | DD-C-0003 |
| Consensus discovery | 0.383468709731 | upstream + independent count enumeration | DD-C-0005 |
| Symmetric market discovery | 0.599099252439 | upstream verifier only | DD-C-0007 |
| Private clue-following discovery | 0.832227840000 | upstream + independent rational formula | DD-C-0004 |
| Planner discovery | 0.859421246199 | upstream + independent count enumeration | DD-C-0006 |
| Market expected distinct actions | 2.673494083278 | upstream verifier only | DD-C-0010 |
| Private expected distinct actions | 6.156849828175 | upstream + independent rational formula | DD-C-0010 |
| Recovery budget | 7 | upstream + independent frontier enumeration | DD-C-0008 |
| Copying crossover | 0.788461656521 | upstream numerical root solve | DD-C-0009 |

The upstream equilibrium/crossover computations use finite enumeration plus high-precision floating-point/root methods; this report does not relabel them exact. The 72-case single-crossing statement is a numerical observation restricted to that grid (DD-C-0015).

## Independent method

`src/distributed_discovery/canonical/model.py` does not import or parse upstream. It uses exact rational formulas for blind/private/private-distinct values, exact-rational brute force for a tiny consensus fixture, and a separate enumeration of all labeled count vectors for canonical consensus and the top-\(L\) planner frontier. Tests verify posterior normalization, relabeling invariance, probability mass, bounds, tiny-method agreement, and canonical regressions.

The market equilibrium, market distinct-action expectation, copying crossover, price-of-anarchy proof, sole-rescue theorem, and monotone planner-gain theorem have not been independently reproduced or locally proof-reviewed. Their ledger statuses preserve that distinction.

## Reproduce

```sh
make fetch-upstream
make reproduce-baseline
make validate-claims
make test
```

Each reproduction creates a new immutable run; it never overwrites this one.
