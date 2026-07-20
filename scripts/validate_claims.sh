#!/bin/sh
set -eu
export PYTHONPATH="$(pwd)/src"
exec uv run --no-editable python -m distributed_discovery.validation.claims "$@"
