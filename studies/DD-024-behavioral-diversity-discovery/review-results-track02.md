# DD-024 track 02: internal audit of preserved numerical results

Audit date: 2026-10-31 UTC. Proposed disposition: **audited exploratory;
zero central claim promotions**.

The saved finite-class findings pass this audit. Coordinated randomization
improves worst-regime success over the best deterministic contingent plan in
**5 of 18 cells**, with a maximum gain of **`1/4`, or 25 percentage points**.
The remaining 13 cells have exactly zero gain. This is a bounded ambiguity
hedging result in a declared six-role library, not evidence that chaotic
personalities or stable population diversity improve society.

## Evidence and audit boundary

Audited run:
`results/exploratory/20261031T215933Z_DD-024_caa1bf80_1d0ab47ae5`.

Frozen source commit:
`caa1bf800bde9033e6b317e46bad0aff73828338`.

Primary configuration digest:
`1d0ab47ae53bd3526cc3150d4dc9bccbed896d2a4aec070ac488bb439c96c616`.

The evidence entry points are the [manifest](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_1d0ab47ae5/manifest.json),
[complete artifact inventory](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_1d0ab47ae5/artifact-hashes.json),
[result and row index](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_1d0ab47ae5/outputs/result.json),
[saved summary](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_1d0ab47ae5/outputs/summary.json),
and [independent verification record](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_1d0ab47ae5/outputs/verification.json).
The model boundaries remain those in [track-02/model.md](tracks/track-02/model.md)
and [track-02/novelty.md](tracks/track-02/novelty.md).

This is an internal review by the track-03 implementation agent, who reviewed
but did not author track 02's scientific module. The same reviewer contributed
the shared runner's artifact-inventory compatibility fix. It is not external
peer review. The audit used separate standard-library calculations over saved
files; it did not call the primary evaluator, rerun its optimizer, execute a
primary configuration, or regenerate latent-world probabilities. Only this
review file was written. Model, source, configuration, and run bytes were not
modified.

## Integrity and provenance checks

All **28 direct manifest-output hashes** and all **30 artifact-inventory
hashes** match the preserved files. The inventory covers exactly the files
other than the manifest and inventory itself; it binds both logs and the
historical invocation script. Paths were checked for safe containment before
reading. The manifest's safe output projection matches the inventory.

All **11 source/input hashes** match both the current inspected files and the
Git blobs at the frozen commit. These include the scientific module, shared
runner, model, novelty screen, complete-grid registry, task contract, and
dependency lock. The saved configuration's canonical digest matches the
manifest, its embedded copy in the result matches the saved configuration,
and the reservation records the same run, track, source, and configuration.
The 18 row specifications match the complete configured grid in order.

The manifest SHA-256 independently read in this audit is
`746ed20eed61d99615040a4b80dc0753ba39dbeb9a113662d30182212f174fb6`.
The copied artifacts are therefore consistent with their preserved primary
inventory. This audit did not repeat a separate comparison with the original
detached-worktree copy.

The manifest records clean source, exit status zero, passed validation, and
normal completion. The [validation record](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_1d0ab47ae5/validation.json)
reports **3.577773 seconds** elapsed against the 120-second cap, with no
reported problems. The [worker resource record](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_1d0ab47ae5/outputs/resources.json)
reports **96,996 KiB**, or **94.72265625 MiB**, peak resident memory against
the 1024-MiB address-space cap; resident memory and address space are distinct
measurements. Worker elapsed time is 3.454253 seconds. Standard error is empty.
These are preserved execution measurements, not a new timing experiment or
an independent observation of the original live process.

## Independent arithmetic checks

The audit reconstructed all **15,768 saved contingent-plan payoff vectors**
from the saved profile payoffs and diagnostic probabilities, checking complete
plan coverage and probability bounds. It recomputed the best deterministic
worst-regime value and checked each saved choice against the complete plan
table. For every coordinated mixture it checked positive weights summing to
one, execution of the selected support, the reported worst-regime value, and
all **15,768 dual inequalities**. Each mixture attains its saved all-plan
upper bound.

