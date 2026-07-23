# Equilibrium scopes and exploratory condition maps

These maps are hand-audited registration derivations. They are not promoted
claims or verified propositions.

## Simultaneous pure Nash

For distinct actions `(i,j)`, the profile is Nash exactly when

`mu_i >= max(mu_j/2, max_(k notin {i,j}) mu_k)`

and

`mu_j >= max(mu_i/2, max_(k notin {i,j}) mu_k)`.

A collision `(j,j)` is Nash exactly when

`mu_j/2 >= max_(k!=j) mu_k`.

These labeled inequalities are complete, including target ties and zero
masses. For generic `a>b>c`:

| Region | Complete pure outcomes | Best discovery | Worst discovery | Every-equilibrium top-two recovery |
| --- | --- | ---: | ---: | --- |
| `b>a/2` | the two label-orderings of the top-two split | `a+b` | `a+b` | yes |
| `b=a/2` | top-two split and top collision | `a+b` | `a` | no |
| `b<a/2` | top collision | `a` | `a` | no |

The exact potential is `Phi(n)=sum_j mu_j H_(n_j)`.

## Sequential pure SPE

After first action `j`, Agent 2 has best-response correspondence

`BR_2(j)=argmax({mu_j/2} union {mu_k:k!=j})`.

For any nodewise continuation `beta(j) in BR_2(j)`, Agent 1's continuation
payoff is `mu_j/2` if `beta(j)=j` and `mu_j` otherwise. The pure SPE set is
exactly every pair `(j,beta)` for which `beta` is nodewise optimal and `j`
maximizes Agent 1's continuation payoff. This formulation is complete at ties.

For generic `a>b>c`, the same three-region table above applies. At equality,
one continuation makes a top first action collide while another splits; the
first mover can also obtain the equality payoff by starting on target two.
Thus visible sequential occupancy does not enlarge the strict
every-equilibrium recovery region in the frozen candidate.

## Implementation labels

- `existence`: at least one equilibrium covers a top-two set.
- `best-equilibrium attainment`: best pure discovery equals `V_2^(2)`.
- `worst-equilibrium guarantee`: worst pure discovery equals `V_2^(2)`.
- `every-equilibrium implementation`: every pure outcome belongs to the
  centralized top-two correspondence.

No refinement or dynamic selection is claimed.
