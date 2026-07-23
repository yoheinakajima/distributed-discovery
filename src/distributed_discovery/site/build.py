"""Build and validate the public research-library site from repository evidence."""

# ruff: noqa: E501

from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml

from distributed_discovery.site.copy import load_copy_map
from distributed_discovery.site.core_labs import build_core_labs
from distributed_discovery.site.navigation import (
    render_breadcrumb,
    render_footer,
    render_header,
    render_section_navigation,
)
from distributed_discovery.site.numbers import expected_count, probability
from distributed_discovery.site.status_labels import human_status
from distributed_discovery.validation.bootstrap import repository_root

PUBLIC_BASE = "https://yoheinakajima.github.io/distributed-discovery/"
REPOSITORY_URL = "https://github.com/yoheinakajima/distributed-discovery"
PHASES = {
    "foundations",
    "exact-result",
    "complete-bounded-study",
    "active-extension",
    "registered",
    "queued",
    "blocked",
    "retired",
}
SAFE_ARTIFACT_SUFFIXES = {".md", ".json", ".csv", ".png", ".svg", ".pdf", ".yml"}
DD006B_RUN = "20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b"
DD009_RUN = "20260721T171249Z_DD-009_bc78d249_0c3851c41a"
DD012_RUN = "20260721T212943Z_DD-012_9ed0928e_4a3f1ba62b"
DD013_RUN = "20260721T215811Z_DD-013_09c07448_cdac4fb512"
DD014_RUN = "20260721T222047Z_DD-014_f5f099a8_ea0276dd16"
DD015_RUN = "20260722T043713Z_DD-015_92d53ac1_0e7cf1ec0a"
DD016_RUN = "20260722T021526Z_DD-016_00271ff8_123b2809e3"
DD017_RUN = "20260722T024032Z_DD-017_033452f6_3d2c74fdfb"
DD018_RUN = "20260722T051847Z_DD-018_a193f602_3b3ddac173"
DD020_RUN = "20260722T142551Z_DD-020_3854fff6_37c11a850a"
DD021_RUN = "20260722T185924Z_DD-021_3cdbbc40_2fea269a9a"
DD022_RUN = "20260722T210334Z_DD-022_2376d5b7_ad67765ca8"


class SiteParser(HTMLParser):
    """Collect enough document structure for generated-route validation."""

    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.id_occurrences: list[str] = []
        self.hrefs: list[str] = []
        self.headings: list[int] = []
        self.tags: set[str] = set()
        self.meta: dict[str, str] = {}
        self.runtime_assets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.add(tag)
        values = dict(attrs)
        if values.get("id"):
            identifier = str(values["id"])
            self.ids.add(identifier)
            self.id_occurrences.append(identifier)
        if tag == "a" and values.get("href"):
            self.hrefs.append(str(values["href"]))
        if tag == "meta" and values.get("name") and values.get("content"):
            self.meta[str(values["name"])] = str(values["content"])
        if tag in {"img", "script"} and values.get("src"):
            self.runtime_assets.append(str(values["src"]))
        if tag == "link" and values.get("rel") == "stylesheet" and values.get("href"):
            self.runtime_assets.append(str(values["href"]))
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected mapping: {path}")
    return value


def _safe_relative(path: str) -> bool:
    candidate = Path(path)
    return not candidate.is_absolute() and ".." not in candidate.parts and "\\" not in path


