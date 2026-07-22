# Information Sharing Frontier paper admission

Date: `2026-07-22`
Gate issue: `#152`
Gate pull request: `#154`
Paper issue: `#153`
Evidence class: documentation and editorial judgment; no research output

## Decision

**Admit *When Does Information Sharing Improve Decentralized Discovery?* as an
archival theorem-paper candidate.** Admission authorizes the paper issue,
ExecPlan, proposed theorem/section map, and ownership map created by this gate.
It does not authorize manuscript drafting, a PDF, submission, release, DOI,
journal contact, a novelty claim, new research, or a rerun.

The prior gate held admission for exactly one mathematical deficiency: DD-021's
strongest positive recovery theorem used a centralized top-`L` portfolio. DD-022
now supplies a simultaneous, anonymous, no-role, no-assignment, no-public-seed,
independent-private-randomization game in which sharing strictly improves both
discovery and each symmetric agent's payoff on an exact dependence interval.
That closes the stated title-level implementation gap.

The admission is deliberately qualified. DD-022 proves the improvement only
for its posterior-only, provenance-blind identical-mixing equilibrium selection.
Opposite constant targets are private pure equilibria with discovery one, and
signal-ownership-aware symmetric strategies split targets on public
disagreement. The candidate paper must put this selection dependence beside the
positive theorem, not bury it as a technical footnote.

## Admission-rule audit

| Criterion | Decision | Reason |
| --- | --- | --- |
| Distinct central question | Pass | The family asks when aggregation gain outweighs lost independent rescue under an explicit discovery architecture. |
| Title-level result | Pass, qualified | DD-022 gives an exact strict decentralized sharing interval; DD-021 supplies the general residual-error criterion. The title cannot imply every-equilibrium monotonicity. |
| Decentralized implementation | Pass, selected | DD-022's frozen protocol has simultaneous anonymous actions and no roles, assignment, action authority, public correlation, or post-disclosure communication. |
| Equilibrium scope | Pass with mandatory limitation | The selected equilibrium is solved exactly and the broader pure correspondence supplies a verified counterboundary. |
| Natural literature and referee set | Pass | Information aggregation and design, team decision theory, Bayesian games, social learning, congestion, and collective search form a coherent referee set. |
| Self-contained reason to exist | Pass | Signal geometry, rescue loss, a general sharing criterion, decentralized implementation, and its selection failure form one editorial argument independent of the repository. |
| Near-term non-obsolescence | Pass | Randomized design and equilibrium refinement can extend the frontier, but neither is required to state the admitted selected-equilibrium theorem family honestly. |

## Exact editorial thesis

The paper may argue that sharing improves decentralized discovery when its
posterior gain overcomes lost independent rescue **and** the declared strategic
selection disperses actions sufficiently. It may not argue that information
sharing is generally beneficial, that common posteriors implement the planner,
or that the DD-022 interval holds in every equilibrium.

At `p=3/5`, the admitted title-level result is the DD-022 comparison between the
private anonymous label-equivariant symmetric Bayes–Nash selection and the
shared posterior-only identical-mixing selection:

`rho in ((5 sqrt(73)-17)/48, 1)`.

Discovery and each symmetric agent's expected payoff rise strictly on that
open interval, with equality at the algebraic root and at `rho=1`. DD-021's
centralized `V_L` remains an upper benchmark and implementation-gap measure.

## Relationship and ownership audit

- DD-019 owns the finite signal-geometry profiles, recovery-budget definition,
  and same-accuracy channel separation.
- DD-020 owns the point-channel aggregation/rescue identity, monotonicity
  theorem, and arbitrary-channel counterexample.
- DD-021 owns the channel-independent local residual-error criterion, bounded
  177-scenario classification and null, and centralized recovery theorem.
- DD-022 owns the selected coordination-free positive-sharing theorem, payoff
  corollary, exact threshold, implementation gap, and equilibrium-selection
  negative result.
- *The Incentive to Ignore* retains primary ownership of its strategic-attention
  theorem. It may cite DD-020 as a companion result but does not own the broader
  sharing-frontier synthesis.
- The living synthesis may explain all results but does not take their primary
  theorem-family ownership.

The detailed mapping is in
`papers/information-sharing-frontier/ownership.yml`; the proposed editorial
order is in `papers/information-sharing-frontier/theorem-section-map.md`.

## Preserved boundaries

- No study ID, claim, run, proof, source implementation, test, site route, or
  immutable artifact is created or changed by this gate.
- Claims DD-C-0089 through DD-C-0110 retain their recorded evidence classes and
  study ownership.
- The DD-019 through DD-022 primary runs are not rerun or rewritten.
- The title is provisional, admission is not submission, and no novelty or
  peer-review status is asserted.
- Human and real data remain outside the authorized program phase.
- Canonical upstream and the isolated ActiveGraph repository remain untouched.

## Local acceptance

The documentation-only branch passes `make bootstrap`, six focused site/paper
tests, `make verify`, `make papers`, and `make site`:

- Ruff formatting and lint pass; strict MyPy passes over 158 source files; all
  244 tests pass.
- All 110 claim records and 51 immutable run manifests validate unchanged.
- All six project papers rebuild at 12, 14, 3, 20, 20, and 20 pages with no
  tracked paper artifact change.
- The site builds 76 HTML routes, 85 public data files, 18 Labs, and 22
  checksum-registered downloads for 26 studies.
- Relationship, link, accessibility, checksum, and provenance checks pass
  through the site and repository integration tests.
- Focused secret and host-path scans pass; the project MIT license remains in
  place; pinned canonical upstream is clean at
  `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`.
- The diff contains no `claims/`, `results/`, `src/`, `tests/`, manuscript
  source, bibliography, or PDF change.

Branch CI and paper/site workflow identifiers are recorded on PR #154 after
they pass. The already-completed DD-022 post-merge CI is `29959514182` and
Pages deployment is `29959514196`; all nine named live-route checks returned
HTTP 200 before this gate began.

## Next authorization boundary

Paper issue #153 records the admitted candidate. The exact next command, only
after a new explicit manuscript task, is:

```sh
git status --short --branch
```

The exact first file for that task is
`papers/information-sharing-frontier/main.tex`. Until then, the repository
contains planning and ownership artifacts only.
