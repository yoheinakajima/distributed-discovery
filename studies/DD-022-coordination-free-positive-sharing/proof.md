# Exact equilibrium proof

All claims concern the frozen two-target, two-agent source mixture. Write
`t=2p-1` and `A=t^2+rho(1-t^2)`. Under sign coding, `t` is each signal's state
correlation and `A` is the two signals' correlation.

## Private information

If the peer follows their signal with probability `r`, direct conditioning on
either private signal gives the payoff difference
`D(r)=[3t+A(1-2r)]/4`. It is affine and decreasing. Thus the complete
equilibrium in the declared anonymous label-equivariant symmetric class is
`r*=1` when `A<=3t` and `r*=1/2+3t/(2A)` when `A>3t`. At equality, `r=1` is the
only symmetric fixed point. At `p=1/2,rho=0`, every `r` is an equilibrium and
the selected value is `1/2`; when `p=1/2,rho>0`, the unique value is `1/2`.
At `p=1`, the value is one; at `rho=0,p>1/2`, it is one; and at `rho=1`, it is
one for `p>=2/3` and `3p-1` otherwise.

For `k=2r-1`, exact expansion gives `Q_P=(1+tk)/2`,
`C_P=(1+Ak^2)/2`, and `G_P=(3+2tk-Ak^2)/4`. Diversity is `1-C_P`, expected
distinct actions is `2-C_P`, and total expected payoff is `G_P` because the
unit prize is split exactly among correct actors. Symmetry gives each agent
`G_P/2`.

## Shared information and selected posterior-only game

Agreement occurs with probability `(1+A)/2`; conditional on agreement, the
agreed label is correct with probability `u=1/2+t/(1+A)`. When disagreement
has positive probability its posterior is exactly `1/2`; at `A=1` it is off
path. If the peer chooses a posterior-favored target with probability `x`,
choosing high rather than low changes payoff by `(3u-1-x)/2`. The selected
identical-mixing equilibrium is `x=1` for `u>=2/3`, otherwise `x=3u-1`; at
disagreement the selected value is `1/2`. Conditional discovery is
`1-u+2ux-x^2`, quality is `1-u+(2u-1)x`, and collision is
`x^2+(1-x)^2`.

This is a selection theorem. Agents in the natural extensive form remember
signal ownership. On disagreement the label-equivariant symmetric rules
“follow my own signal” and “oppose my own signal” deterministically split
targets and are also equilibria. The posterior-only selection excludes this
ownership condition. No asymmetric role allocation is called
coordination-free.

## Canonical `p=3/5` threshold

Here `t=1/5` and `A=(1+24rho)/25`. The private boundary is `rho=7/12`; the
shared boundary is `rho=1/6`. The selected shared-minus-private discovery gain
is

```
-3(1-rho)/25                                      0 <= rho <= 1/6
3(24rho^2+17rho-16)/[25(13+12rho)]                1/6 < rho <= 7/12
9(1-rho)/[(13+12rho)(1+24rho)]                    7/12 < rho <= 1.
```

The quadratic has discriminant `1825=25*73`, exactly one positive root
`rho*=(5 sqrt(73)-17)/48`, and opposite signs at `2679/5000` and `67/125`.
Thus selected sharing strictly improves discovery, and each symmetric agent's
payoff, exactly for `rho in (rho*,1)`. Equality holds at `rho*` and `1`.

Direct private clue-following has `G_D=(21-6rho)/25`. The centralized
two-action value is one. The selected shared implementation gap is
`(7+3rho)/25` through `rho=1/6`, then `(4+3rho)/(13+12rho)`.

## Correspondence limitation

Constant opposite targets are private pure equilibria for every `rho` and
attain discovery one. Follow/follow occurs iff `rho<=7/12`; follow/oppose and
oppose/follow occur iff `rho>=7/12`. Therefore strict improvement does not
survive every equilibrium. This negative result fixes the theorem scope.
