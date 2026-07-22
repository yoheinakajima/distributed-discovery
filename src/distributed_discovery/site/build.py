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
from distributed_discovery.site.navigation import (
    render_breadcrumb,
    render_footer,
    render_header,
    render_section_navigation,
)
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


def _study_card(study: dict[str, Any]) -> str:
    searchable = " ".join(str(study[key]) for key in ("id", "title", "summary", "question")).lower()
    status = human_status(study["phase"])
    return f"""<article class="card study-card {html.escape(study["phase"])}" data-study-card data-category="{html.escape(_study_category(study))}" data-search="{html.escape(searchable)}"><div class="card-meta"><span class="study-id">{html.escape(study["id"])}</span><span class="status-chip">{html.escape(status)}</span></div><h2><a href="research/{html.escape(study["slug"])}.html">{html.escape(str(study["title"]))}</a></h2><p class="card-question">{html.escape(_excerpt(study["question"]))}</p><p class="card-summary">{html.escape(str(study["summary"]))}</p><p class="quiet-meta">{len(study["claim_ids"])} claims · {len(study["run_ids"])} reproducible runs</p><p class="card-link"><a href="research/{html.escape(study["slug"])}.html">Open study <span aria-hidden="true">→</span></a></p></article>"""


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
    body = f"""<header class="page-hero"><p class="eyebrow">{html.escape(study["id"])}</p><h1>{html.escape(str(study["title"]))}</h1><p class="lede">{html.escape(str(study["summary"]))}</p><p class="status-row"><span class="status-chip">{html.escape(phase_label)}</span><span class="status-chip subtle">{html.escape(evidence_label)}</span></p></header><section class="content-section prose"><h2 id="question">The question</h2><p>{html.escape(str(study["question"]))}</p></section><section class="content-section"><h2 id="findings">What we found</h2><ul class="claim-list">{claims}</ul></section><section class="content-section prose"><h2 id="boundary">What this result covers</h2><p>{html.escape(evidence_label)}. The formal evidence wording and registry state remain available below.</p><details class="technical-details"><summary>Technical details</summary><dl><div><dt>Study phase</dt><dd><code>{html.escape(str(study["phase"]))}</code></dd></div><div><dt>Registry status</dt><dd><code>{html.escape(str(study["registry_status"]))}</code></dd></div><div><dt>Evidence status</dt><dd><code>{html.escape(str(study["evidence_status"]))}</code></dd></div></dl></details></section><section class="content-section"><h2 id="evidence">Reproducible evidence</h2><ul class="run-list">{runs}</ul></section><section class="content-section"><h2 id="sources">Files and data</h2><ul>{artifacts}</ul></section><section class="content-section prose"><h2 id="next">What comes next</h2><p>{html.escape(str(study["next_action"]))}</p></section>"""
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

    task_rows = "".join(
        f'<tr data-task-family="{html.escape(str(task["task_family"]))}"><th scope="row">{html.escape(str(task["task_id"]))}</th><td>{html.escape(str(task["task_family"]))}</td><td>{html.escape(", ".join(task["compatible_protocols"]))}</td><td>{html.escape(", ".join(task["reference_claims"]))}</td></tr>'
        for task in tasks
    )
    task_body = f"""<header class="page-hero"><p class="eyebrow">DiscoveryBench</p><h1>Benchmark tasks</h1><p class="lede">Every task declares what evidence is available, which actions are allowed, and how results are evaluated. The complete technical registry remains downloadable.</p></header><table class="matrix"><caption>DiscoveryBench exact benchmark tasks</caption><thead><tr><th>Task</th><th>Family</th><th>Compatible strategy</th><th>Claims</th></tr></thead><tbody>{task_rows}</tbody></table>"""
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
    body = f"""<header class="page-hero"><p class="eyebrow">DD-012 interactive explainer</p><h1>Attention Lab</h1><p class="lede">Explore the exact access-gated follow-public/follow-private model. An ignoring role is not given the public clue; the Lab does not assume an informed person can forget.</p></header><div class="metric-grid"><article class="metric-card"><span>Exact cells</span><strong>{summary["grid_cells"]}</strong></article><article class="metric-card"><span>Attention profiles</span><strong>{summary["profiles"]}</strong></article><article class="metric-card"><span>Reward rules</span><strong>{summary["reward_rules"]}</strong></article></div><section class="lab" data-attention-lab><label for="attention-n">Team size</label><select id="attention-n">{agent_options}</select><label for="attention-p">Private accuracy</label><select id="attention-p">{accuracy_options}</select><label for="attention-q">Public accuracy</label><select id="attention-q">{accuracy_options}</select><label for="attention-k">Number of attenders</label><select id="attention-k">{attender_options}</select><label for="attention-reward">Reward rule</label><select id="attention-reward">{reward_options}</select><p id="attention-status" class="callout" aria-live="polite">Select a registered exact attention profile.</p></section><noscript><p class="callout">JavaScript is off. All {len(rows)} exact profile-and-reward rows remain visible in the complete table.</p></noscript><section class="content-section"><h2>Exact attention profiles</h2><table class="matrix"><caption>Discovery, reward payoffs, social optimum, equilibrium, equal-split attention wedge, first-use gain, and duplicate-use loss</caption><thead><tr><th>N</th><th>p</th><th>q</th><th>Attenders</th><th>Reward</th><th>Discovery</th><th>Attending payoff</th><th>Ignoring payoff</th><th>Social optimum</th><th>Equilibrium</th><th>Equal-split attention wedge</th><th>First-use gain</th><th>Duplicate-use loss</th><th>Transfer budget</th></tr></thead><tbody>{table_rows}</tbody></table></section><details class="technical-details"><summary>Technical details</summary><p><a href="../claims.html#DD-C-0059">DD-C-0059</a> · <a href="../claims.html#DD-C-0060">DD-C-0060</a> · <a href="../claims.html#DD-C-0061">DD-C-0061</a> · reproducible run <a href="{REPOSITORY_URL}/blob/main/results/verified/{DD012_RUN}/manifest.json">{DD012_RUN}</a></p></details><p><a href="../research/dd-012.html">Study page</a> · <a href="../data/attention/census.json">Download attention census</a> · <a href="../data/attention/rewards.json">Download reward registry</a> · <a href="../data/attention/phase-map.json">Download phase map</a></p>"""
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


