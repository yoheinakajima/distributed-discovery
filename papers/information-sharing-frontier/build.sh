#!/bin/sh
set -eu
root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$root"
exec uv run --no-editable python -m distributed_discovery.papers.build_information_sharing_frontier
