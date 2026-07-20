#!/bin/sh
set -eu
selection="${1:-all}"
case "$selection" in
  foundations|all)
    uv run --no-editable python -m distributed_discovery.papers.build_foundations
    ;;
  *)
    echo "unknown paper selection: $selection" >&2
    exit 2
    ;;
esac
