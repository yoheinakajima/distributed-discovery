# DD-024 internal review before primary execution

Review date: 2026-10-31 UTC. Reviewer: the campaign's track-03 implementation
agent, reviewing the coordinator's shared runner and the peer track-02
implementation. This is an internal review within the same assistant team,
not external peer review or independently replicated empirical evidence.

## Scope and current disposition

Reviewed the study/task contracts, the shared runner
`src/distributed_discovery/behavioral_diversity/study.py`, track 02's
`robustness.py`, its model/configuration, and relevant focused tests. The
reviewer initially did not edit those files, execute a primary grid, create a
primary run, commit, push, or promote a numerical claim. One declared track-02
development cell was evaluated for additional adversarial checks. The later
site-compatibility addendum below records a narrowly authorized runner fix
implemented by this reviewer; that addendum is an author validation record,
not an independent review of the author's own change.

**Scientific disposition:** no blocking comparator, probability-accounting,
or certificate-independence error was identified in track 02's inspected
implementation. The restricted scope and interpretation limits below are
necessary parts of any eventual claim.

**Runner disposition:** the initial implementation had a blocking
attempt-preservation gap and a source-binding gap. Both were reported and
corrected before freeze. The second inspection found no remaining blocking
issue for the specified controlled campaign. This review supports proceeding
to the coordinator's clean-source freeze and primary gate; it does not itself
claim that a source commit, resource-limited primary, or result already exists.

The initial review was against working source over repository checkpoint
`2ce35ccb1a8d12c720bdda713de830b9ecfc7ae9`, rather than a claim that the
uncommitted implementation was already a frozen source revision. Inspected
file SHA-256 values were:

| File | SHA-256 |
| --- | --- |
| `study.py`, first inspection | `2c519f2e1470225075858502fcbd89e4036808463d595001de22c0fbef4b741b` |
| `robustness.py` | `411b87385db90f43860632af61dfc7b0eed5129bfcb89ac6cd772da09ac8eae5` |
| track-02 `model.md` | `6efead6d7139e8bbc301515f2816e45d3da08d14e6faca54d2a34464fe8e502f` |
| track-02 `config.json` | `b97890f7f46967d40b39d8448b60fc0fcde960f7c8aa28fe204b57d9aefca4aa` |

## Runner findings and required closure

### R1. Preserve the attempt before launching the worker — blocking initially

The first runner created its final manifest only after worker completion,
verification JSON parsing, environment collection, and output hashing. Its
duplicate guard scanned completed manifests in the local worktree. A parent
interruption or truncated verification JSON could therefore leave an attempted
run without a manifest, allowing another attempt after the timestamp changed.
Two detached worktrees also did not share that manifest scan.

Required closure: reserve the attempt exclusively before launch in the common
Git directory shared by the campaign worktrees; write an initial manifest
before the scientific process; preserve unsuccessful, malformed, interrupted,
and cap-limited outcomes in protected finalization. The reservation should
be keyed by admitted track and store the configuration digest. A key containing
only track plus digest would permit a second attempt after changing the
configuration, contrary to the one-primary-per-track contract. A hard kill
of the parent may prevent final metadata, but it must leave an unmistakable
incomplete attempt and a consumed reservation.

The common Git directory is a local campaign guard, not a cross-clone global
registry. The committed result ledger and coordinator authority remain
necessary if work moves to another repository clone.

### R2. Bind executed inputs and saved scientific artifacts — required

The first runner hashed clean source before launching a worker that reread
the live configuration. It did not recheck those hashes after execution.
Clean detached worktrees reduce the likelihood of a concurrent change but
do not by themselves demonstrate that the recorded inputs were the executed
inputs. The primary file configuration, frozen manifest configuration, and
worker configuration must agree; changed source/input hashes must fail the
attempt rather than inheriting a passing scientific verifier.

The first worker verified its in-memory result after writing shards. Verify
the reloaded saved shards so the checked object is the persisted scientific
artifact. Hashes then bind those checked artifacts. This is separate from
checking the evaluator's mathematical output.

The readiness gate should bind the complete admitted grids before launch:
18 track-02 cells, 80 track-03 cells, and track 04's registered configuration.
Small subgrids accepted by scientific APIs are development conveniences and
must not silently substitute for the frozen primary configuration.

### R3. Describe termination and reproduction accurately — required

The parent enforces a wall-time bound on the combined worker, while child
address-space and CPU limits apply before its Python module imports. These
mechanisms cover evaluation and independent verification together. They do
not ensure the worker can write its resource record after a hard kill or
memory exhaustion; missing measurements must remain missing.

In the initial runner, a negative process return code still retained the
termination label `completed`. Preserve signal termination explicitly; an
exit signal alone should not be mislabeled as a proven memory-cap cause.

