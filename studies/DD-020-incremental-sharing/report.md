# DD-020 exact report

Primary run `20260722T142551Z_DD-020_3854fff6_37c11a850a` passed from clean
source commit `3854fff6` in 2.428850 seconds, below the registered 120-second
cap. It preserves 2,555 point-protocol rows across 73 `(M,p)` cells and all
five DD-019 channel extensions. Full count-vector enumeration and the
independent correct-count/wrong-occupancy dynamic program agree exactly.

## Analytic result

For the registered target-symmetric protocol,

`G_s = 1-(1-C_s)(1-q)^(N-s)`

and the adjacent difference separates marginal aggregation from lost rescue:

`G_(s+1)-G_s = (1-q)^(N-s-1)[C_(s+1)-C_s-q(1-C_s)]`.

For every finite informative symmetric noisy-point channel (`q=p`), absorbing
one more direct searcher into the one-action pooled block weakly lowers group
discovery. The loss is strict for `p<1` and becomes equality at `p=1`. The
proof is in `proof.md`; `proof-audit.md` separately checks the conditioning,
MAP-containment, strictness, boundary, and scope obligations. Computation is a
regression for this theorem, not its proof.

In the two-agent case, `C_2=p` for every finite `M`, so private discovery is
`1-(1-p)^2`, pooled consensus is `p`, and the exact change is `-p(1-p)`.

## Bounded point census

The registered census contains 2,044 adjacent increments: 1,848 are strictly
negative, 196 are zero, and none are positive. Every zero belongs to a
perfect-signal `p=1` row. This finite count is an independently reproduced
bounded result; the analytic theorem supplies the general statement.

## Five-channel extension

Here `s=1` is the three-private-action baseline and `s=3` is one pooled
consensus action duplicated three times.

| DD-019 channel | Direct rule | One-person accuracy | `(G_1,G_2,G_3)` | Increment signs |
| --- | --- | ---: | --- | --- |
| Noisy point | nominated point | `1/2` | `(7/8,3/4,7/12)` | `-,-` |
| Noisy two-shortlist | uniform posterior MAP | `3/8` | `(387/512,11/16,35/64)` | `-,-` |
| Guaranteed two-shortlist | uniform over the observed pair | `1/2` | `(7/8,11/12,17/18)` | `+,+` |
| Explicit exclusion | uniform over nonexcluded targets | `1/3` | `(19/27,17/27,16/27)` | `-,-` |
| Confidence point | nominated point using confidence likelihood | `5/8` | `(485/512,113/128,295/384)` | `-,-` |

For each channel, sources are conditionally independent, the direct rule has
constant target-conditional accuracy, the block takes one uniformly
tie-broken posterior-MAP action, and the remaining agents retain their direct
actions. The exact labeled-sequence and histogram methods agree on every
pooled accuracy and discovery value.

The half-accurate noisy-point and guaranteed-shortlist channels begin at the
same private discovery `7/8` but then move in opposite directions. One-person
accuracy therefore does not determine this bounded incremental-sharing
profile or even its sign. This does not establish a general channel order.

## Negative and limiting evidence

- The point-channel search found no positive increment; the proof explains
  why none can occur in the declared class.
- Four of five DD-019 channels decrease, but the guaranteed shortlist rises;
  arbitrary-channel monotonicity is therefore false.
- No private-team optimum, strategic reward, assignment, pooled top-`L`
  portfolio, anti-informative signal, human data, or real data is analyzed.
- No first-discovery or field-novelty claim is made; `literature.md` records
  the adjacent scholarly ownership.

