# TreasureBench Agents v1 pilot custody commitment

The authorized private custody package for campaign
`treasurebench-agents-v1-pilot-v1`, batch
`tb-agents-v1-pilot-v1-b01`, was created on 2026-07-24 after both exact
direct-route public canaries passed.

This is a public hash-only engineering record. The 50-task allocation is bound
to the frozen execution commit
`fb10435a5d32567e90b1306a1c4eea1ee584d41d` and execution-sensitive tree
`sha256:2f4861759237e419e6901ecc3e6b09385712cc9e47912c0944cb3f9e0a8700a7`.

- Seed commitment:
  `sha256:903c81a0dadc2f0ebcf8b3ae8f9e593434b17fd665985ea931eba770f68cdaa0`
- Task ciphertext commitment:
  `sha256:ef5197edaa23f27487451fd36dda20dafe2f85bbbb0bddb1e836fd4337b3d5c3`
- Answer ciphertext commitment:
  `sha256:07ac8eade872dc5034159ef999ca845b3b5040b5690907f031b6c50c9c87e9fb`
- Custody-stage access-log commitment:
  `sha256:a1dcec32fbd6a2b50c2a825a84e2312ece37c2be469aabb05af95852cbe1395e`

Tasks and answers use separate AES-256-GCM custody domains and independently
generated key and nonce material. No seed, key, private task, answer, prompt,
output, or raw trace is present in Git. The answer package remains sealed;
unsealing is prohibited until the provider phase is closed and the complete
output-lock commitment is published.

This pilot remains non-inferential DD-010 instrument engineering. It creates no
study, claim, immutable scientific run, ranking, leaderboard, composite, or
authority for the base campaign.