The initial `reproduce.sh` reentered the primary execution gate, which correctly
refuses after an attempt is recorded. Distinguish a historical invocation from
an authorized new primary run, and provide or document a separate route for
checking preserved outputs. Reproducibility should not require bypassing the
single-attempt rule or overwriting an immutable result directory.

## Track-02 scientific and comparator review

### Probability and timing specification

The primary factorization correctly separates the common-private-source
branch from independent private-source draws, conditional on target and
public clue. The verifier separately enumerates both branches, including
their distinct latent outcomes when their observed clue pairs coincide.
`rho` is a source-mixture probability, not a Pearson correlation coefficient.

Both routes use the correct threshold events: at least one correct agent for
threshold one and both agents correct for threshold two. They integrate the
diagnostic's regime-dependent distribution before computing regime-conditional
payoffs. Nature chooses the regime before diagnostics and policy randomization;
the optimizer therefore computes the stated ex-ante maximin objective, not
an adversary that sees and counteracts a realized random choice.

All classes receive the same diagnostic and target evidence and make two
actions. Role assignment is conditioned on the diagnostic before target clues
arrive. The common random device used by coordinated mixtures is an explicit
coordination resource. Equal evidence/action accounting does not make that
device equivalent to independent agent randomization.

### Class inclusion and certificate validity

The deterministic comparator contains all 36 role pairs, or all 1,296
diagnostic-contingent pairs for a binary diagnostic. Its role pairs already
include heterogeneous assignments. The coordinated mixture randomizes over
these complete plans. Thus a positive mixture gap would measure the value of
coordinated randomization under regime ambiguity within this restricted class;
it would not demonstrate an advantage of adding stable heterogeneous people.

The independent-departure comparator follows the public clue or chooses a
uniform random target, including the public label as one possible random
draw. Its five-point rates can depend on the same diagnostic. The heterogeneous
rate grid includes the homogeneous grid. Both are distributions over the
declared `S`/constant-role plans and therefore belong to the full coordinated
mixture class. Their values should not exceed its optimum; continuous-rate
optimality is not claimed.

The two-regime convex-hull optimizer's certificate uses a regime weight in
`[0,1]` to upper-bound every deterministic plan. A valid attaining mixture
with equal primal and dual values establishes the finite-class optimum
without requiring the verifier to reproduce the hull algorithm. The
known-prior comparator correctly optimizes integrated expected success and
allows the same diagnostic contingency. Mixing cannot improve that linear
objective above the best deterministic plan in the class.

The perfect-diagnostic zero-gap control and the threshold-event containment
check are appropriate. The target/agent relabeling checks operate on values,
without falsely demanding that arbitrary label-based tie choices themselves
be invariant.

### Verification independence and adversarial fixture

The verifier reconstructs action outcomes by direct target, clue, source-branch,
and diagnostic enumeration. It does not call the primary factorization,
plan evaluator, hull solver, departure evaluator, or summary function. Its
independent-departure calculation enumerates random-device outcomes directly.
It checks all finite plans and the saved mixture's execution, rather than
accepting only a reported optimum value.

Shared configuration parsing, role identifiers, elementary rational types,
and model assumptions remain common dependencies. The two implementations
can agree on a misspecified scientific model. This review does not erase
that limitation or constitute proof-assistant verification.

One additional non-primary fixture evaluated only `rho1-none-tau2` and checked
the saved result. Baseline verification passed. All four additional mutations
were rejected: a negative dual regime weight; a changed mixture member while
retaining the original valid weights; an inflated known-prior expected value;
and a changed saved role assignment. No full 18-cell grid was evaluated by
this reviewer. The fixture produced no primary result or numerical claim.

## Interpretation limits that survive a passing run

- The six-role library excludes general mappings from private/public target
  clues to actions and excludes target-clue-dependent role reassignment.
  Finite-class exactness is not unrestricted optimality.
- The two ambiguity regimes and free diagnostic specify a synthetic decision
  problem. They do not estimate a human environment, a trait distribution,
  institutional costs, or social welfare.
- Mixture value reflects standard ambiguity hedging and an explicit common
  coordination device. Worldwide novelty remains unestablished; the saved
  overlap screen is part of the finding.
- The design has no sampling uncertainty. Exact arithmetic removes sampling
  error inside the model, not model error or external-validity uncertainty.
- Track 03's same-information precommitment contrast must remain zero. Its
  dependence/rescue comparisons cannot be reported as a new adaptivity theorem.
- A passing computational run still requires a separate claim audit against
  its immutable source, configuration, outputs, and verification record.

## Second inspection

Completed 2026-10-31 before any primary execution. The runner SHA-256 at this
second inspection was
`0f1ec890bf00b83cfbb925dd20a2cf2d04e3722dac047f59f833e5f02825f32d`.
The reviewed runner-test hash is
`7b04a8b04e58887ff9d98619253e9767049242df748baf885b1c970fcb89882f`;
the `registered-configs.json` hash is
`367b0efea62abbdfca8298bf32018a37db732e1727e72b08aeb8b21d76578d5d`.
The track-02 implementation, model, and configuration hashes remain unchanged
from the scientific inspection above.

