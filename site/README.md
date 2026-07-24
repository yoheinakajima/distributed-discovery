# Public research-library site

This dependency-light static site extends the canonical guide without altering or
copying its interactive sequence. Its five-item public navigation is Home,
Research, Results, Labs, and Papers; Foundations, Applications, Claims,
Evidence, Benchmark, Experiment Kit, Ideas, and the repository remain available
as contextual or footer resources. Legacy public routes remain available.

Run `make site`, then open `site/dist/index.html` for a local preview. The
builder validates `studies/*/public.yml` against the claim ledger, passing
immutable manifests, repository-relative public artifacts, and checksum-bound
publication PDFs. It emits route, research, per-study, claim, run, publication,
benchmark, experiment, and complete download-checksum JSON; download copies;
sitemap; robots policy; and an accessible 404 route. Only passed, public-safe
evidence summaries are generated.

The validator requires one H1, ordered heading levels, unique element IDs,
exactly one five-item global navigation, table captions, resolved internal
links/fragments, local runtime assets, no tracking, visible focus,
reduced-motion behavior, no-JavaScript fallbacks for interactive Labs, and
exact byte-length/SHA-256 coverage for every generated download. The public
surface contains no submission endpoint, account, cookie, analytics, or
server-side user data.

The Papers route uses the neutral `canonical-public-anchor` lifecycle term and
publishes stable-citation guidance plus the machine-readable paper-dependency
registry. The site remains a living discovery and verification layer: no
project release, DOI, arXiv identifier, submission, acceptance, or peer review
is claimed. Internal preprint sequencing and benchmark-name candidates are not
published on the site.

The current generated surface contains 81 HTML routes for 26 studies, 98 JSON
files (91 under `data/`), 201 total files, 18 Labs, and 23 checksum-covered
downloads. The contextual
`start-here.html` route presents the three-result reading path, `methods.html`
records the dry Phase 1 method, and `program.html` explains the theorem spine,
paper ownership, and centralized-versus-selected-equilibrium boundaries without
changing the five-item primary navigation or scientific inventory. The Program V5 Labs
select immutable exact DD-019 through DD-022 outputs. Exact static-complete Labs
never call a remote service or collect input.

The Program route records Phase 1 completion, the bounded Decentralized Recovery
classical-overlap stop, the Phase 2 theorem-execution hold, DiscoveryBench Agents
v1 as the next registration gate, and Reliable Discovery as a preserved later
theorem-family candidate. This wording adds no study, claim, run, Lab, data
file, or download.

PRs #155–#156 deployed the earlier paper-integrated surface and its mobile
correction. The Phase 2 generated Frontier download has editorial-only SHA-256
`a317e8851a84b494d8ef30eccc1e31dd4448dc1bbcd3fb2de0fc2849bd581a13`;
deployment acceptance is recorded separately after Pages succeeds.

GitHub Actions builds the same ignored `site/dist` artifact from `main` and
deploys it to <https://yoheinakajima.github.io/distributed-discovery/>. Never
commit generated output or add analytics, tracking, advertising, or external
telemetry. See `reports/site-browser-validation.md` for the bounded browser
validation protocol and results.