def _claim_data(root: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    ledger = _read_yaml(root / "claims/claims.yml")
    raw_claims = ledger.get("claims")
    if not isinstance(raw_claims, list):
        raise RuntimeError("claim ledger has no claims list")
    claims: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    for raw in raw_claims:
        if not isinstance(raw, dict):
            raise RuntimeError("claim ledger contains a non-mapping")
        claim_id = raw.get("id")
        if not isinstance(claim_id, str):
            raise RuntimeError("claim without ID")
        summary = {
            key: raw.get(key)
            for key in (
                "id",
                "study_id",
                "short_name",
                "statement",
                "scope",
                "claim_type",
                "status",
                "source_type",
                "source_reference",
                "run_ids",
                "first_added",
                "last_checked",
            )
        }
        claims.append(summary)
        by_id[claim_id] = summary
    return claims, by_id


def _runs(root: Path) -> tuple[list[dict[str, Any]], set[str]]:
    summaries: list[dict[str, Any]] = []
    run_ids: set[str] = set()
    for manifest_path in sorted((root / "results").glob("**/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("validation_status") != "passed" or manifest.get("exit_status") != 0:
            continue
        run_id = manifest.get("run_id")
        study_id = manifest.get("study_id")
        if not isinstance(run_id, str) or not isinstance(study_id, str):
            raise RuntimeError(f"invalid passing manifest: {manifest_path}")
        if run_id != manifest_path.parent.name:
            raise RuntimeError(f"manifest path does not match run ID: {manifest_path}")
        outputs = manifest.get("outputs", {})
        if not isinstance(outputs, dict):
            raise RuntimeError(f"manifest outputs are invalid: {manifest_path}")
        for relative, digest in outputs.items():
            output = manifest_path.parent / relative
            if (
                not isinstance(relative, str)
                or not isinstance(digest, str)
                or not _safe_relative(relative)
                or output.suffix not in SAFE_ARTIFACT_SUFFIXES
                or not output.is_file()
                or _sha256(output) != digest
            ):
                raise RuntimeError(
                    f"unsafe or invalid public run output: {manifest_path}/{relative}"
                )
        relative_manifest = str(manifest_path.relative_to(root))
        summaries.append(
            {
                "run_id": run_id,
                "study_id": study_id,
                "started_utc": manifest.get("started_utc"),
                "ended_utc": manifest.get("ended_utc"),
                "manifest_path": relative_manifest,
                "manifest_sha256": _sha256(manifest_path),
                "output_count": len(outputs),
                "validation_status": "passed",
            }
        )
        run_ids.add(run_id)
    return summaries, run_ids


def _passing_baseline(root: Path) -> Path:
    """Return the latest validated canonical baseline for paper builders."""
    candidates: list[Path] = []
    for validation_path in root.glob("results/baseline/*/validation.json"):
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        manifest_path = validation_path.with_name("manifest.json")
        if not validation.get("passed") or not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("validation_status") == "passed" and manifest.get("exit_status") == 0:
            candidates.append(validation_path.parent)
    if not candidates:
        raise RuntimeError("no passing canonical baseline run found")
    return sorted(candidates)[-1]


def _canonical_data(run: Path) -> dict[str, Any]:
    """Return the compatible canonical summary consumed by paper builders."""
    config = _read_yaml(run / "config.yml")
    metrics = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    return {
        "schema_version": 1,
        "source_run_id": manifest["run_id"],
        "upstream_commit": manifest["upstream_commit"],
        "parameters": config["parameters"],
        "metrics": {
            key: metrics[key]
            for key in ["blind", "consensus", "market", "private", "planner", "recovery_budget"]
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


def _study_data(
    root: Path, claims_by_id: dict[str, dict[str, Any]], run_ids: set[str]
) -> list[dict[str, Any]]:
    studies: list[dict[str, Any]] = []
    for directory in sorted((root / "studies").glob("DD-0*")):
        public_path = directory / "public.yml"
        if not public_path.is_file():
            raise RuntimeError(f"missing public metadata: {public_path}")
        public = _read_yaml(public_path)
        status = _read_yaml(directory / "status.yml")
        study_id = status.get("study_id")
        if public.get("study_id") != study_id or not isinstance(study_id, str):
            raise RuntimeError(f"study ID mismatch: {public_path}")
        phase = public.get("phase")
        if phase not in PHASES:
            raise RuntimeError(f"invalid public phase for {study_id}: {phase}")
        slug = public.get("slug")
        if not isinstance(slug, str) or not re.fullmatch(r"dd-\d{3}[a-z]?", slug):
            raise RuntimeError(f"invalid public slug for {study_id}")
        artifacts = public.get("public_artifacts", [])
        if not isinstance(artifacts, list):
            raise RuntimeError(f"invalid public artifacts for {study_id}")
        checked_artifacts: list[dict[str, str]] = []
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                raise RuntimeError(f"invalid public artifact for {study_id}")
            path = artifact.get("path")
            description = artifact.get("description")
            if (
                not isinstance(path, str)
                or not isinstance(description, str)
                or not _safe_relative(path)
                or Path(path).suffix not in SAFE_ARTIFACT_SUFFIXES
                or not (root / path).is_file()
                or re.search(r"(?:secret|token|password|private key)", path, re.IGNORECASE)
            ):
                raise RuntimeError(f"unsafe public artifact for {study_id}: {path}")
            checked_artifacts.append({"path": path, "description": description})
        study_claims = [claim for claim in claims_by_id.values() if claim["study_id"] == study_id]
        referenced_runs = sorted(
            {run_id for claim in study_claims for run_id in (claim.get("run_ids") or [])}
        )
        missing_runs = set(referenced_runs) - run_ids
        if missing_runs:
            raise RuntimeError(f"claim refers to missing/nonpassing run(s): {sorted(missing_runs)}")
        question = " ".join(
            line.strip()
            for line in (directory / "question.md").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        )
        studies.append(
            {
                "id": study_id,
                "title": public.get("title"),
                "slug": slug,
                "phase": phase,
                "summary": public.get("summary"),
                "question": question,
                "registry_status": status.get("status"),
                "evidence_status": status.get("evidence_status"),
                "next_action": status.get("next_action"),
                "claim_ids": [claim["id"] for claim in study_claims],
                "run_ids": referenced_runs,
                "public_artifacts": checked_artifacts,
            }
        )
    if not studies:
        raise RuntimeError("no public studies found")
    return studies


def _publications(root: Path) -> list[dict[str, Any]]:
    publications: list[dict[str, Any]] = []
    for directory, title in (
        ("foundations", "Foundations of Distributed Discovery"),
        ("three-results", "Three Results in Distributed Discovery"),
        ("discovery-institutions", "Institutions for Distributed Discovery"),
        ("common-source-trap", "The Common-Source Trap"),
        ("incentive-to-ignore", "The Incentive to Ignore"),
        ("threshold-discovery", "Threshold Discovery"),
        (
            "information-sharing-frontier",
            "When Does Information Sharing Improve Decentralized Discovery?",
        ),
    ):
        validation = json.loads((root / "papers" / directory / "validation.json").read_text())
        candidates = sorted((root / "papers" / directory).glob("*.pdf"))
        if len(candidates) != 1:
            raise RuntimeError(f"expected one public PDF in papers/{directory}")
        pdf = candidates[0]
        digest = _sha256(pdf)
        if validation.get("pdf_sha256") != digest:
            raise RuntimeError(f"publication checksum mismatch: {pdf}")
        metadata_path = root / "papers" / directory / "metadata.yml"
        metadata = _read_yaml(metadata_path) if metadata_path.is_file() else {}
        if metadata and metadata.get("title") != title:
            raise RuntimeError(f"publication title mismatch: {metadata_path}")
        author = str(metadata.get("author", "Distributed Discovery project"))
        date = str(metadata.get("date", ""))
        citation = f"{author} ({date}). {title}." if date else f"{author}. {title}."
        citation_bib_path = root / "papers" / directory / "citation.bib"
        citation_bib = (
            citation_bib_path.read_text(encoding="utf-8").strip()
            if citation_bib_path.is_file()
            else ""
        )
        publications.append(
            {
                "title": title,
                "slug": directory,
                "detail": f"publications/{directory}.html",
                "source_pdf": str(pdf.relative_to(root)),
                "download": f"downloads/{pdf.name}",
                "sha256": digest,
                "page_count": validation.get("page_count"),
                "build_source": f"papers/{directory}/main.tex",
                "citation": citation,
                "citation_bib": citation_bib,
                "status": metadata.get("status", "validated-repository-paper"),
                "doi": metadata.get("doi"),
                "submitted": metadata.get("submitted"),
                "peer_reviewed": metadata.get("peer_reviewed"),
            }
        )
    return publications


def _page(title: str, description: str, body: str, current: str) -> str:
    prefix = "../" if "/" in current else ""
    canonical = f"{PUBLIC_BASE}{current}" if current != "index.html" else PUBLIC_BASE
    document_title = (
        "Distributed Discovery" if current == "index.html" else f"{title} — Distributed Discovery"
    )
    layout = (
        "wide"
        if (
            current.startswith(("labs/", "benchmark/", "experiment-kit/"))
            or current
            in {
                "research.html",
                "results.html",
                "labs.html",
                "publications.html",
                "claims.html",
                "evidence.html",
            }
        )
        else "content"
    )
    page_class = current.removesuffix(".html").replace("/", "-") or "home"
    wrapped_body = _wrap_tables(body)
    breadcrumb = render_breadcrumb(current, title)
    section_navigation = render_section_navigation(current)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(document_title)}</title><meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical}"><meta property="og:title" content="{html.escape(document_title)}"><meta property="og:description" content="{html.escape(description)}"><meta property="og:image" content="{PUBLIC_BASE}og.png"><meta property="og:type" content="website"><meta name="twitter:card" content="summary_large_image"><link rel="stylesheet" href="{prefix}styles.css"><script src="{prefix}site.js" defer></script></head>
<body class="page-{html.escape(page_class)}"><a class="skip-link" href="#content">Skip to content</a>{render_header(current)}
<main id="content" class="site-main container-{layout}">{breadcrumb}{section_navigation}{wrapped_body}</main>{render_footer(current, REPOSITORY_URL)}</body></html>"""


def _wrap_tables(body: str) -> str:
    """Add a keyboard-focusable, visibly labelled scroll boundary to each table."""
    return re.sub(
        r'(<table class="matrix".*?</table>)',
        r'<div class="table-region" tabindex="0" aria-label="Scrollable data table"><p class="table-hint">Scroll horizontally to see every column.</p>\1</div>',
        body,
        flags=re.DOTALL,
    )


def _excerpt(value: object, limit: int = 190) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    shortened = text[:limit].rsplit(" ", 1)[0]
    return shortened.rstrip(".,;:") + "…"


def _study_category(study: dict[str, Any]) -> str:
    study_id = str(study["id"])
    categories = ["all"]
    if study_id in {
        "DD-000",
        "DD-001",
        "DD-002",
        "DD-003",
        "DD-006B",
        "DD-008B",
        "DD-009",
        "DD-012",
        "DD-013",
    }:
        categories.append("key-results")
    if study["phase"] == "active-extension":
        categories.append("active")
    if study["phase"] in {"registered", "queued", "blocked"}:
        categories.append("planned")
    if study_id in {"DD-007", "DD-009", "DD-010", "DD-011"}:
        categories.append("tools")
    return " ".join(categories)


def _study_card(study: dict[str, Any], relation: dict[str, Any]) -> str:
    searchable = " ".join(str(study[key]) for key in ("id", "title", "summary", "question")).lower()
    status = human_status(study["phase"])
    return f"""<article class="card study-card {html.escape(study["phase"])}" data-study-card data-category="{html.escape(_study_category(study))}" data-program="{html.escape(str(relation["program"]))}" data-family="{html.escape(str(relation["theorem_family"]))}" data-evidence="{html.escape(str(study["evidence_status"]))}" data-search="{html.escape(searchable)}"><div class="card-meta"><span class="study-id">{html.escape(study["id"])}</span><span class="status-chip">{html.escape(status)}</span></div><h2><a href="research/{html.escape(study["slug"])}.html">{html.escape(str(study["title"]))}</a></h2><p class="card-question">{html.escape(_excerpt(study["question"]))}</p><p class="card-summary">{html.escape(str(study["summary"]))}</p><p class="quiet-meta">{len(study["claim_ids"])} claims · {len(study["run_ids"])} reproducible runs</p><p class="card-link"><a href="research/{html.escape(study["slug"])}.html">Open study <span aria-hidden="true">→</span></a></p></article>"""


def _results_page(
    root: Path,
    studies: list[dict[str, Any]],
    claims_by_id: dict[str, dict[str, Any]],
) -> str:
    registry = _read_yaml(root / "site/content/results.yml")
    if registry.get("schema_version") != 1:
        raise RuntimeError("invalid Results registry schema")
    themes = registry.get("themes")
    results = registry.get("results")
    if not isinstance(themes, list) or not isinstance(results, list):
        raise RuntimeError("Results registry requires theme and result lists")
    study_slugs = {str(study["id"]): str(study["slug"]) for study in studies}
    theme_ids = {str(theme.get("id")) for theme in themes if isinstance(theme, dict)}
    result_ids: set[str] = set()
    grouped: dict[str, list[dict[str, Any]]] = {theme_id: [] for theme_id in theme_ids}
    for result in results:
        if not isinstance(result, dict):
            raise RuntimeError("Results registry contains a non-mapping result")
        result_id = result.get("result_id")
        theme = result.get("theme")
        study_id = result.get("study_id")
        claim_ids = result.get("claim_ids")
        if not isinstance(result_id, str) or result_id in result_ids:
            raise RuntimeError(f"invalid or duplicate result ID: {result_id}")
        if theme not in theme_ids or study_id not in study_slugs:
            raise RuntimeError(f"invalid result ownership: {result_id}")
        if (
            not isinstance(claim_ids, list)
            or not claim_ids
            or any(claim_id not in claims_by_id for claim_id in claim_ids)
        ):
            raise RuntimeError(f"invalid result claims: {result_id}")
        result_ids.add(result_id)
        grouped[str(theme)].append(result)

    groups: list[str] = []
    for theme in sorted(themes, key=lambda item: int(item["order"])):
        theme_id = str(theme["id"])
        findings: list[str] = []
        for result in sorted(grouped[theme_id], key=lambda item: int(item["order"])):
            links = [
                f'<a href="research/{study_slugs[str(result["study_id"])]}.html">Read the study</a>'
            ]
            if result.get("lab_slug"):
                links.append(
                    f'<a href="labs/{html.escape(str(result["lab_slug"]))}.html">Explore the Lab</a>'
                )
            if result.get("paper_slug"):
                links.append(
                    f'<a href="publications/{html.escape(str(result["paper_slug"]))}.html">Read the paper</a>'
                )
            if result.get("paper_slug") == "information-sharing-frontier":
                links.append(
                    '<a href="program.html#information-sharing-frontier">See the theorem family</a>'
                )
            links.extend(
                f'<a href="claims.html#{html.escape(str(claim_id))}">Verify {html.escape(str(claim_id))}</a>'
                for claim_id in result["claim_ids"]
            )
            if result.get("data_route"):
                links.append(
                    f'<a href="{html.escape(str(result["data_route"]))}">Download exact data</a>'
                )
            findings.append(
                '<article class="finding" id="{}" data-result-id="{}"><div><span class="status-chip">{}</span>'
                '<h3>{}</h3><p>{}</p></div><div class="finding-links">{}</div></article>'.format(
                    html.escape(str(result["result_id"])),
                    html.escape(str(result["result_id"])),
                    html.escape(str(result["scope_label"])),
                    html.escape(str(result["title"])),
                    html.escape(str(result["summary"])),
                    "".join(links),
                )
            )
        groups.append(
            '<section class="result-group" data-result-theme="{}"><div class="result-group-heading">'
            '<p class="eyebrow">{}</p><h2>{}</h2></div><div class="finding-stack">{}</div></section>'.format(
                html.escape(theme_id),
                html.escape(str(theme["label"])),
                html.escape(str(theme["heading"])),
                "".join(findings),
            )
        )
    return (
        '<header class="page-hero"><p class="eyebrow">Key findings</p><h1>Findings</h1>'
        '<p class="lede">What the evidence says about gathering information and spreading action across a search portfolio.</p></header>'
        f'<div class="result-groups">{"".join(groups)}</div>'
    )


def _study_page(study: dict[str, Any], claims_by_id: dict[str, dict[str, Any]]) -> str:
    claims = (
        "".join(
            '<li><a href="../claims.html#{}">{}</a>: {}</li>'.format(
                html.escape(claim_id),
                html.escape(claim_id),
                html.escape(str(claims_by_id[claim_id]["statement"])),
            )
            for claim_id in study["claim_ids"]
        )
        or "<li>No substantive claim has been published for this registered study.</li>"
    )
    runs = (
        "".join(f"<li><code>{html.escape(run_id)}</code></li>" for run_id in study["run_ids"])
        or "<li>No passing run yet.</li>"
    )
    artifacts = (
        "".join(
            '<li><a href="{}/blob/main/{}">{}</a></li>'.format(
                REPOSITORY_URL, html.escape(item["path"]), html.escape(item["description"])
            )
            for item in study["public_artifacts"]
        )
        or "<li>No public-safe artifact is registered yet.</li>"
    )
    phase_label = human_status(study["phase"])
    evidence_label = human_status(study["evidence_status"], kind="evidence")
    body = f"""<header class="page-hero"><p class="eyebrow">{html.escape(study["id"])}</p><h1>{html.escape(str(study["title"]))}</h1><p class="lede">{html.escape(str(study["summary"]))}</p><p class="status-row"><span class="status-chip">{html.escape(phase_label)}</span><span class="status-chip subtle">{html.escape(evidence_label)}</span></p></header><nav class="anchor-nav" aria-label="On this study page"><a href="#question">Question</a><a href="#findings">Findings</a><a href="#explore">Explore</a><a href="#evidence">Evidence</a><a href="#next">Next</a></nav><section class="content-section prose"><h2 id="question">The question</h2><p>{html.escape(str(study["question"]))}</p></section><section class="content-section"><h2 id="findings">What we found</h2><ul class="claim-list">{claims}</ul></section><section class="content-section prose"><h2 id="boundary">What this result covers</h2><p>{html.escape(evidence_label)}. The formal evidence wording and registry state remain available below.</p><details class="technical-details"><summary>Technical details</summary><dl><div><dt>Study phase</dt><dd><code>{html.escape(str(study["phase"]))}</code></dd></div><div><dt>Registry status</dt><dd><code>{html.escape(str(study["registry_status"]))}</code></dd></div><div><dt>Evidence status</dt><dd><code>{html.escape(str(study["evidence_status"]))}</code></dd></div></dl></details></section><section class="content-section"><h2 id="evidence">Reproducible evidence</h2><ul class="run-list">{runs}</ul></section><section class="content-section"><h2 id="sources">Files and data</h2><ul>{artifacts}</ul></section><section class="content-section prose"><h2 id="next">What comes next</h2><p>{html.escape(str(study["next_action"]))}</p></section>"""
    return _page(str(study["title"]), str(study["summary"]), body, f"research/{study['slug']}.html")


def _write(output: Path, relative: str, content: str) -> None:
    path = output / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _latest_passing_study_run(root: Path, study_id: str) -> Path:
    candidates = []
    for manifest_path in root.glob("results/**/manifest.json"):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if (
            manifest.get("study_id") == study_id
            and manifest.get("validation_status") == "passed"
            and manifest.get("exit_status") == 0
        ):
            candidates.append(manifest_path.parent)
    if not candidates:
        raise RuntimeError(f"no passing run found for {study_id}")
    return sorted(candidates)[-1]


def _benchmark_pages(root: Path, output: Path) -> dict[str, object]:
    run = _latest_passing_study_run(root, "DD-010")
    source = run / "outputs"
    summary = json.loads((source / "benchmark-summary.json").read_text())
    tasks = json.loads((source / "task-registry.json").read_text())
    protocols = json.loads((source / "protocol-registry.json").read_text())
    metrics = json.loads((source / "metric-registry.json").read_text())
    compatibility = json.loads((source / "compatibility-matrix.json").read_text())
    results = json.loads((source / "exact-result-matrix.json").read_text())
    pareto = json.loads((source / "pareto-report.json").read_text())
    manifest = json.loads((run / "manifest.json").read_text())
    run_id = str(manifest["run_id"])
    benchmark_version = str(summary.get("benchmark_version", "v1"))
    schema_number = 3 if benchmark_version == "v3" else (2 if benchmark_version == "v2" else 1)
    downloads = (
        '<a href="data/benchmark/tasks.json">tasks JSON</a> · '
        '<a href="data/benchmark/protocols.json">protocols JSON</a> · '
        '<a href="data/benchmark/metrics.json">metrics JSON</a> · '
        '<a href="data/benchmark/results.json">results JSON</a> · '
        f'<a href="downloads/discoverybench-task-{benchmark_version}.schema.json">task schema</a>'
    )
    version_flag = f" --version {benchmark_version}" if benchmark_version != "v1" else ""
    claim_id = (
        "DD-C-0087"
        if benchmark_version == "v3"
        else ("DD-C-0069" if benchmark_version == "v2" else "DD-C-0055")
    )
    version_description = (
        "Version 3 adds threshold, equilibrium, dynamic-attention, and team-mechanism fixtures while preserving the v1 default and v2 exact vectors."
        if benchmark_version == "v3"
        else "Version 2 adds selective-attention fixtures while preserving the v1 command default and exact vectors."
    )
    overview = f"""<header class="page-hero"><p class="eyebrow">DiscoveryBench {html.escape(benchmark_version)}</p><h1>Compare search strategies</h1><p class="lede">A bounded, auditable suite for comparing how evidence becomes action. {html.escape(version_description)} It is not a hosted leaderboard or a universal measure of real-world agent quality.</p></header><div class="metric-grid"><article class="metric-card"><span>Benchmark tasks</span><strong>{summary["task_count"]}</strong></article><article class="metric-card"><span>Built-in strategies</span><strong>{summary["protocol_count"]}</strong></article><article class="metric-card"><span>Compatible pairs</span><strong>{summary["compatible_pairs"]}</strong></article></div><p>{downloads}</p><section class="content-section"><h2>Explore the benchmark</h2><div class="card-grid resource-grid"><article class="card"><h3><a href="benchmark/tasks.html">Benchmark tasks</a></h3><p>See the declared information and reference evidence for each task.</p></article><article class="card"><h3><a href="benchmark/protocols.html">What each strategy can see and do</a></h3><p>Compare capability boundaries before comparing results.</p></article><article class="card"><h3><a href="benchmark/metrics.html">How performance is measured</a></h3><p>Inspect every versioned measure and required observable.</p></article><article class="card"><h3><a href="benchmark/results.html">Benchmark results</a></h3><p>Read the exact compatible vectors and scoped Pareto report.</p></article><article class="card"><h3><a href="benchmark/attention.html">Selective-attention extension</a></h3><p>Compare the DD-012--DD-014 attention, audience, and conditional-policy fixtures.</p></article><article class="card"><h3><a href="labs/benchmark.html">Benchmark Lab</a></h3><p>Filter the complete result table by task.</p></article></div></section><section class="content-section prose"><h2>Reproduce</h2><details class="technical-details"><summary>Technical details</summary><p><code>distributed-discovery benchmark{version_flag} run-golden</code><br><code>distributed-discovery benchmark{version_flag} verify-run results/verified/{html.escape(run_id)}</code></p><p>Claim {claim_id} · reproducible run <a href="evidence.html">{html.escape(run_id)}</a>.</p></details></section>"""
    _write(
        output,
        "benchmark.html",
        _page(
            "DiscoveryBench",
            "Exact bounded benchmark for discovery protocols.",
            overview,
            "benchmark.html",
        ),
    )

    claim_owners = {
        str(claim["id"]): str(claim["study_id"])
        for claim in _read_yaml(root / "claims/claims.yml")["claims"]
    }

    def task_row(task: dict[str, Any]) -> str:
        claim_ids = [str(claim_id) for claim_id in task["reference_claims"]]
        study_ids = sorted({claim_owners[claim_id] for claim_id in claim_ids})
        study_links = ", ".join(
            f'<a href="../research/{study_id.lower()}.html">{html.escape(study_id)}</a>'
            for study_id in study_ids
        )
        claim_links = ", ".join(
            f'<a href="../claims.html#{html.escape(claim_id)}">{html.escape(claim_id)}</a>'
            for claim_id in claim_ids
        )
        return f'<tr id="{html.escape(str(task["task_id"]))}" data-task-family="{html.escape(str(task["task_family"]))}"><th scope="row">{html.escape(str(task["task_id"]))}</th><td>{html.escape(str(task["task_family"]))}</td><td>{html.escape(", ".join(task["compatible_protocols"]))}</td><td>{study_links}</td><td>{claim_links}</td></tr>'

    task_rows = "".join(task_row(task) for task in tasks)
    task_body = f"""<header class="page-hero"><p class="eyebrow">DiscoveryBench</p><h1>Benchmark tasks</h1><p class="lede">Every task declares what evidence is available, which actions are allowed, and how results are evaluated. The complete technical registry remains downloadable.</p></header><table class="matrix"><caption>DiscoveryBench exact benchmark tasks and their supporting evidence</caption><thead><tr><th>Task</th><th>Family</th><th>Compatible strategy</th><th>Supporting studies</th><th>Claims</th></tr></thead><tbody>{task_rows}</tbody></table>"""
    _write(
        output,
        "benchmark/tasks.html",
        _page(
            "Benchmark tasks",
            "DiscoveryBench golden task registry.",
            task_body,
            "benchmark/tasks.html",
        ),
    )

    protocol_rows = "".join(
        f'<tr><th scope="row">{html.escape(str(item["protocol_id"]))}</th><td>{html.escape(str(item["description"]))}</td><td>{len(item["capabilities"])}</td><td>{"enabled" if item["enabled"] else "disabled"}</td></tr>'
        for item in protocols
    )
    protocol_body = f"""<header class="page-hero"><p class="eyebrow">DiscoveryBench</p><h1>What each strategy can see and do</h1><p class="lede">Each strategy receives only its declared information and capabilities. External adapters are disabled, credential-free, and never executed in CI.</p></header><table class="matrix"><caption>Built-in strategy capability contracts</caption><thead><tr><th>Strategy</th><th>Definition</th><th>Capabilities</th><th>Status</th></tr></thead><tbody>{protocol_rows}</tbody></table>"""
    _write(
        output,
        "benchmark/protocols.html",
        _page(
            "Benchmark protocols",
            "DiscoveryBench protocol registry and capabilities.",
            protocol_body,
            "benchmark/protocols.html",
        ),
    )

    metric_rows = "".join(
        f'<tr><th scope="row">{html.escape(str(item["metric_id"]))}</th><td>{html.escape(str(item["definition"]))}</td><td>{html.escape(str(item["units"]))}</td><td>{html.escape(", ".join(item["required_observables"]))}</td></tr>'
        for item in metrics
    )
    metric_body = f"""<header class="page-hero"><p class="eyebrow">DiscoveryBench</p><h1>How performance is measured</h1><p class="lede">A measure is omitted when its required observables are absent. The benchmark preserves task vectors and family profiles; no composite score is active.</p></header><table class="matrix"><caption>Versioned benchmark metrics and required observables</caption><thead><tr><th>Metric</th><th>Definition</th><th>Units</th><th>Required observables</th></tr></thead><tbody>{metric_rows}</tbody></table>"""
    _write(
        output,
        "benchmark/metrics.html",
        _page(
            "Benchmark metrics",
            "Versioned DiscoveryBench metric registry.",
            metric_body,
            "benchmark/metrics.html",
        ),
    )

    result_rows = "".join(
        f'<tr data-task="{html.escape(str(row["task_id"]))}" data-protocol="{html.escape(str(row["protocol_id"]))}"><th scope="row">{html.escape(str(row["task_id"]))}</th><td>{html.escape(str(row["protocol_id"]))}</td><td><code>{html.escape(json.dumps(row["metrics"], sort_keys=True))}</code></td><td>{html.escape(", ".join(row["reference_claims"]))}</td></tr>'
        for row in results
    )
    results_body = f"""<header class="page-hero"><p class="eyebrow">DiscoveryBench</p><h1>Benchmark results</h1><p class="lede">All {len(results)} compatible pairs reproduce exact registered fixtures. The other {sum(not row["compatible"] for row in compatibility)} task/strategy pairs are explicit exclusions, not failures.</p></header><div class="summary-callout"><strong>{len(pareto)} rows</strong><span>remain in scoped task-level Pareto comparisons. Missing metrics are never imputed.</span></div><table class="matrix"><caption>Exact compatible task and strategy result vectors</caption><thead><tr><th>Task</th><th>Strategy</th><th>Metric vector</th><th>Claims</th></tr></thead><tbody>{result_rows}</tbody></table>"""
    _write(
        output,
        "benchmark/results.html",
        _page(
            "Benchmark results",
            "Exact DiscoveryBench result matrix and scoped Pareto report.",
            results_body,
            "benchmark/results.html",
        ),
    )

    attention_results = [
        row for row in results if 16 <= int(str(row["task_id"]).replace("DB-G", "")) <= 20
    ]
    attention_rows = "".join(
        f'<tr><th scope="row">{html.escape(str(row["task_id"]))}</th><td>{html.escape(str(row["protocol_id"]))}</td><td><code>{html.escape(json.dumps(row["metrics"], sort_keys=True))}</code></td></tr>'
        for row in attention_results
    )
    attention_body = f"""<p class="eyebrow"><a href="../benchmark.html">DiscoveryBench</a> / Selective attention</p><h1>Attention extension</h1><p class="lede">Five exact DD-012--DD-014 tasks expose private-only, public-only, designated-reader, voluntary-equilibrium, audience-optimal, and conditional-policy comparisons. Version 1 remains the CLI default.</p><table class="matrix"><caption>DiscoveryBench v2 selective-attention rows</caption><thead><tr><th>Task</th><th>Protocol</th><th>Exact metric vector</th></tr></thead><tbody>{attention_rows}</tbody></table><p><a href="../labs/benchmark.html">Filter all benchmark rows</a> · <a href="../data/benchmark/results.json">Download v2 results</a></p>"""
    _write(
        output,
        "benchmark/attention.html",
        _page(
            "Benchmark attention extension",
            "Exact DiscoveryBench v2 selective-attention tasks and results.",
            attention_body,
            "benchmark/attention.html",
        ),
    )

    options = "".join(
        f'<option value="{html.escape(str(task["task_id"]))}">{html.escape(str(task["task_id"]))} — {html.escape(str(task["task_family"]))}</option>'
        for task in tasks
    )
    lab_body = f"""<header class="page-hero"><p class="eyebrow">DiscoveryBench interactive explainer</p><h1>Benchmark Lab</h1><p class="lede">Filter exact benchmark rows and inspect provenance. There are no submissions, accounts, external calls, or leaderboard.</p></header><section class="lab" data-benchmark-lab><label for="benchmark-task">Task</label><select id="benchmark-task"><option value="all">All tasks</option>{options}</select><p id="benchmark-status" class="callout" aria-live="polite">Showing all {len(results)} exact compatible rows.</p></section><noscript><p class="callout">JavaScript is off. Every exact row remains visible in the table.</p></noscript><table class="matrix"><caption>Filterable exact benchmark result vectors</caption><thead><tr><th>Task</th><th>Strategy</th><th>Metric vector</th><th>Provenance</th></tr></thead><tbody>{result_rows}</tbody></table><p><a href="../data/benchmark/compatibility.json">Download compatibility JSON</a> · <a href="../data/benchmark/results.json">Download result JSON</a></p>"""
    lab_body = (
        lab_body.replace(
            '<section class="lab" data-benchmark-lab>',
            '<section class="lab" data-benchmark-lab><fieldset class="lab-controls"><legend>Choose a benchmark task</legend>',
            1,
        )
        .replace(
            '<p id="benchmark-status"',
            '</fieldset><div class="lab-actions"><button type="button" class="filter-button" data-table-lab-reset>Reset</button><a href="../data/benchmark/results.json">Download data</a></div><p id="benchmark-status"',
            1,
        )
        .replace(
            "</section><noscript>",
            '<div class="metric-grid compact"><article class="metric-card"><span>Visible result rows</span><strong data-benchmark-output="count">—</strong></article><article class="metric-card"><span>Selected task</span><strong data-benchmark-output="task">All</strong></article><article class="metric-card"><span>Example strategy</span><strong data-benchmark-output="strategy">—</strong></article><article class="metric-card"><span>Exact metric vector</span><strong data-benchmark-output="vector">—</strong></article></div><p class="takeaway">Compatibility comes before comparison: the Lab shows only registered task–strategy pairs and does not construct a universal score.</p></section><noscript>',
            1,
        )
        .replace(
            '<table class="matrix"><caption>Filterable exact benchmark result vectors',
            '<details class="technical-details complete-data"><summary>Complete exact result table</summary><table class="matrix"><caption>Filterable exact benchmark result vectors',
            1,
        )
        .replace(
            '</tbody></table><p><a href="../data/benchmark/compatibility.json">',
            '</tbody></table></details><p><a href="../data/benchmark/compatibility.json">',
            1,
        )
    )
    _write(
        output,
        "labs/benchmark.html",
        _page(
            "Benchmark Lab",
            "Read-only exact DiscoveryBench explorer.",
            lab_body,
            "labs/benchmark.html",
        ),
    )

    data = {
        "tasks.json": {"schema_version": schema_number, "run_id": run_id, "tasks": tasks},
        "protocols.json": {
            "schema_version": schema_number,
            "run_id": run_id,
            "protocols": protocols,
        },
        "metrics.json": {"schema_version": schema_number, "run_id": run_id, "metrics": metrics},
        "compatibility.json": {
            "schema_version": schema_number,
            "run_id": run_id,
            "compatibility": compatibility,
        },
        "results.json": {
            "schema_version": schema_number,
            "run_id": run_id,
            "results": results,
            "pareto": pareto,
        },
        "summary.json": {
            "schema_version": schema_number,
            "run_id": run_id,
            "summary": summary,
        },
    }
    for name, value in data.items():
        _write(output, f"data/benchmark/{name}", json.dumps(value, indent=2, sort_keys=True) + "\n")
    (output / "downloads").mkdir(exist_ok=True)
    for version in ("v1", "v2", "v3"):
        schema = root / f"studies/DD-010-discoverybench/schemas/task-{version}.schema.json"
        shutil.copy2(schema, output / f"downloads/discoverybench-task-{version}.schema.json")
    return {"run_id": run_id, "summary": summary}


def _experiment_pages(root: Path, output: Path) -> dict[str, object]:
    run = _latest_passing_study_run(root, "DD-011")
    source = run / "outputs"
    summary = json.loads((source / "synthetic-summary.json").read_text())
    design = json.loads((source / "design-registry.json").read_text())
    treatments = json.loads((source / "treatment-matrix.json").read_text())
    hypotheses = json.loads((source / "hypotheses.json").read_text())
    power = json.loads((source / "power-table.json").read_text())
    calibration = json.loads((source / "calibration-report.json").read_text())
    manifest = json.loads((run / "manifest.json").read_text())
    run_id = str(manifest["run_id"])
    experiment_version = str(summary.get("experiment_version", "v1"))
    schema_number = int(experiment_version.removeprefix("v"))
    notice = html.escape(str(design["notice"]))
    warning = f'<aside class="callout" aria-label="No human data warning"><strong>Synthetic package only.</strong> {notice}</aside>'
    downloads = f'<a href="downloads/dd011-preregistration-template.md">preregistration template</a> · <a href="downloads/dd011-participant-instructions.md">participant instructions</a> · <a href="downloads/dd011-researcher-protocol.md">researcher protocol</a> · <a href="downloads/dd011-data-dictionary.md">data dictionary</a> · <a href="downloads/dd011-randomization.md">randomization</a> · <a href="downloads/dd011-design-{experiment_version}.schema.json">design schema</a>'
    version_flag = "" if experiment_version == "v1" else f" --version {experiment_version}"
    make_target = {
        "v1": "dd011-experiment",
        "v2": "dd011-attention",
        "v3": "dd011-threshold-dynamic",
    }[experiment_version]
    claim_id = {"v1": "DD-C-0056", "v2": "DD-C-0070", "v3": "DD-C-0088"}[experiment_version]
    program_v4_card = (
        '<article class="card"><h3><a href="experiment-kit/threshold-dynamic.html">'
        "Threshold and dynamic extension</a></h3><p>Inspect the eight Program V4 "
        "treatments and six appended synthetic contrasts.</p></article>"
        if experiment_version == "v3"
        else ""
    )
    overview = f"""<header class="page-hero"><p class="eyebrow">DD-011 experiment design kit {html.escape(experiment_version)}</p><h1>Plan a discovery experiment</h1><p class="lede">A read-only synthetic package for a proposed experiment on acquisition, disclosure, selective attention, threshold allocation, dynamics, and rewards.</p></header>{warning}<div class="metric-grid"><article class="metric-card"><span>Treatment cells</span><strong>{summary["treatment_cells"]}</strong></article><article class="metric-card"><span>Questions</span><strong>{summary["hypotheses"]}</strong></article><article class="metric-card"><span>Synthetic power rows</span><strong>{summary["power_rows"]}</strong></article></div><section class="content-section"><h2>Explore the proposed experiment</h2><div class="card-grid resource-grid"><article class="card"><h3><a href="experiment-kit/hypotheses.html">What the experiment would test</a></h3><p>Review the frozen questions, outcomes, and estimands.</p></article><article class="card"><h3><a href="experiment-kit/design.html">How participants would be assigned</a></h3><p>Inspect the treatment matrix and bounded alternatives.</p></article><article class="card"><h3><a href="experiment-kit/attention.html">Selective-attention extension</a></h3><p>Inspect the nine attention treatments and six appended hypotheses.</p></article>{program_v4_card}<article class="card"><h3><a href="experiment-kit/power.html">Synthetic power estimates</a></h3><p>See scenario-conditional estimates, MDEs, and retained failures.</p></article><article class="card"><h3><a href="labs/experiment-design.html">Experiment-design Lab</a></h3><p>Filter the complete precomputed power table.</p></article></div></section><section class="content-section prose"><h2>Materials and safeguards</h2><p>{downloads}</p><p>This package is not preregistered and no live assignment or data collection service exists.</p><details class="technical-details"><summary>Technical details</summary><p><code>make {make_target}</code><br><code>distributed-discovery experiment{version_flag} verify {html.escape(run_id)}</code></p><p>Claim <a href="claims.html#{claim_id}">{claim_id}</a> · reproducible run <a href="evidence.html">{html.escape(run_id)}</a>.</p></details></section>"""
    _write(
        output,
        "experiment-kit.html",
        _page(
            "Experiment kit",
            "Synthetic DD-011 experimental design and conditional power package.",
            overview,
            "experiment-kit.html",
        ),
    )

    hypothesis_rows = "".join(
        f'<tr><th scope="row">{html.escape(str(row["hypothesis_id"]))}</th><td>{html.escape(str(row["question"]))}</td><td>{html.escape(str(row["treatment_cell"]))} − {html.escape(str(row["control_cell"]))}</td><td>{html.escape(str(row["outcome"]))}</td><td>{html.escape(str(row["estimand"]))}</td><td>{html.escape(str(row["role"]))}</td></tr>'
        for row in hypotheses
    )
    hypothesis_body = f"""<header class="page-hero"><p class="eyebrow">DD-011 experiment design kit</p><h1>What the experiment would test</h1><p class="lede">Questions, directions, models, and multiplicity families were fixed before the primary synthetic run.</p></header>{warning}<table class="matrix"><caption>Registered DD-011 hypotheses and ITT contrasts</caption><thead><tr><th>ID</th><th>Question</th><th>Contrast</th><th>Outcome</th><th>Estimand</th><th>Role</th></tr></thead><tbody>{hypothesis_rows}</tbody></table><p><a href="../data/experiment/hypotheses.json">Download hypotheses JSON</a> · <a href="../data/experiment/outcomes.json">Download outcome definitions</a></p>"""
    _write(
        output,
        "experiment-kit/hypotheses.html",
        _page(
            "Experiment hypotheses",
            "Frozen DD-011 hypotheses, outcomes, and estimands.",
            hypothesis_body,
            "experiment-kit/hypotheses.html",
        ),
    )

    treatment_rows = "".join(
        f'<tr><th scope="row">{html.escape(str(row["cell_id"]))}</th><td>{html.escape(str(row["acquisition"]))}</td><td>{html.escape(str(row["attribution"]))}</td><td>{html.escape(str(row["disclosure"]))}</td><td>{html.escape(str(row["timing"]))}</td><td>{html.escape(str(row["reward"]))}</td></tr>'
        for row in treatments
    )
    alternative_rows = "".join(
        f'<tr><th scope="row">{html.escape(str(row["design_id"]))}</th><td>{row["cells"]}</td><td>{html.escape(str(row["estimand_coverage"]))}</td><td>{html.escape(str(row["aliasing"]))}</td><td>{"selected" if row["selected"] else html.escape(str(row["reason"]))}</td></tr>'
        for row in design["alternatives"]
    )
    design_body = f"""<header class="page-hero"><p class="eyebrow">DD-011 experiment design kit</p><h1>How participants would be assigned</h1><p class="lede">The proposed {len(treatments)}-cell synthetic matrix covers all {len(hypotheses)} registered contrasts. Unregistered higher-order interactions remain aliased.</p></header>{warning}<table class="matrix"><caption>Comparison of bounded design alternatives</caption><thead><tr><th>Design</th><th>Cells</th><th>Estimand coverage</th><th>Aliasing</th><th>Decision</th></tr></thead><tbody>{alternative_rows}</tbody></table><table class="matrix"><caption>Selected treatment cells</caption><thead><tr><th>Cell</th><th>Acquisition</th><th>Attribution</th><th>Disclosure</th><th>Timing</th><th>Reward</th></tr></thead><tbody>{treatment_rows}</tbody></table><p><a href="../data/experiment/treatments.json">Download treatment JSON</a> · <a href="../data/experiment/randomization.json">Download synthetic assignment manifest</a></p>"""
    _write(
        output,
        "experiment-kit/design.html",
        _page(
            "Experiment design",
            "DD-011 treatment matrix and alternative comparison.",
            design_body,
            "experiment-kit/design.html",
        ),
    )

    attention_treatments = [row for row in treatments if 20 <= int(str(row["cell_id"])[1:3]) <= 28]
    attention_hypotheses = [
        row for row in hypotheses if 9 <= int(str(row["hypothesis_id"])[1:]) <= 14
    ]
    attention_treatment_rows = "".join(
        f'<tr><th scope="row">{html.escape(str(row["cell_id"]))}</th><td>{html.escape(str(row["public_access"]))}</td><td>{html.escape(str(row["public_precision"]))}</td><td>{html.escape(str(row["attention_institution"]))}</td><td>{html.escape(str(row["policy_recommendation"]))}</td><td>{html.escape(str(row["reward"]))}</td></tr>'
        for row in attention_treatments
    )
    attention_hypothesis_rows = "".join(
        f'<tr><th scope="row">{html.escape(str(row["hypothesis_id"]))}</th><td>{html.escape(str(row["question"]))}</td><td>{html.escape(str(row["outcome"]))}</td><td>{html.escape(str(row["multiplicity_family"]))}</td></tr>'
        for row in attention_hypotheses
    )
    attention_body = f"""<header class="page-hero"><p class="eyebrow">DD-011 v2</p><h1>Selective-attention experiment extension</h1><p class="lede">Nine synthetic treatments separate public-clue audience, precision, recommendation, license, reward, and conditional policy. Six appended hypotheses define their contrasts and estimands.</p></header>{warning}<table class="matrix"><caption>Selective-attention treatment cells</caption><thead><tr><th>Cell</th><th>Public access</th><th>Precision</th><th>Institution</th><th>Policy recommendation</th><th>Reward</th></tr></thead><tbody>{attention_treatment_rows}</tbody></table><table class="matrix"><caption>Selective-attention hypotheses</caption><thead><tr><th>ID</th><th>Question</th><th>Outcome</th><th>Multiplicity family</th></tr></thead><tbody>{attention_hypothesis_rows}</tbody></table><p><a href="../data/experiment/design.json">Download v2 design</a> · <a href="../data/experiment/power.json">Download synthetic power rows</a></p>"""
    _write(
        output,
        "experiment-kit/attention.html",
        _page(
            "Selective-attention experiment extension",
            "Synthetic-only DD-011 v2 attention treatments and hypotheses.",
            attention_body,
            "experiment-kit/attention.html",
        ),
    )

    if experiment_version == "v3":
        program_v4_treatments = [row for row in treatments if int(str(row["cell_id"])[1:3]) >= 29]
        program_v4_hypotheses = [
            row for row in hypotheses if int(str(row["hypothesis_id"])[1:]) >= 15
        ]
        program_v4_treatment_rows = "".join(
            f'<tr><th scope="row">{html.escape(str(row["cell_id"]))}</th><td>{html.escape(str(row["team_threshold"]))}</td><td>{html.escape(str(row["portfolio_rule"]))}</td><td>{html.escape(str(row["history_visibility"]))}</td><td>{html.escape(str(row["action_horizon"]))}</td></tr>'
            for row in program_v4_treatments
        )
        program_v4_hypothesis_rows = "".join(
            f'<tr><th scope="row">{html.escape(str(row["hypothesis_id"]))}</th><td>{html.escape(str(row["question"]))}</td><td>{html.escape(str(row["outcome"]))}</td><td>{html.escape(str(row["multiplicity_family"]))}</td></tr>'
            for row in program_v4_hypotheses
        )
        program_v4_body = f"""<header class="page-hero"><p class="eyebrow">DD-011 v3</p><h1>Threshold and dynamic experiment extension</h1><p class="lede">Eight synthetic treatments separate threshold portfolios, history visibility, and fixed-versus-stopping action horizons. Six appended hypotheses are model-derived design inputs, not behavioral findings.</p></header>{warning}<table class="matrix"><caption>Threshold and dynamic treatment cells</caption><thead><tr><th>Cell</th><th>Threshold</th><th>Portfolio rule</th><th>History</th><th>Horizon</th></tr></thead><tbody>{program_v4_treatment_rows}</tbody></table><table class="matrix"><caption>Program V4 synthetic hypotheses</caption><thead><tr><th>ID</th><th>Question</th><th>Outcome</th><th>Multiplicity family</th></tr></thead><tbody>{program_v4_hypothesis_rows}</tbody></table><p><a href="../data/experiment/design.json">Download v3 design</a> · <a href="../data/experiment/calibration.json">Download all retained calibration failures</a></p>"""
        _write(
            output,
            "experiment-kit/threshold-dynamic.html",
            _page(
                "Threshold and dynamic experiment extension",
                "Synthetic-only DD-011 v3 threshold and dynamic treatments.",
                program_v4_body,
                "experiment-kit/threshold-dynamic.html",
            ),
        )

    power_rows = "".join(
        f'<tr data-power-scenario="{html.escape(str(row["scenario_id"]))}" data-power-hypothesis="{html.escape(str(row["hypothesis_id"]))}"><th scope="row">{html.escape(str(row["scenario_id"]))}</th><td>{html.escape(str(row["hypothesis_id"]))}</td><td>{row["sample_size"]}</td><td>{html.escape(str(row["assumed_effect"]))}</td><td>{html.escape(str(row["power"]))} [{html.escape(str(row["power_ci_low"]))}, {html.escape(str(row["power_ci_high"]))}]</td><td>{html.escape(str(row["minimum_detectable_effect"]))}</td></tr>'
        for row in power
    )
    power_body = f"""<header class="page-hero"><p class="eyebrow">DD-011 experiment design kit</p><h1>Synthetic power estimates</h1><p class="lede">Every value is a Monte Carlo estimate under a declared response scenario. The {calibration["failure_count"]} failures among {calibration["evaluated_rows"]} rows at sample sizes 640 or more are retained.</p></header>{warning}<table class="matrix"><caption>Full registered synthetic power and minimum-detectable-effect grid</caption><thead><tr><th>Scenario</th><th>Hypothesis</th><th>Total N</th><th>Assumed effect</th><th>Power (95% Monte Carlo interval)</th><th>MDE</th></tr></thead><tbody>{power_rows}</tbody></table><p><a href="../data/experiment/power.json">Download power JSON</a> · <a href="../data/experiment/calibration.json">Download retained calibration failures</a></p>"""
    _write(
        output,
        "experiment-kit/power.html",
        _page(
            "Synthetic power",
            "Conditional DD-011 synthetic power, MDEs, and retained failures.",
            power_body,
            "experiment-kit/power.html",
        ),
    )

    options = "".join(
        f'<option value="{html.escape(str(row["scenario_id"]))}">{html.escape(str(row["scenario_id"]))} — {html.escape(str(row["label"]))}</option>'
        for row in design["response_scenarios"]
    )
    lab_body = f"""<header class="page-hero"><p class="eyebrow">DD-011 interactive explainer</p><h1>Experiment-design Lab</h1><p class="lede">Filter the precomputed power grid. This read-only control performs no assignment, recruitment, submission, or external call.</p></header>{warning}<section class="lab" data-experiment-lab><label for="experiment-scenario">Response scenario</label><select id="experiment-scenario"><option value="all">All scenarios</option>{options}</select><p id="experiment-status" class="callout" aria-live="polite">Showing all {len(power)} synthetic power rows.</p></section><noscript><p class="callout">JavaScript is off. Every power row remains visible below.</p></noscript><table class="matrix"><caption>Filterable synthetic power and MDE grid</caption><thead><tr><th>Scenario</th><th>Hypothesis</th><th>Total N</th><th>Assumed effect</th><th>Power (95% Monte Carlo interval)</th><th>MDE</th></tr></thead><tbody>{power_rows}</tbody></table><p><a href="../data/experiment/power.json">Download power JSON</a> · <a href="../data/experiment/design.json">Download design JSON</a></p>"""
    lab_body = (
        lab_body.replace(
            '<section class="lab" data-experiment-lab>',
            '<section class="lab" data-experiment-lab><fieldset class="lab-controls"><legend>Choose a synthetic response scenario</legend>',
            1,
        )
        .replace(
            '<p id="experiment-status"',
            '</fieldset><div class="lab-actions"><button type="button" class="filter-button" data-table-lab-reset>Reset</button><a href="../data/experiment/power.json">Download data</a></div><p id="experiment-status"',
            1,
        )
        .replace(
            "</section><noscript>",
            '<div class="metric-grid compact"><article class="metric-card"><span>Visible power rows</span><strong data-experiment-output="count">—</strong></article><article class="metric-card"><span>Scenario</span><strong data-experiment-output="scenario">All</strong></article><article class="metric-card"><span>Example power interval</span><strong data-experiment-output="power">—</strong></article><article class="metric-card"><span>Example MDE</span><strong data-experiment-output="mde">—</strong></article></div><p class="takeaway">These are scenario-conditional synthetic estimates, not observed effects or deployment evidence.</p></section><noscript>',
            1,
        )
        .replace(
            '<table class="matrix"><caption>Filterable synthetic power and MDE grid',
            '<details class="technical-details complete-data"><summary>Complete synthetic power table</summary><table class="matrix"><caption>Filterable synthetic power and MDE grid',
            1,
        )
        .replace(
            '</tbody></table><p><a href="../data/experiment/power.json">',
            '</tbody></table></details><p><a href="../data/experiment/power.json">',
            1,
        )
    )
    _write(
        output,
        "labs/experiment-design.html",
        _page(
            "Experiment-design Lab",
            "Read-only DD-011 synthetic power explorer.",
            lab_body,
            "labs/experiment-design.html",
        ),
    )

    data = {
        "summary.json": {
            "schema_version": schema_number,
            "run_id": run_id,
            "summary": summary,
            "notice": design["notice"],
        },
        "design.json": {"schema_version": schema_number, "run_id": run_id, "design": design},
        "hypotheses.json": {
            "schema_version": schema_number,
            "run_id": run_id,
            "hypotheses": hypotheses,
        },
        "outcomes.json": {
            "schema_version": schema_number,
            "run_id": run_id,
            "outcomes": design["outcomes"],
        },
        "treatments.json": {
            "schema_version": schema_number,
            "run_id": run_id,
            "treatments": treatments,
        },
        "power.json": {"schema_version": schema_number, "run_id": run_id, "power": power},
        "calibration.json": {
            "schema_version": schema_number,
            "run_id": run_id,
            "calibration": calibration,
        },
        "randomization.json": {
            "schema_version": schema_number,
            "run_id": run_id,
            "randomization": json.loads((source / "randomization-manifest.json").read_text()),
        },
        "synthetic-sample.json": {
            "schema_version": schema_number,
            "run_id": run_id,
            "rows": json.loads((source / "synthetic-sample.json").read_text()),
        },
        "exact-checks.json": {
            "schema_version": schema_number,
            "run_id": run_id,
            "checks": json.loads((source / "exact-model-checks.json").read_text()),
        },
    }
    for name, value in data.items():
        _write(
            output, f"data/experiment/{name}", json.dumps(value, indent=2, sort_keys=True) + "\n"
        )
    downloads_dir = output / "downloads"
    downloads_dir.mkdir(exist_ok=True)
    materials = root / "studies/DD-011-experimental-design/materials"
    for source_name, public_name in {
        "preregistration-template.md": "dd011-preregistration-template.md",
        "participant-instructions.md": "dd011-participant-instructions.md",
        "researcher-protocol.md": "dd011-researcher-protocol.md",
        "data-dictionary.md": "dd011-data-dictionary.md",
        "comprehension-checks.md": "dd011-comprehension-checks.md",
        "treatment-screens.md": "dd011-treatment-screens.md",
        "task-examples.md": "dd011-task-examples.md",
        "analysis-plan.md": "dd011-analysis-plan.md",
        "NO-HUMAN-DATA.md": "dd011-no-human-data.md",
        "randomization.md": "dd011-randomization.md",
    }.items():
        shutil.copy2(materials / source_name, downloads_dir / public_name)
    for version in ("v1", "v2", "v3"):
        shutil.copy2(
            root / f"studies/DD-011-experimental-design/schemas/design-{version}.schema.json",
            downloads_dir / f"dd011-design-{version}.schema.json",
        )
    return {"run_id": run_id, "summary": summary}


def _attention_pages(root: Path, output: Path) -> dict[str, object]:
    run = root / "results/verified" / DD012_RUN
    source = run / "outputs"
    summary = json.loads((source / "summary.json").read_text(encoding="utf-8"))
    cells = json.loads((source / "attention-census.json").read_text(encoding="utf-8"))
    phase_map = json.loads((source / "phase-map.json").read_text(encoding="utf-8"))
    rewards = json.loads((source / "reward-registry.json").read_text(encoding="utf-8"))
    agents = sorted({int(cell["agents"]) for cell in cells})
    accuracies = sorted(
        {str(cell["private_accuracy"]) for cell in cells}, key=lambda value: Fraction(value)
    )
    reward_ids = [str(row["rule_id"]) for row in rewards]
    agent_options = "".join(f'<option value="{n}">{n}</option>' for n in agents)
    accuracy_options = "".join(
        f'<option value="{html.escape(value)}">{html.escape(value)}</option>'
        for value in accuracies
    )
    attender_options = "".join(
        f'<option value="{value}">{value}</option>' for value in range(max(agents) + 1)
    )
    reward_options = "".join(
        f'<option value="{html.escape(value)}">{html.escape(value)}</option>'
        for value in reward_ids
    )
    rows: list[str] = []
    for cell in cells:
        profiles = cell["profiles"]
        first_use_gain = Fraction(str(profiles[1]["discovery"])) - Fraction(
            str(profiles[0]["discovery"])
        )
        for profile in profiles:
            attenders = int(profile["attenders"])
            duplicate_loss = max(
                Fraction(0),
                Fraction(str(profiles[1]["discovery"])) - Fraction(str(profile["discovery"])),
            )
            for reward_id in reward_ids:
                if reward_id == "public-reader-license":
                    payoff_attend = "—"
                    payoff_ignore = "—"
                    budget = profile["discovery"]
                    equilibrium_counts = cell["reward_equilibria"][reward_id][
                        "binding_implemented_counts"
                    ]
                    equilibrium = (
                        "binding implementation" if attenders in equilibrium_counts else "no"
                    )
                else:
                    reward = profile["rewards"][reward_id]
                    payoff_attend = reward["attending"] if reward["attending"] is not None else "—"
                    payoff_ignore = reward["ignoring"] if reward["ignoring"] is not None else "—"
                    budget = reward["budget"]
                    equilibrium = (
                        "weak"
                        if attenders in cell["reward_equilibria"][reward_id]["weak"]
                        else "no"
                    )
                rows.append(
                    '<tr data-attention-row data-n="{n}" data-p="{p}" data-q="{q}" data-k="{k}" data-reward="{reward}"><th scope="row">{n}</th><td>{p}</td><td>{q}</td><td>{k}</td><td>{reward}</td><td>{discovery}</td><td>{attend}</td><td>{ignore}</td><td>{optimum}</td><td>{equilibrium}</td><td>{wedge}</td><td>{first}</td><td>{duplicate}</td><td>{budget}</td></tr>'.format(
                        n=cell["agents"],
                        p=html.escape(str(cell["private_accuracy"])),
                        q=html.escape(str(cell["shared_accuracy"])),
                        k=attenders,
                        reward=html.escape(reward_id),
                        discovery=html.escape(str(profile["discovery"])),
                        attend=html.escape(str(payoff_attend)),
                        ignore=html.escape(str(payoff_ignore)),
                        optimum="yes" if attenders in cell["social_optima"] else "no",
                        equilibrium=html.escape(equilibrium),
                        wedge=html.escape(
                            str(profile["attention_wedge"])
                            if profile["attention_wedge"] is not None
                            else "—"
                        ),
                        first=html.escape(str(first_use_gain)),
                        duplicate=html.escape(str(duplicate_loss)),
                        budget=html.escape(str(budget)),
                    )
                )
    table_rows = "".join(rows)
    representative_match = re.search(
        r'(<tr data-attention-row data-n="4" data-p="1/2" data-q="3/4" data-k="1" data-reward="equal-split">.*?</tr>)',
        table_rows,
    )
    if representative_match is None:
        raise RuntimeError("missing representative DD-012 attention fallback row")
    table_rows = representative_match.group(1)
    body = f"""<header class="page-hero"><p class="eyebrow">DD-012 interactive explainer</p><h1>Attention Lab</h1><p class="lede">Explore the exact access-gated follow-public/follow-private model. An ignoring role is not given the public clue; the Lab does not assume an informed person can forget.</p></header><div class="metric-grid"><article class="metric-card"><span>Exact cells</span><strong>{summary["grid_cells"]}</strong></article><article class="metric-card"><span>Attention profiles</span><strong>{summary["profiles"]}</strong></article><article class="metric-card"><span>Reward rules</span><strong>{summary["reward_rules"]}</strong></article></div><section class="lab" data-attention-lab><label for="attention-n">Team size</label><select id="attention-n">{agent_options}</select><label for="attention-p">Private accuracy</label><select id="attention-p">{accuracy_options}</select><label for="attention-q">Public accuracy</label><select id="attention-q">{accuracy_options}</select><label for="attention-k">Number of attenders</label><select id="attention-k">{attender_options}</select><label for="attention-reward">Reward rule</label><select id="attention-reward">{reward_options}</select><p id="attention-status" class="callout" aria-live="polite">Select a registered exact attention profile.</p></section><noscript><p class="callout">JavaScript is off. All {len(rows)} exact profile-and-reward rows remain visible in the complete table.</p></noscript><section class="content-section"><h2>Exact attention profiles</h2><table class="matrix"><caption>Discovery, reward payoffs, social optimum, equilibrium, equal-split attention wedge, first-use gain, and duplicate-use loss</caption><thead><tr><th>N</th><th>p</th><th>q</th><th>Attenders</th><th>Reward</th><th>Discovery</th><th>Attending payoff</th><th>Ignoring payoff</th><th>Social optimum</th><th>Equilibrium</th><th>Equal-split attention wedge</th><th>First-use gain</th><th>Duplicate-use loss</th><th>Transfer budget</th></tr></thead><tbody>{table_rows}</tbody></table></section><details class="technical-details"><summary>Technical details</summary><p><a href="../claims.html#DD-C-0059">DD-C-0059</a> · <a href="../claims.html#DD-C-0060">DD-C-0060</a> · <a href="../claims.html#DD-C-0061">DD-C-0061</a> · reproducible run <a href="{REPOSITORY_URL}/blob/main/results/verified/{DD012_RUN}/manifest.json">{DD012_RUN}</a></p></details><p><a href="../research/dd-012.html">Study page</a> · <a href="../data/attention/census.json">Download attention census</a> · <a href="../data/attention/rewards.json">Download reward registry</a> · <a href="../data/attention/phase-map.json">Download phase map</a></p>"""
    body = (
        body.replace(
            '<section class="lab" data-attention-lab>',
            '<section class="lab" data-attention-lab><fieldset class="lab-controls"><legend>Choose a registered attention profile</legend>',
            1,
        )
        .replace(
            '<p id="attention-status"',
            '</fieldset><div class="lab-actions"><button type="button" class="filter-button" data-table-lab-reset>Reset</button><a href="../data/attention/census.json">Download data</a></div><p id="attention-status"',
            1,
        )
        .replace(
            "</section><noscript>",
            '<div class="metric-grid compact"><article class="metric-card planner"><span>Discovery</span><strong data-attention-output="discovery">—</strong></article><article class="metric-card"><span>Social optimum</span><strong data-attention-output="optimum">—</strong></article><article class="metric-card"><span>Equilibrium</span><strong data-attention-output="equilibrium">—</strong></article><article class="metric-card"><span>Attention wedge</span><strong data-attention-output="wedge">—</strong></article></div><section class="lab-visual"><h2>Selected attention profile</h2><p class="visual-summary">The comparison keeps discovery, private incentives, and social optimality distinct.</p><div class="comparison-readout"><div><span>Attending payoff</span><strong data-attention-output="attending">—</strong></div><div><span>Ignoring payoff</span><strong data-attention-output="ignoring">—</strong></div></div></section><p class="takeaway" data-attention-takeaway>Select a registered profile to compare attention incentives.</p></section><noscript>',
            1,
        )
    )
    body = body.replace(
        f"All {len(rows)} exact profile-and-reward rows remain visible in the complete table.",
        "One representative exact row remains visible below; the complete census is available as a data download.",
    )
    body = body.replace(
        '<section class="content-section"><h2>Exact attention profiles</h2>',
        '<details class="technical-details complete-data"><summary>Complete exact attention table</summary><section class="content-section"><h2>Exact attention profiles</h2>',
        1,
    ).replace(
        '<details class="technical-details"><summary>Technical details</summary>',
        '</details><details class="technical-details"><summary>Technical details</summary>',
        1,
    )
    _write(
        output,
        "labs/attention.html",
        _page(
            "Attention Lab",
            "Read-only exact DD-012 attention, payoff, and reward-rule explorer.",
            body,
            "labs/attention.html",
        ),
    )
    data = {
        "summary.json": {"schema_version": 1, "run_id": DD012_RUN, "summary": summary},
        "census.json": {"schema_version": 1, "run_id": DD012_RUN, "cells": cells},
        "phase-map.json": {"schema_version": 1, "run_id": DD012_RUN, "cells": phase_map},
        "rewards.json": {"schema_version": 1, "run_id": DD012_RUN, "rewards": rewards},
    }
    for name, value in data.items():
        _write(output, f"data/attention/{name}", json.dumps(value, indent=2, sort_keys=True) + "\n")
    return {"run_id": DD012_RUN, "summary": summary}


def _audience_pages(root: Path, output: Path) -> dict[str, object]:
    run = root / "results/verified" / DD013_RUN
    source = run / "outputs"
    summary = json.loads((source / "summary.json").read_text(encoding="utf-8"))
    cells = json.loads((source / "audience-frontier.json").read_text(encoding="utf-8"))
    garbling = json.loads((source / "garbling-frontier.json").read_text(encoding="utf-8"))
    mechanisms = json.loads((source / "mechanism-results.json").read_text(encoding="utf-8"))
    institutions = json.loads((source / "institution-registry.json").read_text(encoding="utf-8"))
    agents = sorted({int(cell["agents"]) for cell in cells})
    accuracies = sorted(
        {str(cell["private_accuracy"]) for cell in cells}, key=lambda value: Fraction(value)
    )
    agent_options = "".join(f'<option value="{n}">{n}</option>' for n in agents)
    accuracy_options = "".join(
        f'<option value="{html.escape(value)}">{html.escape(value)}</option>'
        for value in accuracies
    )
    audience_options = "".join(
        f'<option value="{value}">{value}</option>' for value in range(max(agents) + 1)
    )
    binding_rows = "".join(
        '<tr data-audience-row data-n="{n}" data-p="{p}" data-q="{q}" data-m="{m}"><th scope="row">{n}</th><td>{p}</td><td>{q}</td><td>{m}</td><td>{discovery}</td><td>{quality}</td><td>{distinct}</td><td>{channels}</td><td>{optimal}</td></tr>'.format(
            n=cell["agents"],
            p=html.escape(str(cell["private_accuracy"])),
            q=html.escape(str(cell["shared_accuracy"])),
            m=row["audience"],
            discovery=html.escape(str(row["discovery"])),
            quality=html.escape(str(row["action_quality"])),
            distinct=html.escape(str(row["expected_distinct_actions"])),
            channels=row["effective_action_channels"],
            optimal="yes" if row["audience"] in cell["binding_optima"] else "no",
        )
        for cell in cells
        for row in cell["binding_audiences"]
    )
    garbling_rows = "".join(
        '<tr data-garbling-row data-n="{n}" data-p="{p}" data-q="{q}" data-g="{g}" data-m="{m}"><th scope="row">{n}</th><td>{p}</td><td>{q}</td><td>{g}</td><td>{m}</td><td>{discovery}</td><td>{dominated}</td></tr>'.format(
            n=cell["agents"],
            p=html.escape(str(cell["private_accuracy"])),
            q=html.escape(str(cell["shared_accuracy"])),
            g=html.escape(str(row["delivered_accuracy"])),
            m=row["audience"],
            discovery=html.escape(str(row["discovery"])),
            dominated="strictly" if row["strictly_dominated_by_binding_optimum"] else "ties",
        )
        for cell in garbling
        for row in cell["rows"]
    )
    voluntary_rows = "".join(
        '<tr data-voluntary-row data-n="{n}" data-p="{p}" data-q="{q}" data-m="{m}"><th scope="row">{n}</th><td>{p}</td><td>{q}</td><td>{m}</td><td>{readers}</td><td>{discovery}</td><td>{equilibrium}</td><td>{optimum}</td><td>{implementation}</td></tr>'.format(
            n=cell["agents"],
            p=html.escape(str(cell["private_accuracy"])),
            q=html.escape(str(cell["shared_accuracy"])),
            m=audience["audience"],
            readers=profile["readers"],
            discovery=html.escape(str(profile["discovery"])),
            equilibrium=(
                "strict"
                if profile["strict_equilibrium"]
                else "weak"
                if profile["weak_equilibrium"]
                else "no"
            ),
            optimum=html.escape(", ".join(str(value) for value in cell["binding_optima"])),
            implementation=(
                "binding use implemented"
                if audience["binding_use_implemented"]
                else "implementation gap"
            ),
        )
        for cell in cells
        for audience in cell["voluntary_audiences"]
        for profile in audience["profiles"]
    )
    mechanism_ids = (
        "binding_exclusive_delivery",
        "public_equal_split_nonbinding",
        "public_universal_pooling",
    )
    mechanism_options = "".join(
        f'<option value="{value}">{html.escape(value.replace("_", " "))}</option>'
        for value in mechanism_ids
    )
    mechanism_rows: list[str] = []
    for cell in mechanisms:
        for mechanism_id in mechanism_ids:
            result = cell["mechanisms"][mechanism_id]
            if mechanism_id == "binding_exclusive_delivery":
                equilibrium_use = ", ".join(str(value) for value in result["implemented_counts"])
                implemented = result["implemented_counts"] == cell["binding_optima"]
            else:
                equilibrium_use = "weak: " + ", ".join(str(value) for value in result["weak"])
                implemented = (
                    result.get("count_correspondence_matches_optimum") is True
                    or result["weak"] == cell["binding_optima"]
                )
            budget = result.get("expected_external_subsidy", "—")
            budget_note = result.get("budget_balance")
            if result.get("ex_post_budget_balance") is True:
                budget_note = "ex-post budget balanced"
            mechanism_rows.append(
                '<tr data-mechanism-row data-n="{n}" data-p="{p}" data-q="{q}" data-mechanism="{mechanism}"><th scope="row">{n}</th><td>{p}</td><td>{q}</td><td>{mechanism}</td><td>{equilibrium}</td><td>{optimum}</td><td>{budget}</td><td>{budget_note}</td><td>{implementation}</td></tr>'.format(
                    n=cell["agents"],
                    p=html.escape(str(cell["private_accuracy"])),
                    q=html.escape(str(cell["shared_accuracy"])),
                    mechanism=html.escape(mechanism_id),
                    equilibrium=html.escape(equilibrium_use),
                    optimum=html.escape(", ".join(str(value) for value in cell["binding_optima"])),
                    budget=html.escape(str(budget)),
                    budget_note=html.escape(str(budget_note or "—")),
                    implementation="yes" if implemented else "no",
                )
            )
    body = f"""<header class="page-hero"><p class="eyebrow">DD-013 interactive explainer</p><h1>Audience Design Lab</h1><p class="lede">Compare precomputed exact binding audiences, voluntary use, feasible symmetric garblings, and registered mechanisms. Access, voluntary use, and enforced action roles are different institutions; this read-only Lab makes no external call.</p></header><div class="stats"><div class="stat"><span>Binding rows</span><b>{summary["binding_audience_rows"]}</b></div><div class="stat"><span>Voluntary profiles</span><b>{summary["voluntary_profile_rows"]}</b></div><div class="stat"><span>Garbling rows</span><b>{summary["garbling_rows"]}</b></div></div><section class="lab" data-audience-lab><label for="audience-n">Team size</label><select id="audience-n">{agent_options}</select><label for="audience-p">Private accuracy</label><select id="audience-p">{accuracy_options}</select><label for="audience-q">Original shared accuracy</label><select id="audience-q">{accuracy_options}</select><label for="audience-use">Audience institution</label><select id="audience-use"><option value="binding">binding</option><option value="voluntary">voluntary</option></select><label for="audience-g">Delivered accuracy after garbling</label><select id="audience-g">{accuracy_options}</select><label for="audience-m">Audience size</label><select id="audience-m">{audience_options}</select><label for="audience-mechanism">Mechanism</label><select id="audience-mechanism">{mechanism_options}</select><p id="audience-status" class="callout" aria-live="polite">Select a registered cell. Exact rows below are filtered in place.</p></section><noscript><p class="callout">JavaScript is off. All {summary["binding_audience_rows"]} binding rows, {summary["voluntary_profile_rows"]} voluntary profiles, and {summary["garbling_rows"]} feasible garbling rows remain visible in the complete tables.</p></noscript><section class="content-section" data-binding-section><h2>Binding audience frontier</h2><table class="matrix"><caption>Exact binding audience metrics</caption><thead><tr><th>N</th><th>p</th><th>q</th><th>Audience</th><th>Discovery</th><th>Action quality</th><th>Expected distinct actions</th><th>Effective channels</th><th>Optimal</th></tr></thead><tbody>{binding_rows}</tbody></table></section><section class="content-section" data-voluntary-section><h2>Voluntary audience use</h2><table class="matrix"><caption>Exact reader-count equilibria conditional on information access</caption><thead><tr><th>N</th><th>p</th><th>q</th><th>Audience</th><th>Readers</th><th>Discovery</th><th>Equilibrium</th><th>Optimal audiences</th><th>Implementation</th></tr></thead><tbody>{voluntary_rows}</tbody></table></section><section class="content-section"><h2>Precision versus publicity</h2><table class="matrix"><caption>Exact feasible symmetric-garbling comparisons</caption><thead><tr><th>N</th><th>p</th><th>q</th><th>g</th><th>Audience</th><th>Discovery</th><th>Versus binding optimum</th></tr></thead><tbody>{garbling_rows}</tbody></table></section><section class="content-section"><h2>Mechanism implementation</h2><table class="matrix"><caption>Registered mechanisms, equilibrium audience use, optimum, transfer budget, and implementation status</caption><thead><tr><th>N</th><th>p</th><th>q</th><th>Mechanism</th><th>Equilibrium use</th><th>Optimal audiences</th><th>External subsidy</th><th>Budget status</th><th>Implements optimum</th></tr></thead><tbody>{"".join(mechanism_rows)}</tbody></table></section><details class="technical-details"><summary>Technical details</summary><p><a href="../claims.html#DD-C-0062">DD-C-0062</a> · <a href="../claims.html#DD-C-0063">DD-C-0063</a> · <a href="../claims.html#DD-C-0064">DD-C-0064</a> · <a href="../claims.html#DD-C-0065">DD-C-0065</a> · reproducible run <a href="{REPOSITORY_URL}/blob/main/results/verified/{DD013_RUN}/manifest.json">{DD013_RUN}</a></p></details><p><a href="../research/dd-013.html">Study page</a> · <a href="../data/audience/frontier.json">Download audience frontier</a> · <a href="../data/audience/garbling.json">Download garbling frontier</a> · <a href="../data/audience/mechanisms.json">Download mechanism results</a> · <a href="../data/audience/institutions.json">Download firewall registry</a></p>"""
    body = (
        body.replace(
            '<section class="lab" data-audience-lab>',
            '<section class="lab" data-audience-lab><fieldset class="lab-controls"><legend>Choose a registered audience design</legend>',
            1,
        )
        .replace(
            '<p id="audience-status"',
            '</fieldset><div class="lab-actions"><button type="button" class="filter-button" data-table-lab-reset>Reset</button><a href="../data/audience/frontier.json">Download data</a></div><p id="audience-status"',
            1,
        )
        .replace(
            "</section><noscript>",
            '<div class="metric-grid compact"><article class="metric-card planner"><span>Discovery</span><strong data-audience-output="discovery">—</strong></article><article class="metric-card"><span>Equilibrium / optimum</span><strong data-audience-output="equilibrium">—</strong></article><article class="metric-card"><span>Implementation</span><strong data-audience-output="implementation">—</strong></article><article class="metric-card"><span>Mechanism budget</span><strong data-audience-output="budget">—</strong></article></div><section class="lab-visual"><h2>Selected audience comparison</h2><p class="visual-summary">Binding access, voluntary use, garbling, and mechanism implementation remain visibly separate.</p><div class="comparison-readout"><div><span>Audience institution</span><strong data-audience-output="institution">—</strong></div><div><span>Garbling comparison</span><strong data-audience-output="garbling">—</strong></div></div></section><p class="takeaway" data-audience-takeaway>Select a registered audience design to compare access and use.</p></section><noscript>',
            1,
        )
    )
    body = body.replace(
        '<section class="content-section" data-binding-section>',
        '<details class="technical-details complete-data"><summary>Complete audience, garbling, and mechanism tables</summary><section class="content-section" data-binding-section>',
        1,
    ).replace(
        '<details class="technical-details"><summary>Technical details</summary>',
        '</details><details class="technical-details"><summary>Technical details</summary>',
        1,
    )
    _write(
        output,
        "labs/audience.html",
        _page(
            "Audience Lab",
            "Read-only exact binding-audience and symmetric-garbling explorer.",
            body,
            "labs/audience.html",
        ),
    )
    _write(
        output,
        "labs/audience-design.html",
        _page(
            "Audience Design Lab",
            "Read-only exact binding-audience and symmetric-garbling explorer.",
            body,
            "labs/audience-design.html",
        ),
    )
    data = {
        "summary.json": {"schema_version": 1, "run_id": DD013_RUN, "summary": summary},
        "frontier.json": {"schema_version": 1, "run_id": DD013_RUN, "cells": cells},
        "garbling.json": {"schema_version": 1, "run_id": DD013_RUN, "cells": garbling},
        "mechanisms.json": {
            "schema_version": 1,
            "run_id": DD013_RUN,
            "cells": mechanisms,
        },
        "institutions.json": {
            "schema_version": 1,
            "run_id": DD013_RUN,
            "institutions": institutions,
        },
    }
    for name, value in data.items():
        _write(output, f"data/audience/{name}", json.dumps(value, indent=2, sort_keys=True) + "\n")
    return {"run_id": DD013_RUN, "summary": summary}


def _conditional_pages(root: Path, output: Path) -> dict[str, object]:
    run = root / "results/verified" / DD014_RUN
    source = run / "outputs"
    summary = json.loads((source / "summary.json").read_text(encoding="utf-8"))
    cells = json.loads((source / "policy-census.json").read_text(encoding="utf-8"))
    phase_map = json.loads((source / "policy-phase-map.json").read_text(encoding="utf-8"))
    raw_audit = json.loads((source / "raw-policy-audit.json").read_text(encoding="utf-8"))
    registry = json.loads((source / "policy-registry.json").read_text(encoding="utf-8"))
    agents = sorted({int(cell["agents"]) for cell in cells})
    accuracies = sorted(
        {str(cell["private_accuracy"]) for cell in cells}, key=lambda value: Fraction(value)
    )
    profiles = sorted(
        {
            tuple(
                row["counts"][policy]
                for policy in ("private-dominant", "public-dominant", "contrarian")
            )
            for cell in cells
            for row in cell["profiles"]
        },
        key=lambda counts: (sum(counts), counts),
    )
    agent_options = "".join(f'<option value="{n}">{n}</option>' for n in agents)
    accuracy_options = "".join(
        f'<option value="{html.escape(value)}">{html.escape(value)}</option>'
        for value in accuracies
    )
    profile_options = "".join(
        f'<option value="{a},{b},{c}" data-n="{a + b + c}">private {a} · public {b} · contrarian {c}</option>'
        for a, b, c in profiles
    )
    rows = "".join(
        '<tr data-conditional-row data-n="{n}" data-p="{p}" data-q="{q}" data-profile="{profile}"><th scope="row">{n}</th><td>{p}</td><td>{q}</td><td>{a}</td><td>{b}</td><td>{c}</td><td>{discovery}</td><td>{payoffs}</td><td>{equilibrium}</td><td>{optimal}</td><td>{contrarian}</td></tr>'.format(
            n=cell["agents"],
            p=html.escape(str(cell["private_accuracy"])),
            q=html.escape(str(cell["shared_accuracy"])),
            profile=f"{row['counts']['private-dominant']},{row['counts']['public-dominant']},{row['counts']['contrarian']}",
            a=row["counts"]["private-dominant"],
            b=row["counts"]["public-dominant"],
            c=row["counts"]["contrarian"],
            discovery=html.escape(str(row["discovery"])),
            payoffs=html.escape(
                " · ".join(
                    f"{policy}: {row['payoffs'][policy] if row['payoffs'][policy] is not None else '—'}"
                    for policy in ("private-dominant", "public-dominant", "contrarian")
                )
            ),
            equilibrium="weak" if row["weak_equilibrium"] else "no",
            optimal="yes"
            if [
                row["counts"][policy]
                for policy in ("private-dominant", "public-dominant", "contrarian")
            ]
            in cell["planner_profiles"]
            else "no",
            contrarian="used" if row["counts"]["contrarian"] else "none",
        )
        for cell in cells
        for row in cell["profiles"]
    )
    body = f"""<header class="page-hero"><p class="eyebrow">DD-014 interactive explainer</p><h1>Conditional Attention Lab</h1><p class="lede">Explore every precomputed exact profile in DD-014's complete agreement-respecting label-equivariant disagreement class. Everyone sees both clues; this is not an access gate and not an unrestricted policy class.</p></header><div class="stats"><div class="stat"><span>Cells</span><b>{summary["grid_cells"]}</b></div><div class="stat"><span>Profiles</span><b>{summary["anonymous_profiles"]}</b></div><div class="stat"><span>Positive wedges</span><b>{summary["cells_with_positive_equilibrium_wedge"]}</b></div></div><section class="lab" data-conditional-lab><label for="conditional-n">Team size</label><select id="conditional-n">{agent_options}</select><label for="conditional-p">Private accuracy</label><select id="conditional-p">{accuracy_options}</select><label for="conditional-q">Shared accuracy</label><select id="conditional-q">{accuracy_options}</select><label for="conditional-policy">Role policy profile</label><select id="conditional-policy">{profile_options}</select><p id="conditional-status" class="callout" aria-live="polite">Select a registered exact profile.</p></section><noscript><p class="callout">JavaScript is off. All {summary["anonymous_profiles"]} exact profiles remain visible in the complete table.</p></noscript><section class="content-section"><h2>Conditional-policy census</h2><table class="matrix"><caption>Exact policy profiles, payoffs, equilibrium, optimum, and contrarian use</caption><thead><tr><th>N</th><th>p</th><th>q</th><th>Private roles</th><th>Public roles</th><th>Contrarian roles</th><th>Discovery</th><th>Type payoffs</th><th>Equilibrium</th><th>Optimal profile</th><th>Contrarian use</th></tr></thead><tbody>{rows}</tbody></table></section><details class="technical-details"><summary>Technical details</summary><p><a href="../claims.html#DD-C-0066">DD-C-0066</a> · <a href="../claims.html#DD-C-0067">DD-C-0067</a> · <a href="../claims.html#DD-C-0068">DD-C-0068</a> · reproducible run <a href="{REPOSITORY_URL}/blob/main/results/verified/{DD014_RUN}/manifest.json">{DD014_RUN}</a></p></details><p><a href="../research/dd-014.html">Study page</a> · <a href="../data/conditional/census.json">Download policy census</a> · <a href="../data/conditional/phase-map.json">Download phase map</a> · <a href="../data/conditional/raw-audit.json">Download larger-class audit</a></p>"""
    body = (
        body.replace(
            '<section class="lab" data-conditional-lab>',
            '<section class="lab" data-conditional-lab><fieldset class="lab-controls"><legend>Choose a registered conditional policy</legend>',
            1,
        )
        .replace(
            '<p id="conditional-status"',
            '</fieldset><div class="lab-actions"><button type="button" class="filter-button" data-table-lab-reset>Reset</button><a href="../data/conditional/census.json">Download data</a></div><p id="conditional-status"',
            1,
        )
        .replace(
            "</section><noscript>",
            '<div class="metric-grid compact"><article class="metric-card planner"><span>Discovery</span><strong data-conditional-output="discovery">—</strong></article><article class="metric-card"><span>Equilibrium</span><strong data-conditional-output="equilibrium">—</strong></article><article class="metric-card"><span>Planner-optimal profile</span><strong data-conditional-output="optimal">—</strong></article><article class="metric-card"><span>Contrarian role</span><strong data-conditional-output="contrarian">—</strong></article></div><section class="lab-visual"><h2>Selected role portfolio</h2><p class="visual-summary">Counts show how the selected team is divided across private-dominant, public-dominant, and contrarian policies.</p><div class="comparison-readout"><div><span>Private roles</span><strong data-conditional-output="private">—</strong></div><div><span>Public roles</span><strong data-conditional-output="public">—</strong></div><div><span>Contrarian roles</span><strong data-conditional-output="contrarian-count">—</strong></div></div></section><p class="takeaway" data-conditional-takeaway>The registered class is bounded; the larger-class counterexample remains part of the evidence boundary.</p></section><noscript>',
            1,
        )
    )
    body = body.replace(
        '<section class="content-section"><h2>Conditional-policy census</h2>',
        '<details class="technical-details complete-data"><summary>Complete conditional-policy table</summary><section class="content-section"><h2>Conditional-policy census</h2>',
        1,
    ).replace(
        '<details class="technical-details"><summary>Technical details</summary>',
        '</details><details class="technical-details"><summary>Technical details</summary>',
        1,
    )
    _write(
        output,
        "labs/conditional-attention.html",
        _page(
            "Conditional Attention Lab",
            "Read-only exact conditional-policy profile explorer.",
            body,
            "labs/conditional-attention.html",
        ),
    )
    data = {
        "summary.json": {"schema_version": 1, "run_id": DD014_RUN, "summary": summary},
        "census.json": {"schema_version": 1, "run_id": DD014_RUN, "cells": cells},
        "phase-map.json": {"schema_version": 1, "run_id": DD014_RUN, "cells": phase_map},
        "raw-audit.json": {"schema_version": 1, "run_id": DD014_RUN, "cells": raw_audit},
        "policy-registry.json": {"schema_version": 1, "run_id": DD014_RUN, "registry": registry},
    }
    for name, value in data.items():
        _write(
            output, f"data/conditional/{name}", json.dumps(value, indent=2, sort_keys=True) + "\n"
        )
    return {"run_id": DD014_RUN, "summary": summary}


def _program_v4_lab_pages(root: Path, output: Path) -> None:
    """Render the four Program V4 Labs from immutable exact run outputs."""

    def output_attributes(values: dict[str, object]) -> str:
        return " ".join(
            f'data-{key}="{html.escape(str(value), quote=True)}"' for key, value in values.items()
        )

    def provenance(study_id: str, claim_ids: tuple[str, ...], run_id: str, data: str) -> str:
        claims = " · ".join(
            f'<a href="../claims.html#{claim_id}">{claim_id}</a>' for claim_id in claim_ids
        )
        return f"""<section class="content-section prose"><h2>Evidence boundary</h2><p>These controls select exact rows already present in the immutable {study_id} run. They do not recompute, interpolate, or change claim status.</p><p>{claims} · <a href="{REPOSITORY_URL}/blob/main/results/verified/{run_id}/manifest.json">{run_id}</a> · <a href="../data/labs/{data}">Download the Lab data</a></p></section>"""

    threshold_source = (
        root / "results/verified" / DD016_RUN / "outputs/threshold-phase-diagram.json"
    )
    threshold_rows = json.loads(threshold_source.read_text(encoding="utf-8"))
    if not isinstance(threshold_rows, list) or len(threshold_rows) != 8:
        raise RuntimeError("DD-016 threshold Lab requires eight exact phase rows")
    threshold_data = {
        "schema_version": 1,
        "study_id": "DD-016",
        "claim_ids": ["DD-C-0073", "DD-C-0074"],
        "run_id": DD016_RUN,
        "rows": threshold_rows,
        "boundary": "canonical M=16, N=8, p=1/5 fixture; exact registered rows",
    }
    _write(
        output,
        "data/labs/threshold.json",
        json.dumps(threshold_data, indent=2, sort_keys=True) + "\n",
    )
    threshold_default = threshold_rows[1]

    def probability_display(value: object) -> str:
        return probability(value).display

    def count_display(value: object) -> str:
        return expected_count(value).display

    def threshold_takeaway(row: dict[str, Any]) -> str:
        region = (
            "diversification-dominant"
            if row["diversification_dominates_common_mode"]
            else "coordination-dominant"
        )
        return (
            f"Threshold {row['threshold']} is in the {region} region of this registered fixture: "
            + (
                "the planner benefits from forming the smallest viable teams and spreading them."
                if region == "diversification-dominant"
                else "only one viable coalition can form, so coordination capacity binds the portfolio."
            )
        )

    threshold_table = "".join(
        '<tr {}><th scope="row">{}</th><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            output_attributes(
                {
                    "output-row": "threshold",
                    "threshold": row["threshold"],
                    "planner-display": probability_display(row["planner_discovery"]),
                    "planner-exact": row["planner_discovery"],
                    "private-display": probability_display(row["private_clue_following"]),
                    "private-exact": row["private_clue_following"],
                    "tied-display": probability_display(row["tied_mode_mixed_discovery"]),
                    "tied-exact": row["tied_mode_mixed_discovery"],
                    "viable-display": count_display(row["expected_viable_candidates"]),
                    "viable-exact": row["expected_viable_candidates"],
                    "failed-display": count_display(row["failed_subthreshold_attempts"]),
                    "failed-exact": row["failed_subthreshold_attempts"],
                    "overlap-display": count_display(row["excess_overlap"]),
                    "overlap-exact": row["excess_overlap"],
                    "capacity": 8 // int(row["threshold"]),
                    "region": (
                        "diversification-dominant"
                        if row["diversification_dominates_common_mode"]
                        else "coordination-dominant"
                    ),
                    "takeaway": threshold_takeaway(row),
                }
            ),
            row["threshold"],
            html.escape(str(row["planner_discovery"])),
            html.escape(str(row["private_clue_following"])),
            html.escape(str(row["tied_mode_mixed_discovery"])),
            html.escape(str(row["expected_viable_candidates"])),
            html.escape(str(row["failed_subthreshold_attempts"])),
            html.escape(str(row["excess_overlap"])),
        )
        for row in threshold_rows
    )
    threshold_options = "".join(
        f'<option value="{tau}"{" selected" if tau == 2 else ""}>Minimum team {tau}</option>'
        for tau in range(1, 9)
    )

    def metric_card(label: str, display_key: str, exact_key: str, exact_value: object) -> str:
        identifier = f"threshold-{exact_key}"
        presented = (
            probability(exact_value)
            if "discovery" in label.lower()
            else expected_count(exact_value)
        )
        return f'''<article class="metric-card" data-exact-metric data-metric-label="{html.escape(label)}" aria-label="{html.escape(label)}: {html.escape(presented.accessible)}"><span>{html.escape(label)}</span><strong data-output-key="{display_key}">{html.escape(presented.display)}</strong><small class="exact-value">Exact: <code id="{identifier}" data-output-key="{exact_key}">{html.escape(presented.exact)}</code> <button type="button" class="copy-exact" data-copy-exact data-copy-target="{identifier}">Copy</button></small></article>'''

    def polyline(field: str) -> str:
        points = " ".join(
            f"{40 + (int(row['threshold']) - 1) * 90},{220 - float(Fraction(str(row[field]))) * 190:.2f}"
            for row in threshold_rows
        )
        return points

    def chart_point(row: dict[str, Any]) -> str:
        x = 40 + (int(row["threshold"]) - 1) * 90
        selected = ' class="selected"' if row["threshold"] == 2 else ""
        planner_y = 220 - float(Fraction(str(row["planner_discovery"]))) * 190
        private_y = 220 - float(Fraction(str(row["private_clue_following"]))) * 190
        tied_y = 220 - float(Fraction(str(row["tied_mode_mixed_discovery"]))) * 190
        return f'<g data-threshold-point="{row["threshold"]}"{selected}><circle class="planner-point" cx="{x}" cy="{planner_y:.2f}" r="5"><title>τ={row["threshold"]}, planner {probability_display(row["planner_discovery"])}</title></circle><circle class="private-point" cx="{x}" cy="{private_y:.2f}" r="5"><title>τ={row["threshold"]}, private {probability_display(row["private_clue_following"])}</title></circle><circle class="tied-point" cx="{x}" cy="{tied_y:.2f}" r="5"><title>τ={row["threshold"]}, tied mode {probability_display(row["tied_mode_mixed_discovery"])}</title></circle><text x="{x}" y="238" text-anchor="middle">{row["threshold"]}</text></g>'

    chart_points = "".join(chart_point(row) for row in threshold_rows)
    threshold_body = f"""<header class="page-hero"><p class="eyebrow">Interactive model · DD-016</p><h1>Threshold Lab</h1><p class="lede">Move the minimum viable team size across the complete canonical phase diagram and inspect discovery, viable teams, and crowding in readable units.</p></header><section class="lab explainer-lab" data-output-lab="threshold"><section class="threshold-context" aria-label="Registered context"><div><span>Boxes</span><strong>16</strong></div><div><span>Searchers</span><strong>8</strong></div><div><span>Required team size τ</span><strong data-output-key="threshold">2</strong></div><div><span>Viable-team capacity ⌊N/τ⌋</span><strong data-output-key="capacity">4</strong></div></section><fieldset class="lab-controls"><legend>Choose a registered threshold</legend><div><label for="threshold-tau">Minimum viable team</label><select id="threshold-tau" data-filter-key="threshold">{threshold_options}</select></div></fieldset><div class="lab-actions"><button type="button" class="filter-button" data-lab-reset>Reset</button><a href="../data/labs/threshold.json">Download data</a></div><p class="callout" data-output-status aria-live="polite">Showing the exact threshold-two row.</p><h2>Primary discovery comparison</h2><div class="metric-grid compact">{metric_card("Planner discovery", "planner-display", "planner-exact", threshold_default["planner_discovery"])}{metric_card("Private discovery", "private-display", "private-exact", threshold_default["private_clue_following"])}{metric_card("Tied-mode discovery", "tied-display", "tied-exact", threshold_default["tied_mode_mixed_discovery"])}</div><h2>Occupancy consequences</h2><div class="metric-grid compact">{metric_card("Expected viable candidates", "viable-display", "viable-exact", threshold_default["expected_viable_candidates"])}{metric_card("Failed subthreshold attempts", "failed-display", "failed-exact", threshold_default["failed_subthreshold_attempts"])}{metric_card("Excess overlap", "overlap-display", "overlap-exact", threshold_default["excess_overlap"])}</div><section class="lab-visual" aria-labelledby="threshold-chart-title"><h2 id="threshold-chart-title">Discovery across τ=1 through 8</h2><p class="visual-summary">Planner, private clue-following, and tied-mode discovery share a probability axis. The selected threshold has outlined points; the exact table is the chart fallback.</p><div class="chart-legend"><span class="planner-key">Planner</span><span class="private-key">Private</span><span class="tied-key">Tied mode</span></div><svg class="threshold-chart" viewBox="0 0 720 250" role="img" aria-labelledby="threshold-svg-title threshold-svg-desc"><title id="threshold-svg-title">Discovery probability by minimum viable team size</title><desc id="threshold-svg-desc">Three protocol lines across thresholds one through eight. Exact values are listed in the complete table.</desc><polyline class="planner-line" points="{polyline("planner_discovery")}"/><polyline class="private-line" points="{polyline("private_clue_following")}"/><polyline class="tied-line" points="{polyline("tied_mode_mixed_discovery")}"/>{chart_points}</svg></section><p class="takeaway"><strong>Selected region:</strong> <span data-output-key="region">diversification-dominant</span>. <span data-output-key="takeaway">{html.escape(threshold_takeaway(threshold_default))}</span></p></section><noscript><p class="callout">JavaScript is off. All eight exact threshold rows remain visible in the table.</p></noscript><details class="technical-details complete-data"><summary>Complete exact table</summary><table class="matrix"><caption>Complete exact DD-016 threshold phase diagram</caption><thead><tr><th>Threshold</th><th>Planner discovery</th><th>Private discovery</th><th>Tied-mode discovery</th><th>Viable candidates</th><th>Failed attempts</th><th>Excess overlap</th></tr></thead><tbody>{threshold_table}</tbody></table></details>{provenance("DD-016", ("DD-C-0073", "DD-C-0074"), DD016_RUN, "threshold.json")}"""
    _write(
        output,
        "labs/threshold.html",
        _page(
            "Threshold Lab",
            "Explore the exact DD-016 minimum-viable-team phase diagram.",
            threshold_body,
            "labs/threshold.html",
        ),
    )

    equilibrium_source = root / "results/verified" / DD017_RUN / "outputs/small-game-registry.json"
    equilibrium_registry = json.loads(equilibrium_source.read_text(encoding="utf-8"))
    games = equilibrium_registry.get("games") if isinstance(equilibrium_registry, dict) else None
    if not isinstance(games, list) or len(games) != 160:
        raise RuntimeError("DD-017 equilibrium Lab requires 160 exact games")
    equilibrium_rows = [
        {
            "fixture": row["name"],
            "agents": row["agents"],
            "threshold": row["threshold"],
            "planner_discovery": row["planner_discovery"],
            "best_equilibrium_discovery": row["best_equilibrium_discovery"],
            "worst_equilibrium_discovery": row["worst_equilibrium_discovery"],
            "pure_nash_count": row["pure_nash_count"],
            "pairwise_stable_count": row["pairwise_strict_stable_count"],
            "tau_stable_count": row["tau_strict_stable_count"],
            "price_of_anarchy": row["price_of_anarchy"],
            "tied_mode_is_equilibrium": row["tied_mode_mixed"]["is_equilibrium"],
        }
        for row in games
    ]
    equilibrium_data = {
        "schema_version": 1,
        "study_id": "DD-017",
        "claim_ids": ["DD-C-0075", "DD-C-0076", "DD-C-0077", "DD-C-0078"],
        "run_id": DD017_RUN,
        "rows": equilibrium_rows,
        "boundary": "160 registered rational posterior games; weak pure Nash and declared strict-member coalition tests",
    }
    _write(
        output,
        "data/labs/equilibrium-selection.json",
        json.dumps(equilibrium_data, indent=2, sort_keys=True) + "\n",
    )
    equilibrium_default = next(
        row
        for row in equilibrium_rows
        if row["fixture"] == "tied-top-three" and row["agents"] == 4 and row["threshold"] == 2
    )
    equilibrium_table = "".join(
        '<tr {}><th scope="row">{}</th><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            output_attributes(
                {
                    "output-row": "equilibrium",
                    "fixture": row["fixture"],
                    "agents": row["agents"],
                    "threshold": row["threshold"],
                    "planner-discovery": row["planner_discovery"],
                    "best-equilibrium": row["best_equilibrium_discovery"],
                    "worst-equilibrium": row["worst_equilibrium_discovery"],
                    "nash-count": row["pure_nash_count"],
                    "pair-count": row["pairwise_stable_count"],
                    "tau-count": row["tau_stable_count"],
                    "price-anarchy": row["price_of_anarchy"],
                    "mixed-equilibrium": str(row["tied_mode_is_equilibrium"]).lower(),
                }
            ),
            html.escape(str(row["fixture"])),
            row["agents"],
            row["threshold"],
            html.escape(str(row["planner_discovery"])),
            html.escape(str(row["best_equilibrium_discovery"])),
            html.escape(str(row["worst_equilibrium_discovery"])),
            row["pure_nash_count"],
            row["pairwise_stable_count"],
            row["tau_stable_count"],
        )
        for row in equilibrium_rows
    )
    fixture_options = "".join(
        f'<option value="{html.escape(name, quote=True)}"{" selected" if name == "tied-top-three" else ""}>{html.escape(name.replace("-", " ").title())}</option>'
        for name in sorted({str(row["fixture"]) for row in equilibrium_rows})
    )
    agent_options = "".join(
        f'<option value="{value}"{" selected" if value == 4 else ""}>{value} agents</option>'
        for value in range(2, 7)
    )
    equilibrium_threshold_options = "".join(
        f'<option value="{value}"{" selected" if value == 2 else ""}>{value}</option>'
        for value in range(1, 7)
    )
    equilibrium_body = f"""<header class="page-hero"><p class="eyebrow">Interactive model · DD-017</p><h1>Equilibrium-selection Lab</h1><p class="lede">Select a posterior fixture, team size, and opening threshold to expose the exact planner value, equilibrium range, multiplicity, and coalition-stability counts.</p></header><section class="lab" data-output-lab="equilibrium"><fieldset class="lab-controls"><legend>Choose a registered game</legend><div><label for="equilibrium-fixture">Posterior fixture</label><select id="equilibrium-fixture" data-filter-key="fixture">{fixture_options}</select></div><div><label for="equilibrium-agents">Agents</label><select id="equilibrium-agents" data-filter-key="agents">{agent_options}</select></div><div><label for="equilibrium-threshold">Threshold</label><select id="equilibrium-threshold" data-filter-key="threshold" data-limit-by="equilibrium-agents">{equilibrium_threshold_options}</select></div></fieldset><div class="lab-actions"><button type="button" class="filter-button" data-lab-reset>Reset</button><a href="../data/labs/equilibrium-selection.json">Download data</a></div><p class="callout" data-output-status aria-live="polite">Showing the tied-top-three, four-agent, threshold-two game.</p><div class="metric-grid compact"><article class="metric-card planner"><span>Planner discovery</span><strong data-output-key="planner-discovery">{html.escape(str(equilibrium_default["planner_discovery"]))}</strong></article><article class="metric-card"><span>Best equilibrium</span><strong data-output-key="best-equilibrium">{html.escape(str(equilibrium_default["best_equilibrium_discovery"]))}</strong></article><article class="metric-card"><span>Worst equilibrium</span><strong data-output-key="worst-equilibrium">{html.escape(str(equilibrium_default["worst_equilibrium_discovery"]))}</strong></article><article class="metric-card"><span>Pure Nash states</span><strong data-output-key="nash-count">{equilibrium_default["pure_nash_count"]}</strong></article><article class="metric-card"><span>Pair-stable states</span><strong data-output-key="pair-count">{equilibrium_default["pairwise_stable_count"]}</strong></article><article class="metric-card"><span>τ-stable states</span><strong data-output-key="tau-count">{equilibrium_default["tau_stable_count"]}</strong></article><article class="metric-card"><span>Price of anarchy</span><strong data-output-key="price-anarchy">{html.escape(str(equilibrium_default["price_of_anarchy"]))}</strong></article><article class="metric-card"><span>Tied-mode mixture is equilibrium</span><strong data-output-key="mixed-equilibrium">{str(equilibrium_default["tied_mode_is_equilibrium"]).lower()}</strong></article></div><section class="lab-visual" aria-labelledby="equilibrium-compare"><h2 id="equilibrium-compare">Planner and equilibrium range</h2><p class="visual-summary">The three-column comparison keeps the planner benchmark distinct from the best and worst equilibrium outcomes.</p><div class="comparison-readout"><div><span>Planner</span><strong data-output-key="planner-discovery">{html.escape(str(equilibrium_default["planner_discovery"]))}</strong></div><div><span>Best equilibrium</span><strong data-output-key="best-equilibrium">{html.escape(str(equilibrium_default["best_equilibrium_discovery"]))}</strong></div><div><span>Worst equilibrium</span><strong data-output-key="worst-equilibrium">{html.escape(str(equilibrium_default["worst_equilibrium_discovery"]))}</strong></div></div></section><p class="takeaway">Equilibrium selection matters whenever the best and worst equilibrium values differ; coalition-stability counts are reported separately and do not collapse that range.</p></section><noscript><p class="callout">JavaScript is off. All 160 exact game rows remain visible below.</p></noscript><details class="technical-details complete-data"><summary>Complete exact table — 160 games</summary><table class="matrix"><caption>Complete bounded DD-017 equilibrium census</caption><thead><tr><th>Fixture</th><th>Agents</th><th>Threshold</th><th>Planner</th><th>Best equilibrium</th><th>Worst equilibrium</th><th>Pure Nash</th><th>Pair-stable</th><th>τ-stable</th></tr></thead><tbody>{equilibrium_table}</tbody></table></details>{provenance("DD-017", ("DD-C-0075", "DD-C-0076", "DD-C-0077", "DD-C-0078"), DD017_RUN, "equilibrium-selection.json")}"""
    _write(
        output,
        "labs/equilibrium-selection.html",
        _page(
            "Equilibrium-selection Lab",
            "Inspect exact equilibrium and coalition-stability outcomes in DD-017.",
            equilibrium_body,
            "labs/equilibrium-selection.html",
        ),
    )

    dynamic_source = root / "results/verified" / DD015_RUN / "outputs/dynamic-profile.json"
    dynamic_source_rows = json.loads(dynamic_source.read_text(encoding="utf-8"))
    if not isinstance(dynamic_source_rows, list) or len(dynamic_source_rows) != 64:
        raise RuntimeError("DD-015 dynamic Lab requires 64 exact objective rows")
    dynamic_rows = [
        {
            "agents": row["agents"],
            "private_accuracy": row["private_accuracy"],
            "shared_accuracy": row["shared_accuracy"],
            "objective": row["objective"],
            "planner_discovery": row["planner"]["discovery"],
            "autonomous_discovery": row["autonomous"]["discovery"],
            "private_discovery": row["private_only"]["discovery"],
            "hidden_discovery": row["history_hidden_bayes"]["discovery"],
            "expected_actions": row["planner"]["expected_actions"],
            "distinct_actions": row["planner"]["expected_distinct_actions"],
            "follow_previous_rate": row["autonomous"]["previous_action_follow_rate"],
            "lean_against_rate": row["autonomous"]["lean_against_repeat_rate"],
        }
        for row in dynamic_source_rows
    ]
    dynamic_data = {
        "schema_version": 1,
        "study_id": "DD-015",
        "claim_ids": ["DD-C-0079", "DD-C-0080", "DD-C-0081"],
        "run_id": DD015_RUN,
        "rows": dynamic_rows,
        "boundary": "64 exact objective rows in the registered visible-action dynamic model",
    }
    _write(
        output,
        "data/labs/dynamic-attention.json",
        json.dumps(dynamic_data, indent=2, sort_keys=True) + "\n",
    )
    dynamic_default = next(
        row
        for row in dynamic_rows
        if row["agents"] == 3
        and row["private_accuracy"] == "1/2"
        and row["shared_accuracy"] == "3/4"
        and row["objective"] == "fixed-budget"
    )
    dynamic_table = "".join(
        '<tr {}><th scope="row">{}</th><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            output_attributes(
                {
                    "output-row": "dynamic",
                    "agents": row["agents"],
                    "private-accuracy": row["private_accuracy"],
                    "shared-accuracy": row["shared_accuracy"],
                    "objective": row["objective"],
                    "planner-discovery": row["planner_discovery"],
                    "autonomous-discovery": row["autonomous_discovery"],
                    "private-discovery": row["private_discovery"],
                    "hidden-discovery": row["hidden_discovery"],
                    "expected-actions": row["expected_actions"],
                    "distinct-actions": row["distinct_actions"],
                    "follow-rate": row["follow_previous_rate"],
                    "lean-rate": row["lean_against_rate"],
                }
            ),
            row["agents"],
            html.escape(str(row["private_accuracy"])),
            html.escape(str(row["shared_accuracy"])),
            html.escape(str(row["objective"])),
            html.escape(str(row["planner_discovery"])),
            html.escape(str(row["autonomous_discovery"])),
            html.escape(str(row["private_discovery"])),
            html.escape(str(row["expected_actions"])),
            html.escape(str(row["distinct_actions"])),
            html.escape(str(row["follow_previous_rate"])),
        )
        for row in dynamic_rows
    )
    private_options = "".join(
        f'<option value="{value}"{" selected" if value == "1/2" else ""}>{value}</option>'
        for value in ("1/3", "1/2", "2/3", "3/4")
    )
    shared_options = "".join(
        f'<option value="{value}"{" selected" if value == "3/4" else ""}>{value}</option>'
        for value in ("1/3", "1/2", "2/3", "3/4")
    )
    dynamic_body = f"""<header class="page-hero"><p class="eyebrow">Interactive model · DD-015</p><h1>Dynamic-attention Lab</h1><p class="lede">Change team size, private accuracy, shared accuracy, and stopping objective across the complete registered grid. The outputs distinguish planner, autonomous, private-only, and history-hidden behavior.</p></header><section class="lab" data-output-lab="dynamic"><fieldset class="lab-controls"><legend>Choose an exact dynamic profile</legend><div><label for="dynamic-agents">Agents</label><select id="dynamic-agents" data-filter-key="agents"><option value="2">2</option><option value="3" selected>3</option></select></div><div><label for="dynamic-private">Private accuracy</label><select id="dynamic-private" data-filter-key="private-accuracy">{private_options}</select></div><div><label for="dynamic-shared">Shared accuracy</label><select id="dynamic-shared" data-filter-key="shared-accuracy">{shared_options}</select></div><div><label for="dynamic-objective">Objective</label><select id="dynamic-objective" data-filter-key="objective"><option value="fixed-budget" selected>Fixed budget</option><option value="stopping-on-success">Stop on success</option></select></div></fieldset><div class="lab-actions"><button type="button" class="filter-button" data-lab-reset>Reset</button><a href="../data/labs/dynamic-attention.json">Download data</a></div><p class="callout" data-output-status aria-live="polite">Showing the exact N=3, p=1/2, q=3/4 fixed-budget row.</p><div class="metric-grid compact"><article class="metric-card planner"><span>Planner discovery</span><strong data-output-key="planner-discovery">{html.escape(str(dynamic_default["planner_discovery"]))}</strong></article><article class="metric-card consensus"><span>Autonomous discovery</span><strong data-output-key="autonomous-discovery">{html.escape(str(dynamic_default["autonomous_discovery"]))}</strong></article><article class="metric-card private"><span>Private-only discovery</span><strong data-output-key="private-discovery">{html.escape(str(dynamic_default["private_discovery"]))}</strong></article><article class="metric-card"><span>History-hidden discovery</span><strong data-output-key="hidden-discovery">{html.escape(str(dynamic_default["hidden_discovery"]))}</strong></article><article class="metric-card"><span>Expected actions</span><strong data-output-key="expected-actions">{html.escape(str(dynamic_default["expected_actions"]))}</strong></article><article class="metric-card"><span>Expected distinct actions</span><strong data-output-key="distinct-actions">{html.escape(str(dynamic_default["distinct_actions"]))}</strong></article><article class="metric-card"><span>Follow previous rate</span><strong data-output-key="follow-rate">{html.escape(str(dynamic_default["follow_previous_rate"]))}</strong></article><article class="metric-card"><span>Lean against repeat rate</span><strong data-output-key="lean-rate">{html.escape(str(dynamic_default["lean_against_rate"]))}</strong></article></div><section class="lab-visual" aria-labelledby="dynamic-compare"><h2 id="dynamic-compare">Protocol comparison</h2><p class="visual-summary">The selected row compares four information and coordination rules under one objective.</p><div class="comparison-readout"><div><span>Planner</span><strong data-output-key="planner-discovery">{html.escape(str(dynamic_default["planner_discovery"]))}</strong></div><div><span>Autonomous</span><strong data-output-key="autonomous-discovery">{html.escape(str(dynamic_default["autonomous_discovery"]))}</strong></div><div><span>Private only</span><strong data-output-key="private-discovery">{html.escape(str(dynamic_default["private_discovery"]))}</strong></div><div><span>History hidden</span><strong data-output-key="hidden-discovery">{html.escape(str(dynamic_default["hidden_discovery"]))}</strong></div></div></section><p class="takeaway">Visibility, private evidence, and the stopping objective are separate mechanisms. The selected profile reports their outcomes without treating autonomous behavior as the planner solution.</p></section><noscript><p class="callout">JavaScript is off. All 64 exact dynamic objective rows remain visible below.</p></noscript><details class="technical-details complete-data"><summary>Complete exact table — 64 rows</summary><table class="matrix"><caption>Complete exact DD-015 dynamic profile</caption><thead><tr><th>Agents</th><th>Private p</th><th>Shared q</th><th>Objective</th><th>Planner</th><th>Autonomous</th><th>Private only</th><th>Expected actions</th><th>Distinct actions</th><th>Follow rate</th></tr></thead><tbody>{dynamic_table}</tbody></table></details>{provenance("DD-015", ("DD-C-0079", "DD-C-0080", "DD-C-0081"), DD015_RUN, "dynamic-attention.json")}"""
    _write(
        output,
        "labs/dynamic-attention.html",
        _page(
            "Dynamic-attention Lab",
            "Explore exact planner and autonomous outcomes in DD-015.",
            dynamic_body,
            "labs/dynamic-attention.html",
        ),
    )

    mechanism_source = root / "results/verified" / DD018_RUN / "outputs/mechanism-census.json"
    mechanism_source_rows = json.loads(mechanism_source.read_text(encoding="utf-8"))
    if not isinstance(mechanism_source_rows, list) or len(mechanism_source_rows) != 50:
        raise RuntimeError("DD-018 mechanism Lab requires 50 exact rows")
    mechanism_rows = [
        {
            "fixture": row["fixture"],
            "mechanism": row["name"],
            "discovery": row["expected_discovery"],
            "planner_discovery": row["planner_discovery"],
            "implements_planner": row["implements_planner_portfolio"],
            "obedience": row["obedience"],
            "strict_unilateral": row["strict_unilateral_obedience"],
            "pairwise_stable": row["pairwise_strict_stable"],
            "tau_stable": row["tau_player_strict_stable"],
            "weak_budget_balance": row["weak_budget_balance"],
            "external_subsidy": row["external_subsidy"],
            "equilibrium_multiplicity": row["equilibrium_multiplicity"],
        }
        for row in mechanism_source_rows
    ]
    mechanism_data = {
        "schema_version": 1,
        "study_id": "DD-018",
        "claim_ids": ["DD-C-0083", "DD-C-0084", "DD-C-0085", "DD-C-0086"],
        "run_id": DD018_RUN,
        "rows": mechanism_rows,
        "boundary": "50 exact rows; truthfulness is not applicable under the common-posterior input",
    }
    _write(
        output,
        "data/labs/team-mechanisms.json",
        json.dumps(mechanism_data, indent=2, sort_keys=True) + "\n",
    )
    mechanism_default = next(
        row
        for row in mechanism_rows
        if row["fixture"] == "moderate" and row["mechanism"] == "team-tokens"
    )
    mechanism_table = "".join(
        '<tr {}><th scope="row">{}</th><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            output_attributes(
                {
                    "output-row": "mechanism",
                    "fixture": row["fixture"],
                    "mechanism": row["mechanism"],
                    "discovery": row["discovery"],
                    "planner-discovery": row["planner_discovery"],
                    "implements-planner": str(row["implements_planner"]).lower(),
                    "obedience": row["obedience"],
                    "strict-unilateral": row["strict_unilateral"],
                    "pairwise-stable": row["pairwise_stable"],
                    "tau-stable": row["tau_stable"],
                    "budget-balance": str(row["weak_budget_balance"]).lower(),
                    "external-subsidy": row["external_subsidy"],
                    "multiplicity": row["equilibrium_multiplicity"],
                }
            ),
            html.escape(str(row["fixture"])),
            html.escape(str(row["mechanism"])),
            html.escape(str(row["discovery"])),
            html.escape(str(row["implements_planner"])),
            html.escape(str(row["obedience"])),
            html.escape(str(row["pairwise_stable"])),
            html.escape(str(row["tau_stable"])),
            html.escape(str(row["equilibrium_multiplicity"])),
        )
        for row in mechanism_rows
    )
    mechanism_fixture_options = "".join(
        f'<option value="{html.escape(value, quote=True)}"{" selected" if value == "moderate" else ""}>{html.escape(value.replace("-", " ").title())}</option>'
        for value in sorted({str(row["fixture"]) for row in mechanism_rows})
    )
    mechanism_options = "".join(
        f'<option value="{html.escape(value, quote=True)}"{" selected" if value == "team-tokens" else ""}>{html.escape(value.replace("-", " ").title())}</option>'
        for value in sorted({str(row["mechanism"]) for row in mechanism_rows})
    )
    mechanism_body = f"""<header class="page-hero"><p class="eyebrow">Interactive model · DD-018</p><h1>Team-mechanism Lab</h1><p class="lede">Compare ten declared mechanisms across five posterior fixtures. Outputs keep authority, obedience, coalition stability, budget balance, and multiplicity separate.</p></header><section class="lab" data-output-lab="mechanism"><fieldset class="lab-controls"><legend>Choose a registered fixture and mechanism</legend><div><label for="mechanism-fixture">Posterior fixture</label><select id="mechanism-fixture" data-filter-key="fixture">{mechanism_fixture_options}</select></div><div><label for="mechanism-name">Mechanism</label><select id="mechanism-name" data-filter-key="mechanism">{mechanism_options}</select></div></fieldset><div class="lab-actions"><button type="button" class="filter-button" data-lab-reset>Reset</button><a href="../data/labs/team-mechanisms.json">Download data</a></div><p class="callout" data-output-status aria-live="polite">Showing the exact moderate-fixture team-token row.</p><div class="metric-grid compact"><article class="metric-card planner"><span>Expected discovery</span><strong data-output-key="discovery">{html.escape(str(mechanism_default["discovery"]))}</strong></article><article class="metric-card"><span>Planner discovery</span><strong data-output-key="planner-discovery">{html.escape(str(mechanism_default["planner_discovery"]))}</strong></article><article class="metric-card"><span>Implements planner portfolio</span><strong data-output-key="implements-planner">{str(mechanism_default["implements_planner"]).lower()}</strong></article><article class="metric-card"><span>Obedience</span><strong data-output-key="obedience">{html.escape(str(mechanism_default["obedience"]))}</strong></article><article class="metric-card"><span>Strict unilateral</span><strong data-output-key="strict-unilateral">{html.escape(str(mechanism_default["strict_unilateral"]))}</strong></article><article class="metric-card"><span>Pairwise stable</span><strong data-output-key="pairwise-stable">{html.escape(str(mechanism_default["pairwise_stable"]))}</strong></article><article class="metric-card"><span>τ-player stable</span><strong data-output-key="tau-stable">{html.escape(str(mechanism_default["tau_stable"]))}</strong></article><article class="metric-card"><span>Weak budget balance</span><strong data-output-key="budget-balance">{str(mechanism_default["weak_budget_balance"]).lower()}</strong></article><article class="metric-card"><span>External subsidy</span><strong data-output-key="external-subsidy">{html.escape(str(mechanism_default["external_subsidy"]))}</strong></article><article class="metric-card"><span>Equilibrium multiplicity</span><strong data-output-key="multiplicity">{html.escape(str(mechanism_default["equilibrium_multiplicity"]))}</strong></article></div><section class="lab-visual" aria-labelledby="mechanism-compare"><h2 id="mechanism-compare">Implementation profile</h2><p class="visual-summary">The selected row keeps portfolio implementation, obedience, stability, and budget feasibility as separate checks.</p><div class="comparison-readout"><div><span>Planner portfolio</span><strong data-output-key="implements-planner">{str(mechanism_default["implements_planner"]).lower()}</strong></div><div><span>Obedience</span><strong data-output-key="obedience">{html.escape(str(mechanism_default["obedience"]))}</strong></div><div><span>Pair stable</span><strong data-output-key="pairwise-stable">{html.escape(str(mechanism_default["pairwise_stable"]))}</strong></div><div><span>Budget balance</span><strong data-output-key="budget-balance">{str(mechanism_default["weak_budget_balance"]).lower()}</strong></div></div></section><p class="takeaway">A mechanism can improve discovery without satisfying every implementation concept. Common-posterior allocation does not test report truthfulness.</p></section><noscript><p class="callout">JavaScript is off. All 50 exact mechanism-fixture rows remain visible below.</p></noscript><details class="technical-details complete-data"><summary>Complete exact table — 50 rows</summary><table class="matrix"><caption>Complete exact DD-018 mechanism census</caption><thead><tr><th>Fixture</th><th>Mechanism</th><th>Discovery</th><th>Planner implemented</th><th>Obedience</th><th>Pair stable</th><th>τ stable</th><th>Multiplicity</th></tr></thead><tbody>{mechanism_table}</tbody></table></details>{provenance("DD-018", ("DD-C-0083", "DD-C-0084", "DD-C-0085", "DD-C-0086"), DD018_RUN, "team-mechanisms.json")}"""
    _write(
        output,
        "labs/team-mechanisms.html",
        _page(
            "Team-mechanism Lab",
            "Compare exact implementation and stability outcomes in DD-018.",
            mechanism_body,
            "labs/team-mechanisms.html",
        ),
    )


