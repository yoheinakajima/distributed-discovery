#!/bin/sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: $0 STUDY_ID [runner arguments...]" >&2
  exit 2
fi
study_id="$1"
shift
case "$study_id" in
  DD-001) exec uv run python -m distributed_discovery.private_teams.study "$@" ;;
  *) echo "no executable runner registered for $study_id" >&2; exit 2 ;;
esac
