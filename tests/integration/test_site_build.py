import hashlib
import json
import re
import shutil
from fractions import Fraction
from pathlib import Path

import yaml

from distributed_discovery.site.build import build

ROOT = Path(__file__).resolve().parents[2]


def test_research_library_builds_from_validated_repository_evidence(tmp_path: Path) -> None:
    output = tmp_path / "site"
    report = build(ROOT, output)

    expected_studies = len(list((ROOT / "studies").glob("DD-0*/public.yml")))
    expected_claims = len(yaml.safe_load((ROOT / "claims/claims.yml").read_text())["claims"])
    expected_passing_runs = sum(
        json.loads(path.read_text())["validation_status"] == "passed"
        and json.loads(path.read_text())["exit_status"] == 0
        for path in (ROOT / "results").glob("**/manifest.json")
    )
    expected_publications = sum(
        (directory / "validation.json").is_file() and len(list(directory.glob("*.pdf"))) == 1
        for directory in (ROOT / "papers").iterdir()
        if directory.is_dir()
    )
    assert report["page_count"] == len(list(output.glob("**/*.html")))
    assert report["study_count"] == expected_studies
    assert report["claim_count"] == expected_claims
    assert report["passing_run_count"] == expected_passing_runs
    assert report["publication_count"] == expected_publications
    assert report["internal_links_passed"] is True
    assert report["public_safety_passed"] is True
    assert report["download_checksums_passed"] is True
    assert report["local_assets_passed"] is True
    assert report["no_tracking_passed"] is True
    assert report["no_javascript_fallbacks_passed"] is True
    assert report["accessibility_smoke_passed"] is True

    program = (output / "program.html").read_text(encoding="utf-8")
    assert "The Distributed Discovery program" in program
    assert "The Architecture of Distributed Discovery" in program
    assert "Incremental Sharing and Independent Rescue" in program
    assert "DD-C-0092 through DD-C-0096" in program
    assert "primary ownership" in program
    assert "future Information Sharing Frontier theorem-family paper" in program
    assert "canonical entry paper" in program
    assert "Working notes" in program
    assert "Reproducible studies, Labs, and DiscoveryBench" in program
    assert "No manuscript expansion or submission action is authorized" in program
    assert "journal submission status" in program
    assert "DD-019" in program and "DD-020" in program

    research = (output / "research.html").read_text(encoding="utf-8")
    assert "DD-000" in research and "DD-008" in research
    assert "Completed finite study" in research
    assert ">complete-bounded-study<" not in research
    assert 'type="search"' in research
    assert 'data-study-filter="key-results"' in research
    assert 'aria-live="polite"' in research
    assert 'href="research/dd-004.html"' in research
    assert 'href="program.html"' in research
    assert (output / "research/dd-000.html").is_file()
    assert (output / "research/dd-008.html").is_file()
    assert (output / "research/dd-008a.html").is_file()
    assert (output / "research/dd-006b.html").is_file()
    assert (output / "research/dd-009.html").is_file()
    assert (output / "research/dd-010.html").is_file()
    assert (output / "research/dd-011.html").is_file()
    assert (output / "research/dd-012.html").is_file()
    assert (output / "research/dd-013.html").is_file()
    assert (output / "research/dd-014.html").is_file()
    assert (output / "research/dd-015.html").is_file()
    attention = (output / "research/dd-012.html").read_text(encoding="utf-8")
    assert "DD-C-0059" in attention
    assert "DD-C-0060" in attention
    assert "DD-C-0061" in attention
    assert "20260721T212943Z_DD-012_9ed0928e_4a3f1ba62b" in attention
    attention_data = json.loads((output / "data/studies/dd-012.json").read_text(encoding="utf-8"))
    assert attention_data["phase"] == "complete-bounded-study"
    assert attention_data["claim_ids"] == ["DD-C-0059", "DD-C-0060", "DD-C-0061"]
    audience_study = (output / "research/dd-013.html").read_text(encoding="utf-8")
    assert "DD-C-0062" in audience_study
    assert "DD-C-0065" in audience_study
    assert "20260721T215811Z_DD-013_09c07448_cdac4fb512" in audience_study
    assert (output / "benchmark.html").is_file()
    for route in ["tasks", "protocols", "metrics", "results", "attention"]:
        assert (output / f"benchmark/{route}.html").is_file()
    benchmark_lab = (output / "labs/benchmark.html").read_text()
    assert "no submissions" in benchmark_lab
    assert "JavaScript is off" in benchmark_lab
    assert (output / "labs.html").is_file()
    assert (output / "experiment-kit.html").is_file()
    for route in ["hypotheses", "design", "attention", "power"]:
        page = output / f"experiment-kit/{route}.html"
        assert page.is_file()
        assert "No participants were recruited" in page.read_text()
    experiment_lab = (output / "labs/experiment-design.html").read_text()
    assert "data-experiment-lab" in experiment_lab
    assert "JavaScript is off" in experiment_lab
    assert "No participants were recruited" in experiment_lab
    audience_lab = (output / "labs/audience.html").read_text()
    audience_design_lab = (output / "labs/audience-design.html").read_text()
    assert "data-audience-lab" in audience_design_lab
    assert "Audience Design Lab" in audience_design_lab
    assert "data-audience-lab" in audience_lab
    assert "JavaScript is off" in audience_lab
    assert "DD-C-0065" in audience_lab
    assert "20260721T215811Z_DD-013_09c07448_cdac4fb512" in audience_lab
    for control in [
        "audience-n",
        "audience-p",
        "audience-q",
        "audience-use",
        "audience-g",
        "audience-m",
        "audience-mechanism",
    ]:
        assert f'id="{control}"' in audience_lab
    for row_kind in ["audience-row", "voluntary-row", "garbling-row", "mechanism-row"]:
        assert f"data-{row_kind}" in audience_lab
    attention_lab = (output / "labs/attention.html").read_text()
    assert "data-attention-lab" in attention_lab
    assert "JavaScript is off" in attention_lab
    assert "DD-C-0060" in attention_lab
    assert "20260721T212943Z_DD-012_9ed0928e_4a3f1ba62b" in attention_lab
    assert "Equal-split attention wedge" in attention_lab
    for control in ["attention-n", "attention-p", "attention-q", "attention-k", "attention-reward"]:
        assert f'id="{control}"' in attention_lab
    conditional_lab = (output / "labs/conditional-attention.html").read_text()
    assert "data-conditional-lab" in conditional_lab
    assert "JavaScript is off" in conditional_lab
    assert "DD-C-0068" in conditional_lab
    assert "20260721T222047Z_DD-014_f5f099a8_ea0276dd16" in conditional_lab
    for control in ["conditional-n", "conditional-p", "conditional-q", "conditional-policy"]:
        assert f'id="{control}"' in conditional_lab
    for name in [
        "sequential",
        "coverage",
        "mechanisms",
        "audit",
        "evidence-acquisition",
        "atlas",
    ]:
        page_source = (output / f"labs/{name}.html").read_text(encoding="utf-8")
        assert 'type="range"' not in page_source
        assert "data-lab=" not in page_source
        assert "Lab type" in page_source
        assert "Control fields" in page_source
        assert "Output fields" in page_source
        assert "data/labs/" in page_source
        assert "JavaScript is off" in page_source

    incremental_page = (output / "labs/incremental-sharing.html").read_text(encoding="utf-8")
    assert "data-incremental-lab" in incremental_page
    assert incremental_page.count('data-incremental-row=""') == 2054
    assert "JavaScript is off" in incremental_page
    assert "G<sub>s</sub> = 1 − (1−C<sub>s</sub>)(1−q)<sup>N−s</sup>" in incremental_page
    assert "Download the full 2,555-row point census" in incremental_page
    assert "DD-C-0092" in incremental_page and "DD-C-0096" in incremental_page
    assert "20260722T142551Z_DD-020_3854fff6_37c11a850a" in incremental_page
    for control in [
        "incremental-mode",
        "incremental-targets",
        "incremental-agents",
        "incremental-accuracy",
        "incremental-channel",
        "incremental-step",
        "incremental-comparison",
    ]:
        assert f'id="{control}"' in incremental_page

    program_v4_labs = {
        "threshold": {
            "kind": "threshold",
            "controls": ["threshold-tau"],
            "rows": 8,
            "run": "20260722T021526Z_DD-016_00271ff8_123b2809e3",
            "claim": "DD-C-0074",
        },
        "equilibrium-selection": {
            "kind": "equilibrium",
            "controls": [
                "equilibrium-fixture",
                "equilibrium-agents",
                "equilibrium-threshold",
            ],
            "rows": 160,
            "run": "20260722T024032Z_DD-017_033452f6_3d2c74fdfb",
            "claim": "DD-C-0077",
        },
        "dynamic-attention": {
            "kind": "dynamic",
            "controls": [
                "dynamic-agents",
                "dynamic-private",
                "dynamic-shared",
                "dynamic-objective",
            ],
            "rows": 64,
            "run": "20260722T043713Z_DD-015_92d53ac1_0e7cf1ec0a",
            "claim": "DD-C-0080",
        },
        "team-mechanisms": {
            "kind": "mechanism",
            "controls": ["mechanism-fixture", "mechanism-name"],
            "rows": 50,
            "run": "20260722T051847Z_DD-018_a193f602_3b3ddac173",
            "claim": "DD-C-0084",
        },
    }
    for slug, specification in program_v4_labs.items():
        page_source = (output / f"labs/{slug}.html").read_text(encoding="utf-8")
        assert f'data-output-lab="{specification["kind"]}"' in page_source
        assert (
            page_source.count(f'data-output-row="{specification["kind"]}"') == specification["rows"]
        )
        assert "JavaScript is off" in page_source
        assert "data-output-status" in page_source
        assert specification["run"] in page_source
        assert specification["claim"] in page_source
        for control in specification["controls"]:
            assert f'id="{control}"' in page_source

    claims = (output / "claims.html").read_text(encoding="utf-8")
    assert 'id="DD-C-0001"' in claims
    assert 'id="DD-C-0044"' in claims
    assert 'id="DD-C-0053"' in claims
    assert 'id="DD-C-0054"' in claims
    assert 'id="DD-C-0055"' in claims
    assert 'id="DD-C-0056"' in claims
    assert 'id="DD-C-0061"' in claims
    assert 'id="DD-C-0065"' in claims
    assert 'id="DD-C-0069"' in claims
    assert 'id="DD-C-0070"' in claims
    assert 'id="DD-C-0088"' in claims
    assert "unvalidated values" in claims

    runs = json.loads((output / "data/runs.json").read_text(encoding="utf-8"))["runs"]
    assert all(run["validation_status"] == "passed" for run in runs)
    assert all("/Users/" not in run["manifest_path"] for run in runs)

    publications = json.loads((output / "data/publications.json").read_text(encoding="utf-8"))[
        "publications"
    ]
    for publication in publications:
        download = output / publication["download"]
        assert download.is_file()
        assert download.stat().st_size > 0
    common_source = next(item for item in publications if item["slug"] == "common-source-trap")
    common_source_page = output / common_source["detail"]
    assert common_source_page.is_file()
    common_source_html = common_source_page.read_text(encoding="utf-8")
    assert "working paper · no DOI · not submitted · not peer reviewed" in common_source_html
    assert common_source["sha256"] in common_source_html
    assert common_source["download"] == "downloads/The_Common_Source_Trap.pdf"
    incentive = next(item for item in publications if item["slug"] == "incentive-to-ignore")
    assert incentive["download"] == "downloads/The_Incentive_to_Ignore.pdf"
    incentive_html = (output / incentive["detail"]).read_text(encoding="utf-8")
    assert "working paper · no DOI · not submitted · not peer reviewed" in incentive_html
    threshold = next(item for item in publications if item["slug"] == "threshold-discovery")
    assert threshold["download"] == "downloads/Threshold_Discovery.pdf"
    threshold_html = (output / threshold["detail"]).read_text(encoding="utf-8")
    assert "working paper · no DOI · not submitted · not peer reviewed" in threshold_html

    routes = json.loads((output / "data/routes.json").read_text(encoding="utf-8"))["routes"]
    route_paths = {route["path"] for route in routes}
    assert route_paths == {str(path.relative_to(output)) for path in output.glob("**/*.html")}
    assert {
        "research/dd-008b.html",
        "research/dd-010.html",
        "research/dd-011.html",
        "benchmark.html",
        "benchmark/tasks.html",
        "benchmark/protocols.html",
        "benchmark/metrics.html",
        "benchmark/results.html",
        "benchmark/attention.html",
        "experiment-kit.html",
        "experiment-kit/hypotheses.html",
        "experiment-kit/design.html",
        "experiment-kit/power.html",
        "experiment-kit/attention.html",
        "experiment-kit/threshold-dynamic.html",
        "labs/benchmark.html",
        "labs/experiment-design.html",
        "labs/attention.html",
        "labs/audience.html",
        "labs/audience-design.html",
        "labs/conditional-attention.html",
        "labs/threshold.html",
        "labs/equilibrium-selection.html",
        "labs/dynamic-attention.html",
        "labs/team-mechanisms.html",
        "labs/incremental-sharing.html",
        "labs/general-sharing-frontier.html",
        "publications/common-source-trap.html",
        "publications/incentive-to-ignore.html",
        "publications/threshold-discovery.html",
        "program.html",
    } <= route_paths
    assert (output / "robots.txt").is_file()
    assert (output / "sitemap.xml").is_file()
    sitemap = (output / "sitemap.xml").read_text(encoding="utf-8")
    assert "404.html" not in sitemap
    assert all(
        f"https://yoheinakajima.github.io/distributed-discovery/{route}" in sitemap
        for route in route_paths - {"404.html"}
    )
    download_manifest = json.loads((output / "data/downloads.json").read_text())["downloads"]
    assert {entry["path"] for entry in download_manifest} == {
        str(path.relative_to(output)) for path in (output / "downloads").glob("*")
    }
    for entry in download_manifest:
        artifact = output / entry["path"]
        assert artifact.stat().st_size == entry["bytes"]
        assert hashlib.sha256(artifact.read_bytes()).hexdigest() == entry["sha256"]
    mechanisms = json.loads((output / "data/labs/mechanisms.json").read_text())
    assert "20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b" in mechanisms["run_ids"]
    assert len(mechanisms["rows"]) == 375
    assert any(row.get("strict_margin") == "13/72" for row in mechanisms["rows"])
    atlas = json.loads((output / "data/labs/atlas.json").read_text())
    assert atlas["run_ids"] == ["20260721T171249Z_DD-009_bc78d249_0c3851c41a"]
    assert len(atlas["architectures"]) == 20
    assert len(atlas["validity"]) == 288
    assert sum(row["pareto_status"] == "nondominated" for row in atlas["architectures"]) == 12
    sequential = json.loads((output / "data/labs/sequential.json").read_text())
    assert len(sequential["rows"]) == 16
    sequential_fixture = [
        row
        for row in sequential["rows"]
        if row["case"] == "asymmetric-eight" and row["total_action_budget"] == 4
    ]
    assert (
        len({(row["expected_actions"], row["expected_rounds"]) for row in sequential_fixture}) > 1
    )

    coverage = json.loads((output / "data/labs/coverage.json").read_text())
    coverage_fixture = [
        row for row in coverage["rows"] if row["fixture"] == "duplicated-ranking-witness"
    ]
    assert {row["weighted_union_coverage"] for row in coverage_fixture} == {"3", "4"}
    assert {row["gap_from_optimum"] for row in coverage_fixture} == {"0", "1"}

    mechanism_fixture = [
        row
        for row in mechanisms["rows"]
        if row["family"] == "DD-006B joint score"
        and row["regime"] in {"target-actions", "hidden-actions"}
    ]
    assert (
        len(
            {
                (row["strict_margin"], row["discovery"], row["budget_status"])
                for row in mechanism_fixture
            }
        )
        > 1
    )

    audit = json.loads((output / "data/labs/audit.json").read_text())
    audit_fixture = [
        row
        for row in audit["rows"]
        if row["copying_truth"] == 0.5 and row["provenance_missing_truth"] == 0.0
    ]
    assert len({(row["bias"], row["interval_coverage"]) for row in audit_fixture}) == 2

    acquisition = json.loads((output / "data/labs/evidence-acquisition.json").read_text())
    acquisition_fixture = [
        row
        for row in acquisition["rows"]
        if row["agents"] == 2
        and row["accuracy"] == "1/2"
        and row["mode"] == "equilibrium"
        and row["cost"] in {"0", "1/6"}
    ]
    assert {tuple(row["equilibrium_k"]) for row in acquisition_fixture} == {(0,), (1, 2)}
    assert {row["common_source_trap"] for row in acquisition_fixture} == {False, True}

    assert len({row["architecture_id"] for row in atlas["architectures"]}) == 20
    assert {row["pareto_status"] for row in atlas["architectures"]} == {"dominated", "nondominated"}
    atlas_page = (output / "labs/atlas.html").read_text()
    assert "data-atlas-lab" in atlas_page
    assert atlas_page.count("data-atlas-architecture=") >= 20
    assert "Named coherent architecture" in atlas_page
    assert "explicit rejection reason" in atlas_page
    results_page = (output / "results.html").read_text(encoding="utf-8")
    result_ids = re.findall(r'data-result-id="([^"]+)"', results_page)
    assert len(result_ids) == len(set(result_ids)) == 13
    assert results_page.count('class="finding-stack"') == 6
    assert "Program V3 results" not in results_page

    relations = json.loads((output / "data/relations.json").read_text(encoding="utf-8"))
    assert relations["entity_counts"]["studies"] == 26
    assert relations["entity_counts"]["findings"] == 13
    assert relations["entity_counts"]["labs"] == 17
    assert relations["entity_counts"]["papers"] == 6
    assert relations["entity_counts"]["benchmark_tasks"] == 24
    assert len(relations["relations"]) == 26
    for relation in relations["relations"]:
        assert (output / f"research/{relation['study_id'].lower()}.html").is_file()
        for result_id in relation["result_ids"]:
            assert f'id="{result_id}"' in results_page
        for slug in relation["lab_slugs"]:
            assert (output / f"labs/{slug}.html").is_file()
        for slug in relation["paper_slugs"]:
            assert (output / f"publications/{slug}.html").is_file()
        for task_id in relation["benchmark_task_ids"]:
            assert f'id="{task_id}"' in (output / "benchmark/tasks.html").read_text()
        for route in relation["experiment_routes"] + relation["data_routes"]:
            assert (output / route).is_file()
        for claim_id in relation["claim_ids"]:
            assert f'id="{claim_id}"' in (output / "claims.html").read_text()
        for run_id in relation["run_ids"]:
            assert any(
                run_id == run["run_id"]
                for run in json.loads((output / "data/runs.json").read_text())["runs"]
            )

    for route in [
        "research/dd-012.html",
        "labs/attention.html",
        "publications/incentive-to-ignore.html",
        "benchmark/tasks.html",
        "experiment-kit/attention.html",
    ]:
        page = (output / route).read_text(encoding="utf-8")
        assert "related-resources" in page
        assert "data/relations.json" in page
    threshold_lab = json.loads((output / "data/labs/threshold.json").read_text())
    assert threshold_lab["run_id"] == "20260722T021526Z_DD-016_00271ff8_123b2809e3"
    assert len(threshold_lab["rows"]) == 8
    assert threshold_lab["rows"][1]["planner_discovery"] == "223779310319051/333709716796875"
    equilibrium_lab = json.loads((output / "data/labs/equilibrium-selection.json").read_text())
    assert equilibrium_lab["run_id"] == "20260722T024032Z_DD-017_033452f6_3d2c74fdfb"
    assert len(equilibrium_lab["rows"]) == 160
    assert sum(row["worst_equilibrium_discovery"] == "0" for row in equilibrium_lab["rows"]) == 52
    dynamic_lab = json.loads((output / "data/labs/dynamic-attention.json").read_text())
    assert dynamic_lab["run_id"] == "20260722T043713Z_DD-015_92d53ac1_0e7cf1ec0a"
    assert len(dynamic_lab["rows"]) == 64
    team_lab = json.loads((output / "data/labs/team-mechanisms.json").read_text())
    assert team_lab["run_id"] == "20260722T051847Z_DD-018_a193f602_3b3ddac173"
    assert len(team_lab["rows"]) == 50
    assert sum(row["implements_planner"] for row in team_lab["rows"]) == 40
    incremental_lab = json.loads((output / "data/labs/incremental-sharing.json").read_text())
    assert incremental_lab["run_id"] == "20260722T142551Z_DD-020_3854fff6_37c11a850a"
    assert len(incremental_lab["point_transitions"]) == 2044
    assert len(incremental_lab["channel_transitions"]) == 10
    canonical = next(
        row
        for row in incremental_lab["point_transitions"]
        if row["targets"] == 4
        and row["agents"] == 3
        and row["accuracy"] == "1/2"
        and row["block_size"] == 1
    )
    assert canonical["pooled_accuracy"] == "1/2"
    assert canonical["group_discovery"] == "7/8"
    assert canonical["aggregation_gain"] == "0"
    assert canonical["lost_rescue"] == "1/8"
    assert canonical["net_increment"] == "-1/8"
    guaranteed = next(
        row
        for row in incremental_lab["channel_transitions"]
        if row["channel_id"] == "guaranteed-shortlist-two" and row["block_size"] == 1
    )
    assert guaranteed["aggregation_gain"] == "1/6"
    assert guaranteed["lost_rescue"] == "1/8"
    assert guaranteed["net_increment"] == "1/24"
    assert guaranteed["sign"] == "positive"
    noisy = next(
        row
        for row in incremental_lab["channel_transitions"]
        if row["channel_id"] == "noisy-point-half" and row["block_size"] == 1
    )
    assert noisy["accuracy"] == guaranteed["accuracy"] == "1/2"
    assert noisy["sign"] == "negative"
    for row in incremental_lab["point_transitions"] + incremental_lab["channel_transitions"]:
        assert Fraction(row["aggregation_gain"]) - Fraction(row["lost_rescue"]) == Fraction(
            row["net_increment"]
        )
    run_outputs = ROOT / "results/verified/20260722T142551Z_DD-020_3854fff6_37c11a850a/outputs"
    assert (output / "data/incremental-sharing/point-census.json").read_bytes() == (
        run_outputs / "point-census.json"
    ).read_bytes()
    assert (output / "data/incremental-sharing/channel-profiles.json").read_bytes() == (
        run_outputs / "channel-profiles.json"
    ).read_bytes()
    frontier_page = (output / "labs/general-sharing-frontier.html").read_text(encoding="utf-8")
    assert "data-frontier-lab" in frontier_page
    assert frontier_page.count('data-frontier-row=""') == 177
    assert "JavaScript is off" in frontier_page
    assert "Percentages lead" in frontier_page
    assert "DD-C-0097" in frontier_page and "DD-C-0103" in frontier_page
    assert "20260722T185924Z_DD-021_3cdbbc40_2fea269a9a" in frontier_page
    for control in [
        "frontier-family",
        "frontier-targets",
        "frontier-agents",
        "frontier-parameter",
        "frontier-step",
        "frontier-budget",
    ]:
        assert f'id="{control}"' in frontier_page
    frontier_lab = json.loads((output / "data/labs/general-sharing-frontier.json").read_text())
    assert frontier_lab["run_id"] == "20260722T185924Z_DD-021_3cdbbc40_2fea269a9a"
    assert len(frontier_lab["rows"]) == 177
    assert frontier_lab["witnesses"]["mixed_sharing_curve"] is None
    frontier_outputs = ROOT / "results/verified/20260722T185924Z_DD-021_3cdbbc40_2fea269a9a/outputs"
    assert (output / "data/general-sharing-frontier/registry.json").read_bytes() == (
        frontier_outputs / "registry.json"
    ).read_bytes()

    def distinct_outputs(
        rows: list[dict[str, object]],
        fixed: dict[str, object],
        output_keys: tuple[str, ...],
    ) -> set[tuple[object, ...]]:
        return {
            tuple(row[key] for key in output_keys)
            for row in rows
            if all(row[key] == value for key, value in fixed.items())
        }

    assert (
        len(
            distinct_outputs(
                threshold_lab["rows"],
                {},
                ("planner_discovery", "private_clue_following", "expected_viable_candidates"),
            )
        )
        > 1
    )
    assert (
        len(
            distinct_outputs(
                equilibrium_lab["rows"],
                {"fixture": "tied-top-three", "agents": 4},
                ("best_equilibrium_discovery", "worst_equilibrium_discovery", "pure_nash_count"),
            )
        )
        > 1
    )
    dynamic_output_keys = (
        "planner_discovery",
        "autonomous_discovery",
        "expected_actions",
        "distinct_actions",
    )
    for fixed in [
        {"private_accuracy": "1/2", "shared_accuracy": "3/4", "objective": "fixed-budget"},
        {"agents": 3, "shared_accuracy": "3/4", "objective": "fixed-budget"},
        {"agents": 3, "private_accuracy": "1/2", "objective": "fixed-budget"},
        {"agents": 3, "private_accuracy": "1/2", "shared_accuracy": "3/4"},
    ]:
        assert len(distinct_outputs(dynamic_lab["rows"], fixed, dynamic_output_keys)) > 1
    incremental_outputs = (
        "pooled_accuracy",
        "group_discovery",
        "aggregation_gain",
        "lost_rescue",
        "net_increment",
    )
    for fixed in [
        {"agents": 3, "accuracy": "1/2", "block_size": 2},
        {"targets": 4, "accuracy": "1/2", "block_size": 1},
        {"targets": 4, "agents": 3, "block_size": 1},
        {"targets": 4, "agents": 3, "accuracy": "1/2"},
    ]:
        assert (
            len(distinct_outputs(incremental_lab["point_transitions"], fixed, incremental_outputs))
            > 1
        )
    assert (
        len(
            distinct_outputs(
                incremental_lab["channel_transitions"],
                {"block_size": 1},
                incremental_outputs,
            )
        )
        > 1
    )
    mechanism_output_keys = (
        "discovery",
        "implements_planner",
        "strict_unilateral",
        "pairwise_stable",
        "equilibrium_multiplicity",
    )
    assert (
        len(distinct_outputs(team_lab["rows"], {"mechanism": "team-tokens"}, mechanism_output_keys))
        > 1
    )
    assert (
        len(distinct_outputs(team_lab["rows"], {"fixture": "moderate"}, mechanism_output_keys)) > 1
    )
    labs_manifest = json.loads((output / "data/labs.json").read_text())
    for data_name in [
        "threshold_data",
        "equilibrium_selection_data",
        "dynamic_attention_data",
        "team_mechanisms_data",
        "incremental_sharing_data",
        "general_sharing_frontier_data",
    ]:
        assert (output / labs_manifest[data_name]).is_file()
    benchmark = json.loads((output / "data/benchmark/summary.json").read_text())
    assert benchmark["run_id"] == "20260722T054447Z_DD-010_d265e480_6930915b02"
    assert benchmark["schema_version"] == 3
    assert benchmark["summary"]["task_count"] == 24
    assert benchmark["summary"]["compatible_pairs"] == 36
    assert (output / "downloads/discoverybench-task-v1.schema.json").is_file()
    assert (output / "downloads/discoverybench-task-v2.schema.json").is_file()
    assert (output / "downloads/discoverybench-task-v3.schema.json").is_file()
    assert (output / "downloads/dd011-design-v3.schema.json").is_file()
    experiment = json.loads((output / "data/experiment/summary.json").read_text())
    assert experiment["run_id"] == "20260722T061958Z_DD-011_5743ccba_19b6517655"
    assert experiment["schema_version"] == 3
    assert experiment["summary"]["treatment_cells"] == 37
    assert experiment["summary"]["hypotheses"] == 20
    assert experiment["summary"]["outcomes"] == 23
    assert experiment["summary"]["response_scenarios"] == 14
    assert experiment["summary"]["power_rows"] == 1680
    assert experiment["summary"]["calibration_failures_retained"] == 644
    assert experiment["summary"]["no_human_data"] is True
    attention_summary = json.loads((output / "data/attention/summary.json").read_text())
    assert attention_summary["run_id"] == "20260721T212943Z_DD-012_9ed0928e_4a3f1ba62b"
    assert attention_summary["summary"]["grid_cells"] == 175
    assert attention_summary["summary"]["profiles"] == 1050
    assert attention_summary["summary"]["reward_rules"] == 7
    audience = json.loads((output / "data/audience/summary.json").read_text())
    assert audience["run_id"] == "20260721T215811Z_DD-013_09c07448_cdac4fb512"
    assert audience["summary"]["binding_audience_rows"] == 1050
    assert audience["summary"]["garbling_rows"] == 2625
    institutions = json.loads((output / "data/audience/institutions.json").read_text())
    assert len(institutions["institutions"]) == 8
    for name in [
        "dd011-preregistration-template.md",
        "dd011-participant-instructions.md",
        "dd011-researcher-protocol.md",
        "dd011-data-dictionary.md",
        "dd011-design-v1.schema.json",
        "dd011-design-v2.schema.json",
        "dd011-randomization.md",
    ]:
        assert (output / f"downloads/{name}").is_file()

    home = (output / "index.html").read_text(encoding="utf-8")
    assert "How groups turn evidence into portfolios of action." in home
    assert "Better shared information can produce worse collective discovery." in home
    assert "Share the evidence. <strong>Diversify the actions.</strong>" in home
    assert "The Incentive to Ignore" in home
    assert "Threshold Discovery" in home
    assert (
        "When actions require teams, form the smallest viable teams and diversify those teams."
        in home
    )
    assert "See the paradox" in home
    assert (output / "og.png").is_file()

    papers_page = (output / "publications.html").read_text(encoding="utf-8")
    assert 'href="program.html"' in papers_page

    stylesheet = (output / "styles.css").read_text(encoding="utf-8")
    assert "repeat(auto-fit, minmax(min(100%, 16rem), 1fr))" in stylesheet
    assert "grid-template-columns: repeat(7" not in stylesheet
    assert ".pipeline" not in stylesheet
    assert "font: 1.025rem/1.62 var(--sans)" in stylesheet
    assert "position: sticky" in stylesheet
    javascript = (output / "site.js").read_text(encoding="utf-8")
    assert 'querySelectorAll("[data-output-lab]")' in javascript
    assert "data-${control.dataset.filterKey}" in javascript

    for page in output.glob("**/*.html"):
        source = page.read_text(encoding="utf-8")
        header_match = re.search(r'<header class="site-header".*?</header>', source, re.DOTALL)
        assert header_match is not None
        header = header_match.group(0)
        assert header.count("<nav ") == 1
        primary = re.search(r'<div class="nav-links">(.*?)</div>', header, re.DOTALL)
        assert primary is not None
        assert primary.group(1).count("<a ") == 5
        assert "Research navigation" not in header
        assert "secondary" not in header
        assert source.count("<table") == source.count("<caption")

    for route in [
        "research/dd-013.html",
        "labs/attention.html",
        "labs/audience-design.html",
        "labs/audience.html",
        "benchmark/results.html",
        "experiment-kit/power.html",
        "publications/common-source-trap.html",
    ]:
        nested = (output / route).read_text(encoding="utf-8")
        assert 'aria-label="Breadcrumb"' in nested
        assert 'href="../index.html"' in nested

    study_source = (output / "research/dd-013.html").read_text(encoding="utf-8")
    assert "The question" in study_source
    assert "What we found" in study_source
    assert "What this result covers" in study_source
    assert "Reproducible evidence" in study_source
    assert "Files and data" in study_source
    assert "What comes next" in study_source
    assert "three-verified-theorems-and-independently-reproduced-voluntary-census" in study_source
    assert "Technical details" in study_source

    papers = (output / "publications.html").read_text(encoding="utf-8")
    assert "<h1>Papers</h1>" in papers
    assert "Validated working paper" in papers
    assert "SHA-256" in papers
    assert "Technical details" in papers

    benchmark_overview = (output / "benchmark.html").read_text(encoding="utf-8")
    assert "Compare search strategies" in benchmark_overview
    assert "Benchmark tasks" in benchmark_overview
    assert "What each strategy can see and do" in benchmark_overview
    assert "How performance is measured" in benchmark_overview

    experiment_overview = (output / "experiment-kit.html").read_text(encoding="utf-8")
    assert "Plan a discovery experiment" in experiment_overview
    assert "Materials and safeguards" in experiment_overview
    assert "No participants were recruited" in experiment_overview
    assert "Threshold and dynamic extension" in experiment_overview
    threshold_dynamic_experiment = (output / "experiment-kit/threshold-dynamic.html").read_text(
        encoding="utf-8"
    )
    assert "Eight synthetic treatments" in threshold_dynamic_experiment
    assert "not behavioral findings" in threshold_dynamic_experiment
    assert "Threshold + dynamics" in threshold_dynamic_experiment

    results = (output / "results.html").read_text(encoding="utf-8")
    for phrase in [
        "The first reader can help; duplicate use can reduce discovery.",
        "contains 63 excessive-attention cells",
        "One reader can be the discovery-maximizing audience.",
        "The registered conditional-policy theorem is not unrestricted.",
    ]:
        assert phrase in results


def test_research_library_rejects_missing_public_metadata(tmp_path: Path) -> None:
    copied = tmp_path / "repo"
    copied.mkdir()
    for name in [
        "claims",
        "results",
        "studies",
        "papers",
        "reports",
        "design",
        "site",
        "src",
        "experiments",
    ]:
        source = ROOT / name
        target = copied / name
        if source.is_dir():
            shutil.copytree(source, target)
    missing = copied / "studies/DD-004-sequential-discovery/public.yml"
    missing.unlink()
    try:
        build(copied, copied / "dist")
    except RuntimeError as error:
        assert "missing public metadata" in str(error)
    else:
        raise AssertionError("missing public metadata was accepted")
