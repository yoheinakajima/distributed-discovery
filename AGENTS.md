# Distributed Discovery agent instructions

This repository develops **Distributed Discovery**: how organizations and multi-agent systems convert dispersed evidence into portfolios of search actions. The repository is public by explicit project-owner decision; the canonical paper and site remain read-only upstream at `yoheinakajima/shared-discovery-paradox`.

## Mandatory read order

1. This file.
2. `.agent/PLANS.md`.
3. `plans/MASTER_EXEC_PLAN.md`.
4. `docs/repository-contract.md`.
5. The nearest study `README.md`, `plan.md`, and `status.yml`.

Use a living ExecPlan for substantial work. Execute registered milestones sequentially unless a hard blocker is recorded. Every research output must name a study ID; every generated numerical claim must trace to immutable run IDs.

## Non-negotiable rules

- Never invent results, proofs, citations, metadata, certificates, novelty, exactness, or completion.
- Label definitions, identities, sourced upstream results, proofs, exact computations, reproductions, observations, Monte Carlo estimates, conjectures, questions, hypotheses, and negative results accurately.
- Use “exact” and “optimal” only with the evidence allowed by `docs/claim-status-policy.md`.
- Preserve null, negative, and failed results. Keep source data for displayed numbers.
- Follow `docs/reproducibility.md`: pin inputs, record Git state, commands, versions, hashes, seeds, outputs, validation, and UTC timestamps. Never overwrite runs.
- Validate claim records against `claims/schema.json`; promotion requires evidence and checks.
- Add hand-checkable tests, invariance/normalization/bound tests, and regressions proportional to each change. Run the relevant Make targets before commit.
- Update the active ExecPlan, claim ledger, study status, result index, and documentation with material findings or decisions.
- Make small milestone commits on task branches. Do not force-push, rewrite shared history, commit secrets, deploy outside the authorized Pages workflow, or modify/push to canonical upstream. Releases and DOI publication require explicit future approval.

Detailed policies live in `docs/`; do not duplicate them here.
