# DD-024 track 04: independent results audit

## Disposition

**Audited exploratory computation; zero central claims promoted.** This
review found no discrepancy in the preserved hashes, source/configuration
bindings, saved-policy values, or comparison arithmetic. The numerical
scope is the registered 36-cell finite model and its two specified receiver
classes. The results do not establish worldwide novelty, a human personality
effect, or a societal-welfare conclusion.

Review date: 2026-10-31 UTC. Evidence run:
[`20261031T215933Z_DD-024_caa1bf80_30b8369b0c`](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_30b8369b0c/README.md).
Frozen source: `caa1bf800bde9033e6b317e46bad0aff73828338`.

No primary run, source edit, configuration change, result mutation, or claim
ledger change was performed in this audit. Only this review file was written.

## Provenance and integrity

Independently recomputed SHA-256 hashes for all **588 files** in the complete
artifact inventory and all **586 manifest output bindings**. All matched.
The inventory covers exactly the preserved files except the manifest and
inventory itself; the manifest binds the inventory. The complete safe-output
mapping also matches the manifest, including the individual row files.

All **11 frozen input hashes** match both their content in the source commit
and the current integration checkout. The manifest records a clean source
tree, exit status zero, completed termination, and passing validation.
The saved configuration's canonical JSON digest agrees with the reservation,
manifest, and frozen registration. Its raw file digest is different by
design because the canonical digest ignores JSON formatting.

| Artifact or binding | SHA-256 |
| --- | --- |
| Canonical configuration | `30b8369b0c82b6c717f9e4d9e0ad594eca0edc5c07abd63ca6b261466fb78383` |
| Saved `config.json` bytes | `78e596b79fe785755e06ae380297e682a613499de03c186a932229b3967cc7b4` |
| `manifest.json` | `3363e7beed3e7584cc50b0142dc0c52e880dd5e251e42e0913357ec5398a1f94` |
| `artifact-hashes.json` | `255d8d12346f8d93f3630af0246a9a2390ee79716f3a26112399a3add5dd5eef` |
| `outputs/result.json` | `0c1da552b6fd84c0f08369ffd2a509d5e7e17ef7d1e3045958a95762c4cc7144` |
| `outputs/verification.json` | `cfdd81af1d65ce3858ac3fe1592ff629746b51dcb773ee3b76c6ef9d20aa6865` |
| Frozen `timing.py` | `dd45bd1bcfb37b2f6153475e92c6547a2b139851115a6a3eaf3658b620874243` |

The run records Python 3.12.14, PyYAML 6.0.3, jsonschema 4.26.0, and pytest
8.4.2. Its recorded worker time is 2.363524 seconds and peak RSS is 63,988
KiB, within the enforced 120-second / 1,024-MiB limits. The validation wall
measurement is 2.471802 seconds. These are preserved runtime observations,
not new timing measurements made by this review. No random seeds apply.

## Independent numerical checks

The review loaded the **576 individual base-row files**, covering 36 source
laws, eight protocols, and two receiver classes. It rebuilt the row lookup
and recalculated each of the **144 event comparisons** directly from base
values with Python's `Fraction`, including the maximum of the fixed early
and fixed late controls. All stored comparison fractions agree.

In a separate source-independent calculation, the reviewer enumerated raw
target and clue outcomes, reconstructed A's two actual own-feedback actions,
integrated each timing rule/independent timing coin, rebuilt B's observable
history, and executed the saved B policy. This used standard-library code
only and did not import the project's probability, optimization, or
verification helpers. All **720 saved policies**—576 base and 144 event
emulations—reproduce their saved exact values. All **288 protocol-world
normalizations** equal one. No policy was reoptimized and no parameter cell
was added. This is another implementation of direct world enumeration, not
a claim to a new mathematical verification method.

The preserved registered verifier additionally reports 285,208 local
deviation checks, all 576 raw rows checked, all 144 emulations checked,
and successful rejection of all five prescribed corruptions. Its substantive
corruption path and the limits of its label-conjugation diagnostic were
reviewed separately in [the pre-freeze audit](review-track04.md).

## Aggregate comparison counts

