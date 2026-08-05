# TreasureBench open-weight cloud-runtime feasibility and conformance

## R5 generic owner-gate compatibility repair (2026-08-04)

The owner authorized one forward-only preauthorization repair after the R4
authorization was consumed by its legitimate pre-ingress hard stop. R1 through
R3 remain superseded unused; R4 remains consumed and nonreusable. R5 changes
only the task-specific authorization adapter: it validates the canonical
generic owner-gate `cumulative_state`, `hard_caps`, and `remaining_caps`
mappings at exact zero cumulative spend/calls, USD 20 and 400 hard caps, and
fully reconciled remaining caps. It accepts no legacy `budget` fallback and
does not change the generic Agent Operations engine.

The complete R4 runtime is inherited unchanged: public unauthenticated GitHub
and Git preflight, repository-root `.env.txt` exact two-name ingress, temporary
RunPod Secrets/template, encrypted REST Pod creation, controller finalizer,
Pod-resident six-hour watchdog, measured attestation, public 50-pairing
calibration, exact teardown/billing/projections, and one-session administrative
closeout. No credential, authenticated provider call, resource, download,
inference, or spend is permitted while R5 is prepared and validated.

### R5 milestones

- **R5-M0 — complete:** verify issue #212, draft PR #213, branch and remote
  head, the clean tracked tree, five unrelated untracked files, and the exact
  R4 hard-stop boundary; register the additive R5 contract.
- **R5-M1 — complete:** implement the forward-only validator/entry point,
  real-writer regressions, corruption layer, and exact offline rehearsal.
- **R5-M2 — complete:** 15 focused and 159 inherited-plus-R5 tests, 95
  corruptions, the exact 50-pairing/294-call rehearsal, Ruff on 379 files,
  strict MyPy on 220 source files, 1,016 repository tests, all audits, seven
  papers/119 pages, and the 89-page/26-study site pass.
- **R5-M3 — pending:** commit and push the execution tree, update PR #213,
  pass exact-head checks, and freeze every execution-sensitive hash.
- **R5-M4 — pending:** create and validate, but do not authorize or execute,
  `AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION-R5`; freeze the schema-valid
  owner-gate-required handoff and stop once.

### R5 preserved failures and corrections

- The first combined focused command invoked `load_yaml` with a string instead
  of a `Path`; that one-off contract check failed before any task action. The
  same run then found the rehearsal test expected a nonexistent aggregate
  `methods_agree` key, and Ruff found import ordering, two unused imports, two
  long lines, and an overly broad exception assertion. MyPy also found unsafe
  optional narrowing and test mapping/type annotations. These were mechanical
  test/typing defects; the contract check now uses `Path`, the rehearsal checks
  the actual Method A/B and Method C fields, imports/lines were normalized,
  schema failure is asserted specifically, and explicit narrowing/types were
  added. The next focused run passed 15 tests and strict focused MyPy; a final
  Ruff import-order pass then succeeded.
- A final source-wide search found the same obsolete `gate["budget"]` reads in
  superseded R2 and R3. Their live validators, plus consumed R4, now fail
  explicitly as nonusable before any authorization-dependent work, and the
  obsolete reads were removed. The R5 regression searches every AO-0012
  open-weight live adapter, so no legacy gate-budget dependency remains.
- The first post-documentation `make verify` was intentionally interrupted
  after 43 passing tests when that source-wide search identified the R2/R3
  cleanup while the wall was already running. The partial run was not counted;
  validation restarted from Ruff and strict MyPy after the correction.
- The first local R5 gate-schema validation parsed one unquoted owner statement
  containing a colon as a YAML mapping instead of a string. Validation failed
  before commit or authorization. The statement now uses a folded scalar; the
  gate was refrozen from a new execution commit rather than rewriting the
  already pushed compatibility commit.

## R4 owner-authorized live attempt hard stop (2026-08-04)

The owner supplied and the generic Agent Operations engine accepted the exact
R4 challenge at `2026-08-04T13:45:02Z`. The immediately following exact command
`make treasurebench-open-weight-runtime-live` failed closed in
`validate_owner_authorization` before repository-root `.env.txt` ingress. The
protected R4 runtime attempted to read `gate["budget"]`, but the validated
generic owner-gate manifest and authorization surface use `cumulative_state`,
`hard_caps`, and `remaining_caps`; Python raised `KeyError: 'budget'`.

The failure preceded credential loading, control-plane construction, namespace
inventory, Secret or template creation, Pod creation, model download, endpoint
startup, inference, and spend. The AO-0012 lifecycle state path is absent, so
there is no possible Pod, temporary resource, disposable volume, billing, or
teardown ambiguity. The registered decision is
`calibration-integrity-failure-stop`. The attempted R4 authorization must not
be rerun or reused. PR #213 remains draft and issue #212 remains open pending an
explicit owner-authorized additive repair, protected-tree refreeze, and new
gate.

Public-safe hard-stop closeout validation passes the outcome and handoff
schemas, the selected-decision validator, all 144 combined open-weight tests,
Ruff, strict MyPy on 219 source files, all 1,001 repository tests, every audit,
the offline compendium wall, and the 89-page/26-study site build. These checks
do not repair or authorize reuse of the failed R4 live surface.

## R4 final live-preflight and encrypted-Pod correction (2026-08-02)

The owner superseded the unused, unauthorized R3 gate without creating or
consuming it. AO-0012 remains the same task under issue #212, draft PR #213,
branch `agent/treasurebench-open-weight-cloud-runtime`, and this living plan.
The exact model revision and BF16 checksums, Tekken tokenizer, vLLM 0.23.0,
immutable Linux/amd64 container, one Secure Cloud dedicated noninterruptible
A100 80GB PCIe, repository-local two-name credential ingress, temporary
Secrets/template, measured attestation, 50-pairing public calibration, six
GPU-hour and 400-call ceilings, and USD 10 expected/USD 20 hard limits remain
unchanged.

