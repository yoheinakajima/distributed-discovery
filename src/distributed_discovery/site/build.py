"""Build and validate the private static companion site from repository evidence."""

from __future__ import annotations

import html
import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml

from distributed_discovery.validation.bootstrap import repository_root


class SiteParser(HTMLParser):
    """Collect structural elements and links for lightweight validation."""

    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.headings: list[int] = []
        self.tags: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.add(tag)
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(str(values["id"]))
        if tag == "a" and values.get("href"):
            self.hrefs.append(str(values["href"]))
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))


def _passing_baseline(root: Path) -> Path:
    candidates: list[Path] = []
    for validation_path in root.glob("results/baseline/*/validation.json"):
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        manifest_path = validation_path.with_name("manifest.json")
        if validation.get("passed") and manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("validation_status") == "passed" and manifest.get("exit_status") == 0:
                candidates.append(validation_path.parent)
    if not candidates:
        raise RuntimeError("no passing canonical baseline run found")
    return sorted(candidates)[-1]


def _question_text(path: Path) -> str:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return (
        " ".join(line for line in lines if line and not line.startswith("#"))
        .replace(r"\(", "")
        .replace(r"\)", "")
    )


def _study_data(root: Path) -> list[dict[str, str]]:
    studies: list[dict[str, str]] = []
    for directory in sorted((root / "studies").glob("DD-00*")):
        status = yaml.safe_load((directory / "status.yml").read_text(encoding="utf-8"))
        if status["study_id"] == "DD-000":
            continue
        title = directory.name.split("-", 2)[-1].replace("-", " ").title()
        studies.append(
            {
                "id": status["study_id"],
                "title": title,
                "question": _question_text(directory / "question.md"),
                "registry_status": status["status"],
                "evidence_status": status["evidence_status"],
                "next_action": status["next_action"],
                "display_status": "Open question",
            }
        )
    if len(studies) != 7:
        raise RuntimeError(f"expected seven open studies, found {len(studies)}")
    return studies


def _study_cards(studies: list[dict[str, str]]) -> str:
    cards: list[str] = []
    for study in studies:
        cards.append(
            "\n".join(
                [
                    '<article class="problem-card">',
                    '  <div class="problem-meta">',
                    f'    <span class="study-id">{html.escape(study["id"])}</span>',
                    f'    <span class="badge open">{html.escape(study["display_status"])}</span>',
                    "  </div>",
                    f"  <h2>{html.escape(study['title'])}</h2>",
                    f"  <p>{html.escape(study['question'])}</p>",
                    '  <dl class="status-list">',
                    "    <div><dt>Registry</dt><dd>"
                    f"{html.escape(study['registry_status'])}</dd></div>",
                    "    <div><dt>Evidence</dt><dd>"
                    f"{html.escape(study['evidence_status'])}</dd></div>",
                    f"    <div><dt>Next</dt><dd>{html.escape(study['next_action'])}</dd></div>",
                    "  </dl>",
                    "</article>",
                ]
            )
        )
    return "\n".join(cards)


def _canonical_data(run: Path) -> dict[str, Any]:
    config = yaml.safe_load((run / "config.yml").read_text(encoding="utf-8"))
    metrics = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    return {
        "schema_version": 1,
        "source_run_id": manifest["run_id"],
        "upstream_commit": manifest["upstream_commit"],
        "parameters": config["parameters"],
        "metrics": {
            key: metrics[key]
            for key in [
                "blind",
                "consensus",
                "market",
                "private",
                "planner",
                "recovery_budget",
            ]
        },
        "evidence": {
            "blind": "independently-reproduced",
            "consensus": "independently-reproduced",
            "market": "verified-upstream-computation",
            "private": "independently-reproduced",
            "planner": "independently-reproduced",
            "recovery_budget": "independently-reproduced",
        },
        "claim_ids": {
            "blind": "DD-C-0003",
            "private": "DD-C-0004",
            "consensus": "DD-C-0005",
            "planner": "DD-C-0006",
            "market": "DD-C-0007",
            "recovery_budget": "DD-C-0008",
        },
    }


