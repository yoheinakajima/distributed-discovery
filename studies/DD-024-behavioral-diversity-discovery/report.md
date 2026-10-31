# DD-024: What behavioral variation contributes to discovery

## Outcome

This campaign preserved a 51-source interdisciplinary literature landscape, screened six research directions before implementation, and executed three registered finite experiments in parallel. Three directions closed for overlap with existing research. All three admitted experiments completed once from the same clean source revision and passed their independent numerical checks. The resulting 134 parameter cells are retained as **audited exploratory computations**, with no central claim promotion.

The experiments identify three distinct mechanisms: hedging uncertain evidence reliability through coordinated randomization; transferring a search when failures persist within a searcher; and information carried by the timing or absence of a message. Their useful comparisons include strong controls that often remove an apparent advantage. They do not estimate a benefit of personality traits, spontaneity, life planning, or any population mixture.

| Registered experiment | Grid | Main bounded observation | Decisive control |
| --- | ---: | --- | --- |
| 02: Ambiguous evidence reliability | 18 cells | Coordinated mixtures improve worst-regime success in 5 cells; maximum gain is `1/4`, or 25 percentage points. | All 9 one-success cells and all 6 perfect-diagnostic cells have zero mixture advantage. Deterministic plans already permit heterogeneous roles. |
| 03: Unreliable negative feedback | 80 cells | Cross-searcher revisits improve success in 12 cells; maximum gain is `1/8`, or 12.5 points. | A matched precommitted schedule equals the calibrated continuation policy in all 80 cells. |
| 04: Communication timing | 36 cells, 144 event comparisons | The largest event advantage over the better plain fixed schedule is `1/64`, or 1.5625 points, under individual MAP behavior. | No event advantage remains in any of the 144 comparisons against earlier delivery of the complete equivalent information. |

These counts describe the chosen finite grids, not population frequencies. Exact fractions are authoritative; percentages and percentage-point differences are display conversions. Every empirical-looking number below is a synthetic model output with the provenance listed in the [results index](results/README.md).

## How the literature was incorporated

The complete review, 51 annotated references, source JSON, and bibliography mapping are stored in [the literature archive](../../docs/literature/spontaneity-exploration-planning/README.md). The review is a broad landscape search rather than a certified systematic review. The [novelty matrix](novelty/index.md) links six dated screens saved before scientific code was written. Each screen examines external primary research, relevant completed DD studies, classical reductions, and a potential falsifier.

| Track | Disposition before implementation | Reason and retained scope |
| --- | --- | --- |
| 01: Stable specialists and rotating roles | Closed for overlap | A sufficiently broad adaptive team can keep fixed assignments; an exchangeable rotation can preserve the relevant success law. Introducing an explicit switching cost alone does not discover a new specialization mechanism. |
| 02: Adaptation and uncertain sources | Narrowed and executed | Broad randomization benefits are established in robust optimization. The admitted contribution is an exact interaction and comparator audit across regime ambiguity, common diagnostics, source dependence, and success thresholds. |
| 03: Commitment and feedback | Pivoted and executed | Recast as imperfect detection with different failure dependence. The experiment tests calibration, revisiting, and transfer while explicitly checking precommitment equivalence. |
| 04: Communication timing | Narrowed and executed | Event timing and silence can convey information. The experiment compares full observable transcripts and different receiver objectives before attributing a gain to timing. |
| 05: Information externalities and attribution | Closed for overlap | Strategic experimentation, free riding, marginal-contribution rewards, and attribution already cover the broad proposed mechanism. |
| 06: Execution reliability and downside | Closed for overlap | Common-mode failure, diversification, and downside constraints reduce to existing reliability or robust-coverage questions without an additional sharply specified mechanism. |

The three closures are literature and model-containment decisions, not failed empirical experiments. They used none of the primary execution allocation. The three admitted residual questions have not been established as worldwide novelties; their precise computations and attribution checks are the contribution preserved here.

## Experiment 02: Which kind of randomness helps?

### Model and comparison

Two agents each choose one of three target labels. There are two possible evidence regimes: in A, private clues have accuracy `1/3` and the public clue has accuracy `5/6`; in B those accuracies are reversed. A source-mixture parameter `rho` specifies whether private clues arise from a shared draw or independent draws. A common diagnostic is absent, 3/4 reliable, or perfect. Success means either at least one agent finds the target or both agents do.

