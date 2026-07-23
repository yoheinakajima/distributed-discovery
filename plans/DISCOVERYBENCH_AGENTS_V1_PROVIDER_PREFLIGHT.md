# DiscoveryBench Agents v1 provider preflight and public calibration

This living ExecPlan follows `.agent/PLANS.md` and owns issue #175 from clean
`main` commit `8fa51758f39d4d04290784969d7990dd998019cb`. It implements
disabled-by-default live provider boundaries and executes only the explicitly
authorized public credential/model-route preflight and engineering
calibration. It is not the sealed engineering pilot or the claim-grade base
campaign.

## Purpose and intended outcome

Produce one fail-soft, redacted readiness matrix for every configured in-scope
gateway credential and exact model route; prove the adapter, structured-output,
usage/cost, redaction, exact-evaluator, and Method A/B boundaries on public
tasks; reconcile the owner-supplied four-paper review; and publish a truthful
operational status. Preserve direct-provider campaign requirements, private
custody, scientific claims, studies, immutable runs, and paper artifacts.

The permitted overall outcomes are:

- `all-required-providers-ready-public-calibration-complete`;
- `all-required-providers-ready-public-calibration-partial`;
- `required-provider-credential-failure`;
- `required-provider-model-access-failure`;
- `required-provider-policy-ineligible`;
- `authorization-invalid-or-expired`;
- `projected-cost-exceeds-authorization`;
- `structured-output-boundary-failure`;
- `adapter-boundary-failure`;
- `trace-redaction-boundary-failure`;
- `usage-cost-accounting-boundary-failure`; or
- `public-calibration-verification-failure`.

## Live baseline

At `2026-07-23T22:02:09Z`, local `main` and `origin/main` both equal
`8fa51758f39d4d04290784969d7990dd998019cb`, the squash merge of PR
#174. Issue #173 is closed as completed, PR #174 is merged at that SHA, and no
pull request is open. Issue #175 and branch
`benchmark/discoverybench-agents-v1-provider-preflight` own the sole active
substantive lane.

The repository-local credential file exists, is ignored by `.gitignore`,
untracked, unstaged, nonsymlink, and mode `0600`. The local authorization file
is a nonsymlink at mode `0600`. Authorization
`agents-v1-openrouter-preflight-20260723T215657Z` is active for this exact base
commit and branch, expires `2026-07-30T21:56:57Z`, permits at most USD 20,
permits at most two concurrent live providers, and forbids private tasks and
scientific evidence. Credential values and the local authorization artifact
remain outside Git.

The scientific inventory remains 110 claims through DD-C-0110, 26 studies
through DD-022, and 51 manifests with 48 passing immutable runs. No DD-023 or
DD-C-0111 exists. Seven accepted PDFs total 119 pages at their registered
hashes. The completed offline rehearsal hash remains
`sha256:d3410ff04bb73dcae929c3abc4cf289d58d6830f2a5ab50ca53764bef4af2c59`.

## Credential and authorization boundary

The sole credential source is the ignored repository-local `.env.txt`.
Credential loading requires explicit live mode and a strict, non-executing
dotenv parser. The parser rejects duplicate names, malformed names, NUL bytes,
command substitution, shell operators, and executable multiline constructs.
It exposes only the six allowlisted LLM variables to an adapter process and
never returns values in diagnostics, exceptions, `repr`, logs, traces, tests,
reports, or Git artifacts.

`FLYMYAI_API_KEY` and `MONID_API_KEY` may be recorded only as unused names
present. Their values are never loaded or transmitted. Tests use synthetic
secrets and never read the repository credential or authorization files.

Before every live call, authorization, base commit, branch, expiry, revocation,
gateway/route caps, total cap, route call ceilings, total call ceiling, and
concurrency are checked. After every call, provider-reported usage and
calculated cost update the redacted receipt. No call may begin when its
conservative maximum exposure would cross a limit.

## Scope

1. Implement strict local-input parsing, redaction, authorization, cost, and
   resume boundaries.
2. Implement disabled-by-default, transport-injected live adapters for
   configured routes supported by the registered campaign and explicitly
   authorized OpenRouter alternatives.
