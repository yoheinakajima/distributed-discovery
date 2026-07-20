# DD-000 report

## Evidence summary

DD-000 now has a pinned and successfully executed canonical reproduction, independent checks for the simplest finite-model quantities, a formal foundations layer, and a compiled additive upstream-paper patch. The canonical evidence run is `20260720T190336Z_DD-000_32dd1c32_217c602fa0`; see `reports/baseline-reproduction.md` for exact status distinctions. Market equilibrium and copying-crossover values are verified upstream computations, not independent local derivations.

## M3 paper extension

The extension preserves the original paper as the primary concise account. It adds a working definition of distributed discovery, reframes the existing frontier/loss section, exposes the information/assignment matrix and missing private-team cell, extends the existing dictionary, and poses DD-001 through DD-007 as questions. Source comments connect the additions to ledger claims; no new empirical or theorem claim is introduced.

The generated patch applies to pinned commit `5025cc8e8f2f8ca015dff2066f08f81ad5715a51` and compiles to a 30-page preview with Tectonic 0.16.9. The canonical cache remained clean. Visual review found no defects in the inserted material. The exact placement rationale and reviewer-risk analysis are in `papers/upstream-extension/change-memo.md`.

## M4 private companion site

The local site preserves the canonical guide as the primary six-minute explanation and appends a “Beyond the Paradox” research-program entry point. Foundations, Open Problems, and Applications pages use the pinned guide’s lightweight visual language without copying its interactive sequence. Benchmark statements are generated from the passing canonical run, while study cards are generated from registry question/status files and label every DD-001 through DD-007 direction as open.

`make site` builds four pages and provenance data, then validates internal links, semantic landmarks and heading order, resolved data markers, and tracking absence. Integration tests also verify generated content and primary light/dark text contrast. The output remains private and un-deployed.
