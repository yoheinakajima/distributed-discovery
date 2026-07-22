# Frozen model boundary

Nature draws one target uniformly from `M` finite locations. Each of `N`
agents receives a conditionally independent symmetric noisy-point signal with
private accuracy `p` and wrong-target probability `(1-p)/(M-1)`. The first
study restricts `p>=1/M` and uses simultaneous ordinary one-hit actions with a
common discovery objective and no strategic reward.

For block size `s in {1,...,N}`, the first `s` agents pool their signals. The
block chooses one posterior-MAP target and all block members execute that
duplicate action. A tie is resolved uniformly over posterior maximizers using
an independent randomization source. Each remaining agent executes the direct
private Bayes action, which is its nominated point under the declared
informative channel and tie rule. The group succeeds when the block candidate
or any remaining private action equals the target.

`s=1` is the ordinary direct-private baseline and `s=N` is full pooled
consensus. This is a protocol comparison, not the private-team optimum. It
does not use assignment, a pooled top-`L` portfolio, strategic equilibrium,
threshold teams, unreliable execution, overlap, human data, or real data.

For any registered symmetric channel with constant conditional private-action
accuracy `q`, define pooled MAP accuracy `C_s(W)` and the incremental-sharing
profile

`I_N(W)=(G_1(W),...,G_N(W))`.

The notation `I_N` avoids collision with the action-budget profile in DD-019.
That profile varies pooled action budget after full sharing; this one varies
the number of signals absorbed into a one-action block while remaining agents
keep private actions.