3. Add one unified fail-soft credential/model-route preflight.
4. Audit exact OpenRouter endpoints before generation and freeze endpoint,
   pricing, supported parameters, retention/training policy, ZDR/data
   collection, fallback, and max-price behavior.
5. Run one smallest provider-native structured-output smoke and one smallest
   public DiscoveryBench task per authorized passing route.
6. Plan and execute only the bounded public calibration permitted by the
   authorization and route decision.
7. Preserve redacted operational traces, usage, cost, route identity, and
   verification records outside `results/verified`.
8. Reconcile the owner-supplied four-paper review without editing any paper.
9. Produce the benchmark-to-paper interpretation map and post-campaign
   publication-implications template.
10. Publish a public-safe operational status, validate, merge, deploy, close
    issue #175, and synchronize `main`.

## Non-goals

No private seed, holdout, answer key, custody key, sealed pilot, 200-instance
base campaign, scientific claim, immutable scientific run, DD-023,
DD-C-0111, paper/PDF/citation/metadata/lifecycle edit, provider ranking,
leaderboard, composite score, hidden chain-of-thought request or retention,
human scoring, human or real data, Reliable Discovery, ActiveGraph, SQLite,
canonical-upstream mutation, submission, release, DOI, or external contact.

## Fixed decisions

- OpenRouter is one gateway/account even when it exposes multiple model-author
  families.
- The merged campaign manifest selects direct OpenAI
  `gpt-5.4-2026-03-05` and direct Anthropic `claude-sonnet-4-6`; it does not
  authorize OpenRouter.
- Owner-proposed OpenRouter Mistral and Gemini routes are therefore
  noncampaign alternatives unless a separate route-amendment decision is
  merged. They cannot silently satisfy direct-provider gateway diversity or
  the local/open baseline.
- Every campaign-eligible OpenRouter request would require one exact endpoint,
  no fallback, required parameters, data collection denied, accepted ZDR
  policy, and a frozen max-price ceiling.
- A model slug without an exact endpoint/provider slug is not route-frozen.
- A successful call does not imply campaign, policy, retention, or snapshot
  eligibility.
- Hidden reasoning is never requested, collected, inferred, stored, or
  scored. Only visible messages and structured actions are retained.
- One schema-only retry is allowed. Semantic retries are prohibited.
  Transport retries are bounded and limited to registered transient classes.

## Provider matrix

Gateway rows represent one credential/account. Route rows separately record
exact model and endpoint identity, required/optional and campaign/noncampaign
status, returned upstream identity, fallback policy, data/ZDR/retention and
snapshot eligibility, structured-output support, adapter and public-task
status, usage/cost availability, calibration status, and failure class.

Direct OpenAI, Anthropic, Google, and Mistral rows exist only when their
allowlisted variables are configured and the authorization/manifest permits
the route. `GEMINI_API_KEY` takes precedence over `GOOGLE_API_KEY`; ambiguous
dual configuration is rejected. Hosted Mistral through OpenRouter is distinct
from the registered revision-pinned local/open Mistral candidate.

## Adapter design

Live transports are standard-library HTTPS clients behind explicit network and
authorization gates. Request builders and response parsers are independently
testable with injected synthetic transports. Traces omit request and
authorization headers and retain only registered response metadata. Provider
errors normalize to authentication, account access, exact-model access,
policy, rate limit, transient transport, schema, usage, cost, and unknown
classes.

## Preflight sequence

1. Run offline schemas, mocks, authorization, cost, redaction, and matrix
   validation.
2. Discover configured allowlisted variable names without printing values.
3. Validate the local authorization and plan all maximum exposures.
4. Query OpenRouter model endpoint metadata before generation.
5. Select or reject exact endpoints and freeze a route-amendment decision.
6. Run the smallest authorized structured-output call for every configured
   route, fail-soft with maximum concurrency two.
7. Run one smallest public DiscoveryBench task through every passing route.
8. Plan the registered public calibration and freeze the largest deterministic
   prefix that fits.
