#!/bin/sh
set -eu
selection="${1:-all}"
case "$selection" in
  foundations)
    uv run --no-editable python -m distributed_discovery.papers.build_foundations
    ;;
  three-results)
    uv run --no-editable python -m distributed_discovery.papers.build_three_results
    ;;
  discovery-institutions)
    uv run --no-editable python -m distributed_discovery.papers.build_discovery_institutions
    ;;
  all)
    uv run --no-editable python -m distributed_discovery.papers.build_foundations
    uv run --no-editable python -m distributed_discovery.papers.build_three_results
    uv run --no-editable python -m distributed_discovery.papers.build_discovery_institutions
    ;;
  *)
    echo "unknown paper selection: $selection" >&2
    exit 2
    ;;
esac
