.PHONY: bootstrap lint typecheck test fetch-upstream reproduce-baseline upstream-patch validate-claims foundations dd001 papers site verify all clean

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
	$(PY) -m distributed_discovery.private_teams.study --config studies/DD-001-private-information-teams/configs/baseline.yml

papers:
	./scripts/build_papers.sh all

site:
	./scripts/build_site.sh

verify: lint typecheck test validate-claims

all: verify reproduce-baseline papers site

clean:
	rm -rf build site/dist .pytest_cache .mypy_cache .ruff_cache