R4 removes the live-path dependency on GitHub CLI authentication. Before
`.env.txt` ingress, the controller performs bounded, fixed-User-Agent,
unauthenticated public GETs for issue #212 and PR #213 plus exact `git
ls-remote` branch verification. It retains only the normalized issue number and
state and the PR number/state/draft/base/head identity required for the gate;
raw bodies and unexpected fields are not written to logs or artifacts.

R4 replaces GraphQL Pod creation with the documented Bearer-authenticated
`POST https://rest.runpod.io/v1/pods`. Its exact frozen body requests Secure
Cloud, one A100 80GB PCIe, CUDA compatibility list `['13.0']`, the exact
temporary template, 50-GB container disk, 120-GB `/workspace` volume,
`volumeEncrypted: true`, US placement, port `8000/http`, and no public IP.
It prohibits `minCudaVersion`, `terminateAfter`, network volume, raw secret,
environment override, alternate hardware, and fallback fields. The create
response and one fresh Pod GET must independently agree on identity, template,
image, Secure Cloud hardware, storage, encryption, no network volume, and rate
before any model work.

Because this encrypted REST operation has no documented `terminateAfter`
input, R4 does not claim a native termination guarantee. Orphan control is the
unconditional controller finalizer plus a minimal Pod-resident watchdog armed
before model download. The watchdog uses only the automatically supplied Pod
ID and Pod-scoped RunPod key, verifies its exact encrypted/no-network-volume
Pod by bounded REST GET, records only public-safe PID/existence/deadline data,
and issues REST DELETE for its own Pod at a six-hour monotonic deadline. The
parent removes the Pod key before vLLM or proxy launch. The endpoint bearer is
stored only in a mode-0600 `/run` file, never under `/workspace`.

The additive fixed R4 contract is
`tasks/treasurebench-open-weight-cloud-runtime-r4.yml`. No R4 authorization
exists. No real `.env.txt`, RunPod or Hugging Face account, model artifact,
GPU, endpoint, inference call, private/scientific state, or spend has been
accessed.

### R4 milestones

- **R4-M0 — complete:** verify local branch/head, public issue #212, public
  draft PR #213, remote branch head, R3 unconsumed state, and official RunPod
  REST Pod-create/storage/Pod-variable surfaces without credential access.
- **R4-M1 — complete:** register the additive R4 contract, official-source
  audit, 30-case corruption layer, public GitHub preflight, exact encrypted
  REST Pod creation, dual observed-state verification, and Pod watchdog.
- **R4-M2 — complete:** the complete 50-pairing rehearsal, all 84
  inherited-plus-R4 corruptions, 62 R4 tests, 144 combined open-weight tests,
  Ruff, strict focused mypy, repository mypy on 219 source files, all 1,001
  repository tests, every repository audit, the offline compendium release
  wall, and the site build pass.
- **R4-M3 — complete:** execution commit
  `710fcc333b78e153ba317d76f0e68303f7617092` contains only the 17 intended
  R4 files and is pushed; PR #213 remains open and draft, retains `Tracks
  #212`, points to that exact head, and both exact-head validation checks pass.
- **R4-M4 — complete:** freeze the protected tree, create and validate the
  unconsumed generic R4 owner gate, freeze the schema-valid handoff, and stop
  once at owner-gate-required.
- **R4-M5 — hard stop:** the exact owner authorization succeeded, but the exact
  live command stopped before credential ingress on the generic-authorization
  versus owner-gate cumulative-state mismatch. Zero resources, calls, and spend
  exist; repair and retry require a new prospective gate.

### R4 preserved failures and corrections

- The initial direct web opener refused the raw GitHub API URL under its safe
  URL policy. A fixed public curl request with the registered User-Agent and a
  normalized jq projection verified the issue and PR state without retaining
  response bodies.
- `rg` was unavailable for the first local R4 source scan. The read-only scan
  was repeated with `grep`, which found the expected copied R2/R3 terms before
  they were corrected.
- The first focused Ruff run found one unused test-only `subprocess` import and
  stopped before pytest. Removing that import changed no runtime behavior.
- The next focused pytest collection failed because `scripts` is not an
  importable installed package. The test now loads the watchdog file through
  `runpy` without modifying packaging or deployment identity.
- The first complete R4 test execution found one overly broad assertion that
  searched for substring `gh`; the word `weight` contains that substring. The
  regression now rejects only an exact `gh` executable. All 62 R4 tests then
  passed.
- The first strict focused mypy pass found ten narrowing and test-wrapper type
  errors. Explicit Mapping guards, one nonoptional Pod-ID local, and an
  annotated synthetic `Path.open` guard corrected the types without changing
  runtime semantics; strict mypy then passed all four R4 Python files.
- The first complete `make verify` passed Ruff and mypy and reached 995 passing
  tests; six nested `uv run` preview tests failed only because sandbox DNS
  blocked isolated build dependency resolution. The identical approved
  network-enabled rerun passed all 1,001 tests, claims and runs, every audit,
  and the offline compendium release wall.
- An explicit `make papers` invariant command stopped because `pdfinfo` is not
  installed in this host environment. Paper source, visual-QA, and generated
  invariant tests had already passed inside the 1,001-test wall; no paper
  source or artifact was changed. The separate `make site` build passed 89
  pages and 26 studies.
- The final sandboxed public preflight stopped at `git ls-remote` because DNS
  resolution was blocked before the Python verifier ran. The identical
  approved network-enabled command then matched local, remote, and public draft
  PR heads and passed the complete token-free R4 pre-ingress verifier.


