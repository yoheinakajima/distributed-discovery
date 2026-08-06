# AO-0014 Common-Source Trap independent review

## Purpose and intended outcome

Freeze one exact, repository-authoritative review baseline for *The
Common-Source Trap*, let Research Atlas coordinate four fresh independent
reviews using only exact pointers and provenance, then revise only after the
complete four-review bundle arrives simultaneously. The task creates no new
scientific evidence and authorizes no manuscript merge or publication.

## Current state

- Public `main` and `origin/main` resolve to
  `7268e445347c4d7f9106d129af42d0e8667eb115`.
- PR #219 is merged at that commit. Main CI run `31110671441` passed; Pages run
  `31110671871` built and uploaded the artifact but its final deployment timed
  out. The Pages incident remains separate and does not block offline review.
- Issue #220 and branch `agent/common-source-trap-review-packet` own AO-0014.
- The canonical paper tree at the source commit is
  `2c34089accf3e9bbd2d6d038aceb2156bc0aa2a4`.
- The manuscript SHA-256 is
  `2f7d9ead7e54a7c4b852935b9648361cc682772c5fe41853d0193b86ce3fbdad`.
- The byte-reproducible 21-page PDF SHA-256 is
  `afa9384eca60cf2a0291c2c42012f15ca59bf3d29b7c939b1882a0237ea58ff7`.
- Research Atlas returned the complete independent ChatGPT, Claude, Gemini, and
  Grok Round 1 bundle simultaneously at `2026-08-06T17:04:40.316Z`. All four
  inputs match the frozen commit, manuscript hash, and PDF hash. Post-bundle
  editorial revision is now active under the original fixed contract.

## DISCUSSION AND DECISION DELTA AUDIT

- `docs/program-memory/registry.yml` was read before issue and branch
  registration.
- PM-0009 is now due: its routed internal queue already selects Common-Source
  Trap as the first freeze candidate. AO-0014 routes the current owner decision
  into a review-only packet and does not change the queue or make a public
  promise.
- PM-0010 remains deferred: this task does not open a journal track, contact a
  venue, or authorize submission.
- PM-0006 and PM-0007 remain implemented through immutable citation and
  self-containment checks; the review packet exposes their verification
  surfaces but changes neither policy.
- Information Sharing Frontier is explicitly parked. No trigger moves it into
  the active lane.
- The current owner decision is fixed in the AO-0014 task contract and this
  plan. No scientific claim or owner authorization is delegated to Atlas.

## Scope

- Freeze exact source, PDF, receipt, input, claim, run, and toolchain pointers.
- Provide one concise guide and one machine-readable review packet.
- Prove the packet against Git objects at the frozen source commit.
- Rebuild in a disposable checkout and run the docs-editorial wall.
- Push one draft PR and wait for all four independent reviews.
- After the complete bundle, preserve provenance and dispositions before any
  evidence-bound manuscript revision.

## Non-goals

- No manuscript change during packet preparation.
- No Information Sharing Frontier work.
- No scientific execution, claim or lifecycle mutation, provider access,
  credentials, spend, release, DOI, submission, publication, deployment, or
  merge.
- No mutation of issues #212 or #218, retained historical branches, or the five
  historical untracked files.

## Assumptions

- Git object `7268e445...` is sufficient to reconstruct the exact review input.
- The tracked validation and provenance receipts accurately describe the
  frozen paper only if their hashes and referenced inputs verify.
- Review independence requires each reviewer to receive the same packet and no
  other review, then return provenance sufficient for Atlas to bundle all four.

## Milestones

1. Register issue #220, the AO-0014 contract, plan, and branch.
2. Freeze and test the machine-readable review packet and reviewer guide.
3. Rebuild the frozen paper in a disposable checkout and run focused and full
   docs-editorial validation.
4. Commit, push, open one draft PR, and stop at `review-bundle-required`.
5. Receive one simultaneous complete four-review bundle from Research Atlas.
6. Add reviewer provenance and a disposition table, revise from repository
   evidence, rebuild, and rerun every native check.
7. Freeze the exact revised PR head and stop before manuscript merge.

## Progress checklist

- [x] Reverified public main, PR #219, issue #218, main CI, Pages failure, and
  the absence of another substantive PR.
- [x] Read root, paper, study, research-governance, Agent Operations, and
  program-memory authority.
- [x] Registered issue #220 and the AO-0014 task branch.
- [x] Validated and committed the fixed task contract and living plan as
  `724e131`.
- [x] Froze the review packet and reviewer guide without changing the paper.
- [x] Run focused packet tests and the complete docs-editorial wall. The clean
  pushed-head rerun passed Ruff, strict MyPy, all 1,057 tests, claim/run and
  literature audits, all Agent Operations/program-memory/publication audits,
  and a byte-identical 21-page active-paper build.
