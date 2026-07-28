# AO-0009 owner gate required

AO-0009 is frozen at diagnostic execution commit
`b7a3345af7d1af861bbddab58ba3af2a1d442297`. The committed gate manifest
passed live validate-only checks on draft PR
[207](https://github.com/yoheinakajima/distributed-discovery/pull/207).
No authorization was created and no retained private evidence was read.

The authorized diagnostic ceiling is one selected logical call, at most two
preceding and two following records, at most two corresponding response
decryptions, and at most one corresponding trace decryption. It permits zero
provider calls, zero credential reads, and zero spend. The command creates its
one-use marker before access and permanently closes private-read authority after
the invocation.

Owner authorization:

```sh
make owner-gate GATE=reports/agent-ops/AO-0009-treasurebench-ao0008-fixed-batch-diagnostic-owner-gate.yml OWNER_GATE_CHALLENGE='AUTHORIZE AOG-AO-0009-AO0008-FIXED-BATCH-DIAGNOSTIC b7a3345'
```

After authorization, resume this same task and run exactly once:

```sh
make treasurebench-fixed-batch-read-only-diagnostic
```

The exact resume message and full prohibition set are recorded in the
[owner-gate manifest](AO-0009-treasurebench-ao0008-fixed-batch-diagnostic-owner-gate.yml)
and the schema-valid
[handoff](AO-0009-owner-gate-required-handoff.yml).