The six-role library contains private followers, public followers, a specified third-label contrarian, and three constant-label roles. There are 36 deterministic role pairs without a diagnostic and 1,296 diagnostic-contingent plans with a binary diagnostic. The deterministic comparator already includes different roles for different agents. The coordinated class mixes over complete plans using a common random device. Nature chooses the reliability regime before the device is realized.

The computation evaluates all 15,768 plan vectors across the registered grid. The primary optimizer finds a mixture; a distinct direct-world verifier checks its execution and a dual upper bound against every deterministic plan. Optimality therefore applies to this declared finite role class and ambiguity objective, not arbitrary policies.

### Findings

The mixture-minus-deterministic contrast is positive in five cells, zero in thirteen, and never negative:

| Private-source mixture | Diagnostic | Required successes | Exact gain | Percentage points |
| --- | --- | ---: | ---: | ---: |
| `rho=0` | None | 2 | `1/6` | 16.6667 |
| `rho=0` | Noisy | 2 | `1/144` | 0.6944 |
| `rho=1/2` | None | 2 | `31/150` | 20.6667 |
| `rho=1/2` | Noisy | 2 | `217/46944` | 0.4623 |
| `rho=1` | None | 2 | `1/4` | 25.0000 |

At the maximum, a fair common coin chooses either both agents following the private clue or both following the shared clue. Each realized team uses the same role. Its success probability is `7/12` in either regime, versus the best deterministic worst-regime value of `1/3`: 58.3333% versus 33.3333%. This is coordinated hedging between plans. It is not evidence that permanent within-team personality heterogeneity generated the gain. See [the exact witness, row 0013](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_1d0ab47ae5/outputs/rows/0013.json).

All nine at-least-one-success cells have a zero mixture gain; both role classes attain `8/9`. All six perfect-diagnostic cells also have zero mixture gain. In 54 known-prior comparisons, a mixture never beats the best deterministic expected-success plan. A robust mixture ties that expected-value optimum in 39 combinations and is below it in 15. The worst-regime objective and the expected-value objective should therefore not be conflated.

### A comparator limitation that changes the interpretation

The independent-departure baselines choose between the shared clue and uniform random targeting. Their homogeneous and heterogeneous versions tie in every cell: `5/9` under one-success objectives and `1/3` under two-success objectives. They exclude private-following and other roles available to the broader class.

Their largest deficit to the coordinated class is 50 points at `rho=1` with perfect diagnosis and a two-success objective. At that same cell the mixture advantage over the deterministic role class is exactly zero. Reporting the 50-point deficit as the benefit of coordinating otherwise identical random noise would be incorrect. The main 25-point result uses the stronger, heterogeneous deterministic class; even that result concerns an additional common randomization resource under a specified ambiguity set.

The complete evidence, controls, exact positive cells, and independent saved-table reconstruction are in [the track 02 results audit](review-results-track02.md). The [prior-art screen](tracks/track-02/novelty.md) explains why the broad robust-randomization mechanism is not a new discovery.

## Experiment 03: When should somebody else try again?

### Model and comparison

Two agents search three targets over two rounds, with four attempts in every policy. Private clue accuracy `p` takes five registered values; per-attempt ex ante detection reliability `r` takes four. Four detector laws preserve that marginal reliability while changing dependence: independent failures, failures persistent within each searcher, failures shared within a round, and failures shared across the whole team and both rounds.

The policies share clues, first-round outcomes, and action budgets. Comparators include a calibrated joint allocator, its equivalent precommitted schedule, a rule assuming iid detectors, a rule incorrectly treating failure as perfect elimination, same-searcher revisits, cross-searcher revisits, and an unvisited-only restriction. The iid rule and the impossible-history fallback are explicitly selected rules, not statements about every optimizer under those assumptions.

### Findings and witnesses

| Contrast | Positive / zero / negative cells | Maximum | Exact witness values |
| --- | ---: | ---: | --- |
| Calibrated minus iid-assumed rule | 31 / 49 / 0 | `1/12` = 8.3333 points | `25/36` versus `11/18`, at `p=2/3, r=1/2`, searcher-persistent failures |
| Calibrated minus perfect-elimination rule | 36 / 44 / 0 | `1/4` = 25 points | `3/4` versus `1/2`, at `p=1, r=1/2`, round-common failures |
| Cross-searcher minus same-searcher revisit | 12 / 68 / 0 | `1/8` = 12.5 points | `9/16` versus `7/16`, at `p=1/2, r=1/2`, searcher-persistent failures |
| Calibrated minus matched precommitment | 0 / 80 / 0 | `0` | Equal in every cell |

