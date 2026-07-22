"""Independent exact verification and adversarial gates for DD-022."""

from __future__ import annotations

import copy
from collections import Counter
from fractions import Fraction
from typing import Any

from distributed_discovery.coordination_free_sharing import exact, private_game, shared_game
from distributed_discovery.coordination_free_sharing.equilibrium import (
    private_correspondence_record,
    shared_pure_correspondence,
)
from distributed_discovery.coordination_free_sharing.model import (
    joint_probability,
    posterior,
    serialize,
)
from distributed_discovery.coordination_free_sharing.thresholds import certificate, polynomial


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def _row(p: Fraction, rho: Fraction) -> dict[str, Any]:
    private_selection = private_game.selected_equilibrium(p, rho)
    shared_selection = shared_game.selected_equilibrium(p, rho)
    private_closed = private_game.selected_metrics(p, rho)
    shared_closed = shared_game.metrics(p, rho)
    private_direct = exact.private_selected_equilibrium(p, rho)
    private_enumerated = exact.private_metrics(p, rho, private_direct.probability)
    shared_enumerated = exact.shared_metrics(p, rho)
    gain = shared_closed.discovery - private_closed.discovery
    return {
        "accuracy": p,
        "dependence": rho,
        "dependence_index": private_game.dependence_index(p, rho),
        "private_selection": private_selection,
        "shared_selection": shared_selection,
        "private_metrics": private_closed.record(),
        "shared_metrics": shared_closed.record(),
        "direct_private_metrics": private_game.direct_private_metrics(p, rho).record(),
        "selected_sharing_gain": gain,
        "gain_class": "positive" if gain > 0 else "negative" if gain < 0 else "neutral",
        "private_correspondence": private_correspondence_record(p, rho),
        "shared_pure_correspondence": shared_pure_correspondence(p, rho),
        "checks": {
            "private_selection_agreement": private_selection.follow_probability
            == private_direct.probability,
            "private_metric_agreement": private_closed == private_enumerated,
            "shared_metric_agreement": shared_closed == shared_enumerated,
            "payoff_budget_private": 2 * private_closed.payoff_per_agent
            == private_closed.discovery,
            "payoff_budget_shared": 2 * shared_closed.payoff_per_agent == shared_closed.discovery,
            "metric_bounds": all(
                0 <= value <= 1
                for value in (
                    private_closed.discovery,
                    private_closed.collision,
                    private_closed.average_action_quality,
                    shared_closed.discovery,
                    shared_closed.collision,
                    shared_closed.average_action_quality,
                )
            ),
            "centralized_bound": private_closed.discovery <= 1 and shared_closed.discovery <= 1,
        },
    }


def _canonical_checks(rows: list[dict[str, Any]]) -> dict[str, bool]:
    canonical = {row["dependence"]: row for row in rows if row["accuracy"] == Fraction(3, 5)}
    threshold = Fraction(7, 12)
    shared_threshold = Fraction(1, 6)
    checks = {
        "canonical_slice_complete": len(canonical) == 7,
        "private_boundary": canonical[threshold]["private_selection"].follow_probability == 1,
        "shared_boundary": canonical[shared_threshold][
            "shared_selection"
        ].agreement_action_probability
        == 1,
        "positive_registered_witness": canonical[Fraction(3, 4)]["selected_sharing_gain"] > 0,
        "negative_registered_witness": canonical[Fraction(1, 2)]["selected_sharing_gain"] < 0,
        "rho_one_neutral": canonical[Fraction(1)]["selected_sharing_gain"] == 0,
        "constant_split_private_equilibrium": all(
            row["private_correspondence"]["best_pure_discovery"] == 1 for row in canonical.values()
        ),
        "selection_dependence_exposed": any(
            row["private_correspondence"]["best_pure_discovery"]
            > row["private_metrics"]["discovery"]
            for row in canonical.values()
        ),
    }
    return checks


def _corruptions(rows: list[dict[str, Any]], source_checksum: str) -> dict[str, bool]:
    sample = next(
        row
        for row in rows
        if row["accuracy"] == Fraction(3, 5) and row["dependence"] == Fraction(3, 4)
    )
    bad = copy.deepcopy(sample)
    bad["shared_metrics"]["discovery"] += Fraction(1, 1000)
    lower, upper = certificate()["isolating_interval"]
    return {
        "source_mixture_probability": sum(
            joint_probability(theta, first, second, Fraction(3, 5), Fraction(1, 2))
            for theta in (0, 1)
            for first in (0, 1)
            for second in (0, 1)
        )
        == 1,
        "posterior": posterior(0, 1, Fraction(3, 5), Fraction(1, 2))
        == (Fraction(1, 2), Fraction(1, 2)),
        "private_best_response": exact.private_payoff_difference(
            Fraction(3, 5), Fraction(3, 4), sample["private_selection"].follow_probability
        )
        == 0,
        "shared_support": sample["shared_selection"].agreement_action_probability < 1,
        "threshold_polynomial": polynomial(Fraction(1, 2)) < 0 < polynomial(Fraction(7, 12)),
        "root_interval": polynomial(lower) < 0 < polynomial(upper),
        "discovery": bad["shared_metrics"]["discovery"]
        != exact.shared_metrics(Fraction(3, 5), Fraction(3, 4)).discovery,
        "equilibrium_label": sample["private_selection"].regime != "corrupted-follow",
        "implementation_gap": sample["shared_metrics"]["implementation_gap"]
        == 1 - sample["shared_metrics"]["discovery"],
        "source_checksum": source_checksum != "0" * 64 and len(source_checksum) == 64,
    }


def build(config: dict[str, Any], source_checksum: str) -> dict[str, Any]:
    accuracies = [parse_fraction(value) for value in config["accuracies"]]
    dependence = [parse_fraction(value) for value in config["dependence"]]
    rows = [_row(p, rho) for p in accuracies for rho in dependence]
    row_checks = [row["checks"] for row in rows]
    canonical_checks = _canonical_checks(rows)
    root_certificate = certificate()
    verification = {
        "registered_cells": len(rows) == config["cells"] == len(accuracies) * len(dependence),
        "row_checks": all(all(checks.values()) for checks in row_checks),
        "canonical_checks": all(canonical_checks.values()),
        "threshold_certificate": root_certificate["passed"],
        "canonical_detail": canonical_checks,
    }
    verification["passed"] = all(
        value for key, value in verification.items() if key not in {"canonical_detail", "passed"}
    )
    corruptions = _corruptions(rows, source_checksum)
    classes = Counter(row["gain_class"] for row in rows)
    summary = {
        "cells": len(rows),
        "accuracy_values": len(accuracies),
        "dependence_values": len(dependence),
        "gain_class_counts": dict(sorted(classes.items())),
        "canonical_accuracy": Fraction(3, 5),
        "private_regime_boundary": Fraction(7, 12),
        "shared_regime_boundary": Fraction(1, 6),
        "positive_root": "(5*sqrt(73)-17)/48",
        "root_isolating_interval": root_certificate["isolating_interval"],
        "source_checksum_sha256": source_checksum,
        "selection_scope": "posterior-only-provenance-blind-identical-mixing",
        "selection_dependence": True,
    }
    return {
        "rows": serialize(rows),
        "raw_rows": rows,
        "verification": verification,
        "corruptions": corruptions,
        "threshold_certificate": root_certificate,
        "summary": summary,
    }
