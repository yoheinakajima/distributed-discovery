# Public research-library site

This dependency-light static site extends the canonical guide without altering or
copying its interactive sequence. It exposes Foundations, Research, Results,
Publications, Applications, Claims, Evidence, Open Questions, and a clearly
separate Ideas Incubator. Legacy public routes remain available.

Run `make site`, then open `site/dist/index.html` for a local preview. The
builder validates `studies/*/public.yml` against the claim ledger, passing
immutable manifests, repository-relative public artifacts, and checksum-bound
publication PDFs. It emits route, research, per-study, claim, run, and
publication JSON; download copies; sitemap; robots policy; and an accessible
404 route. Only passed, public-safe evidence summaries are generated.

GitHub Actions builds the same ignored `site/dist` artifact from `main` and
deploys it to <https://yoheinakajima.github.io/distributed-discovery/>. Never
commit generated output or add analytics, tracking, advertising, or external
telemetry. See `reports/site-browser-validation.md` for the bounded browser
validation protocol and results.
