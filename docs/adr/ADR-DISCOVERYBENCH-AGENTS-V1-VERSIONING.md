# ADR — DiscoveryBench Agents v1 versioning

Status: accepted for offline registration.

## Context

DiscoveryBench v1, v2, and v3 are immutable content versions owned by DD-010.
They contain exact golden task, protocol, metric, compatibility, exclusion,
and result vectors. The proposed software-agent instrument adds prompts,
multi-turn topology, structured actions, traces, custody, contamination
controls, stochastic estimands, and provider/model snapshots. Those objects do
not constitute a new exact benchmark-content release.

## Decision

Use independent version axes:

- benchmark content: `v1`, `v2`, or `v3`;
- agent evaluation protocol: `agents-v1`;
- task generator: `agents-task-generator-v1`;
- prompt template: `agents-prompt-v1`;
- structured action: `agents-action-v1`;
- trace: `agents-trace-v1`;
- result: `agents-result-v1`;
- custody manifest: `agents-custody-v1`;
- contamination report: `agents-contamination-v1`;
- statistical analysis: `agents-analysis-v1`.

Every future execution config and trace must record all applicable axes. A
moving provider alias may be observed in the candidate audit but cannot serve
as the frozen execution identifier.

The instrument remains under DD-010. No DD study ID is allocated for this
registration. The public registration route is
`benchmark/agents-v1.html`. Existing content commands remain unchanged and v1
remains the CLI default.

## Compatibility rules

1. Agents v1 may target declared subsets of content v1/v2/v3 without modifying
   any source task or expected metric vector.
2. Isomorphic private tasks derive from separately versioned generators and
   may not expose DD IDs, claim IDs, run IDs, known values, theorem names, paper
   titles, or exact public wording.
3. Provider/model adapters remain disabled by default. The repository may
   contain an interface and deterministic no-network mock, but no live provider
   implementation or credential loading.
4. Trace and result schema changes require their own versions and do not bump
   content versions.
5. There is no composite score or universal cross-provider ranking.

## Consequences

The architecture preserves exact baseline authority, makes stochastic
software-agent evidence visibly separate, permits one protocol revision to
operate over multiple immutable content versions, and avoids presenting
Agents v1 as DiscoveryBench v4. It requires verbose version manifests, which is
intentional for reproducibility.

## Rejected alternatives

- **DiscoveryBench v4:** rejected because it conflates content and evaluation
  protocol.
- **Separate repository/package:** rejected because it duplicates provenance,
  validators, exact comparators, and public integration.
- **New DD study at registration:** deferred because no evidence-producing
  campaign is authorized or sufficiently frozen.

## Reconsideration

A later evaluation gate may allocate a new study if selected provider/model
snapshots, estimands, stochastic evidence ownership, explicit cost authority,
accepted implementation, private custody, and verification make the campaign a
new evidence unit. Availability of an unused ID is not sufficient.