def _replacements(canonical: dict[str, Any], studies: list[dict[str, str]]) -> dict[str, str]:
    parameters = canonical["parameters"]
    metrics = canonical["metrics"]

    def percent(value: float | int) -> str:
        return f"{100 * value:.2f}%"

    return {
        "{{CANDIDATES}}": str(parameters["candidates"]),
        "{{SEARCHERS}}": str(parameters["searchers"]),
        "{{CLUE_ACCURACY}}": percent(parameters["clue_accuracy"]),
        "{{CONSENSUS}}": percent(metrics["consensus"]),
        "{{PRIVATE}}": percent(metrics["private"]),
        "{{PLANNER}}": percent(metrics["planner"]),
        "{{RECOVERY_BUDGET}}": str(metrics["recovery_budget"]),
        "{{RUN_ID}}": str(canonical["source_run_id"]),
        "{{UPSTREAM_COMMIT}}": str(canonical["upstream_commit"]),
        "{{STUDY_CARDS}}": _study_cards(studies),
    }


def validate_site(output: Path) -> dict[str, Any]:
    pages = sorted(output.glob("*.html"))
    errors: list[str] = []
    for page in pages:
        source = page.read_text(encoding="utf-8")
        parser = SiteParser()
        parser.feed(source)
        if "{{" in source or "}}" in source:
            errors.append(f"{page.name}: unresolved template marker")
        for required in ["main", "nav", "header", "footer"]:
            if required not in parser.tags:
                errors.append(f"{page.name}: missing {required}")
        if not parser.headings or parser.headings[0] != 1:
            errors.append(f"{page.name}: first heading must be h1")
        if any(
            next_level > level + 1
            for level, next_level in zip(parser.headings, parser.headings[1:], strict=False)
        ):
            errors.append(f"{page.name}: skipped heading level")
        tracking_markers = ["googletagmanager", "google-analytics.com", "plausible.io/js"]
        if any(marker in source.lower() for marker in tracking_markers):
            errors.append(f"{page.name}: tracking-like content found")
        for href in parser.hrefs:
            parsed = urlsplit(href)
            if parsed.scheme in {"http", "https", "mailto"}:
                continue
            target = page if not parsed.path else (page.parent / parsed.path).resolve()
            if not target.exists():
                errors.append(f"{page.name}: broken link {href}")
                continue
            if parsed.fragment and target.suffix == ".html":
                target_parser = SiteParser()
                target_parser.feed(target.read_text(encoding="utf-8"))
                if parsed.fragment not in target_parser.ids:
                    errors.append(f"{page.name}: missing fragment {href}")
    if len(pages) != 4:
        errors.append(f"expected four HTML pages, found {len(pages)}")
    if errors:
        raise RuntimeError("site validation failed:\n" + "\n".join(errors))
    return {
        "schema_version": 1,
        "pages": [page.name for page in pages],
        "page_count": len(pages),
        "internal_links_passed": True,
        "semantic_structure_passed": True,
        "template_markers_resolved": True,
        "tracking_absent": True,
    }


def build(root: Path, output: Path) -> dict[str, Any]:
    run = _passing_baseline(root)
    canonical = _canonical_data(run)
    studies = _study_data(root)
    source = root / "site/src"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for asset in ["styles.css", "site.js"]:
        shutil.copy2(source / asset, output / asset)
    replacements = _replacements(canonical, studies)
    for template in sorted(source.glob("*.html")):
        rendered = template.read_text(encoding="utf-8")
        for marker, value in replacements.items():
            rendered = rendered.replace(marker, value)
        (output / template.name).write_text(rendered, encoding="utf-8")
    data_dir = output / "data"
    data_dir.mkdir()
    (data_dir / "canonical.json").write_text(
        json.dumps(canonical, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (data_dir / "studies.json").write_text(
        json.dumps(studies, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    shutil.copy2(root / "claims/claims.yml", data_dir / "claims.yml")
    report = validate_site(output)
    report["canonical_source_run"] = canonical["source_run_id"]
    report["study_count"] = len(studies)
    (output / "build-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    root = repository_root()
    report = build(root, root / "site/dist")
    print(
        f"site build passed: {report['page_count']} pages, "
        f"{report['study_count']} open studies, source {report['canonical_source_run']}"
    )


if __name__ == "__main__":
    main()