- [ ] Push and open the draft PR.
- [x] Received all four reviews simultaneously through Research Atlas.
- [x] Read all four reviews and the provenance record completely; recorded
  their exact input hashes, verdicts, scores, limitations, and disagreements.
- [x] Complete every Round 1 disposition and the evidence-bound revision.
- [x] Rebuild the revised artifact twice to identical bytes and inspect every
  page of the final 21-page PDF.
- [ ] Run the complete post-revision validation wall.
- [x] Freeze a fresh-session Round 2 packet without dispatching it.
- [ ] Stop before manuscript merge.

## Discoveries and surprises

- The paper source surfaces seven claim IDs across DD-008, DD-008A, DD-006B,
  DD-009, DD-011, and DD-008B. The theorem-family map names the primary family,
  while the review packet must preserve all actual manuscript dependencies.
- A local `build.log` exists but `*.log` is ignored and the file is absent from
  the frozen Git tree. The first packet test correctly rejected it as a
  canonical receipt. The packet now excludes it and relies only on tracked
  `validation.json`, generated provenance, visual QA, and the exact PDF.
- The first disposable-checkout command created the checkout correctly but ran
  `make` from `/tmp` instead of the printed checkout path, so both targets
  failed with `No rule to make target`. The same already-created checkout was
  then used with the correct working directory; no repository state changed.
- The complete review bundle supplies exact reviewer models and session
  locators but not separate review-start and review-completion timestamps. The
  disposition records the missing fields rather than inventing them; Atlas
  retains the raw locators while the public repository binds the inputs by
  SHA-256.
- Claude proposed a closed-form interior sign boundary. Independent algebra and
  a rational-grid regression agree with the formula, but adding it to the paper
  would create a new scientific result. AO-0014 therefore records and defers it
  instead of silently promoting reviewer output.

## Decision log

- 2026-08-06: Use AO-0014 documentation-editorial governance because the work
  creates a durable review artifact and later editorial revision but no new
  evidence.
- 2026-08-06: Freeze the review input at current public main rather than at the
  AO-0014 branch head, so governance-only packet commits cannot change what
  reviewers evaluate.
- 2026-08-06: Treat Pages as a separate operational failure; do not delay
  offline review preparation and do not retry deployment here.
- 2026-08-06: The first focused packet run had four passing tests and one
  failure because it tried to bind ignored `build.log` to the source commit.
  Preserve the failure and exclude that noncanonical intermediate rather than
  weakening commit-bound validation.
- 2026-08-06: The corrected five packet tests passed, then standalone Ruff
  found one import-order issue and strict MyPy found 25 consequences of an
  overbroad `object` annotation in the new test helper. The test now uses an
  explicit `Any` boundary at YAML ingress; no production or scientific type
  surface was weakened.
- 2026-08-06T16:49:22Z: Corrected focused validation passed five tests, Ruff,
  and strict MyPy. The exact frozen commit rebuilt in a disposable checkout to
  the registered 21-page PDF and identical PDF, validation, and provenance
  hashes with no tracked paper diff.
- 2026-08-06T16:49:22Z: Poppler rendered all 21 pages. Two contact sheets plus
  full-size inspection of dense figures/tables, the extension audit, and both
  reference pages showed no clipping, overlap, malformed glyph, missing page,
  or new visual defect. This confirms the existing visual-QA receipt without
  changing it.
- 2026-08-06: The first complete `make verify` attempt stopped at Ruff's format
  check because the new typed test had not been run through `ruff format`.
  Subsequent shell commands continued and `make papers` passed all six paper
  builds, but that all-paper generator refreshed two parked Information Sharing
  Frontier `source_commit` fields to the AO-0014 head. Both out-of-scope changes
  were immediately restored byte-for-byte with no commit. AO-0014 retains the
  successful all-paper build observation and reruns the repository wall plus
  the active paper target after formatting.
- 2026-08-06: After formatting, the next `make verify` passed Ruff, strict MyPy,
  paper-specific integrations, and 1,053 tests, but four historical pilot
  fixtures rejected the unpushed AO-0014 head because their production guard
  requires the synthetic authorization commit to exist on a remote branch.
  This is the expected fail-closed remote-ancestry invariant. Commit and push
  the intended packet changes, then rerun the exact wall; do not weaken or
  bypass the guard.
- 2026-08-06: The exact pushed-head rerun passed all 1,057 tests in 375.18
  seconds, every repository audit, the compendium dry-run verification, and the
  active Common-Source Trap build. This closes the packet-preparation
  validation wall without relying on the truncated prior process receipt.
- 2026-08-06: Research Atlas returned one simultaneous four-review bundle. The
  fixed AO-0014 contract already authorizes a repository-evidence-bound
  post-bundle revision, so no contract expansion or competing substantive lane
  is needed.
