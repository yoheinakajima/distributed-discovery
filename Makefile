.PHONY: bootstrap lint typecheck test fetch-upstream reproduce-baseline upstream-patch validate-claims foundations three-results canonical-exact-frontier dd001 dd001-signatures dd001-thresholds dd001-alignment-bound dd002-disclosure dd002-selection-robustness dd003-source-graphs dd003-heterogeneous-sources papers site verify all clean

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

papers:
	./scripts/build_papers.sh all

site:
	./scripts/build_site.sh

verify: lint typecheck test validate-claims

all: verify reproduce-baseline papers site

clean:
	rm -rf build site/dist .pytest_cache .mypy_cache .ruff_cache