9. Execute only routes permitted by the route and campaign boundaries.
10. Reconcile usage/cost, verify traces and Method A/B outputs, and emit the
    final matrix.

Passing stages may resume only for the same issue, execution commit, manifest,
and exact route. No credential fingerprint is retained. Credential rotation
therefore requires an explicit rerun.

## Public calibration plan

The reference public tier has ten public tasks, all five architectures, one
repeat, small registered teams, exact comparators, and no hidden answer or
private material. Direct campaign-selected routes may run only if configured
and policy eligible. Noncampaign OpenRouter routes may run only to the degree
explicitly permitted by the route-amendment decision and authorization, and
their outputs remain engineering-only optional-route calibration.

The plan records calls, token ceilings, provider/route maximum cost, total
maximum cost, and authorization margin before execution. If the full plan
cannot fit, it freezes the largest deterministic prefix. Calibration never
becomes provider-quality evidence.

## Trace, redaction, cost, and verification

Operational records retain exact route identity, request/generation IDs,
finish status, visible structured output, registered usage categories, actual
charged cost, calculated cost, timing, retry class, and redaction audit.
Credentials, headers, account/project identifiers, local paths, private
material, and undeclared metadata are prohibited. Deliberate synthetic-secret
corruptions prove stdout/stderr, exception, trace, and report redaction.

Method A uses the existing evaluator. Method B independently reconstructs
rights, exact comparators, metric primitives, trace hashes, cost accounting,
and contamination decisions. Disagreement blocks calibration completion.

## Paper-review reconciliation and interpretation

The owner-supplied four-paper review is a backlog, not a paper-edit
authorization. Each critique is checked against live source, bibliography,
literature coverage, citation graph, and transmission audit and classified as
already fixed, partly fixed, still open, factually disputed,
primary-source-verification required, useful but out of scope,
DiscoveryBench-dependent, or superseded by the current paper architecture.

The interpretation map links task families only to existing study/claim/paper
owners and states supportive, contradictory, null, and forbidden
generalization language. The publication template authorizes no paper action.

## Milestones

- **M0 (complete):** baseline, preservation, credential hardening, strict local
  input parser, authorization validation, issue, branch, and living plan.
- **M1 (complete):** live adapter implementation and mock transport tests.
- **M2 (complete):** unified preflight, resume, fail-soft matrix, authorization,
  cost, and redaction guards.
- **M2A (complete):** OpenRouter endpoint discovery and route-amendment audit.
- **M3 (complete):** provider-native structured-output smoke.
- **M4 (complete):** tiny end-to-end public DiscoveryBench task.
- **M5 (complete):** deterministic public calibration planning.
- **M6 (complete):** bounded public calibration execution and Method A/B
  verification.
- **M7 (complete):** combined guarded command path.
- **M8 (complete):** redacted authorization and cost receipt.
- **M9 (complete):** trace and secret-redaction audit.
- **M10 (complete):** provider readiness decision.
- **M11 (complete):** four-paper review reconciliation.
- **M12 (complete):** benchmark-to-paper interpretation map.
- **M13 (complete):** post-campaign publication-implications template.
- **M14 (complete):** public-safe operational site status.
- **M15 (complete):** full validation, CI, merge, Pages, live acceptance,
  issue closeout, and synchronized `main`.

Exactly one milestone is active at a time.

## Progress checklist

- [x] Verify local/remote main and authorized base SHA.
- [x] Verify issue #173, PR #174, and no competing pull request.
- [x] Verify the credential file is ignored, untracked, unstaged, nonsymlink,
  and mode `0600`.
- [x] Verify authorization file mode, scope, base, branch, caps, expiry,
  revocation, and public-only restrictions without printing credential data.
- [x] Freeze the five-file preservation set.
- [x] Complete the mandatory governance, Phase 2, registration, DD-010,
  adapter, paper-source, bibliography, citation-graph, and literature reading.
- [x] Create issue #175 and the sole substantive branch.
- [x] Implement and test the strict local-input parser and complete M0.
- [x] Complete M1 offline implementation and mock validation.
- [x] Complete M2 through M14 sequentially.
- [x] Complete M15 and synchronize `main`.

