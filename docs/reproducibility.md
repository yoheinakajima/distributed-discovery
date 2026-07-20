# Reproducibility policy

## Run identity

Use `YYYYMMDDTHHMMSSZ_<study-id>_<short-git-sha>_<config-hash>`. Never overwrite a run. A run records manifest, config, exact command, reproducer, environment, dependency-lock hash, input hashes, separate random seeds, stdout, stderr, metrics, validation, checksums, and a README where applicable.

The manifest records clean/dirty Git state, commit, OS/architecture, Python and relevant packages, UTC start/end, exit status, study ID, config hash, relevant upstream commit, outputs/hashes, and validation state.

## Determinism and randomness

Prefer deterministic exact evaluation when feasible. Serialize with stable key ordering. For randomized work, require explicit multiple seeds where relevant, separate search randomness from simulated-model randomness, state estimators and uncertainty, and preserve each attempt.

## Computation guardrails

Estimate policy/state space and resource cost before large runs. Configure time and memory bounds, checkpoint long searches, retain partial certified bounds, and record termination reason. Heuristics store policies, receive exact evaluation where feasible, run multiple seeds, and are labeled lower bounds.

## Storage

Commit compact source, configs, manifests, important logs, proofs, final tables, and figures. Ignore caches, environments, clones, and rebuildable intermediates. Do not silently omit metadata needed for large outputs. Any artifact over 10 MB follows ADR-0008.
