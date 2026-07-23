#!/usr/bin/env python3
"""Run the offline DiscoveryBench Agents v1 registration audit."""

from __future__ import annotations

import json
from pathlib import Path

from distributed_discovery.benchmark.agents import audit_registration

ROOT = Path(__file__).resolve().parents[1]


if __name__ == "__main__":
    print(json.dumps(audit_registration(ROOT), sort_keys=True))