## Discoveries and surprises

- `2026-07-23T22:02:09Z`: all baseline, GitHub, credential metadata, and
  authorization metadata checks pass.
- `2026-07-23T22:02:09Z`: the local authorization caps OpenRouter at USD 20,
  OpenRouter Mistral at USD 5, and OpenRouter Gemini at USD 10, while reserving
  direct-provider caps. It permits at most 600 calls per route and 2,000 total,
  but the implementation must use the smaller registered public-calibration
  plan.
- `2026-07-23T22:02:09Z`: the merged model manifest does not authorize
  OpenRouter. Route reconciliation is therefore mandatory before any
  OpenRouter calibration and cannot change the claim-grade campaign silently.
- `2026-07-23T22:08:00Z`: the strict live parser reports configured
  OpenRouter, direct OpenAI, and direct Anthropic variables. Direct Google and
  Mistral variables are absent. The out-of-scope FlyMyAI and Monid names are
  present but their values were not loaded or transmitted. The required direct
  campaign routes can therefore enter preflight alongside optional OpenRouter
  alternatives.
- `2026-07-23T22:32:00Z`: standard-library, transport-injected adapters now
  implement the exact OpenAI Responses, Anthropic Messages, and OpenRouter
  Chat Completions contracts. OpenRouter payloads pin one discovered provider,
  disable fallback, require structured output, deny data collection, request
  ZDR, and freeze the endpoint price ceiling.
- `2026-07-23T22:32:00Z`: the real public matrix contains 294 initial calls
  per route. Reserving one schema-only retry for every call yields 588 maximum
  calls per route, below the authorization ceiling of 600. The registered
  1,000-input/256-output token ceilings keep both required direct routes below
  their USD 5 caps.
- `2026-07-23T22:25:00Z`: all pre-live validation passed: 43 focused live
  boundary tests, 329 repository tests, claim and run validation, all
  editorial audits, all seven paper builds at registered hashes and 119 total
  pages, and the 81-page/26-study site build.
- `2026-07-23T22:27:05Z`: the first committed live sweep made three rejected,
  zero-cost generation attempts. Both required direct routes authenticated but
  returned HTTP 400 at the provider schema boundary. OpenRouter exposed no
  structured-output endpoint for the Mistral route; the frozen Gemini/Google
  request was rejected under the exact data/ZDR/parameter policy filters. No
  public task completed, and no private or scientific material was created.
- `2026-07-23T22:31:00Z`: official provider documentation confirms that the
  strict schema subset must omit unsupported length/item constraints and that
  OpenAI requires every property to be required. The corrected shared provider
  schema uses typed singleton enums and leaves length/uniqueness validation to
  the existing downstream parser. The failed attempt will remain archived by
  execution commit before the corrected sweep replaces active state.
- `2026-07-23T22:31:47Z`: the corrected sweep passes structured output, one
  tiny public task, trace redaction, and Method A/B agreement for direct
  OpenAI and direct Anthropic. Seven generation attempts cost USD 0.0220905.
  OpenRouter Mistral remains ineligible because its only returned endpoint
  lacks structured output; the exact Gemini/Google request remains
  policy-ineligible under the frozen data/ZDR/parameter filters.
- `2026-07-23T22:58:29Z`: the full registered public calibration completed on
  the two required direct routes with two provider workers. OpenAI completed
  50 cases in 294 calls with 132,000 input tokens, 32,975 output tokens, and
  USD 0.8246250. Anthropic completed 50 cases in 296 calls, including two
  schema retries, with 257,281 input tokens, 43,808 output tokens, and USD
  1.428963. Method A/B agreement, protocol compliance, and contamination
  checks pass.
- `2026-07-23T23:11:45Z`: the cumulative ledger preserves all attempts at 607
  calls and USD 2.311758000, leaving USD 17.688242000 under authorization. A
  generic sensitive-key pattern had over-redacted token usage names in event
  traces; the rule is corrected and each existing trace now carries reconciled
  run-level usage totals sourced from the already-recorded public case or
  preflight metrics, without another provider call.

## Decision log

