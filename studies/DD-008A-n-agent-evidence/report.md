# DD-008A report

Primary clean run `20260721T163030Z_DD-008A_8b70668b_06307caab4` evaluates every
registered `(N,p,c,k)` source-count cell with exact `Fraction` arithmetic. For
`k<N`, gross discovery is `1-(1-p)^(k+1)`; for `k=N`, it is
`1-(1-p)^N`. Closed-form binomial equal-split payoffs and a direct enumeration
of target and source-signal states agree exactly, including total prize equal to
gross discovery. This is a bounded accounting census, not a general-N theorem.
