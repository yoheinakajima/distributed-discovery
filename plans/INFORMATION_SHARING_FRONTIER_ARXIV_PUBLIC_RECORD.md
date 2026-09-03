# AO-0017 Information Sharing Frontier public arXiv metadata record

## Purpose and intended outcome

Record the already-public arXiv v1 metadata for *When Does Information Sharing
Improve Decentralized Discovery? Aggregation, Independent Rescue, and Equilibrium
Selection* in deterministic repository records and projections. This is a
metadata reconciliation only: the manuscript, canonical PDF, scientific claims,
studies, runs, evidence, and external arXiv record remain untouched.

## Current state

- Frozen DD `main`: `29264f89ab0f4dbd11b31b05faf36fdc1854bdff`.
- Canonical repository PDF:
  `papers/information-sharing-frontier/When_Does_Information_Sharing_Improve_Decentralized_Discovery.pdf`;
  28 pages; SHA-256
  `8d116b86cdbbc6cda66d65ac72077d29c15b05b86f4dc862ee8ec8e69d8f4ac0`.
- Sourced public record: arXiv `2609.01814`, v1 submitted
  `2026-09-01T19:41:30Z`, primary `cs.AI`, cross-list `cs.GT`, displayed DOI
  `10.48550/arXiv.2609.01814` with registration pending at observation, and the
  arXiv perpetual non-exclusive distribution license (not CC BY 4.0).
- Issue #228 and branch `agent/information-sharing-frontier-arxiv-record` own
  this metadata-only task. AO-0016 / issue #225 remain frozen Explore Science
  polish history and are not edited or reused.

## DISCUSSION AND DECISION DELTA AUDIT

- PM-0005 through PM-0007 remain implemented policy and provenance controls;
  they do not authorize a new external action. This task observes a completed
  public record rather than exercising submission authority.
- PM-0009's former Information Sharing Frontier preprint-candidate status is
  stale as a current fact. This task records public v1 metadata without starting
  any further preprint, journal, or research lane. PM-0010 remains deferred.
- The prior owner-upload package receipt remains historical immutable preparation
  evidence. A new sourced public-record receipt keeps the time boundary explicit.
- The arXiv source does not establish peer review, DOI registration/resolution,
  later moderation, or exact external-PDF byte identity. Those claims remain out
  of scope and are not inferred.

## Scope

Update only publication/citation/lifecycle/category/license/identifier metadata,
the source-package receipt semantics, associated tests/audits, and deterministic
site projections. Preserve `working-paper` editorial classification,
`peer_reviewed: false`, repository MIT source licensing, all 22 claim
authorities, DD-019 through DD-022 immutable evidence, and Compendium v0.1.0
artifacts/hashes exactly.

## Non-goals

No manuscript or PDF edit; no scientific object, claim, run, study, proof, or
evidence mutation; no arXiv edit/submission/withdrawal/license action; no DOI,
release, provider, credential, spend, merge, undraft, deployment, or branch
deletion.

## Milestones

1. [x] Reverify exact remote main, canonical PDF identity, public arXiv facts,
   and no target-purpose collision.
2. [x] Create issue #228, fixed task contract, branch, and this living ExecPlan.
3. [x] Record canonical publication metadata and a separate public-record receipt.
4. [x] Regenerate deterministic package/site projections and run focused audits.
5. [x] Run the full non-executing validation wall: lint, strict typing, 1,101
   tests, claim/run validation, editorial/program-memory/Agent Ops/publication
   audits, release/Compendium verification, all-paper build, and site build.
6. [x] Open draft PR #229 and stop at exact-head owner merge review.

## Validation strategy

Run YAML/schema validation, focused Information Sharing Frontier metadata,
package, pointer, publication-audit, and site tests; rebuild the portable source
package twice; run `make verify`, `make papers`, and `make site`; compare the
canonical manuscript/PDF/claims/runs/evidence and frozen Compendium files before
and after. Render and inspect the unchanged 28-page canonical PDF while checking
that only public metadata projections change.

## Blockers

- None at registration. Stop on public-record mismatch, any canonical artifact
  drift, target-purpose collision, nondeterminism, validation failure, or a
  requested change that exceeds metadata reconciliation.

## Outcome and retrospective

- The canonical manuscript remains SHA-256
  `b7a6489bc96acbfbfa6fe57cf20fdf97d25e81fe62bf2e250d985291afcb2688`; the
  28-page canonical PDF remains SHA-256
  `8d116b86cdbbc6cda66d65ac72077d29c15b05b86f4dc862ee8ec8e69d8f4ac0`.
- The historical source archive remains byte-identical at SHA-256
  `02c2090e239a8799fc751bee1b20074991502616f2053140b127a867228612e2`.
  The rebuilt public-record manifest, metadata, and receipt checklist have
  SHA-256 `98660b1b73d244dc8d74040d4ccf73cf32f84875ded1629c2a82d867f1994a92`,
  `56d8cf9842c5512b17571c23d2c47add80458076c10fc3bf980474bd329c79f7`, and
  `6b43330e0d41a0991071cc391aa43623dd7bdc6910fa80810daf02619aef8307`.
- All 28 rendered PDF pages were visually inspected as an unchanged-layout
  contact sheet. The only paper-build-derived updates are two current
  provenance `source_commit` pointers from the prior accepted main to
  `29264f89ab0f4dbd11b31b05faf36fdc1854bdff`, plus correction of the stale
  `paper-audit.json` PDF hash to the same unchanged canonical PDF identity.
  Immutable DD-019--DD-022 outputs, all 22 claim authorities, and Compendium
  v0.1.0 bytes are unchanged.
- `main.tex` and the unchanged canonical PDF retain their frozen pre-submission
  wording. That manuscript content is not treated as current publication
  metadata; the current canonical metadata surfaces and this receipt record the
  public arXiv v1 fact instead.
- The Information Sharing generator derives its source-provenance commit from
  the paper's explicit accepted-content binding, not mutable branch HEAD. Two
  paper-target rebuilds retain that frozen content commit while the paper source
  and PDF hashes remain unchanged.

## Recovery and restart instructions

Reverify `main`, issue #228, the public arXiv facts, canonical PDF hash/page
count, and collision state before continuing. Do not reuse issue #225 or infer
external authority from the public record or from a later merge.
