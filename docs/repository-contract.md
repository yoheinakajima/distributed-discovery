# Repository contract

## Authority and read order

`AGENTS.md` is the concise instruction index. `.agent/PLANS.md` defines planning. `plans/MASTER_EXEC_PLAN.md` records live state. This contract supplies detailed operating rules. Study files narrow, but may not weaken, these rules.

## Research outputs

Every output names one study ID (`DD-000`–`DD-007`). Generated numerical claims cite immutable run IDs. Public-facing sources may hide internal IDs only if nearby source comments or metadata retain them. Source-of-truth data generates every displayed number.

Claims use `claims/claims.yml`, conform to `claims/schema.json`, and follow `docs/claim-status-policy.md`. Definitions, identities, sourced results, proofs, exact computations, reproductions, observations, Monte Carlo estimates, conjectures, questions, hypotheses, and negative results remain distinct.

## Execution and documentation

Substantial work uses an ExecPlan. Update the master plan, study status, results index, and claims after material discoveries, decisions, failed experiments, or approach changes. Preserve failure logs and partial certified bounds. All meaningful documentation directories have an index or README.

## Validation

Tests must include relevant hand-checkable cases, normalization and bounds, invariance, regression, parser, manifest, schema, paper, site, and link checks. No Make target may report success without performing its named check. Long studies remain separated from routine CI.

## Safety and Git

This repository is public and project-authored content uses the root MIT License by explicit project-owner decision recorded on 2026-07-20. GitHub Pages deployment from generated `site/dist` artifacts is authorized only through the workflow on `main`. Never expose local paths or secrets, commit credentials, force-push, rewrite shared history, or modify/push canonical upstream. Fetch upstream into ignored cache and prepare changes as patches or fragments. Inspect dirty state before edits; preserve unrelated work. Commit coherent, passing milestone states on task branches.

## Time and artifacts

Use UTC machine timestamps. Commit compact source, configs, manifests, logs, proofs, tables, and final figures. Ignore environments, caches, clones, and rebuildable intermediates. Artifacts over 10 MB require an ADR and a recoverable storage decision.
