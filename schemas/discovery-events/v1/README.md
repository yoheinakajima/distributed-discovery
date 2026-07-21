# Discovery-event ontology v1

This versioned schema is exclusively for DD-007 synthetic recovery experiments.
`session.schema.json` is one session's registered context; `event.schema.json`
is a single actor action; `source.schema.json` is an available provenance unit.
All records require `synthetic: true`. `source_id: null` denotes intentionally
missing provenance, never an unknown real-world entity.

The schemas define data shape only. They do not identify copying, causal protocol
effects, or real-system quantities. Any real-data use requires a new data, ethics,
and identification review.
