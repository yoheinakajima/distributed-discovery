# Research-library site audit

Audit date: 2026-07-20 UTC. Scope: the public-site source at commit
`a3b1f760ff6b4d3d580696e537e5d3f45caf1ed3` before the research-library work.

## Baseline

The existing dependency-light site has five pages: home, Foundations, Results,
Open Problems, and Applications. It accurately presents the canonical benchmark
and three completed bounded extensions, but it is a companion narrative rather
than a browsable research library. The generated data contract has canonical,
studies, results, and a copied claim ledger only; it has no per-study public
metadata, evidence catalogue, publication catalogue, route registry, or public
artifact policy.

## Material gaps

- DD-000 through DD-003 have validated results but no dedicated study routes;
  DD-004 through DD-007 are only indistinguishable open-problem cards.
- Claim status, exact scope, source run, and provenance cannot be browsed as a
  linked inventory.
- Passed run manifests are validated in the repository but are not exposed as a
  safe public evidence index. Raw outputs and failed/preliminary runs have no
  explicit public-safety policy.
- The two generated PDFs have no downloads page, checksum, page-count, build
  source, or citation metadata in the site.
- Navigation does not provide the requested Foundations / Research / Results /
  Publications hierarchy or a claims/evidence secondary path.
- No route registry protects legacy paths, fragment links, download checksums,
  or generated research-data endpoints.
- The old static open-problems framing cannot distinguish completed bounded
  studies, active extensions, registered questions, and queued work.

## Design response and boundaries

The replacement is still a static, no-tracking site. `public.yml` records are
validated against the claim ledger, passing manifests, and repository-relative
paths before generation. The builder emits summaries and checksums rather than
copying raw run outputs. Publication PDFs are copied only from validated paper
artifacts. Failed/preliminary material is excluded from substantive evidence.
Legacy pages remain routes. Site tests validate generated navigation, metadata,
links, claims, manifests, downloads, and route declarations; a later bounded
browser layer will exercise the deployed behavior.
