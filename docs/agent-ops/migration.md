# Agent Operations migration

Migration is prospective. Existing prompts, issues, branches, plans,
authorizations, reports, and closeouts remain historical evidence and are not
rewritten into the new formats.

## From roadmap decision to task delta

1. Verify the roadmap decision and its source records against live Git/GitHub.
2. Reconcile `docs/program-memory/registry.yml`.
3. Write a small `task-delta` containing only the new objective, adopted owner
   decisions, permissions (false unless explicit), expected outcomes,
   non-goals, frozen identifiers, and exact next gate.
4. If selected, register a new issue, task contract, ExecPlan, and task branch.
5. Render context and the bootstrap from the committed contract.

A candidate delta is not registration or execution authority.

## Checkpoints

Use a typed handoff whenever work stops at an owner gate, legitimate milestone,
policy stop, inconsistency, or completion. The handoff states the exact next
command and file. A checkpoint does not weaken unfinished acceptance criteria.

## Switching the director chat

A replacement director reads the director contract, live repository state,
active task contract, ExecPlan, issue/PR, gate manifest, and latest handoff. It
verifies pasted output rather than trusting it. Chat carries only current
intake and the newly selected delta.

## Resuming a task

Within one issue, resume the existing task thread when available. Read root and
scoped instructions, the same task contract, ExecPlan, pull request, current
gate manifest, and latest handoff. Continue from the first incomplete
milestone. Do not create a second task or substantive lane for a normal resume.

## Superseding a contract or gate

Never rewrite an authority-bearing contract change in place. Create a new
contract that names the old one and records the owner decision. Scope
expansion, newly true permissions, higher caps, weaker stops, new external or
private actions, and changed scientific authority always require
supersession.

A later gate manifest supersedes an earlier gate at a new exact commit. The
engine preserves the prior local authorization in mode-`0600` history. Expired,
revoked, changed, synthetic, or mismatched authorizations do not transfer.

## Extended task types

- Scientific registration adds model, resource, independent verification,
  corruption, stopping, and identifier gates but no execution.
- Scientific execution adds clean-source, immutable-run, claim-audit, and
  evidence gates.
- Private evaluation adds custody, exact private path, provider/call/cost caps,
  redaction, and output-lock gates.
- Release/external publication adds deterministic offline candidate,
  licensing, exact owner authorization, and post-action identifier checks.

Profiles only name defaults. The task contract and exact owner gate must
authorize every action.

## Chat versus Git

Chat contains intake, questions, and the smallest new delta. Git contains
instructions, contracts, ExecPlans, ADRs, program memory, policies, manifests,
handoffs intended as durable records, and closeout evidence. GitHub contains
coordination and directly observed issue/PR/check state. Generated build
context remains ignored and disposable.
