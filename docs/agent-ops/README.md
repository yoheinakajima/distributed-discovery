# Agent Operations v1

Agent Operations is the workflow authority layer for Distributed Discovery.
It makes prompts small by keeping stable rules and live task state in the
repository. It does not create scientific authority.

## Authority layers

Highest applicable authority wins; lower layers may narrow but never broaden
it.

1. Project-owner decisions and repository-wide `AGENTS.md`.
2. Scientific, reproducibility, publication, release, private-data, and
   repository policies.
3. Scoped `AGENTS.md` files for the directories a task touches.
4. The committed task contract: fixed authority for one task.
5. The living ExecPlan: mutable execution state, evidence, failures, and
   restart instructions.
6. GitHub issue and pull request: coordination, review, and observed external
   state.
7. A committed owner-gate manifest plus a valid local authorization: temporary
   permission for the exact declared consequential action.
8. Generated context, prompts, and handoffs: disposable views, never authority.
9. Chat: intake and task-specific delta only.

The existing scientific authority hierarchy is unchanged. Agent Operations
cannot allocate or promote studies, claims, runs, proofs, evidence, paper
lifecycles, citations, or external-service state.
Workflow metadata cannot create scientific truth.

## Task lifecycle

1. Reconcile program memory and record the discussion/decision delta audit.
2. Register one issue, one task contract, one ExecPlan, and one task branch.
3. Validate the contract against its task type and acceptance profile.
4. Render live context and a thin bootstrap; continue from the first incomplete
   ExecPlan milestone.
5. Open one draft pull request after the contract/schema skeleton and focused
   tests exist.
6. At a consequential boundary, commit a gate manifest, freeze the exact
   commit, and obtain a local owner authorization.
7. Validate with the acceptance profile and produce a typed checkpoint or
   completion handoff.
8. Merge, verify external observations, repeat the decision-delta audit, close
   the issue, and synchronize `main`.

One active substantive lane remains the default. A new substantive issue uses
a new task thread; continuation within one issue resumes the same task thread
when available.

## Prompt as delta

A prompt states only the new objective, new owner decisions, truly frozen
identifiers, and the task contract or candidate delta path. Stable policy is
read from root and scoped instructions. Dynamic GitHub, Git, budget, due-item,
and validation state is rendered at execution time. Full prior prompts and raw
chat transcripts are not copied into Git.

The normal generated bootstrap is capped at 120 lines and 12 KiB. A resume
message is capped at 30 lines. If a task needs more, move durable content into
the contract, ExecPlan, ADR, or policy rather than expanding the prompt.

## Task contract and ExecPlan

The task contract fixes objective, authority references, owner decisions,
scope, non-goals, permissions, budgets, expected outcomes, stop conditions,
acceptance profile, canonical destinations, GitHub assignment, ExecPlan,
supersession, and next gate. Permission values default false.

The ExecPlan records changing facts: milestones, timestamps, observations,
failed checks, discoveries, decisions, validation results, blockers, recovery,
and outcome. A changed observation never requires a contract edit.

After the first contract commit, authority-bearing edits require an explicit
owner decision. This includes broader scope, a newly true permission, a higher
cap, weaker stop condition, scientific/private/external authority, a different
task type, or a different intended outcome. Make those changes in a new
contract that names the prior contract under `supersession`; do not rewrite the
old contract. Typographical or path-only repairs that cannot broaden authority
may use an additive corrected contract version with a recorded rationale.

Issue/PR numbers discovered after registration are observations and belong in
generated context or handoffs unless they were already frozen in the contract.

## Owner gates

A task profile can require a gate but cannot authorize it. A committed gate
manifest declares the complete surface: issue/PR, branch, frozen execution commit, tree and
contract hashes, purpose, irreversible/private/external actions, cumulative
spend, remaining caps, prohibitions, expiry, authorization path, next
milestone, and resume message.

Because a tracked manifest cannot contain the SHA of its own commit, `commit`
and `pull_request.head_sha` name the exact execution commit immediately before
the manifest commit. The engine verifies that execution commit is an ancestor
of the clean local, remote, and live pull-request head and that every declared
execution-sensitive tree still has the frozen hash. It also verifies branch,
pull-request state, permissions, caps, prohibitions, expiry, and challenge.
It then writes a mode-`0600` authorization outside Git and preserves a
superseded local authorization in local history. It never performs the gated
action. Authorization is exact, expiring, nontransferable, and fails closed.

## Handoffs

Every checkpoint and completion uses the handoff schema. The machine-readable
record carries status, repository, task/issue/PR/branch/base/head identifiers,
contract and ExecPlan, completed/next gates, decision, external/private/
scientific changes, validation, owner action, exact next command/file, and
blocker. Human rendering normally stays under 50 lines.

The five statuses are `complete`, `owner-gate-required`,
`legitimate-checkpoint`, `stop-by-policy`, and `inconsistent-state`.

## Acceptance profiles

Acceptance profiles name reusable Make targets and invariant classes. They do
not duplicate command walls in prompts and do not reduce checks already
required by repository policy. Task-type profiles select a default acceptance
profile and required checkpoint classes; the task contract makes the final
selection.

## Instruction bounds

Root `AGENTS.md` must remain at or below 8 KiB. Each scoped `AGENTS.md` must
remain at or below 6 KiB. The common loaded chain—root plus every unique scoped
instruction selected by a task—must remain at or below 32 KiB. Agent Operations
audits byte counts and refuses copied governance walls or instructions to
start another Codex session.

## Migration policy

Migration is prospective. Historical prompts, issues, plans, authorizations,
and closeouts remain unchanged. A current roadmap decision becomes a task
delta; registration converts it into a new task contract, ExecPlan, issue, and
branch. Switching director chats or resuming a task reconstructs state from
Git/GitHub rather than pasted output. See
[`migration.md`](migration.md) for the operating procedure.

## Private and scientific boundaries

Generated context must not read secrets, owner authorizations, retained private
state, or credentials. A task requiring private access names only a symbolic
path until a valid gate authorizes exact access. Private outputs stay outside
Git unless a separate policy explicitly permits a redacted artifact.

Workflow metadata is not evidence. A profile, task contract, issue, gate,
authorization, prompt, or handoff cannot make a scientific proposition true.
Scientific mutation requires the existing registration, immutable-run,
verification, claim, proof, and paper-governance systems in addition to any
Agent Operations workflow gate.
