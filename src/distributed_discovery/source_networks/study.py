"""Run the immutable DD-003 bounded latent-source graph census."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import subprocess
import time
from collections import defaultdict
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.source_networks.model import (
    Graph,
    canonical_graph,
    enumerate_graphs,
    exact_metrics,
    graph_label,
    independent_orbit_count,
    labeled_graphs,
    matched_pairwise_groups,
    mean_pair_agreement,
    pairwise_signature,
)
from distributed_discovery.source_networks.verification import verify_registry
from distributed_discovery.validation.bootstrap import repository_root

CONFIG = Path("studies/DD-003-source-networks/configs/bounded-source-graphs.yml")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    return value


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(_jsonable(value), indent=2, sort_keys=True) + "\n")


def _scatter_svg(registry: list[dict[str, Any]], witness_labels: set[str]) -> str:
    width, height = 760, 440
    left, right, top, bottom = 80, 30, 44, 70
    plot_width = width - left - right
    plot_height = height - top - bottom
    agreements = [float(item["mean_pair_agreement"]) for item in registry]
    discoveries = [float(item["private_discovery"]) for item in registry]
    x_min, x_max = min(agreements), max(agreements)
    y_min, y_max = min(discoveries), max(discoveries)

    def x(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * plot_width

    def y(value: float) -> float:
        return top + (y_max - value) / (y_max - y_min) * plot_height

    colors = {1: "#6b5fb5", 2: "#087d26", 3: "#2a78d6"}
    elements = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 440" role="img">',
        "<title>Pairwise agreement and private discovery across bounded source graphs</title>",
        (
            "<desc>Exact graph results by latent source count; rings mark the "
            "equal-average-agreement counterexample.</desc>"
        ),
        '<rect width="760" height="440" fill="white"/>',
        (
            f'<line x1="{left}" y1="{top + plot_height}" '
            f'x2="{left + plot_width}" y2="{top + plot_height}" stroke="#222"/>'
        ),
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#222"/>',
    ]
    for tick in range(5):
        x_value = x_min + (x_max - x_min) * tick / 4
        x_position = x(x_value)
        elements.append(
            f'<text x="{x_position:.1f}" y="{top + plot_height + 24}" '
            f'text-anchor="middle" font-family="system-ui" font-size="12">'
            f"{x_value:.3f}</text>"
        )
        y_value = y_min + (y_max - y_min) * tick / 4
        y_position = y(y_value)
        elements.append(
            f'<line x1="{left}" y1="{y_position:.1f}" '
            f'x2="{left + plot_width}" y2="{y_position:.1f}" stroke="#e2e2e2"/>'
        )
        elements.append(
            f'<text x="{left - 10}" y="{y_position + 4:.1f}" text-anchor="end" '
            f'font-family="system-ui" font-size="12">{y_value:.3f}</text>'
        )
    elements.extend(
        [
            (
                f'<text x="{left + plot_width / 2:.1f}" y="{height - 20}" '
                'text-anchor="middle" font-family="system-ui" font-size="14">'
                "mean pairwise scalar-report agreement</text>"
            ),
            (
                f'<text transform="translate(21 {top + plot_height / 2:.1f}) rotate(-90)" '
                'text-anchor="middle" font-family="system-ui" font-size="14">'
                "private discovery</text>"
            ),
        ]
    )
    for item in registry:
        label = str(item["canonical_label"])
        radius = 7 if label in witness_labels else 4
        stroke_width = 3 if label in witness_labels else 1
        cx = x(float(item["mean_pair_agreement"]))
        cy = y(float(item["private_discovery"]))
        color = colors[int(item["sources"])]
        elements.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius}" fill="{color}" '
            f'fill-opacity="0.76" stroke="#111" stroke-width="{stroke_width}"/>'
        )
    for index, sources in enumerate((1, 2, 3)):
        legend_y = 20 + index * 18
        elements.append(f'<circle cx="{left + 8}" cy="{legend_y}" r="4" fill="{colors[sources]}"/>')
        elements.append(
            f'<text x="{left + 18}" y="{legend_y + 4}" font-family="system-ui" '
            f'font-size="12">K={sources}</text>'
        )
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def _registry(graphs: list[Graph], accuracy: Fraction) -> list[dict[str, Any]]:
    entries = []
    for index, graph in enumerate(graphs):
        entries.append(
            {
                "graph_id": f"G{index:02d}",
                "canonical_label": graph_label(graph),
                "adjacency": graph,
                **exact_metrics(graph, accuracy),
                "pairwise_signature": pairwise_signature(graph, accuracy),
                "mean_pair_agreement": mean_pair_agreement(graph, accuracy),
            }
        )
    return entries


def main() -> None:
    root = repository_root()
    config_path = root / CONFIG
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    canonical_config = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    config_hash = hashlib.sha256(canonical_config).hexdigest()
    commit = _git(root, "rev-parse", "HEAD")
    dirty = bool(_git(root, "status", "--porcelain"))
    started = datetime.now(UTC)
    start = time.monotonic()
    run_id = f"{started.strftime('%Y%m%dT%H%M%SZ')}_DD-003_{commit[:8]}_{config_hash[:10]}"
    run_dir = root / "results/verified" / run_id
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True)
    (run_dir / "config.yml").write_text(config_path.read_text(encoding="utf-8"))

    accuracy = Fraction(config["source_accuracy"])
    searchers = int(config["searchers"])
    source_counts = [int(value) for value in config["source_counts"]]
    labeled_counts = {sources: len(labeled_graphs(sources, searchers)) for sources in source_counts}
    graphs_by_sources = {sources: enumerate_graphs(sources, searchers) for sources in source_counts}
    orbit_counts = {sources: len(graphs) for sources, graphs in graphs_by_sources.items()}
    independent_counts = {
        sources: independent_orbit_count(sources, searchers) for sources in source_counts
    }
    graphs = [graph for sources in source_counts for graph in graphs_by_sources[sources]]
    registry = _registry(graphs, accuracy)
    _write_json(outputs / "graph-registry.json", registry)

    matched = matched_pairwise_groups(graphs, accuracy)
    matched_output = [
        {
            "group_id": f"M{index:02d}",
            "canonical_labels": [graph_label(graph) for graph in group],
            "pairwise_signature": pairwise_signature(group[0], accuracy),
            "private_discovery_values": sorted(
                {exact_metrics(graph, accuracy)["private_discovery"] for graph in group}
            ),
        }
        for index, group in enumerate(matched)
    ]
    _write_json(outputs / "pairwise-matched-groups.json", matched_output)

    left = canonical_graph(((0, 0, 0, 1), (1, 1, 1, 0)))
    right = canonical_graph(((0, 1, 1, 1), (1, 1, 1, 1)))
    scalar_witness = {
        "left_label": graph_label(left),
        "right_label": graph_label(right),
        "left_adjacency": left,
        "right_adjacency": right,
        "matched_mean_pair_agreement": mean_pair_agreement(left, accuracy),
        "left_private_discovery": exact_metrics(left, accuracy)["private_discovery"],
        "right_private_discovery": exact_metrics(right, accuracy)["private_discovery"],
        "private_discovery_difference": exact_metrics(left, accuracy)["private_discovery"]
        - exact_metrics(right, accuracy)["private_discovery"],
        "full_pairwise_signatures_equal": pairwise_signature(left, accuracy)
        == pairwise_signature(right, accuracy),
    }
    _write_json(outputs / "mean-agreement-counterexample.json", scalar_witness)

    pairwise_null = {
        "graph_count": len(graphs),
        "matched_pairwise_signature_group_count": len(matched),
        "graphs_in_matched_groups": sum(len(group) for group in matched),
        "matched_groups_with_different_private_discovery": sum(
            len({exact_metrics(graph, accuracy)["private_discovery"] for graph in group}) > 1
            for group in matched
        ),
        "bounded_conclusion": "no counterexample on the complete configured graph class",
    }
    _write_json(outputs / "pairwise-null-certificate.json", pairwise_null)

    verifier = verify_registry(registry, scalar_witness)
    _write_json(outputs / "independent-verification.json", verifier)
    witness_labels = {graph_label(left), graph_label(right)}
    (outputs / "agreement-discovery.svg").write_text(
        _scatter_svg(registry, witness_labels), encoding="utf-8"
    )

    rows = []
    for entry in registry:
        rows.append(
            {
                key: str(entry[key])
                for key in [
                    "graph_id",
                    "canonical_label",
                    "sources",
                    "edges",
                    "source_hhi",
                    "effective_sources",
                    "mean_pair_source_overlap",
                    "mean_pair_agreement",
                    "private_discovery",
                    "consensus_discovery",
                    "planner_discovery",
                    "planner_two_discovery",
                    "expected_distinct_private_actions",
                    "all_reports_equal_probability",
                ]
            }
        )
    with (outputs / "graph-summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    mean_groups: dict[Fraction, list[dict[str, Any]]] = defaultdict(list)
    hhi_groups: dict[Fraction, list[dict[str, Any]]] = defaultdict(list)
    for entry in registry:
        mean_groups[entry["mean_pair_agreement"]].append(entry)
        hhi_groups[entry["source_hhi"]].append(entry)
    mean_scalar_counterexample_pairs = sum(
        left_entry["private_discovery"] != right_entry["private_discovery"]
        for group in mean_groups.values()
        for index, left_entry in enumerate(group)
        for right_entry in group[index + 1 :]
    )
    hhi_counterexample_pairs = sum(
        left_entry["private_discovery"] != right_entry["private_discovery"]
        for group in hhi_groups.values()
        for index, left_entry in enumerate(group)
        for right_entry in group[index + 1 :]
    )
    elapsed = time.monotonic() - start
    exact_expectations = (
        orbit_counts == {1: 1, 2: 8, 3: 42}
        and labeled_counts == {1: 1, 2: 79, 3: 2161}
        and independent_counts == orbit_counts
        and len(graphs) == 51
        and len({graph_label(graph) for graph in graphs}) == 51
        and len(matched) == 10
        and sum(len(group) for group in matched) == 20
        and pairwise_null["matched_groups_with_different_private_discovery"] == 0
        and scalar_witness["matched_mean_pair_agreement"] == Fraction(3, 4)
        and scalar_witness["left_private_discovery"] == Fraction(8, 9)
        and scalar_witness["right_private_discovery"] == Fraction(31, 36)
        and not scalar_witness["full_pairwise_signatures_equal"]
    )
    validation = {
        "passed": bool(
            not dirty
            and exact_expectations
            and verifier["passed"]
            and elapsed <= float(config["time_budget_seconds"])
        ),
        "git_clean_at_start": not dirty,
        "labeled_graph_counts": labeled_counts,
        "canonical_orbit_counts": orbit_counts,
        "independent_orbit_counts": independent_counts,
        "all_51_graphs_enumerated": len(graphs) == 51,
        "canonical_labels_unique": len({graph_label(graph) for graph in graphs}) == 51,
        "pairwise_matrix_bounded_null_verified": pairwise_null[
            "matched_groups_with_different_private_discovery"
        ]
        == 0,
        "mean_pair_agreement_counterexample_verified": scalar_witness[
            "private_discovery_difference"
        ]
        == Fraction(1, 36),
        "independent_verifier_passed": verifier["passed"],
        "elapsed_seconds": elapsed,
        "time_budget_seconds": config["time_budget_seconds"],
    }
    _write_json(run_dir / "validation.json", validation)
    _write_json(
        run_dir / "metrics.json",
        {
            "graph_count": len(graphs),
            "labeled_graph_counts": labeled_counts,
            "canonical_orbit_counts": orbit_counts,
            "matched_pairwise_signature_group_count": len(matched),
            "graphs_in_matched_pairwise_groups": sum(len(group) for group in matched),
            "pairwise_matrix_discovery_counterexample_count": pairwise_null[
                "matched_groups_with_different_private_discovery"
            ],
            "mean_pair_agreement_discovery_counterexample_pair_count": (
                mean_scalar_counterexample_pairs
            ),
            "source_hhi_discovery_counterexample_pair_count": hhi_counterexample_pairs,
        },
    )
    (run_dir / "stdout.log").write_text(
        f"run_id={run_id}\ngraph_count={len(graphs)}\n"
        f"validation_status={'passed' if validation['passed'] else 'failed'}\n",
        encoding="utf-8",
    )
    (run_dir / "stderr.log").write_text("", encoding="utf-8")
    packages = subprocess.check_output(["uv", "pip", "freeze"], cwd=root, text=True).splitlines()
    _write_json(
        run_dir / "environment.json",
        {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "packages": sorted(
                line
                for line in packages
                if not line.lower().startswith("distributed-discovery @ file:")
            ),
        },
    )
    output_hashes = {
        str(path.relative_to(run_dir)): _sha(path)
        for path in sorted(outputs.iterdir())
        if path.is_file()
    }
    _write_json(run_dir / "output-checksums.json", output_hashes)
    ended = datetime.now(UTC)
    input_paths = [
        config_path,
        root / "src/distributed_discovery/source_networks/model.py",
        root / "src/distributed_discovery/source_networks/study.py",
        root / "src/distributed_discovery/source_networks/verification.py",
    ]
    command = "make dd003-source-graphs"
    manifest = {
        "schema_version": 1,
        "run_id": run_id,
        "study_id": "DD-003",
        "started_utc": started.isoformat().replace("+00:00", "Z"),
        "ended_utc": ended.isoformat().replace("+00:00", "Z"),
        "exit_status": 0 if validation["passed"] else 1,
        "validation_status": "passed" if validation["passed"] else "failed",
        "git_commit": commit,
        "git_dirty": dirty,
        "upstream_commit": None,
        "command": command,
        "config_hash_sha256": config_hash,
        "dependency_lock_hash_sha256": _sha(root / "uv.lock"),
        "input_hashes": {str(path.relative_to(root)): _sha(path) for path in input_paths},
        "random_seeds": {"algorithm": None, "model": None},
        "outputs": output_hashes,
    }
    _write_json(run_dir / "manifest.json", manifest)
    (run_dir / "command.txt").write_text(command + "\n", encoding="utf-8")
    (run_dir / "reproduce.sh").write_text(
        "#!/bin/sh\nset -eu\nexec make dd003-source-graphs\n", encoding="utf-8"
    )
    os.chmod(run_dir / "reproduce.sh", 0o755)
    (run_dir / "README.md").write_text(
        f"# DD-003 bounded source-graph run {run_id}\n\n"
        "Complete canonical graph registry, exact protocol summaries, pairwise-moment "
        "bounded-null certificate, scalar counterexample, figure, and independent verification.\n",
        encoding="utf-8",
    )
    print(run_id)
    print(f"validation_status={manifest['validation_status']}")
    if not validation["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
