.PHONY: bootstrap lint typecheck test fetch-upstream reproduce-baseline upstream-patch validate-claims foundations three-results discovery-institutions common-source-trap incentive-to-ignore canonical-exact-frontier dd001 dd001-signatures dd001-thresholds dd001-alignment-bound dd002-disclosure dd002-selection-robustness dd003-source-graphs dd003-heterogeneous-sources dd004-sequential dd005-coverage dd006-mechanisms dd006-general-frontier dd006b-joint-mechanism dd007-synthetic-audit dd008-acquisition dd008a-acquisition dd008b-analysis dd009-atlas dd010-discoverybench dd010-attention dd010-threshold dd011-experiment dd011-attention dd012-attention dd013-audience dd014-conditional dd015-preview dd015-dynamic dd015-threshold-preview dd015-threshold-extension dd016-threshold dd017-equilibrium dd018-preview dd018-team-mechanisms papers site verify all clean

UV := uv
export PYTHONPATH := $(CURDIR)/src
RUN := $(UV) run --no-editable
PY := $(RUN) python

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

papers:
	./scripts/build_papers.sh all

site:
	./scripts/build_site.sh

verify: lint typecheck test validate-claims

all: verify reproduce-baseline papers site

clean:
	rm -rf build site/dist .pytest_cache .mypy_cache .ruff_cache
