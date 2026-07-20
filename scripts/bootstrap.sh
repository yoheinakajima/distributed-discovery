#!/bin/sh
set -eu
export PYTHONPATH="$(pwd)/src"
uv sync --locked --no-editable
uv run --no-editable python -m distributed_discovery.validation.bootstrap
uv run --no-editable python -m distributed_discovery.validation.claims --fixture
