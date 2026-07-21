"""Independent exact verifier for the DD-003 colored-source census."""

from __future__ import annotations

import itertools
from collections import defaultdict, deque
from fractions import Fraction
from typing import Any

Network = tuple[tuple[Fraction, tuple[int, ...]], ...]
Signature = tuple[Fraction, ...]


def _valid(network: Network) -> bool:
    return all(sum(row) > 0 for _, row in network) and all(
        sum(row[column] for _, row in network) > 0 for column in range(4)
    )


def _permute(
    network: Network, source_order: tuple[int, ...], searcher_order: tuple[int, ...]
) -> Network:
    return tuple(
        (
            network[source][0],
            tuple(network[source][1][searcher] for searcher in searcher_order),
        )
        for source in source_order
    )


def _equivalent(left: Network, right: Network) -> bool:
    if len(left) != len(right):
        return False
    return any(
        _permute(left, source_order, searcher_order) == right
        for source_order in itertools.permutations(range(len(left)))
        for searcher_order in itertools.permutations(range(4))
    )


def _valid_graphs(sources: int) -> list[tuple[tuple[int, ...], ...]]:
    result = []
    for bits in itertools.product((0, 1), repeat=sources * 4):
        graph = tuple(
            tuple(bits[source * 4 + searcher] for searcher in range(4)) for source in range(sources)
        )
        if all(sum(row) > 0 for row in graph) and all(
            sum(row[searcher] for row in graph) > 0 for searcher in range(4)
        ):
            result.append(graph)
    return result


def _assignments(levels: tuple[Fraction, ...], sources: int) -> list[tuple[Fraction, ...]]:
    return sorted(
        assignment
        for assignment in set(itertools.product(levels, repeat=sources))
        if set(assignment) == set(levels)
    )


def _labeled_networks(levels: tuple[Fraction, ...], sources: int) -> set[Network]:
    return {
        tuple((accuracy, row) for accuracy, row in zip(assignment, graph, strict=True))
        for graph in _valid_graphs(sources)
        for assignment in _assignments(levels, sources)
    }


def _orbit_count(levels: tuple[Fraction, ...], sources: int) -> int:
    unseen = _labeled_networks(levels, sources)
    count = 0
    while unseen:
        count += 1
        queue = deque([unseen.pop()])
        while queue:
            network = queue.popleft()
            neighbors = []
            for index in range(sources - 1):
                order = list(range(sources))
                order[index], order[index + 1] = order[index + 1], order[index]
                neighbors.append(_permute(network, tuple(order), tuple(range(4))))
            for index in range(3):
                order = list(range(4))
                order[index], order[index + 1] = order[index + 1], order[index]
                neighbors.append(_permute(network, tuple(range(sources)), tuple(order)))
            for neighbor in neighbors:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
    return count


def _summary(labels: tuple[int, ...]) -> int:
    counts = [labels.count(target) for target in range(3)]
    maximum = max(counts)
    return sum(1 << target for target, count in enumerate(counts) if count == maximum)


def _reports(network: Network, signals: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        _summary(
            tuple(signals[source] for source in range(len(network)) if network[source][1][searcher])
        )
        for searcher in range(4)
    )


def _weight(target: int, signals: tuple[int, ...], network: Network) -> Fraction:
    result = Fraction(1, 3)
    for signal, (accuracy, _) in zip(signals, network, strict=True):
        result *= accuracy if signal == target else (1 - accuracy) / 2
    return result


def _choice(report: int, action: int) -> Fraction:
    return Fraction(1, report.bit_count()) if report & (1 << action) else Fraction(0)


def _private(network: Network) -> Fraction:
    result = Fraction(0)
    for target in range(3):
        for signals in itertools.product(range(3), repeat=len(network)):
            miss = Fraction(1)
            for report in _reports(network, signals):
                miss *= 1 - _choice(report, target)
            result += _weight(target, signals, network) * (1 - miss)
    return result


