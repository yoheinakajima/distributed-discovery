# Public companion site

This dependency-light static companion extends the canonical guide without altering or copying its interactive sequence. It reuses the upstream visual language, adds “Beyond the Paradox,” and provides Foundations, Results, Open Problems, and Applications pages.

Run `make site`, then open `site/dist/index.html` for a local preview. The builder reads the latest passing canonical run and all study status/question files, emits provenance-bearing JSON, and validates internal links, semantic structure, resolved data markers, and the absence of tracking code.

GitHub Actions builds the same ignored `site/dist` artifact from `main` and deploys it to <https://yoheinakajima.github.io/distributed-discovery/>. Never commit generated output or add analytics, tracking, advertising, or external telemetry.
