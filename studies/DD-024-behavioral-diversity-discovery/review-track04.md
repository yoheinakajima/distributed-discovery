# Independent pre-freeze review of track 04

## Disposition and review scope

Reviewed 2026-10-31 by the track-02 implementation agent, independently of
the track-04 author. **No blocking scientific error was found in the declared
finite model, information accounting, policy optimization, or independent
payoff verification.** The two qualifications below concern the strength
of supplementary audit labels, not an identified wrong policy value.

This was a read-only source/model/configuration/test review. No primary
grid, supplementary parameter grid, or developmental numerical fixture was
executed by this reviewer. No track-04 code was edited. The implementation
record reports ten passing focused tests; this reviewer inspected those
tests and their assertions without claiming to have rerun them.

Reviewed files and SHA-256 identities:

| File | SHA-256 |
| --- | --- |
| `src/distributed_discovery/behavioral_diversity/timing.py` | `58a19b5f5973ad4c0b92acfff254c8e847e256593bf1f983f6aea93a31f73036` |
| `studies/DD-024-behavioral-diversity-discovery/tracks/track-04/model.md` | `0d332ca56f16bc10abced722ec8a940c94e4711c64a761db2f4e0bc158fcdadb` |
| `studies/DD-024-behavioral-diversity-discovery/tracks/track-04/config.json` | `78e596b79fe785755e06ae380297e682a613499de03c186a932229b3967cc7b4` |
| `tests/unit/test_behavioral_diversity_timing.py` | `7de29f7b33c45d9ccf68ad726ea47e2fc4c11680dff965fcc8b7ee60fa4d9a57` |

These hashes identify this review target, not a clean committed primary
source freeze. Root owns that later gate.

## Information and silence accounting

The primary source law gives A independent clues `X,Z` and B clue `Y`, all
conditionally independent given the target, with the advertised `p,q,p`
accuracies. The agreement probability used to yoke arrival rates is
`p*q + (1-p)*(1-q)/(M-1)`. The primary integrates the yoked coin independently
of all source variables. The verifier obtains agreement by summing raw
world probabilities instead of trusting that formula.

`_first_observation` correctly withholds `X` on late branches. Event timing
reveals the agreement bit even when no packet arrives; the primary records
that bit, and `_independent_worlds` reconstructs it from observed arrival
and the known trigger rule. The verifier therefore does not treat the bit
as a free direct observation of hidden `Z`. Yoked silence reveals no such
bit. Late augmented delivery also withholds the bit until the second action.

The second-history key preserves the initial information, delivered payload,
the receiver's own first action, and its own detection outcome. For each
registered protocol, a second-history key identifies its preceding first
information set, so the optimizer's continuation table does not improperly
merge histories with different remembered observations. Neither history
key includes A's action, A's success, or the hidden target.

The channel record separates packet count, payload alphabet, complete
transcript alphabet, observed arrival rate, and first-history target masses.
This is essential: matching event and yoked packet/arrival counts does not
match the information conveyed by the event bit. The code and model make
that distinction explicit.

## Allocation and feedback budgets

Both agents have exactly two action opportunities in every treatment. A's
policy and observations are fixed across receiver classes and schedules.
A uses its posterior mode, then its next-best remaining target following
failure; following success it takes the declared default action. B similarly
uses the default second action after its own success. Continuing these
otherwise redundant actions is consistent with the terminal union objective
and the absence of an action-cost or discovery-speed objective.

The primary's A-coverage indicator is equivalent to execution of A's two
own-feedback branches: a hit on the first action already guarantees union
success, and otherwise the second ranked target is searched. The verifier
independently executes the actual success/failure branch when constructing
its sender-hit indicator. This equivalence does not silently grant B an
observation of that indicator.

There are three clues, four inspections, and one packet throughout. The
augmented packet has a larger payload alphabet than the plain packet; the
comparison is justified by its matching complete event transcript, not by
pretending those payloads are identical.

## Finite-horizon optimization and receiver comparison

`_optimize` evaluates every first action in every positive-mass first
information set and every feasible second information set after each such
action. It saves continuations for unselected first-action alternatives too.
Consequently the coverage-aware result is an exact two-stage best response
to the fixed A policy within the specified observation process; it is not
a joint team optimum in which A can also change.

For the coverage-aware second action, already-covered A worlds contribute
the same payoff under every candidate B action. Omitting that constant from
the primary action score is valid. The verifier instead explicitly adds
that mass to every candidate score, then checks all local deviations. The
first-stage coverage score executes the saved, independently checked optimal
continuation for each possible first action. These checks are sufficient for
this two-stage decision problem.

