"""Build and validate the public research-library site from repository evidence."""

# ruff: noqa: E501

from __future__ import annotations

import hashlib
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


class SiteParser(HTMLParser):
    """Collect enough document structure for generated-route validation."""

    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.headings: list[int] = []
        self.tags: set[str] = set()
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.add(tag)
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(str(values["id"]))
        if tag == "a" and values.get("href"):
            self.hrefs.append(str(values["href"]))
        if tag == "meta" and values.get("name") and values.get("content"):
            self.meta[str(values["name"])] = str(values["content"])
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
    ):
        validation = json.loads((root / "papers" / directory / "validation.json").read_text())
        candidates = sorted((root / "papers" / directory).glob("*.pdf"))
        if len(candidates) != 1:
            raise RuntimeError(f"expected one public PDF in papers/{directory}")
        pdf = candidates[0]
        digest = _sha256(pdf)
        if validation.get("pdf_sha256") != digest:
            raise RuntimeError(f"publication checksum mismatch: {pdf}")
        publications.append(
            {
                "title": title,
                "slug": directory,
                "source_pdf": str(pdf.relative_to(root)),
                "download": f"downloads/{pdf.name}",
                "sha256": digest,
                "page_count": validation.get("page_count"),
                "build_source": f"papers/{directory}/main.tex",
                "citation": f"Distributed Discovery project ({directory}). {title}.",
            }
        )
    return publications


