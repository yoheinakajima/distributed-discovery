# Task generator contract

Generator `agents-task-generator-v1` is deterministic given a complete public
or future private generator manifest. It consumes only registered finite
parameter cells and emits a primitive task instance, an agent-visible
capability view, an evaluator-only answer object, and cryptographic
commitments.

The registered public domain has 138 canonical parameter cells and 58,945
primitive labeled task-state evaluations. One canonical user prompt exists per
cell. The permitted isomorphism set has four variants per cell—identity or one
fixed nontrivial target relabeling crossed with identity or one fixed
nontrivial agent relabeling—so the frozen prompt space has 552 isomorphic
surface forms. These are design counts, not generated private instances.

Generator rules:

1. validate the registry and selected cell;
2. canonicalize rational inputs and stable JSON ordering;
3. apply only declared target and agent isomorphisms;
4. render `agents-prompt-v1` without benchmark-specific cues;
5. construct separate agent-visible and evaluator-only objects;
6. reject any leaked expected value, source identity, claim/run reference,
   answer, generator-internal field, or undeclared private signal;
7. hash primitive canonical JSON before rendering;
8. never use network access or provider code.

Public fixtures use explicit `PUBLIC-TOY-*` identifiers and fixed public toy
inputs. A later private generator must be authorized separately and use the
custody sequence; this registration creates no private seed or instance.
