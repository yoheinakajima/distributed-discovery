.PHONY: bootstrap lint typecheck test fetch-upstream reproduce-baseline upstream-patch validate-claims audit-editorial audit-program-memory audit-publication-infrastructure audit-treasurebench-naming release-readiness compendium-release-dry-run verify-compendium-release compendium-release-readiness audit-agents-v1 audit-agents-v1-evaluation agents-v1-dry-run agents-v1-readiness agents-v1-provider-preflight agents-v1-public-calibration agents-v1-provider-preflight-all treasurebench-pilot-audit treasurebench-pilot-offline-readiness treasurebench-pilot-live treasurebench-pilot-verify treasurebench-pilot-redacted-summary treasurebench-pilot-rehearsal foundations three-results discovery-institutions common-source-trap incentive-to-ignore threshold-discovery information-sharing-frontier canonical-exact-frontier dd001 dd001-signatures dd001-thresholds dd001-alignment-bound dd002-disclosure dd002-selection-robustness dd003-source-graphs dd003-heterogeneous-sources dd004-sequential dd005-coverage dd006-mechanisms dd006-general-frontier dd006b-joint-mechanism dd007-synthetic-audit dd008-acquisition dd008a-acquisition dd008b-analysis dd009-atlas dd010-discoverybench dd010-attention dd010-threshold dd011-experiment dd011-attention dd011-threshold-dynamic dd012-attention dd013-audience dd014-conditional dd015-preview dd015-dynamic dd015-threshold-preview dd015-threshold-extension dd016-threshold dd017-equilibrium dd018-preview dd018-team-mechanisms dd019-preview dd019-signal-geometry dd020-preview dd020-incremental-sharing dd021-preview dd021-general-sharing-frontier dd022-preview dd022-coordination-free-positive-sharing papers site verify all clean

UV := uv
export PYTHONPATH := $(CURDIR)/src
RUN := $(UV) run --no-editable
PY := $(RUN) python
VERSION ?= 0.1.0
RELEASE_SOURCE_REVISION ?= $(shell git rev-parse HEAD)
RELEASE_GENERATED_UTC ?= 2026-07-24T00:00:00Z
COMPENDIUM_RELEASE_DIR ?= build/compendium-release/$(VERSION)

bootstrap:
	$(UV) sync --locked --no-editable
	$(PY) -m distributed_discovery.validation.bootstrap
	$(PY) -m distributed_discovery.validation.claims --fixture

lint:
	$(RUN) ruff format --check .
	$(RUN) ruff check .

typecheck:
	$(RUN) mypy

test:
	$(RUN) pytest

fetch-upstream:
	./scripts/fetch_upstream.sh

reproduce-baseline:
	$(PY) -m distributed_discovery.canonical.reproduce

upstream-patch: fetch-upstream
	$(PY) scripts/update_upstream_patch.py

validate-claims:
	$(PY) -m distributed_discovery.validation.claims
	$(PY) -m distributed_discovery.validation.runs

audit-editorial:
	$(PY) scripts/audit_literature_transmission.py
	$(PY) scripts/audit_claim_prominence.py
	$(PY) scripts/audit_optionality_portfolio.py
	$(PY) scripts/audit_translation_concordance.py
	$(PY) scripts/audit_paper_lifecycle.py
	$(PY) scripts/audit_paper_claim_roles.py
	$(PY) scripts/audit_paper_recomposition.py
	$(PY) scripts/audit_phase2_prospectus_schemas.py
	$(PY) scripts/audit_discoverybench_agents_v1.py

audit-program-memory:
	$(PY) scripts/audit_program_memory.py

audit-publication-infrastructure:
	$(PY) scripts/audit_paper_dependencies.py
	$(PY) scripts/audit_publication_infrastructure.py

audit-treasurebench-naming:
	$(PY) scripts/audit_treasurebench_naming.py

release-readiness:
	$(PY) scripts/audit_release_readiness.py

compendium-release-dry-run:
	$(PY) scripts/build_compendium_release.py --version $(VERSION) --source-revision $(RELEASE_SOURCE_REVISION) --output-dir $(COMPENDIUM_RELEASE_DIR) --mode dry-run --generated-utc $(RELEASE_GENERATED_UTC)

verify-compendium-release:
	$(PY) scripts/verify_compendium_release.py --version $(VERSION) --output-dir $(COMPENDIUM_RELEASE_DIR)

compendium-release-readiness: compendium-release-dry-run verify-compendium-release
	$(RUN) pytest -q tests/unit/test_compendium_release.py

audit-agents-v1:
	$(PY) scripts/audit_discoverybench_agents_v1.py

audit-agents-v1-evaluation:
	$(PY) scripts/audit_discoverybench_agents_v1_evaluation.py

agents-v1-dry-run:
	$(PY) -m distributed_discovery.cli agents-v1 dry-run

agents-v1-readiness:
	$(PY) -m distributed_discovery.cli agents-v1 readiness

agents-v1-provider-preflight:
	$(PY) -m distributed_discovery.cli agents-v1 provider-preflight

agents-v1-public-calibration:
	$(PY) -m distributed_discovery.cli agents-v1 public-calibration

agents-v1-provider-preflight-all:
	$(PY) -m distributed_discovery.cli agents-v1 provider-preflight-all

treasurebench-pilot-audit:
	$(PY) scripts/audit_treasurebench_agents_v1_pilot.py

treasurebench-pilot-offline-readiness:
	$(PY) -m distributed_discovery.cli treasurebench pilot-offline-readiness