It also checked **54 known-prior objectives** against all saved plans and
recomputed **36 selected independent-departure policy values**. The latter
uses a separate elementary formula: conditional on a correct shared clue, an
agent with departure rate `epsilon` succeeds with probability
`1 - 2*epsilon/3`; conditional on an incorrect shared clue the probability is
`epsilon/3`. The two independent-device outcomes give the at-least-one or
both-correct probability, which is then integrated over the shared clue and
diagnostic. This checks the selected saved policies; their grid-optimality
check remains in the preserved independent primary verifier.

All audited contrasts and grid counts agree with the saved summary. These
checks are conditional on the archived profile payoff table. They complement
the preserved verifier, which separately reconstructed those payoffs from
latent-world enumeration, checked 60 normalizations, and rejected all four
registered corruptions. This audit does not misrepresent saved-table
reconciliation as a second raw-world replication.

## Full-grid findings

Probabilities below are worst-regime success probabilities. Decimal
percentages are rounded to six decimal places; fractions are authoritative.
Differences are percentage points, not relative percentage increases.

There are **5 positive cells (`5/18` = 27.777778%)**, **13 zero cells
(`13/18` = 72.222222%)**, and no negative cells. Nonnegativity follows from
including deterministic plans in the mixture class; it is a construction
check, not an empirical discovery about randomization.

All nine **at-least-one-success** cells have the same values, across all three
source-mixture settings and all three diagnostic settings:

| Quantity | Exact probability or contrast | Percentage or percentage points |
| --- | --- | --- |
| Best deterministic contingent plan | `8/9` | 88.888889% |
| Best coordinated mixture | `8/9` | 88.888889% |
| Best homogeneous independent departure | `5/9` | 55.555556% |
| Best heterogeneous independent departure | `5/9` | 55.555556% |
| Mixture minus deterministic | `0/1` | 0 percentage points |
| Coordinated class minus either departure baseline | `1/3` | 33.333333 percentage points |

The nine **both-agents-successful** cells are:

| Private-source mixture `rho` | Diagnostic | Deterministic value | Coordinated-mixture value | Mixture gain over deterministic |
| --- | --- | --- | --- | --- |
| `0/1` | None | `1/3` (33.333333%) | `1/2` (50.000000%) | `1/6` (16.666667 pp) |
| `0/1` | Noisy | `29/48` (60.416667%) | `11/18` (61.111111%) | `1/144` (0.694444 pp) |
| `0/1` | Perfect | `25/36` (69.444444%) | `25/36` (69.444444%) | `0/1` (0 pp) |
| `1/2` | None | `1/3` (33.333333%) | `27/50` (54.000000%) | `31/150` (20.666667 pp) |
| `1/2` | Noisy | `21/32` (65.625000%) | `1939/2934` (66.087253%) | `217/46944` (0.462253 pp) |
| `1/2` | Perfect | `55/72` (76.388889%) | `55/72` (76.388889%) | `0/1` (0 pp) |
| `1/1` | None | `1/3` (33.333333%) | `7/12` (58.333333%) | `1/4` (25.000000 pp) |
| `1/1` | Noisy | `17/24` (70.833333%) | `17/24` (70.833333%) | `0/1` (0 pp) |
| `1/1` | Perfect | `5/6` (83.333333%) | `5/6` (83.333333%) | `0/1` (0 pp) |

Both independent-departure baselines equal `1/3` (33.333333%) in all nine
both-success cells. Thus all positive mixture gains occur under the
both-success objective: three with no diagnostic and two with noisy diagnosis.
Perfect diagnosis removes the mixture gain in all six perfect-diagnostic
cells, including both success thresholds.

## Maximum-gap witness

The unique maximum occurs in `rho1-none-tau2`, preserved in
[row 0013](../../results/exploratory/20261031T215933Z_DD-024_caa1bf80_1d0ab47ae5/outputs/rows/0013.json):
one common private-source draw, no diagnostic, and a requirement that both
agents identify the target.

The best deterministic worst-regime value is `1/3` (33.333333%). The saved
coordinated policy flips a common fair coin between these two complete plans:

