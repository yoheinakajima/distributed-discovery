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
  common-source-trap)
    uv run --no-editable python -m distributed_discovery.papers.build_common_source_trap
    ;;
  incentive-to-ignore)
    uv run --no-editable python -m distributed_discovery.papers.build_incentive_to_ignore
    ;;
  all)
    uv run --no-editable python -m distributed_discovery.papers.build_foundations
    uv run --no-editable python -m distributed_discovery.papers.build_three_results
    uv run --no-editable python -m distributed_discovery.papers.build_discovery_institutions
    uv run --no-editable python -m distributed_discovery.papers.build_common_source_trap
    uv run --no-editable python -m distributed_discovery.papers.build_incentive_to_ignore
    ;;
  *)
    echo "unknown paper selection: $selection" >&2
    exit 2
    ;;
esac
