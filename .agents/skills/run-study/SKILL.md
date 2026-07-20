---
name: run-study
description: Run or resume a registered Distributed Discovery study with immutable provenance. Use for executing study configurations, resuming bounded searches, or recording reproducible research runs in this repository.
---

# Run a registered study

1. Read `AGENTS.md`, the active ExecPlan, and the study `README.md`, `plan.md`, and `status.yml`.
2. Validate the configuration and estimate time, memory, state, and policy-space cost before large work.
3. Inspect `git status` and record commit SHA plus dirty state; never discard unrelated changes.
4. Generate `YYYYMMDDTHHMMSSZ_<study-id>_<short-sha>_<config-hash>` using UTC and deterministic config serialization. Never overwrite a run.
5. Record command, configuration, dependency-lock/input hashes, versions, upstream commit if relevant, and separate algorithm/model seeds.
6. Execute within configured resource bounds; preserve checkpoints and termination reason.
7. Save stdout, stderr, metrics, environment, output checksums, and validation in the run directory.
8. Re-run required tiny/invariance/normalization/bound checks and update the study and global result indexes.
9. Update the ExecPlan and study status. Do not promote claims automatically; use `$verify-claim` separately.

On failure, retain the manifest/logs when useful, label the run failed, and record the next executable action.
