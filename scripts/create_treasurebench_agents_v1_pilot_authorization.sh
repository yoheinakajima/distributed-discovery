#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  echo "usage: $0 REPOSITORY 100.00" >&2
  exit 2
fi

pilot_repo="$(cd "$1" && pwd -P)"
pilot_cap="$2"
pilot_branch="benchmark/treasurebench-agents-v1-sealed-pilot"

if [[ "$pilot_cap" != "100.00" ]]; then
  echo "the frozen pilot requires the exact total cap 100.00" >&2
  exit 2
fi
if [[ "$(git -C "$pilot_repo" branch --show-current)" != "$pilot_branch" ]]; then
  echo "refusing outside the frozen pilot branch" >&2
  exit 2
fi
if [[ -n "$(git -C "$pilot_repo" status --porcelain --untracked-files=no)" ]]; then
  echo "refusing with tracked working-tree changes" >&2
  exit 2
fi

pilot_commit="$(git -C "$pilot_repo" rev-parse HEAD)"
pilot_remote_commit="$(git -C "$pilot_repo" rev-parse "origin/$pilot_branch")"
if [[ "$pilot_commit" != "$pilot_remote_commit" ]]; then
  echo "local and remote execution commits differ" >&2
  exit 2
fi

pilot_tree_hash="$(
  cd "$pilot_repo"
  PYTHONPATH="$pilot_repo/src" uv run --no-editable python \
    scripts/validate_treasurebench_agents_v1_pilot_authorization.py \
    --repo "$pilot_repo" --print-tree-hash
)"

pilot_config_root="${XDG_CONFIG_HOME:-${HOME}/.config}"
pilot_authorization_dir="$pilot_config_root/distributed-discovery"
pilot_authorization_path="$pilot_authorization_dir/treasurebench-agents-v1-pilot-authorization.yml"
install -d -m 0700 "$pilot_authorization_dir"
cd "$pilot_repo"

PILOT_REPO="$pilot_repo" \
PILOT_COMMIT="$pilot_commit" \
PILOT_TREE_HASH="$pilot_tree_hash" \
PILOT_AUTHORIZATION_PATH="$pilot_authorization_path" \
PYTHONPATH="$pilot_repo/src" \
uv run --no-editable python - <<'PY'
from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

repo = Path(os.environ["PILOT_REPO"])
template = yaml.safe_load(
    (
        repo
        / "docs/benchmark/agents-v1/treasurebench-pilot-authorization-template.yml"
    ).read_text(encoding="utf-8")
)
now = datetime.now(UTC)
template.update(
    {
        "authorization_id": f"tb-agents-v1-pilot-{uuid.uuid4()}",
        "authorization_status": "authorized",
        "authorized_at_utc": now.isoformat(),
        "expires_at_utc": (now + timedelta(days=7)).isoformat(),
        "synthetic": False,
        "owner_attestation": (
            "I authorize this exact frozen engineering pilot, its private custody, "
            "two direct provider routes, retained encrypted traces, and caps only."
        ),
        "authorized_base_commit": "0d3757caf322402c0c47117b3aff0490926a133d",
        "authorized_execution_commit": os.environ["PILOT_COMMIT"],
        "execution_tree_hash": os.environ["PILOT_TREE_HASH"],
        "caps": {
            "total_usd": 100,
            "provider_usd": {"OpenAI": 50, "Anthropic": 50},
            "calls": 5200,
            "input_tokens": 10600000,
            "output_tokens": 1400000,
            "live_concurrency": 2,
        },
        "permissions": {
            "live_provider_calls": True,
            "private_generation": True,
            "encryption": True,
            "unsealing_after_output_lock": True,
            "trace_retention": True,
            "public_redacted_summary": True,
            "claim": False,
            "study": False,
            "scientific_run": False,
            "package": False,
            "arxiv": False,
            "journal": False,
        },
    }
)
target = Path(os.environ["PILOT_AUTHORIZATION_PATH"])
temporary = target.with_suffix(".tmp")
temporary.write_text(yaml.safe_dump(template, sort_keys=False), encoding="utf-8")
temporary.chmod(0o600)
temporary.replace(target)
target.chmod(0o600)
PY

PYTHONPATH="$pilot_repo/src" uv run --no-editable python \
  scripts/validate_treasurebench_agents_v1_pilot_authorization.py \
  --repo "$pilot_repo" --authorization "$pilot_authorization_path"
echo "authorization created and validated at the symbolic XDG configuration path"
