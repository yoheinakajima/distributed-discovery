# Compendium v0.1.0 external publication plan

Status: **nonexecuting template**. None of these commands was run during offline
preparation. This plan does not authorize publication.

Official GitHub, Zenodo, and Citation File Format documentation was reviewed on
2026-07-24 UTC. GitHub represents an annotated tag as a tag object followed by
a tag reference, and release assets attach to a GitHub Release. Zenodo requires
the repository owner to enable the repository; a GitHub release then triggers
archiving. Zenodo publishes a version DOI for the exact record and a concept
DOI for the evolving work. `.zenodo.json` would take metadata precedence, so it
remains absent.

## 1. Validate owner authorization

Set `AUTHORIZATION_FILE` only to the owner-supplied file and do not infer it:

```sh
release_sha="$(git rev-parse HEAD)"
uv run --no-editable python scripts/validate_first_compendium_release_authorization.py \
  --authorization "${AUTHORIZATION_FILE}" \
  --source-revision "${release_sha}"
```

The real record must be active, match the exact commit, attest manuscript/PDF/
generated-figure licensing, allow the tag and GitHub Release operations, and
record owner-side Zenodo readiness. Synthetic fixtures are refused.

## 2. Generate final local assets

After the candidate PR is merged and `main` is synchronized:

```sh
git switch main
git pull --ff-only origin main
release_sha="$(git rev-parse HEAD)"
release_generated_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
uv run --no-editable python scripts/build_compendium_release.py \
  --version 0.1.0 \
  --source-revision "${release_sha}" \
  --output-dir build/compendium-release/0.1.0 \
  --mode release \
  --generated-utc "${release_generated_utc}" \
  --release-url "https://github.com/yoheinakajima/distributed-discovery/releases/tag/dd-compendium-v0.1.0" \
  --authorization "${AUTHORIZATION_FILE}"
uv run --no-editable python scripts/verify_compendium_release.py \
  --version 0.1.0 \
  --output-dir build/compendium-release/0.1.0
```

At this point DOI arguments remain absent because Zenodo has not yet published
them. Rebuild only after observed identifiers need to be recorded.

## 3. Create the annotated tag

Verify the tag is absent, then create and push it:

```sh
git tag --list dd-compendium-v0.1.0
git tag -a dd-compendium-v0.1.0 "${release_sha}" \
  -m "Distributed Discovery Research Compendium v0.1.0"
git show --no-patch --format=fuller dd-compendium-v0.1.0
git push origin refs/tags/dd-compendium-v0.1.0
```

Stop if the tag already exists or resolves to a different commit. Never move or
force-update the tag.

## 4. Create and verify the GitHub Release

Create the release with exactly the five verified files:

```sh
gh release create dd-compendium-v0.1.0 \
  build/compendium-release/0.1.0/distributed-discovery-compendium-v0.1.0-release-evidence-manifest.json \
  build/compendium-release/0.1.0/distributed-discovery-compendium-v0.1.0-SHA256SUMS.txt \
  build/compendium-release/0.1.0/distributed-discovery-compendium-v0.1.0-paper-citation-metadata.yml \
  build/compendium-release/0.1.0/distributed-discovery-compendium-v0.1.0-papers.zip \
  build/compendium-release/0.1.0/distributed-discovery-compendium-v0.1.0-release-notes.md \
  --repo yoheinakajima/distributed-discovery \
  --title "Distributed Discovery Research Compendium v0.1.0" \
  --notes-file docs/releases/compendium-v0.1.0-release-notes.md \
  --verify-tag
gh release view dd-compendium-v0.1.0 \
  --repo yoheinakajima/distributed-discovery \
  --json tagName,targetCommitish,name,isDraft,isPrerelease,url,assets
```

Download the published assets into a fresh verification directory and compare
them to `SHA256SUMS`. Do not edit or replace an immutable release artifact to
repair a mismatch; stop and record the discrepancy.

## 5. Verify Zenodo ingestion and metadata

The owner must first confirm that the canonical GitHub repository is enabled in
Zenodo. Poll the public record only after the GitHub Release exists:

```sh
curl --fail --silent --show-error \
  "https://zenodo.org/api/records?q=related.identifier:%22https://github.com/yoheinakajima/distributed-discovery%22&sort=newest"
```

Verify the exact title, creators, version, release date, repository relation,
license, description, files, and checksums in the returned published record.
Record the version DOI and concept DOI only from the published Zenodo response.
The version DOI identifies v0.1.0; the concept DOI identifies the evolving
compendium. If ingestion or metadata is absent or wrong, stop without inventing
an identifier.

## 6. Durable closeout

Create `plans/FIRST_COMPENDIUM_RELEASE.md` only in the later authorized task.
That closeout records the tag object, release URL and asset hashes, observed
Zenodo record and identifiers, CI/Pages state, and any discrepancy in a
documentation-only pull request. No package, arXiv, journal, provider, private
benchmark, or scientific-evidence action belongs in that task unless separately
authorized.
