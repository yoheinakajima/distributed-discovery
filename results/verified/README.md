# Verified results

Only claims meeting `docs/claim-status-policy.md` are indexed here.

DD-001 passing runs:

- `20260720T200124Z_DD-001_6eb12861_f9bcf73ec7`: initial 17-point exact grid and canonical search.
- `20260720T200245Z_DD-001_6eb12861_ba766d1eba`: expanded 21-point exact grid.
- `20260720T200447Z_DD-001_6eb12861_ba766d1eba`: primary complete run, adding the generated phase figure.
- `20260720T220911Z_DD-001_6822d4c6_40bf5b06a5`: preliminary signature audit; preserved, with its overstrong presentation key superseded.
- `20260720T221139Z_DD-001_b1d8d431_40bf5b06a5`: DD-001A primary signature run; all 21 tiny optima and tie counts independently reproduced, feasibility audited through M=5, and canonical signature counts independently certified.
- `20260720T223829Z_DD-001_b2cc23f4_5e16a90ad1`: DD-001B primary threshold run; exact three-family theorem audit, continuous unrestricted informative certificates for M=3,4,5, and anti-informative counterexamples.

Within each run, exact-grid optima have exhaustive certificates. Canonical coordinate-ascent values are constructive lower bounds only. The signature primary run certifies a lossless reduction and exact state-space counts, not a canonical private-team objective bound.

DD-002 passing runs:

- `20260720T225701Z_DD-002_a12ba3e8_e29b1460ae`: preliminary complete partition/equilibrium audit.
- `20260720T225848Z_DD-002_94607423_e29b1460ae`: primary run with independent selection-witness verification and corruption test.

The primary DD-002 run exhausts the declared deterministic partition lattice and verifies a selection-dependent reversal. Randomized disclosure is not implemented.
