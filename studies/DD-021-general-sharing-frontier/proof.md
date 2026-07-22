# Analytic proof record

This record works only under `model.md`. It recovers DD-020's identity with
explicit attribution, derives the new frontier criterion, and proves the
centralized full-capacity result. It does not prove decentralized
implementation or an unrestricted information-structure theorem.

## Definitions

Let `q` be the constant target-conditional success probability of the declared
direct rule. Let `C_s` be accuracy of one uniformly tie-broken pooled posterior
MAP action from `s` signals, and let `G_s` be discovery from that block action
plus `N-s` remaining direct actions. Define pooled MAP error `e_s=1-C_s`.

After all `N` signals, let `V_L` be expected posterior mass of a set of at most
`L` distinct atomic target actions chosen by a centralized pooled planner. Let
`P_N` be discovery from the `N` declared direct private actions, including
their independent tie randomization.

## Recovered identity — aggregation and independent rescue

DD-020 (DD-C-0092) proves

`G_s = 1-(1-C_s)(1-q)^(N-s)`.

Conditional on the target, the block and remaining direct actions depend on
disjoint independent signal and tie-randomization sources. Thus group failure
has probability `(1-C_s)(1-q)^(N-s)`. This statement is recovered here, not
claimed as a new DD-021 result.

Subtracting adjacent terms gives

`G_(s+1)-G_s`

`= (1-q)^(N-s-1)[C_(s+1)-C_s-q(1-C_s)]`

`= (1-q)^(N-s-1)[(1-q)e_s-e_(s+1)]`.

## Theorem — Independent-Rescue Error-Contraction Criterion

For every adjacent step `s=1,...,N-1` in the frozen protocol:

- sharing helps exactly when `e_(s+1)<(1-q)e_s`;
- sharing is neutral exactly when `e_(s+1)=(1-q)e_s`;
- sharing hurts exactly when `e_(s+1)>(1-q)e_s`.

When `e_s>0`, define `rho_s=e_(s+1)/e_s`. Then sharing helps, is neutral, or
hurts exactly when `rho_s` is respectively below, equal to, or above `1-q`.

**Proof.** The multiplier `(1-q)^(N-s-1)` in the adjacent identity is
nonnegative. If it is positive, the sign is exactly the sign of
`(1-q)e_s-e_(s+1)`, yielding all three equivalences. If the multiplier is zero,
then `q=1` and at least one direct action is perfect before the terminal step.
Target-equivariance and perfect direct accuracy imply that one signal identifies
the target through its direct action, so `C_s=C_(s+1)=1`; both sides are zero
and the neutral equality holds. Division by positive `e_s` gives the ratio
form. When `e_s=0`, expected MAP accuracy cannot fall after another conditionally
independent observation (the old decision rule remains feasible), so
`e_(s+1)=0`; the step is neutral and `rho_s` is intentionally undefined. ∎

The criterion is exact and tight as an accounting equivalence. It is not a
bound on `rho_s`, a Chernoff exponent, a strong data-processing coefficient,
or a claim that arbitrary channels lie on one side of the threshold.

## Sharing-curve and consensus classifications

For exclusive registry counting, a profile is:

- **strict compression-dominated** if every adjacent increment is nonpositive
  and at least one is negative;
- **strict aggregation-dominated** if every increment is nonnegative and at
  least one is positive;
- **all-neutral** if every increment is zero;
- **mixed** otherwise.

The full-sharing value `C_N` is separately:

- **strict no one-action aggregation gain** when `C_N<q`;
- **Shared Discovery Paradox** when `q<C_N<P_N`;
- **strict aggregation-dominated consensus** when `C_N>P_N`;
- **boundary** when `C_N=q` or `C_N=P_N`.

The weak verbal classes requested by the study are recovered by adjoining the
all-neutral or equality boundary as stated. These two classification axes are
not logically equivalent.

## Theorem — full-capacity pooled-planner dominance

Under the frozen atomic action technology and centralized authority,

`V_min(N,M)^(N) >= P_N`.

Consequently the recovery budget exists and satisfies
`1<=L*<=min(N,M)`. Moreover, under the same posterior and tie conventions,

`L*=1` if and only if `C_N>=P_N`.

**Proof.** Fix a complete signal profile and let `pi` be its posterior over the
`M` targets. Also fix any realization of all private tie draws. The union `U`
of the `N` direct actions contains at most `min(N,M)` distinct targets;
duplicates only reduce its cardinality. Conditional discovery from this
realized direct portfolio is `pi(U)`.

Let `L=min(N,M)`. A set of the `L` largest posterior masses maximizes `pi(A)`
over all target sets with cardinality at most `L`. Therefore its mass is at
least `pi(U)` for every private tie realization. A tie at the `L`th posterior
rank does not alter the summed mass, and when `N>M`, `L=M` gives mass one.
Average first over private tie draws and then over signal profiles. The left
side becomes `V_L`; the right side becomes `P_N`, proving dominance.

Monotonicity of `V_L` and full-capacity dominance make the defining set for
`L*` nonempty. Finally `V_1=C_N`: both are expected posterior maximum, and a
uniform MAP tie selects targets with the same posterior mass. Hence `L*=1`
exactly when `C_N>=P_N`. ∎

The planner need not observe or reproduce private tie seeds. Pointwise
dominance holds for every possible realized direct-action union, so averaging
is sufficient. The theorem supplies an information-and-authority benchmark;
it gives no decentralized protocol for implementing the top-`L` set.
