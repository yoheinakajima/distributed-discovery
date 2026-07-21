"""Exact colored-source model for the DD-003 heterogeneous census."""

from __future__ import annotations

import itertools
from collections import defaultdict, deque
from fractions import Fraction

from distributed_discovery.source_networks.model import Graph, labeled_graphs, report_profile

ColoredRow = tuple[Fraction, tuple[int, ...]]
ColoredNetwork = tuple[ColoredRow, ...]
MomentSignature = tuple[Fraction, ...]


def colored_network(graph: Graph, accuracies: tuple[Fraction, ...]) -> ColoredNetwork:
    if len(graph) != len(accuracies):
        raise ValueError("one accuracy is required per source")
    return tuple((accuracy, row) for accuracy, row in zip(accuracies, graph, strict=True))


def adjacency(network: ColoredNetwork) -> Graph:
    return tuple(row for _, row in network)


def accuracies(network: ColoredNetwork) -> tuple[Fraction, ...]:
    return tuple(accuracy for accuracy, _ in network)


def permute_colored(
    network: ColoredNetwork,
    source_order: tuple[int, ...],
    searcher_order: tuple[int, ...],
) -> ColoredNetwork:
    return tuple(
        (
            network[source][0],
            tuple(network[source][1][searcher] for searcher in searcher_order),
        )
        for source in source_order
    )


def canonical_colored(network: ColoredNetwork) -> ColoredNetwork:
    sources = range(len(network))
    searchers = range(len(network[0][1]))
    return min(
        permute_colored(network, source_order, searcher_order)
        for source_order in itertools.permutations(sources)
        for searcher_order in itertools.permutations(searchers)
    )


def colored_label(network: ColoredNetwork) -> str:
    rows = []
    for accuracy, row in network:
        color = f"{accuracy.numerator}-{accuracy.denominator}"
        rows.append(f"{color}@{''.join(str(value) for value in row)}")
    return f"K{len(network)}N{len(network[0][1])}:" + ";".join(rows)


def accuracy_assignments(
    levels: tuple[Fraction, ...], sources: int, *, require_every_level: bool = True
) -> list[tuple[Fraction, ...]]:
    if not levels or len(set(levels)) != len(levels):
        raise ValueError("accuracy levels must be a nonempty set")
    if require_every_level and len(levels) > sources:
        return []
    assignments = set(itertools.product(levels, repeat=sources))
    if require_every_level:
        assignments = {assignment for assignment in assignments if set(assignment) == set(levels)}
    return sorted(assignments)


def labeled_colored_networks(
    levels: tuple[Fraction, ...], sources: int, searchers: int
) -> list[ColoredNetwork]:
    return [
        colored_network(graph, assignment)
        for graph in labeled_graphs(sources, searchers)
        for assignment in accuracy_assignments(levels, sources)
    ]


def enumerate_colored_networks(
    levels: tuple[Fraction, ...], sources: int, searchers: int
) -> list[ColoredNetwork]:
    return sorted(
        {
            canonical_colored(network)
            for network in labeled_colored_networks(levels, sources, searchers)
        }
    )


def independent_colored_orbit_count(
    levels: tuple[Fraction, ...], sources: int, searchers: int
) -> int:
    """Count colored orbits by adjacent-swap traversal, without minimization."""
    unseen = set(labeled_colored_networks(levels, sources, searchers))
    count = 0
    while unseen:
        count += 1
        start = unseen.pop()
        queue = deque([start])
        while queue:
            network = queue.popleft()
            neighbors: list[ColoredNetwork] = []
            for index in range(sources - 1):
                order = list(range(sources))
                order[index], order[index + 1] = order[index + 1], order[index]
                neighbors.append(permute_colored(network, tuple(order), tuple(range(searchers))))
            for index in range(searchers - 1):
                order = list(range(searchers))
                order[index], order[index + 1] = order[index + 1], order[index]
                neighbors.append(permute_colored(network, tuple(range(sources)), tuple(order)))
            for neighbor in neighbors:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
    return count


def signal_probability(
    target: int,
    source_signals: tuple[int, ...],
    source_accuracies: tuple[Fraction, ...],
) -> Fraction:
    probability = Fraction(1, 3)
    for signal, accuracy in zip(source_signals, source_accuracies, strict=True):
        probability *= accuracy if signal == target else (1 - accuracy) / 2
    return probability


def _action_probability(report: int, action: int) -> Fraction:
    if not report & (1 << action):
        return Fraction(0)
    return Fraction(1, report.bit_count())


