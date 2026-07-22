# Final handoff — Program V3

Program V3's required sequence is complete at its registered bounded scope.
This handoff creates no new research run. DD-015 remains an unexecuted optional
registration, and issue #32 remains a settings-only authority blocker.

## What was established

1. **DD-012 — attention.** For `r=1-p`, discovery is
   `G_N(0)=1-r^N` and `G_N(k)=1-(1-q)r^(N-k)` for `k>=1`. The first-use gain is
   `r^(N-1)(q-p)` and every duplicate-use margin is negative. One reader is
   uniquely optimal for `q>p`, zero for `q<p`, and `{0,1}` tie at equality.
   Equal-split attention equilibria are threshold counts because `Delta_k`
   strictly decreases. The exact grid retains excessive attention rather than
   a strategic all-ignore failure when `q>p`.
2. **DD-013 — audiences.** The binding audience optimum is the same `{0,1}`
   correspondence. Full-precision optimal publicity weakly dominates every
   registered feasible garbling, with 105 ties and 2,520 strict losses. Public
   universal pooling implements the optimal count correspondence in all 175
   cells with ex-post budget balance and zero external subsidy.
3. **DD-014 — conditional policies.** Registered contrarian roles never improve
   on the private/public planner optimum for `p>=1/3`; they tie only in 15
   uninformative-private cells. Conditional policies leave a best-equilibrium
   wedge in 23 of 75 cells. A raw two-label audit refutes unrestricted
   extrapolation by finding complementary constant-policy improvements.
4. **Tools and dissemination.** DiscoveryBench v2 has 20 tasks, 21 protocols,
   27 metrics, 28 compatible exact rows, and 392 explicit exclusions. The
   synthetic experiment v2 has 29 treatments, 14 hypotheses, 11 scenarios, 924
   power rows, and 924,000 draws. The five attention/audience public routes and
   their static data are live.

## Evidence identifiers

- DD-012: `20260721T212943Z_DD-012_9ed0928e_4a3f1ba62b`, DD-C-0059–0061.
- DD-013: `20260721T215811Z_DD-013_09c07448_cdac4fb512`, DD-C-0062–0065.
- DD-014: `20260721T222047Z_DD-014_f5f099a8_ea0276dd16`, DD-C-0066–0068.
- DiscoveryBench v2: `20260721T230249Z_DD-010_add85590_56c61a2195`, DD-C-0069.
- Synthetic experiment v2: `20260721T232119Z_DD-011_121162f8_e454b06d2c`, DD-C-0070.

No participant was recruited, no human data were collected, and no experiment
was conducted. DD-011's power values are conditional synthetic Monte Carlo
estimates, not behavioral results.

## Publication

*The Incentive to Ignore: Selective Attention and Audience Design in
Distributed Discovery* is a validated 20-page working paper. SHA-256:
`ee9e27f741d25a9597994f18caf2bf406098db7aca4d2ed067a7a011f64be250`.
Public page:
<https://yoheinakajima.github.io/distributed-discovery/publications/incentive-to-ignore.html>.
It has no DOI, submission, peer review, or verified novelty claim.

## Final acceptance

`make bootstrap`, `make verify`, `make papers`, and `make site` passed. The
current inventory is 183 tests, 70 claims, 40 manifests, 37 passing immutable
runs, 19 studies, five papers, 59 HTML routes, 59 public data files, 12 Labs,
and 19 checksum-covered downloads. Certificate/corruption, leakage/schema,
synthetic-only, PDF/render, download, secret, host-path, license, provenance,
upstream-cleanliness, browser/accessibility, Git, CI/Pages, and live-route gates
are recorded in `reports/project-status.md`.

## Preserved negative results and limits

- Equal-split incentives create duplicate attention in 63 grid cells; 24 cells
  sustain all-attend despite a unique one-reader optimum.
- Off-shared-success implements all-ignore; the registered positive assigned-
  reader subsidy has no socially optimal weak equilibrium on the DD-012 grid.
- DD-013 voluntary use differs from binding use in 656 settings, including 273
  excessive-use settings and eight welfare-multiplicity settings.
- Full broadcast is suboptimal in every DD-013 cell; garbling never beats the
  registered binding optimum.
- DD-014's restricted theorem is not an unrestricted-policy result.
- DiscoveryBench has no composite score, hosted leaderboard, or public
  submissions. DD-011 retains 335 below-threshold large-sample calibrations.

## Resume point

Start from clean `main`; do not rerun completed primary configurations. The
next substantive command is `git switch main && git pull --ff-only origin main
&& make verify`. The next orientation file is `docs/current-roadmap.md`.
Settings-only work must instead begin with issue #32 and intentionally supplied
settings-capable authority. New science requires a fresh bounded issue and
ExecPlan entry.
