# DD-024 preserved results

All three primary attempts began at 2026-10-31T21:59:33Z from clean detached worktrees at source commit `caa1bf800bde9033e6b317e46bad0aff73828338`. Each completed once with exit status zero and independent validation passed. These are exact finite-model computations retained as audited exploratory evidence; no central claim is promoted.

| Track | Parameter cells | Immutable run |
| --- | ---: | --- |
| 02 | 18 | [20261031T215933Z_DD-024_caa1bf80_1d0ab47ae5](../../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_1d0ab47ae5/README.md) |
| 03 | 80 | [20261031T215933Z_DD-024_caa1bf80_614ce37ebc](../../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_614ce37ebc/README.md) |
| 04 | 36 | [20261031T215933Z_DD-024_caa1bf80_30b8369b0c](../../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_30b8369b0c/README.md) |

## Provenance and scope

Each run stores its configuration, frozen source/input hashes, dependency lock hash, command, environment, UTC start/end, resource use, complete exact outputs and saved policies, independent verification, corruption outcomes, logs, and a complete manifest-bound artifact checksum inventory. All three original worktree directories were copied byte-identically into this branch; no result file was edited after creation.

Each worker had a combined evaluation, persistence, and verification limit of 120 seconds and 1024 MiB. Evaluation uses exact rational arithmetic, not stochastic sampling, so Monte Carlo confidence intervals are inapplicable. This does not remove uncertainty about model assumptions or human applicability.

See the [report](../report.md), [separate claim audit](../claim-audit.md), and the three `review-results-track*.md` files for the checked interpretations and limitations.

## Checking preserved evidence

Use a detached checkout of the source commit above, copy the relevant preserved run directory into the identical relative path, and run the following command with the locked Python environment:

```bash
PYTHONPATH=src python -m distributed_discovery.behavioral_diversity.study --track track-02 --verify-existing results/exploratory/20261031T215933Z_DD-024_caa1bf80_1d0ab47ae5
```

Use the matching track/run identity for the other two runs. The later integration branch updates task/status documentation and is not a substitute for the frozen source when checking every input hash. This read-only route checks preserved evidence and creates no new primary. The historical `reproduce.sh` is not an instruction to consume another primary attempt.
