# DD-013 report

Primary clean run `20260721T215811Z_DD-013_09c07448_cdac4fb512` passed in
109.147 seconds, within the registered 480-second estimate and 720-second cap.
It evaluates 175 parameter cells, 1,050 binding audiences, 4,025 voluntary
profiles, 2,625 feasible garbling rows, and eight information-firewall forms.

The Binding Audience Theorem proves that full precision should be delivered to
one role when `q>p`, withheld when `q<p`, and either withheld or sent to one at
equality. Within the registered symmetric garbling family, this binding optimum
weakly dominates every feasible garbled audience. Exactly 105 rows tie it—all
are full-precision one-recipient designs with `q>=p`; the other 2,520 rows are
strictly worse. Full broadcast is suboptimal in all 175 cells.

Voluntary recipients choose ex ante between shared-following and private-
following modes. Their outcome differs from mandated audience use in 656 of
1,050 audience settings. There are 273 excessive-use settings and eight with
welfare-relevant multiplicity. All 70 insufficient-use cases have audience
zero, so no positive-audience setting under-attends relative to the global
optimum on this grid.

Exclusive delivery binds the optimal access count. With full public access,
universal pooling implements the same count correspondence in all 175 cells,
is strict when `p!=q`, is ex-post budget balanced, and needs no external
subsidy. It does not select reader identity or cover conditional policies.

The independent enumerator reproduces all rows across 3,319,200 labeled states
and rejects altered binding, voluntary, mechanism, and garbling records. Claims
DD-C-0062 through DD-C-0064 are verified theorems; DD-C-0065 is an independently
reproduced bounded census.
