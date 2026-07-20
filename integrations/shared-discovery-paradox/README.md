# Canonical upstream integration — DD-000

The Shared Discovery Paradox repository is canonical and read-only. `upstream.lock` pins commit `5025cc8e8f2f8ca015dff2066f08f81ad5715a51`, fetched into ignored `.cache/upstream/shared-discovery-paradox`; `upstream-requirements.lock` pins the reproduction environment. Store only provenance, additive fragments, and reviewable patches here. Never push upstream from this workspace.

Inspected source paths and SHA-256 values:

| Path | SHA-256 |
|---|---|
| `verify_shared_discovery_v8_6.py` | `83871228a6743acbcbce9e60806529108860b74bd43c62cc60addbc1eedd75d9` |
| `paper/The_Shared_Discovery_Paradox.tex` | `95503c4af1118727592fc55ce5ac660e8aba57973745d45751f13975887d2db0` |
| `docs/index.html` | `6662f3a70e3930841a05ca56bb8b4f0abf992f7b2e6e8a65e9917997d4636145` |
| `LICENSE` | `a38ea78f852a563f5172121b14a24f144e428b8a259d9e7179f8775e863ea021` |

The actual upstream verifier was executed by `make reproduce-baseline`. Its first two executions completed their research checks but exposed post-run provenance-wrapper defects; those operational failures are preserved and excluded from claim evidence. Run `20260720T190336Z_DD-000_32dd1c32_217c602fa0` completed the full wrapper and is the M1 evidence run.

## Additive paper extension

`patches/0001-distributed-discovery-additions.patch` is generated from the small source fragments in `papers/upstream-extension/fragments/`. Run `make upstream-patch` to fetch/check the pinned source, regenerate the patch, apply it in a disposable detached worktree, compile it with Tectonic 0.16.9, copy the review PDF and build log, and confirm that the canonical cache stayed clean.

The patch preserves the original title, abstract, theorem numbering, results, and conclusion. It adds a working definition, a reframed framework heading, the institutional matrix, two dictionary rows, suggested keywords, and a question-only research-program subsection. Source comments link these additions to existing ledger claims DD-C-0001, DD-C-0002, DD-C-0004, DD-C-0006, DD-C-0007, DD-C-0011, DD-C-0016, and DD-C-0017.
