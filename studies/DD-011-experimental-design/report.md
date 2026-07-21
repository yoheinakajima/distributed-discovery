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
