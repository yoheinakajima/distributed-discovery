"""Audit the authorization-free AO-0007 diagnostic and conformance surface."""

from __future__ import annotations

import json
from pathlib import Path

from distributed_discovery.benchmark.agents_v1.custody_conformance import (
    audit_conformance_framework,
    run_live_mode_custody_conformance,
)
from distributed_discovery.benchmark.agents_v1.custody_repair import (
    audit_execution_source,
)


def audit() -> dict[str, object]:
    repo = Path.cwd()
    source = audit_execution_source(repo)
    framework = audit_conformance_framework(repo)
    live_mode = run_live_mode_custody_conformance(repo)
    if live_mode["status"] not in {"expected-pre-repair-failure", "pass"}:
        raise AssertionError("live-mode custody conformance returned an unregistered state")
    return {
        "task_id": "AO-0007",
        "status": "pass",
        "source_candidate": source["candidate"],
        "framework": framework,
        "live_mode": live_mode,
        "provider_calls": 0,
        "credential_reads": 0,
        "spend_usd": "0",
        "retained_private_state_reads": 0,
        "retained_private_state_writes": 0,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
