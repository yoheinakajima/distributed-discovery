from pathlib import Path

from distributed_discovery.site.build import build

ROOT = Path(__file__).resolve().parents[2]


def _relative_luminance(color: str) -> float:
    channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(first: str, second: str) -> float:
    light, dark = sorted([_relative_luminance(first), _relative_luminance(second)], reverse=True)
    return (light + 0.05) / (dark + 0.05)


def test_site_builds_from_repository_evidence(tmp_path: Path) -> None:
    report = build(ROOT, tmp_path / "site")
    assert report["page_count"] == 5
    assert report["study_count"] == 7
    assert report["internal_links_passed"] is True
    index = (tmp_path / "site/index.html").read_text(encoding="utf-8")
    assert "38.35%" in index
    assert "{{" not in index
    problems = (tmp_path / "site/open-problems.html").read_text(encoding="utf-8")
    assert problems.count('class="badge open"') == 7
    results = (tmp_path / "site/results.html").read_text(encoding="utf-8")
    assert "16/25" in results
    assert "7/10" in results
    assert "5/9" in results and "171/308" in results
    assert "8/9" in results and "31/36" in results
    assert "bounded null, not a theorem" in results.lower()
    generated = (tmp_path / "site/data/results.json").read_text(encoding="utf-8")
    assert "20260721T012208Z_DD-000_8e4b55e2_e8321d1048" in generated


def test_primary_text_colors_exceed_wcag_aa() -> None:
    assert _contrast("#0b0b0b", "#f9f9f7") >= 4.5
    assert _contrast("#52514e", "#f9f9f7") >= 4.5
    assert _contrast("#706f69", "#f9f9f7") >= 4.5
    assert _contrast("#ffffff", "#0d0d0d") >= 4.5
    assert _contrast("#c3c2b7", "#0d0d0d") >= 4.5
    assert _contrast("#aaa89f", "#0d0d0d") >= 4.5
