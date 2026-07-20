# Distributed Discovery

Distributed Discovery studies how organizations and multi-agent systems convert dispersed evidence into a finite portfolio of search actions. Its central distinction is that information aggregation and action allocation are different operations.

The Shared Discovery Paradox is the canonical atomic result: pooled evidence may improve candidate ranking while a one-answer action rule compresses many searches into repeated action, so better information can coexist with worse group discovery. The design principle is: **Share the evidence. Diversify the actions.**

> The canonical public paper and interactive guide remain in the upstream shared-discovery-paradox repository. This repository contains the broader research program, reproducibility infrastructure, companion materials, and extension studies.

This public repository is MIT-licensed. The [companion site](https://yoheinakajima.github.io/distributed-discovery/) is built from `site/src` on `main` and deployed through GitHub Actions; generated `site/dist` files are not committed. Canonical upstream remains separate and read-only.

## Status and navigation

Verified, sourced, exploratory, refuted, and open claims are distinguished in [`claims/claims.yml`](claims/claims.yml) under the policy in [`docs/claim-status-policy.md`](docs/claim-status-policy.md). DD-000 through DD-001 have reproducible evidence; DD-001A proves a lossless policy-signature reduction and certifies its canonical state-space barrier, while the canonical objective remains unresolved. DD-002 through DD-007 have actionable briefs but no results. The active A–E execution queue and exact resume point are in [`plans/MASTER_EXEC_PLAN.md`](plans/MASTER_EXEC_PLAN.md). See [`reports/project-status.md`](reports/project-status.md), [`studies/index.md`](studies/index.md), [`results/index.md`](results/index.md), and [`docs/index.md`](docs/index.md) for research navigation.

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
make papers               # build all paper artifacts
make site                 # build the public companion site locally
make all                  # verify, reproduce canonical baseline, build papers and site
```

`make reproduce-baseline`, `make dd001`, and `make dd001-signatures` create new immutable run directories, so use them intentionally. `make site` produces a local preview in `site/dist`; only the Pages workflow publishes that generated artifact.

## Resume protocol

New agents must read `AGENTS.md`, `.agent/PLANS.md`, `plans/MASTER_EXEC_PLAN.md`, `docs/repository-contract.md`, and the active study files. Then inspect Git status and run the acceptance command named at the plan’s restart point. DD-001A is complete; the next research task is the exact DD-001B two-searcher hybrid-threshold analysis.