## R3 exact RunPod API contract correction (2026-08-02)

The owner superseded both unused gates
`AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION` and
`AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION-R2` without creating or consuming
authorization. AO-0012 continues under issue #212, draft PR #213, branch
`agent/treasurebench-open-weight-cloud-runtime`, and this living plan. The
runtime identity, exact model, tokenizer, vLLM, immutable container, one Secure
Cloud A100 80GB PCIe, R2 credential/resource/attestation/finalizer design,
public 50-pairing calibration, six-hour limit, 400-call cap, and USD 20 hard cap
remain unchanged.

R3 corrects only the prospective RunPod control-plane contract. Current
official GraphQL guidance sends requests to
`https://api.runpod.io/graphql?api_key=<URL-ENCODED-KEY>`; R3 therefore uses
the URL-encoded `api_key` query parameter and no Authorization header for
GraphQL inventory, `secretCreate`, `secretDelete`, and
`podFindAndDeployOnDemand`. Current REST references require
`Authorization: Bearer <token>`; R3 preserves that header and prohibits the
`api_key` query parameter for template creation/deletion, Pod deletion and
lookup, and exact Pod billing. HTTP failures expose only the fixed GraphQL or
REST operation class and numeric status; raw authenticated URLs, credentials,
headers, responses, and provider bodies remain redacted.

The official Pod guide demonstrates `allowedCudaVersions` for
`podFindAndDeployOnDemand`. R3 freezes `allowedCudaVersions: ["13.0"]`,
prohibits `minCudaVersion`, `cudaVersion`, and unregistered CUDA fields, and
freezes the complete supported input field set. The current GraphQL schema
continues to expose `terminateAfter`, so the authorization-start-plus-six-hour
server-side backstop remains. The schema also lists `minCudaVersion` as an
available input, but AO-0012 deliberately follows the current Pod guide's
exact-list field; R3 does not claim the schema field is nonexistent.

The additive fixed R3 contract is
`tasks/treasurebench-open-weight-cloud-runtime-r3.yml`. No R3 authorization
exists. No real `.env.txt`, RunPod or Hugging Face account, model artifact,
GPU, endpoint, inference call, private/scientific state, or spend has been
accessed.

### R3 milestones

- **R3-M0 — complete:** verify local/live branch, issue, draft PR, exact head,
  checks, and five unrelated untracked files; audit current official GraphQL,
  Pod-create, REST, and `terminateAfter` sources.
- **R3-M1 — complete:** the additive R3 contract, official-source audit, 18-case
  corruption layer, query-only GraphQL transport, Bearer-only REST transport,
  and exact Pod create-input implementation are registered.
- **R3-M2 — complete:** 101 combined focused runtime/input tests, the complete
  50-pairing rehearsal, all 54 inherited-plus-R3 corruptions, focused audits,
  Ruff, mypy on 218 source files, all 939 tests, and the complete repository
  verification wall pass.
- **R3-M3 — complete:** execution commit
  `1b6845d5cec11cdf64da66a23ecbd96ae8927fc7` contains only the 13 intended
  R3 files and is pushed; draft PR #213 accurately retains `Tracks #212`,
  points to the exact execution head, and both required checks pass.
- **R3-M4 — complete:** the 33-path protected tree and execution commit are
  frozen in committed gate head `efe5c53838c0eb6b1b41cdfd5553c76d9a047394`;
  the generic engine live-validates the gate with exact challenge
  `AUTHORIZE AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION-R3 1b6845d` and creates
  no authorization or consequential action.
- **R3-M5 — complete:** the schema-valid owner-gate-required handoff is frozen
  at `reports/agent-ops/AO-0012-r3-owner-gate-required-handoff.yml`; commit and
  push this final public-safe record, confirm exact-head checks, and stop without
  running the owner-gate or live command.

### R3 preserved failures and corrections

- The repository patch helper again failed before mutation because its bundled
  Codex executable is absent. Exact, assertion-checked mechanical edits are the
  narrow fallback, and every resulting diff is reviewed.
- The first assertion-checked R3 module rewrite stopped before writing because
  one offline-rehearsal block had a different key order than expected. The
  corrected exact pattern then applied successfully.
- The first Makefile replacement exposed shell command substitution of
  `$(PY)` and `$(RUN)` inside a double-quoted synthetic edit payload. The
  commands were not found, the replacement assertion failed, and the Makefile
  remained unchanged; a single-quoted JSON payload corrected the edit.
- The first R3 focused format check correctly reported both new Python files
  required formatting. The next Ruff pass found only import ordering and two
  unused imports. After correction, 17 new transport/create-input tests passed.
- The first focused mypy pass found seven test-only type errors in request-body,
  synthetic HTTP-header, and rehearsal-object narrowing. Explicit byte,
  `Message`, `Mapping`, and cast guards corrected them without runtime
  semantic change.
- Two subsequent combined Ruff passes each found one import-order correction
  after new imports were added; both were fixed mechanically before the next
  passing mypy and 17-test run.
- The first ExecPlan insertion attempt passed Markdown backticks through a
  double-quoted shell argument, so the shell rejected the command before Python
  ran and the plan remained unchanged. The corrected single-quoted payload
  preserved the literal registration text.
- The first milestone/status update used a mismatched assertion marker and
  stopped before writing. The corrected exact-indentation marker applied the
  same intended documentation-only update.
- The first complete `make verify` passed formatting, Ruff, and mypy, then
  reached 933 passing tests with six nested `uv run` CLI previews failing only
  because sandbox DNS blocked build-dependency resolution. The approved
  network-enabled rerun passed all 939 tests and the complete claims, runs,
  audits, site, and compendium release dry-run wall.
