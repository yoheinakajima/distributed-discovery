# Post-run quantitative audit: track 03

Audit completed 2026-10-31 at 22:02:51 UTC by the campaign agent that did
not author the track-03 implementation. This is an internal audit of saved
synthetic evidence, not external peer review or a central claim promotion.

## Disposition

**Accept the reported quantities below as audited exploratory findings for
the registered finite model.** The source and output hashes agree, the
independent raw-world verifier passes, and a separate read-only calculation
reconciles every contrast and summary count to the saved policy values.
No central claim ID is allocated or promoted by this audit. No scientific
source, configuration, or immutable run file was changed, and no primary
experiment was rerun.

The authoritative run is
`20261031T215933Z_DD-024_caa1bf80_614ce37ebc`, under
[`results/exploratory`](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_614ce37ebc/README.md).
The [pre-execution review](review-track03.md) explains finite completeness,
matched resources, precommitment equivalence, and verifier independence.

## Provenance and artifact integrity

| Item | Audited record |
| --- | --- |
| Study / track | `DD-024` / `track-03` |
| Frozen Git source | `caa1bf800bde9033e6b317e46bad0aff73828338` |
| Source state at primary | `git_dirty: false` |
| Canonical configuration hash | `614ce37ebcb099aa0b032214b27be53e373c44aeab0056df5066ae5bae4c9ab5` |
| Dependency-lock hash | `0766c91477cdc28e1ed36ec7bcd60669ed6e80fd0a6f55892bc8fba2c57a3588` |
| Start / end UTC | `2026-10-31T21:59:33.517765Z` / `2026-10-31T21:59:34.868622Z` |
| Termination | `completed`; exit status zero; validation passed |
| Recorded coordinator elapsed time | `1.319668` seconds, against the registered 120-second cap |
| Worker elapsed time | `1.222745` seconds |
| Observed peak resident memory | `24960 KiB`, or `24.375 MiB`; registered address-space cap `1024 MiB` |
| Scientific evidence boundary | Exact only for the declared finite model and continuation class; separate claim admission required |

The [manifest](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_614ce37ebc/manifest.json)
has SHA-256
`c835d93e480b7342e4850f49691fa1a4f2a6d2df5cc5c772ab007925dacc0a72`.
The complete artifact-hash inventory has SHA-256
`e7ff6b91d5ea07511e90b52a0c0d6479a7af5eaf85e4a8791ad6914a4c2ece84`.

Independent SHA-256 calculations checked all **92 artifact inventory
entries**, including logs and reproduction script, and all **90 manifest
public-output entries**. All **11 frozen input hashes** were additionally
checked against the actual Git blobs at the recorded source commit, rather
than relying only on the current integration checkout. There were no hash
disagreements. The preserved stderr is empty. The largest file in this run
is 11,750 bytes, below the repository's large-artifact threshold.

## Independent reconstruction

The following existing-evidence command completed successfully:

```sh
PYTHONPATH=src .venv/bin/python -m distributed_discovery.behavioral_diversity.study --track track-03 --verify-existing results/exploratory/20261031T215933Z_DD-024_caa1bf80_614ce37ebc
```

It returned `new_primary_run: false`, `verification.passed: true`, no errors,
and all four required corruption rejections. The verifier checked:

- **80 cells**, each with all nine clue pairs and nine ordered tails:
  **6,480 candidate comparisons**.
- **45,360** target/searcher relabeling equalities.
- Four executed attempts, two clues, and two shared first-round detection
  outcomes for every policy.
- Detector-pattern weights and marginals, complete saved policies and ties,
  raw detection payoffs, fallback probability, conditional-disagreement
  values, and all reported contrasts.

The saved
[verification record](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_614ce37ebc/outputs/verification.json)
and the read-only reconstruction agree. A separate calculation, using only
saved row policy values and Fraction subtraction, rebuilt all four
estimands in all 80 cells and their positive/zero/negative counts and
extrema. It exactly matched both the indexed result summary and
[`outputs/summary.json`](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_614ce37ebc/outputs/summary.json).

For later reproduction, the command requires the frozen input bytes. The
task contract is among those inputs, so normal closeout edits to that
contract may require running existing-evidence verification in a checkout
of the recorded source commit with the immutable run made available there.
That is not authority to create another primary run or to alter the
original manifest.

## Grid completeness and audited summary

There are 80 unique cells, exactly the Cartesian product of:

