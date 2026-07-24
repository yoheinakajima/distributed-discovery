# ADR: TreasureBench formal suite and Treasure Hunt playable companion

- Status: accepted for implementation
- Decision date: 2026-07-23
- Decision:
  `treasurebench-selected-and-implemented`
- Authority: editorial naming and compatibility only

## Context

The repository historically used DiscoveryBench as both an internal instrument
name and a public display name. That exact public name collides with an
established ICLR 2025 benchmark and software ecosystem. The repository
therefore held an owner-name-decision gate and a ranked shortlist without
authorizing a partial rename.

The owner has now selected TreasureBench for the formal suite and Treasure Hunt
for its playable companion. This decision supersedes earlier prompts that
selected or proposed BoxHunt, SearchParty, TreasureHunt as the formal token,
ActionPortfolioBench, or DiscoveryBench.

## Decision

The formal public suite is **TreasureBench**.

The canonical subtitle is:

> TreasureBench: a benchmark for collective search under shared and private
> evidence.

The required formal keywords are:

- collective search;
- multi-agent;
- benchmark;
- shared.

The playable companion is **Treasure Hunt**. Its required relationship is:

> Treasure Hunt is the playable companion to the TreasureBench suite.

Treasure Hunt is not a separate benchmark, package namespace, schema prefix,
metric prefix, claim name, run ID, paper theorem, scientific identifier, or
peer brand.

## Collision finding and bounded claim

The dated audit found no disqualifying exact `TreasureBench` same-domain
scholarly artifact, AI/ML benchmark, multi-agent system, required package, or
active high-confusion product in the declared channels. It did find unrelated
spaced-phrase furniture residue and longstanding technical/consumer usage of
`Treasure Hunt`.

The repository may state only:

> As of the recorded audit date, no disqualifying same-domain scholarly,
> AI-benchmark, multi-agent-system, package, or active high-confusion product
> collision for the exact name TreasureBench was found in the declared search
> channels.

The repository does not claim global uniqueness, exhaustive search, worldwide
namespace ownership, trademark clearance, legal review, guaranteed package or
domain availability, future availability, or absence of every exact-string
use.

## Hierarchy and funnel

The two public names form one family:

1. TreasureBench is the formal instrument.
2. Treasure Hunt is the interactive companion.
3. The Treasure Hunt route visibly uses the required relationship sentence and
   links directly to the canonical TreasureBench route.
4. Every current TreasureBench overview surface names and links Treasure Hunt
   in opening material.
5. README and future benchmark-paper metadata name the companion early.
6. Announcement templates pair the names on first mention.
7. Structured metadata records the formal-instrument and
   interactive-companion roles.
8. A machine validator rejects a broken funnel.

## Internal continuity

The rename is forward-only. Preserve exactly:

- DD-010;
- all DD claim IDs;
- all immutable run IDs and result paths;
- all historical study directories;
- all existing frozen schema, task, protocol, metric, certificate, and
  benchmark-content version IDs;
- exact outputs and evidence;
- old public routes through HTTP 200 aliases or compatibility surfaces;
- existing CLI behavior through compatibility aliases.

DiscoveryBench remains the historical/internal compatibility alias and the
correct spelling inside frozen identifiers. Dated evidence is not mass-renamed.

## Schema and content transition

Existing identifiers including `discoverybench-task-v1`,
`discoverybench-task-v2`, `discoverybench-task-v3`, Agents v1 protocol IDs, and
historical result keys remain unchanged. The next substantive nonfrozen
schema/content version may adopt a TreasureBench identifier only through an
explicit version transition and compatibility record. Rebranding alone does
not create a version.

## Package and CLI policy

The repository and root Python distribution remain
`distributed-discovery`. Existing imports and commands remain supported.
`distributed-discovery treasurebench ...` and, when packaging tests pass, a
delegating `treasurebench` console-script alias provide the formal public
interface. No standalone package is published. A future package requires owner
namespace reservation, licensing, release-policy, and packaging authorization.

## Theme boundary

Treasure/pirate presentation is allowed only for the companion guide, companion
task narratives, explanatory cards, local one-bit illustrations, restrained
non-authoritative CLI flavor, and educational copy.

It is prohibited in scientific claims, theorem statements, formal metric or
schema field names, IDs, estimands, comparators, evidence status, mathematical
prose, and immutable evidence. Existing formal terms remain unchanged,
including group discovery, distinct action coverage, duplication, planner
regret, private-baseline regret, recovery-budget attainment, source diversity,
communication-induced action compression, recovery budget, action portfolio,
and threshold team.

