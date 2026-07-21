# Public research-library site

This dependency-light static site extends the canonical guide without altering or
copying its interactive sequence. It exposes Foundations, Research, Results,
Publications, Applications, Claims, Evidence, Open Questions, and a clearly
separate Ideas Incubator. Legacy public routes remain available.

Run `make site`, then open `site/dist/index.html` for a local preview. The
builder validates `studies/*/public.yml` against the claim ledger, passing
immutable manifests, repository-relative public artifacts, and checksum-bound
publication PDFs. It emits route, research, per-study, claim, run, publication,
benchmark, experiment, and complete download-checksum JSON; download copies;
sitemap; robots policy; and an accessible 404 route. Only passed, public-safe
evidence summaries are generated.

The validator requires one H1, ordered heading levels, unique element IDs,
resolved internal links/fragments, local runtime assets, no tracking, visible
focus, reduced-motion behavior, no-JavaScript fallbacks for interactive Labs,
and exact byte-length/SHA-256 coverage for every generated download. The public
surface contains no submission endpoint, account, cookie, analytics, or
server-side user data.

GitHub Actions builds the same ignored `site/dist` artifact from `main` and
deploys it to <https://yoheinakajima.github.io/distributed-discovery/>. Never
commit generated output or add analytics, tracking, advertising, or external
telemetry. See `reports/site-browser-validation.md` for the bounded browser
validation protocol and results.
