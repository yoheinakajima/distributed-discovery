# Compendium v0.1.0 dry-run acceptance

Decision: **passed byte-identical double build**.

Two builds used source revision
`cdcc1d592e8a98969cc8666cd2161cda198bb89a`, fixed generated time
`2026-07-24T00:00:00Z`, mode `dry-run`, and separate fresh temporary output
directories. Each build generated exactly five assets. Both independent
verifier runs passed with 132 archive members, seven papers, and 119 pages.

The commands were:

```sh
uv run --no-editable python scripts/build_compendium_release.py \
  --version 0.1.0 \
  --source-revision cdcc1d592e8a98969cc8666cd2161cda198bb89a \
  --output-dir "${ACCEPTANCE_DIRECTORY}/first" \
  --mode dry-run \
  --generated-utc 2026-07-24T00:00:00Z
uv run --no-editable python scripts/build_compendium_release.py \
  --version 0.1.0 \
  --source-revision cdcc1d592e8a98969cc8666cd2161cda198bb89a \
  --output-dir "${ACCEPTANCE_DIRECTORY}/second" \
  --mode dry-run \
  --generated-utc 2026-07-24T00:00:00Z
diff -rq "${ACCEPTANCE_DIRECTORY}/first" "${ACCEPTANCE_DIRECTORY}/second"
```

## Resource measurements

The first build took 0.51 wall seconds, 0.17 user seconds, and 0.09 system
seconds with maximum resident set size 32,243,712 bytes. The second took 0.27
wall seconds, 0.17 user seconds, and 0.05 system seconds with maximum resident
set size 32,899,072 bytes.

## Asset acceptance

| Asset | Bytes | SHA-256 |
|---|---:|---|
| `distributed-discovery-compendium-v0.1.0-SHA256SUMS.txt` | 511 | `f38c1aa5ff44ee131d1ae246883c5ee7bb7a6fb6e097dc9d92affb01b000dd47` |
| `distributed-discovery-compendium-v0.1.0-paper-citation-metadata.yml` | 5,725 | `37c66ed19a9d84cc021eb27567fa74fd399b0f73b34b7aae845486c9420e538c` |
| `distributed-discovery-compendium-v0.1.0-papers.zip` | 1,088,601 | `08bab6f3d0fb7b1c6282b8663a11e1709ded0ee93769f7ee60fec690e01af469` |
| `distributed-discovery-compendium-v0.1.0-release-evidence-manifest.json` | 4,619 | `3ca70f603ff1c45394ef107c3bdb774e5d0d38d5ab5fdb3ffaae10331bfcd4e3` |
| `distributed-discovery-compendium-v0.1.0-release-notes.md` | 2,152 | `35d757da84ea3a5400db4e64963c3aee484029fe0e3da9c0c07fa54352128b92` |

Total size is 1,101,608 bytes. Every asset byte, digest, ZIP byte, manifest
byte, checksum byte, citation byte, and release-note byte matched. Differences:
none. No external mutation occurred.
