#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "usage: $0 REPOSITORY" >&2
  exit 2
fi

diagnostic_repo="$(cd "$1" && pwd -P)"
diagnostic_branch="benchmark/treasurebench-agents-v1-pilot-repair"

if [[ "$(git -C "$diagnostic_repo" branch --show-current)" != "$diagnostic_branch" ]]; then
  echo "refusing outside the exact pilot-repair branch" >&2
  exit 2
fi
if [[ -n "$(git -C "$diagnostic_repo" status --porcelain --untracked-files=no)" ]]; then
  echo "refusing with tracked working-tree changes" >&2
  exit 2
fi

diagnostic_commit="$(git -C "$diagnostic_repo" rev-parse HEAD)"
diagnostic_remote_commit="$(
  git -C "$diagnostic_repo" rev-parse "origin/$diagnostic_branch"
)"
if [[ "$diagnostic_commit" != "$diagnostic_remote_commit" ]]; then
  echo "local and remote diagnostic commits differ" >&2
  exit 2
fi

diagnostic_tree_hash="$(
  cd "$diagnostic_repo"
  PYTHONPATH="$diagnostic_repo/src" uv run --no-editable python \
    scripts/validate_treasurebench_pilot_diagnostic_authorization.py \
    --repo "$diagnostic_repo" --print-tree-hash
)"

confirm_yes() {
  local confirmation_prompt="$1"
  local confirmation_answer
  printf '%s Type YES to confirm: ' "$confirmation_prompt"
  IFS= read -r confirmation_answer
  if [[ "$confirmation_answer" != "YES" ]]; then
    echo "authorization not created" >&2
    exit 2
  fi
}

confirm_yes "1/8 Read-only access to the retained locked audit package."
confirm_yes "2/8 Verify the original output lock and custody commitments."
confirm_yes "3/8 Inspect exactly 500 private run traces for aggregate action cardinality and contract conformance."
confirm_yes "4/8 Diagnose exactly two provider errors with only their minimum trace context."
confirm_yes "5/8 Keep all metric sensitivity and detailed performance analysis private."
confirm_yes "6/8 Make no provider call, authorize no spend, and create no new private material."
confirm_yes "7/8 Mutate no retained private-state file, ledger, trace, ciphertext, or lock."
confirm_yes "8/8 Publish no raw task, prompt, output, answer, seed, key, trace, identifier, or performance; emit only a redacted candidate."

diagnostic_config_root="${XDG_CONFIG_HOME:-${HOME}/.config}"
diagnostic_authorization_dir="$diagnostic_config_root/distributed-discovery"
diagnostic_authorization_file="$diagnostic_authorization_dir/treasurebench-agents-v1-pilot-diagnostic-authorization.yml"
install -d -m 0700 "$diagnostic_authorization_dir"

DIAGNOSTIC_REPOSITORY="$diagnostic_repo" \
DIAGNOSTIC_COMMIT="$diagnostic_commit" \
DIAGNOSTIC_TREE_HASH="$diagnostic_tree_hash" \
DIAGNOSTIC_AUTHORIZATION_FILE="$diagnostic_authorization_file" \
PYTHONPATH="$diagnostic_repo/src" \
uv run --no-editable python - <<'PY'
from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

repo = Path(os.environ["DIAGNOSTIC_REPOSITORY"])
template = yaml.safe_load(
    (
        repo
        / "docs/benchmark/agents-v1/pilot-diagnostic-authorization-template.yml"
    ).read_text(encoding="utf-8")
)
authorization_id = f"tb-pilot-diagnostic-{uuid.uuid4()}"
now = datetime.now(UTC)
template.update(
    {
        "authorization_id": authorization_id,
        "authorization_status": "authorized",
        "authorized_at_utc": now.isoformat(),
        "expires_at_utc": (now + timedelta(hours=24)).isoformat(),
        "synthetic": False,
        "owner_attestation": (
            "I explicitly authorize this exact nonsynthetic, read-only, zero-call "
            "diagnosis of the two retained TreasureBench pilot provider errors and "
            "aggregate action-budget contract conformance across exactly 500 private "
            "run traces, with private sensitivity only, no retained-state mutation, "
            "and only redacted public output."
        ),
        "owner_confirmations": {
            "retained_audit_read_only": True,
            "verify_original_lock_and_custody": True,
            "inspect_exactly_500_run_traces_for_action_cardinality": True,
            "diagnose_exactly_two_provider_errors_with_minimum_context": True,
            "private_metric_sensitivity_only": True,
            "no_provider_call_spend_or_new_private_material": True,
            "no_private_state_mutation": True,
            "no_raw_private_publication_and_redacted_output_only": True,
        },
        "diagnostic_commit": os.environ["DIAGNOSTIC_COMMIT"],
        "diagnostic_tree_hash": os.environ["DIAGNOSTIC_TREE_HASH"],
        "private_detail_output_symbolic_path": (
            "XDG_STATE_HOME/distributed-discovery/treasurebench-agents-v1/"
            f"diagnostics/pilot-repair/{authorization_id}.json"
        ),
        "permissions": {
            "read_retained_state": True,
            "verify_output_lock": True,
            "verify_custody_and_logs": True,
            "decrypt_final_audit_package": True,
            "decrypt_two_error_records": True,
            "decrypt_exactly_500_private_run_traces": True,
            "decrypt_locked_task_answer_for_sensitivity": True,
            "aggregate_action_cardinalities": True,
            "compute_private_metric_sensitivity": True,
            "write_private_detail_outside_retained_root": True,
            "emit_redacted_public_candidate": True,
            "provider_calls": False,
            "credential_access": False,
            "generate_seed_task_answer_key_or_batch": False,
            "mutate_retained_private_state": False,
            "publish_raw_private_content": False,
        },
    }
)
target = Path(os.environ["DIAGNOSTIC_AUTHORIZATION_FILE"])
flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
if hasattr(os, "O_NOFOLLOW"):
    flags |= os.O_NOFOLLOW
descriptor = os.open(target, flags, 0o600)
try:
    os.fchmod(descriptor, 0o600)
    payload = yaml.safe_dump(template, sort_keys=False).encode()
    offset = 0
    while offset < len(payload):
        offset += os.write(descriptor, payload[offset:])
    os.fsync(descriptor)
finally:
    os.close(descriptor)
PY

cd "$diagnostic_repo"
PYTHONPATH="$diagnostic_repo/src" uv run --no-editable python \
  scripts/validate_treasurebench_pilot_diagnostic_authorization.py \
  --repo "$diagnostic_repo"
echo "read-only diagnostic authorization created and validated at the symbolic XDG configuration path"
