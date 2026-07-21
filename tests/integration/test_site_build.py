import json
import shutil
from pathlib import Path

from distributed_discovery.site.build import build

ROOT = Path(__file__).resolve().parents[2]


def test_research_library_builds_from_validated_repository_evidence(tmp_path: Path) -> None:
    output = tmp_path / "site"
    report = build(ROOT, output)

    assert report["page_count"] == 26
    assert report["study_count"] == 9
    assert report["claim_count"] == 51
    assert report["passing_run_count"] == 21
    assert report["publication_count"] == 3
    assert report["internal_links_passed"] is True
    assert report["public_safety_passed"] is True

    research = (output / "research.html").read_text(encoding="utf-8")
    assert "DD-000" in research and "DD-008" in research
    assert "complete-bounded-study" in research
    assert 'href="research/dd-004.html"' in research
    assert (output / "research/dd-000.html").is_file()
    assert (output / "research/dd-008.html").is_file()
    assert (output / "labs.html").is_file()
    for name in ["sequential", "coverage", "mechanisms", "audit", "evidence-acquisition"]:
        page = (output / f"labs/{name}.html").read_text(encoding="utf-8")
        assert 'type="range"' in page
        assert "bounded fixture only" in page

    claims = (output / "claims.html").read_text(encoding="utf-8")
    assert 'id="DD-C-0001"' in claims
    assert 'id="DD-C-0044"' in claims
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
