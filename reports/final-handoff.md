# Final handoff — Program V2

Program V2 is complete at its registered bounded scope. The authoritative
detailed acceptance record is [`project-status.md`](project-status.md); concise
navigation begins at [`docs/current-state.md`](../docs/current-state.md) and
[`docs/current-roadmap.md`](../docs/current-roadmap.md).

## Delivered

- DD-010 DiscoveryBench: 15 exact golden tasks, 13 protocols, 19 metrics, 16
  compatible exact vectors, capability-isolated execution, independent
  verification, corruption tests, and a separated 8,000-draw sensitivity suite.
- DD-011: a frozen 20-cell, eight-hypothesis design with eight declared response
  scenarios, 384 power/MDE rows, 384,000 seeded draws, 140 retained
  large-sample calibration failures, and preregistration-ready read-only
  materials.
- DD-008B: a general finite-team private-threshold/equilibrium-count theorem,
  an exact all-common trap of width `p(1-p)/N`, and an exact interior
  counterexample to universal under-acquisition.
- *The Common-Source Trap*: a deterministic, visually audited 20-page working
  paper, SHA-256
  `c997bba31c021bd799f2b3a561e8e558a1334f844aa87a448ade10319dac2ad3`.
- A static, no-tracking public surface with 48 HTML routes, eight Labs, complete
  no-JavaScript fallbacks, and a 15-artifact download checksum manifest.

Primary runs are:

- DD-010 `20260721T183014Z_DD-010_ce930050_8ec718c242`
- DD-011 `20260721T185647Z_DD-011_fa0271d9_fcaa647c55`
- DD-008B `20260721T192412Z_DD-008B_649deb08_29dbeaf3a9`

The repository contains 58 claims, 32 passing runs among 35 immutable manifests,
15 registered studies, four validated papers, 94 Python source files, and 138
passing tests. Final acceptance created no duplicate immutable run.

> **No participants were recruited. No human data were collected. No experiment
> was conducted. Separate ethics and institutional review are required before
> deployment.**

The DD-011 kit is not preregistered or deployed. The paper has no DOI,
submission, peer review, or verified novelty claim. DiscoveryBench is not a
hosted leaderboard or universal measure. DD-006B is subsidized and does not
establish budget balance; DD-009 is a bounded Atlas, not a universal ranking.

All Program V2 research, paper, and site issues/PRs through #75/#76 are closed
and merged. Issue #77 / PR #78 provide this documentation-only handoff. Stale
paper issue #52 was closed after reconciliation. Settings issue #32 remains open
because the single authorized authentication attempt failed before mutation;
do not retry without intentionally supplied authority.

Resume with:

```sh
git switch main && git pull --ff-only origin main && make verify
```

There is no automatic next research task. New theory, benchmark tasks, adapters,
or human-study work require a fresh bounded registration and the applicable
evidence/ethics gates.
