# DD-011 report

Primary run `20260721T185647Z_DD-011_fa0271d9_fcaa647c55` starts from clean
commit `fa0271d9` and passes its separate verifier. The selected 20-cell design
assigns 640 balanced synthetic IDs. It evaluates eight frozen hypotheses under
eight response scenarios and six sample sizes with 1,000 replications per row:
384 power rows and 384,000 Monte Carlo draws.

All eight assumed effects in the rational-response scenario reach estimated power
of at least 0.80 by total sample size 960; seven do so by 640. This favorable
limiting scenario does not generalize: 140 of the 192 rows evaluated at sample
sizes 640, 800, or 960 remain below 0.80. Those calibration failures are retained.
Power, Wilson intervals, and MDEs are conditional estimates, not exact results.

Four exact project fixtures are checked as limiting synthetic ground truth:
DD-008, bounded DD-008A, DD-006B, and DD-009. They are not human treatment
effects. The verifier independently recreates all random streams and rejects an
altered power count, a real-looking identifier, and removal of the ethics flag.

> **No participants were recruited. No human data were collected. No experiment
> was conducted. Separate ethics and institutional review are required before
> deployment.**

Selective-attention v2 run
`20260721T232119Z_DD-011_121162f8_e454b06d2c` preserves the v1 package and
extends it to 29 cells, 14 hypotheses, 19 outcomes, 11 response scenarios, 928
balanced synthetic assignments, and 924 power rows with 924,000 seeded draws.
The separate verifier reproduces every rejection count. All 335 below-threshold
rows among the 462 large-sample checks are retained. Under the rational-attention
scenario at N=960, H13 and H14 remain below 0.80 at 0.764 and 0.632; these are
calibration failures, not behavioral results. Claim DD-C-0070 is synthetic
Monte Carlo evidence only.

Threshold/dynamic v3 run
`20260722T061958Z_DD-011_5743ccba_19b6517655` preserves v1/v2 and extends the
registry to 37 cells, 20 hypotheses, 23 outcomes, and 14 response scenarios.
It generates 1,184 balanced synthetic assignments and 1,680 power rows from
1,680,000 seeded draws. The separate verifier reproduces every rejection count,
the complete shared-seed v2 grid, and four immutable Program V4 source fixtures.
All 644 below-threshold rows among the 840 large-sample checks are retained. In
the favorable rational scenario at N=960, H15–H20 are respectively 1.000,
0.999, 0.918, 0.948, 1.000, and 0.999. Claim DD-C-0088 is conditional synthetic
Monte Carlo evidence only, not a human or behavioral result.