The individual-MAP class intentionally maximizes immediate personal hit
probability at the first action and posterior hit probability after its own
failure. It is a myopic prescribed rule, not a strategic equilibrium and
not the two-stage optimum for the team objective. The documentation states
those limitations. A difference from the coverage-aware class should be
reported as a decision-rule restriction, not as evidence that information
harms an unrestricted team. The no-information unit test supplies a useful
independent control: with five labels, A and MAP B duplicate labels zero
and one, while coverage-aware B can cover two additional labels.

## Earlier-information emulation

The emulation uses early augmented `(X,C)` information to construct the
event's virtual arrival time. On the virtual-late first branch it indexes
the event policy with missing `X`, correctly ignoring the prematurely
available clue. The second-stage lookup includes the actual delivered `X`,
the inferred bit, the receiver's own first action, and its hit status.

Both primary and verifier check the saved mapping, not just an accidentally
equal payoff. The verifier then executes the emulated policy on independently
built early-augmented worlds. The coverage-aware early-augmented receiver
can therefore attain every event-policy value, so the nonpositive residual
gate is appropriate. An emulated MAP policy need not itself remain MAP under
the richer information, which the model explicitly acknowledges.

## Independence and coverage of verification

The primary uses common-denominator integer channel weights and grouped
backward induction. The verifier uses separate Fraction likelihood products,
constructs timing branches and observable histories independently, executes
saved policies, and checks every relevant first- and second-action deviation.
It validates sender policies, missing/alien receiver histories, target and
information-set masses, channel summaries, all comparison rows, emulation
records, and the aggregate summary. The monkeypatch test explicitly disables
the primary probability, observation, optimizer, executor, and emulation
helpers while invoking verification.

Shared `_cells`, identifiers, basic serialization, and the same scientific
assumptions remain common dependencies. Method independence cannot rule out
a mistaken model specification, but here it is materially stronger than
re-reading a primary optimizer's reported value.

## Two nonblocking qualifications to preserve in reporting

1. **Label conjugation is a narrow check.** The source-law check genuinely
   compares cyclically relabeled world probabilities. The policy check in
   `_audit_saved_policy` shifts the already-selected target and actions
   together and retains the sender-hit indicator. This verifies the elementary
   success-event conjugation identity; it does not rerun optimization on a
   relabeled observation table or independently exercise transformed
   tie-priority logic. Avoid describing it as a fresh relabeled-policy
   optimization test. Either keep this narrower description or strengthen
   it prospectively if a stronger invariance claim is desired.
2. **Built-in corruption booleans exercise comparison predicates.**
   `_corruption_checks` mutates a copied independently reconstructed channel
   and checks dictionary inequality; its value control checks that a changed
   rational differs. These are limited predicate-level controls. The focused
   unit tests separately pass channel, silence, value, and policy mutations
   through the full verifier, which addresses the integration concern.
   Preserve that distinction rather than calling each runtime corruption
   boolean a separate end-to-end verifier run.

An additional implementation boundary is that `_cells` permits other
chance-to-one rational accuracy values as long as the cell count does not
exceed 36. Therefore the external frozen configuration hash, rather than
this function alone, enforces the exact registered accuracy palette. This
does not change the reviewed `config.json`; the coordinator must retain its
normal source/configuration-mismatch gate.

## Recommendation

Proceed to the coordinator's freeze gate for the specified 36-cell grid,
subject to retaining the bounded policy/timing-channel interpretation and
the supplementary-check qualifications above. No additional numerical
experiment is needed to resolve an identified correctness issue from this
review. Publication novelty, real organizational behavior, and societal
welfare remain outside the evidence this implementation can establish.

## Follow-up: substantive corruption path reviewed

Later on 2026-10-31, reviewed the author's strengthened corruption path at
`timing.py` SHA-256
`dd45bd1bcfb37b2f6153475e92c6547a2b139851115a6a3eaf3658b620874243`.
The earlier predicate-level-corruption qualification is **resolved for this
source version**. The reviewer did not execute a new fixture or primary grid.

The new `_corruption_checks` extracts a complete one-cell subset of the
already verified result, constructs the matching configuration and summary,
and first requires its uncorrupted control to pass the substantive `_verify`
path. It then sends each of the five damaged fixtures through that same path,
disabling only recursive generation of further corruptions. A rejection must
contain the expected channel- or value-validation reason, so malformed
fixture extraction cannot silently count as a successful negative control.
This is an appropriate end-to-end strengthening without rerunning the
scientific optimizer or broadening the configuration.

The label-conjugation diagnostic remains bounded as described above; no
claim of independent relabeled optimization is warranted or required for
the reviewed payoff/finite-horizon correctness conclusion.
