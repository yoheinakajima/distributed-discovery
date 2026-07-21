# DD-014 proof record

## Restricted-class completeness

Fix three labels and require a deterministic policy to respect agreement and
commute with every relabeling. Agreement inputs form one orbit and must return
their common label. Ordered disagreement inputs also form one orbit. The
stabilizer of a representative disagreement pair fixes exactly three possible
outputs: its private label, its shared label, or the remaining label. Therefore
the registered class contains exactly the private-dominant, public-dominant,
and third-option contrarian policies. This is a completeness statement only for
the declared agreement-respecting, deterministic, label-equivariant class.

## Unconditional embedding

Private-dominant reproduces unconditional private use and public-dominant
reproduces unconditional shared use. Profiles with zero contrarians therefore
embed the DD-012 unconditional class without changing its target or signal
law. Adding contrarian roles weakly expands the planner's feasible set.

Write a role profile as `(a,b,c)` for private-dominant, public-dominant, and
contrarian counts. Conditioning on whether the shared clue is correct gives
the exact failure probability

`q(1-p)^(a+c) + (1-q)(1-p)^a((1+p)/2)^c` when `b=0`, and

`(1-q)(1-p)^a((1+p)/2)^c` when `b>=1`.

For `p>=1/3`, replacing a contrarian with a private-dominant role weakly lowers
failure because `1-p <= (1+p)/2`, strictly when `p>1/3`. The DD-012 one-reader
classification then applies after setting `c=0`. Thus for `p>1/3`, the optimum
has `(a,b,c)=(N-1,1,0)` when `q>p`, `(N,0,0)` when `q<p`, and either of those
two profiles when `q=p`. At `p=1/3`, contrarian and private-dominant roles tie:
when `q>p`, exactly one role is public-dominant and every split of the remaining
roles is optimal; at `q=p=1/3`, zero or one public-dominant roles and every
remaining split are optimal. This proves that conditional roles do not improve
the unconditional planner optimum on the registered grid.

## Larger-class audit

The registered raw audit separately enumerates all sixteen deterministic
two-label policy tables for two ordered agents. It is not used to prove the
three-label restricted theorem. Its purpose is adversarial: it can expose
conclusions that fail outside the declared class. In particular, complementary
constant policies cover both two-label targets with discovery probability one,
showing why the restricted-class boundary must remain explicit.