def exact_action_moments(
    network: ColoredNetwork,
) -> tuple[
    tuple[tuple[Fraction, ...], ...],
    tuple[tuple[tuple[tuple[Fraction, ...], ...], ...], ...],
]:
    graph = adjacency(network)
    source_accuracies = accuracies(network)
    searchers = len(graph[0])
    first = [[Fraction(0) for _ in range(3)] for _ in range(searchers)]
    second = [
        [[[Fraction(0) for _ in range(3)] for _ in range(3)] for _ in range(searchers)]
        for _ in range(searchers)
    ]
    for target in range(3):
        for signals in itertools.product(range(3), repeat=len(network)):
            weight = signal_probability(target, signals, source_accuracies)
            reports = report_profile(graph, signals)
            actions = [
                [_action_probability(report, action) for action in range(3)] for report in reports
            ]
            for searcher in range(searchers):
                for action in range(3):
                    first[searcher][action] += weight * actions[searcher][action]
            for left in range(searchers):
                for right in range(left + 1, searchers):
                    for left_action in range(3):
                        for right_action in range(3):
                            second[left][right][left_action][right_action] += (
                                weight * actions[left][left_action] * actions[right][right_action]
                            )
    return (
        tuple(tuple(row) for row in first),
        tuple(
            tuple(tuple(tuple(row) for row in matrix) for matrix in right_rows)
            for right_rows in second
        ),
    )


def complete_moment_signature(network: ColoredNetwork) -> MomentSignature:
    first, second = exact_action_moments(network)
    searchers = len(first)
    candidates = []
    for order in itertools.permutations(range(searchers)):
        values = [
            first[order[position]][action] for position in range(searchers) for action in range(3)
        ]
        for left in range(searchers):
            for right in range(left + 1, searchers):
                first_searcher = order[left]
                second_searcher = order[right]
                if first_searcher < second_searcher:
                    matrix = second[first_searcher][second_searcher]
                    values.extend(matrix[a][b] for a in range(3) for b in range(3))
                else:
                    matrix = second[second_searcher][first_searcher]
                    values.extend(matrix[b][a] for a in range(3) for b in range(3))
        candidates.append(tuple(values))
    return min(candidates)


def pairwise_agreement_signature(network: ColoredNetwork) -> tuple[Fraction, ...]:
    _, second = exact_action_moments(network)
    searchers = len(network[0][1])
    candidates = []
    for order in itertools.permutations(range(searchers)):
        values = []
        for left in range(searchers):
            for right in range(left + 1, searchers):
                first_searcher, second_searcher = sorted((order[left], order[right]))
                matrix = second[first_searcher][second_searcher]
                values.append(sum((matrix[action][action] for action in range(3)), Fraction(0)))
        candidates.append(tuple(values))
    return min(candidates)


def exact_private_discovery(network: ColoredNetwork) -> Fraction:
    graph = adjacency(network)
    source_accuracies = accuracies(network)
    discovery = Fraction(0)
    for target in range(3):
        for signals in itertools.product(range(3), repeat=len(network)):
            weight = signal_probability(target, signals, source_accuracies)
            miss = Fraction(1)
            for report in report_profile(graph, signals):
                miss *= 1 - _action_probability(report, target)
            discovery += weight * (1 - miss)
    return discovery


def exact_colored_metrics(network: ColoredNetwork) -> dict[str, Fraction | int]:
    graph = adjacency(network)
    source_accuracies = accuracies(network)
    edge_count = sum(sum(row) for row in graph)
    degrees = [sum(row) for row in graph]
    source_hhi = Fraction(sum(degree**2 for degree in degrees), edge_count**2)
    overlap_total = 0
    pair_count = 0
    for left in range(len(graph[0])):
        for right in range(left + 1, len(graph[0])):
            overlap_total += sum(row[left] * row[right] for row in graph)
            pair_count += 1
    agreement = pairwise_agreement_signature(network)
    return {
        "sources": len(network),
        "edges": edge_count,
        "source_hhi": source_hhi,
        "effective_sources": 1 / source_hhi,
        "mean_pair_source_overlap": Fraction(overlap_total, pair_count),
        "mean_source_accuracy": sum(source_accuracies, Fraction(0)) / len(source_accuracies),
        "minimum_source_accuracy": min(source_accuracies),
        "maximum_source_accuracy": max(source_accuracies),
        "exposure_weighted_accuracy": sum(
            (
                accuracy * degree
                for accuracy, degree in zip(source_accuracies, degrees, strict=True)
            ),
            Fraction(0),
        )
        / edge_count,
        "mean_pair_agreement": sum(agreement, Fraction(0)) / len(agreement),
        "private_discovery": exact_private_discovery(network),
    }


def matched_complete_moment_groups(
    networks: list[ColoredNetwork],
) -> list[list[ColoredNetwork]]:
    groups: dict[MomentSignature, list[ColoredNetwork]] = defaultdict(list)
    for network in networks:
        groups[complete_moment_signature(network)].append(network)
    return [group for group in groups.values() if len(group) > 1]
