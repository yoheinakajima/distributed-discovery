---
name: verify-claim
description: Audit one Distributed Discovery claim against its sources, proof, code, runs, and tests. Use when checking evidence, considering status promotion, or recording a failed verification.
---

# Verify a claim

1. Read `docs/claim-status-policy.md`, then locate the claim in `claims/claims.yml`.
2. Follow every declared source, proof, implementation, run, dependency, and test path; fail on missing evidence.
3. Re-run the evidence-specific checks and confirm manifests/configs/hashes make the result reproducible.
4. Match terminology to evidence: computation is not proof; heuristic is a lower bound; Monte Carlo is not exact; upstream execution is not independent reproduction.
5. Write a dated validation record under `claims/checks/`, including failures and commands.
6. Update `status` and `last_checked` only when the policy requirements are met. Preserve refuted/superseded history.
7. Run `make validate-claims` and relevant tests, then update the ExecPlan and affected report/index.

Never convert a conjecture into a theorem based only on computation or a failed counterexample search.
