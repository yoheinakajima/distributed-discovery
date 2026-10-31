# Track 02 implementation and freeze handoff

## Status

Prepared 2026-10-31. The coordinator admitted a bounded 18-cell interaction
audit after the saved novelty screen. Implementation and focused validation
are complete and ready for coordinator review; **no full primary grid has
run**. Source SHA, input hashes, immutable run ID, and clean-worktree
provenance belong to the later coordinator freeze.

## Owned interfaces

Module: `distributed_discovery.behavioral_diversity.robustness`.

- `run(config: dict[str, Any]) -> dict[str, Any]`: evaluates actual policies,
  returning JSON-safe rows, all plan vectors, saved choices, mixture/dual
  certificates, comparator values, and a summary.
- `verify(config: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]`:
  reconstructs probabilities by direct state enumeration, checks every
  declared deterministic plan and certificate, and requires four specified
  corruptions to be rejected.

The verification result has `passed`, `checks`, `errors`, and `corruptions`.
Each corruption boolean is true when its mutation was rejected. The runner
fields are `study_id="DD-024"`, `track_id="track-02"`,
`time_cap_seconds=120`, `memory_cap_mb=1024`, and
`random_seeds={"algorithm": [], "model": null}`. The nested resource-cap
record mirrors the same limits. Configuration validation accepts nonempty
subsets of the 18 cells for development tests; only the complete frozen
configuration is the primary study input.

The root runner owns process resource enforcement, manifests, checksums,
stdout/stderr preservation, immutable output storage, and source provenance.
These functions do not write files or claim to provide that provenance.

## Resource estimate before execution

Each cell uses 36 labeled role profiles. A binary diagnostic induces 1,296
contingent plans, and an absent diagnostic induces 36. The full 18-cell
configuration contains 15,768 contingent-plan payoff rows. Homogeneous
departure candidate counts are 5 or 25 per cell; heterogeneous counts are
25 or 625. The primary optimizer sorts two-dimensional payoff vectors and
uses a linear hull scan, rather than enumerating every pair of plans.

The independent path sums at most 216 joint source/diagnostic states per
regime/cell before evaluating role pairs, and checks a finite list of dual
inequalities. It builds its reference once, then reuses that independently
calculated reference to check corrupted output copies. Exact
integer/rational objects and JSON output should fit
comfortably under 1024 MiB; the 120-second hard cap remains mandatory. This
is an analytical estimate, not a runtime measurement or a guarantee.

## Validation record

Commands used for focused validation:

```bash
PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_behavioral_diversity_robustness.py
.venv/bin/mypy src/distributed_discovery/behavioral_diversity/robustness.py
.venv/bin/ruff check src/distributed_discovery/behavioral_diversity/robustness.py tests/unit/test_behavioral_diversity_robustness.py
.venv/bin/ruff format --check src/distributed_discovery/behavioral_diversity/robustness.py tests/unit/test_behavioral_diversity_robustness.py
```

The six focused tests passed in 0.65 seconds. They execute three individually selected
development cells, not the full Cartesian grid: a shared-private-source
two-success hand case; its perfect-diagnostic limit; and a noisy-diagnostic
one-success case with both source branches. They check a hand-derived
attaining mixture and dual bound, known-prior values, diagnostic-conditioned
plan coverage, independent departure candidate counts, source identities,
and JSON serialization. Separate tests corrupt a saved plan payoff and
remove a plan. A monkeypatch test makes the primary scientific helpers raise
if called by the verifier; verification still passes.

The initial plain pytest invocation failed during collection because the
virtual environment contained an installed package snapshot without the new
module. It performed no scientific evaluation. The source-qualified command
above resolved that environment mismatch. The root worker must likewise
import the frozen worktree source or install that frozen package.

The first lint check reported one conditional-style suggestion and one
overlong line; both were fixed. The mypy check passed with no issues.
Formatting was then applied only to the owned module and test file. The
final Ruff lint check passed, and the final format check reported both files
already formatted. A static JSON
check confirmed 18 unique cell specifications and matching runner cap/seed
fields; it did not evaluate policies.

Development validation is not an immutable primary result or a promoted
scientific claim. The full registered grid remains unexecuted until root
records the clean-source freeze and draft-PR gate. The primary worker must
call both APIs within its total 120-second and 1024-MiB process limits and
retain any failure rather than restarting the primary configuration.
