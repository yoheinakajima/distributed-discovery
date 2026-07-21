# ADR-0017: DD-012 selective-attention census

DD-012 fixes a three-target access-gate model. Attention is chosen ex ante;
attending roles receive and follow the shared clue, while ignoring roles do not
receive it and follow private clues. This avoids treating an observed public
signal as something an agent can literally forget.

The primary grid uses `N=2,...,8` and
`p,q in {1/3,1/2,2/3,3/4,5/6}`: 175 parameter cells and 1,050 attention
profiles. Six strategic reward rules add 6,300 exact payoff rows; a seventh,
the public-reader license, is a binding access institution and therefore has no
voluntary-attention equilibrium. The direct verifier traverses 3,319,200
labeled target/shared/action-relevant-private states. It losslessly omits the
private clues of attenders because the frozen action rule cannot use them; the
unreduced count would be 18,820,350 states.

Exact closed-form binomial sums are primary. A separate labeled-state evaluator
must reproduce normalization, discovery, type payoffs, total payments,
deviations, equilibria, and optima and reject corrupted discovery, reward, and
equilibrium fields. The ten-minute/2-GB cap is far above the estimated
four-minute/256-MB requirement. No partial output supports claim promotion.

Reward results remain scoped to their exact registry and observability. In the
single-target atomic model, sole-rescue and marginal-coverage payments coincide;
this identity must be reported rather than hidden. The assigned-reader rule is
an external `1/N` stipend for every registered reader, while the license is a
binding delivery cap rather than a claim that voluntary inattention occurs.