treasurebench-pilot-live:
	$(PY) -m distributed_discovery.cli treasurebench pilot-live

treasurebench-pilot-verify:
	$(PY) -m distributed_discovery.cli treasurebench pilot-verify

treasurebench-pilot-redacted-summary:
	$(PY) -m distributed_discovery.cli treasurebench pilot-redacted-summary

treasurebench-pilot-rehearsal:
	$(PY) -m distributed_discovery.cli treasurebench pilot-rehearsal

foundations:
	./scripts/build_papers.sh foundations

three-results:
	./scripts/build_papers.sh three-results

discovery-institutions:
	./scripts/build_papers.sh discovery-institutions

common-source-trap:
	./scripts/build_papers.sh common-source-trap

incentive-to-ignore:
	./scripts/build_papers.sh incentive-to-ignore

threshold-discovery:
	./scripts/build_papers.sh threshold-discovery

information-sharing-frontier:
	./scripts/build_papers.sh information-sharing-frontier

canonical-exact-frontier:
	$(PY) -m distributed_discovery.canonical.exact_frontier_study

dd001:
	$(PY) -m distributed_discovery.private_teams.study

dd001-signatures:
	$(PY) -m distributed_discovery.private_teams.signature_study

dd001-thresholds:
	$(PY) -m distributed_discovery.private_teams.threshold_study

dd001-alignment-bound:
	$(PY) -m distributed_discovery.private_teams.alignment_bound_study

dd002-disclosure:
	$(PY) -m distributed_discovery.information_design.study

dd002-selection-robustness:
	$(PY) -m distributed_discovery.information_design.selection_study

dd003-source-graphs:
	$(PY) -m distributed_discovery.source_networks.study

dd003-heterogeneous-sources:
	$(PY) -m distributed_discovery.source_networks.heterogeneous_study

dd004-sequential:
	$(PY) -m distributed_discovery.sequential.study

dd005-coverage:
	$(PY) -m distributed_discovery.coverage.study

dd006-mechanisms:
	$(PY) -m distributed_discovery.mechanisms.study

dd006-general-frontier:
	$(PY) -m distributed_discovery.mechanisms.general_study

dd006b-joint-mechanism:
	$(PY) -m distributed_discovery.mechanisms.joint_study

dd008-acquisition:
	$(PY) -m distributed_discovery.acquisition.study

dd008a-acquisition:
	$(PY) -m distributed_discovery.acquisition.n_agent_study

dd008b-analysis:
	$(PY) -m distributed_discovery.acquisition.common_source_study

dd007-synthetic-audit:
	$(PY) -m distributed_discovery.audits.study

dd009-atlas:
	$(PY) -m distributed_discovery.atlas.study

dd010-discoverybench:
	$(PY) -m distributed_discovery.benchmark.study

dd010-attention:
	$(PY) -m distributed_discovery.benchmark.attention_study

dd010-threshold:
	$(PY) -m distributed_discovery.benchmark.threshold_study

dd011-experiment:
	$(PY) -m distributed_discovery.experimental_design.study

dd011-attention:
	$(PY) -m distributed_discovery.experimental_design.attention_study

dd011-threshold-dynamic:
	$(PY) -m distributed_discovery.experimental_design.threshold_dynamic_study

dd012-attention:
	$(PY) -m distributed_discovery.attention.study

dd013-audience:
	$(PY) -m distributed_discovery.audience.study

dd014-conditional:
	$(PY) -m distributed_discovery.conditional.study

dd015-preview:
	$(PY) -m distributed_discovery.dynamic_attention.study --preview

dd015-dynamic:
	$(PY) -m distributed_discovery.dynamic_attention.study

dd015-threshold-preview:
	$(PY) -m distributed_discovery.dynamic_attention.threshold_extension --preview

dd015-threshold-extension:
	$(PY) -m distributed_discovery.dynamic_attention.threshold_extension

dd016-threshold:
	$(PY) -m distributed_discovery.threshold_discovery.study

dd017-equilibrium:
	$(PY) -m distributed_discovery.threshold_equilibrium.study

dd018-preview:
	$(PY) -m distributed_discovery.team_mechanisms.study --preview

dd018-team-mechanisms:
	$(PY) -m distributed_discovery.team_mechanisms.study

dd019-preview:
	$(PY) -m distributed_discovery.signal_geometry.study --preview

dd019-signal-geometry:
	$(PY) -m distributed_discovery.signal_geometry.study

dd020-preview:
	$(PY) -m distributed_discovery.incremental_sharing.study --preview

dd020-incremental-sharing:
	$(PY) -m distributed_discovery.incremental_sharing.study

dd021-preview:
	$(PY) -m distributed_discovery.general_sharing.study --preview

dd021-general-sharing-frontier:
	$(PY) -m distributed_discovery.general_sharing.study

dd022-preview:
	$(PY) -m distributed_discovery.coordination_free_sharing.study --preview

dd022-coordination-free-positive-sharing:
	$(PY) -m distributed_discovery.coordination_free_sharing.study

papers:
	./scripts/build_papers.sh all

site:
	./scripts/build_site.sh

verify: lint typecheck test validate-claims audit-editorial audit-program-memory audit-publication-infrastructure audit-treasurebench-naming release-readiness compendium-release-readiness

all: verify reproduce-baseline papers site

clean:
	rm -rf build site/dist .pytest_cache .mypy_cache .ruff_cache