- A later milestone-update payload contained an unescaped apostrophe inside its
  single-quoted shell argument, so the shell rejected it before Python ran and
  the plan remained unchanged. The corrected payload removed that ambiguity.
- The first sandboxed GitHub authentication check reported the keyring token as
  unavailable and the combined PR/issue read failed DNS. The approved
  network-enabled checks verified the keyring session, open issue #212, exact
  open draft PR #213, execution head, body, and checks without provider access.
- The first explicit `git add` attempt was refused because the sandbox exposes
  `.git` read-only. The approved retry staged only the 13 named AO-0012 files;
  the five unrelated untracked files remain untouched.
- The first protected-hash command used the default uv cache and failed before
  hashing because the sandbox denied that cache. The task-local cache retry
  froze all 33 hashes. The first gate generator then used system Python 3.9,
  which lacks `datetime.UTC`; the pinned uv Python 3.11 retry created the gate.
- The first direct gate-schema check imported a nonexistent validation module
  and failed before validation. Importing the repository validator from the
  Agent Operations core then passed the owner-gate schema, exact contract hash,
  and all 33 protected tree hashes without creating authorization.


## R2 preauthorization safety and closeout repair (2026-08-01)

The owner superseded only the unused R1 live surface and gate
`AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION`. No R1 authorization was
created or consumed. AO-0012 continues in issue #212, draft PR #213, branch
`agent/treasurebench-open-weight-cloud-runtime`, this living plan, the same
runtime identity, exact model/tokenizer/engine/container/GPU identity, public
10-task/50-pairing calibration, and unchanged six-hour, 400-call, and USD 20
hard caps. The draft PR now says `Tracks #212`; closure remains post-calibration
or honest failure closeout, exact teardown and billing, squash merge,
post-merge CI/Pages, and named-route verification only.

The additive fixed R2 contract is
`tasks/treasurebench-open-weight-cloud-runtime-r2.yml`. R2 requires the
repository-root `.env.txt` strict nonexecuting loader to return only
`RUNPOD_API_KEY` and `HF_TOKEN`, after exact authorization, contract,
protected-tree, branch, issue, draft-PR/head, ancestry, zero-cumulative-state,
and local lifecycle-conflict checks. Tests inject synthetic credentials and
never inspect the real file.

Three authorization-bound RunPod Secrets carry the HF token, generated
endpoint bearer, and generated attestation HMAC key. A temporary private Pod
template contains only `{{ RUNPOD_SECRET_name }}` references. The exact Pod
namespace derives from AO-0012, the R2 gate, and the authorization digest.
Every possible Pod enters one finalizer that stops dispatch, deletes and
verifies the Pod and disposable volume boundary, deletes and verifies all
temporary secrets and the template, polls the exact Pod bill, reconciles
positive billed time/amount plus returned storage usage, applies the caps, and
writes one schema-validated redacted success or failure outcome.

Current official RunPod GraphQL spec 1.1.0 and tagged runpodctl v2.8.0 expose
`PodFindAndDeployOnDemandInput.terminateAfter`; R2 freezes authorization time
plus six hours as the native server-side backstop. The same public GraphQL
input does not expose `volumeEncrypted`. R2 does not invent that field:
both the authenticated create response and a Pod-scoped self-query must report
`volumeEncrypted: true` before the startup script writes any secret to disk.
False or absent is an exact bounded control-boundary failure followed by
teardown and billing.

Measured HMAC attestation now distinguishes requested CUDA compatibility from
measured toolkit, CUDA runtime, and PyTorch CUDA. It measures the actual GPU
name/count/memory, driver, vLLM, mistral-common at least 1.11.3, exact model and
tokenizer SHA-256, no quantization, tensor parallel size one, startup/load
times, and peak GPU memory. vLLM and the proxy launch under `env -i`; the HF
token, Pod-scoped RunPod key, attestation key, base64 payloads, and endpoint
bearer environment variable are cleared before either child. The bearer is
read once from one mode-0600 file on the verified encrypted disposable volume.

### R2 milestones

- **R2-M0 — complete:** verify live Git/GitHub state, register the additive R2
  authority, preserve R1 unconsumed, and change PR #213 to track rather than
  auto-close issue #212.
- **R2-M1 — complete:** audit current official Secrets, templates, Pod
  inventory, `terminateAfter`, storage-encryption, billing, and deletion
  surfaces; record the exact encrypted-volume API limitation.
- **R2-M2 — complete:** implement credential ingress, temporary
  secret/template lifecycle, in-Pod secret minimization, deterministic
  namespace and ambiguous-create reconciliation, server-side termination,
  measured attestation, finalizer, redacted outcome schema, and separated
  projections.
- **R2-M3 — complete:** preserve the original 50-pairing rehearsal and
  corruptions; add 36 R2 corruptions and focused authorization-free tests for
  ingress, secrets, inheritance, orphan control, attestation, every bounded
  post-create failure, teardown, billing, ambiguity, false-feasibility, and
  leakage.
- **R2-M4 — complete:** focused validation and the full repository wall pass;
  execution commit `09dd13837093d3c4ff7fa52f57fce4b84ab0acc3` is pushed;
  all 28 execution-sensitive hashes are frozen; and both exact-head draft-PR
  checks passed.
- **R2-M5 — complete:** the generic unconsumed
  `AOG-AO-0012-OPEN-WEIGHT-PUBLIC-CALIBRATION-R2` gate validates live at
  committed gate head `986bb339662bd15e388c0d7a5c77c321b06a2b2f`; the
  schema-valid R2 owner-gate-required handoff is frozen. Stop without
  authorization.

