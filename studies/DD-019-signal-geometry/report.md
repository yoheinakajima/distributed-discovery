# DD-019 bounded exact report

Primary run `20260722T084145Z_DD-019_a77bb786_04a5e9f0c5` passed from clean
source commit `a77bb786` in the frozen `M=4`, `N=3` fixture. Labeled
signal-profile enumeration and independent histogram enumeration agree exactly
for all five channels and all three action budgets. Three registered
corruptions are rejected.

| Channel | One-person accuracy | Private portfolio | `(V1,V2,V3)` | Recovery `L*` |
| --- | ---: | ---: | --- | ---: |
| Noisy point, `q=1/2` | `1/2` | `7/8` | `(7/12,43/54,25/27)` | 3 |
| Noisy two-shortlist, `a=3/4` | `3/8` | `387/512` | `(35/64,79/96,539/576)` | 2 |
| Guaranteed two-shortlist | `1/2` | `7/8` | `(17/18,1,1)` | 1 |
| Explicit exclusion | `1/3` | `19/27` | `(16/27,26/27,1)` | 2 |
| Confidence point | `5/8` | `485/512` | `(295/384,175/192,31/32)` | 3 |

The noisy point and guaranteed-shortlist channels have the same one-person
Bayes accuracy and the same named direct private-portfolio discovery, but every
entry of their pooled profile differs. Thus one-person accuracy (equivalently,
expected posterior maximum here) does not determine the complete bounded
profile. This is an exact counterexample to that scalar's sufficiency, not a
claim about mutual information, entropy reduction, likelihood ratios, or every
possible scalar.

The registered recovery budget is baseline-specific. The guaranteed shortlist
already exceeds `7/8` with one pooled action (`17/18`), while the noisy point
requires three (`25/27`; its first two values are below `7/8`). These results do
not establish an unrestricted anonymous-private optimum, strategic result,
general theorem, or canonical `M=16,N=8` result.