def _page(title: str, description: str, body: str, current: str) -> str:
    primary = [
        ("Foundations", "foundations.html"),
        ("Research", "research.html"),
        ("Results", "results.html"),
        ("Labs", "labs.html"),
        ("Publications", "publications.html"),
        ("Applications", "applications.html"),
    ]
    secondary = [
        ("Claims", "claims.html"),
        ("Evidence", "evidence.html"),
        ("Open questions", "open-problems.html"),
        ("Ideas", "ideas.html"),
        ("Repo", REPOSITORY_URL),
    ]
    prefix = "../" if "/" in current else ""
    nav = "".join(
        '<a href="{}"{}>{}</a>'.format(
            prefix + href, ' aria-current="page"' if current == href else "", name
        )
        for name, href in primary
    )
    subnav = " · ".join(
        f'<a href="{href if href.startswith("http") else prefix + href}">{name}</a>'
        for name, href in secondary
    )
    canonical = f"{PUBLIC_BASE}{current}" if current != "index.html" else PUBLIC_BASE
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — Distributed Discovery</title><meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical}"><meta property="og:title" content="{html.escape(title)} — Distributed Discovery"><meta property="og:description" content="{html.escape(description)}"><meta property="og:image" content="{PUBLIC_BASE}og.svg"><meta property="og:type" content="website"><link rel="stylesheet" href="{prefix}styles.css"><script src="{prefix}site.js" defer></script></head>
<body><a class="skip-link" href="#content">Skip to content</a><header class="topbar"><div class="wrap"><a class="brand" href="{prefix}index.html">Distributed Discovery</a><nav aria-label="Primary navigation">{nav}</nav></div><div class="wrap secondary" aria-label="Research navigation">{subnav}</div></header>
<main id="content" class="narrow">{body}</main><footer><div class="wrap"><span>Public MIT-licensed research library · no analytics or tracking</span><span><a href="{prefix}index.html">Home</a> · <a href="{REPOSITORY_URL}">Repository</a></span></div></footer></body></html>"""


def _study_card(study: dict[str, Any]) -> str:
    return f"""<article class="card {html.escape(study["phase"])}"><p class="eyebrow">{html.escape(study["id"])} · {html.escape(study["phase"])}</p><h2><a href="research/{html.escape(study["slug"])}.html">{html.escape(str(study["title"]))}</a></h2><p>{html.escape(str(study["summary"]))}</p><p><span class="badge">{len(study["claim_ids"])} claims · {len(study["run_ids"])} passing runs</span></p></article>"""


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
        "".join(f"<li>{html.escape(run_id)}</li>" for run_id in study["run_ids"])
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
    body = f"""<p class="eyebrow"><a href="../research.html">Research</a> / {html.escape(study["id"])}</p><h1>{html.escape(str(study["title"]))}</h1><p class="lede">{html.escape(str(study["summary"]))}</p><p><span class="badge">{html.escape(study["phase"])}</span> Registry: {html.escape(str(study["registry_status"]))}</p><section><h2 id="question">Question</h2><p>{html.escape(str(study["question"]))}</p></section><section><h2 id="evidence">Evidence boundary</h2><p>{html.escape(str(study["evidence_status"]))}</p><h3>Claims</h3><ul>{claims}</ul><h3>Passing immutable runs</h3><ul>{runs}</ul></section><section><h2 id="sources">Public sources</h2><ul>{artifacts}</ul><p>Next action: {html.escape(str(study["next_action"]))}</p></section>"""
    return _page(str(study["title"]), str(study["summary"]), body, f"research/{study['slug']}.html")


def _write(output: Path, relative: str, content: str) -> None:
    path = output / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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
    counts = {phase: sum(study["phase"] == phase for study in studies) for phase in PHASES}
    home = f"""<section class="hero"><p class="kicker">Research library</p><h1>A research program in Distributed Discovery</h1><p class="lede">Evidence, action allocation, coverage, incentives, and feedback are distinct margins. This library makes the bounded evidence and its limits inspectable.</p></section><section><h2 id="research-map">Research map</h2><p>{len(claims)} ledger claims · {len(runs)} passing immutable runs · {len(publications)} validated publications.</p><div class="grid-2">{cards}</div></section><section><h2 id="incubator">Ideas incubator</h2><p>Speculative extensions are kept separate from results: noisy sequential tests, randomized disclosure, higher-order source laws, mechanism classes beyond the registered fixture, and real-data audits require new registrations and evidence.</p><p><a class="primary-link" href="ideas.html">Browse the incubator and boundary conditions →</a></p></section>"""
    _write(
        output,
        "index.html",
        _page(
            "Research Library",
            "Evidence-indexed public research library for Distributed Discovery.",
            home,
            "index.html",
        ),
    )
    phase_links = "".join(
        f'<a href="#{phase}">{phase} ({counts[phase]})</a> '
        for phase in sorted(PHASES)
        if counts[phase]
    )
    phase_targets = "".join(
        f'<span id="{phase}"></span>' for phase in sorted(PHASES) if counts[phase]
    )
    research = f"""<p class="eyebrow">Research library</p><h1>Studies</h1><p class="lede">All studies are visible without JavaScript. Use the phase anchors to narrow the page, or use browser find to search titles, IDs, and terms.</p><p class="filter-links">{phase_links}</p>{phase_targets}<section class="grid-2">{cards}</section>"""
    _write(
        output,
        "research.html",
        _page(
            "Research",
            "All registered and completed Distributed Discovery studies.",
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
    claims_body = f"""<p class="eyebrow">Evidence index</p><h1>Claims</h1><p class="lede">Stable claim anchors expose type, status, statement, and scope. Browser find is the no-JavaScript search control; no unvalidated values are rendered as claims.</p><section class="grid-2">{claim_items}</section>"""
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
        '<article class="card"><h2>{run_id}</h2><p>{study_id} · passed immutable manifest · {output_count} checksum-validated public-safe outputs.</p><p><a href="{repo}/blob/main/{manifest_path}">Manifest source</a> · SHA-256 {manifest_sha}</p></article>'.format(
            run_id=html.escape(str(run["run_id"])),
            study_id=html.escape(str(run["study_id"])),
            output_count=html.escape(str(run["output_count"])),
            repo=REPOSITORY_URL,
            manifest_path=html.escape(str(run["manifest_path"])),
            manifest_sha=html.escape(str(run["manifest_sha256"])),
        )
        for run in runs
    )
    evidence_body = f"""<p class="eyebrow">Evidence index</p><h1>Passing runs</h1><p class="lede">Only manifests with passed validation, exit status zero, repository-relative paths, and checksum-validated safe outputs appear here. Failed and preliminary material is not substantive public evidence.</p><section class="grid-2">{evidence_items}</section>"""
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
    publication_items = "".join(
        '<article class="card"><h2>{title}</h2><p>{page_count} pages · SHA-256 <code>{sha256}</code></p><p><a href="{download}">Download PDF</a> · <a href="{repo}/blob/main/{build_source}">Build source</a></p><p>{citation}</p></article>'.format(
            title=html.escape(str(item["title"])),
            page_count=html.escape(str(item["page_count"])),
            sha256=html.escape(str(item["sha256"])),
            download=html.escape(str(item["download"])),
            repo=REPOSITORY_URL,
            build_source=html.escape(str(item["build_source"])),
            citation=html.escape(str(item["citation"])),
        )
        for item in publications
    )
    publications_body = f"""<p class="eyebrow">Publications</p><h1>Validated papers</h1><p class="lede">Downloads are copied only from validation-recorded PDF artifacts. Checksums and page counts are generated from the current repository evidence.</p><section class="grid-2">{publication_items}</section>"""
    _write(
        output,
        "publications.html",
        _page(
            "Publications",
            "Validated Distributed Discovery paper downloads and provenance.",
            publications_body,
            "publications.html",
        ),
    )
    open_studies = [
        study
        for study in studies
        if study["phase"] in {"registered", "queued", "active-extension", "blocked"}
    ]
    open_body = (
        '<p class="eyebrow">Research agenda</p><h1>Open questions</h1><p class="lede">These are registered next steps, not results.</p><section class="grid-2">'
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
    ideas_body = """<p class="eyebrow">Ideas incubator</p><h1>Speculation is not evidence</h1><p class="lede">The following directions are deliberately separated from the claim ledger.</p><ul><li>Noisy or state-coupled sequential tests after DD-004’s perfect-elimination baseline.</li><li>Randomized disclosure and broader equilibrium-selection procedures after DD-002.</li><li>Higher-order report laws and expanded source palettes after DD-003.</li><li>Mechanism classes, equilibrium concepts, and observability variants outside DD-006’s registration.</li><li>Real-data work only after DD-007 privacy, identification, and ethics review.</li></ul>"""
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
    foundations_body = """<p class="eyebrow">Foundations</p><h1>Information and action allocation</h1><p class="lede">The program distinguishes information architecture from the protocol that transforms evidence into a portfolio of actions.</p><p class="identity">G<sub>B</sub>(Π; I) = V<sub>B</sub>(I) − L<sub>B</sub>(Π; I)</p><p>It is an accounting identity, not a universal monotonicity theorem. Consult the <a href="research/dd-000.html">foundations record</a> and <a href="publications.html">validated note</a> for scope and provenance.</p>"""
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
    results_body = (
        """<p class="eyebrow">Results</p><h1>Completed bounded evidence</h1><p class="lede">Exact canonical, private-role, disclosure, and source-network results are bounded by their registered model classes.</p><section class="grid-2">"""
        + "".join(
            _study_card(study)
            for study in studies
            if study["phase"] in {"foundations", "exact-result", "complete-bounded-study"}
        )
        + "</section>"
    )
    _write(
        output,
        "results.html",
        _page(
            "Results",
            "Completed bounded results with direct links to claim and run evidence.",
            results_body,
            "results.html",
        ),
    )
    applications_body = """<p class="eyebrow">Applications</p><h1>Mappings, not results</h1><p class="lede">Science, R&amp;D, venture portfolios, and multi-agent systems can be represented as evidence, action, coverage, and feedback systems. Each mapping needs its own action technology, objective, dependence model, and evidence standard.</p>"""
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
            "DD-C-0050",
            "20260721T140745Z_DD-006_401ad624_c942f43e42",
            "Explore the registered normalized-linear transfer frontier; no arbitrary-transfer conclusion is implied.",
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
    ]
    lab_cards = "".join(
        f'<article class="card"><p class="eyebrow">Interactive lab</p><h2><a href="labs/{slug}.html">{html.escape(title)}</a></h2><p>{html.escape(description)}</p><p><a href="claims.html#{claim}">{claim}</a> · <a href="evidence.html">passing run</a></p></article>'
        for slug, title, claim, _, description in lab_specs
    )
    labs_body = f"""<p class="eyebrow">Public labs</p><h1>Discovery Stack Labs</h1><p class="lede">Small browser-native controls expose bounded fixtures. Every lab has a readable fallback and links to the claim ledger and immutable passing run; controls never call an external API.</p><section class="grid-2">{lab_cards}</section>"""
    _write(
        output,
        "labs.html",
        _page(
            "Labs",
            "Interactive, evidence-indexed Distributed Discovery labs.",
            labs_body,
            "labs.html",
        ),
    )
    for slug, title, claim, run_id, description in lab_specs:
        value_label = "Scenario index"
        lab_body = f"""<p class="eyebrow"><a href="../labs.html">Labs</a> / {html.escape(title)}</p><h1>{html.escape(title)}</h1><p class="lede">{html.escape(description)}</p><section class="lab" data-lab="{slug}"><label for="scenario">{value_label}: <output id="scenario-output">1</output></label><input id="scenario" type="range" min="1" max="5" value="1" step="1" aria-describedby="lab-note"><p id="lab-note" class="callout" aria-live="polite">Scenario 1 is the readable default. Adjust the slider to compare the five precomputed fixture views.</p></section><noscript><p class="callout">JavaScript is off. The default scenario remains available below.</p></noscript><table class="matrix"><thead><tr><th>Evidence boundary</th><th>Registered interpretation</th></tr></thead><tbody><tr><td>Claim</td><td><a href="../claims.html#{claim}">{claim}</a></td></tr><tr><td>Immutable run</td><td><a href="{REPOSITORY_URL}/blob/main/results/verified/{run_id}/manifest.json">{run_id}</a></td></tr><tr><td>Fallback</td><td>Scenario 1; bounded fixture only, not a recommendation.</td></tr></tbody></table>"""
        _write(
            output, f"labs/{slug}.html", _page(title, description, lab_body, f"labs/{slug}.html")
        )
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
        if not parser.headings or parser.headings[0] != 1:
            errors.append(f"{relative}: first heading must be h1")
        if "description" not in parser.meta:
            errors.append(f"{relative}: missing description")
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
    for download in (output / "downloads").glob("*.pdf"):
        if download.stat().st_size == 0:
            errors.append(f"empty download: {download.name}")
    if errors:
        raise RuntimeError("site validation failed:\n" + "\n".join(errors))
    return {
        "schema_version": 2,
        "page_count": len(actual),
        "routes": sorted(expected),
        "internal_links_passed": True,
        "semantic_structure_passed": True,
        "public_safety_passed": True,
    }


def build(root: Path, output: Path) -> dict[str, Any]:
    claims, claims_by_id = _claim_data(root)
    runs, run_ids = _runs(root)
    studies = _study_data(root, claims_by_id, run_ids)
    publications = _publications(root)
    source = root / "site/src"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for asset in ["styles.css", "site.js", "og.svg"]:
        shutil.copy2(source / asset, output / asset)
    routes = _render(root, output, studies, claims, claims_by_id, runs, publications)
    data = {
        "research-index.json": {"schema_version": 1, "studies": studies},
        "claims.json": {"schema_version": 1, "claims": claims},
        "runs.json": {"schema_version": 1, "runs": runs},
        "publications.json": {"schema_version": 1, "publications": publications},
        "routes.json": {"schema_version": 1, "routes": routes},
        "labs.json": {
            "schema_version": 1,
            "source": "precomputed bounded fixture controls",
            "scenario_count": 5,
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
    _write(
        output, "robots.txt", "User-agent: *\nAllow: /\nSitemap: " + PUBLIC_BASE + "sitemap.xml\n"
    )
    urls = "".join(f"<url><loc>{PUBLIC_BASE}{route['path']}</loc></url>" for route in routes)
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
        }
    )
    _write(output, "build-report.json", json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    report = build(repository_root(), repository_root() / "site/dist")
    print(f"site build passed: {report['page_count']} pages, {report['study_count']} studies")


if __name__ == "__main__":
    main()