### R2 preserved failures and corrections

- The final plan patch-helper retry again failed before mutation because the
  bundled Codex executable is absent, and the stdin-less `git apply` fallback
  rejected an empty input. Exact mechanical replacements were used and their
  diffs were rechecked.
- The first live generic-gate validate-only attempt failed only because the
  sandbox could not resolve GitHub for `git ls-remote`. The identical approved
  network-enabled command passed and explicitly created no authorization.
- A PR-body update passed Markdown backticks through a double-quoted shell
  argument, causing local command substitution and inserting public validation
  output in draft PR #213. No secret or private value was involved. The body was
  immediately replaced with a compact no-substitution R2 summary, re-read live,
  and still says `Tracks #212`.
- Public official-source retrieval first failed under sandbox DNS isolation;
  the approved public-network retry succeeded. A quoted URL correction was
  required after zsh treated the GitHub tree query string as a glob.
- The repository patch helper failed before mutation because its bundled Codex
  executable path did not exist. Patch-format `git apply` was used as the
  narrow fallback. Two hand-authored patch-count attempts and one quoted Perl
  replacement failed without changing files; the resulting diffs were
  rechecked.
- The first focused command failed because uv could not initialize its default
  cache under sandbox permissions. The task-local `UV_CACHE_DIR` correction
  preserved dependency identity. The next focused pass found only Ruff import,
  unused-value, annotation, and line-length errors; after correction 39 R2
  tests and the combined original/R2 focused suites pass.
- The first targeted mypy pass found 21 narrowing and object-conversion errors.
  Explicit type guards and string-normalized numeric conversion fixed them
  without changing lifecycle semantics. A later insertion temporarily placed
  an authorization return inside the live-GitHub verifier; Ruff/mypy caught
  it immediately and the function boundary was corrected before tests.
- A mistakenly named `tests/test_live_inputs.py` focused command ran zero
  tests and failed path resolution. It was corrected to
  `tests/test_agents_v1_live_inputs.py`, after which the combined credential
  and runtime suite passed.
- The first full `make verify` passed formatting, Ruff, and mypy, then finished
  with 915 passing and seven failures. Six nested `uv run` CLI previews
  attempted an isolated package build and failed only because sandbox DNS
  blocked build-dependency retrieval. The seventh correctly detected that the
  new outcome schema raised the registered schema count from 54 to 55; the
  exact-count regression was updated. The public-network rerun and the final
  post-correction wall both passed: Ruff, mypy, all 922 tests, claim and run
  validation, every repository audit, and the compendium release dry run.
- The original R2 draft wrote the endpoint bearer before checking the volume
  encryption observation. That contradicted the R2 custody boundary. Startup
  now performs an authenticated Pod-scoped self-query and requires encrypted
  disposable storage before writing the bearer, then clears the Pod key.
- The original R2 finalizer call preceded credential clearing in one outer
  `finally`; an unexpected finalizer exception could therefore skip clearing.
  Nested finalization now converts that exception to a teardown hard stop and
  clears all selected and generated secret references in its inner
  unconditional cleanup.


## Purpose and intended outcome

Execute AO-0012 as an infrastructure-only feasibility and conformance task.
Define whether the current third-model purpose can be met by an owner-controlled
open-weight, self-operated cloud runtime; prepare a reproducible single-A100
BF16 deployment and public-only calibration package; and stop at one exact
generic owner gate before credential access, model download, provisioning,
endpoint launch, calibration, or spend. This plan does not register DD-023 or
the claim-grade campaign.

## Current state

At `2026-07-30T13:45:35Z`, local and live `main` both resolve to
`6e86b43a8db8d20380dd64bf9490772b7152f484`. No pull request is open; issue
#32 is the only pre-existing open issue. Issue #212 and branch
`agent/treasurebench-open-weight-cloud-runtime` now register AO-0012. Five
unrelated untracked duplicate files are preserved and excluded from every
task-specific stage.

AO-0011 is complete: 500 intended pairings terminalized as 496
protocol-valid, four protocol-invalid, zero provider-operational missing, and
zero provider contract/safety failure; one frozen five-second transient retry
recovered; Methods A/B/C and independent all-pairing bounds passed. Provider
access and the v5 retained root are permanently closed. No DD-023, claim,
scientific run, paper result, ranking, release, submission, or base-campaign
authority exists.

The current base registration fixes 200 public metadata slots, four batches,
five families, five architectures, three repeats, two proprietary provider
families, and one exact open-weight candidate. The exact candidate is
`mistralai/Mistral-Small-3.1-24B-Instruct-2503` at revision
`68faf511d618ef198fef186659617cfd2eb8e33a`; no weight was downloaded. The
historical 16-GB owner host failed the registered environment gate. AO-0012
tests whether physical ownership was an unnecessary proxy for the separable
model-control and serving-stack-control goals.

## DISCUSSION AND DECISION DELTA AUDIT

All 39 pre-existing program-memory records were read before issue or branch
creation. PM-0039 remains implemented and immutable: AO-0011 is complete
engineering evidence only and its explicit-owner-review trigger does not
reopen v5. PM-0010, PM-0014, PM-0015, and PM-0019 remain deferred,
evidence-dependent, or rejected because no claim-grade evidence trigger has
occurred. No adopted item was unrouted, no superseded item became due, and no
raw conversation is retained.

The new owner decision is routed as PM-0040 and this AO-0012 contract. It
separates open-weight model-family diversity, inference-stack transparency,
independence from the two proprietary model providers, owner control, physical
locality, and infrastructure-provider independence. It adopts no scientific
conclusion and creates no external execution authority before the generic
owner gate. Repeat this audit at closeout; no owner decision may remain only in
conversation.

## Scope

