# Private holdout policy

No private holdout exists. This policy freezes prerequisites for a later gate.

Future private instances must be generated only after the generator, provider
and model snapshots, prompts, architectures, sampling, cost cap, trace policy,
and evaluator are frozen. Holdouts must be isomorphic to registered task
families, use post-freeze CSPRNG seeds, be encrypted with established
authenticated-encryption libraries, carry commitments and ciphertext hashes,
and remain inaccessible to evaluated agents.

The planned design uses four independently generated batches with ten
instances per task family per batch: 200 private instances in total. This is a
planning count, not authorization to generate them. Outputs become immutable
before unsealing. Parameters, seeds, and answers are released after campaign
lock when safe. A leakage or commitment failure quarantines the affected batch
and stops confirmatory analysis.
