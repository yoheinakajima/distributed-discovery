#!/bin/sh
set -eu
exec uv run --no-editable python -m distributed_discovery.site.build
