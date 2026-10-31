# Track 04 implementation and validation record

## Scope and public API

The scientific implementation is
`src/distributed_discovery/behavioral_diversity/timing.py`.
The public functions are `run(config: dict[str, Any]) -> dict[str, Any]`
and `verify(config, result) -> dict[str, Any]`. They return JSON-safe data;
all exact probabilities and contrasts use `numerator/denominator` strings.
The coordinator owns primary execution, manifests, output persistence,
repository-wide integration, and the clean-source/config freeze.

The source-law grid has 36 cells, at most `M^4=625` labeled worlds per cell,
and at most two exact timing-coin branches per world. Eight schedules and
two receiver rules produce 576 base rows. All per-agent budgets are held
fixed. Complete saved receiver policies include second decisions after
every candidate first action. Event-policy emulations supply 144 additional
saved policies and comparisons; they do not consume additional primary
sub-runs.

## Algorithm and independence

Primary probability construction uses unreduced common integer channel
masses. Only exported values are converted to reduced fractions. The
coverage optimizer evaluates at most `M` first actions and `M` second
actions per positive world/information partition, giving a conservative
`O(cells * schedules * receivers * M^6)` arithmetic-operation bound.
The maximum M is five; no unrestricted policy-tree enumeration is needed.

The verifier independently constructs raw probabilities as products of
Fractions, converts those probabilities to a common integer denominator,
and evaluates saved decisions. It separately checks all local deviations;
it never invokes the primary backward-induction solver or primary
observation/world functions. Its additional action-deviation work has the
same bounded polynomial scale. Corruption tests extract one complete cell,
first validate that unmodified fixture, and send five separately damaged
copies through the actual verifier. Only recursive corruption testing is
disabled inside those fixture validations; probability reconstruction,
history accounting, policy execution, and all other applicable checks stay
enabled. This avoids five repeated full-grid computations.

## Before primary execution

The novelty screen preceded this model/configuration and implementation.
The model and prospective grid were recorded before the first scientific
implementation. Only focused single-cell unit checks may run before the
coordinator freezes the full source and configuration. The 36-cell primary
has not been executed by the implementation agent.

## Focused checks completed before primary

- `PYTHONPATH=src .venv/bin/pytest tests/unit/test_behavioral_diversity_timing.py -q`
  passed: **10 tests in 0.44 seconds**. Only two separate one-cell fixtures
  were evaluated: `(M=5,p=q=chance)` and `(M=3,p=1/2,q=3/4)`.
- `.venv/bin/ruff check src/distributed_discovery/behavioral_diversity/timing.py tests/unit/test_behavioral_diversity_timing.py`
  passed.
- `.venv/bin/mypy src/distributed_discovery/behavioral_diversity/timing.py`
  passed after correcting two tuple type annotations. These corrections did
  not change the scientific model or grid.

The no-information test has an independent analytic answer: A covers labels
zero and one, MAP B duplicates them, and coverage-aware B selects labels two
and three. The respective values are `2/5` and `4/5` for every schedule.
This is an implementation control, not a new campaign finding. Other tests
check the exact timing match, informative silence, emulation, and local
optimality; corruptions of the stored channel, probabilities, payoff, or
policy are rejected by the full verifier. A monkeypatch test makes every
primary probability/observation/optimization routine raise if called, then
successfully runs the verifier on the saved small result.

An initial direct pytest invocation could not import the new source module
because the local environment contains an older installed package copy.
Using `PYTHONPATH=src` resolves the source path explicitly. No package files,
dependency versions, or shared build configuration were changed by this
implementation agent.

The largest-support single-cell fixture includes all 625 source worlds and
both branches of the independent timing coin. Its small-test completion is
consistent with the proposed cap; the full primary has not been timed or
executed. The coordinator's shared 120-second limit must cover both `run`
and `verify`, and remains the authoritative stopping condition. No new
claim or scientific-result status follows from these implementation checks.

## Peer-review refinement before source freeze

The internal track-04 review found that the original built-in corruption
booleans tested equality predicates rather than routing altered artifacts
through the substantive audit. The separate unit tests did use the full
verifier, but that did not make the built-in primary verification controls
equivalent. The implementation was strengthened before any primary run.

The public `verify(config, result)` now calls a shared private audit path.
It validates the real result, extracts its first complete source-law cell,
and checks that the unmodified fixture passes the same path. Each registered
corruption then independently changes a trigger, arrival probability,
silence likelihood, payload alphabet, or saved payoff. Rejection counts
only when that actual audit fails for the relevant channel/value reason.
No primary optimizer is invoked and no new numerical experiment is run.

A new regression test disables the channel validator. The public verifier
then correctly fails because all four channel corruptions go undetected;
the saved-value corruption remains rejected. This tests that the built-in
negative controls depend on the functioning validation path rather than
merely on inequality of a copied scalar.

After the refinement, the same focused command passed **11 tests in
0.86 seconds**. Ruff and strict mypy also passed. Only the original two
single-cell fixture configurations were used. The scientific model,
prospective 36-cell grid, policy classes, estimands, 120-second/1024-MiB caps,
and public function signatures were unchanged. The full primary remains
unexecuted by the implementation agent.

The peer review's separate label-check qualification still applies. Source
probabilities are checked under cyclic relabeling; the saved-action check
then shifts selected actions and target together and preserves the sender
success indicator. This exercises the success-event conjugation identity,
not a new optimization on relabeled observations or an independent execution
of transformed tie-priority logic. Reporting must retain that narrow scope.
