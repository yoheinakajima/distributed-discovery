# Design model

The candidate full factorial has `3 × 2 × 3 × 2 × 5 = 180` cells. The selected
contrast-complete fractional design has 20 cells and identifies the eight frozen
contrasts while leaving unregistered higher-order interactions aliased. Assignment
is blocked across four synthetic strata, clustered in sessions of eight, and uses
opaque `SYN-*` identifiers.

Power is a conditional Monte Carlo calculation under eight explicitly versioned
response scenarios. It simulates treatment-effect estimates from their registered
sampling distributions, applies conservative familywise alpha, and reports Wilson
intervals for Monte Carlo power. These response models are not empirical models of
people.