The revision closes R1 with an exclusive per-track file in the common Git
directory, flushed to disk before worker launch. The reservation stores the
configuration digest and cannot be replaced by using a second worktree or
changing that digest. A copied reservation and initial incomplete manifest
precede scientific execution. Missing or malformed verification is converted
to a preserved failed outcome; prior track manifests also block another run.

The revision closes R2 by binding the complete primary configurations through
`registered-configs.json`, verifying reloaded saved result shards, and checking
all frozen input hashes after the worker exits. The reviewer called only
`load_config` for all three tracks and confirmed the registered digest matches;
that operation did not import scientific modules or evaluate cells. The
registered grids contain 18, 80, and 36 cells respectively.

R3 is closed for the normal controlled execution paths: wall-time termination,
negative worker signals, and coordinator keyboard interruption have explicit
labels. The generated README calls the reproducer a historical invocation,
requires separately registered authority for a new primary reproduction, and
directs the present campaign to the read-only `--verify-existing` route.
That route checks preserved artifact hashes, source-input hashes, and the
saved configuration digest before independent reconstruction.

The reviewer ran
`PYTHONPATH=src .venv/bin/python -m pytest tests/unit/test_behavioral_diversity_study.py -q`:
**six runner fixtures passed in 0.05 seconds**. They include the shared-worktree
reservation with a changed digest and a fake worker producing malformed
verification JSON; no scientific primary is launched by these fixtures.

Remaining engineering limits are explicit. This is a local common-Git-dir
reservation, not a registry across unrelated clones. The post-run hash check
does not defend against a malicious transient source replacement followed by
restoration; clean isolated worktrees and coordinator control are part of the
execution assumptions. A hard parent kill or storage failure can leave an
incomplete record and missing resource measurements, while the consumed
reservation still prevents a silent retry. A live parent enforces the wall
deadline; operating-system CPU/address-space limits remain the child-level
backstop. The tests exercise focused failure paths and do not constitute a
power-loss, filesystem-durability, or adversarial sandbox audit.

**Review closure:** no further code blocker was identified. Retain the
scientific interpretation limits, preserve any actual execution failure, and
perform the separate result/claim audit after the authorized frozen runs.

## Site-compatibility addendum before freeze

An additional peer check exposed a compatibility defect missed in the first
two inspections: the public site's `_runs` reader rejects `.log` and `.sh`
entries in `manifest.outputs`, while the runner listed every preserved file
there. No primary had run. The coordinator authorized this reviewer to change
only the shared runner, its focused tests, and this review record; the site's
safe-suffix policy remains unchanged.

The runner now preserves every original artifact, including both logs and
the historical invocation script. It writes `artifact-hashes.json`, a mapping
from relative artifact paths to SHA-256 values covering every preserved file
except `manifest.json` and the checksum inventory itself. The manifest lists
the inventory plus the safe `.json` and `.md` artifacts. Thus logs and the
script remain bound through the inventory without being advertised as safe
public output downloads.

Read-only verification checks the manifest's direct hashes, the bound
inventory's hashes, exact inventory coverage of preserved files, correspondence
between safe inventory entries and manifest outputs, and frozen-source hashes.
Both checksum layers require relative paths without traversal or backslashes;
resolved paths must remain inside the intended directory. This also rejects
symlink escapes. The public site checks the safe projection; the runner's
read-only verifier performs the complete transitive artifact check.

The new successful-worker fixture uses no scientific module: its fake process
writes a declared engineering fixture, then the real site `_runs` reader
accepts the resulting manifest. Read-only verification of its untouched files
passes through a mocked scientific verifier. Changing `stdout.log` is rejected
before scientific verification, and a traversal entry in an otherwise
rehashed inventory is rejected. The malformed-worker fixture additionally
checks that preserved logs and the invocation script have correct inventory
hashes even for a failed attempt.

Focused checks after this change:

- Eight runner tests passed in **0.13 seconds**.
- Targeted Ruff checks and formatting passed for the runner and its tests.
- Mypy passed for the runner.
- No full primary configuration or new scientific cell was evaluated.

The final runner SHA-256 for this addendum is
`cb273145f4262510e0a00b503ec8c538a82dfabbbcb4cb871ef956aafc197280`.
The focused test file SHA-256 is
`55eb3c9b842ddb3f1d1597b26953cd8695223f182d1b7303a905a0a16eaef702`.
The prior source-hash references above describe their earlier inspection
snapshots. No remaining compatibility blocker was found in the focused
fixtures; the coordinator retains the final clean-source freeze and execution
gate.
