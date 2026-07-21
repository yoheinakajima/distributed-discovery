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
    assert report["page_count"] == len(list(output.glob("**/*.html")))
    assert report["study_count"] == expected_studies
    assert report["claim_count"] == expected_claims
    assert report["passing_run_count"] == expected_passing_runs
    assert report["publication_count"] == 3
    assert report["internal_links_passed"] is True
    assert report["public_safety_passed"] is True

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
    assert (output / "benchmark.html").is_file()
    for route in ["tasks", "protocols", "metrics", "results"]:
        assert (output / f"benchmark/{route}.html").is_file()
    benchmark_lab = (output / "labs/benchmark.html").read_text()
    assert "no submissions" in benchmark_lab
    assert "JavaScript is off" in benchmark_lab
    assert (output / "labs.html").is_file()
    for name in [
        "sequential",
        "coverage",
        "mechanisms",
        "audit",
        "evidence-acquisition",
        "atlas",
    ]:
        page = (output / f"labs/{name}.html").read_text(encoding="utf-8")
        assert 'type="range"' in page
        assert "bounded fixture only" in page

    claims = (output / "claims.html").read_text(encoding="utf-8")
    assert 'id="DD-C-0001"' in claims
    assert 'id="DD-C-0044"' in claims
    assert 'id="DD-C-0053"' in claims
    assert 'id="DD-C-0054"' in claims
    assert 'id="DD-C-0055"' in claims
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

    routes = json.loads((output / "data/routes.json").read_text(encoding="utf-8"))["routes"]
    assert {route["path"] for route in routes} == {
        str(path.relative_to(output)) for path in output.glob("**/*.html")
    }
    assert (output / "robots.txt").is_file()
    assert (output / "sitemap.xml").is_file()
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