- `2026-07-23T22:02:09Z`: preserve all five unrelated untracked duplicates;
  never read, edit, stage, move, delete, normalize, or clean them.
- `2026-07-23T22:02:09Z`: treat OpenRouter as one gateway with model-family
  diversity but no gateway diversity.
- `2026-07-23T22:02:09Z`: retain direct OpenAI/Anthropic routes as required
  campaign rows even when their credentials are absent. Optional OpenRouter
  success cannot upgrade those rows.
- `2026-07-23T22:02:09Z`: write all calibration output under public-safe
  operational reports, never `results/verified`.
- `2026-07-23T22:32:00Z`: direct OpenAI and Anthropic are the only routes
  eligible for the full registered public matrix. OpenRouter Mistral and
  Gemini receive endpoint audit, structured smoke, and one tiny public task
  only; their route-amendment decision remains
  `optional-public-calibration-only`.
- `2026-07-23T22:35:00Z`: execute the two required calibration routes in two
  provider-level workers, the authorization maximum, with a thread-safe shared
  ledger. Calls within each route remain deterministic and sequential. All
  attempt calls and costs accumulate across execution commits; no archived
  zero-cost failure or paid passing stage disappears from the receipt.

## Validation strategy

Before live calls run focused dotenv, authorization, cost, redaction, adapter,
matrix, calibration-plan, and editorial-schema tests, followed by:

```text
git diff --check
make bootstrap
make audit-agents-v1
make agents-v1-dry-run
make agents-v1-readiness
make verify
make papers
make site
```

Live commands are:

```text
make agents-v1-provider-preflight
make agents-v1-public-calibration
make agents-v1-provider-preflight-all
```

After live calls, verify Method A/B agreement, exact comparators, usage/cost,
authorization margin, contamination, redaction, no private material, frozen
claims/studies/runs/papers, all route statuses, public site truthfulness, and
live desktop/mobile containment.

## Commands and expected observations

Ordinary tests never read local sensitive files or enable network. Live
commands require the exact branch and authorization and fail closed on any
mismatch. The unified command tests all configured in-scope gateways even
after a peer failure, but returns nonzero when any required campaign route is
not ready.

## Artifacts produced

The gate produces adapters, strict local-input and authorization/cost guards,
Make commands, mocks and corruptions, endpoint and route-amendment audits,
redacted readiness/cost/calibration records, three editorial artifacts, a
public operational status page/JSON, tests, and closeout evidence.

## Blockers

None. The provider-preflight lane is closed.

## Preservation set

These unrelated untracked files predate issue #175 and remain untouched and
unstaged:

- `papers/information-sharing-frontier/paper-audit 2.json`
- `papers/information-sharing-frontier/visual-qa 2.md`
- `plans/POST_V5_THEOREM_SPINE_CONSOLIDATION 2.md`
- `reports/roadmap-consolidation/post-v5-literature-and-nonoverlap 2.md`
- `reports/roadmap-consolidation/post-v5-next-program-gate 2.yml`

## Recovery and restart instructions

The lane is complete. Start any sealed engineering pilot from synchronized
`main` under a new issue, living plan, branch, pull request, and owner
authorization. Never treat the public calibration as private or scientific
evidence.

## Outcome and retrospective

PR #176 squash-merged as
`28a71f48db979664b4254c7693ae6622d9c38343`. Branch CI run `30052598698`,
post-merge CI run `30052895632`, and Pages run `30052895643` passed. The
deployed Agents v1 page and public JSON report the exact public-engineering
boundary, and desktop plus 390-pixel containment checks pass without
horizontal overflow or broken images. Issue #175 is closed as completed.

The final decision is
`all-required-providers-ready-public-calibration-complete`. Across every
preserved attempt, 607 calls cost USD 2.311758000, leaving USD 17.688242000
under the USD 20 authorization. Direct OpenAI and direct Anthropic completed
the full registered public matrix; optional OpenRouter routes remained
policy-ineligible and are not campaign substitutes. No private material,
sealed pilot, base campaign, scientific evidence, DD-023, DD-C-0111, paper
change, provider ranking, leaderboard, or composite score was created.
