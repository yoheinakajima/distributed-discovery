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
  inputs match the frozen commit, manuscript hash, and PDF hash.
- The evidence-bound revision is frozen at reviewed-artifact commit
  `4fa15aa7f77dcae9f02a42c64273a04969247571`, source SHA-256
  `87a6e85450c72fc9c93b281646ecfbd60193747c80aae9eac0a022301e1f06e1`,
  and 21-page PDF SHA-256
  `ab53c6e4bd099234e42178646abdd7c9692533dfb0b63cea9d3d60ba1ccf1150`.
- Draft PR #221 tracks issue #220. AO-0014 is stopped before out-of-scope
  publication/lifecycle/release pointer mutation and before Round 2 dispatch.
- At `2026-08-06T20:06:00Z`, the owner authorized additive contract
  `tasks/common-source-trap-current-working-paper-pointers-r2.yml` against exact
  PR head `9cf1720c2b23737f1937ea2c3f1a35a898fa9809`. The contract preserves the
  immutable Compendium v0.1.0 snapshot while permitting only the current-paper
  pointer/versioning repair, full validation, and an exact revised Round 2
  packet.
- At `2026-08-06T20:11:54Z`, the owner requested an orderly computer restart.
  Work paused before pointer implementation, long validation, or Round 2
  dispatch at committed checkpoint
  `5f388fbb145421ddfad129825d8742ab8a36fb9d`.
- After restart, local HEAD, remote branch, and draft PR #221 reverified at the
  exact checkpoint; main remained `7268e445...`, issue #220 remained open, and
  the tracked tree was clean with exactly the five protected historical files
  untracked.
- The current working-paper pointers now bind revised PDF
  `ab53c6e4...`, while v0.1.0 build, verify, and readiness paths resolve paper,
  citation, registry, and release-note bytes from registered source revision
  `3ca173f4...`. No immutable release record or published hash changed.
- At 2026-08-07, the owner activated the bounded paper-review standing lane.
  Additive contract
  `tasks/common-source-trap-round2-standing-review-completion-r3.yml` records
  only its Common-Source Trap authority: existing-credential-only headless
  replacement reviews, private receipts, a USD 1 per-provider-call ceiling,
  and a USD 3 current-task ceiling within the owner-wide USD 10 aggregate.
  It does not authorize credential changes, merge, publication, deployment,
  Explore Science, new research, or Information Sharing Frontier work.
- The new OpenAI replacement wrapper reconstructs the frozen artifact through
  Git, validates its manuscript/PDF/packet hashes and 21 extracted PDF pages,
  constructs one no-tool `gpt-5.6-terra` Responses request at medium reasoning,
  requires strict closed-schema output, and stores success or redacted failure
  receipts outside Git at mode 0600. Its default command is local preflight;
  it cannot read Keychain or contact a provider without the explicit execute
  flag. Synthetic coverage is green. The exact service-only Keychain presence
  check then returned absent. No credential value was read, and no OpenAI
  request or spend occurred.
- The complete verification wall is currently blocked by a protected unrelated
  tracked deletion: `reports/benchmark/treasurebench-provider-schema-canaries/`
  `AO-0004-public-engineering-ledger.jsonl` is absent in the inherited dirty
  worktree. Its immutable-artifact test fails at file read. Formatting, Ruff,
  strict MyPy, the 18 focused Common-Source Trap tests, Agent Operations,
  program-memory, claim, editorial, publication, naming, and release audits
  pass. The missing historical file is neither restored nor modified here.

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
8. Under the additive owner decision, separate current working-paper pointers
   from the immutable v0.1.0 release snapshot, restore the complete wall, and
   freeze the correctly labeled Round 2 packet before any review dispatch.

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
- [x] Pushed the AO-0014 branch and opened draft PR #221.
- [x] Received all four reviews simultaneously through Research Atlas.
- [x] Read all four reviews and the provenance record completely; recorded
  their exact input hashes, verdicts, scores, limitations, and disagreements.
- [x] Complete every Round 1 disposition and the evidence-bound revision.
- [x] Rebuild the revised artifact twice to identical bytes and inspect every
  page of the final 21-page PDF.
- [x] Ran the complete post-revision validation wall. Ruff and strict MyPy
  passed; 1,052 of 1,060 tests passed. The eight remaining failures all require
  a revised-PDF pointer/versioning decision outside AO-0014's fixed paths.
- [x] Freeze a fresh-session Round 2 packet without dispatching it.
- [x] Stopped before pointer mutation, Round 2 dispatch, PR readiness,
  manuscript merge, and publication.