Each receiver has **72 event contrasts**: two triggers in each of 36 cells.
Entries below are event value minus the named comparator. Positive means
the event policy has greater terminal team discovery probability. Counts
describe this finite grid; they are not frequencies in a sampled population
or estimates for arbitrary environments.

| Receiver | Comparator | Positive | Zero | Negative | Minimum | Maximum |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Individual MAP | Fixed early, payload X | 4 | 65 | 3 | -1/72 | 1/64 |
| Individual MAP | Fixed late, payload X | 4 | 65 | 3 | -1/72 | 1/64 |
| Individual MAP | Better of fixed early/late X | 4 | 65 | 3 | -1/72 | 1/64 |
| Individual MAP | Corresponding timing-matched yoked X | 4 | 65 | 3 | -1/72 | 1/64 |
| Individual MAP | Early full transcript (X,C) | 0 | 69 | 3 | -1/72 | 0 |
| Individual MAP | Late full transcript (X,C) | 3 | 69 | 0 | 0 | 1/72 |
| Coverage-aware | Fixed early, payload X | 4 | 54 | 14 | -1/48 | 1/96 |
| Coverage-aware | Fixed late, payload X | 22 | 50 | 0 | 0 | 1/48 |
| Coverage-aware | Better of fixed early/late X | 4 | 54 | 14 | -1/48 | 1/96 |
| Coverage-aware | Corresponding timing-matched yoked X | 13 | 56 | 3 | -7/2048 | 1/96 |
| Coverage-aware | Early full transcript (X,C) | 0 | 52 | 20 | -1/48 | 0 |
| Coverage-aware | Late full transcript (X,C) | 20 | 52 | 0 | 0 | 1/48 |

For the prespecified best-fixed contrast, the trigger-level counts are:

| Receiver / trigger | Positive | Zero | Negative |
| --- | ---: | ---: | ---: |
| MAP / agreement | 2 | 31 | 3 |
| MAP / disagreement | 2 | 34 | 0 |
| Coverage / agreement | 2 | 24 | 10 |
| Coverage / disagreement | 2 | 30 | 4 |

There are eight positive best-fixed comparison entries across both classes,
but **zero positive early-full-transcript residuals in all 144 entries**:
121 residuals are zero and 23 are negative. All 144 event-policy emulations
under early augmented information equal their source event policy exactly.
Coverage dominance is a model-class containment check; the absence of a
positive matched-transcript MAP residual is an additional bounded observation,
not a general dominance theorem for myopic policies.

Eighteen of the 36 source-law cells have `p=1` or `q=1`. A then has a perfect
clue, and every protocol/receiver attains discovery one. These account for
288 base rows and **72 automatic-zero event comparisons**. They were
registered boundary controls and remain visible; the zero counts must not
be presented as evidence from 144 equally difficult search situations.

## Largest apparent benefit: the agreement bit removes the residual

The largest event-minus-best-fixed gain is **1/64**, or **1.5625 percentage
points**, for individual MAP with `M=3, p=1/2, q=3/4`. Both trigger schedules
attain it. The complete values at this witness are:

| Protocol | Individual MAP | Coverage-aware |
| --- | ---: | ---: |
| Early X | 123/128 | 1 |
| Late X | 123/128 | 127/128 |
| Agreement trigger | 125/128 | 127/128 |
| Disagreement trigger | 125/128 | 1 |
| Yoked agreement | 123/128 | 2039/2048 |
| Yoked disagreement | 123/128 | 2041/2048 |
| Early (X,C) | 125/128 | 1 |
| Late (X,C) | 125/128 | 127/128 |

The agreement trigger and its yoked control both arrive early with
probability `7/16`; the disagreement pair both arrive early with probability
`9/16`. Thus merely matching delivery frequency does not remove the MAP
gain. **Providing the actual agreement bit does:** either fixed augmented
schedule attains the same `125/128` as the events. The evidence supports an
information-content explanation at this witness, not an intrinsic advantage
of event timing over equally informative early delivery.