def _render(
    root: Path,
    output: Path,
    studies: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    claims_by_id: dict[str, dict[str, Any]],
    runs: list[dict[str, Any]],
    publications: list[dict[str, Any]],
) -> list[dict[str, str]]:
    cards = "".join(_study_card(study) for study in studies)
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
    home = f"""<header class="home-hero"><div class="hero-copy"><p class="eyebrow">Collective search under dispersed information</p><h1>Distributed Discovery</h1><p class="tagline">How groups turn evidence into portfolios of action.</p><p class="hero-hook">Better shared information can produce worse collective discovery.</p><p class="lede">A group can improve its best guess and still waste its attempts by sending everyone to the same place. This project studies how evidence, roles, incentives, and timing shape a portfolio of search actions.</p><div class="actions"><a class="button primary" href="https://yoheinakajima.github.io/shared-discovery-paradox/">See the paradox</a><a class="button" href="research.html">Explore the research</a><a class="text-link" href="labs.html">Browse the Labs <span aria-hidden="true">→</span></a></div></div><aside class="paradox-panel" aria-labelledby="paradox-heading"><p class="eyebrow">Evidence is only the first step</p><h2 id="paradox-heading">Same clues. Different ways to search.</h2><p>Pooling improves the group’s ranking, but a one-answer rule compresses the action portfolio.</p><div class="metric-grid compact"><article class="metric-card consensus"><span>One shared answer</span><strong>{html.escape(str(metrics["consensus"]))}</strong></article><article class="metric-card private"><span>Private clue-following</span><strong>{html.escape(str(metrics["private"]))}</strong></article><article class="metric-card planner"><span>Coordinated portfolio</span><strong>{html.escape(str(metrics["planner"]))}</strong></article></div><p class="quiet-meta">Discovery probabilities from run <code>{html.escape(str(canonical["source_run_id"]))}</code>. <a href="research/dd-000.html">Scope and evidence</a>.</p></aside></header><section class="content-section" aria-labelledby="process-heading"><p class="eyebrow">How the system works</p><h2 id="process-heading">From evidence to discovery</h2><p class="section-intro">A discovery architecture determines more than what a group knows. It shapes who sees evidence, which actions are taken, and what the group learns next.</p><ol class="process-grid"><li><span>01</span><strong>Acquire evidence</strong><small>Choose sources and measurements.</small></li><li><span>02</span><strong>Share evidence</strong><small>Decide who can see which signals.</small></li><li><span>03</span><strong>Choose actions</strong><small>Spread attempts across the search space.</small></li><li><span>04</span><strong>Learn and adapt</strong><small>Use outcomes to update the next move.</small></li><li><span>05</span><strong>Reward discovery</strong><small>Align reporting, attention, and effort.</small></li><li><span>06</span><strong>Measure outcomes</strong><small>Track coverage, quality, and discovery.</small></li></ol></section><section class="content-section" aria-labelledby="findings-heading"><p class="eyebrow">Key findings</p><h2 id="findings-heading">Where architecture changes the result</h2><div class="card-grid finding-grid"><article class="card result-card"><p class="card-kicker">Shared Discovery Paradox</p><h3>One better answer can produce fewer discoveries.</h3><p><strong>{html.escape(str(metrics["consensus"]))}</strong> discovery under one shared answer in the canonical fixture.</p><a href="https://yoheinakajima.github.io/shared-discovery-paradox/">See the interactive guide <span aria-hidden="true">→</span></a></article><article class="card result-card"><p class="card-kicker">Common-Source Trap</p><h3>Many reports can still come from one source.</h3><p><strong>p(1−p)/N</strong> is the exact all-common trap width in the frozen model.</p><a href="publications/common-source-trap.html">Read the paper <span aria-hidden="true">→</span></a></article><article class="card result-card"><p class="card-kicker">Truthful discovery mechanisms</p><h3>Rewards can support truthful, differentiated action.</h3><p><strong>{html.escape(str(joint_summary["strict_rows"]))}</strong> strict rows in the registered exact mechanism class.</p><a href="research/dd-006b.html">Open the study <span aria-hidden="true">→</span></a></article><article class="card result-card"><p class="card-kicker">Architecture Atlas</p><h3>Coherent designs reveal real tradeoffs.</h3><p><strong>{html.escape(str(atlas_summary["pareto_cells"]))}</strong> nondominated cells in the bounded synthetic Atlas.</p><a href="labs/atlas.html">Explore the Atlas <span aria-hidden="true">→</span></a></article></div></section><section class="content-section" aria-labelledby="explore-heading"><p class="eyebrow">Explore the work</p><h2 id="explore-heading">Choose your depth</h2><div class="card-grid entry-grid"><article class="card entry-card"><h3><a href="research.html">Research</a></h3><p>Browse every completed, active, and planned study.</p></article><article class="card entry-card"><h3><a href="labs.html">Labs</a></h3><p>Change inputs and inspect precomputed model behavior.</p></article><article class="card entry-card"><h3><a href="publications.html">Papers</a></h3><p>Read the long-form arguments and validated artifacts.</p></article><article class="card entry-card"><h3><a href="benchmark.html">Benchmark</a></h3><p>Compare search strategies on compatible exact tasks.</p></article></div></section><section class="principle"><p>Share the evidence. <strong>Diversify the actions.</strong></p></section>"""
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
    research = f"""<header class="page-hero"><p class="eyebrow">Collective search under dispersed information</p><h1>Research</h1><p class="lede">Browse studies of how evidence, roles, incentives, timing, and action allocation shape collective search.</p></header><section class="catalog" data-research-catalog><div class="research-tools"><div><label for="study-search">Search studies</label><input id="study-search" type="search" placeholder="Search by question, title, or study ID" autocomplete="off"></div><div class="filter-group" aria-label="Filter studies"><button type="button" class="filter-button" data-study-filter="all" aria-pressed="true">All</button><button type="button" class="filter-button" data-study-filter="key-results" aria-pressed="false">Key results</button><button type="button" class="filter-button" data-study-filter="active" aria-pressed="false">Active</button><button type="button" class="filter-button" data-study-filter="planned" aria-pressed="false">Planned</button><button type="button" class="filter-button" data-study-filter="tools" aria-pressed="false">Tools and infrastructure</button></div><p id="study-status" class="result-count" aria-live="polite">{len(studies)} studies shown</p></div><noscript><p class="callout">JavaScript is off. All {len(studies)} studies remain visible; use browser find to search this page.</p></noscript><div class="card-grid study-grid">{cards}</div></section>"""
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
    claim_items = "".join(
        '<article id="{id}" class="card"><p class="eyebrow">{id} · {status} · {claim_type}</p><h2>{short_name}</h2><p>{statement}</p><p><strong>Scope:</strong> {scope}</p><p><a href="research/dd-{suffix}.html">{study_id}</a></p></article>'.format(
            id=html.escape(str(claim["id"])),
            status=html.escape(str(claim["status"])),
            claim_type=html.escape(str(claim["claim_type"])),
            short_name=html.escape(str(claim["short_name"])),
            statement=html.escape(str(claim["statement"])),
            scope=html.escape(str(claim["scope"])),
            suffix=str(claim["study_id"])[3:].lower(),
            study_id=html.escape(str(claim["study_id"])),
        )
        for claim in claims
    )
    claims_body = f"""<header class="page-hero"><p class="eyebrow">Technical evidence</p><h1>Claims</h1><p class="lede">Stable claim anchors connect every formal statement to its scope and evidence. This is the technical ledger; start with <a href="results.html">Results</a> for the plain-language findings.</p><p class="quiet-meta">No unvalidated values are rendered as claims.</p></header><section class="card-grid claim-grid">{claim_items}</section>"""
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
    publications_body = f"""<header class="page-hero"><p class="eyebrow">Long-form research</p><h1>Papers</h1><p class="lede">Working papers on how groups acquire, share, and convert evidence into portfolios of action.</p></header><section class="card-grid paper-grid">{publication_items}</section><p class="quiet-meta"><a href="data/downloads.json">Complete download checksum manifest</a></p>"""
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
        status_bits = [str(item["status"]).replace("-", " ")]
        if item["doi"]:
            status_bits.append(f"DOI {item['doi']}")
        else:
            status_bits.append("no DOI")
        if item["submitted"] is False:
            status_bits.append("not submitted")
        if item["peer_reviewed"] is False:
            status_bits.append("not peer reviewed")
        detail_body = f"""<header class="page-hero"><p class="eyebrow">Working paper</p><h1>{html.escape(str(item["title"]))}</h1><p class="lede">{html.escape(publication_purposes[str(item["slug"])])}</p><p class="status-row"><span class="status-chip">{html.escape(human_status(item["status"], kind="publication"))}</span><span>{html.escape(str(item["page_count"]))} pages</span></p><p><a class="button primary" href="../{html.escape(str(item["download"]))}">Download PDF</a></p></header><section class="content-section prose"><h2>Citation</h2><p>{html.escape(str(item["citation"]))}</p></section><section class="content-section prose"><h2>Source and provenance</h2><p><a href="{REPOSITORY_URL}/blob/main/{html.escape(str(item["build_source"]))}">Read the build source</a> · <a href="{REPOSITORY_URL}/tree/main/papers/{html.escape(str(item["slug"]))}">Inspect validation and provenance</a></p><details class="technical-details"><summary>Technical details</summary><p>{html.escape(" · ".join(status_bits))}</p><p>The download is copied only after its SHA-256 matches the committed validation record.</p><p>SHA-256 <code>{html.escape(str(item["sha256"]))}</code></p></details></section>"""
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
        + "".join(_study_card(study) for study in open_studies)
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
    results_body = f"""<header class="page-hero"><p class="eyebrow">Key findings</p><h1>Results</h1><p class="lede">What the evidence says about gathering information and spreading action across a search portfolio.</p></header><div class="result-groups"><section class="result-group"><p class="eyebrow">How information is gathered</p><h2>The source of a clue changes what agreement means.</h2><article class="finding"><div><span class="status-chip">Exact in this model</span><h3>The all-common source trap has a closed-form width.</h3><p>In the frozen homogeneous equal-prize model, the exact trap width is <strong>p(1−p)/N</strong>; a separate finite audit and negative result define the boundary.</p></div><div class="finding-links"><a href="research/dd-008b.html">Open DD-008B</a><a href="claims.html#DD-C-0057">Technical evidence</a></div></article></section><section class="result-group"><p class="eyebrow">How information is shared</p><h2>More accurate evidence need not belong in every hand.</h2><article class="finding"><div><span class="status-chip">Checked independently</span><h3>One reader can be the discovery-maximizing audience.</h3><p>When shared accuracy q exceeds private accuracy p in the frozen follow/private class, the exact optimum reader count is <strong>1</strong>.</p></div><div class="finding-links"><a href="research/dd-013.html">Open DD-013</a><a href="claims.html#DD-C-0062">Technical evidence</a></div></article></section><section class="result-group"><p class="eyebrow">How actions are allocated</p><h2>A better shared ranking can still concentrate search.</h2><article class="finding"><div><span class="status-chip">Canonical fixture</span><h3>Same clues, different action portfolios.</h3><p>Discovery is <strong>{html.escape(str(metrics["consensus"]))}</strong> under one shared answer, <strong>{html.escape(str(metrics["private"]))}</strong> under private clue-following, and <strong>{html.escape(str(metrics["planner"]))}</strong> under a coordinated pooled portfolio.</p></div><div class="finding-links"><a href="research/dd-000.html">Open DD-000</a><a href="claims.html#DD-C-0005">Technical evidence</a></div></article></section><section class="result-group"><p class="eyebrow">How incentives change behavior</p><h2>Truthful reporting and differentiated action can coexist.</h2><article class="finding"><div><span class="status-chip">Completed finite study</span><h3>A bounded mechanism class contains strict rows.</h3><p>The exact census finds <strong>{html.escape(str(joint_summary["strict_rows"]))}</strong> strict rows, with a maximum all-tie margin of <strong>{html.escape(str(joint_summary["maximum_margin"]))}</strong>.</p></div><div class="finding-links"><a href="research/dd-006b.html">Open DD-006B</a><a href="claims.html#DD-C-0053">Technical evidence</a></div></article></section><section class="result-group"><p class="eyebrow">How discovery is measured</p><h2>No single score captures every architecture.</h2><article class="finding"><div><span class="status-chip">Bounded synthetic Atlas</span><h3>Tradeoffs leave multiple coherent designs standing.</h3><p>Among <strong>{html.escape(str(atlas_summary["valid_cells"]))}</strong> valid cells, <strong>{html.escape(str(atlas_summary["pareto_cells"]))}</strong> are nondominated under the declared objectives.</p></div><div class="finding-links"><a href="research/dd-009.html">Open DD-009</a><a href="labs/atlas.html">Explore the Lab</a></div></article></section></div>"""
    results_body = (
        results_body.removesuffix("</div>")
        + """<section class="result-group">
    <p class="eyebrow">Program V3 · selective attention</p>
    <h2>Shared evidence can have a first-use benefit and a duplicate-use cost.</h2>
    <article class="finding"><div><span class="status-chip">Verified theorem</span>
    <h3>The first reader can help; duplicate use can reduce discovery.</h3>
    <p>In DD-012's frozen access-gated follow/private model, the first shared-signal reader improves discovery exactly when q exceeds p, while every later reader has a strictly negative marginal discovery effect.</p>
    </div><div class="finding-links"><a href="research/dd-012.html">Open DD-012</a><a href="claims.html#DD-C-0059">Technical evidence</a></div></article>
    <article class="finding"><div><span class="status-chip">Checked independently</span>
    <h3>Equilibrium can overuse a shared clue.</h3>
    <p>The registered 175-cell equal-split census contains <strong>63</strong> excessive-attention cells and <strong>24</strong> all-attend equilibria despite a unique one-reader planner optimum.</p>
    </div><div class="finding-links"><a href="research/dd-012.html">Open DD-012</a><a href="claims.html#DD-C-0060">Technical evidence</a></div></article>
    <article class="finding"><div><span class="status-chip">Checked independently</span>
    <h3>One reader can be the discovery-maximizing audience.</h3>
    <p>In DD-013's binding follow/private class, the optimal audience is one recipient when q exceeds p; the claim does not prescribe general information restriction.</p>
    </div><div class="finding-links"><a href="research/dd-013.html">Open DD-013</a><a href="claims.html#DD-C-0062">Technical evidence</a></div></article>
    <article class="finding"><div><span class="status-chip">Preserved negative result</span>
    <h3>The registered conditional-policy theorem is not unrestricted.</h3>
    <p>DD-014's separate two-label raw-policy audit finds complementary constant policies with discovery one, strictly above the best embedded private/public profile in all four audited cells.</p>
    </div><div class="finding-links"><a href="research/dd-014.html">Open DD-014</a><a href="claims.html#DD-C-0068">Technical evidence</a></div></article>
    </section></div>"""
    )
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
            "Mechanism scenario",
            "Incentive and discovery boundaries",
            "DD-006B",
        ),
        "audit": (
            "Measurement and experiments",
            "Synthetic audit scenario",
            "Recovery and calibration behavior",
            "DD-007",
        ),
        "atlas": (
            "Measurement and experiments",
            "Architecture index",
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
    generic_by_slug = {
        slug: (title, claim, description) for slug, title, claim, _, description in lab_specs
    }
    special_labs = {
        "attention": (
            "Attention",
            "DD-C-0060",
            "Explore exact access-gated attention profiles, payoffs, equilibria, and rewards.",
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
    for group in (
        "Search and allocation",
        "Information and sources",
        "Incentives and mechanisms",
        "Measurement and experiments",
    ):
        group_cards = []
        for slug, details in lab_details.items():
            if details[0] != group:
                continue
            title, claim, description = (special_labs | generic_by_slug)[slug]
            group_cards.append(
                f'<article class="card lab-card"><p class="eyebrow">Interactive explainer</p><h3><a href="labs/{slug}.html">{html.escape(title)}</a></h3><p>{html.escape(description)}</p><dl><div><dt>What can I change?</dt><dd>{html.escape(details[1])}</dd></div><div><dt>What will I see?</dt><dd>{html.escape(details[2])}</dd></div><div><dt>Supported by</dt><dd>{html.escape(details[3])}</dd></div></dl><p class="card-link"><a href="labs/{slug}.html">Open Lab <span aria-hidden="true">→</span></a></p><details class="technical-details"><summary>Technical details</summary><p><a href="claims.html#{claim}">{claim}</a> · <a href="evidence.html">Reproducible evidence</a></p></details></article>'
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
    for slug, title, claim, run_id, description in lab_specs:
        scenario_count = 20 if slug == "atlas" else 5
        value_label = "Architecture index" if slug == "atlas" else "Scenario index"
        lab_body = f"""<header class="page-hero"><p class="eyebrow">Interactive explainer</p><h1>{html.escape(title)}</h1><p class="lede">{html.escape(description)}</p></header><section class="lab" data-lab="{slug}"><label for="scenario">{value_label}: <output id="scenario-output">1</output></label><input id="scenario" type="range" min="1" max="{scenario_count}" value="1" step="1" aria-describedby="lab-note"><p id="lab-note" class="callout" aria-live="polite">Scenario 1 is the readable default. Adjust the slider to compare {scenario_count} precomputed fixture views.</p></section><noscript><p class="callout">JavaScript is off. The default scenario remains available below.</p></noscript><table class="matrix"><caption>Study support and fallback behavior</caption><thead><tr><th>What this covers</th><th>Registered interpretation</th></tr></thead><tbody><tr><td>Claim</td><td><a href="../claims.html#{claim}">{claim}</a></td></tr><tr><td>Reproducible run</td><td><a href="{REPOSITORY_URL}/blob/main/results/verified/{run_id}/manifest.json">{run_id}</a></td></tr><tr><td>Fallback</td><td>Scenario 1; bounded fixture only, not a recommendation.</td></tr></tbody></table>"""
        _write(
            output, f"labs/{slug}.html", _page(title, description, lab_body, f"labs/{slug}.html")
        )
    _benchmark_pages(root, output)
    _experiment_pages(root, output)
    _attention_pages(root, output)
    _audience_pages(root, output)
    _conditional_pages(root, output)
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
            re.search(r"data-(?:(?:benchmark|experiment|audience)-)?lab", source)
            and "<noscript>" not in source
        ):
            errors.append(f"{relative}: interactive Lab lacks a no-JavaScript fallback")
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
    joint_summary_path = (
        root / "results/verified" / DD006B_RUN / "outputs/joint-mechanism-summary.json"
    )
    joint_summary = json.loads(joint_summary_path.read_text(encoding="utf-8"))
    atlas_run = root / "results/verified" / DD009_RUN / "outputs"
    atlas_summary = json.loads((atlas_run / "atlas-summary.json").read_text(encoding="utf-8"))
    atlas_rows = json.loads((atlas_run / "architectures.json").read_text(encoding="utf-8"))
    atlas_dominance = json.loads((atlas_run / "dominance.json").read_text(encoding="utf-8"))
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
            "source": "precomputed bounded fixture controls",
            "scenario_count": 5,
            "mechanisms_data": "data/labs/mechanisms.json",
            "atlas_data": "data/labs/atlas.json",
            "benchmark_data": "data/benchmark/results.json",
            "experiment_data": "data/experiment/power.json",
            "audience_data": "data/audience/frontier.json",
            "conditional_data": "data/conditional/census.json",
        },
        "labs/mechanisms.json": {
            "schema_version": 1,
            "study_id": "DD-006B",
            "claim_id": "DD-C-0053",
            "run_id": DD006B_RUN,
            "frontier_rows": joint_summary["frontier_rows"],
            "weak_rows": joint_summary["weak_rows"],
            "strict_rows": joint_summary["strict_rows"],
            "maximum_margin": joint_summary["maximum_margin"],
            "best_strict_discovery": joint_summary["best_strict_discovery"],
            "regime_results": joint_summary["regime_results"],
            "boundary": "registered exact subsidized class; not arbitrary mechanisms",
        },
        "labs/atlas.json": {
            "schema_version": 1,
            "study_id": "DD-009",
            "claim_id": "DD-C-0054",
            "run_id": DD009_RUN,
            "summary": atlas_summary,
            "architectures": atlas_rows,
            "dominance": atlas_dominance,
            "boundary": "registered finite synthetic atlas; not a universal ranking",
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