The corresponding witnesses are [row 0037](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_614ce37ebc/outputs/rows/0037.json), [row 0070](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_614ce37ebc/outputs/rows/0070.json), and [row 0021](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_614ce37ebc/outputs/rows/0021.json).

In the revisit witness, changing searcher raises success from 43.75% to 56.25%. The advantage arises because one person's failed detector remains failed while another person's detector may work. Every cell matches the model-specific expression `2p(1-p)r(1-r)` for persistent searcher failures, with zero contrast under the other three laws. This agreement explains the result; it is not presented as a newly discovered general formula.

The zero precommitment contrast is equally important. Under this short terminal-discovery model, the relevant all-failure continuation can be encoded in advance. The experiment supplies no positive adaptability premium over that matched precommitted control. The result concerns how a policy interprets and allocates searches under dependent failures.

The 8.3333-point regret is specific to the registered lexicographic iid-assumed selection. At the largest perfect-elimination loss, the false assumed model assigns zero probability to a history that actually occurs, and its registered fallback is reached with probability `1/2`. The 25-point number must retain that qualification. Matching ex ante reliability also does not match the conditional reliability after a failure; those different conditional implications are the mechanism being tested.

The independent check enumerates detector worlds rather than reusing the primary failure-factorization calculation. It checks 6,480 continuation candidates, 45,360 relabeling equalities, every saved value, action budgets, and four prescribed corruptions. See [the track 03 results audit](review-results-track03.md) and [model registration](tracks/track-03/model.md).

## Experiment 04: Does timing help, or does it communicate another fact?

### Model and comparison

The sender observes clues `X` and `Z`; the receiver observes `Y`. All initial clues and the four-action budget are fixed across protocols. One packet carries `X`, either early, late, or at a time determined by whether `X` and `Z` agree. Independent yoked schedules match the arrival frequency without conditioning on the clues. Augmented controls send `(X,C)`, where `C` is the agreement bit that event timing or silence reveals.

Receiver policies are either a specified individual maximum-posterior rule (MAP) or a coverage-aware best response to the fixed sender policy. The stronger rule does not jointly optimize both agents. There are 36 source-law cells, eight protocols, and two receiver classes: 576 base rows, 144 event comparisons, and 144 explicit emulation policies.

### Findings

| Receiver | Event minus comparator | Positive | Zero | Negative |
| --- | --- | ---: | ---: | ---: |
| Individual MAP | Better plain fixed early/late schedule | 4 | 65 | 3 |
| Individual MAP | Timing-matched yoked schedule | 4 | 65 | 3 |
| Individual MAP | Earlier complete transcript | 0 | 69 | 3 |
| Coverage-aware | Better plain fixed early/late schedule | 4 | 54 | 14 |
| Coverage-aware | Timing-matched yoked schedule | 13 | 56 | 3 |
| Coverage-aware | Earlier complete transcript | 0 | 52 | 20 |

The largest apparent event advantage is `1/64`, or 1.5625 percentage points, under individual MAP at `M=3, p=1/2, q=3/4`. Either trigger attains `125/128`, versus `123/128` under either plain fixed schedule. Independent yoked timing also attains `123/128`, so matching delivery frequency leaves the gap. Sending the actual agreement bit attains `125/128`, removing it. These are 97.65625% versus 96.09375% discovery probabilities. See base rows [0064](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_30b8369b0c/outputs/rows/0064.json) through 0079 and the [complete comparison index](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_30b8369b0c/outputs/result.json).

At that same cell, coverage-aware fixed early delivery already attains one. The agreement-triggered coverage policy attains only `127/128`. Thus the largest MAP gain should not be described as a timing benefit surviving the stronger decision rule.

The largest coverage-aware gain against the better plain fixed schedule is `1/96`, approximately 1.0417 points: `31/32` versus `23/24` at `M=4, p=1/4, q=3/4`, agreement trigger. Earlier augmented information also attains `31/32`. Across both receiver classes, all 144 earlier-full-transcript residuals are zero or negative: 121 zero, 23 negative. All 144 explicit emulations equal their source event policy exactly.