1. Audit the existing base registration and state exactly why the third model
   was required without altering the allocation or scientific design.
2. Define five runtime classes and their control, reproducibility, locality,
   and independence properties in a versioned machine-readable record.
3. Audit current official primary sources for the exact Mistral revision,
   license, tokenizer and chat template, recommended vLLM configuration,
   BF16 memory feasibility, immutable vLLM container, CUDA/driver compatibility,
   and RunPod Pod price, API, storage, network, security, retention, lifecycle,
   and recreation controls.
4. Build an authorization-free immutable manifest, fail-closed startup package,
   authenticated endpoint attestation, repository adapter, synthetic
   corruptions, and tests.
5. Freeze ten public tasks, five architectures, one repeat, 50 intended
   pairings, acceptance rules, operational-only outputs, projection formulas,
   and one pending permitted-decision record.
6. Validate, commit, push, open a draft PR, freeze an execution commit, commit
   one generic owner gate, validate it without authorization, and stop.
7. Only after later exact authorization, run the public calibration, teardown,
   reconcile cost and controls, select one permitted decision, and complete
   the public-safe closeout.

## Non-goals

- No DD-023, study, claim, scientific run, evidence or proof promotion.
- No private material, holdout, retained-root access, credential read, model
  download, RunPod API access, provisioning, endpoint, call, or spend before
  owner authorization.
- No base-allocation change, third-model weakening, quantization, sharding,
  alternate model or GPU, managed endpoint, routed API, fallback, or
  autosubstitution.
- No task, family, architecture, or model performance publication; no ranking,
  composite, leaderboard, paper, release, DOI, submission, or upstream change.

## Assumptions

- Official public documentation and unauthenticated metadata are sufficient to
  prepare the feasibility record without downloading weights or reading a
  token.
- The exact registered revision remains the only candidate identity; any
  upstream drift is recorded but never silently adopted.
- One A100 80GB can hold the official BF16 24B weights only if current official
  engine guidance and measured later calibration both pass the frozen
  single-GPU identity.
- RunPod is compute infrastructure, Mistral is model origin, and vLLM is the
  inference engine; these roles remain separately recorded.

## Milestones

- **M0 — complete:** issue, branch, PM-0040, fixed task contract, living
  ExecPlan, master-plan registration, schema validation, and first
  authority-bearing commit.
- **M1 — complete:** existing-design audit, five-class runtime definition, and
  current official-source model/engine/container/CUDA/RunPod feasibility
  record.
- **M2 — complete:** immutable runtime manifest, fail-closed container startup,
  repository endpoint adapter, authenticated attestation, safe telemetry and
  cost ledger, and no-credential deployment package.
- **M3 — complete:** frozen public-only 50-pairing calibration, acceptance,
  permitted-decision record, complete synthetic corruptions, independent
  checks, and focused tests.
- **M4 — complete:** authorization-free full acceptance, clean execution
  commit, push, draft PR, exact-head checks, and protected-tree freeze.
- **M5 — complete:** committed generic owner gate, live validate-only pass,
  schema-valid owner-gate-required handoff, and exact stop.
- **M6 — hard stop before credential ingress:** the exact owner authorization
  succeeded, but the runtime authorization adapter raised `KeyError: 'budget'`
  before `.env.txt`, provider, or resource access.
- **M7 — R5 repair in progress:** the explicit owner amendment permits only
  generic-gate compatibility repair, validation, refreeze, and a new
  unconsumed R5 owner gate. No live retry is authorized.

## Progress checklist

- [x] Read root, planning, master-plan, repository, Agent Operations, scoped,
  DD-010, and GitHub workflow authority.
- [x] Verify local worktree, local and remote main, worktrees, open issues and
  pull requests, GitHub CLI status, and identity collisions.
- [x] Read and reconcile all 39 program-memory records.
- [x] Create issue #212 and branch
  `agent/treasurebench-open-weight-cloud-runtime`.
- [x] Add and validate PM-0040, the fixed contract, living plan, and master
  continuation.
- [x] Complete M1 through M3 sequentially without consequential activity.
- [x] Complete M4 without consequential activity.
- [x] Commit and validate the generic gate and owner-gate-required handoff.
- [x] Stop before every gated action.
- [x] Consume the exact R4 owner direction once, preserve the pre-ingress
  integrity failure, and stop with zero credentials, resources, calls, or spend.

## Discoveries and surprises

- GitHub CLI 2.96.0 is installed but its stored token is invalid. Public list
  operations and SSH transport remain available; issue and PR mutations use the
  connected GitHub integration. The settings-only issue #32 remains separate.
- The existing registration uses `local/open` as a bundled label but its
  machine-readable selection rule actually combines at least six separable
  objectives. AO-0012 must not preserve the bundled wording as if physical
  locality were identical to model or serving-stack independence.
- The first M0 program-memory audit rejected the new descriptive
  `AO-0012-public-calibration-closeout` review token because review classes are
  schema-enumerated. PM-0040 now uses the existing
  `explicit-owner-decision` class; no proposition, route, trigger, or task
  authority changed.
- The second M0 audit rejected `task-contract` as a canonical-destination type.
  Existing TreasureBench program-memory records classify task contracts as
  `decision-record`; PM-0040 now follows that enumerated convention.
- The third M0 audit rejected a reserved future study identifier inside program
  memory. PM-0040 now states the same boundary generically as
  `no scientific-study allocation`, leaving the exact identifier in the task
  contract and plan where it belongs.
- The first combined M0 stage/commit command stopped before staging because the
  sandbox could not create `.git/index.lock`. The task paths remained
  unstaged and no commit was created; the explicit Git operations require the
  repository's approved Git permission.
