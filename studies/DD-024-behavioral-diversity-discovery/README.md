# DD-024: Behavioral Diversity in Discovery

## Question

When does stable variation in discovery behavior improve group performance beyond homogeneous intermediate policies, adaptive generalists, and rotating roles with the same information and action budgets?

This is a bounded synthetic research campaign motivated by the [interdisciplinary literature review](../../docs/literature/spontaneity-exploration-planning/README.md). It extends the actual finite Shared Discovery Paradox search model with novelty-screened behavioral mechanisms. The existing TreasureBench golden-vector runner is a contract check, not a simulator for these new policies.

## Registration sequence

1. Preserve the literature review and campaign authority.
2. Launch six separate novelty screens, distributed across parallel research agents. Each names closest external papers, overlapping repository studies, a falsifiable additional question, and an explicit proceed/pivot/overlap disposition.
3. Freeze admitted models, comparison policies, primary estimands, parameter grids, resources, independent verification, corruptions, and stop rules before any primary result.
4. Run each frozen track once from clean committed source, in parallel where independent; retain every failure and null.
5. Independently audit numerical outputs and record calibrated findings before synthesis.

The living plan is [BEHAVIORAL_DIVERSITY_DISCOVERY.md](../../plans/BEHAVIORAL_DIVERSITY_DISCOVERY.md). DD-023 remains unallocated for its previously identified TreasureBench evaluation prospectus; this separate synthetic study starts at DD-024.

## Scope

At most six bounded primary sub-runs, initially capped at 120 seconds and 1 GiB each. A gate may close a candidate for overlap without producing an experiment. No human data, private benchmark data, paid model calls, new manuscript, or personality-to-society causal inference is part of this campaign.

## Current status

Six novelty screens complete: tracks 01, 05 and 06 stop for overlap; tracks 02, 03 and 04 proceed as bounded interaction diagnostics with worldwide novelty unestablished. Models and implementations are being frozen; no primary experiment has run.

## Execution and verification

Read [model boundaries](model.md), the [novelty matrix](novelty/index.md), and the [complete configuration bindings](registered-configs.json). `make dd024-readiness` reads files and hashes without evaluating a scientific cell. `make audit-dd024` runs small development fixtures and guardrail tests.

The three `make dd024-track02`, `make dd024-track03`, and `make dd024-track04` targets create primary evidence and are one-use within this campaign. The coordinator executes them from separate clean detached worktrees at the same frozen source commit. Do not rerun these merely to refresh timestamps. Existing outputs can be independently reconstructed with `python -m distributed_discovery.behavioral_diversity.study --track <track-id> --verify-existing <run-directory>`; this reads evidence without creating a primary run.
