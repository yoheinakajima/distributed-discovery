# ADR-0013: DD-007 synthetic audit boundary

DD-007 uses only generated records marked `synthetic: true` under the versioned
`schemas/discovery-events/v1` ontology. Its recovery grid has four candidates,
two actors, 240 sessions per replicate, eight fixed seeds, copying rates 0, 1/2,
and 1, provenance missingness 0 and 1/2, and action-matching error 0 and 0.1.

The copying estimator is calibrated only against the known generator. It corrects
the independent-action agreement baseline for the shared latent target (`7/12`),
then reports a normal-approximation interval. DD-007 records calibration failure
under matching error and explicit action-only/provenance-only nonidentification
counterexamples. This ADR authorizes no real-data ingestion, empirical claim, or
causal interpretation.
