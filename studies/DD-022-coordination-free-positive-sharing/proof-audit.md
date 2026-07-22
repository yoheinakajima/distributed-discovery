# Independent proof audit

The analytic derivation is checked by a separate enumerator over target, both
signals, both actions, and every unilateral action deviation. It does not
import the closed-form equilibrium formulas.

The audit checks all 42 rational `(p,rho)` cells, all 16 labeled private pure
strategy profiles per cell with both players' signal types, and each on-path
public posterior game. It verifies source normalization, Bayes posteriors,
payoff budget balance, metric bounds, selected best responses,
closed-form/enumeration agreement, boundaries, pure correspondences, and the
quadratic root certificate.

Ten adversarial gates challenge the source-mixture probability, posterior,
private best response, shared support, polynomial, root interval, discovery,
equilibrium label, implementation gap, and source checksum.

The audit corrected two overstatements. Agreement only updates beliefs about
the latent common-source branch; it does not reveal that branch. Public
disagreement also permits signal-ownership-aware split equilibria, so the
theorem is explicitly about a posterior-only, provenance-blind identical-
mixing selection and not every shared equilibrium.
