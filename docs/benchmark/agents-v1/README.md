# DiscoveryBench Agents v1

Status: offline implementation complete; evaluation campaign registered;
owner authorization pending; not model-evaluated.

DiscoveryBench Agents v1 measures how declared software-agent team
architectures convert dispersed synthetic evidence into structured search
actions. It operates over immutable DiscoveryBench content versions and exact
study-owned comparators. It is not DiscoveryBench v4, a provider leaderboard,
a universal intelligence benchmark, or evidence about humans or organizations.

Version axes are independent:

- benchmark content: v1/v2/v3;
- agent evaluation protocol: `agents-v1`;
- task generator: `agents-task-generator-v1`;
- prompt, action, trace, result, custody, contamination, and analysis schemas:
  their corresponding `agents-*-v1` identifiers.

The registered contracts now have an offline implementation under
`src/distributed_discovery/benchmark/agents_v1/`. The implementation generates
public calibration fixtures, compiles leakage-checked prompts, enforces closed
capabilities, runs all five architectures with deterministic mocks, validates
structured actions, computes exact-rational metrics by two paths, creates
public toy custody vectors, redacts and hashes traces, executes contamination
probes and all 24 corruptions, and refuses live execution. No provider/model
call, model download, cost, credential, private seed, holdout, private answer
key, evaluated provider trace, performance result, claim, or immutable run
exists.

Future evaluation requires a separate issue and registration, exact
provider/model snapshots, explicit owner cost
authorization, generated cryptographic holdouts, immutable outputs before
unsealing, independent verification, and corruption acceptance.

## Registered package

- `versioning.yml`, content/generator contracts, and compatibility policy;
- `task-families.yml`, `agent-protocol.yml`, `team-architectures.yml`, and
  `metrics.yml`;
- official-source `provider-model-candidates.yml` and the dated no-spend cost
  envelope in `reports/benchmark/`;
- cryptographic custody, contamination, visible-trace/redaction, and
  statistical-analysis contracts;
- two-path `verification-plan.yml` and 24-case `corruption-plan.yml`;
- 16 JSON schemas, clearly public toy fixtures and commitments, deterministic
  and adversarial no-network mocks, and the offline audit command
  `make audit-agents-v1`;
- `make agents-v1-dry-run` for the 50-case public rehearsal and
  `make agents-v1-readiness` for the implementation decision.

The implementation outcome remains
`reports/benchmark/discoverybench-agents-v1-implementation-decision.yml`:
`ready-for-evaluation-registration`. The current campaign outcome is
`reports/roadmap-consolidation/discoverybench-agents-v1-evaluation-decision.yml`:
`sealed-pilot-ready-owner-authorization-pending`. Neither is model
performance, scientific evidence, or execution authority.
