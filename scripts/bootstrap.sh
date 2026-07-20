#!/bin/sh
set -eu
uv sync --locked
uv run python -m distributed_discovery.validation.bootstrap
uv run python -m distributed_discovery.validation.claims --fixture