- The exact Hugging Face revision remains
  `68faf511d618ef198fef186659617cfd2eb8e33a`. Its public metadata records
  96,115,639,662 bytes because it contains both the original 48,022,792,280
  byte consolidated BF16 artifact and a duplicate ten-shard HF-format set.
  AO-0012 pins and checksum-verifies the original Mistral load format, exact
  Tekken tokenizer, and every downloaded small revision file.
- Current vLLM release `0.23.0` supports the exact Mistral3 architecture. The
  selected Linux/amd64 image is
  `sha256:3a1e7f5904e1a1192a02aa0086ceaffc33985d7044c7bb25b3a43d61bdbe3ac0`,
  built from `91df0fad4dc98a67c7659d9dbd915245d5c43d96` with CUDA
  13.0.2 and SM80 support. Startup forces the native vLLM implementation,
  Mistral tokenizer/config/load modes, BF16, one GPU, no request logging, no
  tools, no quantization, and no implementation fallback.
- RunPod's public price for Secure Cloud A100 80GB PCIe is USD 1.39/GPU-hour,
  so six compute hours are USD 8.34 before low storage charges. Its HTTPS
  proxy route is public once exposed; the Pod ID is not treated as a secret,
  and bearer authentication is required for every endpoint operation.
- RunPod documentation says volume encryption is selected at creation and
  returns `volumeEncrypted`, while the current OpenAPI `PodCreateInput` omits
  that property. The package requests encryption and verifies the response,
  then terminates on omission or false. The volume contains public model cache
  only; prompts and raw outputs are prohibited from Pod disk and logs.
- The deterministic public matrix needs 294 normal inference calls, leaving
  106 calls inside the 400-call cap for frozen schema-only repair and bounded
  transport-retry paths. The executor refuses the 401st inference attempt.
- The first focused validation after adding the complete matrix stopped only
  on Ruff import ordering. A second focused validation after adding exact
  billing and teardown tests exposed the same mechanical import-order issue in
  the test module. Both failures are preserved here; import order was corrected
  without changing runtime semantics, after which Ruff, mypy, and all 26
  focused tests passed.
- The first billing implementation supplied a pre-matrix accrued-cost estimate
  to policy-v3 bounds. That was not exact billed-cost reconciliation. Bounds
  now remain pending in memory until the exact post-teardown Pod bill is
  available, then allocate that reconciled amount equally over all 50 intended
  pairings before primary and independent reconstruction.
- The first teardown implementation treated a successful Pod DELETE response
  as sufficient verification. It now requires the exact Pod ID to become
  unaddressable before billing reconciliation; otherwise the calibration fails
  closed and reports that retained-volume deletion is unverified.
- NVIDIA's current CUDA 13.0 release table invalidated the original provisional
  driver allowance: CUDA 13.0 GA requires Linux driver 580.65.06 or newer.
  The manifest, feasibility audit, startup order, attestation validation, and
  tests now reject 535 through 575 hosts before model download and accept only
  a numerically compatible recorded driver.
- The first full `make verify` reached 879 passing tests and four failures in
  legacy pilot synthetic-live tests. Those tests require the current HEAD to be
  present on a remote branch; the AO-0012 implementation head had deliberately
  not yet been pushed. No AO-0012 test failed. This is an expected sequencing
  failure, preserved here and to be rerun after the path-explicit commit and
  branch push.

## Decision log

- `2026-07-30T13:45:35Z`: verify local and live remote main at
  `6e86b43a8db8d20380dd64bf9490772b7152f484`, no open PR, only issue #32
  open, and five unrelated untracked files preserved.
- `2026-07-30T13:45:35Z`: route the new owner decision as PM-0040 and AO-0012;
  preserve PM-0039 and every earlier campaign without access.
- `2026-07-30T13:45:35Z`: classify AO-0012 as infrastructure rather than
  scientific registration or private evaluation. The later public calibration
  is engineering-only and must remain behind the generic owner gate.
- `2026-07-30T13:45:35Z`: freeze the primary identity at RunPod Secure Cloud
  dedicated Pod, one A100 80GB, exact registered Mistral revision, official
  BF16 unquantized weights, pinned vLLM, and an authenticated
  repository-controlled endpoint. Any quantized, sharded, multi-GPU,
  alternate-hardware, managed-endpoint, or routed identity is outside AO-0012.
- `2026-07-30T13:45:35Z`: preserve the first M0 program-memory validation
  failure and use the registry schema's existing `explicit-owner-decision`
  review class instead of expanding stable program-memory policy for one task.
- `2026-07-30T13:45:35Z`: preserve the second M0 validation failure and use the
  existing `decision-record` destination type for the task contract.
- `2026-07-30T13:45:35Z`: preserve the third M0 validation failure and keep the
  program-memory record free of reserved future study identifiers.
- `2026-07-30T13:48:43Z`: complete M0 after Agent Operations accepts 15 task
  contracts with unchanged scientific authority, program memory accepts 40
  records with zero adopted-unrouted or duplicate canonical records, and
  `git diff --check` passes. Begin M1.
- `2026-07-30T13:48:43Z`: preserve the stopped pre-staging Git attempt; rerun
  path-explicit `git add` and `git commit` with approved Git permissions.
- `2026-07-30T22:30:00Z`: freeze runtime-definition version `ow-runtime-v1`
  and class B, `rented-raw-gpu-owner-operated`. It prospectively supplies
  open-weight family diversity, transparent reproducible inference,
  independence from the two proprietary model providers, and owner control;
  it supplies neither physical locality nor complete infrastructure
  independence.
