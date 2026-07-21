# Exact canonical pooled frontier

## Outcome

Primary immutable run
`20260721T012208Z_DD-000_8e4b55e2_e8321d1048` certifies the complete canonical
pooled frontier for budgets one through eight. It started from clean commit
`8e4b55e2e2cf33c69e3605dccf6ceec9c3dba8d4`, used no randomness, finished in
8.29 seconds inside its 30-second budget, and passed every validation condition.

| Budget | Exact pooled discovery | Decimal |
|---:|---:|---:|
| 1 | `37916217637/98876953125` | 0.3834687097312395 |
| 2 | `528127925854561/1001129150390625` | 0.5275322625941855 |
| 3 | `605210407502177/1001129150390625` | 0.6045278046953616 |
| 4 | `223779310319051/333709716796875` | 0.6705807444476144 |
| 5 | `736434813280609/1001129150390625` | 0.7356042055046180 |
| 6 | `159066470090413/200225830078125` | 0.7944353135074917 |
| 7 | `92994931014809/111236572265625` | 0.8360103976661897 |
| 8 | `860391662035297/1001129150390625` | 0.8594212461994395 |

The exact recovery budget remains seven.

## Independent methods

Method A exhausts all `C(23,15)=490314` labeled count vectors conditional on a
fixed target. Method B independently exhausts 67 target-count/false-count-
histogram orbits with exact multiplicities. Both masses equal one exactly and the
reduced frontier fractions agree at every budget. A third implementation traverses
decreasing integer partitions, recomputes every value, and rejects a certificate
whose last numerator is incremented by one.

The run records the configuration, code and lock hashes, environment, formulas,
state counts, timings, validation flags, output hashes, and reproduction command.
Claim checks DD-C-0006, DD-C-0008, DD-C-0035, and DD-C-0036 follow every evidence
path.

## DD-001 consequence

Direct clue-following remains a feasible exact lower bound, while pooled
observation plus conditional top-eight assignment upper-bounds every emulated
zero-communication role profile. Therefore

```text
325089/390625
  <= T_8(16,1/5)
  <= 860391662035297/1001129150390625.
```

The exact gap is `27224111644672/1001129150390625`, approximately
`0.0271934061994395`. This is a valid interval under the frozen emulation
assumptions. The pooled endpoint is not claimed attainable by a private team, and
the private-team optimum and interval tightness remain unresolved.