Every themed element must be removable without changing a scientific result.

## Approved metaphor map

| Companion metaphor | Exact formal term |
|---|---|
| map fragments | dispersed private signals |
| pooled fragments | information aggregation |
| X marks the spot / one shovel hole | one-answer or consensus action compression |
| copied or forged maps | common-source correlation |
| splitting doubloons | equal-split success rewards |
| minimum crew to dig | threshold-team technology |
| separate digging sites | diversified action portfolios |

Each use must sit beside owning studies, claim IDs, exact evidence, and
limitations. No metaphor broadens a theorem.

## Classical Treasure Hunt distinction

`Treasure Hunt` is a long-established label in distributed/mobile-agent,
robotic active-perception, reinforcement-learning, and navigation work. Those
problems generally ask an agent or agents to navigate a graph, grid, or
continuous arena to locate an inert hidden target and analyze travel, time,
advice, memory, or communication complexity.

TreasureBench instead gives software-agent teams shared and private evidence,
asks them to choose a portfolio of actions, and evaluates them against
registered exact private, planner, and equilibrium comparators under
alternative information/action architectures.

A future benchmark-paper related-work section must state this distinction with
primary citations. It is mandatory for AAMAS-adjacent submission and
recommended for every formal benchmark paper. This ADR creates no paper.

## Rejection and supersession record

- **DiscoveryBench**: rejected as the external scholarly name because of the
  established ICLR 2025 benchmark/software collision. Retained only for
  historical, frozen, compatibility, and dated uses.
- **SearchParty / Search Party**: permanently excluded under current public
  information because of an active same-industry AI-visibility/GEO company and
  package/search-surface confusion. No private social-graph claim is recorded.
- **TreasureHunt / Treasure Hunt as formal token**: rejected because the phrase
  is established technical vocabulary, extremely generic, and likely to cause
  reviewer/citation-graph misclassification. Retained as the companion only.
- **BoxHunt**: superseded as the selected formal name. It is the first internal
  fallback because known commercial, game, retail/event, and repository
  residue makes it weaker than the TreasureBench/Treasure Hunt family.
- **SharedBench, SharedSearch, SharedHunt**: rejected because of communal-X
  misreading, shared-task vocabulary collision, acronym risk, and dilution of
  The Shared Discovery Paradox.
- **treasuregame, guessinggame, finditgame**: rejected because `-game`
  miscategorizes the formal artifact and creates a consumer/hidden-object
  register.
- **boxpicker**: rejected because of robotic box-picking confusion.
- **choosebench, guessbench**: rejected for semantic emptiness or
  category-error framing, with occupied-name signals retained where verified.
- **ActionPortfolioBench and the earlier ranked shortlist**: historical
  decision input superseded by the owner TreasureBench decision, not active
  candidates.

If a future fatal TreasureBench collision appears, the internal fallback order
is BoxHunt, ForageBench, SixteenBoxes. This order is not public branding and is
not reopened by this decision.

## Vernacular option

If sustained third-party usage independently refers to the formal suite—not
only the companion—as `Treasure Hunt` or `Yohei's Treasure Hunt`, the owner may
open a separate bounded decision. Valid evidence must be owner-supplied and may
include independent citations, forks, third-party documentation, posts, or
package references.

No monitoring of people, social media, AI retrieval, or search rank is
authorized. No adoption is inferred automatically and no future rename is
precommitted.

## Namespace owner actions

The owner may separately reserve PyPI, npm, GitHub, Hugging Face, optional
domains, and optional social handles. The owner should perform one-time USPTO
and EUIPO preliminary register checks before the first DOI or package release.
This milestone performs none of those actions.

## Risks

- Future same-domain use can arise after the audit.
- The generic companion phrase can be misread without the funnel.
- Historical and frozen DiscoveryBench strings can look like an incomplete
  migration unless compatibility metadata is explicit.
- A console-script alias does not reserve a package namespace.
- Preliminary registry searches are not legal conclusions.

## Reversibility

Current display metadata, aliases, and companion presentation are reversible
without changing scientific evidence. Frozen identifiers and historical
records are intentionally not rewritten. Any future formal-name change
requires a new bounded decision and another compatibility migration.

## Consequences

TreasureBench becomes the formal current-facing suite identity. Treasure Hunt
becomes its presentation-only companion. DiscoveryBench remains load-bearing
where history, compatibility, or frozen evidence requires it. Scientific
counts, paper artifacts, and evidence status do not change.