def _incremental_sharing_pages(root: Path, output: Path) -> None:
    """Render DD-020 controls from the sole immutable exact run."""

    run_outputs = root / "results/verified" / DD020_RUN / "outputs"
    point_source = run_outputs / "point-census.json"
    channel_source = run_outputs / "channel-profiles.json"
    point_rows = json.loads(point_source.read_text(encoding="utf-8"))
    channels = json.loads(channel_source.read_text(encoding="utf-8"))
    if not isinstance(point_rows, list) or len(point_rows) != 2555:
        raise RuntimeError("DD-020 Lab requires all 2,555 exact point rows")
    if not isinstance(channels, list) or len(channels) != 5:
        raise RuntimeError("DD-020 Lab requires all five exact channel profiles")

    def exact(value: Fraction) -> str:
        return str(value.numerator) if value.denominator == 1 else str(value)

    def transition(
        *,
        mode: str,
        targets: int,
        agents: int,
        accuracy: str,
        channel_id: str,
        block_size: int,
        pooled_profile: list[str],
        discovery_profile: list[str],
    ) -> dict[str, Any]:
        current_pooled = Fraction(pooled_profile[block_size - 1])
        next_pooled = Fraction(pooled_profile[block_size])
        current_discovery = Fraction(discovery_profile[block_size - 1])
        next_discovery = Fraction(discovery_profile[block_size])
        private_accuracy = Fraction(accuracy)
        factor = (1 - private_accuracy) ** (agents - block_size - 1)
        aggregation_gain = factor * (next_pooled - current_pooled)
        lost_rescue = factor * private_accuracy * (1 - current_pooled)
        net_increment = next_discovery - current_discovery
        sign = "positive" if net_increment > 0 else "negative" if net_increment < 0 else "zero"
        return {
            "mode": mode,
            "targets": targets,
            "agents": agents,
            "accuracy": accuracy,
            "channel_id": channel_id,
            "block_size": block_size,
            "next_block_size": block_size + 1,
            "pooled_accuracy": exact(current_pooled),
            "next_pooled_accuracy": exact(next_pooled),
            "group_discovery": exact(current_discovery),
            "next_group_discovery": exact(next_discovery),
            "aggregation_gain": exact(aggregation_gain),
            "lost_rescue": exact(lost_rescue),
            "net_increment": exact(net_increment),
            "sign": sign,
            "private_baseline": discovery_profile[0],
            "consensus": discovery_profile[-1],
            "pooled_profile": pooled_profile,
            "discovery_profile": discovery_profile,
        }

    point_profiles: dict[tuple[int, int, str], list[dict[str, object]]] = {}
    for row in point_rows:
        key = (int(row["targets"]), int(row["agents"]), str(row["accuracy"]))
        point_profiles.setdefault(key, []).append(row)
    point_transitions: list[dict[str, Any]] = []
    for (targets, agents, accuracy), rows in sorted(
        point_profiles.items(), key=lambda item: (item[0][0], item[0][1], Fraction(item[0][2]))
    ):
        ordered = sorted(rows, key=lambda row: int(str(row["block_size"])))
        pooled_profile = [str(row["pooled_accuracy"]) for row in ordered]
        discovery_profile = [str(row["group_discovery"]) for row in ordered]
        for block_size in range(1, agents):
            point_transitions.append(
                transition(
                    mode="point",
                    targets=targets,
                    agents=agents,
                    accuracy=accuracy,
                    channel_id="symmetric-noisy-point",
                    block_size=block_size,
                    pooled_profile=pooled_profile,
                    discovery_profile=discovery_profile,
                )
            )
    if len(point_transitions) != 2044:
        raise RuntimeError("DD-020 Lab requires all 2,044 adjacent point transitions")

    channel_transitions: list[dict[str, Any]] = []
    for channel in channels:
        for block_size in (1, 2):
            channel_transitions.append(
                transition(
                    mode="channel",
                    targets=4,
                    agents=3,
                    accuracy=str(channel["one_person_accuracy"]),
                    channel_id=str(channel["channel_id"]),
                    block_size=block_size,
                    pooled_profile=[str(value) for value in channel["pooled_accuracy"]],
                    discovery_profile=[str(value) for value in channel["profile"]],
                )
            )

    lab_data = {
        "schema_version": 1,
        "study_id": "DD-020",
        "claim_ids": ["DD-C-0092", "DD-C-0093", "DD-C-0094", "DD-C-0095", "DD-C-0096"],
        "run_id": DD020_RUN,
        "point_transitions": point_transitions,
        "channel_transitions": channel_transitions,
        "source_sha256": {
            "point_census": _sha256(point_source),
            "channel_profiles": _sha256(channel_source),
        },
        "boundary": "registered one-action sharing block with remaining direct private actions; not a private-team optimum or arbitrary-channel theorem",
    }
    _write(
        output,
        "data/labs/incremental-sharing.json",
        json.dumps(lab_data, indent=2, sort_keys=True) + "\n",
    )
    _write(output, "data/incremental-sharing/point-census.json", point_source.read_text())
    _write(output, "data/incremental-sharing/channel-profiles.json", channel_source.read_text())

    channel_names = {
        "noisy-point-half": "Noisy point (accuracy 1/2)",
        "noisy-shortlist-three-quarters": "Noisy shortlist (accuracy 3/8)",
        "guaranteed-shortlist-two": "Guaranteed shortlist (accuracy 1/2)",
        "explicit-exclusion": "Explicit exclusion (accuracy 1/3)",
        "confidence-point": "Confidence point (accuracy 5/8)",
    }

    def incremental_attributes(row: dict[str, Any]) -> str:
        values = {
            "incremental-row": "",
            "mode": row["mode"],
            "targets": row["targets"],
            "agents": row["agents"],
            "accuracy": row["accuracy"],
            "channel": row["channel_id"],
            "block-size": row["block_size"],
            "pooled-accuracy": row["pooled_accuracy"],
            "next-pooled-accuracy": row["next_pooled_accuracy"],
            "group-discovery": row["group_discovery"],
            "next-group-discovery": row["next_group_discovery"],
            "aggregation-gain": row["aggregation_gain"],
            "lost-rescue": row["lost_rescue"],
            "net-increment": row["net_increment"],
            "sign": row["sign"],
            "private-baseline": row["private_baseline"],
            "consensus": row["consensus"],
            "pooled-profile": "|".join(str(value) for value in row["pooled_profile"]),
            "discovery-profile": "|".join(str(value) for value in row["discovery_profile"]),
        }
        return " ".join(
            f'data-{key}="{html.escape(str(value), quote=True)}"' for key, value in values.items()
        )

    def table_row(row: dict[str, Any]) -> str:
        source = (
            channel_names[str(row["channel_id"])]
            if row["mode"] == "channel"
            else f"M={row['targets']}, N={row['agents']}, p={row['accuracy']}"
        )
        return """<tr {attrs}><th scope="row">{source}</th><td>{step}→{next_step}</td><td>{pooled}</td><td>{discovery}</td><td>{gain}</td><td>{rescue}</td><td>{net}</td><td>{sign}</td><td>{private}</td><td>{consensus}</td></tr>""".format(
            attrs=incremental_attributes(row),
            source=html.escape(source),
            step=row["block_size"],
            next_step=row["next_block_size"],
            pooled=html.escape(str(row["pooled_accuracy"])),
            discovery=html.escape(str(row["group_discovery"])),
            gain=html.escape(str(row["aggregation_gain"])),
            rescue=html.escape(str(row["lost_rescue"])),
            net=html.escape(str(row["net_increment"])),
            sign=html.escape(str(row["sign"])),
            private=html.escape(str(row["private_baseline"])),
            consensus=html.escape(str(row["consensus"])),
        )

    default = next(
        row
        for row in point_transitions
        if row["targets"] == 4
        and row["agents"] == 3
        and row["accuracy"] == "1/2"
        and row["block_size"] == 1
    )
    target_options = "".join(
        f'<option value="{value}"{" selected" if value == 4 else ""}>M={value} targets</option>'
        for value in range(2, 9)
    )
    agent_options = "".join(
        f'<option value="{value}"{" selected" if value == 3 else ""}>N={value} agents</option>'
        for value in range(2, 9)
    )
    accuracy_targets: dict[str, set[int]] = {}
    for targets, _, accuracy in point_profiles:
        accuracy_targets.setdefault(accuracy, set()).add(targets)
    accuracy_options = "".join(
        '<option value="{}" data-targets="{}"{}>p={}</option>'.format(
            html.escape(accuracy, quote=True),
            ",".join(str(value) for value in sorted(targets)),
            " selected" if accuracy == "1/2" else "",
            html.escape(accuracy),
        )
        for accuracy, targets in sorted(
            accuracy_targets.items(), key=lambda item: Fraction(item[0])
        )
    )
    step_options = "".join(
        f'<option value="{value}"{" selected" if value == 1 else ""}>s={value} → {value + 1}</option>'
        for value in range(1, 8)
    )
    channel_options = "".join(
        f'<option value="{html.escape(channel_id, quote=True)}"{" selected" if channel_id == "noisy-point-half" else ""}>{html.escape(channel_names[channel_id])}</option>'
        for channel_id in channel_names
    )
    comparison_options = '<option value="none">No comparison</option>' + "".join(
        f'<option value="{html.escape(channel_id, quote=True)}" data-accuracy="{html.escape(str(channel["one_person_accuracy"]), quote=True)}"{" selected" if channel_id == "guaranteed-shortlist-two" else ""}>{html.escape(channel_names[channel_id])}</option>'
        for channel_id, channel in ((str(channel["channel_id"]), channel) for channel in channels)
    )
    chart_points = "".join(
        '<div class="profile-point" data-profile-point="{index}"{hidden}><span class="profile-value" data-profile-value>{value}</span><span class="profile-bar" data-profile-bar style="--profile-value:{height}%"></span><strong>s={index}</strong></div>'.format(
            index=index,
            hidden=" hidden" if index > 3 else "",
            value=html.escape(default["discovery_profile"][index - 1] if index <= 3 else "0"),
            height=float(Fraction(default["discovery_profile"][index - 1])) * 100
            if index <= 3
            else 0,
        )
        for index in range(1, 9)
    )
    canonical_profile = [
        row
        for row in sorted(
            point_profiles[(4, 3, "1/2")], key=lambda item: int(str(item["block_size"]))
        )
    ]
    canonical_rows = "".join(
        f'<tr><th scope="row">{row["block_size"]}</th><td>{html.escape(str(row["pooled_accuracy"]))}</td><td>{html.escape(str(row["group_discovery"]))}</td><td>{html.escape(str(row["increment"] if row["increment"] is not None else "baseline"))}</td></tr>'
        for row in canonical_profile
    )
    channel_rows = "".join(
        '<tr><th scope="row">{}</th><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
            html.escape(channel_names[str(channel["channel_id"])]),
            html.escape(str(channel["one_person_accuracy"])),
            html.escape(", ".join(str(value) for value in channel["profile"])),
            html.escape(", ".join(str(value) for value in channel["increments"])),
        )
        for channel in channels
    )
    all_rows = "".join(table_row(row) for row in point_transitions + channel_transitions)
    body = f"""<header class="page-hero"><p class="eyebrow">DD-020 exact output Lab</p><h1>Incremental Sharing Lab</h1><p class="lede">Move one signal at a time from independent private search into a one-action pooling block. The Lab separates pooled-accuracy gain from lost independent rescue and selects only rows in the immutable DD-020 run.</p></header><section class="content-section prose"><h2>The registered identity</h2><p class="identity">G<sub>s</sub> = 1 − (1−C<sub>s</sub>)(1−q)<sup>N−s</sup></p><p>The point-channel theorem says each adjacent move weakly lowers discovery, strictly unless signals are perfect. The five-channel audit supplies a scope boundary: the guaranteed shortlist rises, so the point theorem is not an arbitrary-channel monotonicity result.</p></section><section class="lab" data-incremental-lab><div class="lab-controls"><div><label for="incremental-mode">Evidence view</label><select id="incremental-mode"><option value="point" selected>Point-channel census</option><option value="channel">Registered channel comparison</option></select></div><div data-point-control><label for="incremental-targets">Targets</label><select id="incremental-targets">{target_options}</select></div><div data-point-control><label for="incremental-agents">Agents</label><select id="incremental-agents">{agent_options}</select></div><div data-point-control><label for="incremental-accuracy">Private accuracy</label><select id="incremental-accuracy">{accuracy_options}</select></div><div data-channel-control hidden><label for="incremental-channel">Channel</label><select id="incremental-channel" disabled>{channel_options}</select></div><div><label for="incremental-step">Sharing step</label><select id="incremental-step">{step_options}</select></div><div data-channel-control hidden><label for="incremental-comparison">Same-accuracy comparison</label><select id="incremental-comparison" disabled>{comparison_options}</select></div></div><p id="incremental-status" class="callout" aria-live="polite">Showing M=4, N=3, p=1/2, s=1→2 from the exact point census.</p><div class="metric-grid compact"><article class="metric-card"><span>Pooled accuracy C<sub>s</sub></span><strong data-incremental-output="pooled-accuracy">{default["pooled_accuracy"]}</strong></article><article class="metric-card"><span>Next pooled accuracy C<sub>s+1</sub></span><strong data-incremental-output="next-pooled-accuracy">{default["next_pooled_accuracy"]}</strong></article><article class="metric-card planner"><span>Discovery G<sub>s</sub></span><strong data-incremental-output="group-discovery">{default["group_discovery"]}</strong></article><article class="metric-card planner"><span>Next discovery G<sub>s+1</sub></span><strong data-incremental-output="next-group-discovery">{default["next_group_discovery"]}</strong></article><article class="metric-card"><span>Marginal aggregation gain</span><strong data-incremental-output="aggregation-gain">{default["aggregation_gain"]}</strong></article><article class="metric-card"><span>Lost rescue</span><strong data-incremental-output="lost-rescue">{default["lost_rescue"]}</strong></article><article class="metric-card consensus"><span>Net increment</span><strong data-incremental-output="net-increment">{default["net_increment"]}</strong></article><article class="metric-card"><span>Increment sign</span><strong data-incremental-output="sign">{default["sign"]}</strong></article><article class="metric-card private"><span>Private baseline G<sub>1</sub></span><strong data-incremental-output="private-baseline">{default["private_baseline"]}</strong></article><article class="metric-card consensus"><span>Consensus G<sub>N</sub></span><strong data-incremental-output="consensus">{default["consensus"]}</strong></article></div><section class="profile-panel" aria-labelledby="incremental-curve-title"><h2 id="incremental-curve-title">Exact discovery profile</h2><p data-incremental-comparison>Same-accuracy comparison is available in the registered-channel view.</p><div class="profile-plot" role="img" aria-label="Discovery profile by sharing-block size" data-incremental-chart>{chart_points}</div></section></section><noscript><p class="callout">JavaScript is off. The exact canonical point profile and all five channel profiles remain visible below; the complete 2,555-row census is available as a direct data download.</p></noscript><section class="content-section"><h2>Canonical exact point profile</h2><table class="matrix"><caption>M=4, N=3, p=1/2 under the registered symmetric noisy-point channel</caption><thead><tr><th>Block size s</th><th>Pooled accuracy C<sub>s</sub></th><th>Discovery G<sub>s</sub></th><th>Increment</th></tr></thead><tbody>{canonical_rows}</tbody></table></section><section class="content-section"><h2>Registered channel comparison</h2><table class="matrix"><caption>Five exact M=4, N=3 incremental-sharing profiles</caption><thead><tr><th>Channel</th><th>One-person accuracy</th><th>(G<sub>1</sub>, G<sub>2</sub>, G<sub>3</sub>)</th><th>Adjacent increments</th></tr></thead><tbody>{channel_rows}</tbody></table></section><details class="technical-details complete-data"><summary>Inspect all 2,054 exact adjacent transitions</summary><table class="matrix"><caption>Complete point-census and registered-channel transitions used by the Lab</caption><thead><tr><th>Source</th><th>Step</th><th>C<sub>s</sub></th><th>G<sub>s</sub></th><th>Aggregation gain</th><th>Lost rescue</th><th>Net</th><th>Sign</th><th>Private baseline</th><th>Consensus</th></tr></thead><tbody>{all_rows}</tbody></table></details><section class="content-section prose"><h2>Evidence boundary and data</h2><p>These controls select and decompose exact rows from DD-020; they do not recompute the study, interpolate, or change claim status. Marginal aggregation gain and lost rescue are the two exact contributions in the registered adjacent-difference identity.</p><p><a href="../claims.html#DD-C-0092">DD-C-0092</a> · <a href="../claims.html#DD-C-0094">DD-C-0094</a> · <a href="../claims.html#DD-C-0095">DD-C-0095</a> · <a href="../claims.html#DD-C-0096">DD-C-0096</a> · <a href="{REPOSITORY_URL}/blob/main/results/verified/{DD020_RUN}/manifest.json">{DD020_RUN}</a></p><p><a href="../data/incremental-sharing/point-census.json">Download the full 2,555-row point census</a> · <a href="../data/incremental-sharing/channel-profiles.json">Download the five channel profiles</a> · <a href="../data/labs/incremental-sharing.json">Download the Lab transition data</a></p></section>"""
    _write(
        output,
        "labs/incremental-sharing.html",
        _page(
            "Incremental Sharing Lab",
            "Explore exact aggregation gain, lost independent rescue, and net discovery increments in DD-020.",
            body,
            "labs/incremental-sharing.html",
        ),
    )


