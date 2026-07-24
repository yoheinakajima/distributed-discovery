# Conversation-to-repository protocol

Chat is an intake surface, not program memory. A proposition becomes durable
only after it is distilled, classified, assigned a status, routed to an
authoritative repository destination, and committed to Git. Raw transcripts,
chat URLs, private conversational detail, credentials, and full prompt text are
not committed by default.

## Capture workflow

1. Distill the proposition and rationale without conversational framing.
2. Assign one capture classification:
   `capture-now`, `queue-after-active-pr`, `evidence-dependent`,
   `already-canonical`, `superseded`, or `do-not-canonicalize`.
3. Assign one durable status:
   `captured-unreviewed`, `candidate`, `owner-adopted`, `routed`,
   `evidence-dependent`, `deferred`, `rejected`, `superseded`, `implemented`,
   `closed-by-overlap`, or `closed-by-null`.
4. Record dependencies, promotion/review trigger, permitted stops,
   not-a-result boundaries, supersession, visibility, and owner decision.
5. Route the item to a policy, decision, ADR, ExecPlan, roadmap, lifecycle
   registry, release record, or other authoritative destination.
6. Commit the registry update and its destination together when routing is new.

Every `owner-adopted` item has a canonical destination. Every `superseded` item
names its replacement. `evidence-dependent` items retain the exact event that
will make them due. The registry routes authority; it does not replace the
claim ledger, study records, proofs, run manifests, ADRs, plans, papers, or
publication metadata.

## Evidence and authority boundaries

Program-memory records are governance metadata, never scientific evidence.
They cannot create or promote a study, claim, theorem, proof, exact result,
estimate, citation, provider result, publication state, or external-service
state. Scientific propositions link to existing study and claim IDs at their
canonical destination.

Owner decisions may be recorded as adopted policy. Suggestions, hypotheses,
questions, and evidence-dependent options remain labeled as such. An external
service state is recorded only after direct verification.

## Visibility

`public` records contain policy already suitable for public repository
governance. `internal` records may contain publication sequencing, parked venue
options, or decision frameworks but never secrets or private transcripts.
`restricted-reference-only` is permitted only to say that a separate
untracked/private artifact exists; the registry stores no path, content, or
access token for it.

## Supersession and review

Supersession preserves the old proposition, replacement ID/path, reason, and
review date. It does not erase history. Evidence-dependent and deferred records
must identify an event or date for review. Valid stops include rejection,
overlap, bounded null, continued deferral, or implementation when those
outcomes were declared in advance.

## ExecPlan and closeout delta audit

Every substantive ExecPlan begins with the exact
`DISCUSSION AND DECISION DELTA AUDIT` required by `.agent/PLANS.md`. The audit
reads the registry before issue/branch creation, reconciles every due item, and
records the result. Issue closeout repeats the audit and routes newly due
items. A future owner brief or megaprompt must provide a delta against the
registry instead of assuming the conversation is canonical.

The machine-readable companion is
`docs/governance/conversation-to-repository-protocol.yml`.
