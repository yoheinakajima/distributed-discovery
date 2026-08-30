# AO-0015 Information Sharing Frontier Explore Science closeout

## Purpose and intended outcome

Apply only evidence-backed clarifications and generated-asset repairs from the
owner-supplied Explore Science report to *When Does Information Sharing Improve
Decentralized Discovery?*. Produce a portable, deterministic, owner-gated arXiv
handoff. Create no new scientific evidence and stop before merge or submission.

## Current state

- Public `main` and `origin/main` resolve to
  `66ba4449572b20c519a4629ef20cfc030fae1762`.
- PRs #221 and #222 are merged. Exact-head CI run `33281789179` and Pages run
  `33281789183` succeeded. No substantive paper pull request is open.
- Issue #223 and branch
  `agent/information-sharing-frontier-explore-closeout` own AO-0015.
- The canonical 26-page PDF SHA-256 is
  `a317e8851a84b494d8ef30eccc1e31dd4448dc1bbcd3fb2de0fc2849bd581a13`;
  `main.tex` SHA-256 is
  `41cb86cb4ea4fc1221c3fb4c88a31418b2f5bff0fbc35777d9c895e35084982f`.
- The local 13-page owner-supplied Explore Science report has SHA-256
  `38da612da7f1889a219ae5c6cfd2db2a95190feb7cf94deb2d6815c62f7282de`.
  It reports 97/100 Platinum, zero major issues, 13 minor issues, and 37
  merits. Only ten issue details are printed; three online-only findings are
  unavailable and will not be guessed.

## DISCUSSION AND DECISION DELTA AUDIT

- Program memory was read before issue and branch registration.
- PM-0009 is due: Common-Source Trap is accepted on `main`, so Information
  Sharing Frontier is now the next live-readiness preprint candidate. This is
  internal routing, not publication authority.
- PM-0005, PM-0006, and PM-0007 remain implemented: this task prepares a
  preprint, pins public evidence, and keeps logical dependencies self-contained.
- PM-0010 remains deferred: no journal track, venue contact, or submission is
  authorized.
- The owner-supplied review is diagnostic input only. DD-019 through DD-022,
  the claim ledger, proofs, immutable outputs, and repository policy retain all
  manuscript and evidence authority.
- The first full-wall run exposed stale current-working-paper pointers in the
  lifecycle and citation registries after the PDF identity changed. Additive
  contract R2 authorizes only those exact current pointers and a regression;
  Compendium v0.1.0 and every historical release identity remain unchanged.

## Scope and boundaries

- Correct the report where repository evidence contradicts it: 511 chain
  starts explain the DD-020 accounting; evidence is publicly accessible; and
  independent verification means a separate implementation, not external
  replication.
- Accept bounded clarifications for the direct rule, parameter grids,
  by-accuracy gain counts, mechanism intervals, intermediate coverage values,
  and generated claim mappings.
- Defer the mixed-curve feasibility question as untested research.
- Package existing public immutable outputs without rerunning them.
- Preserve `working-paper`, `submitted: false`, `peer_reviewed: false`, DOI
  null, and owner-controlled category/license/upload decisions.

## Milestones

1. [x] Verify live GitHub state, source identities, program memory, and all 13
   review pages.
2. [x] Register issue #223, AO-0015 contract, plan, and task branch.
3. [x] Add focused regressions and open one draft PR.
4. [x] Apply the evidence-bounded manuscript/generator/disposition edits.
5. [x] Build and extract-test the deterministic arXiv source package.
6. [x] Rebuild twice, inspect every PDF page, and run focused/native checks.
7. [x] Run `make verify`, `make papers`, and `make site`; inspect the bounded
   six-file public artifact/pointer delta.
8. [ ] Await exact-head GitHub checks, freeze the live head, and stop at owner
   merge review.

## Restart instructions

Work only in the isolated checkout for branch
`agent/information-sharing-frontier-explore-closeout`. Reverify exact base/main,
issue #223, branch/PR identity, and a clean tree; resume from the first unchecked
milestone. Never infer authority for merge, upload, license selection, DOI,
release, or submission.
