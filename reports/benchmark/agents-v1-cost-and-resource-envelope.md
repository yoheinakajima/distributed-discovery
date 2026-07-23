# DiscoveryBench Agents v1 cost and resource envelope

Pricing date: 2026-07-23. Cost authorized: **false**. Cost incurred:
**false**. Owner approval required: **true**.

The frozen design has five task families, 138 generator cells, ten planned
public calibration cases, four planned private batches containing 200 total
instances, five agent architectures, one exact comparator, four audited model
candidates, and three base repeats. No case has been generated or executed.

For team size \(n\), the maximum call count across the five agent
architectures for one instance/model/repeat is \(12n\): isolated \(n\),
broadcast \(3n\), designated-reader \(2n\), consensus \(3n\), and structured
portfolio \(3n\). The exact comparator makes no model call.

| Scenario | Calls | Input/output ceiling | Estimated cloud cost |
|---|---:|---:|---:|
| 10-case public calibration, two clouds, one repeat, team 2 | 480 | 0.48M / 0.123M | $3.16 |
| 200-case base, two clouds, three repeats, team 4 | 57,600 | 115.2M / 14.746M | $537.98 |
| high sensitivity, three clouds, five repeats, team 6 | 216,000 | 864M / 110.592M | $3,418.56 |

The base estimate splits calls evenly between OpenAI GPT-5.4 at
$2.50/MTok input and $15/MTok output and Anthropic Sonnet 4.6 at
$3/MTok input and $15/MTok output. It assumes no cache or batch discount and
therefore avoids depending on an unverified discount. The high case adds
Gemini 2.5 Pro at its documented at-or-below-200k rate solely as a resource
sensitivity; that model remains blocked by the snapshot gate.

The local Mistral candidate needs a separately approved hardware gate. Reserve
at least 64 GB GPU memory, 64 GB system RAM, 16 CPU cores, and 128 GB storage
for the official unquantized path; a 32 GB quantized path changes the execution
configuration and needs its own comparability audit. Base storage reserves are
3 GB raw traces, 1 GB redacted traces, and 0.25 GB encrypted custody
artifacts. Independent verification is budgeted at 12 CPU-hours.

The recommended future execution cap is $750, not an authorization. If a
preflight forecast exceeds it, execution stops for owner review. Task families,
estimands, and repeats may not be reduced after prices or pilot outputs are
seen without a versioned design amendment explaining the scientific tradeoff.
