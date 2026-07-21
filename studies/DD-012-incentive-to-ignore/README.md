# DD-012 — Incentive to Ignore

Completed bounded Program V3 study of how many agents should receive and follow one shared
clue in an equal-split discovery game. The model, rational grid, reward
registry, proof, exact evaluator, separate labeled-state verifier, and compute
guardrails are frozen. The clean immutable run and claim audit passed; see
`report.md` and `results/README.md`.

The central access interpretation is ex-ante non-delivery: an ignoring role
does not receive the shared clue. The study does not assume an agent can forget
an already observed signal.

The primary run must not be repeated merely to refresh a timestamp. Reproduction
entry point: `make dd012-attention` from a new clean commit under a separately
registered run.