- [x] Reverified local, remote, PR, base, issue, and five-file worktree state at
  exact authorized head `9cf1720c2b23737f1937ea2c3f1a35a898fa9809`.
- [x] Added and schema-validated the narrow superseding AO-0014 pointer task.
- [x] Implement the current-versus-v0.1.0 versioning seam and its regressions.
- [x] Run the focused and complete validation wall and freeze the correctly
  labeled Round 2 packet against the revised artifact.
- [ ] Commit and push the packet and legitimate-checkpoint handoff, revalidate
  the exact final head, and route it only through fresh isolated sessions.
- [x] Record the owner standing paper-review authorization in an additive
  AO-0014 contract without copying any credential, private receipt, or owner
  private path into Git.
- [x] Implement and run synthetic tests for the headless OpenAI replacement
  wrapper: frozen source/PDF/packet/page validation, strict schema, no-tool
  request, private receipt permissions, credential clearing, missing
  credential, ambiguous delivery, page-coverage failure, model drift, and
  exact Keychain-service lookup.
- [ ] Run the wrapper only after complete local validation and an exact existing
  credential check; stop before provider contact if the credential or aggregate
  spend bound is unavailable.
- [x] Check only the exact OpenAI reviewer Keychain service after local
  validation. It is absent; preserve this as a no-contact, no-spend blocker and
  require owner credential setup outside this task before any execution.
- [x] Run the complete verification wall until its inherited protected-file
  blocker, then rerun its recorded final failure in isolation and preserve the
  exact file-absence cause without repair or cleanup.

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
- 2026-08-06: A direct `python -m jsonschema` handoff check failed before
  schema evaluation because that deprecated CLI parses instance files as JSON,
  while Agent Operations handoffs are YAML. No handoff field was weakened or
  changed in response; the repository-native `make audit-agent-ops` validator
  remains authoritative for the YAML handoff.
- 2026-08-06T20:11:54Z: The additive pointer contract passed the repository-
  native Agent Operations audit with 25 task contracts and unchanged
  scientific authority. The owner then requested an orderly restart, so no
  pointer, release tool, test, site, review packet, reviewer session, or long
  validation action began. Preserve this as the clean resumption boundary.
- 2026-08-06: Restart preflight passed exactly at local, remote, and draft PR
  head `5f388fbb145421ddfad129825d8742ab8a36fb9d`, base
  `7268e445347c4d7f9106d129af42d0e8667eb115`, open issue #220, and the five
  protected untracked files. No mutation preceded this verification.
- 2026-08-06: The first new-code style check failed on one 101-character test
  line and reported four files requiring canonical formatting. Repository Ruff
  formatting corrected only the intended files; the next focused style checks
  passed.
- 2026-08-06: The first focused pointer/release run passed 25 checks and failed
  one new regression because the lifecycle YAML collection is named `records`,
  not `papers`. Correcting the test to the existing schema yielded 26 passing
  focused checks; no production behavior was weakened.
- 2026-08-06: Compendium readiness rebuilt and verified 132 archive members,
  seven papers, and 119 pages from immutable release source `3ca173f4...` even
  when invoked from moving checkpoint `5f388fbb...`. The historical paper ZIP,
  citation asset, and release notes retained hashes `08bab6f3...`,
  `37c66ed...`, and `35d757da...` respectively.
- 2026-08-06: The first complete-wall rerun passed formatting, Ruff, strict
  MyPy, and 1,058 tests, with six CLI integration failures. Each failure was an
  identical nested-`uv` DNS lookup caused by the deliberately isolated
  `/tmp/uv-cache-ao0014`; no repository assertion failed. A first retry against
  the normal cache was itself refused by the filesystem sandbox before test
  collection. The same six tests then passed in 26.02 seconds with read access
  to the existing normal cache. Repeat the full wall in that established
  environment and preserve both failed receipts.
- 2026-08-06: The established-cache complete wall passed formatting, Ruff,
  strict MyPy, all 1,064 tests in 336.27 seconds, all claim/run/literature,
  Agent Operations, program-memory, publication, naming, release-readiness,
  and Compendium checks. The site then built 89 pages. A parallel active-paper
  build was refused before execution by the filesystem sandbox because its
  subprocess could not open the normal `uv` cache; rerun that one local build
  with the same already-validated cache access used by the green wall.
- 2026-08-06: The first correctly labeled Round 2 packet test passed eight of
  nine checks and rejected a false receipt relationship: the final visual-QA
  correction was committed at `843e1b5`, after reviewed-artifact commit
  `4fa15aa`. The packet now freezes the source/PDF at the artifact commit and
  the three canonical receipts at the later exact receipt commit instead of
  pretending one Git tree contains both histories.