def _general_sharing_pages(root: Path, output: Path) -> None:
    """Render the DD-021 Lab from the sole immutable exact registry."""

    run_outputs = root / "results/verified" / DD021_RUN / "outputs"
    registry_source = run_outputs / "registry.json"
    witnesses_source = run_outputs / "minimal-witnesses.json"
    channels_source = run_outputs / "channels.json"
    rows = json.loads(registry_source.read_text(encoding="utf-8"))
    witnesses = json.loads(witnesses_source.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) != 177:
        raise RuntimeError("DD-021 Lab requires all 177 exact scenarios")
    if witnesses.get("mixed_sharing_bounded_null") is not True:
        raise RuntimeError("DD-021 Lab requires the audited bounded-null record")

    claims = [f"DD-C-{identifier:04d}" for identifier in range(97, 104)]
    lab_data = {
        "schema_version": 1,
        "study_id": "DD-021",
        "claim_ids": claims,
        "run_id": DD021_RUN,
        "rows": rows,
        "witnesses": witnesses,
        "source_sha256": {
            "registry": _sha256(registry_source),
            "minimal_witnesses": _sha256(witnesses_source),
            "channels": _sha256(channels_source),
        },
        "boundary": "selectors expose immutable exact rows; top-L values require centralized pooled action authority and are not decentralized implementations",
    }
    _write(
        output,
        "data/labs/general-sharing-frontier.json",
        json.dumps(lab_data, indent=2, sort_keys=True) + "\n",
    )


