# Registered synthetic audit model

ADR-0013 fixes a synthetic-only two-actor, four-candidate generator with a
shared latent target, copying, partial source provenance, and action-matching
error. It records versioned session, event, and source objects, then estimates
copying from pair agreement after correcting for shared-target agreement.
Identification counterexamples remain part of the result, rather than being
treated as a failed implementation detail.
