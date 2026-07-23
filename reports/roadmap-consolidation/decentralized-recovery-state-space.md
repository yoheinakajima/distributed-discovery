# Decentralized Recovery state-space and resource audit

Evidence class: read-only registration audit over immutable DD-021 run
`20260722T185924Z_DD-021_3cdbbc40_2fea269a9a`. No DD-021 target was rerun and
no candidate study execution occurred.

## Inherited channel slice

The `M=3,N=2` slice contains 16 channel laws. Thirteen have three signals and
three confidence channels have six. Therefore the raw ordered signal-pair count
is

`13*3^2 + 3*6^2 = 225`.

Of these, 207 have positive probability and 18 are off support. Exact Bayes
reconstruction from the immutable `channels.json` yields 46 distinct labeled
posterior vectors across the slice and 15 classes after sorting target masses.
Among the 207 positive rows, 108 satisfy `b>a/2`, 18 satisfy `b=a/2`, and 81
satisfy `b<a/2`. Among the 15 permutation classes the counts are seven, one,
and seven respectively. These are registration observations, not claims.

There are three target states. Primitive target/signal rows therefore number
`3*225=675` before excluding zero-probability signal pairs and `3*207=621`
on support.

## Simultaneous game

Each posterior has `3^2=9` labeled action profiles. Each profile has two
players and two alternative actions, hence four unilateral deviations and 36
checks per posterior. Across 207 on-support rows this is 1,863 action profiles
and 7,452 deviation checks. The 15-class regression reduction has 135 profiles
and 540 deviations, but the primitive method must retain all 207 labeled rows.

## Sequential game

Each posterior has one root, three second-mover histories, and nine terminal
histories: 13 histories total. There are three second-mover decision nodes and
nine continuation actions. Agent 1 has three pure strategies; Agent 2 has
`3^3=27` contingent strategies; the normal-form cross product has 81 pure
strategy profiles.

A deliberately redundant full audit checks, for each of 81 strategy profiles,
three second-mover nodes and two deviations (486 checks) plus two first-mover
deviations (162 checks), for 648 SPE checks per posterior and 134,136 across
the 207 on-support rows. The direct backward-induction implementation is much
smaller, but the redundant count is the hard verification workload.

## Channel, regression, corruption, and output counts

The planned channel aggregation has 16 rows. The symbolic regression table has
15 posterior-permutation rows and explicitly labels strict-recovery,
tie-boundary, and collision witnesses. Twelve semantic corruptions are
registered. A future evidence bundle would have ten expected output files:
posterior rows, simultaneous correspondence, sequential correspondence,
channel summary, comparison regressions, witnesses, method agreement,
verification, corruptions, and summary/provenance.

## Resource boundary

All signs and averages use exact rational arithmetic. Network access, Monte
Carlo, and floating-point sign authority are prohibited. A future complete
audit is estimated below two seconds and 64 MiB peak memory. The frozen hard
caps are 30 seconds and 256 MiB. Any cap breach, method disagreement, missing
equilibrium, failed invariant, or unrejected corruption would stop evidence
promotion.

The decision is `stop-classical-overlap`, so these caps authorize no future
run on this branch and are retained only to show that resources and
verification were not the reason for stopping.