- `2026-07-30T22:30:00Z`: freeze vLLM 0.23.0, the exact Linux/amd64 digest,
  original Mistral BF16 format, CUDA 13.0.2, one A100 80GB PCIe, native-engine
  enforcement, and authenticated attestation as one prospective identity.
  The model-specific minimum remains vLLM 0.8.1; no moving tag is used.
- `2026-07-30T22:30:00Z`: freeze a 120-GB encrypted volume, 50-GB container
  disk, exact artifact verification, bearer-authenticated no-log proxy,
  HMAC-authenticated attestation, 21,600-second deadline, automatic
  termination, and post-termination billing reconciliation.
- `2026-07-30T22:30:00Z`: freeze the ten existing public task commitments,
  five architectures, one repeat, 50 pairings, policy v2 plus the prospective
  self-operated policy-v3 extension, Methods A/B/C, independent bounds,
  operational-only reporting, and no protocol-validity-rate threshold.
- `2026-07-31T23:26:23Z`: correct exact-cost handling so Methods and bounds use
  the post-teardown bill rather than a provisional accrual; require DELETE plus
  exact-Pod absence before billing; add deterministic exact billing aggregation
  and teardown tests; and preserve the superseded implementations above.
- `2026-07-31T23:26:23Z`: correct the CUDA 13.0 host minimum to NVIDIA Linux
  driver 580.65.06, fail before model download on any lower driver, and record
  the correction as an official-source audit finding rather than silently
  preserving an incompatible branch list.
- `2026-07-31T23:26:23Z`: complete the no-network 50-pairing rehearsal with 294
  calls, 50 protocol-valid terminal outcomes, zero missing or runtime failure,
  no circuit-breaker firing, Methods A/B/C agreement, and 72 primary and
  independently reconstructed agreeing bounds. Credential reads, downloads,
  provider calls, GPU provisioning, private state, and spend all remain zero.
- `2026-07-31T23:40:00Z`: local `make verify` passes with 883 tests plus every
  claim, run, program-memory, Agent Operations, paper, publication, naming,
  release, and offline compendium check. Both exact-head GitHub CI runs pass.
  Freeze execution commit `37162565b3a46e495a8764af4979e2a74b03a72f`,
  draft PR #213, and all 19 execution-sensitive tree hashes in the generic
  owner gate; no authorization exists.
- `2026-07-31T23:45:00Z`: the committed generic gate passes live validate-only
  contract, issue, open draft PR, branch, descendant, cap, permission,
  prohibition, expiry, and all 19 protected-tree checks. It reports
  `validated-no-authorization-or-consequential-action-performed`. Complete M5
  and stop exactly once at owner-gate-required.

## Validation strategy

1. Repository JSON Schema validation for the task contract, owner gate, and
   handoff, plus fail-closed machine-readable cross-record validation for the
   runtime definition, feasibility record, manifest, attestation, calibration,
   corruptions, and decision record.
2. Hand-checkable five-class conformance matrix plus independent reconstruction
   of every class/property result.
3. Manifest rejection tests for revision, tokenizer, image digest, GPU,
   quantization, managed endpoint/router, fallback, authentication, logging,
   model/engine drift, malformed attestation, answer/generator access, and
   credential leakage.
4. Synthetic repository-adapter tests for exact action schema,
   protocol-validity policy v2, provider-outcome policy v3 extension, zero
   semantic retry, exact terminal classification, token/latency/throughput/cost
   accounting, and public-only task custody.
5. Complete 50-pairing no-network rehearsal with Methods A/B/C and independent
   bounds, followed by the infrastructure acceptance profile and exact-head CI.
6. Generic owner-gate validation against a clean pushed execution commit and
   live draft-PR ancestry without creating authorization.

## Commands and expected observations

- `make audit-agent-ops` and `make audit-program-memory`: accept AO-0012 and
  PM-0040 with no authority drift.
- Task-specific audit and rehearsal targets added in M2/M3: pass entirely from
  synthetic public fixtures with zero credential, model download, provider
  call, GPU, private, scientific, or spend state.
- `make verify`: preserve all claims, immutable runs, papers, release records,
  prior campaign locks, and closed private/provider boundaries.
- `make owner-gate GATE=reports/agent-ops/AO-0012-open-weight-public-calibration-owner-gate.yml OWNER_GATE_VALIDATE_ONLY=1`: validate the exact live gate and create no authorization.

## Artifacts produced

Issue #212 and the task branch exist. The M0 registration, runtime definition,
official-source feasibility record, immutable manifest, startup and proxy
package, repository adapter, policy-v3 extension, public calibration,
corruptions, focused tests, and pending permitted-decision record exist.

## Blockers

The attempted R4 authorization cannot be reused. The protected runtime expects
a nonexistent `budget` mapping on the generic owner-gate manifest, so it cannot
reach credential ingress safely. An explicit owner amendment must authorize an
additive repair, protected-tree refreeze, and new exact gate. The unrelated
untracked files remain outside AO-0012 and every stage stays path-explicit.

## Recovery and restart instructions

Resume on `agent/treasurebench-open-weight-cloud-runtime`. Read the R4 task
contract, this plan, the R4 hard-stop outcome, and the stop-by-policy handoff;
verify issue #212 and draft PR #213 and preserve the five unrelated untracked
files. Do not reuse the attempted R4 authorization. Never inspect prior
retained roots. No credential, RunPod or authenticated Hugging Face access,
model download, GPU, endpoint, calibration, or spend is permitted without a
new explicit owner amendment and exact prospective gate.

## Outcome and retrospective

R4 selected `calibration-integrity-failure-stop` before credential ingress.
AO-0012 remains open because this is a protected live-path integrity failure,
not a calibrated feasibility decision. There are zero provider resources,
calls, or spend and no teardown or billing ambiguity. A future additive repair
requires explicit owner authority and a new exact gate.