| Plan | Team roles | Regime A success | Regime B success | Mixture weight |
| --- | --- | --- | --- | --- |
| `d0000` | Both follow the private clue (`P,P`) | `1/3` | `5/6` | `1/2` |
| `d0007` | Both follow the shared clue (`S,S`) | `5/6` | `1/3` | `1/2` |

The mixture therefore obtains `7/12` (58.333333%) in either regime, giving
the exact `1/4` gain. The saved dual gives equal weight to the two regimes and
bounds every one of the 36 deterministic plans by `7/12`; the mixture attains
that bound.

This witness is especially important for interpretation: **the team is
homogeneous within each realized plan**. The improvement comes from ex-ante
coordination and ambiguity hedging between plans, not a team containing one
stable planner type and one stable spontaneous type. Nature chooses its
regime before observing the common coin's realization, as registered.

## Independent departures versus the coordinated class

Allowing distinct independent departure rates does not improve over a common
rate anywhere on the declared grid: the two independent baselines tie in
**18 of 18 cells**. Neither exceeds the deterministic role-class benchmark:
they tie it in three cells and fall below it in fifteen.

The coordinated class exceeds either departure baseline in every cell. Its
smallest excess is `1/6` (16.666667 pp), at `rho0-none-tau2`; its largest is
`1/2` (50 pp), at `rho1-perfect-tau2`. The latter is **not** a benefit of added
randomization: that cell's mixture-versus-deterministic gap is exactly zero.
The deterministic class already achieves `5/6`, versus the departure
baseline's `1/3`.

The comparator difference must therefore remain explicit. Independent
departure means following the shared clue or selecting a uniformly random
target. It does not mean independently mixing over the same full six-role
library available to the coordinated class, and it does not use the private
clue to choose a role. The coordinated class also has a common random device.
Equal evidence access and two actions do not isolate these policy and
coordination differences. Describing the entire class-versus-departure gap
as a pure benefit of correlated noise would overstate this experiment.

## Diagnostic and known-prior controls

Every perfect-diagnostic cell has zero mixture gain. In the both-success
subset, the deterministic/coordinated values are `25/36` (69.444444%),
`55/72` (76.388889%), and `5/6` (83.333333%) as `rho` rises from zero to one.
Noisy diagnosis leaves only the two small positive gaps `1/144` and
`217/46944`; it removes the gap at `rho=1`.

Across all 54 registered cell/prior combinations, no mixture exceeds the
best deterministic plan for the known-prior expected-success objective.
The saved robust mixture equals that known-prior optimum in 39 combinations
and falls below it in 15. The best deterministic expected value bounds every
mixture because expected success is linear in mixture weights; these data
respect that control.

At the maximum-gap witness, known regime-A priors `1/4`, `1/2`, and `3/4`
give deterministic expected-success optima `17/24`, `7/12`, and `17/24`
(70.833333%, 58.333333%, and 70.833333%). The robust fair mixture gives
`7/12` under all three priors. It ties at the equal prior and loses by `1/8`
(12.5 pp) at either unequal prior. A worst-regime advantage therefore does
not translate into a general expected-success advantage under known odds.

## Disposition and limitations

**Retain as audited exploratory exact bounded computation, with zero central
claim promotions.** The numerical table and witness are coherent, the
independent verification record passes, and the saved certificate and
provenance checks withstand this additional audit. No replacement run or
parameter expansion is warranted by these results.

The six-role library excludes general clue-to-action mappings and role
assignment after target clues arrive. Its exact optimum is not unrestricted
team optimality. Diagnostic observations are free in this synthetic model;
the experiment does not price sensing, communication, implementation, or
coordination. The two adversarial evidence regimes are specified assumptions,
not estimated frequencies in a human environment.

Grid proportions describe the 18 chosen configurations; they are not
probabilities that a benefit occurs in society. The model contains no
longitudinal personalities, stable planner/nonplanner populations, observed
human behavior, welfare measure, or costs of unpredictability. Exact rational
arithmetic removes sampling uncertainty inside this model, not model error
or external-validity uncertainty. Established maximin randomization and
convexification explain the mechanism; worldwide novelty remains
unestablished. Any future broader claim requires a separately registered
question, a properly matched comparator, and an appropriate empirical or
theoretical evidentiary basis.
