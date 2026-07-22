#!/bin/sh
set -eu
root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$root"
uv run --no-editable python scripts/audit_information_sharing_frontier_paper.py
uv run --no-editable pytest -q tests/integration/test_information_sharing_frontier_paper.py
