# Lifecycle terminology audit

The former current value `canonical-published` was locally defined as an
owner-declared public anchor, but its ordinary reading could imply formal
publication. That reading conflicts with the pinned upstream working-paper
citation and the absence of submission, acceptance, journal, peer-review, or
DOI evidence.

Current registries, schema, validators, tests, and public presentation now use
`canonical-public-anchor`. The migration changes no scientific status, route,
citation, checksum, upstream lock, or edit authority. Historical plans retain
the old spelling as evidence of the decision path; the machine-readable
decision maps it to the current value.
