"""Seeded synthetic sessions and explicitly bounded audit estimators."""

from __future__ import annotations

import math
import random
from collections import Counter
from typing import Any


def _other(candidate: int, target: int, candidates: int, rng: random.Random) -> int:
    value = rng.randrange(candidates - 1)
    return value if value < target else value + 1


def generate_sessions(
    *,
    candidates: int,
    sessions: int,
    copying_rate: float,
    protocol: str,
    provenance_missing_rate: float,
    matching_error_rate: float,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Generate two-action synthetic sessions with retained ground truth."""
    rng = random.Random(seed)
    session_rows: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    sources = [
        {"source_id": f"source-{index}", "synthetic": True, "source_type": "private-signal"}
        for index in range(candidates)
    ]
    for index in range(sessions):
        target = rng.randrange(candidates)
        if protocol == "consensus":
            first_action = target if rng.random() < 0.75 else _other(0, target, candidates, rng)
            second_action = first_action
        else:
            first_action = target if rng.random() < 0.75 else _other(0, target, candidates, rng)
            second_action = (
                first_action
                if rng.random() < copying_rate
                else (target if rng.random() < 0.75 else _other(0, target, candidates, rng))
            )
        observed_second = second_action
        if rng.random() < matching_error_rate:
            observed_second = rng.randrange(candidates)
        session_id = f"session-{seed}-{index}"
        session_rows.append(
            {
                "session_id": session_id,
                "protocol": protocol,
                "target_id": f"candidate-{target}",
                "synthetic": True,
                "event_count": 2,
            }
        )
        for actor, action in enumerate((first_action, observed_second)):
            events.append(
                {
                    "event_id": f"event-{seed}-{index}-{actor}",
                    "session_id": session_id,
                    "timestamp": f"2026-01-01T00:{index // 60:02d}:{index % 60:02d}Z",
                    "actor_id": f"agent-{actor}",
                    "candidate_id": f"candidate-{action}",
                    "action_id": f"candidate-{action}",
                    "source_id": None
                    if rng.random() < provenance_missing_rate
                    else f"source-{action}",
                    "outcome": {"success": action == target, "observed": True},
                    "synthetic": True,
                }
            )
    return session_rows, events, sources


def audit_events(events: list[dict[str, Any]], candidates: int) -> dict[str, float]:
    """Return descriptive and model-based values for complete two-action sessions."""
    by_session: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        by_session.setdefault(str(event["session_id"]), []).append(event)
    pairs = [pair for pair in by_session.values() if len(pair) == 2]
    agreement = sum(pair[0]["action_id"] == pair[1]["action_id"] for pair in pairs) / len(pairs)
    # Independent private actions agree above 1/M because both respond to the
    # common latent target: 3/4^2 + (1/4)^2/(M-1) in this registered generator.
    baseline = 0.75**2 + 0.25**2 / (candidates - 1)
    copying = (agreement - baseline) / (1 - baseline)
    standard_error = math.sqrt(agreement * (1 - agreement) / len(pairs)) / (1 - baseline)
    ci_low = max(0.0, copying - 1.96 * standard_error)
    ci_high = min(1.0, copying + 1.96 * standard_error)
    counts = Counter(str(event["action_id"]) for event in events)
    total = len(events)
    action_hhi = sum((count / total) ** 2 for count in counts.values())
    source_missing = sum(event["source_id"] is None for event in events) / total
    discovery = sum(bool(event["outcome"]["success"]) for event in events) / total
    return {
        "agreement": agreement,
        "copying_estimate": copying,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "action_hhi": action_hhi,
        "source_missing_rate": source_missing,
        "observed_success_rate": discovery,
    }