- 2026-08-06: Corrected Round 2 packet validation passes nine checks. The packet
  names only the revised manuscript, revised PDF, and Round 2 rubric/response
  contract as reviewer inputs; it explicitly excludes prior packets, reviews,
  dispositions, manager synthesis, and prior sessions.
- 2026-08-06: The final packet-inclusive complete wall passed formatting, Ruff,
  strict MyPy, all 1,065 tests in 347.98 seconds, and every claim, run,
  literature, Agent Operations, program-memory, publication, naming, release,
  and Compendium audit. The immutable v0.1.0 paper ZIP, citation metadata, and
  release notes remained byte-identical. Freeze one public-safe checkpoint
  handoff for Research Atlas reviewer dispatch; do not impersonate named model
  providers from this repository worker.
- 2026-08-07: The owner activated a milestone-bounded standing paper-review
  lane. Because the prior AO-0014 contract correctly prohibited provider calls,
  private receipts, and spend, record the standing decision in a new additive
  contract rather than silently widening the old one. The new contract keeps
  the exact packet, one-call-per-missing-reviewer, no-retry, existing-
  credential-only, per-call USD 1, aggregate USD 10, and no-merge/publication
  boundaries explicit.
- 2026-08-07: The first wrapper style pass found only one unused import,
  import-order normalization, and three overlong test lines. Ruff corrected
  the mechanical issues in the two intended files; no behavioral test or
  frozen-input invariant failed. A direct installed-package preflight initially
  could not import the uninstalled new module, so the validation command now
  uses the repository source path explicitly. The source-path preflight passed
  without Keychain or provider contact.
- 2026-08-07: After the local wall passed, the exact non-enumerating Keychain
  presence check for `com.yoheinakajima.chief-of-staff.openai-reviewer` returned
  absent. No credential value was requested or read, no provider endpoint was
  contacted, and no spend occurred. The standing authorization expressly
  prohibits credential creation or changes, so the OpenAI replacement review
  stops at owner credential setup rather than falling back to a browser, Codex
  session, another provider, or another model.
- 2026-08-07: A post-build no-execute command found a local-only portability
  defect: the wrapper inferred `ROOT` from its installed wheel path and could
  not locate the frozen packet. It stopped before Keychain ingress. Resolve the
  repository from the current checkout instead, add a regression, and rerun the
  installed no-execute command before treating the wrapper as ready.
- 2026-08-07: This local `uv --no-editable` environment retained an older wheel
  even after the wrapper commit and package reinstall, so its no-execute command
  repeated the already-corrected root failure. The repository-source invocation
  `PYTHONPATH=src uv run --no-editable python -m
  distributed_discovery.editorial_review` loads the committed source, passes
  the frozen preflight, and is the sole permitted execution form for this
  wrapper. Do not use a stale installed wheel for the consequential call.
- 2026-08-07: The complete `make verify` wall passed formatting, Ruff, and
  strict MyPy, then encountered the inherited missing
  `AO-0004-public-engineering-ledger.jsonl` during the full pytest stage. Its
  isolated last-failure rerun reproduces `FileNotFoundError` at the immutable
  provider-canary preservation test. This is unrelated to AO-0014 and belongs
  to the protected dirty worktree; do not restore, delete, stage, or otherwise
  change it in this lane. The focused 18-test review suite and all repository
  audits completed green.

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
- The prior authority blocker is resolved prospectively by the additive owner
  decision and standing-review contract. The review path remains blocked until
  the owner establishes the missing exact Keychain credential and the
  aggregate-spend bound verifies after the local validation wall.
- Manuscript merge and every publication action remain unauthorized.

## Recovery and restart instructions

Resume AO-0014 from issue #220, branch
`agent/common-source-trap-review-packet`, additive standing-review contract
`tasks/common-source-trap-round2-standing-review-completion-r3.yml`, and this
plan. Confirm local, remote, and draft PR #221 still share the checkpoint head;
preserve every protected dirty worktree entry; then run the source-path wrapper
preflight and its focused tests before reading the exact OpenAI Keychain entry.
Stop with zero provider contact if that one entry is absent or the aggregate
spend bound is not provable. Round 1 and every prior failed or excluded Round 2
attempt remain nonreusable. Any qualifying Round 2 review must use only the
reverified revised manuscript, rubric, page-labelled rendered-paper input, and
correctly labeled Round 2 packet.

## Outcome and retrospective

Round 1 hardening remains complete and frozen in draft PR #221. The owner has
authorized the narrow additive pointer/versioning continuation, and its task
contract validates, but implementation is intentionally paused for an orderly
restart. No Round 2, readiness, merge, lifecycle-status, release, deployment,
or publication action has begun.
