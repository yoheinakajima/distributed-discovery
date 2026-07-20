# Local companion site

This dependency-light static companion extends the canonical guide without altering or copying its interactive sequence. It reuses the upstream visual language, adds “Beyond the Paradox,” and provides Foundations, Open Problems, and Applications pages.

Run `make site`, then open `site/dist/index.html` locally. The builder reads the latest passing canonical run and all study status/question files, emits provenance-bearing JSON, and validates internal links, semantic structure, resolved data markers, and the absence of tracking code. The source is public; the site is intentionally un-deployed.
