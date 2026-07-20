.PHONY: bootstrap lint typecheck test fetch-upstream reproduce-baseline upstream-patch validate-claims foundations dd001 dd001-signatures dd001-thresholds dd002-disclosure papers site verify all clean

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

dd001:
	$(PY) -m distributed_discovery.private_teams.study

dd001-signatures:
	$(PY) -m distributed_discovery.private_teams.signature_study

dd001-thresholds:
	$(PY) -m distributed_discovery.private_teams.threshold_study

dd002-disclosure:
	$(PY) -m distributed_discovery.information_design.study

papers:
	./scripts/build_papers.sh all

site:
	./scripts/build_site.sh

verify: lint typecheck test validate-claims

all: verify reproduce-baseline papers site

clean:
	rm -rf build site/dist .pytest_cache .mypy_cache .ruff_cache
