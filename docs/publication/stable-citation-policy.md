# Stable citation policy

A load-bearing scientific citation resolves to an immutable object: a specific
arXiv version, a version-specific repository release DOI, a formally published
version, or a tagged repository release with an immutable evidence manifest.
The living site may support discovery and verification but is not sufficient
by itself.

Compendium v0.1.0 is published and verified. For exact reproduction, cite
version DOI [`10.5281/zenodo.21535005`](https://doi.org/10.5281/zenodo.21535005).
For the evolving Distributed Discovery compendium, cite concept DOI
[`10.5281/zenodo.21535004`](https://doi.org/10.5281/zenodo.21535004). The
immutable Git source and five custom release assets are available from
[`dd-compendium-v0.1.0`](https://github.com/yoheinakajima/distributed-discovery/releases/tag/dd-compendium-v0.1.0).

Preferred evidence citation fields are:

1. paper-specific arXiv version when real;
2. version-specific compendium release DOI when real;
3. claim ID;
4. immutable run ID for generated evidence;
5. file checksum when the file is load-bearing.

Use a concept/latest DOI only when the citation intentionally means the
evolving compendium. Never fabricate a DOI, arXiv identifier, release tag, or
realistic-looking placeholder. For objects without their own identifier, store
`null` and cite the current working-paper metadata plus the real compendium
version DOI, claim/run provenance, and checksum.

Example for a load-bearing v0.1.0 citation:

> Nakajima (2026), *paper title*, working paper; Distributed Discovery
> Research Compendium v0.1.0, doi:10.5281/zenodo.21535005; claim:
> `DD-C-xxxx`; immutable run: `YYYY...`; artifact SHA-256:
> `<computed checksum>`.

The symbolic values above are field descriptions, not reserved identifiers.
Root `CITATION.cff` remains the compendium citation. Per-paper metadata is
separate.

For formal benchmark references, use **TreasureBench: A Benchmark for
Collective Search under Shared and Private Evidence**. The first section must
pair the formal name with Treasure Hunt as the playable companion. Historical
DiscoveryBench strings may be cited only when a frozen schema, path, protocol,
or dated record requires them. The compendium DOI identifies the repository
archive; it is not a paper-specific or standalone TreasureBench package DOI.
No standalone package or arXiv identifier exists.