- 2026-08-06: Public primary records verify that R&D portfolio choice,
  duplication, and innovation contests are close mechanism-level neighbors.
  They do not establish equivalence or non-equivalence to the exact finite
  threshold theorem. The revision therefore sharpens conditional novelty and
  does not import reviewer-supplied citations into the manuscript.
- 2026-08-06: Preserve the reviewer disagreement on the proposed interior
  formula. It is algebraically consistent with the existing definitions on the
  tested rational grid, but it remains outside the manuscript because AO-0014
  cannot create or promote a new scientific claim.
- 2026-08-06: The first post-edit focused run passed 14 checks and failed two
  source-string regressions because required boundary phrases were split across
  TeX source lines. The manuscript now retains the exact tested strings; no
  assertion or scientific boundary was weakened.
- 2026-08-06: The second focused run passed 15 checks and retained one failure
  because the universal-under-acquisition phrase still broke before its final
  word. The exact full phrase is now contiguous in source for the native paper
  boundary test.
- 2026-08-06: The first revised build was byte-reproducible and passed compiler
  checks at 22 pages, but all-page rendering found an excessive-blank-page
  defect: only one two-line reference appeared on page 22. Use a conventional
  smaller bibliography block, rebuild from a committed source, and repeat the
  complete visual review.
- 2026-08-06: The layout repair produced a byte-reproducible 21-page PDF at
  `ab53c6e4bd099234e42178646abdd7c9692533dfb0b63cea9d3d60ba1ccf1150`.
  Final rendered pages 1--19 are byte-identical to the already inspected
  revised render; final pages 20--21 were inspected directly. All 21 pages pass
  clipping, collision, glyph, equation, table, figure, heading, missing-content,
  and blank-space review.
- 2026-08-06: The first complete post-revision wall passed Ruff, strict MyPy,
  1,052 of 1,060 tests, and every unrelated test. Eight failures all traced to
  the new PDF identity: the visual-QA reader selected the historical hash, and
  site, lifecycle, compendium, release-readiness, and naming checks selected
  stale publication/release pointers. The visual-QA pointer is inside AO-0014
  and is corrected. The other pointer files are outside the fixed task paths,
  and release mutation is explicitly unauthorized, so they remain unchanged
  pending additive owner authority.

## Validation strategy

- Validate the task contract and Agent Operations invariants.
- Recompute every packet hash from the exact source commit with `git show`.
- Verify claim IDs, study IDs, run IDs, lifecycle labels, source inputs,
  validation receipts, and generated provenance.
- Build twice through the native paper target in a disposable checkout and
  require the recorded PDF hash and page count.
- Run `make bootstrap`, focused packet tests, `make common-source-trap`,
  `make verify`, `make papers`, `make audit-agent-ops`,
  `make audit-program-memory`, and `make audit-publication-infrastructure` as
  applicable without deploying.
- Confirm the active branch diff contains no paper or Information Sharing
  Frontier change and preserves exactly the five unrelated untracked files.

## Commands and expected observations

- `uv run pytest tests/integration/test_common_source_trap_review_packet.py`:
  packet hashes and boundaries match the frozen Git object.
- `make common-source-trap`: two byte-identical builds produce the recorded
  21-page PDF with resolved claims and citations.
- `make verify && make papers`: repository and all paper checks pass without a
  manuscript diff.
- `make audit-agent-ops && make audit-program-memory && make
  audit-publication-infrastructure`: governance and publication boundaries
  pass.

## Artifacts produced

- `tasks/common-source-trap-independent-review.yml`
- `plans/COMMON_SOURCE_TRAP_INDEPENDENT_REVIEW.md`
- `reports/editorial/common-source-trap-review-packet.yml`
- `reports/editorial/common-source-trap-review-guide.md`
- `tests/integration/test_common_source_trap_review_packet.py`
- A later `reports/editorial/common-source-trap-review-disposition.yml` only
  after the complete review bundle arrives.

## Blockers

- Round 1 no longer blocks revision: the complete simultaneous bundle is
  present and provenance-bound.
- Round 2 dispatch, manuscript merge, and every publication action remain
  unauthorized.

## Recovery and restart instructions

Resume AO-0014 from issue #220, branch
`agent/common-source-trap-review-packet`, the fixed task contract, and this
plan. Confirm the five unrelated untracked files remain untouched. Continue
from the first unchecked milestone. Round 1 is complete and nonreusable; any
Round 2 review must use four fresh isolated sessions and only the revised
manuscript, rubric, and revised packet.

## Outcome and retrospective

Pending. The first checkpoint is complete only when the exact packet and draft
PR pass validation and the task stops at `review-bundle-required`.
