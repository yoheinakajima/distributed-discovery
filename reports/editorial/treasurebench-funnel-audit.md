# TreasureBench/Treasure Hunt funnel audit

Audit date: 2026-07-23 PDT.

Status: **pass locally; live Pages acceptance pending merge**.

The machine audit in `scripts/audit_treasurebench_naming.py` builds the complete
static site and verifies both directions of the required naming funnel:

- `treasure-hunt.html` visibly states “The playable companion to the
  TreasureBench suite.” and links directly to `treasurebench.html`;
- the opening material on `treasurebench.html` names and links Treasure Hunt as
  the interactive playable companion;
- the README and announcement-copy template pair both names in their opening
  material;
- structured naming JSON identifies TreasureBench as `formal-instrument` and
  Treasure Hunt as `interactive-companion`;
- Treasure Hunt is explicitly not a separate benchmark;
- the five companion modules retain adjacent formal terms, evidence ownership,
  and limitations;
- a complete no-JavaScript explanation and exact fallback tables are present.

The same audit verifies that Treasure Hunt does not enter claims, frozen task
schemas, formal metric/schema namespaces, run IDs, or theorem names. It also
checks the canonical subtitle, required keywords, old/new routes, historical
JSON endpoints, route-alias registry, frozen schema hashes, and prohibited
Shared-family artifact names.

This is a naming, presentation, and compatibility audit. It is not scientific
evidence, user research, legal review, or external validation.