def _coordination_free_sharing_pages(root: Path, output: Path) -> None:
    """Render DD-022 using only its immutable exact registry."""

    run_outputs = root / "results/verified" / DD022_RUN / "outputs"
    registry_source = run_outputs / "registry.json"
    certificate_source = run_outputs / "threshold-certificate.json"
    rows = json.loads(registry_source.read_text(encoding="utf-8"))
    certificate = json.loads(certificate_source.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or len(rows) != 42:
        raise RuntimeError("DD-022 Lab requires all 42 exact cells")
    if certificate.get("passed") is not True:
        raise RuntimeError("DD-022 Lab requires the passing root certificate")
    claims = [f"DD-C-{identifier:04d}" for identifier in range(104, 111)]
    lab_data = {
        "schema_version": 1,
        "study_id": "DD-022",
        "claim_ids": claims,
        "run_id": DD022_RUN,
        "rows": rows,
        "threshold_certificate": certificate,
        "source_sha256": {
            "registry": _sha256(registry_source),
            "threshold_certificate": _sha256(certificate_source),
        },
        "boundary": "selectors expose immutable posterior-only selected-equilibrium outputs; signal-ownership-aware equilibria and centralized role allocation are separate",
    }
    _write(
        output,
        "data/labs/coordination-free-positive-sharing.json",
        json.dumps(lab_data, indent=2, sort_keys=True) + "\n",
    )
    _write(
        output,
        "data/coordination-free-positive-sharing/registry.json",
        registry_source.read_text(),
    )
    _write(
        output,
        "data/coordination-free-positive-sharing/threshold-certificate.json",
        certificate_source.read_text(),
    )

    accuracies = sorted({str(row["accuracy"]) for row in rows}, key=lambda x: Fraction(x))
    dependence = sorted({str(row["dependence"]) for row in rows}, key=lambda x: Fraction(x))
    accuracy_options = "".join(
        f'<option value="{value}"{" selected" if value == "3/5" else ""}>{float(Fraction(value)):.2f} · {value}</option>'
        for value in accuracies
    )
    dependence_options = "".join(
        f'<option value="{value}"{" selected" if value == "1/2" else ""}>{float(Fraction(value)):.3f} · {value}</option>'
        for value in dependence
    )

    def coordination_attributes(row: dict[str, Any]) -> str:
        private = row["private_metrics"]
        shared = row["shared_metrics"]
        direct = row["direct_private_metrics"]
        values = {
            "coordination-row": "",
            "accuracy": row["accuracy"],
            "dependence": row["dependence"],
            "private-r": row["private_selection"]["follow_probability"],
            "private-regime": row["private_selection"]["regime"],
            "agreement-posterior": row["shared_selection"]["agreement_posterior"],
            "shared-x": row["shared_selection"]["agreement_action_probability"],
            "shared-regime": row["shared_selection"]["agreement_regime"],
            "direct-discovery": direct["discovery"],
            "private-discovery": private["discovery"],
            "shared-discovery": shared["discovery"],
            "private-payoff": private["payoff_per_agent"],
            "shared-payoff": shared["payoff_per_agent"],
            "private-collision": private["collision"],
            "shared-collision": shared["collision"],
            "private-diversity": private["diversity"],
            "shared-diversity": shared["diversity"],
            "private-quality": private["average_action_quality"],
            "shared-quality": shared["average_action_quality"],
            "private-gap": private["implementation_gap"],
            "shared-gap": shared["implementation_gap"],
            "selected-gain": row["selected_sharing_gain"],
            "private-minus-direct": str(
                Fraction(private["discovery"]) - Fraction(direct["discovery"])
            ),
            "shared-minus-direct": str(
                Fraction(shared["discovery"]) - Fraction(direct["discovery"])
            ),
            "private-minus-shared": str(
                Fraction(private["discovery"]) - Fraction(shared["discovery"])
            ),
            "shared-minus-private": row["selected_sharing_gain"],
            "gain-class": row["gain_class"],
        }
        return " ".join(
            f'data-{key}="{html.escape(str(value), quote=True)}"' for key, value in values.items()
        )

    table_rows = "".join(
        '<tr {attrs}><th scope="row">{p}</th><td>{rho}</td><td>{r}</td><td>{x}</td><td>{private}</td><td>{shared}</td><td>{gain}</td><td>{kind}</td></tr>'.format(
            attrs=coordination_attributes(row),
            p=html.escape(str(row["accuracy"])),
            rho=html.escape(str(row["dependence"])),
            r=html.escape(str(row["private_selection"]["follow_probability"])),
            x=html.escape(str(row["shared_selection"]["agreement_action_probability"])),
            private=html.escape(str(row["private_metrics"]["discovery"])),
            shared=html.escape(str(row["shared_metrics"]["discovery"])),
            gain=html.escape(str(row["selected_sharing_gain"])),
            kind=html.escape(str(row["gain_class"])),
        )
        for row in rows
    )
    default = next(row for row in rows if row["accuracy"] == "3/5" and row["dependence"] == "1/2")

    def coordination_percent(value: str) -> str:
        return f"{float(Fraction(value)) * 100:.1f}%"

    def coordination_metric(label: str, key: str, value: str) -> str:
        return f'<article class="metric-card" data-coordination-output="{key}"><span>{label}</span><strong>{coordination_percent(value)}</strong><code class="exact-value">{html.escape(value)}</code></article>'

    metrics = "".join(
        [
            coordination_metric(
                "Follow probability r",
                "strategy",
                str(default["private_selection"]["follow_probability"]),
            ),
            coordination_metric(
                "Agreement posterior u",
                "posterior",
                str(default["shared_selection"]["agreement_posterior"]),
            ),
            coordination_metric(
                "Agreement action probability x",
                "shared-action",
                str(default["shared_selection"]["agreement_action_probability"]),
            ),
            coordination_metric(
                "Discovery", "discovery", str(default["private_metrics"]["discovery"])
            ),
            coordination_metric(
                "Payoff per agent", "payoff", str(default["private_metrics"]["payoff_per_agent"])
            ),
            coordination_metric(
                "Collision", "collision", str(default["private_metrics"]["collision"])
            ),
            coordination_metric(
                "Action diversity", "diversity", str(default["private_metrics"]["diversity"])
            ),
            coordination_metric(
                "Average action quality",
                "quality",
                str(default["private_metrics"]["average_action_quality"]),
            ),
            coordination_metric("Gain over baseline", "gain", "0"),
            coordination_metric(
                "Gap to centralized V2",
                "gap",
                str(default["private_metrics"]["implementation_gap"]),
            ),
        ]
    )
    profile_points = "".join(
        f'<div class="profile-point" data-coordination-point data-rho="{html.escape(value, quote=True)}"><strong>ρ={html.escape(value)}</strong><div class="profile-bar" data-coordination-private-bar></div><div class="profile-bar" data-coordination-shared-bar></div><span class="profile-value" data-coordination-value>—</span></div>'
        for value in dependence
    )
    claim_links = " · ".join(f'<a href="../claims.html#{claim}">{claim}</a>' for claim in claims)
    root_expression = html.escape(str(certificate["exact_positive_root"]))
    body = f"""<header class="page-hero"><p class="eyebrow">Interactive exact-output model · DD-022</p><h1>Coordination-Free Positive Sharing Lab</h1><p class="lede">Select an immutable exact cell and compare the declared private and posterior-only shared symmetric equilibria. The Lab never recomputes or interpolates evidence.</p></header><section class="content-section prose"><h2>Exact selected crossover</h2><p class="identity">at p=3/5, shared discovery &gt; private equilibrium discovery iff ρ ∈ ({root_expression}, 1)</p><p>Approximate marker: ρ*=53.583%. Sharing reveals the agreement pattern and updates dependence beliefs; it does not reveal the latent source branch or assign roles.</p></section><section class="lab" data-coordination-lab><fieldset class="lab-controls"><legend>Choose an exact registered comparison</legend><div><label for="coordination-accuracy">Signal accuracy p</label><select id="coordination-accuracy">{accuracy_options}</select></div><div><label for="coordination-dependence">Dependence ρ</label><select id="coordination-dependence">{dependence_options}</select></div><div><label for="coordination-regime">Information regime</label><select id="coordination-regime"><option value="private">Private</option><option value="shared">Shared</option></select></div><div><label for="coordination-baseline">Comparison baseline</label><select id="coordination-baseline"><option value="direct">Direct private</option><option value="private">Private symmetric equilibrium</option><option value="shared">Shared symmetric equilibrium</option></select></div></fieldset><div class="lab-actions"><button type="button" class="filter-button" data-coordination-reset>Reset</button><a href="../data/labs/coordination-free-positive-sharing.json">Download Lab data</a></div><p id="coordination-status" class="callout" aria-live="polite">Showing the p=3/5, rho=1/2 private selected equilibrium.</p><div class="metric-grid compact">{metrics}<article class="metric-card"><span>Private regime</span><strong data-coordination-text="private-regime">{html.escape(str(default["private_selection"]["regime"]))}</strong></article><article class="metric-card"><span>Shared regime</span><strong data-coordination-text="shared-regime">{html.escape(str(default["shared_selection"]["agreement_regime"]))}</strong></article></div><section class="profile-panel"><h2>Discovery versus ρ</h2><p class="visual-summary">Private is the first bar; shared is the second. The exact crossover applies to p=3/5.</p><div class="profile-plot" role="img" aria-label="Private and shared selected discovery by registered dependence" data-coordination-chart>{profile_points}</div></section><section class="profile-panel"><h2>Regimes and implementation gap</h2><p class="visual-summary" data-coordination-regime-summary>The selected cell reports both equilibrium regimes and the remaining gap to centralized V2=1.</p></section></section><noscript><p class="callout">JavaScript is off. All 42 exact cells remain visible below and downloadable.</p></noscript><details class="technical-details complete-data"><summary>Complete exact table — 42 cells</summary><table class="matrix"><caption>DD-022 selected-equilibrium registry</caption><thead><tr><th>p</th><th>ρ</th><th>Private r</th><th>Shared agreement x</th><th>Private discovery</th><th>Shared discovery</th><th>Gain</th><th>Class</th></tr></thead><tbody>{table_rows}</tbody></table></details><section class="content-section prose"><h2>Evidence and selection boundary</h2><p>The result is exact for a posterior-only, provenance-blind identical-mixing selection. Ownership-aware and role-dependent equilibria can split targets and attain different discovery; the strict result does not survive every equilibrium.</p><p>{claim_links} · <a href="{REPOSITORY_URL}/blob/main/results/verified/{DD022_RUN}/manifest.json">{DD022_RUN}</a></p><p><a href="../data/coordination-free-positive-sharing/registry.json">Download exact registry</a> · <a href="../data/coordination-free-positive-sharing/threshold-certificate.json">Download root certificate</a></p></section>"""
    _write(
        output,
        "labs/coordination-free-positive-sharing.html",
        _page(
            "Coordination-Free Positive Sharing Lab",
            "Explore DD-022's exact selected-equilibrium sharing threshold and selection boundary.",
            body,
            "labs/coordination-free-positive-sharing.html",
        ),
    )
    # Finish rendering the adjacent DD-021 Lab whose data envelope is emitted
    # by `_general_sharing_pages` immediately before this renderer is called.
    run_outputs = root / "results/verified" / DD021_RUN / "outputs"
    registry_source = run_outputs / "registry.json"
    witnesses_source = run_outputs / "minimal-witnesses.json"
    channels_source = run_outputs / "channels.json"
    rows = json.loads(registry_source.read_text(encoding="utf-8"))
    claims = [f"DD-C-{identifier:04d}" for identifier in range(97, 104)]
    _write(output, "data/general-sharing-frontier/registry.json", registry_source.read_text())
    _write(
        output, "data/general-sharing-frontier/minimal-witnesses.json", witnesses_source.read_text()
    )
    _write(output, "data/general-sharing-frontier/channels.json", channels_source.read_text())

    families = sorted({str(row["family"]) for row in rows})
    family_names = {
        "symmetric-noisy-point": "Symmetric noisy point",
        "noisy-k-shortlist": "Noisy K-shortlist",
        "guaranteed-k-shortlist": "Guaranteed K-shortlist",
        "explicit-k-exclusion": "Explicit K-exclusion",
        "confidence-augmented-point": "Confidence-augmented point",
    }
    channels: dict[str, dict[str, Any]] = {}
    for row in rows:
        channels.setdefault(str(row["channel_id"]), row)

    def parameter_label(row: dict[str, Any]) -> str:
        parts = []
        if row["parameter_k"] is not None:
            parts.append(f"K={row['parameter_k']}")
        parameters = ", ".join(
            f"{str(key).replace('_', ' ')}={value}" for key, value in row["parameters"].items()
        )
        if parameters:
            parts.append(parameters)
        return "; ".join(parts) or str(row["channel_id"])

    family_options = "".join(
        f'<option value="{html.escape(family, quote=True)}"{" selected" if family == "symmetric-noisy-point" else ""}>{html.escape(family_names[family])}</option>'
        for family in families
    )
    target_options = "".join(
        f'<option value="{target}"{" selected" if target == 4 else ""}>M={target}</option>'
        for target in (3, 4, 5)
    )
    agent_options = "".join(
        f'<option value="{agents}"{" selected" if agents == 3 else ""}>N={agents}</option>'
        for agents in (2, 3, 4)
    )
    parameter_options = "".join(
        '<option value="{channel}" data-family="{family}" data-targets="{targets}"{selected}>{label}</option>'.format(
            channel=html.escape(channel_id, quote=True),
            family=html.escape(str(row["family"]), quote=True),
            targets=row["targets"],
            selected=" selected" if channel_id == "point-m4-p1of2" else "",
            label=html.escape(parameter_label(row)),
        )
        for channel_id, row in sorted(
            channels.items(),
            key=lambda item: (
                families.index(str(item[1]["family"])),
                int(item[1]["targets"]),
                item[0],
            ),
        )
    )
    step_options = "".join(
        f'<option value="{step}">s={step}→{step + 1}</option>' for step in (1, 2, 3)
    )
    budget_options = "".join(
        f'<option value="{budget}">L={budget}</option>' for budget in (1, 2, 3, 4)
    )

    def attributes(row: dict[str, Any]) -> str:
        values = {
            "frontier-row": "",
            "family": row["family"],
            "targets": row["targets"],
            "agents": row["agents"],
            "channel": row["channel_id"],
            "q": row["q"],
            "threshold": row["rescue_threshold"],
            "private": row["private_discovery"],
            "pooled-profile": "|".join(row["pooled_accuracy"]),
            "error-profile": "|".join(row["pooled_error"]),
            "discovery-profile": "|".join(row["sharing_discovery"]),
            "increment-profile": "|".join(row["sharing_increments"]),
            "ratio-profile": "|".join(
                "zero-error" if value is None else value for value in row["error_contraction_ratio"]
            ),
            "budget-profile": "|".join(row["action_budget_profile"]),
            "recovery-budget": row["recovery_budget"],
            "sharing-class": row["sharing_class"],
            "full-class": row["full_sharing_class"],
        }
        return " ".join(
            f'data-{key}="{html.escape(str(value), quote=True)}"' for key, value in values.items()
        )

    table_rows = "".join(
        '<tr {attrs}><th scope="row">{channel}</th><td>{family}</td><td>{targets}</td><td>{agents}</td><td>{q}</td><td>{private}</td><td>{consensus}</td><td>{sharing}</td><td>{full}</td><td>{budget}</td></tr>'.format(
            attrs=attributes(row),
            channel=html.escape(str(row["channel_id"])),
            family=html.escape(family_names[str(row["family"])]),
            targets=row["targets"],
            agents=row["agents"],
            q=html.escape(str(row["q"])),
            private=html.escape(str(row["private_discovery"])),
            consensus=html.escape(str(row["pooled_accuracy"][-1])),
            sharing=html.escape(str(row["sharing_class"])),
            full=html.escape(str(row["full_sharing_class"])),
            budget=row["recovery_budget"],
        )
        for row in rows
    )
    default = next(
        row for row in rows if row["channel_id"] == "point-m4-p1of2" and row["agents"] == 3
    )

    def percent(value: str) -> str:
        rendered = f"{float(Fraction(value)) * 100:.1f}".rstrip("0").rstrip(".")
        return f"{rendered}%"

    def metric(label: str, key: str, value: str) -> str:
        return f'<article class="metric-card" data-frontier-output="{key}"><span>{label}</span><strong>{percent(value)}</strong><code class="exact-value">{html.escape(value)}</code></article>'

    discovery_points = "".join(
        f'<div class="profile-point" data-frontier-point="discovery" data-index="{index}"><strong>s={index}</strong><div class="profile-bar" data-frontier-bar></div><span class="profile-value" data-frontier-value>—</span></div>'
        for index in range(1, 5)
    )
    pooled_points = "".join(
        f'<div class="profile-point" data-frontier-point="pooled" data-index="{index}"><strong>s={index}</strong><div class="profile-bar" data-frontier-bar></div><span class="profile-value" data-frontier-value>—</span></div>'
        for index in range(1, 5)
    )
    budget_points = "".join(
        f'<div class="profile-point" data-frontier-point="budget" data-index="{index}"><strong>L={index}</strong><div class="profile-bar" data-frontier-bar></div><span class="profile-value" data-frontier-value>—</span></div>'
        for index in range(1, 5)
    )
    metrics = "".join(
        [
            metric("Direct accuracy q", "q", str(default["q"])),
            metric("Private discovery P_N", "private", str(default["private_discovery"])),
            metric("Pooled accuracy C_s", "pooled", str(default["pooled_accuracy"][0])),
            metric("Discovery G_s", "discovery", str(default["sharing_discovery"][0])),
            metric("Adjacent increment", "increment", str(default["sharing_increments"][0])),
            metric("Error contraction ρ_s", "ratio", str(default["error_contraction_ratio"][0])),
            metric("Rescue threshold 1−q", "threshold", str(1 - Fraction(default["q"]))),
            metric("Pooled value V_L", "budget-value", str(default["action_budget_profile"][0])),
        ]
    )
    class_metrics = f'<article class="metric-card"><span>Recovery budget L*</span><strong data-frontier-text="recovery-budget">{default["recovery_budget"]}</strong></article><article class="metric-card"><span>Sharing-curve class</span><strong data-frontier-text="sharing-class">{html.escape(str(default["sharing_class"]))}</strong></article><article class="metric-card"><span>Full-sharing class</span><strong data-frontier-text="full-class">{html.escape(str(default["full_sharing_class"]))}</strong></article>'
    claim_links = " · ".join(f'<a href="../claims.html#{claim}">{claim}</a>' for claim in claims)
    body = f"""<header class="page-hero"><p class="eyebrow">Interactive exact-output model · DD-021</p><h1>General Sharing Frontier Lab</h1><p class="lede">Select one immutable channel scenario, a sharing step, and a centralized pooled action budget. Percentages lead; exact fractions remain attached to every probability.</p></header><section class="content-section prose"><h2>The decision boundary</h2><p class="identity">share one more signal iff ρ<sub>s</sub> = e<sub>s+1</sub>/e<sub>s</sub> &lt; 1−q</p><p>Below the threshold, aggregation outruns the independent rescue action that sharing removes. Top-L recovery assumes centralized authority to choose distinct posterior-leading targets.</p></section><section class="lab" data-frontier-lab><fieldset class="lab-controls"><legend>Choose an exact registered scenario</legend><div><label for="frontier-family">Channel family</label><select id="frontier-family">{family_options}</select></div><div><label for="frontier-targets">Targets</label><select id="frontier-targets">{target_options}</select></div><div><label for="frontier-agents">Agents</label><select id="frontier-agents">{agent_options}</select></div><div><label for="frontier-parameter">Registered parameter</label><select id="frontier-parameter">{parameter_options}</select></div><div><label for="frontier-step">Sharing step</label><select id="frontier-step">{step_options}</select></div><div><label for="frontier-budget">Pooled action budget</label><select id="frontier-budget">{budget_options}</select></div></fieldset><div class="lab-actions"><button type="button" class="filter-button" data-frontier-reset>Reset</button><a href="../data/labs/general-sharing-frontier.json">Download Lab data</a></div><p id="frontier-status" class="callout" aria-live="polite">Showing the exact M=4, N=3 half-accurate point scenario.</p><div class="metric-grid compact">{metrics}{class_metrics}</div><section class="profile-panel"><h2>Discovery G<sub>s</sub></h2><p class="visual-summary">The selected step is marked; every bar is an immutable exact value.</p><div class="profile-plot" role="img" aria-label="Exact discovery profile" data-frontier-chart="discovery">{discovery_points}</div></section><section class="profile-panel"><h2>Pooled accuracy C<sub>s</sub> and rescue threshold</h2><p class="visual-summary" data-frontier-threshold>The threshold is 1−q.</p><div class="profile-plot" role="img" aria-label="Exact pooled accuracy profile with error-contraction threshold" data-frontier-chart="pooled">{pooled_points}</div></section><section class="profile-panel"><h2>Centralized action-budget recovery V<sub>L</sub></h2><p class="visual-summary" data-frontier-recovery>Selected budget and recovery threshold are marked.</p><div class="profile-plot" role="img" aria-label="Exact centralized pooled action-budget profile" data-frontier-chart="budget">{budget_points}</div></section></section><noscript><p class="callout">JavaScript is off. All 177 exact scenarios remain visible below, with direct links to the immutable data.</p></noscript><details class="technical-details complete-data"><summary>Complete exact table — 177 scenarios</summary><table class="matrix"><caption>Complete DD-021 General Sharing Frontier registry</caption><thead><tr><th>Channel</th><th>Family</th><th>M</th><th>N</th><th>q</th><th>P<sub>N</sub></th><th>C<sub>N</sub></th><th>Sharing class</th><th>Full-sharing class</th><th>L*</th></tr></thead><tbody>{table_rows}</tbody></table></details><section class="content-section prose"><h2>Evidence boundary and provenance</h2><p>The Lab selects rows from the sole exact run; it does not simulate, interpolate, or change claim status. The absent mixed curve is a bounded null over the declared registry.</p><p>{claim_links} · <a href="{REPOSITORY_URL}/blob/main/results/verified/{DD021_RUN}/manifest.json">{DD021_RUN}</a></p><p><a href="../data/general-sharing-frontier/registry.json">Download the exact registry</a> · <a href="../data/general-sharing-frontier/minimal-witnesses.json">Download minimal witnesses</a> · <a href="../data/general-sharing-frontier/channels.json">Download channel laws</a></p></section>"""
    _write(
        output,
        "labs/general-sharing-frontier.html",
        _page(
            "General Sharing Frontier Lab",
            "Explore exact error contraction, sharing regimes, and action-budget recovery in DD-021.",
            body,
            "labs/general-sharing-frontier.html",
        ),
    )


def _build_relationship_registry(
    root: Path,
    output: Path,
    studies: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    runs: list[dict[str, Any]],
    publications: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate presentation relations and add evidence-owned reverse edges."""

    source = _read_yaml(root / "site/content/relations.yml")
    if source.get("schema_version") != 1:
        raise RuntimeError("invalid relationship registry schema")
    configured = source.get("studies")
    programs = source.get("programs")
    families = source.get("theorem_families")
    contextual_routes = source.get("contextual_routes", {})
    if (
        not isinstance(configured, dict)
        or not isinstance(programs, dict)
        or not isinstance(families, dict)
        or not isinstance(contextual_routes, dict)
    ):
        raise RuntimeError("relationship registry requires programs, theorem families, and studies")
    for route, targets in contextual_routes.items():
        if (
            not isinstance(route, str)
            or not isinstance(targets, list)
            or any(not isinstance(target, str) for target in targets)
            or not (output / route).is_file()
        ):
            raise RuntimeError(f"invalid contextual relation: {route}")
        route_source = (output / route).read_text(encoding="utf-8")
        for target in targets:
            if not (output / target).is_file():
                raise RuntimeError(f"missing contextual relation target: {route}/{target}")
            target_source = (output / target).read_text(encoding="utf-8")
            if target not in route_source or route not in target_source:
                raise RuntimeError(f"contextual relation is not bidirectional: {route}/{target}")

    studies_by_id = {str(study["id"]): study for study in studies}
    if set(configured) != set(studies_by_id):
        missing = sorted(set(studies_by_id) - set(configured))
        extra = sorted(set(configured) - set(studies_by_id))
        raise RuntimeError(
            f"relationship registry study mismatch: missing={missing}, extra={extra}"
        )
    claims_by_id = {str(claim["id"]): claim for claim in claims}
    runs_by_id = {str(run["run_id"]): run for run in runs}
    papers_by_slug = {str(paper["slug"]): paper for paper in publications}
    result_source = _read_yaml(root / "site/content/results.yml")
    results_by_id = {
        str(result["result_id"]): result for result in result_source.get("results", [])
    }
    benchmark_document = json.loads(
        (output / "data/benchmark/tasks.json").read_text(encoding="utf-8")
    )
    benchmark_tasks = benchmark_document.get("tasks", [])
    tasks_by_id = {str(task["task_id"]): task for task in benchmark_tasks}

    claim_owner = {claim_id: str(claim["study_id"]) for claim_id, claim in claims_by_id.items()}
    task_owners: dict[str, set[str]] = {study_id: set() for study_id in studies_by_id}
    for task_id, task in tasks_by_id.items():
        for claim_id in task.get("reference_claims", []):
            if claim_id not in claim_owner:
                raise RuntimeError(f"benchmark task {task_id} references missing claim {claim_id}")
            task_owners[claim_owner[claim_id]].add(task_id)
        task_owners["DD-010"].add(task_id)

    relations: list[dict[str, Any]] = []
    for study_id, configured_relation in configured.items():
        if not isinstance(configured_relation, dict):
            raise RuntimeError(f"invalid relation for {study_id}")
        program = configured_relation.get("program")
        family = configured_relation.get("theorem_family")
        if program not in programs or family not in families:
            raise RuntimeError(f"missing program or theorem family for {study_id}")
        for field in (
            "result_ids",
            "lab_slugs",
            "paper_slugs",
            "experiment_routes",
            "data_routes",
        ):
            value = configured_relation.get(field, [])
            if not isinstance(value, list) or len(value) != len(set(value)):
                raise RuntimeError(f"duplicate or invalid {field} for {study_id}")
            if any(
                not isinstance(item, str) or re.search(r"(?:^/|\.\.|file:|/Users/)", item)
                for item in value
            ):
                raise RuntimeError(f"unsafe {field} for {study_id}")

        result_ids = [str(value) for value in configured_relation.get("result_ids", [])]
        for result_id in result_ids:
            result = results_by_id.get(result_id)
            if result is None or result.get("study_id") != study_id:
                raise RuntimeError(f"inconsistent result ownership: {study_id}/{result_id}")
        lab_slugs = [str(value) for value in configured_relation.get("lab_slugs", [])]
        paper_slugs = [str(value) for value in configured_relation.get("paper_slugs", [])]
        experiment_routes = [
            str(value) for value in configured_relation.get("experiment_routes", [])
        ]
        data_routes = [str(value) for value in configured_relation.get("data_routes", [])]
        for slug in lab_slugs:
            if not (output / f"labs/{slug}.html").is_file():
                raise RuntimeError(f"missing related Lab: {study_id}/{slug}")
        for slug in paper_slugs:
            if slug not in papers_by_slug:
                raise RuntimeError(f"missing related paper: {study_id}/{slug}")
        for route in experiment_routes + data_routes:
            if not (output / route).is_file():
                raise RuntimeError(f"missing related route: {study_id}/{route}")

        study = studies_by_id[study_id]
        claim_ids = [str(value) for value in study["claim_ids"]]
        run_ids = [str(value) for value in study["run_ids"]]
        for claim_id in claim_ids:
            if claim_id not in claims_by_id or claim_owner[claim_id] != study_id:
                raise RuntimeError(f"inconsistent claim ownership: {study_id}/{claim_id}")
        for run_id in run_ids:
            if run_id not in runs_by_id:
                raise RuntimeError(f"missing related run: {study_id}/{run_id}")
        related_studies = sorted(
            other_id
            for other_id, other in configured.items()
            if other_id != study_id and other.get("theorem_family") == family
        )
        relations.append(
            {
                "study_id": study_id,
                "program": str(program),
                "theorem_family": str(family),
                "related_studies": related_studies,
                "result_ids": result_ids,
                "lab_slugs": lab_slugs,
                "paper_slugs": paper_slugs,
                "benchmark_task_ids": sorted(task_owners[study_id]),
                "experiment_routes": experiment_routes,
                "claim_ids": claim_ids,
                "run_ids": run_ids,
                "data_routes": data_routes,
            }
        )

    registry = {
        "schema_version": 1,
        "source": "site/content/relations.yml",
        "programs": programs,
        "theorem_families": families,
        "contextual_routes": contextual_routes,
        "relations": relations,
        "entity_counts": {
            "programs": len(programs),
            "theorem_families": len(families),
            "studies": len(studies),
            "findings": len(results_by_id),
            "labs": len({slug for relation in relations for slug in relation["lab_slugs"]}),
            "papers": len({slug for relation in relations for slug in relation["paper_slugs"]}),
            "benchmark_tasks": len(tasks_by_id),
            "experiment_modules": len(
                {route for relation in relations for route in relation["experiment_routes"]}
            ),
            "claims": len(
                {claim_id for relation in relations for claim_id in relation["claim_ids"]}
            ),
            "runs": len({run_id for relation in relations for run_id in relation["run_ids"]}),
            "public_data": len(
                {route for relation in relations for route in relation["data_routes"]}
            ),
        },
    }
    _write(output, "data/relations.json", json.dumps(registry, indent=2, sort_keys=True) + "\n")
    return registry


def _inject_relationship_panels(
    root: Path,
    output: Path,
    registry: dict[str, Any],
    studies: list[dict[str, Any]],
    publications: list[dict[str, Any]],
) -> None:
    """Render contextual reverse links from the validated relation graph."""

    studies_by_id = {str(study["id"]): study for study in studies}
    papers_by_slug = {str(paper["slug"]): paper for paper in publications}
    results_source = _read_yaml(root / "site/content/results.yml")
    results_by_id = {
        str(result["result_id"]): result for result in results_source.get("results", [])
    }
    programs = registry["programs"]
    families = registry["theorem_families"]
    relations = registry["relations"]
    route_relations: dict[str, list[dict[str, Any]]] = {}

    def add(route: str, relation: dict[str, Any]) -> None:
        route_relations.setdefault(route, []).append(relation)

    for relation in relations:
        study = studies_by_id[str(relation["study_id"])]
        add(f"research/{study['slug']}.html", relation)
        for slug in relation["lab_slugs"]:
            add(f"labs/{slug}.html", relation)
            if slug == "audience-design":
                add("labs/audience.html", relation)  # preserved legacy route for the same Lab
        for slug in relation["paper_slugs"]:
            add(str(papers_by_slug[slug]["detail"]), relation)
        for route in relation["experiment_routes"]:
            add(route, relation)
        if relation["benchmark_task_ids"]:
            add("benchmark/tasks.html", relation)
            add("benchmark/results.html", relation)

    def unique(items: list[tuple[str, str]]) -> list[tuple[str, str]]:
        seen: set[str] = set()
        values: list[tuple[str, str]] = []
        for item in items:
            if item[0] not in seen:
                seen.add(item[0])
                values.append(item)
        return values

    for route, related in route_relations.items():
        depth = len(Path(route).parts) - 1
        prefix = "../" * depth
        is_study = route.startswith("research/")
        title = (
            "Where this work appears"
            if is_study
            else "Related evidence"
            if route.startswith("labs/")
            else "Supporting research"
            if route.startswith(("benchmark/", "experiment-kit/"))
            else "Related research"
        )
        identifiers = sorted({str(relation["study_id"]) for relation in related})
        program_family = unique(
            [
                (
                    f"{prefix}program.html"
                    + (
                        f"#{families[relation['theorem_family']]['synthesis_anchor']}"
                        if families[relation["theorem_family"]].get("synthesis_anchor")
                        else ""
                    ),
                    f"{programs[relation['program']]['label']} · {families[relation['theorem_family']]['label']}",
                )
                for relation in related
            ]
        )
        study_links = unique(
            [
                (
                    f"{prefix}research/{studies_by_id[study_id]['slug']}.html",
                    f"{study_id} — {studies_by_id[study_id]['title']}",
                )
                for study_id in identifiers
                if not (is_study and route.endswith(f"{studies_by_id[study_id]['slug']}.html"))
            ]
        )
        related_study_links = unique(
            [
                (
                    f"{prefix}research/{studies_by_id[study_id]['slug']}.html",
                    f"{study_id} — {studies_by_id[study_id]['title']}",
                )
                for relation in related
                for study_id in relation["related_studies"]
                if study_id not in identifiers
            ]
        )
        result_links = unique(
            [
                (f"{prefix}results.html#{result_id}", str(results_by_id[result_id]["title"]))
                for relation in related
                for result_id in relation["result_ids"]
            ]
        )
        lab_links = unique(
            [
                (f"{prefix}labs/{slug}.html", f"{slug.replace('-', ' ').title()} Lab")
                for relation in related
                for slug in relation["lab_slugs"]
                if route != f"labs/{slug}.html"
            ]
        )
        paper_links = unique(
            [
                (f"{prefix}{papers_by_slug[slug]['detail']}", str(papers_by_slug[slug]["title"]))
                for relation in related
                for slug in relation["paper_slugs"]
                if route != papers_by_slug[slug]["detail"]
            ]
        )
        task_links = unique(
            [
                (f"{prefix}benchmark/tasks.html#{task_id}", task_id)
                for relation in related
                for task_id in relation["benchmark_task_ids"]
            ]
        )
        experiment_links = unique(
            [
                (
                    f"{prefix}{experiment_route}",
                    experiment_route.replace("experiment-kit/", "")
                    .replace(".html", "")
                    .replace("-", " ")
                    .title(),
                )
                for relation in related
                for experiment_route in relation["experiment_routes"]
                if route != experiment_route
            ]
        )
        claim_links = unique(
            [
                (f"{prefix}claims.html#{claim_id}", claim_id)
                for relation in related
                for claim_id in relation["claim_ids"]
            ]
        )
        run_links = unique(
            [
                (f"{REPOSITORY_URL}/blob/main/results/verified/{run_id}/manifest.json", run_id)
                for relation in related
                for run_id in relation["run_ids"]
            ]
        )
        data_links = unique(
            [
                (f"{prefix}{data_route}", data_route.rsplit("/", 1)[-1])
                for relation in related
                for data_route in relation["data_routes"]
            ]
        )

        groups = [
            ("Program / theorem family", program_family),
            (
                "Studies used" if not is_study else "Related studies",
                study_links + related_study_links,
            ),
            ("Findings", result_links),
            ("Explore interactively", lab_links),
            ("Papers", paper_links),
            ("Benchmark tasks", task_links),
            ("Experiment Kit", experiment_links),
            ("Claims", claim_links),
            ("Evidence runs", run_links),
            ("Public data", data_links),
        ]
        rendered_groups = "".join(
            "<article><h3>{}</h3><ul>{}</ul></article>".format(
                html.escape(label),
                "".join(
                    f'<li><a href="{html.escape(href, quote=True)}">{html.escape(text)}</a></li>'
                    for href, text in links
                ),
            )
            for label, links in groups
            if links
        )
        panel_id = ' id="explore"' if is_study else ""
        panel = f'<section class="content-section related-resources"{panel_id}><p class="eyebrow">Relationship map</p><h2>{html.escape(title)}</h2><div class="related-grid">{rendered_groups}</div><p class="quiet-meta"><a href="{prefix}data/relations.json">Download the validated relationship registry</a></p></section>'
        page = output / route
        source = page.read_text(encoding="utf-8")
        if "</main>" not in source:
            raise RuntimeError(f"cannot inject relationship panel: {route}")
        page.write_text(source.replace("</main>", panel + "</main>", 1), encoding="utf-8")


def _render(
    root: Path,
    output: Path,
    studies: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    claims_by_id: dict[str, dict[str, Any]],
    runs: list[dict[str, Any]],
    publications: list[dict[str, Any]],
) -> list[dict[str, str]]:
    relation_source = _read_yaml(root / "site/content/relations.yml")
    relation_config = relation_source["studies"]
    cards = "".join(_study_card(study, relation_config[study["id"]]) for study in studies)
    canonical = _canonical_data(_passing_baseline(root))
    metrics = canonical["metrics"]
    joint_summary = json.loads(
        (root / "results/verified" / DD006B_RUN / "outputs/joint-mechanism-summary.json").read_text(
            encoding="utf-8"
        )
    )
    atlas_summary = json.loads(
        (root / "results/verified" / DD009_RUN / "outputs/atlas-summary.json").read_text(
            encoding="utf-8"
        )
    )
    home = f"""<header class="home-hero"><div class="hero-copy"><p class="eyebrow">Collective search under dispersed information</p><h1>Distributed Discovery</h1><p class="tagline">How groups turn evidence into portfolios of action.</p><p class="hero-hook">Better shared information can produce worse collective discovery.</p><p class="lede">A group can improve its best guess and still waste its attempts by sending everyone to the same place. This project studies how evidence, roles, incentives, and timing shape a portfolio of search actions.</p><div class="actions"><a class="button primary" href="https://yoheinakajima.github.io/shared-discovery-paradox/">See the paradox</a><a class="button" href="research.html">Explore the research</a><a class="text-link" href="program.html">See the program map <span aria-hidden="true">→</span></a><a class="text-link" href="labs.html">Browse Labs <span aria-hidden="true">→</span></a><a class="text-link" href="publications.html">Read papers <span aria-hidden="true">→</span></a></div></div><aside class="paradox-panel" aria-labelledby="paradox-heading"><p class="eyebrow">Evidence is only the first step</p><h2 id="paradox-heading">Same clues. Different ways to search.</h2><p>Pooling improves the group’s ranking, but a one-answer rule compresses the action portfolio.</p><div class="metric-grid compact"><article class="metric-card consensus"><span>One shared answer</span><strong>{html.escape(str(metrics["consensus"]))}</strong></article><article class="metric-card private"><span>Private clue-following</span><strong>{html.escape(str(metrics["private"]))}</strong></article><article class="metric-card planner"><span>Coordinated portfolio</span><strong>{html.escape(str(metrics["planner"]))}</strong></article></div><p class="quiet-meta">Discovery probabilities from run <code>{html.escape(str(canonical["source_run_id"]))}</code>. <a href="research/dd-000.html">Scope and evidence</a>.</p></aside></header><section class="content-section" aria-labelledby="process-heading"><p class="eyebrow">How the system works</p><h2 id="process-heading">From evidence to discovery</h2><p class="section-intro">A discovery architecture determines more than what a group knows. It shapes who sees evidence, which actions are taken, and what the group learns next.</p><ol class="process-grid"><li><span>01</span><strong>Acquire evidence</strong><small>Choose sources and measurements.</small></li><li><span>02</span><strong>Share evidence</strong><small>Decide who can see which signals.</small></li><li><span>03</span><strong>Choose actions</strong><small>Spread attempts across the search space.</small></li><li><span>04</span><strong>Learn and adapt</strong><small>Use outcomes to update the next move.</small></li><li><span>05</span><strong>Reward discovery</strong><small>Align reporting, attention, and effort.</small></li><li><span>06</span><strong>Measure outcomes</strong><small>Track coverage, quality, and discovery.</small></li></ol></section><section class="content-section" aria-labelledby="findings-heading"><p class="eyebrow">Key findings</p><h2 id="findings-heading">Where architecture changes the result</h2><div class="card-grid finding-grid"><article class="card result-card"><p class="card-kicker">Shared Discovery Paradox</p><h3>One better answer can produce fewer discoveries.</h3><p><strong>{html.escape(str(metrics["consensus"]))}</strong> discovery under one shared answer in the canonical fixture.</p><a href="https://yoheinakajima.github.io/shared-discovery-paradox/">See the interactive guide <span aria-hidden="true">→</span></a></article><article class="card result-card"><p class="card-kicker">Common-Source Trap</p><h3>Many reports can still come from one source.</h3><p><strong>p(1−p)/N</strong> is the exact all-common trap width in the frozen model.</p><a href="publications/common-source-trap.html">Read the paper <span aria-hidden="true">→</span></a></article><article class="card result-card"><p class="card-kicker">Truthful discovery mechanisms</p><h3>Rewards can support truthful, differentiated action.</h3><p><strong>{html.escape(str(joint_summary["strict_rows"]))}</strong> strict rows in the registered exact mechanism class.</p><a href="research/dd-006b.html">Open the study <span aria-hidden="true">→</span></a></article><article class="card result-card"><p class="card-kicker">Architecture Atlas</p><h3>Coherent designs reveal real tradeoffs.</h3><p><strong>{html.escape(str(atlas_summary["pareto_cells"]))}</strong> nondominated cells in the bounded synthetic Atlas.</p><a href="labs/atlas.html">Explore the Atlas <span aria-hidden="true">→</span></a></article></div></section><section class="content-section" aria-labelledby="explore-heading"><p class="eyebrow">Explore the work</p><h2 id="explore-heading">Choose your depth</h2><div class="card-grid entry-grid"><article class="card entry-card"><h3><a href="research.html">Research</a></h3><p>Browse every completed, active, and planned study.</p></article><article class="card entry-card"><h3><a href="labs.html">Labs</a></h3><p>Change inputs and inspect precomputed model behavior.</p></article><article class="card entry-card"><h3><a href="publications.html">Papers</a></h3><p>Read the long-form arguments and validated artifacts.</p></article><article class="card entry-card"><h3><a href="benchmark.html">Benchmark</a></h3><p>Compare search strategies on compatible exact tasks.</p></article></div></section><section class="principle"><p>Share the evidence. <strong>Diversify the actions.</strong></p></section>"""
    home = home.replace(
        '</div></section><section class="content-section" aria-labelledby="explore-heading">',
        """</div></section><section class="content-section" aria-labelledby="attention-finding">
        <p class="eyebrow">Key finding · The Incentive to Ignore</p>
        <h2 id="attention-finding">One reader can beat a broadcast.</h2>
        <article class="card result-card"><p>In the frozen shared-versus-private action class, the first reader can improve discovery while duplicate shared-signal use reduces it.</p>
        <a href="publications/incentive-to-ignore.html">Read the paper <span aria-hidden="true">→</span></a></article>
        </section><section class="content-section" aria-labelledby="explore-heading">""",
        1,
    )
    home = home.replace(
        '</section><section class="content-section" aria-labelledby="explore-heading">',
        """</section><section class="content-section" aria-labelledby="threshold-finding">
        <p class="eyebrow">Key finding · Threshold Discovery</p>
        <h2 id="threshold-finding">Form the smallest viable teams, then diversify the teams.</h2>
        <article class="card result-card"><p>When candidates open only after a minimum team forms, too little overlap strands effort and too much overlap crowds the portfolio.</p>
        <a href="publications/threshold-discovery.html">Read the paper <span aria-hidden="true">→</span></a></article>
        </section><section class="content-section" aria-labelledby="explore-heading">""",
        1,
    )
    home = home.replace(
        '<section class="principle"><p>Share the evidence. <strong>Diversify the actions.</strong></p></section>',
        '<section class="principle"><p>Share the evidence. <strong>Diversify the actions.</strong></p><p>When actions require teams, form the smallest viable teams and diversify those teams.</p></section>',
        1,
    )
    home = home.replace(
        '<a class="button primary" href="https://yoheinakajima.github.io/shared-discovery-paradox/">See the paradox</a>',
        '<a class="button primary" href="start-here.html">Start with three results</a>',
        1,
    )
    _write(
        output,
        "index.html",
        _page(
            "Distributed Discovery",
            "How groups and multi-agent systems turn evidence into portfolios of action.",
            home,
            "index.html",
        ),
    )
    start_here = """<header class="page-hero"><p class="eyebrow">Start Here — Three Results</p><h1>Three steps into Distributed Discovery</h1><p class="lede">A contextual reading path from the atomic paradox to strategic attention and the sharing frontier. The order is editorial; evidence status remains in the claim ledger.</p></header>
<section class="card-grid paper-grid">
<article class="card"><p class="eyebrow">1 · Canonical upstream entry</p><h2>Shared Discovery Paradox</h2><p><strong>Question:</strong> Can better pooled ranking produce worse group discovery?</p><p><strong>Title result:</strong> in the atomic fixture, one pooled answer can compress several searches into duplication.</p><p><strong>Strongest limitation:</strong> the separation depends on the declared signal, action, and protocol classes.</p><p><strong>Evidence:</strong> sourced upstream exact result. <strong>Status:</strong> canonical upstream entry; no submission or peer-review status represented here.</p><p><a href="https://yoheinakajima.github.io/shared-discovery-paradox/">Read the anchor</a> · <a href="research/dd-000.html">Study</a> · <a href="claims.html#DD-C-0005">Claim</a> · <a href="evidence.html">Evidence</a> · <a href="publications/incentive-to-ignore.html">Next paper</a></p></article>
<article class="card"><p class="eyebrow">2 · Strategic-attention family</p><h2>The Incentive to Ignore</h2><p><strong>Question:</strong> Who should use a shared clue when independent private action routes remain?</p><p><strong>Title result:</strong> one shared-clue reader maximizes discovery in the frozen role class.</p><p><strong>Strongest limitation:</strong> unrestricted constant territorial policies can escape the evidence-responsive class.</p><p><strong>Evidence:</strong> analytic theorems plus independently reproduced bounded classifications. <strong>Status:</strong> working paper; not submitted, not peer reviewed, no DOI.</p><p><a href="publications/incentive-to-ignore.html">Read the paper</a> · <a href="research/dd-012.html">Study</a> · <a href="claims.html#DD-C-0059">Claim</a> · <a href="evidence.html">Evidence</a> · <a href="publications/information-sharing-frontier.html">Next paper</a></p></article>
<article class="card"><p class="eyebrow">3 · Sharing-frontier family</p><h2>When Does Information Sharing Improve Decentralized Discovery?</h2><p><strong>Question:</strong> When does aggregation improve faster than sharing removes independent rescue?</p><p><strong>Title result:</strong> a residual-error criterion determines the sign of an adjacent sharing step under the registered rescue protocol.</p><p><strong>Strongest limitation:</strong> the decentralized positive interval is selection-dependent; it is not an every-equilibrium theorem.</p><p><strong>Evidence:</strong> analytic identities/theorems, independently reproduced bounded classifications, and a bounded null. <strong>Status:</strong> working paper; not submitted, not peer reviewed, no DOI.</p><p><a href="publications/information-sharing-frontier.html">Read the paper</a> · <a href="research/dd-021.html">Study</a> · <a href="claims.html#DD-C-0097">Claim</a> · <a href="evidence.html">Evidence</a> · <a href="publications/common-source-trap.html">Next theorem-family paper</a></p></article>
</section>
<section class="content-section prose"><h2>Continue through the canon</h2><p><a href="publications/common-source-trap.html">Common-Source Trap</a> · <a href="publications/threshold-discovery.html">Threshold Discovery</a> · <a href="publications.html">notes and syntheses</a> · <a href="research.html">studies</a> · <a href="labs.html">Labs</a> · <a href="benchmark.html">DiscoveryBench</a> · <a href="methods.html">methods</a></p></section>"""
    _write(
        output,
        "start-here.html",
        _page(
            "Start Here — Three Results",
            "A three-result reading path through Distributed Discovery.",
            start_here,
            "start-here.html",
        ),
    )
    methods_body = """<header class="page-hero"><p class="eyebrow">Factual methods record</p><h1>How Phase 1 work was recorded</h1><p class="lede">Issues, branches, living plans, claim statuses, immutable runs, independent checks, corruptions, failed results, paper gates, and human owner decisions are recorded as repository practices.</p></header>
<section class="content-section prose"><h2>Boundary</h2><p>This is not a claim that the process is novel, autonomous, externally validated, peer reviewed, or sufficient for research quality. Exact computations and Monte Carlo estimates remain distinct. Internal reproduction is not external review. Failed and null results remain visible. No human study was conducted.</p><p><a href="https://github.com/yoheinakajima/distributed-discovery/blob/main/docs/methods/phase-1-research-methods.md">Read the methods record</a> · <a href="claims.html">Claim ledger</a> · <a href="evidence.html">Immutable evidence</a> · <a href="program.html">Program governance</a></p></section>"""
    _write(
        output,
        "methods.html",
        _page(
            "Methods",
            "A factual repository methods record for Phase 1.",
            methods_body,
            "methods.html",
        ),
    )
    program_body = f"""<header class="page-hero"><p class="eyebrow">How the work is organized</p><h1>The Distributed Discovery program</h1><p class="lede">Distributed Discovery is the research program on collective search under dispersed information. A discovery architecture is the formal object: the rules that turn evidence into a portfolio of search actions.</p></header>
<section class="content-section prose"><h2>One program, several output types</h2><ol><li><strong>The research program</strong> holds the complete agenda.</li><li><strong>Theorem families</strong> organize durable mathematical questions across studies.</li><li><strong>Registered studies</strong> are the smallest evidence-producing units and own models, proofs or certificates, runs, and claims.</li><li><strong>Papers</strong> are theorem-family arguments admitted by a separate editorial gate; a study does not automatically become a paper.</li><li><strong>The living synthesis</strong>, <em>The Architecture of Distributed Discovery</em>, maps the whole program without silently re-owning theorem novelty.</li><li><strong>Infrastructure</strong> includes DiscoveryBench, Labs, schemas, verifiers, the claim ledger, and audit tooling.</li></ol></section>
<section class="content-section prose" id="information-sharing-frontier"><p class="eyebrow">Completed theorem family</p><h2>From information to implemented discovery</h2><p>Program V5, <em>The Information Sharing Frontier</em>, is complete at its registered scope. Signal geometry determines what a pooled posterior can cover with one, two, or more distinct actions. Independent rescue determines whether folding another private search into a common action helps or hurts. A recovery budget then asks how many pooled actions recover a named private baseline.</p><p><strong>Positive result:</strong> DD-022 proves an exact interval where sharing raises discovery and each symmetric agent’s payoff under the declared posterior-only identical-mixing equilibrium selection.</p><p><strong>Essential limitation:</strong> that comparison does not hold across every equilibrium. Roles and signal ownership can select different portfolios, and DD-021’s full-capacity recovery theorem assumes a centralized posterior top-<code>L</code> selector. A shared posterior alone does not implement the planner.</p><p><a href="research/dd-019.html">DD-019 Signal geometry</a> · <a href="research/dd-020.html">DD-020 Independent rescue</a> · <a href="research/dd-021.html">DD-021 Centralized recovery</a> · <a href="research/dd-022.html">DD-022 Selected decentralized sharing</a> · <a href="publications/information-sharing-frontier.html">Read the working paper</a> · <a href="{REPOSITORY_URL}/blob/main/docs/theorem-spine.md">Inspect the claim-linked theorem spine</a></p></section>
<section class="content-section prose"><h2>Next open boundary</h2><p>The bounded Decentralized Recovery registration gate stopped at classical overlap: the frozen equal-sharing action game is singleton congestion, and visible sequential occupancy adds ordinary backward induction without enlarging the every-equilibrium top-two recovery region. No study, claim, run, or paper was created.</p><p>Reliable Discovery is now the next unregistered theorem program. It asks when reliable, unreliable, repeated, or overlapping actions should diversify or concentrate, and must establish content beyond classical reliability allocation before registration. The Price of Missing Provenance follows separately.</p></section>
<section class="content-section prose"><h2>How evidence status works</h2><p>Definitions, analytic theorems, exact bounded computations, independent reproductions, estimates, negative results, conjectures, and editorial recommendations remain distinct. Scientific statements link to stable claim IDs; generated numerical claims also link to immutable runs.</p><p><a href="claims.html">Inspect {len(claims)} scoped claims</a> · <a href="evidence.html">Inspect {len(runs)} passing runs</a> · <a href="research.html">Browse all {len(studies)} studies</a></p></section>
<section class="content-section prose"><h2>How the work is published</h2><p>The canonical entry paper introduces the atomic paradox. Theorem-family papers own durable mathematical questions. Working notes support intermediate or synthetic arguments. The living synthesis preserves the complete intellectual account. Reproducible studies, Labs, and DiscoveryBench expose evidence and interfaces.</p><p>No journal submission status is represented here. A validated PDF, exact run, or polished site does not by itself satisfy the paper-admission rule.</p><p><a href="publications.html">Browse working papers</a> · <a href="{REPOSITORY_URL}/blob/main/docs/research-governance.md">Read the governance source</a></p></section>"""
    program_body = program_body.replace(
        '<section class="content-section prose"><h2>Next open boundary</h2><p>The bounded Decentralized Recovery registration gate stopped at classical overlap: the frozen equal-sharing action game is singleton congestion, and visible sequential occupancy adds ordinary backward induction without enlarging the every-equilibrium top-two recovery region. No study, claim, run, or paper was created.</p><p>Reliable Discovery is now the next unregistered theorem program. It asks when reliable, unreliable, repeated, or overlapping actions should diversify or concentrate, and must establish content beyond classical reliability allocation before registration. The Price of Missing Provenance follows separately.</p></section>',
        '<section class="content-section prose"><h2>Phase boundary and hold</h2><p>Phase 1 is complete: Programs V1–V5, this Frontier, post-V5 consolidation, and the stopped decentralized-recovery overlap gate form the completed boundary. This does not mean every theorem direction is complete.</p><p>Phase 2 holds theorem-family execution. Reliable Discovery remains a major candidate but is deferred. The next substantive session is DiscoveryBench Agents v1 registration; no provider call, model run, cost, trace, private seed, or result is underway. <a href="start-here.html">Start with three results</a> · <a href="methods.html">Read the factual methods record</a>.</p></section>',
        1,
    )
    _write(
        output,
        "program.html",
        _page(
            "Program",
            "How Distributed Discovery organizes theorem families, studies, papers, synthesis, infrastructure, and evidence status.",
            program_body,
            "program.html",
        ),
    )
    program_options = "".join(
        f'<option value="{html.escape(program_id)}">{html.escape(str(details["label"]))}</option>'
        for program_id, details in relation_source["programs"].items()
    )
    family_options = "".join(
        f'<option value="{html.escape(family_id)}">{html.escape(str(details["label"]))}</option>'
        for family_id, details in relation_source["theorem_families"].items()
    )
    evidence_options = "".join(
        f'<option value="{html.escape(status)}">{html.escape(human_status(status, kind="evidence"))}</option>'
        for status in sorted({str(study["evidence_status"]) for study in studies})
    )
    research = f"""<header class="page-hero"><p class="eyebrow">Collective search under dispersed information</p><h1>Research</h1><p class="lede">Browse studies of how evidence, roles, incentives, timing, and action allocation shape collective search.</p><p><a href="program.html">See how studies fit into theorem families, papers, and the living synthesis.</a></p></header><section class="catalog" data-research-catalog><div class="research-tools"><div><label for="study-search">Search studies</label><input id="study-search" type="search" placeholder="Search by question, title, or study ID" autocomplete="off"></div><fieldset class="catalog-selects"><legend>Relationship filters</legend><div><label for="study-program">Program</label><select id="study-program"><option value="all">All programs</option>{program_options}</select></div><div><label for="study-family">Theorem family</label><select id="study-family"><option value="all">All theorem families</option>{family_options}</select></div><div><label for="study-evidence">Evidence status</label><select id="study-evidence"><option value="all">All evidence statuses</option>{evidence_options}</select></div></fieldset><div class="filter-group" aria-label="Filter studies"><button type="button" class="filter-button" data-study-filter="all" aria-pressed="true">All</button><button type="button" class="filter-button" data-study-filter="key-results" aria-pressed="false">Key results</button><button type="button" class="filter-button" data-study-filter="active" aria-pressed="false">Active</button><button type="button" class="filter-button" data-study-filter="planned" aria-pressed="false">Planned</button><button type="button" class="filter-button" data-study-filter="tools" aria-pressed="false">Tools and infrastructure</button></div><p id="study-status" class="result-count" aria-live="polite">{len(studies)} studies shown</p></div><noscript><p class="callout">JavaScript is off. All {len(studies)} studies remain visible; use browser find to search this page.</p></noscript><div class="card-grid study-grid">{cards}</div></section>"""
    research = research.replace(
        '<p><a href="program.html">See how studies fit into theorem families, papers, and the living synthesis.</a></p>',
        '<p><a href="start-here.html">Start with three results</a> · <a href="program.html">See how studies fit into theorem families, papers, and the living synthesis.</a></p>',
        1,
    )
    _write(
        output,
        "research.html",
        _page(
            "Research",
            "Studies of collective search under dispersed information, covering evidence, roles, incentives, timing, and action allocation.",
            research,
            "research.html",
        ),
    )
    for study in studies:
        _write(output, f"research/{study['slug']}.html", _study_page(study, claims_by_id))
    prominence_source = _read_yaml(root / "docs/claim-prominence.yml")
    prominence = prominence_source["claims"]
    if set(prominence) != {str(claim["id"]) for claim in claims}:
        raise RuntimeError("claim prominence registry does not match live claims")
    claim_items = "".join(
        '<article id="{id}" class="card"><p class="eyebrow">{id} · {status} · {claim_type}</p><p class="status-row"><span class="status-chip">{prominence}</span></p><h2>{short_name}</h2><p>{statement}</p><p><strong>Scope:</strong> {scope}</p><p><a href="research/dd-{suffix}.html">{study_id}</a></p></article>'.format(
            id=html.escape(str(claim["id"])),
            status=html.escape(str(claim["status"])),
            claim_type=html.escape(str(claim["claim_type"])),
            prominence=html.escape(str(prominence[str(claim["id"])]).replace("-", " ")),
            short_name=html.escape(str(claim["short_name"])),
            statement=html.escape(str(claim["statement"])),
            scope=html.escape(str(claim["scope"])),
            suffix=str(claim["study_id"])[3:].lower(),
            study_id=html.escape(str(claim["study_id"])),
        )
        for claim in claims
    )
    claims_body = f"""<header class="page-hero"><p class="eyebrow">Technical evidence</p><h1>Claims</h1><p class="lede">Stable claim anchors connect every formal statement to its scope and evidence. This is the technical ledger; start with <a href="results.html">Results</a> for the plain-language findings.</p><p class="quiet-meta">No unvalidated values are rendered as claims. Editorial prominence badges control reading role only and never change evidence status.</p></header><section class="card-grid claim-grid">{claim_items}</section>"""
    _write(
        output,
        "claims.html",
        _page(
            "Claims",
            "Stable, scoped claim ledger for Distributed Discovery.",
            claims_body,
            "claims.html",
        ),
    )
    evidence_items = "".join(
        '<article class="card evidence-card"><p class="eyebrow">{study_id} · reproducible evidence</p><h2><code>{run_id}</code></h2><p>Passed validation with {output_count} checksum-validated public-safe outputs.</p><details class="technical-details"><summary>Technical details</summary><p><a href="{repo}/blob/main/{manifest_path}">Manifest source</a></p><p>SHA-256 <code>{manifest_sha}</code></p></details></article>'.format(
            run_id=html.escape(str(run["run_id"])),
            study_id=html.escape(str(run["study_id"])),
            output_count=html.escape(str(run["output_count"])),
            repo=REPOSITORY_URL,
            manifest_path=html.escape(str(run["manifest_path"])),
            manifest_sha=html.escape(str(run["manifest_sha256"])),
        )
        for run in runs
    )
    evidence_body = f"""<header class="page-hero"><p class="eyebrow">Technical evidence</p><h1>Reproducible runs</h1><p class="lede">Only runs with passed validation, exit status zero, repository-relative paths, and checksum-validated safe outputs appear here. Failed and preliminary material is not substantive public evidence.</p></header><section class="card-grid evidence-grid">{evidence_items}</section>"""
    _write(
        output,
        "evidence.html",
        _page(
            "Evidence",
            "Safe summaries of checksum-validated immutable research runs.",
            evidence_body,
            "evidence.html",
        ),
    )
    publication_purposes = {
        "foundations": "Defines the core objects and separates information quality from action allocation.",
        "three-results": "Connects exact results on roles, disclosure, and correlated sources.",
        "discovery-institutions": "Synthesizes how evidence, assignment, incentives, and feedback interact.",
        "common-source-trap": "Explains why many reports can still behave like one source of evidence.",
        "incentive-to-ignore": "Synthesizes selective attention, audience design, and conditional evidence use.",
        "threshold-discovery": "Connects minimum viable teams, equilibrium selection, dynamic attention, and implementable team portfolios.",
        "information-sharing-frontier": "Identifies when pooled error contraction beats lost independent rescue, then separates the selected positive result from its equilibrium-selection boundary.",
    }
    publication_items = "".join(
        '<article class="card paper-card"><div class="card-meta"><span class="status-chip">{status}</span><span>{page_count} pages</span></div><h2><a href="{detail}">{title}</a></h2><p>{purpose}</p><div class="card-actions"><a class="button small" href="{download}">Download PDF</a><a href="{detail}">Paper details</a></div><p class="citation">{citation}</p><details class="technical-details"><summary>Technical details</summary><p><a href="{repo}/blob/main/{build_source}">Build source</a></p><p>SHA-256 <code>{sha256}</code></p></details></article>'.format(
            title=html.escape(str(item["title"])),
            detail=html.escape(str(item["detail"])),
            purpose=html.escape(publication_purposes[str(item["slug"])]),
            status=html.escape(human_status(item["status"], kind="publication")),
            page_count=html.escape(str(item["page_count"])),
            sha256=html.escape(str(item["sha256"])),
            download=html.escape(str(item["download"])),
            repo=REPOSITORY_URL,
            build_source=html.escape(str(item["build_source"])),
            citation=html.escape(str(item["citation"])),
        )
        for item in publications
    )
    publications_body = f"""<header class="page-hero"><p class="eyebrow">Long-form research</p><h1>Papers</h1><p class="lede">Working papers on how groups acquire, share, and convert evidence into portfolios of action.</p><p><a href="program.html">See the paper-admission rule and publication architecture.</a></p></header><section class="card-grid paper-grid">{publication_items}</section><p class="quiet-meta"><a href="data/downloads.json">Complete download checksum manifest</a></p>"""
    publications_body = publications_body.replace(
        '<p><a href="program.html">See the paper-admission rule and publication architecture.</a></p>',
        '<p><a href="start-here.html">Start with three results</a> · <a href="program.html">See the four-layer hierarchy and paper-admission rule.</a></p>',
        1,
    ).replace(
        '<p class="quiet-meta"><a href="data/downloads.json">Complete download checksum manifest</a></p>',
        '<p class="quiet-meta">All project PDFs are not submitted, not peer reviewed, and have no DOI. <a href="data/downloads.json">Complete download checksum manifest</a></p>',
        1,
    )
    _write(
        output,
        "publications.html",
        _page(
            "Papers",
            "Working papers on how groups acquire, share, and convert evidence into portfolios of action.",
            publications_body,
            "publications.html",
        ),
    )
    for item in publications:
        publication_label = human_status(item["status"], kind="publication")
        status_bits = [str(item["status"]).replace("-", " ")]
        if item["doi"]:
            status_bits.append(f"DOI {item['doi']}")
        else:
            status_bits.append("no DOI")
        if item["submitted"] is False:
            status_bits.append("not submitted")
        if item["peer_reviewed"] is False:
            status_bits.append("not peer reviewed")
        bibtex = (
            f'<h3>BibTeX</h3><pre class="bibtex-block"><code>'
            f"{html.escape(str(item['citation_bib']))}</code></pre>"
            if item["citation_bib"]
            else ""
        )
        detail_body = f"""<header class="page-hero"><p class="eyebrow">{html.escape(publication_label)}</p><h1>{html.escape(str(item["title"]))}</h1><p class="lede">{html.escape(publication_purposes[str(item["slug"])])}</p><p class="status-row"><span class="status-chip">{html.escape(publication_label)}</span><span>{html.escape(str(item["page_count"]))} pages</span></p><p><a class="button primary" href="../{html.escape(str(item["download"]))}">Download PDF</a></p></header><section class="content-section prose"><h2>Citation</h2><p>{html.escape(str(item["citation"]))}</p>{bibtex}</section><section class="content-section prose"><h2>Source and provenance</h2><p><a href="{REPOSITORY_URL}/blob/main/{html.escape(str(item["build_source"]))}">Read the build source</a> · <a href="{REPOSITORY_URL}/tree/main/papers/{html.escape(str(item["slug"]))}">Inspect validation and provenance</a></p><details class="technical-details"><summary>Technical details</summary><p>{html.escape(" · ".join(status_bits))}</p><p>The download is copied only after its SHA-256 matches the committed validation record.</p><p>SHA-256 <code>{html.escape(str(item["sha256"]))}</code></p></details></section>"""
        _write(
            output,
            str(item["detail"]),
            _page(
                str(item["title"]),
                f"Validated publication artifact and provenance for {item['title']}.",
                detail_body,
                str(item["detail"]),
            ),
        )
    open_studies = [
        study
        for study in studies
        if study["phase"] in {"registered", "queued", "active-extension", "blocked"}
    ]
    open_body = (
        '<header class="page-hero"><p class="eyebrow">Research agenda</p><h1>Open questions</h1><p class="lede">These are registered next steps, not results.</p></header><section class="card-grid study-grid">'
        + "".join(_study_card(study, relation_config[study["id"]]) for study in open_studies)
        + "</section>"
    )
    _write(
        output,
        "open-problems.html",
        _page(
            "Open Questions",
            "Registered research directions and explicit evidence boundaries.",
            open_body,
            "open-problems.html",
        ),
    )
    ideas_body = """<header class="page-hero"><p class="eyebrow">Ideas incubator</p><h1>Speculation is not evidence</h1><p class="lede">The following directions are deliberately separated from the claim ledger.</p></header><section class="content-section prose"><ul><li>Noisy or state-coupled sequential tests after DD-004’s perfect-elimination baseline.</li><li>Randomized disclosure and broader equilibrium-selection procedures after DD-002.</li><li>Higher-order report laws and expanded source palettes after DD-003.</li><li>Mechanism classes, equilibrium concepts, and observability variants outside DD-006’s registration.</li><li>Real-data work only after DD-007 privacy, identification, and ethics review.</li></ul></section>"""
    _write(
        output,
        "ideas.html",
        _page(
            "Ideas Incubator",
            "Clearly labelled speculative extensions for future research.",
            ideas_body,
            "ideas.html",
        ),
    )
    foundations_body = """<header class="page-hero"><p class="eyebrow">Foundations</p><h1>Information and action allocation</h1><p class="lede">Information aggregation is not action allocation. The program separates available evidence from the protocol that turns it into a portfolio of actions.</p></header><section class="content-section prose"><p class="identity">G<sub>B</sub>(Π; I) = V<sub>B</sub>(I) − L<sub>B</sub>(Π; I)</p><p>It is an accounting identity, not a universal monotonicity theorem. Consult the <a href="research/dd-000.html">foundations record</a> and <a href="publications.html">validated note</a> for scope and provenance.</p></section>"""
    _write(
        output,
        "foundations.html",
        _page(
            "Foundations",
            "Definitions and evidence boundaries for Distributed Discovery.",
            foundations_body,
            "foundations.html",
        ),
    )
    results_body = _results_page(root, studies, claims_by_id)
    _write(
        output,
        "results.html",
        _page(
            "Results",
            "Findings about how groups gather evidence and spread action across search.",
            results_body,
            "results.html",
        ),
    )
    applications_body = """<header class="page-hero"><p class="eyebrow">Applications</p><h1>Mappings, not results</h1><p class="lede">Science, R&amp;D, venture portfolios, and multi-agent systems can be represented as evidence, action, coverage, and feedback systems.</p></header><section class="content-section prose"><p>Each mapping needs its own action technology, objective, dependence model, and evidence standard. These translations identify objects to measure; they do not establish that results from one model transfer to a domain.</p></section>"""
    _write(
        output,
        "applications.html",
        _page(
            "Applications",
            "Scoped application mappings for Distributed Discovery.",
            applications_body,
            "applications.html",
        ),
    )
    lab_specs = [
        (
            "sequential",
            "Sequential Discovery",
            "DD-C-0045",
            "20260721T050038Z_DD-004_8ab02e7f_71d84de7c4",
            "Compare registered batch schedules; terminal discovery is held separate from actions and rounds.",
        ),
        (
            "coverage",
            "Coverage and Redundancy",
            "DD-C-0046",
            "20260721T050706Z_DD-005_be3b544c_98698dee2f",
            "Inspect why a portfolio's union value is not recovered from action labels alone.",
        ),
        (
            "mechanisms",
            "Mechanisms and Incentives",
            "DD-C-0053",
            DD006B_RUN,
            "Explore the joint proper-score, observable-action, and subsidy frontier; no arbitrary-transfer conclusion is implied.",
        ),
        (
            "audit",
            "Audit and Calibration",
            "DD-C-0049",
            "20260721T052307Z_DD-007_af4ea130_72fb89c5fc",
            "Examine synthetic recovery and the provenance conditions needed for interpretation.",
        ),
        (
            "evidence-acquisition",
            "Evidence Acquisition",
            "DD-C-0051",
            "20260721T141527Z_DD-008_0d11dc77_7e0c8f1d66",
            "Compare common and independent evidence sources in the registered two-agent source-choice fixture.",
        ),
        (
            "atlas",
            "Architecture Atlas",
            "DD-C-0054",
            DD009_RUN,
            "Compare only coherent aligned architecture cells under the registered exact metric and Pareto boundaries.",
        ),
    ]
    lab_details = {
        "threshold": (
            "Search and allocation",
            "Minimum viable team",
            "Exact discovery, viability, and crowding metrics",
            "DD-016",
        ),
        "equilibrium-selection": (
            "Search and allocation",
            "Posterior fixture, team size, and threshold",
            "Planner value, equilibrium range, multiplicity, and stability",
            "DD-017",
        ),
        "sequential": (
            "Search and allocation",
            "Batch schedule",
            "Actions, rounds, and terminal discovery",
            "DD-004",
        ),
        "coverage": (
            "Search and allocation",
            "Action portfolio",
            "Union coverage and redundancy",
            "DD-005",
        ),
        "evidence-acquisition": (
            "Information and sources",
            "Evidence source",
            "Acquisition and discovery outcomes",
            "DD-008",
        ),
        "attention": (
            "Information and sources",
            "Team, accuracy, attenders, and reward",
            "Discovery, payoffs, equilibria, and attention wedges",
            "DD-012",
        ),
        "dynamic-attention": (
            "Information and sources",
            "Team size, private/shared accuracy, and stopping objective",
            "Planner, autonomous, private, and history-hidden outcomes",
            "DD-015",
        ),
        "incremental-sharing": (
            "Information and sources",
            "Targets, agents, point accuracy or channel, and sharing step",
            "Pooled accuracy, discovery, aggregation gain, lost rescue, net increment, and profile",
            "DD-020",
        ),
        "general-sharing-frontier": (
            "Information and sources",
            "Channel family, targets, agents, parameter, sharing step, and action budget",
            "Error contraction, discovery, sharing regime, consensus class, and recovery budget",
            "DD-021",
        ),
        "coordination-free-positive-sharing": (
            "Information and sources",
            "Signal accuracy, dependence, information regime, and baseline",
            "Selected strategy, posterior, discovery, payoff, diversity, gain, and implementation gap",
            "DD-022",
        ),
        "audience-design": (
            "Information and sources",
            "Team, accuracy, and audience",
            "Binding and garbling frontiers",
            "DD-013",
        ),
        "conditional-attention": (
            "Information and sources",
            "Conditional policy profile",
            "Private-, public-, and contrarian-dominant outcomes",
            "DD-014",
        ),
        "mechanisms": (
            "Incentives and mechanisms",
            "Family, observability regime, named row, and tie role",
            "Incentive and discovery boundaries",
            "DD-006B",
        ),
        "team-mechanisms": (
            "Incentives and mechanisms",
            "Posterior fixture and mechanism",
            "Discovery, obedience, stability, budget, and multiplicity",
            "DD-018",
        ),
        "audit": (
            "Measurement and experiments",
            "Copying rate, missingness, matching error, and sample size",
            "Recovery and calibration behavior",
            "DD-007",
        ),
        "atlas": (
            "Measurement and experiments",
            "Named architecture or six registered components",
            "Metric and Pareto tradeoffs",
            "DD-009",
        ),
        "benchmark": (
            "Measurement and experiments",
            "Benchmark task",
            "Compatible strategy result vectors",
            "DD-010",
        ),
        "experiment-design": (
            "Measurement and experiments",
            "Synthetic response scenario",
            "Power and minimum detectable effects",
            "DD-011",
        ),
    }
    lab_capability = {
        "threshold": "Interactive models",
        "equilibrium-selection": "Interactive models",
        "sequential": "Data explorers",
        "evidence-acquisition": "Interactive models",
        "attention": "Interactive models",
        "dynamic-attention": "Interactive models",
        "incremental-sharing": "Interactive models",
        "general-sharing-frontier": "Interactive models",
        "coordination-free-positive-sharing": "Interactive models",
        "mechanisms": "Data explorers",
        "team-mechanisms": "Interactive models",
        "coverage": "Guided exhibits",
        "audit": "Data explorers",
        "atlas": "Data explorers",
        "benchmark": "Data explorers",
        "experiment-design": "Data explorers",
        "audience-design": "Guided exhibits",
        "conditional-attention": "Guided exhibits",
    }
    capability_label = {
        "Interactive models": "Interactive model",
        "Data explorers": "Data explorer",
        "Guided exhibits": "Guided exhibit",
    }
    generic_by_slug = {
        slug: (title, claim, description) for slug, title, claim, _, description in lab_specs
    }
    special_labs = {
        "threshold": (
            "Threshold",
            "DD-C-0074",
            "Move across all eight exact minimum-team rows in the canonical phase diagram.",
        ),
        "equilibrium-selection": (
            "Equilibrium selection",
            "DD-C-0077",
            "Inspect all 160 exact games without collapsing best, worst, or stable equilibria.",
        ),
        "attention": (
            "Attention",
            "DD-C-0060",
            "Explore exact access-gated attention profiles, payoffs, equilibria, and rewards.",
        ),
        "dynamic-attention": (
            "Dynamic attention",
            "DD-C-0080",
            "Explore every exact dynamic objective row and separate planner from autonomous behavior.",
        ),
        "incremental-sharing": (
            "Incremental sharing",
            "DD-C-0094",
            "Separate marginal aggregation gain from lost independent rescue across exact point and channel profiles.",
        ),
        "general-sharing-frontier": (
            "General sharing frontier",
            "DD-C-0097",
            "Compare exact error contraction, sharing regimes, and centralized action-budget recovery across all 177 registered scenarios.",
        ),
        "coordination-free-positive-sharing": (
            "Coordination-free positive sharing",
            "DD-C-0106",
            "Compare private and posterior-only shared symmetric equilibria across all 42 exact cells while preserving selection dependence.",
        ),
        "team-mechanisms": (
            "Team mechanisms",
            "DD-C-0084",
            "Compare all 50 exact mechanism-fixture rows across distinct implementation concepts.",
        ),
        "benchmark": (
            "DiscoveryBench",
            "DD-C-0069",
            "Filter compatible task and strategy rows without submissions or external calls.",
        ),
        "experiment-design": (
            "Experiment design",
            "DD-C-0088",
            "Filter conditional synthetic power while preserving the no-human-data boundary.",
        ),
        "audience-design": (
            "Audience design",
            "DD-C-0065",
            "Compare binding audiences and feasible precision-versus-publicity designs.",
        ),
        "conditional-attention": (
            "Conditional attention",
            "DD-C-0067",
            "Explore exact private-dominant, public-dominant, and contrarian role profiles.",
        ),
    }
    grouped_labs: list[str] = []
    for group in ("Interactive models", "Data explorers", "Guided exhibits"):
        group_cards = []
        for slug, details in lab_details.items():
            if lab_capability[slug] != group:
                continue
            title, claim, description = (special_labs | generic_by_slug)[slug]
            group_cards.append(
                f'<article class="card lab-card"><p class="eyebrow">{capability_label[group]} · {html.escape(details[0])}</p><h3><a href="labs/{slug}.html">{html.escape(title)}</a></h3><p>{html.escape(description)}</p><dl><div><dt>What can I change?</dt><dd>{html.escape(details[1])}</dd></div><div><dt>What will I see?</dt><dd>{html.escape(details[2])}</dd></div><div><dt>Supported by</dt><dd>{html.escape(details[3])}</dd></div></dl><p class="card-link"><a href="labs/{slug}.html">Open Lab <span aria-hidden="true">→</span></a></p><details class="technical-details"><summary>Technical details</summary><p><a href="claims.html#{claim}">{claim}</a> · <a href="evidence.html">Reproducible evidence</a></p></details></article>'
            )
        grouped_labs.append(
            f'<section class="lab-group"><h2>{html.escape(group)}</h2><div class="card-grid lab-grid">{"".join(group_cards)}</div></section>'
        )
    labs_body = f"""<header class="page-hero"><p class="eyebrow">Interactive explainers</p><h1>Labs</h1><p class="lede">Change inputs and inspect precomputed exact or synthetic models. Every Lab works without an external API and keeps its evidence boundary close at hand.</p></header>{"".join(grouped_labs)}"""
    _write(
        output,
        "labs.html",
        _page(
            "Labs",
            "Interactive explainers for the exact and synthetic models in the Distributed Discovery research program.",
            labs_body,
            "labs.html",
        ),
    )
    core_labs = build_core_labs(root)
    for slug, lab in core_labs.items():
        _write(
            output,
            f"labs/{slug}.html",
            _page(
                str(lab["title"]), str(lab["description"]), str(lab["body"]), f"labs/{slug}.html"
            ),
        )
        _write(
            output,
            f"data/labs/{slug}.json",
            json.dumps(lab["data"], indent=2, sort_keys=True) + "\n",
        )
    _program_v4_lab_pages(root, output)
    _incremental_sharing_pages(root, output)
    _general_sharing_pages(root, output)
    _coordination_free_sharing_pages(root, output)
    _benchmark_pages(root, output)
    _experiment_pages(root, output)
    _attention_pages(root, output)
    _audience_pages(root, output)
    _conditional_pages(root, output)
    relationship_registry = _build_relationship_registry(
        root, output, studies, claims, runs, publications
    )
    _inject_relationship_panels(root, output, relationship_registry, studies, publications)
    _write(
        output,
        "404.html",
        _page(
            "Not found",
            "The requested research-library route does not exist.",
            '<h1>Not found</h1><p>Return to the <a href="index.html">research library</a>.</p>',
            "404.html",
        ),
    )
    routes = [{"path": "index.html", "kind": "home"}]
    for path in sorted(output.glob("**/*.html")):
        relative = str(path.relative_to(output))
        if relative != "index.html":
            routes.append({"path": relative, "kind": "page"})
    return routes


def validate_site(output: Path, routes: list[dict[str, str]]) -> dict[str, Any]:
    errors: list[str] = []
    expected = {route["path"] for route in routes}
    actual = {str(path.relative_to(output)) for path in output.glob("**/*.html")}
    if expected != actual:
        errors.append("route registry does not match generated HTML")
    for relative in sorted(actual):
        page = output / relative
        source = page.read_text(encoding="utf-8")
        parser = SiteParser()
        parser.feed(source)
        if re.search(r"\{\{[A-Z_]+\}\}", source):
            errors.append(f"{relative}: unresolved template marker")
        if not {"main", "nav", "header", "footer"}.issubset(parser.tags):
            errors.append(f"{relative}: missing landmark")
        header = re.search(r'<header class="site-header".*?</header>', source, re.DOTALL)
        if header is None:
            errors.append(f"{relative}: missing global site header")
        else:
            header_source = header.group(0)
            if header_source.count("<nav ") != 1:
                errors.append(f"{relative}: expected exactly one global nav region")
            primary = re.search(r'<div class="nav-links">(.*?)</div>', header_source, re.DOTALL)
            if primary is None or primary.group(1).count("<a ") != 5:
                errors.append(f"{relative}: expected exactly five primary nav items")
            if "secondary" in header_source or "Research navigation" in header_source:
                errors.append(f"{relative}: secondary global navigation is prohibited")
        if not parser.headings or parser.headings[0] != 1:
            errors.append(f"{relative}: first heading must be h1")
        if parser.headings.count(1) != 1:
            errors.append(f"{relative}: expected exactly one h1")
        if any(
            current > previous + 1
            for previous, current in zip(parser.headings, parser.headings[1:], strict=False)
        ):
            errors.append(f"{relative}: heading hierarchy skips a level")
        if len(parser.ids) != len(parser.id_occurrences):
            errors.append(f"{relative}: duplicate element ID")
        if source.count("<table") != source.count("<caption"):
            errors.append(f"{relative}: every table requires a caption")
        if "description" not in parser.meta:
            errors.append(f"{relative}: missing description")
        if any(urlsplit(asset).scheme in {"http", "https"} for asset in parser.runtime_assets):
            errors.append(f"{relative}: external runtime asset")
        if (
            re.search(r"data-(?:(?:benchmark|experiment|audience|output)-)?lab", source)
            and "<noscript>" not in source
        ):
            errors.append(f"{relative}: interactive Lab lacks a no-JavaScript fallback")
        if relative.startswith("labs/") and "data-lab=" in source:
            errors.append(f"{relative}: generic scenario-only Lab handler is prohibited")
        if relative.startswith("labs/") and 'type="range"' in source:
            errors.append(f"{relative}: scenario-index range controls are prohibited")
        if relative.startswith("labs/") and "<select" in source:
            supported = any(
                marker in source
                for marker in (
                    "data-output-lab",
                    "data-atlas-lab",
                    "data-benchmark-lab",
                    "data-experiment-lab",
                    "data-attention-lab",
                    "data-audience-lab",
                    "data-conditional-lab",
                    "data-incremental-lab",
                    "data-frontier-lab",
                    "data-coordination-lab",
                )
            )
            if not supported:
                errors.append(f"{relative}: Lab controls lack a substantive output mapping")
        if re.search(
            r"googletagmanager|google-analytics|plausible\.io|segment\.io|mixpanel|hotjar",
            source,
            re.IGNORECASE,
        ):
            errors.append(f"{relative}: tracking or analytics reference")
        for href in parser.hrefs:
            parsed = urlsplit(href)
            if parsed.scheme in {"http", "https", "mailto"}:
                continue
            target = page if not parsed.path else (page.parent / parsed.path).resolve()
            if not target.exists():
                errors.append(f"{relative}: broken link {href}")
            elif parsed.fragment and target.suffix == ".html":
                target_parser = SiteParser()
                target_parser.feed(target.read_text(encoding="utf-8"))
                if parsed.fragment not in target_parser.ids:
                    errors.append(f"{relative}: missing fragment {href}")
        if re.search(r"(?:/Users/|file://|AKIA|ghp_)", source):
            errors.append(f"{relative}: local path or secret-like content")
    download_manifest_path = output / "data/downloads.json"
    if not download_manifest_path.is_file():
        errors.append("missing download checksum manifest")
    else:
        download_manifest = json.loads(download_manifest_path.read_text(encoding="utf-8"))
        entries = download_manifest.get("downloads", [])
        registered = {entry.get("path") for entry in entries if isinstance(entry, dict)}
        actual_downloads = {
            str(path.relative_to(output))
            for path in (output / "downloads").glob("*")
            if path.is_file()
        }
        if registered != actual_downloads:
            errors.append("download checksum manifest does not match generated downloads")
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                errors.append("invalid download checksum entry")
                continue
            download = output / entry["path"]
            if (
                not _safe_relative(entry["path"])
                or not download.is_file()
                or download.stat().st_size == 0
                or entry.get("bytes") != download.stat().st_size
                or entry.get("sha256") != _sha256(download)
            ):
                errors.append(f"invalid download checksum entry: {entry['path']}")
    stylesheet = (output / "styles.css").read_text(encoding="utf-8")
    if "prefers-reduced-motion: reduce" not in stylesheet:
        errors.append("stylesheet lacks reduced-motion behavior")
    if ":focus-visible" not in stylesheet and ":focus" not in stylesheet:
        errors.append("stylesheet lacks visible focus behavior")
    if "repeat(auto-fit, minmax(min(100%, 16rem), 1fr))" not in stylesheet:
        errors.append("stylesheet lacks responsive auto-fit card grids")
    if "grid-template-columns: repeat(7" in stylesheet or ".pipeline" in stylesheet:
        errors.append("stylesheet retains the fixed seven-column pipeline")
    if not (output / "og.png").is_file():
        errors.append("missing local social preview image")
    if errors:
        raise RuntimeError("site validation failed:\n" + "\n".join(errors))
    return {
        "schema_version": 2,
        "page_count": len(actual),
        "routes": sorted(expected),
        "internal_links_passed": True,
        "semantic_structure_passed": True,
        "public_safety_passed": True,
        "download_checksums_passed": True,
        "local_assets_passed": True,
        "no_tracking_passed": True,
        "no_javascript_fallbacks_passed": True,
        "accessibility_smoke_passed": True,
    }


def build(root: Path, output: Path) -> dict[str, Any]:
    load_copy_map(root / "design/site-refresh/copy-map.yml")
    claims, claims_by_id = _claim_data(root)
    runs, run_ids = _runs(root)
    studies = _study_data(root, claims_by_id, run_ids)
    publications = _publications(root)
    source = root / "site/src"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for asset in ["styles.css", "site.js", "og.png"]:
        shutil.copy2(source / asset, output / asset)
    routes = _render(root, output, studies, claims, claims_by_id, runs, publications)
    benchmark_run_id = _latest_passing_study_run(root, "DD-010").name
    canonical_data = _canonical_data(_passing_baseline(root))
    data = {
        "canonical.json": canonical_data,
        "research-index.json": {"schema_version": 1, "studies": studies},
        "claims.json": {"schema_version": 1, "claims": claims},
        "runs.json": {"schema_version": 1, "runs": runs},
        "publications.json": {"schema_version": 1, "publications": publications},
        "routes.json": {"schema_version": 1, "routes": routes},
        "labs.json": {
            "schema_version": 1,
            "source": "precomputed bounded fixture outputs",
            "lab_count": 17,
            "threshold_data": "data/labs/threshold.json",
            "equilibrium_selection_data": "data/labs/equilibrium-selection.json",
            "dynamic_attention_data": "data/labs/dynamic-attention.json",
            "team_mechanisms_data": "data/labs/team-mechanisms.json",
            "incremental_sharing_data": "data/labs/incremental-sharing.json",
            "general_sharing_frontier_data": "data/labs/general-sharing-frontier.json",
            "sequential_data": "data/labs/sequential.json",
            "coverage_data": "data/labs/coverage.json",
            "mechanisms_data": "data/labs/mechanisms.json",
            "atlas_data": "data/labs/atlas.json",
            "benchmark_data": "data/benchmark/results.json",
            "experiment_data": "data/experiment/power.json",
            "audience_data": "data/audience/frontier.json",
            "conditional_data": "data/conditional/census.json",
        },
    }
    for name, value in data.items():
        _write(output, f"data/{name}", json.dumps(value, indent=2, sort_keys=True) + "\n")
    for study in studies:
        _write(
            output,
            f"data/studies/{study['slug']}.json",
            json.dumps(study, indent=2, sort_keys=True) + "\n",
        )
    for publication in publications:
        source_pdf = root / str(publication["source_pdf"])
        destination = output / str(publication["download"])
        destination.parent.mkdir(exist_ok=True)
        shutil.copy2(source_pdf, destination)
        if _sha256(destination) != publication["sha256"]:
            raise RuntimeError(f"download copy checksum mismatch: {destination}")
    download_entries = [
        {
            "path": str(path.relative_to(output)),
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in sorted((output / "downloads").glob("*"))
        if path.is_file()
    ]
    _write(
        output,
        "data/downloads.json",
        json.dumps({"schema_version": 1, "downloads": download_entries}, indent=2, sort_keys=True)
        + "\n",
    )
    _write(
        output, "robots.txt", "User-agent: *\nAllow: /\nSitemap: " + PUBLIC_BASE + "sitemap.xml\n"
    )
    urls = "".join(
        f"<url><loc>{PUBLIC_BASE}{route['path']}</loc></url>"
        for route in routes
        if route["path"] != "404.html"
    )
    _write(
        output,
        "sitemap.xml",
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>',
    )
    report = validate_site(output, routes)
    report.update(
        {
            "study_count": len(studies),
            "claim_count": len(claims),
            "passing_run_count": len(runs),
            "publication_count": len(publications),
            "benchmark_run_id": benchmark_run_id,
        }
    )
    _write(output, "build-report.json", json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    report = build(repository_root(), repository_root() / "site/dist")
    print(f"site build passed: {report['page_count']} pages, {report['study_count']} studies")


if __name__ == "__main__":
    main()
