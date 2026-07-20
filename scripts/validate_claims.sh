#!/bin/sh
set -eu
exec uv run python -m distributed_discovery.validation.claims "$@"
