# AO-0009 aggregate diagnostic R2 owner gate required

The unused one-trace R1 gate is superseded. AO-0009 R2 is frozen at execution
commit `fbecbfb89e634967d48931c00e1d8a4fbed81c79`, and its committed gate
manifest passed live validate-only checks on draft PR
[207](https://github.com/yoheinakajima/distributed-discovery/pull/207).
No authorization exists and no retained state was read.

R2 permits one invocation that authenticates and extracts aggregate-only
signals from exactly 450 fixed-full-batch traces. It preserves one bounded
logical call, at most two corresponding responses, and at most two preceding
and two following operational records. Provider calls, credential reads, and
spend remain zero.

Owner authorization:

```sh
make owner-gate GATE=reports/agent-ops/AO-0009-treasurebench-ao0008-fixed-batch-diagnostic-r2-owner-gate.yml OWNER_GATE_CHALLENGE='AUTHORIZE AOG-AO-0009-AO0008-FIXED-BATCH-DIAGNOSTIC-R2 fbecbfb'
```

After authorization, resume this same task and run exactly once:

```sh
make treasurebench-fixed-batch-read-only-diagnostic
```
