# ExecPlan contract

An ExecPlan is a living, self-contained implementation and research plan that lets a new researcher resume without prior conversation. Create or update one before substantial work. Record evidence and UTC timestamps; never rewrite history to hide failed approaches.

Every ExecPlan must contain:

1. Purpose and intended outcome
2. Current state
3. Scope
4. Non-goals
5. Assumptions
6. Milestones
7. Progress checklist
8. Discoveries and surprises
9. Decision log
10. Validation strategy
11. Commands and expected observations
12. Artifacts produced
13. Blockers
14. Recovery and restart instructions
15. Outcome and retrospective

## Discussion and Decision Delta Audit

Every substantive ExecPlan must include a section titled exactly
`DISCUSSION AND DECISION DELTA AUDIT` immediately after its live/current-state
section. Before issue or branch creation, the author must read
`docs/program-memory/registry.yml`, identify owner-adopted items not yet routed,
evidence-dependent items whose trigger occurred, and items superseded by
completed work; then route, defer, reject, or supersede every due item and
record the reconciliation in the plan. Chat is intake, not durable authority.

At issue closeout, repeat the audit, identify newly due items, update the
registry and canonical destinations, and state whether any owner decision
remains only in conversation. Raw chat transcripts, private conversation
links, and unclassified conversational content are not plan artifacts.

After every material discovery, decision, completed subtask, failed experiment, or changed approach, append an update and set exactly one active milestone. Include exact commands and observed outcomes, not merely intentions. Mark completion only when stated criteria pass. When blocked, identify the condition, preserved state, and next executable action.
