# Distributed Discovery

Distributed Discovery studies how organizations and multi-agent systems convert dispersed evidence into a finite portfolio of search actions. Its central distinction is that information aggregation and action allocation are different operations.

The Shared Discovery Paradox is the canonical atomic result: pooled evidence may improve candidate ranking while a one-answer action rule compresses many searches into repeated action, so better information can coexist with worse group discovery. The design principle is: **Share the evidence. Diversify the actions.**

> The canonical public paper and interactive guide remain in the upstream shared-discovery-paradox repository. This repository contains the broader research program, reproducibility infrastructure, companion materials, and extension studies.

This public repository is MIT-licensed. The [companion site](https://yoheinakajima.github.io/distributed-discovery/) is built from `site/src` on `main` and deployed through GitHub Actions; generated `site/dist` files are not committed. Canonical upstream remains separate and read-only.

## Status and navigation

Programs V1, V2, and the required Program V3 queue are complete at their
registered bounded scopes. Program V3,
[*The Incentive to Ignore*](docs/program-v3.md), completed DD-012 through
DD-014, the focused paper, versioned benchmark and synthetic experiment
extensions, and the public Labs. Program V4, *Threshold Discovery*, is complete
at its registered bounded scope: DD-015 through DD-018, DiscoveryBench v3, the
synthetic experiment v3 extension, the 20-page focused paper, and four
output-connected Labs are deployed. Program V5's documentation baseline and
DD-019 Signal Geometry is complete and deployed. DD-020 Incremental Sharing
and Independent Rescue is complete on its research branch with a passing
immutable run and five audited claims; deployment is pending PR #136. The concise entry points
are [`docs/current-state.md`](docs/current-state.md) and
[`docs/current-roadmap.md`](docs/current-roadmap.md). Claims remain in
[`claims/claims.yml`](claims/claims.yml) under the
[`claim-status policy`](docs/claim-status-policy.md); studies are indexed in
[`studies/index.md`](studies/index.md). DD-007 is synthetic-only. Program V2's
DD-008A, DD-006B, the exact bounded DD-009 Architecture Atlas, DiscoveryBench
v2, and the synthetic-only DD-011 v2 experiment kit are merged and deployed.
DD-008B adds a verified general-`N` Common-Source threshold theorem and a scoped
exact counterexample. The deterministic 20-page
[*Common-Source Trap* working paper](https://yoheinakajima.github.io/distributed-discovery/publications/common-source-trap.html)
and the 20-page [*Incentive to Ignore* working paper](https://yoheinakajima.github.io/distributed-discovery/publications/incentive-to-ignore.html)
are live. No real-data work is authorized; no
participants were recruited and no human experiment was conducted.

The output hierarchy, paper-admission rule, and living-synthesis relationship
are defined in [`docs/research-governance.md`](docs/research-governance.md) and
[`docs/publication-architecture.md`](docs/publication-architecture.md).

## Setup and common commands

Install [`uv`](https://docs.astral.sh/uv/), then run:

```sh
make bootstrap
make verify
```

The command interface is:

```sh
make test                 # unit, integration, and regression tests
make fetch-upstream       # cache the read-only canonical repository
make reproduce-baseline  # execute and record the pinned benchmark
make validate-claims      # validate the claim ledger
make foundations          # build/validate the companion note
make dd001                # run the registered DD-001 baseline configuration
make dd001-signatures     # run the registered DD-001A signature audit
make dd001-thresholds     # run the registered DD-001B threshold audit
make dd001-alignment-bound # certify the alignment-preserving DD-001 upper bound
make dd002-disclosure     # run the registered DD-002 disclosure audit
make dd002-selection-robustness # run the six-rule DD-002 selection catalogue
make dd003-source-graphs  # run the registered DD-003 graph census
make dd003-heterogeneous-sources # run the colored-source accuracy census
make dd004-sequential       # run the perfect-elimination sequential baseline
make dd005-coverage         # run the overlapping-coverage frontiers
make dd006-mechanisms       # run the score-difference mechanism catalogue
make dd006b-joint-mechanism # run the normalized joint-mechanism frontier
make dd007-synthetic-audit  # run the synthetic-only recovery audit
make dd008b-analysis         # audit the general-N common-source threshold theorem
make dd009-atlas             # run the aligned architecture registry and Pareto census
make dd010-discoverybench    # run the exact golden benchmark and bounded seeded sensitivity
make dd010-attention         # run the versioned selective-attention benchmark extension
make dd011-experiment        # run the synthetic design, power grid, and separate verifier
make dd011-attention         # run the versioned synthetic attention design extension
make dd012-attention         # run the exact access-gated attention census
make dd013-audience          # run the binding/voluntary audience census
make dd014-conditional       # run the conditional-policy census and raw audit
make dd016-threshold         # run the registered exact threshold-discovery census
make dd020-preview           # inspect DD-020 exact summaries without creating a run
make dd017-equilibrium       # run the bounded threshold-equilibrium registry
make papers               # build all paper artifacts
make site                 # build the public companion site locally
make all                  # verify, reproduce canonical baseline, build papers and site
```

The reproduction and registered study targets create new immutable run directories, so use them intentionally. `make site` produces a local preview in `site/dist`; only the Pages workflow publishes that generated artifact.

## Resume protocol

New agents must read `AGENTS.md`, `.agent/PLANS.md`, `plans/MASTER_EXEC_PLAN.md`,
`docs/repository-contract.md`, and the relevant study files. Then inspect Git
status and run `git switch main && git pull --ff-only origin main && make verify`.
Do not rerun completed primary configurations merely to refresh timestamps.
Program V3 primary configurations are complete and must not be rerun merely to
refresh timestamps. Any extension needs a new bounded issue, state-space cap,
and verification plan. Settings-only issue #32 must not be retried without
intentionally supplied authority.