Baseline choice changes the apparent frequency of benefits. Coverage-aware event policies beat fixed late delivery in 22/72 comparisons but beat the better fixed schedule in only 4/72. At `M=4, p=1/2, q=1/4`, an agreement event has value `47/48`: a gain of `1/144` over late delivery, but a loss of `1/48` against early delivery. These comparisons are all retained.

Eighteen of the 36 source-law cells contain a perfect sender clue. They guarantee discovery under every protocol and account for 72 automatic-zero event comparisons. These registered boundary controls are useful checks; they should not be counted as 72 difficult independent tests of a broad social hypothesis.

The independent verifier checks 285,208 local deviations and five substantive corruptions. The post-run reviewer separately executes all 720 saved policies from raw Fraction-weighted worlds without importing project scientific helpers; all values match. The [full timing audit](review-results-track04.md) includes complete sign tables and positive and negative witnesses. The model prices neither time nor communication nor cognition. Its complete-information control is therefore not a claim about costless earlier communication in actual organizations.

## What this changes about the original hypothesis

The original intuition links predictable planners, less predictable explorers, and collective progress. These experiments show why the intermediate mechanisms must be separated before testing that intuition about people.

First, a policy can deliberately plan to randomize. In the largest ambiguity witness, both agents follow the same rule in each realized trial; the team randomizes between plans. Second, a new searcher can help because their failures differ, even when their behavior is perfectly planned. Third, changing message timing can help because it communicates another fact, and a well-specified earlier message can supply that fact directly. Fourth, an adaptive policy can sometimes be exactly emulated by a precommitted schedule.

A useful next hypothesis is that behavioral variation helps when it preserves alternatives or independent failure modes that a group's shared model or decision rule would otherwise discard. That is a synthesis to test, not a result established about human traits. The present objective is target discovery, not welfare, creativity, long-run social change, or individual fulfillment.

For further synthetic work, the strongest remaining tests would require nonterminal feedback with genuinely different continuation histories; equally expressive independent and coordinated randomization classes; and explicit costs for switching, communication, or learning. Their novelty must be screened afresh before execution. To test the original claim about people, a separately designed human-team study would need measured traits, ability matching, strong adaptive-team controls, and identification of error dependence. Assigned policy effects, trait associations, and societal effects are separate inference steps. No such follow-up was executed here.

## Execution, verification, and disposition

All runs started at `2026-10-31T21:59:33Z` from clean detached worktrees at commit `caa1bf800bde9033e6b317e46bad0aff73828338` after the literature and novelty checkpoint `2ce35ccb1a8d12c720bdda713de830b9ecfc7ae9`. The complete grids were bound before execution. Each track consumed one atomic reservation, with a combined 120-second and 1024-MiB limit for evaluation, persistence, and independent checking. No primary was repeated.

| Track | Immutable run suffix | Worker time | Peak RSS | Numerical verification |
| --- | --- | ---: | ---: | --- |
| 02 | `caa1bf80_1d0ab47ae5` | 3.454253 s | 96,996 KiB | Passed; 4/4 prescribed corruptions rejected |
| 03 | `caa1bf80_614ce37ebc` | 1.222745 s | 24,960 KiB | Passed; 4/4 prescribed corruptions rejected |
| 04 | `caa1bf80_30b8369b0c` | 2.363524 s | 63,988 KiB | Passed; 5/5 prescribed corruptions rejected |

These times are preserved primary observations, not benchmark comparisons. Source/configuration hashes, environment, complete policy outputs, logs, validation, and full artifact inventories are preserved in the [three immutable run directories](results/README.md). The independent routes share scientific assumptions and basic exact arithmetic; agreement does not rule out model misspecification. Internal cross-agent review is not external peer review.

The pre-execution repository gate passed all 1,129 then-existing tests, required audits, seven paper builds, and the site build; the later runner compatibility fixtures passed before the freeze. Post-integration acceptance is recorded in the living ExecPlan and typed handoff. Separate [claim audit](claim-audit.md) records the permitted interpretations. The central ledger remains at 110 claims, existing paper evidence is unchanged, and this campaign ends at draft PR #232 for review.
