from pathlib import Path

import pytest

from distributed_discovery.site.copy import load_copy_map
from distributed_discovery.site.navigation import (
    PRIMARY_LINKS,
    prefix_for,
    render_breadcrumb,
    render_footer,
    render_header,
)
from distributed_discovery.site.status_labels import human_status

ROOT = Path(__file__).resolve().parents[2]


def test_copy_map_defines_the_approved_public_navigation() -> None:
    copy_map = load_copy_map(ROOT / "design/site-refresh/copy-map.yml")

    assert [item["label"] for item in copy_map["navigation"]["primary"]] == [
        "Home",
        "Research",
        "Results",
        "Labs",
        "Papers",
    ]
    assert [item["route"] for item in copy_map["navigation"]["primary"]] == [
        route for _, route in PRIMARY_LINKS
    ]
    assert copy_map["brand"]["name"] == "Distributed Discovery"
    assert copy_map["brand"]["principle"] == "Share the evidence. Diversify the actions."


def test_copy_map_rejects_an_incomplete_primary_navigation(tmp_path: Path) -> None:
    invalid = tmp_path / "copy.yml"
    invalid.write_text("schema_version: 1\nnavigation:\n  primary: []\n  resources: []\n")

    with pytest.raises(RuntimeError, match="missing sections"):
        load_copy_map(invalid)


@pytest.mark.parametrize(
    ("raw", "kind", "expected"),
    [
        ("complete-bounded-study", "phase", "Completed finite study"),
        ("active-extension", "phase", "Active research"),
        ("registered", "phase", "Planned study"),
        ("independently-reproduced", "evidence", "Checked independently"),
        ("seeded-synthetic-power", "evidence", "Synthetic only"),
        ("no-result-registration-only", "evidence", "Open question"),
        ("validated-repository-paper", "publication", "Validated working paper"),
    ],
)
def test_human_status_maps_machine_values(raw: str, kind: str, expected: str) -> None:
    assert human_status(raw, kind=kind) == expected


def test_shell_has_one_five_item_global_nav_and_footer_resources() -> None:
    header = render_header("research/dd-013.html")
    footer = render_footer("research/dd-013.html", "https://example.test/repository")

    assert header.count("<nav ") == 1
    assert header.count("<a ") == 6  # brand plus five primary destinations
    assert 'href="../research.html" aria-current="page"' in header
    assert "Research navigation" not in header
    assert "Foundations" in footer
    assert "Experiment Kit" in footer
    assert "Repository" in footer


def test_nested_navigation_uses_relative_links_and_semantic_breadcrumbs() -> None:
    assert prefix_for("research/dd-013.html") == "../"
    breadcrumb = render_breadcrumb("research/dd-013.html", "Audience Design")
    assert 'aria-label="Breadcrumb"' in breadcrumb
    assert 'href="../index.html"' in breadcrumb
    assert 'href="../research.html"' in breadcrumb
    assert 'aria-current="page">Audience Design' in breadcrumb
