from fractions import Fraction

from distributed_discovery.source_networks.model import (
    canonical_graph,
    enumerate_graphs,
    exact_metrics,
    graph_label,
    independent_orbit_count,
    matched_pairwise_groups,
    mean_pair_agreement,
    pairwise_signature,
    plurality_report,
    report_law,
)


def test_plurality_report_preserves_ties() -> None:
    assert plurality_report((0, 1)) == 0b011
    assert plurality_report((0, 1, 2)) == 0b111
    assert plurality_report((2, 2, 1)) == 0b100


def test_canonical_graph_is_relabeling_invariant() -> None:
    graph = ((1, 0, 1, 0), (0, 1, 0, 1))
    relabeled = ((0, 1, 0, 1), (1, 0, 1, 0))
    assert canonical_graph(graph) == canonical_graph(relabeled)
    assert graph_label(canonical_graph(graph)).startswith("K2N4:")


def test_orbit_counts_have_independent_confirmation() -> None:
    expected = {1: 1, 2: 8, 3: 42}
    for sources, count in expected.items():
        assert len(enumerate_graphs(sources, 4)) == count
        assert len(enumerate_graphs(sources, 4)) == independent_orbit_count(sources, 4)


def test_exact_laws_and_metrics_normalize() -> None:
    graph = ((1, 1, 1, 1),)
    accuracy = Fraction(2, 3)
    assert sum(report_law(graph, accuracy).values()) == 1
    metrics = exact_metrics(graph, accuracy)
    assert metrics["private_discovery"] == accuracy
    assert metrics["planner_discovery"] == 1
    assert metrics["source_hhi"] == 1


def test_pairwise_signature_is_searcher_relabeling_invariant() -> None:
    graph = ((1, 1, 0, 1), (0, 1, 1, 0))
    relabeled = ((1, 0, 1, 1), (0, 1, 0, 1))
    accuracy = Fraction(2, 3)
    assert pairwise_signature(graph, accuracy) == pairwise_signature(relabeled, accuracy)


def test_pairwise_matrix_null_and_average_counterexample() -> None:
    accuracy = Fraction(2, 3)
    graphs = sum((enumerate_graphs(sources, 4) for sources in (1, 2, 3)), [])
    groups = matched_pairwise_groups(graphs, accuracy)
    assert len(groups) == 10
    assert sum(len(group) for group in groups) == 20
    for group in groups:
        assert len({exact_metrics(graph, accuracy)["private_discovery"] for graph in group}) == 1

    left = canonical_graph(((0, 0, 0, 1), (1, 1, 1, 0)))
    right = canonical_graph(((0, 1, 1, 1), (1, 1, 1, 1)))
    assert mean_pair_agreement(left, accuracy) == mean_pair_agreement(right, accuracy)
    assert exact_metrics(left, accuracy)["private_discovery"] == Fraction(8, 9)
    assert exact_metrics(right, accuracy)["private_discovery"] == Fraction(31, 36)
