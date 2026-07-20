"""Exact bounded latent-source graph model for DD-003."""

from __future__ import annotations

import itertools
from collections import defaultdict, deque
from fractions import Fraction

Graph = tuple[tuple[int, ...], ...]
Report = int
ReportProfile = tuple[Report, ...]


def valid_graph(graph: Graph) -> bool:
    """Require every declared source and every searcher to have an edge."""
    if not graph or not graph[0]:
        return False
    searchers = len(graph[0])
    return all(any(row) for row in graph) and all(
        any(graph[source][searcher] for source in range(len(graph)))
        for searcher in range(searchers)
    )


def permute_graph(
    graph: Graph, source_order: tuple[int, ...], searcher_order: tuple[int, ...]
) -> Graph:
    return tuple(
        tuple(graph[source][searcher] for searcher in searcher_order) for source in source_order
    )


def canonical_graph(graph: Graph) -> Graph:
    """Return the least adjacency matrix under independent bipartite relabeling."""
    sources = range(len(graph))
    searchers = range(len(graph[0]))
    return min(
        permute_graph(graph, source_order, searcher_order)
        for source_order in itertools.permutations(sources)
        for searcher_order in itertools.permutations(searchers)
    )


def graph_label(graph: Graph) -> str:
    bits = "".join(str(value) for row in graph for value in row)
    return f"K{len(graph)}N{len(graph[0])}:{bits}"


def labeled_graphs(sources: int, searchers: int) -> list[Graph]:
    graphs: list[Graph] = []
    for bits in itertools.product((0, 1), repeat=sources * searchers):
        graph = tuple(
            tuple(bits[source * searchers + searcher] for searcher in range(searchers))
            for source in range(sources)
        )
        if valid_graph(graph):
            graphs.append(graph)
    return graphs


def enumerate_graphs(sources: int, searchers: int) -> list[Graph]:
    return sorted({canonical_graph(graph) for graph in labeled_graphs(sources, searchers)})


def independent_orbit_count(sources: int, searchers: int) -> int:
    """Count relabeling orbits by traversal, without canonical minimization."""
    unseen = set(labeled_graphs(sources, searchers))
    count = 0
    while unseen:
        count += 1
        start = unseen.pop()
        queue = deque([start])
        while queue:
            graph = queue.popleft()
            neighbors: list[Graph] = []
            for index in range(sources - 1):
                order = list(range(sources))
                order[index], order[index + 1] = order[index + 1], order[index]
                neighbors.append(permute_graph(graph, tuple(order), tuple(range(searchers))))
            for index in range(searchers - 1):
                order = list(range(searchers))
                order[index], order[index + 1] = order[index + 1], order[index]
                neighbors.append(permute_graph(graph, tuple(range(sources)), tuple(order)))
            for neighbor in neighbors:
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
    return count


def plurality_report(labels: tuple[int, ...], targets: int = 3) -> Report:
    counts = [labels.count(target) for target in range(targets)]
    maximum = max(counts)
    return sum(1 << target for target, count in enumerate(counts) if count == maximum)


def report_profile(graph: Graph, source_signals: tuple[int, ...]) -> ReportProfile:
    return tuple(
        plurality_report(
            tuple(source_signals[source] for source in range(len(graph)) if graph[source][searcher])
        )
        for searcher in range(len(graph[0]))
    )


def signal_probability(
    target: int, source_signals: tuple[int, ...], accuracy: Fraction
) -> Fraction:
    incorrect = (1 - accuracy) / 2
    probability = Fraction(1, 3)
    for signal in source_signals:
        probability *= accuracy if signal == target else incorrect
    return probability


def report_law(graph: Graph, accuracy: Fraction) -> dict[ReportProfile, Fraction]:
    law: dict[ReportProfile, Fraction] = defaultdict(Fraction)
    for target in range(3):
        for signals in itertools.product(range(3), repeat=len(graph)):
            law[report_profile(graph, signals)] += signal_probability(target, signals, accuracy)
    assert sum(law.values()) == 1
    return dict(law)


def _winner_probability(report: Report, target: int) -> Fraction:
    if not report & (1 << target):
        return Fraction(0)
    return Fraction(1, report.bit_count())


