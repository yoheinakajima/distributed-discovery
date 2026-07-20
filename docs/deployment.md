# GitHub Pages deployment

The public companion is served at <https://yoheinakajima.github.io/distributed-discovery/>. Source templates live in `site/src`. `make site` validates the repository evidence and generates the four-page artifact plus provenance data in ignored `site/dist`.

`.github/workflows/pages.yml` is the sole deployment path. Pushes to `main` and manual dispatches run the locked bootstrap, routine verification, and site build; the official Pages artifact action uploads `site/dist`; the deploy job publishes through the `github-pages` environment. Pull requests never deploy to production, and generated site files are not committed.

After any site-facing merge, inspect the workflow conclusion and smoke-test:

- `/distributed-discovery/`
- `/distributed-discovery/foundations.html`
- `/distributed-discovery/open-problems.html`
- `/distributed-discovery/applications.html`
- `/distributed-discovery/data/canonical.json`

The site contains no analytics, tracking, advertising, or external telemetry. Canonical upstream remains the primary interactive explanation and is linked from the companion home page.
