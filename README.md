# Distributed Discovery

Distributed Discovery studies how organizations and multi-agent systems convert dispersed evidence into a finite portfolio of search actions. Its central distinction is that information aggregation and action allocation are different operations.

The Shared Discovery Paradox is the canonical atomic result: pooled evidence may improve candidate ranking while a one-answer action rule compresses many searches into repeated action, so better information can coexist with worse group discovery. The design principle is: **Share the evidence. Diversify the actions.**

> The canonical public paper and interactive guide remain in the upstream shared-discovery-paradox repository. This repository contains the broader research program, reproducibility infrastructure, companion materials, and extension studies.

This public repository is MIT-licensed. The [companion site](https://yoheinakajima.github.io/distributed-discovery/) is built from `site/src` on `main` and deployed through GitHub Actions; generated `site/dist` files are not committed. Canonical upstream remains separate and read-only.

## Status and navigation

Program V1 bounded studies are complete through DD-008. The concise entry points
are [`docs/current-state.md`](docs/current-state.md) and
[`docs/current-roadmap.md`](docs/current-roadmap.md). Claims remain in
[`claims/claims.yml`](claims/claims.yml) under the
[`claim-status policy`](docs/claim-status-policy.md); studies are indexed in
[`studies/index.md`](studies/index.md). DD-007 is synthetic-only. Program V2's
DD-008A evidence is merged and DD-006B has a completed exact bounded frontier;
the queued Architecture Atlas is next. No real-data work is authorized.

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
make papers               # build all paper artifacts
make site                 # build the public companion site locally
make all                  # verify, reproduce canonical baseline, build papers and site
```

The reproduction and registered study targets create new immutable run directories, so use them intentionally. `make site` produces a local preview in `site/dist`; only the Pages workflow publishes that generated artifact.

## Resume protocol

New agents must read `AGENTS.md`, `.agent/PLANS.md`, `plans/MASTER_EXEC_PLAN.md`, `docs/repository-contract.md`, and the active study files. Then inspect Git status and run the acceptance command named at the plan’s restart point. The authorized A–E queue through bounded DD-003 is complete at the evidence layer; the final merge/deployment handoff is recorded in the plan.