def _planner_success(
    target: int, signals: tuple[int, ...], budget: int, accuracy: Fraction
) -> Fraction:
    if budget >= 3:
        return Fraction(1)
    incorrect = (1 - accuracy) / 2
    scores = []
    for candidate in range(3):
        score = Fraction(1)
        for signal in signals:
            score *= accuracy if signal == candidate else incorrect
        scores.append(score)
    cutoff = sorted(scores, reverse=True)[budget - 1]
    above = sum(score > cutoff for score in scores)
    tied = sum(score == cutoff for score in scores)
    if scores[target] > cutoff:
        return Fraction(1)
    if scores[target] < cutoff:
        return Fraction(0)
    return Fraction(budget - above, tied)


def exact_metrics(graph: Graph, accuracy: Fraction) -> dict[str, Fraction | int]:
    private = Fraction(0)
    consensus = Fraction(0)
    planner = Fraction(0)
    planner_two = Fraction(0)
    expected_distinct = Fraction(0)
    all_reports_equal = Fraction(0)
    for target in range(3):
        for signals in itertools.product(range(3), repeat=len(graph)):
            weight = signal_probability(target, signals, accuracy)
            reports = report_profile(graph, signals)
            miss = Fraction(1)
            for report in reports:
                miss *= 1 - _winner_probability(report, target)
            private += weight * (1 - miss)
            for candidate in range(3):
                candidate_miss = Fraction(1)
                for report in reports:
                    candidate_miss *= 1 - _winner_probability(report, candidate)
                expected_distinct += weight * (1 - candidate_miss)
            edge_labels = tuple(
                signals[source]
                for source, row in enumerate(graph)
                for connected in row
                if connected
            )
            consensus += weight * _winner_probability(plurality_report(edge_labels), target)
            planner += weight * _planner_success(target, signals, 4, accuracy)
            planner_two += weight * _planner_success(target, signals, 2, accuracy)
            if len(set(reports)) == 1:
                all_reports_equal += weight
    edge_count = sum(sum(row) for row in graph)
    degree_square_sum = sum(sum(row) ** 2 for row in graph)
    source_hhi = Fraction(degree_square_sum, edge_count**2)
    pair_overlap = Fraction(0)
    pairs = 0
    for left in range(len(graph[0])):
        for right in range(left + 1, len(graph[0])):
            pair_overlap += sum(
                graph[source][left] * graph[source][right] for source in range(len(graph))
            )
            pairs += 1
    return {
        "sources": len(graph),
        "edges": edge_count,
        "source_hhi": source_hhi,
        "effective_sources": 1 / source_hhi,
        "mean_pair_source_overlap": pair_overlap / pairs,
        "private_discovery": private,
        "consensus_discovery": consensus,
        "planner_discovery": planner,
        "planner_two_discovery": planner_two,
        "expected_distinct_private_actions": expected_distinct,
        "all_reports_equal_probability": all_reports_equal,
    }


def _action_agreement(left: Report, right: Report) -> Fraction:
    return Fraction((left & right).bit_count(), left.bit_count() * right.bit_count())


def pairwise_signature(graph: Graph, accuracy: Fraction) -> tuple[Fraction, ...]:
    """Canonical one-hot first/second moments via pair action agreement."""
    law = report_law(graph, accuracy)
    signatures: list[tuple[Fraction, ...]] = []
    for order in itertools.permutations(range(len(graph[0]))):
        values: list[Fraction] = []
        for left in range(len(order)):
            for right in range(left + 1, len(order)):
                values.append(
                    sum(
                        (
                            probability
                            * _action_agreement(profile[order[left]], profile[order[right]])
                            for profile, probability in law.items()
                        ),
                        Fraction(0),
                    )
                )
        signatures.append(tuple(values))
    return min(signatures)


def mean_pair_agreement(graph: Graph, accuracy: Fraction) -> Fraction:
    signature = pairwise_signature(graph, accuracy)
    return sum(signature, Fraction(0)) / len(signature)


def matched_pairwise_groups(graphs: list[Graph], accuracy: Fraction) -> list[list[Graph]]:
    groups: dict[tuple[Fraction, ...], list[Graph]] = defaultdict(list)
    for graph in graphs:
        groups[pairwise_signature(graph, accuracy)].append(graph)
    return [group for group in groups.values() if len(group) > 1]