- `p = {1/3, 1/2, 2/3, 5/6, 1}`;
- `r = {1/4, 1/2, 3/4, 1}`;
- `iid`, `searcher_persistent`, `round_common`, and `global_common`.

All seven registered policy values occur in every cell. The disagreement
stratum is correctly `null` in the 16 perfect-clue cells, where disagreement
has probability zero. It is not encoded as a zero success rate.

| Registered contrast | Positive cells | Zero cells | Negative cells | Minimum | Maximum on this grid |
| --- | ---: | ---: | ---: | ---: | ---: |
| Calibrated minus iid-assumed | 31 | 49 | 0 | `0/1` | `1/12` |
| Calibrated minus perfect-elimination | 36 | 44 | 0 | `0/1` | `1/4` |
| Cross-searcher minus same-searcher revisit | 12 | 68 | 0 | `0/1` | `1/8` |
| Calibrated minus precommitted calibrated | 0 | 80 | 0 | `0/1` | `0/1` |

The nonnegative calibrated regrets follow from its enumerated feasible
action class; their signs are not independent discoveries. The grid
magnitudes describe the specified comparison rules. They are not worst-case
bounds over unregistered accuracies, failure laws, or policy classes.

## Exact maximal witnesses

### Dependence misspecification: `1/12`

At `p=2/3`, `r=1/2`, with persistent searcher detector states:

- Calibrated joint continuation: `25/36`.
- Registered iid-assumed continuation: `11/18`.
- Difference: `1/12`, approximately **8.33 percentage points**.

This is the unique maximizing cell on the registered grid. The full saved
policy tables and candidate masses are in
[row 0037](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_614ce37ebc/outputs/rows/0037.json).
The iid-assumed rule uses the registered lexicographic tie choice. This
finding concerns that selected misspecified rule, not every policy that
could be optimal under an iid assumption. It does not establish a universal
price of failing to model dependence.

### Perfect-elimination rule: `1/4`

At `p=1`, `r=1/2`, with a detector state shared within each round and fresh
between rounds:

- Calibrated joint continuation: `3/4`.
- Perfect-elimination continuation: `1/2`.
- Difference: `1/4`, or **25 percentage points**.

This is the unique grid maximum, saved in
[row 0070](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_614ce37ebc/outputs/rows/0070.json).
The true reached mass of the impossible-assumed-history fallback is `1/2`.
With perfect clues, the failed perfect-detection assumption assigns zero
probability to those observed failures. The prescribed fallback then sends
search to unvisited labels. Thus the 25-point loss is specifically a result
for this prospectively completed restrictive rule; it must not be presented
as a generic empirical loss from planning or as a realistic human error rate.

### Cross-searcher rescue: `1/8`

At `p=1/2`, `r=1/2`, with persistent searcher detector states:

- Cross-searcher revisit: `9/16`.
- Same-searcher revisit: `7/16`.
- Difference: `1/8`, or **12.5 percentage points**.

This is the unique grid maximum, saved in
[row 0021](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_614ce37ebc/outputs/rows/0021.json).
The calibrated joint value is `5/8`, so the cross-revisit rule is itself a
restricted comparator rather than the full optimal continuation class.

## Analytic rescue qualification and mandatory zero control

The rescue contrast has a simple model-specific explanation. Under
persistent searcher detectors, exactly one correct clue with disagreement
has probability `2p(1-p)`. Cross rescue then needs the initially assigned
detector to be dead and the other to be live, a factor `r(1-r)`. The resulting
hand-check expression is `2p(1-p)r(1-r)`. Under iid, round-common, or
global-common detection, swapping the same target pair leaves the relevant
detection event/distribution unchanged and the contrast is zero. A
read-only comparison checked this expression against all 80 saved rows
with no disagreement.

This formula is an explanatory sanity check on a known redundancy mechanism,
not a promoted new theorem. The positive cells do not establish an
unanticipated general advantage of behavioral diversity.

The calibrated and precommitted calibrated policies are equal in **all
80 cells**. Only the double-failure branch can still improve terminal
success, so fixing the same clue-indexed tail table in advance reproduces
the feedback policy's objective value. The experiment therefore provides
**no positive adaptivity premium** over that matched precommitted control.

Finally, equal `r` means equal ex ante detector-bit marginals. Dependence
changes conditional reliability after observed failure, which is precisely
the intended mechanism. These synthetic comparisons establish no result
about human personalities, social welfare, or an optimal population mixture.
