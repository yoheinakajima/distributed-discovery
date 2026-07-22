# Synthetic randomization v2

The registered generator assigns 32 synthetic IDs to each of 29 cells, balanced
equally across four pre-treatment blocks and grouped into sessions of eight.
Seed `111011` is fixed before the synthetic power calculation. Only `SYN-P` and
`SYN-S` identifiers are valid; the verifier rejects any real-looking identifier.

Random-reader identity, selected-audience membership, designated-reader
identity, and license assignment would be generated before clue realization in
any separately authorized protocol. This repository generates cell assignments
only. **No participants were recruited. No human data were collected. No
experiment was conducted.**

## Program V4 v3 extension

V3 uses seed `111012` to assign 32 synthetic IDs to each of 37 cells: 1,184
assignments in 148 sessions of eight, balanced equally across four blocks.
Threshold portfolio, history-visibility, and horizon fields are frozen before
simulation. The same identifier rejection and no-human-data rules apply.
