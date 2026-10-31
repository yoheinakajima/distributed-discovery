# Track 03 implementation and freeze handoff

Prepared 2026-10-31. The coordinator admitted this bounded failure-dependence
diagnostic after [the novelty screen](novelty.md). The scientific model and
80-cell configuration are in [model.md](model.md) and [config.json](config.json).
No full primary grid has run. The coordinator owns the clean-source freeze,
draft PR, immutable run ID, manifest, hashes, process limits, and output paths.

## Interfaces and saved evidence

Module: `distributed_discovery.behavioral_diversity.feedback`.

- `run(config: dict[str, Any]) -> dict[str, Any]` returns JSON-safe metadata,
  configuration, cell rows, and a summary. Rows preserve all seven policy
  values, their clue-indexed continuation tables, maximizing ties, all nine
  candidate rescue masses for each clue pair, detector-pattern probabilities,
  fallback reached mass, the disagreement stratum, and all four contrasts.
- `verify(config: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]`
  returns `passed`, `checks`, `errors`, and `corruptions`. A true corruption
  value means that the deliberately damaged output was rejected.

Every fraction is serialized as an explicit numerator/denominator string,
including `0/1` and `1/1`. Functions perform no filesystem writes. The supplied
registered primary configuration has 80 cells. Small subsets of its declared
parameters are accepted solely to support focused implementation fixtures;
they are not primary evidence and do not replace the frozen configuration.

## Separate evaluation routes

The primary route computes miss events from independent detector-group
partitions and checks the nine finite continuation pairs. The verifier uses
separately generated raw Bernoulli worlds, direct detection predicates, and
its own finite alternative checks. It additionally executes all four slots
of each saved policy, including after a first-round detection, to check the
attempt accounting and the precommitted control.

The verifier never calls `_groups`, `_miss`, `_pattern_weights`, `_weights`,
`_scores`, `_best`, `_primary_row`, or `run`. Its source-probability calculation
and detector construction are separate. Shared constants, validation,
fraction formatting, and summary formatting are explicitly disclosed;
these routes are computationally independent checks of the scientific values,
not independently authored software or a formal proof assistant certificate.

Four internal corruption fixtures alter a detector weight, the cross-searcher
revisit mapping, a saved calibrated value, and the four-attempt budget. They
are exercised on the first cell after full verification, so corruption checks
do not multiply the full-grid workload. Focused unit tests also corrupt a
candidate value and a summary count.

## Resource estimate before primary execution

There are at most 432 latent world labels per cell. Each cell has nine clue
pairs, nine candidate continuations, and seven saved policies. The primary
route uses a fixed small set of rational sums. The verifier constructs raw
tables for the true, iid-assumed, and perfect-detection laws, then directly
executes seven policies and checks target/searcher relabelings. It does not
enumerate arbitrary multi-round policy trees.

This bounded state count is expected to fit under 1024 MiB and the combined
120-second evaluation-and-verification cap. It is an analytical estimate,
not a full-grid runtime measurement. The root runner must enforce both caps
and preserve any breach without an automatic retry or claim promotion.

## Validation record

The five focused tests passed on 2026-10-31 (pytest reported 0.31 seconds).
They cover analytically computed perfect-clue values under all four laws, an
explicit cross-searcher rescue probability, perfect-detection law equivalence,
the precommitment control, saved-output corruption, and budget rejection.
Their small configurations collectively evaluate ten parameter cells; they
do not execute the frozen 80-cell grid or constitute primary evidence.

The first lint/type pass found a long metadata string and an imprecisely typed
Cartesian-product tuple. Both were corrected without changing the scientific
model. Final checks passed:

- `.venv/bin/ruff check src/distributed_discovery/behavioral_diversity/feedback.py tests/unit/test_behavioral_diversity_feedback.py`
- `.venv/bin/ruff format --check src/distributed_discovery/behavioral_diversity/feedback.py tests/unit/test_behavioral_diversity_feedback.py`
- `.venv/bin/mypy src/distributed_discovery/behavioral_diversity/feedback.py`

The focused test command was
`PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_behavioral_diversity_feedback.py -q`.
The full registered grid remains unexecuted until the coordinator records its
clean-source freeze.
