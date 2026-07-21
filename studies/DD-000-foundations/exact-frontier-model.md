# Exact canonical pooled-frontier model

## Frozen instance

There are `M=16` candidate labels, one uniformly distributed target, and `N=8`
conditionally independent reports. Conditional on target `0`, a report equals `0`
with probability `p=1/5` and equals each false label with probability
`q=(1-p)/(M-1)=4/75`. By target symmetry it is sufficient to condition on label
`0`.

For report-count vector `c=(c_0,...,c_15)`, the joint likelihood for candidate
`t` is proportional to `p^(c_t) q^(N-c_t)`. Because `p>q`, posterior order is
exactly count order. A pooled planner with budget `L` selects the `L` labels with
largest counts. If the cutoff crosses a tie, uniform cutoff tie-breaking includes
the target with share

```text
0                         if g >= L,
1                         if g + r <= L,
(L-g)/r                   otherwise,
```

where `g` is the number of false labels with count strictly above `c_0` and `r`
is one plus the number tied with `c_0`.

## Method A: labeled count vectors

Enumerate all weak compositions of eight reports into sixteen labeled counts.
There are exactly

```text
C(N+M-1,M-1) = C(23,15) = 490314
```

vectors. A vector has conditional probability

```text
N! / product_t(c_t!) * p^(c_0) * q^(N-c_0).
```

The frontier value is the exact sum of this weight times the cutoff share.
Arithmetic is integer-scaled: conditional probabilities use denominator `75^8`,
and tie shares use the least common multiple of `1,...,16`.

## Method B: false-count histograms

Independently fix target count `k` and let `h_j` be the number of the fifteen
false labels occurring exactly `j` times. The constraints are

```text
sum_j h_j = 15,
sum_j j h_j = 8-k.
```

The exact number of labeled report sequences represented by `(k,h)` is

```text
[N! / (k! product_j (j!)^(h_j))] * [15! / product_j h_j!].
```

The target cutoff share uses `g=sum_(j>k) h_j` and `r=h_k+1`. This evaluator does
not enumerate or consume Method A's labeled vectors.

## Independent certificate verification

The verifier uses a third traversal: decreasing integer partitions of the false
report count. It reconstructs occupancy frequencies, recomputes multiplicities,
probability mass, all eight exact frontier values, and the DD-001 interval
arithmetic. A corruption test increments the stored final numerator by one and
must be rejected.

## DD-001 emulation boundary

For any deterministic zero-communication private-team profile, a planner that
observes all private reports can apply the same role policies and emit the same
action vector. The pooled top-eight planner maximizes conditional target coverage
over all eight-action portfolios, so its exact value upper-bounds every such
emulated profile. Direct clue-following supplies the exact lower bound. This
argument does not imply that the pooled endpoint is attainable without pooled
information, that either endpoint is the private-team optimum, or that the
resulting interval is tight.
