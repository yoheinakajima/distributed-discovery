# DiscoveryBench Agents v1 ownership decision

Status: accepted registration architecture, no evaluation evidence.

## Decision

Register DiscoveryBench Agents v1 as an instrument layer owned by DD-010, with
`agents-v1` as an agent-evaluation protocol axis independent of the immutable
DiscoveryBench content axes v1, v2, and v3. A later evidence-producing
provider/model campaign requires a separate issue, registration, explicit
model/provider snapshots, explicit owner cost authorization, accepted
implementation, generated sealed holdouts, immutable traces, independent
verification, and corruption acceptance. That later gate may allocate a new DD
study only if its estimands and evidence ownership justify one.

No DD-023, claim, run, result, model call, cost, private seed, or holdout is
allocated by this decision.

## Alternatives

| Alternative | Scientific owner | Version preservation | Evidence category | Study ID now | Compatibility and public route | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| DiscoveryBench v4 | DD-010 | Misleading: implies new content after v3 | Would mix exact content and stochastic agent protocol | No | Could preserve APIs, but the label conflates axes | Reject |
| `agents-v1` protocol axis over content versions | DD-010 | Preserves v1/v2/v3 exactly | Registration only; future agent outputs stochastic | No | Additive adapter/protocol boundary and `benchmark/agents-v1.html` | Accept |
| Separate repository/package | Separate infrastructure owner | Strong isolation but duplicates provenance and validation | Registration only | No | Fragments claims, runs, exact comparators, routes, and CI | Reject |
| New DD evaluation study now | Future evaluation study | Content can remain immutable | Would own stochastic provider/model evidence | Not justified before execution authority | Premature without selected snapshots, cost, holdouts, and implementation | Defer |
| DD-010 instrument plus later evaluation gate | DD-010 now; later evidence owner decided at execution registration | Strongest separation of exact content, protocol, generator, trace, and result versions | Exact baselines remain DD-010; future agent evidence remains separate | No now | Reuses disabled adapter/capability boundary; stable public registration route | Accept |

## Decision dimensions

- **Scientific owner:** DD-010 owns benchmark instrument contracts and exact
  comparators. Existing task-family studies own their scientific results.
- **Version preservation:** content v1/v2/v3, their defaults, schemas, golden
  vectors, 24 v3 tasks, 29 protocols, 39 metrics, 36 compatible rows, and 660
  exclusions remain immutable.
- **Exact versus stochastic evidence:** theoretical baselines retain exact
  fractions. Any future model outcomes are stochastic software-agent evidence.
- **Study-ID need:** none for instrument registration. Reassess only at the
  separately authorized evaluation gate.
- **Claim ownership:** no claim is created. Future claims, if any, belong to
  the future evaluation evidence unit and cannot change baseline theorem status.
- **Public route:** one registration-safe static route,
  `benchmark/agents-v1.html`; no result route or leaderboard.
- **Compatibility:** benchmark-content and agent-protocol versions are recorded
  independently in every future task, trace, and result.
- **Adapter architecture:** extend the existing disabled-by-default boundary
  with interfaces and a deterministic no-network mock only; bundle no provider
  client or credential path.
- **Future execution workflow:** separate issue/branch, owner cost approval,
  frozen provider/model snapshots, committed generator, private custody,
  execution, immutable outputs, unsealing, verification, analysis, and only
  then claim consideration.
- **Paper ownership:** none. No paper or lifecycle change is authorized.
- **Stop conditions:** unresolved version conflation, public-answer leakage,
  absent datable snapshots, unsafe traces, unauthorized cost, insufficient
  model diversity, generic-accuracy collapse, or unverifiable evaluator.

## Why this is not v4

DiscoveryBench v1–v3 version benchmark content. Agents v1 versions the
software-agent evaluation protocol. Calling the latter v4 would imply a
content successor, obscure compatibility with all three existing content
versions, and make trace/result schemas appear to extend task schemas. Separate
axes make each future record explicit:

`content_version × agent_protocol_version × generator_version × prompt_version
× trace_version × result_version`.

## Reconsideration boundary

Reconsider a new DD evaluation study only after implementation acceptance,
provider/model selection, explicit cost authorization, generator freeze, and
cryptographic holdout generation are separately authorized. Do not allocate a
study merely because DD-023 is unused.
