# TreasureBench Agents v1 pilot output-lock commitment

The provider phase for campaign `treasurebench-agents-v1-pilot-v1`, batch
`tb-agents-v1-pilot-v1-b01`, is closed. No further provider call, retry,
replacement task, repeat, or replacement custody material is authorized.

The complete existing encrypted inventory was locked before unsealing:

- output-lock commitment:
  `sha256:1d487723f7587e8e2fa865682e6f6cc473cf2da4967b837dedf3952cddfcbfab`;
- locked objects: 3,545;
- attempts: 3,037, including 3,035 successes and two preserved Anthropic
  errors;
- usage: 2,004,503 input tokens and 392,889 output tokens;
- total cost: USD 11.5702435, comprising OpenAI USD 4.1798125 and Anthropic
  USD 7.390431.

The lock covers the encrypted provider outputs, encrypted traces, hash-chained
usage/cost ledger, hash-chained access log, custody transitions, custody
commitments, provider-stage state, and preserved errors and costs. It is bound
to execution commit `b166e6fa19cbdec0bb8e786aee2de0d9edfc12d1` and
execution-sensitive tree
`sha256:81c3b51688dc2b61b225b989b81fbd922cbfe4c5059c171aa19499e7024e8757`.

At publication of this record, nothing had been unsealed. The correct
predeclared closeout outcome is
`sealed-pilot-quarantined-provider-failure`; the pilot cannot authorize a base
campaign.

This public record contains no task text, answer, seed, key, prompt, output,
raw trace, task-level metric, ranking, composite, or inferential claim. The
pilot remains non-inferential DD-010 instrument engineering and creates no
study, claim, immutable scientific run, paper result, leaderboard, or
base-campaign authority.