def _signature(network: Network) -> Signature:
    first = [[Fraction(0) for _ in range(3)] for _ in range(4)]
    second = [
        [[[Fraction(0) for _ in range(3)] for _ in range(3)] for _ in range(4)] for _ in range(4)
    ]
    for target in range(3):
        for signals in itertools.product(range(3), repeat=len(network)):
            weight = _weight(target, signals, network)
            reports = _reports(network, signals)
            choices = [[_choice(report, action) for action in range(3)] for report in reports]
            for searcher in range(4):
                for action in range(3):
                    first[searcher][action] += weight * choices[searcher][action]
            for left in range(4):
                for right in range(left + 1, 4):
                    for left_action in range(3):
                        for right_action in range(3):
                            second[left][right][left_action][right_action] += (
                                weight * choices[left][left_action] * choices[right][right_action]
                            )
    candidates = []
    for order in itertools.permutations(range(4)):
        values = [first[order[position]][action] for position in range(4) for action in range(3)]
        for left in range(4):
            for right in range(left + 1, 4):
                first_searcher, second_searcher = order[left], order[right]
                if first_searcher < second_searcher:
                    matrix = second[first_searcher][second_searcher]
                    values.extend(matrix[a][b] for a in range(3) for b in range(3))
                else:
                    matrix = second[second_searcher][first_searcher]
                    values.extend(matrix[b][a] for a in range(3) for b in range(3))
        candidates.append(tuple(values))
    return min(candidates)


def _network(entry: dict[str, Any]) -> Network:
    accuracy_values = tuple(Fraction(value) for value in entry["accuracies"])
    rows = tuple(tuple(int(value) for value in row) for row in entry["adjacency"])
    return tuple((accuracy, row) for accuracy, row in zip(accuracy_values, rows, strict=True))


def verify_pairwise_counterexample(counterexample: dict[str, Any]) -> bool:
    left = _network(counterexample["left"])
    right = _network(counterexample["right"])
    return (
        not _equivalent(left, right)
        and _signature(left) == _signature(right)
        and _private(left) == Fraction(counterexample["left_private_discovery"])
        and _private(right) == Fraction(counterexample["right_private_discovery"])
        and _private(left) - _private(right)
        == Fraction(counterexample["private_discovery_difference"])
        and _private(left) != _private(right)
    )


def verify_colored_registry(
    registry: list[dict[str, Any]],
    specs: list[dict[str, Any]],
    counterexample: dict[str, Any],
) -> dict[str, Any]:
    networks = [_network(entry) for entry in registry]
    valid = all(_valid(network) for network in networks)
    orbit_counts: dict[str, int] = {}
    count_checks: dict[str, bool] = {}
    nonisomorphism_checks: dict[str, bool] = {}
    profile_checks: dict[str, bool] = {}
    for spec in specs:
        key = str(spec["key"])
        levels = tuple(Fraction(value) for value in spec["levels"])
        sources = int(spec["sources"])
        subset = [
            network
            for network, entry in zip(networks, registry, strict=True)
            if entry["spec_key"] == key
        ]
        orbit_counts[key] = _orbit_count(levels, sources)
        count_checks[key] = len(subset) == orbit_counts[key]
        profile_checks[key] = all(
            len(network) == sources and set(accuracy for accuracy, _ in network) == set(levels)
            for network in subset
        )
        nonisomorphism_checks[key] = all(
            not _equivalent(left, right)
            for index, left in enumerate(subset)
            for right in subset[index + 1 :]
        )
    stored_checks = [
        _private(network) == Fraction(entry["private_discovery"])
        and _signature(network)
        == tuple(Fraction(value) for value in entry["complete_moment_signature"])
        for network, entry in zip(networks, registry, strict=True)
    ]
    groups: dict[Signature, list[int]] = defaultdict(list)
    for index, network in enumerate(networks):
        groups[_signature(network)].append(index)
    matched = [group for group in groups.values() if len(group) > 1]
    differing = [
        group for group in matched if len({_private(networks[index]) for index in group}) > 1
    ]
    witness_check = verify_pairwise_counterexample(counterexample)
    passed = (
        valid
        and all(count_checks.values())
        and all(profile_checks.values())
        and all(nonisomorphism_checks.values())
        and all(stored_checks)
        and bool(differing)
        and witness_check
    )
    return {
        "passed": passed,
        "all_networks_model_valid": valid,
        "independent_orbit_counts": orbit_counts,
        "registry_counts_match_independent_orbits": all(count_checks.values()),
        "registry_accuracy_profiles_match_specs": all(profile_checks.values()),
        "all_spec_registries_pairwise_nonisomorphic": all(nonisomorphism_checks.values()),
        "stored_private_discovery_and_complete_moments_recomputed": all(stored_checks),
        "stored_entry_checks": len(stored_checks),
        "matched_complete_moment_group_count": len(matched),
        "matched_groups_with_different_private_discovery": len(differing),
        "counterexample_recomputed": witness_check,
    }
