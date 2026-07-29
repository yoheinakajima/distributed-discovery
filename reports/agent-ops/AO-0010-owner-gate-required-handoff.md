# AO-0010 owner gate required

AO-0010 is frozen at execution commit
`5289882dca6b8912a0518bba72aba1f4d595c2a8`. The committed generic gate
manifest at `17acd93030e815daf22a7a00e4cf6633b38b2829` passed live validate-only
checks on draft PR
[209](https://github.com/yoheinakajima/distributed-discovery/pull/209).
No authorization was created, and no credential, private material, provider
call, spend, or unseal occurred.

Policy `treasurebench-agents-v1-protocol-validity-policy-v2` governs campaign
`treasurebench-agents-v1-repair-confirmation-v4`, batch
`tb-agents-v1-repair-confirmation-v4-b01`. Expected cost is USD 11.51, the
conservative envelope is USD 15, and hard caps are USD 25 total, USD 10
OpenAI, USD 15 Anthropic, and 5,200 calls.

Owner authorization:

```sh
make owner-gate GATE=reports/agent-ops/AO-0010-treasurebench-fresh-pilot-v4-owner-gate.yml OWNER_GATE_CHALLENGE='AUTHORIZE AOG-AO-0010-FRESH-PILOT-V4 5289882'
```

After authorization, resume this same task and run:

```sh
make treasurebench-fresh-pilot-v4-live
```

The exact resume message, fixed task contract, living ExecPlan, and full
prohibition set are recorded in the
[owner-gate manifest](AO-0010-treasurebench-fresh-pilot-v4-owner-gate.yml)
and the schema-valid
[handoff](AO-0010-owner-gate-required-handoff.yml).
