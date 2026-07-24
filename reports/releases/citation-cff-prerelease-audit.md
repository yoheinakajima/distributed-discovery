# CITATION.cff pre-release audit

Decision: **`valid-prerelease-without-date-released-or-doi`**.

The CFF record remains compendium-level and type `software`. Version `0.1.0`
accurately identifies the repository's candidate version under the semantic
compendium policy, but `date-released` is omitted because CFF 1.2.0 defines it
as the date the software was released and no release exists. A future date must
not be guessed. DOI is absent. Repository, site, author, MIT repository license,
message, title, and abstract describe the compendium rather than a paper.

No `.zenodo.json` is added. Zenodo documents that this file takes metadata
precedence over citation metadata, so any future addition requires a deliberate
owner-approved metadata decision.

Official GitHub, Zenodo, and Citation File Format documentation was checked on
2026-07-24 UTC. This audit makes no claim that Zenodo integration is enabled.
