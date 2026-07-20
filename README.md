# Distributed Discovery

Distributed Discovery studies how organizations and multi-agent systems convert dispersed evidence into a finite portfolio of search actions. Its central distinction is that information aggregation and action allocation are different operations.

The Shared Discovery Paradox is the canonical atomic result: pooled evidence may improve candidate ranking while a one-answer action rule compresses many searches into repeated action, so better information can coexist with worse group discovery. The design principle is: **Share the evidence. Diversify the actions.**

> The canonical public paper and interactive guide remain in the upstream shared-discovery-paradox repository. This repository contains the broader research program, reproducibility infrastructure, companion materials, and extension studies.

This repository is private and must not be published or deployed. Upstream is read-only.

## Status and navigation

Verified, sourced, exploratory, refuted, and open claims are distinguished in [`claims/claims.yml`](claims/claims.yml) under the policy in [`docs/claim-status-policy.md`](docs/claim-status-policy.md). The active work and exact resume point are in [`plans/MASTER_EXEC_PLAN.md`](plans/MASTER_EXEC_PLAN.md). See [`studies/index.md`](studies/index.md), [`results/index.md`](results/index.md), and [`docs/index.md`](docs/index.md) for research navigation.

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
make papers               # build all paper artifacts
make site                 # build the private local companion site
make all                  # complete routine validation
```

Until M1 and M6 complete, baseline and DD-001 commands may report precise registered blockers rather than research results. Paper and site outputs remain local.

## Resume protocol

New agents must read `AGENTS.md`, `.agent/PLANS.md`, `plans/MASTER_EXEC_PLAN.md`, `docs/repository-contract.md`, and the active study files. Then inspect Git status and run the acceptance command named at the plan’s restart point.
