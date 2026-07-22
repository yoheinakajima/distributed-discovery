# DD-015 execution plan

## Purpose and intended outcome

Determine exactly when visible prior actions make later searchers follow a
public-looking action or lean away from it, and separate autonomous Bayesian
choice from a dynamic common-payoff planner under fixed-budget and
stopping-on-success objectives.

## Current state

Program V4's roadmap reconciliation merged through PR #109 as `6cd7190` and
passed post-merge CI `29890818431` and Pages `29890818405`. Issue #110 and
branch `research/dd015-dynamic-attention` are active. No DD-015 run or claim
exists.

## Scope

- three uniform targets;
- two or three sequential agents;
- a conditionally independent shared clue of accuracy `q` and private clues of
  accuracy `p`, with wrong labels uniform;
- all agents observe the shared clue and their own private clue;
- fixed budget: prior actions are visible but outcomes are hidden until the end;
- stopping: continuation reveals that every prior action failed;
- autonomous agents receive full duplicate credit and choose a posterior mode;
- the common-payoff planner selects a private-clue prescription at each public
  history to maximize union discovery, with lexicographic exact tie-breaking.

## Non-goals

No equal-split congestion reward, mixed or signaling equilibrium, action cost,
communication, hidden source dependence, unreliable execution, human behavior,
or general theorem is claimed. Threshold-two search is a separate extension
gate after this baseline.

## Assumptions

The shared and private clues are independent conditional on the target. The
autonomous full-credit rule is a pure sequential Bayesian equilibrium because
an agent's payoff is exactly the probability its own action is correct and is
not diluted by later actions. Off-path beliefs are unnecessary for reached
histories in the bounded exact evaluator.

## Milestones

1. Freeze model, accuracy grid, state counts, resource caps, and exactness plan.
2. Implement posterior filtering, autonomous equilibrium, and common-information
   planner DP.
3. Implement a materially separate labeled policy-tree verifier and corruption
   gates.
4. Pass targeted and repository validation; commit the frozen source.
5. Execute one clean immutable primary run and audit claims separately.
6. Add the separately labeled threshold-two extension only after baseline
   agreement is established. **Active after the passing baseline run.**
7. Integrate report, public-safe data, study page, CI, Pages, and live routes.

## Progress checklist

- [x] Roadmap predecessor merged and deployed.
- [x] Issue and branch created.
- [x] Original model and resource boundary frozen.
- [x] Exact implementation and independent verifier pass.
- [ ] Clean source commit and immutable primary run pass.
- [ ] Claims and documentation are audited.
- [x] Baseline claims and documentation are audited.
- [x] Separately labeled threshold-two planner extension passes.
- [ ] Repository/site acceptance, merge, CI, Pages, and live routes pass.

## Discoveries and surprises

- The first preview was stopped before completion because the exact planner
  recomputed identical common-information states. No output or run directory
  was created. State memoization is required to meet the registered estimate.
- A direct one-file pytest command omitted the repository `PYTHONPATH` and
  failed at import collection; Make-based validation retains the correct path.
- The memoized non-evidence preview completes within the estimate and agrees
  with 128 direct policy-tree checks. Its regression targets are 38 rows with a
  strict planner gain, 18 fixed-budget rows where visibility reduces both
  discovery and dispersion relative to history-hidden Bayes choice, no row
  where it raises either, 32 stopping rows with fewer expected actions, and
  positive instances of both following and leaning against. These are not
  research results until the clean immutable run and claim audit pass.
- The first full verification stopped at Ruff UP033 because the memoization
  decorator used `lru_cache(maxsize=None)` rather than the equivalent preferred
  `cache` spelling. No scientific check ran before that stop; the style-only
  failure is retained here.
- After the Ruff correction, MyPy stopped on fixed-length prescription and
  policy-object narrowing. These are static typing defects only; explicit casts
  preserve the already checked runtime objects and model.
- After typing passed, the first full test run reached 197 passes and one site
  metadata failure: `active-registered-baseline` is not a public phase enum.
  DD-015 now uses the existing `active-extension` public label while its study
  status retains the more precise frozen-baseline state.

## Decision log

- Use full duplicate credit for the autonomous baseline. This yields a declared
  sequential Bayesian equilibrium and keeps action-information effects separate
  from DD-012/DD-017 reward congestion.
- Treat fixed-budget outcome feedback and stopping feedback separately. Visible
  action is evidence about a prior private clue; stopping continuation adds the
  logically distinct event that the action was wrong.

## Validation strategy

Check exact probability normalization, label-permutation invariance, hidden-
action and direct-policy controls, planner weak dominance, fixed/stopping scope,
and hand cases at uninformative and perfect boundaries. Recompute every policy
by direct enumeration over target, shared clue, and labeled private-clue paths.
Reject altered posterior normalization, action, planner value, and objective
labels.

## Commands and expected observations

- `make dd015-preview`: bounded non-evidence summary with method agreement.
- `make verify`: formatting, types, all tests, claims, and manifests pass.
- `make dd015-dynamic`: only from the clean frozen commit; creates one new
  immutable run and refuses a dirty tree.

## Artifacts produced

Planned: frozen config, model, evaluator, verifier, corruption record, primary
run, report, claim checks, public-safe summary/profile table, and study route.

## Blockers

None. GitHub CLI is unauthenticated; the connected GitHub integration and SSH
are available for ordinary issue/PR work. Settings issue #32 is unrelated.

## Recovery and restart instructions

Inspect `git status --short --branch`, this plan, and `configs/baseline.yml`.
Before the primary run, the exact next command is `make dd015-preview`. Never
run the primary target from a dirty tree and never overwrite a run directory.

## Outcome and retrospective

Pending. Completion requires a merged evidence package, passing post-merge CI
and Pages, and live route/data verification.

Pre-run acceptance passed bootstrap, Ruff, MyPy on 125 source files, all 198
tests, the unchanged 78-claim ledger and 42 manifests, and a 61-page/21-study
site build. The next action is the clean source commit and draft PR; only then
may the one primary configuration execute.

The primary baseline run and DD-C-0079 through DD-C-0081 now pass. The separate
threshold-two extension registers 16 parameter cells, 32 objective rows, 3,888
unique labeled paths, and a planner-only policy audit over starting a singleton,
joining a singleton, joining a viable team, and following/opposing the shared
clue. It makes no decentralized implementation claim and will use a distinct
secondary immutable run rather than repeating the baseline.

The first extension-wide verification stopped at MyPy because a list-to-tuple
conversion needed an explicit fixed-length occupancy cast. Unit behavior and
the preview had passed; the static-only defect is retained and corrected without
changing the registered extension.

After the cast correction, extension pre-run acceptance passed Ruff, MyPy on
126 source files, all 200 tests, 81 validated claims, and all 43 existing
manifests. The exact next action is to commit the baseline evidence and frozen
extension source, then execute the distinct extension configuration once from
that clean commit.

The separately labeled extension run
`20260722T044453Z_DD-015_34bc4379_33e1da478b` passed in 13.842954 seconds.
DD-C-0082 passed its separate audit. The active gate is full repository/site
acceptance, evidence commit, PR CI, merge, post-merge CI/Pages, and live routes.
