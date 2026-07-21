import hashlib
import json
import re
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
    assert "Completed finite study" in research
    assert ">complete-bounded-study<" not in research
    assert 'type="search"' in research
    assert 'data-study-filter="key-results"' in research
    assert 'aria-live="polite"' in research
    assert 'href="research/dd-004.html"' in research
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
        assert 'type="range"' in page_source
        assert "bounded fixture only" in page_source

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
        "labs/benchmark.html",
        "labs/experiment-design.html",
        "labs/attention.html",
        "labs/audience.html",
        "labs/audience-design.html",
        "labs/conditional-attention.html",
        "publications/common-source-trap.html",
        "publications/incentive-to-ignore.html",
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
    assert benchmark["run_id"] == "20260721T230249Z_DD-010_add85590_56c61a2195"
    assert benchmark["schema_version"] == 2
    assert benchmark["summary"]["task_count"] == 20
    assert benchmark["summary"]["compatible_pairs"] == 28
    assert (output / "downloads/discoverybench-task-v1.schema.json").is_file()
    assert (output / "downloads/discoverybench-task-v2.schema.json").is_file()
    experiment = json.loads((output / "data/experiment/summary.json").read_text())
    assert experiment["run_id"] == "20260721T232119Z_DD-011_121162f8_e454b06d2c"
    assert experiment["schema_version"] == 2
    assert experiment["summary"]["treatment_cells"] == 29
    assert experiment["summary"]["hypotheses"] == 14
    assert experiment["summary"]["response_scenarios"] == 11
    assert experiment["summary"]["power_rows"] == 924
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
    assert "See the paradox" in home
    assert (output / "og.png").is_file()

    stylesheet = (output / "styles.css").read_text(encoding="utf-8")
    assert "repeat(auto-fit, minmax(min(100%, 16rem), 1fr))" in stylesheet
    assert "grid-template-columns: repeat(7" not in stylesheet
    assert ".pipeline" not in stylesheet
    assert "font: 1.025rem/1.62 var(--sans)" in stylesheet
    assert "position: sticky" in stylesheet

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