The receiver restriction also matters. In the same cell, coverage-aware
early X already attains one. Its agreement event loses `1/128` against that
fixed control and `7/2048` against its yoked control, while its disagreement
event ties the best fixed value. Consequently the largest MAP apparent gain
cannot be described as a benefit persisting under the stronger receiver.

Evidence locations: cell `m3-p1of2-q3of4`; base rows `0064.json` through
`0079.json`; comparison IDs ending in
`agreement_trigger/individual_map` and
`disagreement_trigger/individual_map` in `outputs/result.json`.

## Largest coverage-aware apparent benefit

For `M=4, p=1/4, q=3/4`, the agreement trigger improves coverage-aware value
from **23/24** under either plain fixed schedule to **31/32**. Its gain is
**1/96**, approximately **1.0417 percentage points**. Early augmented
information also attains **31/32**, again leaving zero residual.

| Coverage-aware protocol group | Value |
| --- | ---: |
| Early X; late X; either yoked schedule | 23/24 |
| Agreement trigger; early (X,C) | 31/32 |
| Disagreement trigger; late (X,C) | 185/192 |

The corresponding matched early-arrival probabilities are `1/4` for
agreement and `3/4` for disagreement. Here X and Y are individually
uninformative about the target, but C reveals a relationship between X and
A's informative clue Z. That can help B account for A's likely coverage.
The early augmented receiver has the same complete event transcript in
time to emulate either event rule. The equality at the maximum is observed
in the saved values and the explicit emulation; it does not require an
asserted additive causal decomposition.

Evidence locations: cell `m4-p1of4-q3of4`; base rows `0208.json` through
`0223.json`; comparison ID
`m4-p1of4-q3of4/agreement_trigger/coverage_aware`.

All positive best-fixed entries are retained, not only the maxima:

| Receiver | Cell | Agreement gain | Disagreement gain |
| --- | --- | ---: | ---: |
| MAP | M=3, p=1/2, q=3/4 | 1/64 | 1/64 |
| MAP | M=4, p=1/2, q=3/4 | 1/72 | 1/72 |
| Coverage | M=4, p=1/4, q=3/4 | 1/96 | 1/192 |
| Coverage | M=5, p=1/5, q=3/4 | 3/400 | 1/200 |

## Negative witnesses and baseline sensitivity

The largest MAP loss occurs for the agreement trigger at
`M=3, p=1/3, q=3/4`: event value **65/72**, versus **11/12** under either
plain fixed schedule and early augmented delivery. The difference is
**-1/72**. Coverage-aware value is one for every protocol in that cell.

The largest coverage loss occurs for the agreement trigger at
`M=4, p=1/2, q=1/4`: event value **47/48**, versus **one** under fixed early
or early augmented delivery. The loss is **1/48**, approximately **2.0833
percentage points**. Fixed late is only **35/36**, so comparison with late
alone would instead show an event gain of **1/144**. The corresponding yoked
agreement policy also attains **47/48**.

This illustrates the aggregate baseline issue: coverage-aware events beat
fixed late in 22 entries, but beat the better fixed schedule in only four.
Neither figure supports a claim that intermittent delivery generally beats
the best use of earlier information.

## Interpretation and limits

The audited output supplies a concrete timing-channel diagnostic: apparent
event advantages of up to `1/64` occur against plain-message controls, and
matching delivery frequency alone can leave those differences intact.
Matching the **complete information content** removes every positive
early-information residual in the registered grid. Negative differences and
the zero controls are part of the result, not exclusions.

The coverage-aware optimizer is a best response to fixed A behavior with
the declared two-action horizon; it does not jointly optimize both agents
or characterize all organizational communication designs. Individual MAP
is a prescribed myopic policy, not a measured personality or equilibrium.
The model has no time reward, communication cost, cognitive cost, false
detections, or social-welfare objective. Counts and extrema apply to the
prespecified finite grid, including its deterministic boundaries; they are
not continuous-parameter phase boundaries or out-of-sample estimates.

The appropriate integration outcome is **audited exploratory evidence with
zero central claims**, preserving the immutable run and the prior novelty
screen. A general mechanism or human applicability claim would require a
separate argument and evidence beyond this audit.
