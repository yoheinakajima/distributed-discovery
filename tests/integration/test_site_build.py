import hashlib
import json
import shutil
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

    research = (output / "research.html").read_text(encoding="utf-8")
    assert "DD-000" in research and "DD-008" in research
    assert "complete-bounded-study" in research
    assert 'href="research/dd-004.html"' in research
    assert (output / "research/dd-000.html").is_file()
    assert (output / "research/dd-008.html").is_file()
    assert (output / "research/dd-008a.html").is_file()
    assert (output / "research/dd-006b.html").is_file()
    assert (output / "research/dd-009.html").is_file()
    assert (output / "research/dd-010.html").is_file()
    assert (output / "research/dd-011.html").is_file()
    assert (output / "benchmark.html").is_file()
    for route in ["tasks", "protocols", "metrics", "results"]:
        assert (output / f"benchmark/{route}.html").is_file()
    benchmark_lab = (output / "labs/benchmark.html").read_text()
    assert "no submissions" in benchmark_lab
    assert "JavaScript is off" in benchmark_lab
    assert (output / "labs.html").is_file()
    assert (output / "experiment-kit.html").is_file()
    for route in ["hypotheses", "design", "power"]:
        page = output / f"experiment-kit/{route}.html"
        assert page.is_file()
        assert "No participants were recruited" in page.read_text()
    experiment_lab = (output / "labs/experiment-design.html").read_text()
    assert "data-experiment-lab" in experiment_lab
    assert "JavaScript is off" in experiment_lab
    assert "No participants were recruited" in experiment_lab
    for name in [
        "sequential",
        "coverage",
        "mechanisms",
        "audit",
        "evidence-acquisition",
        "atlas",
    ]:
        page_source = (output / f"labs/{name}.html").read_text(encoding="utf-8")
        assert 'type="range"' in page_source
        assert "bounded fixture only" in page_source

    claims = (output / "claims.html").read_text(encoding="utf-8")
    assert 'id="DD-C-0001"' in claims
    assert 'id="DD-C-0044"' in claims
    assert 'id="DD-C-0053"' in claims
    assert 'id="DD-C-0054"' in claims
    assert 'id="DD-C-0055"' in claims
    assert 'id="DD-C-0056"' in claims
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
        "experiment-kit.html",
        "experiment-kit/hypotheses.html",
        "experiment-kit/design.html",
        "experiment-kit/power.html",
        "labs/benchmark.html",
        "labs/experiment-design.html",
        "publications/common-source-trap.html",
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
    assert mechanisms["run_id"] == "20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b"
    assert mechanisms["strict_rows"] == 16
    assert mechanisms["maximum_margin"] == "13/72"
    atlas = json.loads((output / "data/labs/atlas.json").read_text())
    assert atlas["run_id"] == "20260721T171249Z_DD-009_bc78d249_0c3851c41a"
    assert atlas["summary"]["valid_cells"] == 20
    assert atlas["summary"]["pareto_cells"] == 12
    atlas_page = (output / "labs/atlas.html").read_text()
    assert 'max="20"' in atlas_page
    assert "Architecture index" in atlas_page
    benchmark = json.loads((output / "data/benchmark/summary.json").read_text())
    assert benchmark["run_id"] == "20260721T183014Z_DD-010_ce930050_8ec718c242"
    assert benchmark["summary"]["task_count"] == 15
    assert benchmark["summary"]["compatible_pairs"] == 16
    assert (output / "downloads/discoverybench-task-v1.schema.json").is_file()
    experiment = json.loads((output / "data/experiment/summary.json").read_text())
    assert experiment["run_id"] == "20260721T185647Z_DD-011_fa0271d9_fcaa647c55"
    assert experiment["summary"]["treatment_cells"] == 20
    assert experiment["summary"]["power_rows"] == 384
    assert experiment["summary"]["no_human_data"] is True
    for name in [
        "dd011-preregistration-template.md",
        "dd011-participant-instructions.md",
        "dd011-researcher-protocol.md",
        "dd011-data-dictionary.md",
        "dd011-design-v1.schema.json",
    ]:
        assert (output / f"downloads/{name}").is_file()


def test_research_library_rejects_missing_public_metadata(tmp_path: Path) -> None:
    copied = tmp_path / "repo"
    copied.mkdir()
    for name in [
        "claims",
        "results",
        "studies",
        "papers",
        "reports",
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
