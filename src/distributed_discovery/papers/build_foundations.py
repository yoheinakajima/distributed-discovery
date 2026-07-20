"""Generate evidence-backed assets and compile the foundations note."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.site.build import _canonical_data, _passing_baseline
from distributed_discovery.validation.bootstrap import repository_root


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_table(run: Path) -> str:
    rows = list(csv.DictReader((run / "outputs/canonical_quality.csv").open(encoding="utf-8")))
    metadata = {
        "consensus": ("Consensus", "DD-C-0005", "independently reproduced"),
        "symmetric_market": ("Symmetric market", "DD-C-0007", "verified upstream"),
        "private_clues": ("Private clues", "DD-C-0004", "independently reproduced"),
        "planner_portfolio": ("Planner portfolio", "DD-C-0006", "independently reproduced"),
    }
    rendered = [
        "% Generated from the passing canonical run; do not edit by hand.",
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
        r"\caption{Canonical protocol quantities. Status is intentionally metric-specific.}",
        r"\label{tab:canonical}",
        r"\begin{tabularx}{\textwidth}{lrrrrX}",
        r"\toprule",
        r"Protocol & $Q$ & $G$ & Distinct & Claim & Evidence status\\",
        r"\midrule",
    ]
    for row in rows:
        label, claim, status = metadata[row["protocol"]]
        rendered.append(
            f"{label} & {float(row['avg_action_quality_Q']):.4f} & "
            f"{float(row['discovery_G']):.4f} & {float(row['expected_distinct']):.3f} & "
            f"{claim} & {status}\\\\"
        )
    rendered.extend(
        [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\begin{minipage}{\textwidth}\footnotesize\vspace{0.4em}",
            r"$Q$ is average action quality and $G$ is union discovery. Source: passing run "
            r"\RunID. Values are restated from the pinned canonical model; the market is not "
            r"independently reproduced.",
            r"\end{minipage}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(rendered)


def _frontier_figure(run: Path, private_value: float) -> str:
    rows = list(csv.DictReader((run / "outputs/independent_frontier.csv").open(encoding="utf-8")))
    coordinates = " ".join(
        f"({row['budget']},{100 * float(row['pooled_discovery']):.6f})" for row in rows
    )
    points = "\n".join(
        rf"\fill[planner] ({row['budget']},"
        rf"{100 * float(row['pooled_discovery']):.6f}) circle (2pt);"
        for row in rows
    )
    return "\n".join(
        [
            "% Generated from outputs/independent_frontier.csv; do not edit by hand.",
            r"\begin{figure}[t]",
            r"\centering",
            r"\begin{tikzpicture}[x=0.82cm,y=0.085cm]",
            r"\draw[->] (0.7,35) -- (8.55,35) node[right] {budget $L$};",
            r"\draw[->] (0.7,35) -- (0.7,91) node[above] {$G$ (percent)};",
            r"\foreach \x in {1,...,8} {\draw (\x,34.4)--(\x,35.6) node[below=4pt] {\small \x};}",
            r"\foreach \y in {40,50,...,90} {\draw (0.62,\y)--(0.78,\y) "
            r"node[left=3pt] {\small \y};}",
            rf"\draw[dashed,private,thick] (0.7,{100 * private_value:.6f}) -- "
            rf"(8.35,{100 * private_value:.6f}) node[above left] "
            r"{\small private benchmark};",
            rf"\draw[planner,very thick] plot coordinates {{{coordinates}}};",
            points,
            r"\end{tikzpicture}",
            r"\caption{Pooled-information discovery frontier by coordinated action budget. "
            r"The first budget that weakly exceeds private clue-following is seven "
            r"(DD-C-0008).}",
            r"\label{fig:frontier}",
            r"\end{figure}",
            "",
        ]
    )


def _bib_keys(text: str) -> set[str]:
    return set(re.findall(r"^@\w+\{([^,]+),", text, flags=re.MULTILINE))


def _citation_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for group in re.findall(r"\\cite[tp]?\{([^}]+)\}", text):
        keys.update(key.strip() for key in group.split(","))
    return keys


def _validate_source(root: Path, paper: Path, bibliography: Path) -> dict[str, Any]:
    source = (paper / "main.tex").read_text(encoding="utf-8")
    bib_text = bibliography.read_text(encoding="utf-8")
    missing_citations = sorted(_citation_keys(source) - _bib_keys(bib_text))
    claims = yaml.safe_load((root / "claims/claims.yml").read_text(encoding="utf-8"))["claims"]
    ledger_ids = {claim["id"] for claim in claims}
    cited_claims = set(re.findall(r"DD-C-\d{4}", source))
    missing_claims = sorted(cited_claims - ledger_ids)
    required_sections = [
        "Introduction",
        "Discovery architectures",
        "Information frontiers and protocol loss",
        "Atomic distributed discovery",
        "Canonical protocols",
        "Redundancy and recovery budgets",
        "Information, assignment, and incentives",
        "Correlated channels",
        "Research agenda",
        "Measurement and applications",
        "Limitations",
        "Conclusion",
    ]
    missing_sections = [
        title for title in required_sections if rf"\section{{{title}}}" not in source
    ]
    if missing_citations or missing_claims or missing_sections:
        raise RuntimeError(
            f"source validation failed: citations={missing_citations}, "
            f"claims={missing_claims}, sections={missing_sections}"
        )
    return {
        "citation_keys_resolved": True,
        "claim_ids_resolved": True,
        "required_sections_present": True,
        "claim_id_count": len(cited_claims),
        "citation_key_count": len(_citation_keys(source)),
    }


def build(root: Path) -> dict[str, Any]:
    paper = root / "papers/foundations"
    generated = paper / "generated"
    build_dir = paper / "build"
    generated.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)
    run = _passing_baseline(root)
    canonical = _canonical_data(run)
    (generated / "canonical-table.tex").write_text(_canonical_table(run), encoding="utf-8")
    (generated / "frontier-figure.tex").write_text(
        _frontier_figure(run, float(canonical["metrics"]["private"])), encoding="utf-8"
    )
    bibliography = generated / "references.bib"
    bibliography_source = (root / "bibliography/references.bib").read_text(encoding="utf-8")
    # The canonical entry's long repository URL produces poor line breaking in
    # plainnat. The pinned commit remains in the note field and provenance.
    paper_bibliography = re.sub(
        r"\n  url\s+= \{https://github\.com/yoheinakajima/shared-discovery-paradox\},",
        "",
        bibliography_source,
        count=1,
    )
    paper_bibliography = paper_bibliography.replace(
        "commit 5025cc8e8f2f8ca015dff2066f08f81ad5715a51",
        "commit 5025cc8e",
        1,
    )
    bibliography.write_text(paper_bibliography, encoding="utf-8")
    provenance = {
        "schema_version": 1,
        "run_id": canonical["source_run_id"],
        "upstream_commit": canonical["upstream_commit"],
        "inputs": {
            str(path.relative_to(root)): _sha256(path)
            for path in [
                run / "outputs/canonical_quality.csv",
                run / "outputs/independent_frontier.csv",
                run / "metrics.json",
                root / "bibliography/references.bib",
            ]
        },
    }
    (generated / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    source_validation = _validate_source(root, paper, bibliography)
    source_epoch = subprocess.check_output(
        ["git", "-C", root, "show", "-s", "--format=%ct", "HEAD"], text=True
    ).strip()
    compiled = subprocess.run(
        ["tectonic", "main.tex", "--outdir", str(build_dir), "--keep-logs"],
        cwd=paper,
        env={**os.environ, "SOURCE_DATE_EPOCH": source_epoch},
        capture_output=True,
        text=True,
        check=False,
    )
    raw_log = (compiled.stdout + compiled.stderr).replace(str(root), "<repository>")
    log = "\n".join(line.rstrip() for line in raw_log.splitlines()) + "\n"
    (paper / "build.log").write_text(log, encoding="utf-8")
    unresolved = re.findall(
        r"(?:undefined (?:reference|citation)|citation .* undefined|there were undefined)",
        log,
        flags=re.IGNORECASE,
    )
    if compiled.returncode != 0 or unresolved:
        raise RuntimeError("foundations paper build failed; inspect papers/foundations/build.log")
    built_pdf = build_dir / "main.pdf"
    output_pdf = paper / "Foundations_of_Distributed_Discovery.pdf"
    shutil.copy2(built_pdf, output_pdf)
    pdfinfo = subprocess.run(["pdfinfo", output_pdf], capture_output=True, text=True, check=True)
    page_match = re.search(r"^Pages:\s+(\d+)$", pdfinfo.stdout, flags=re.MULTILINE)
    if page_match is None:
        raise RuntimeError("pdfinfo did not report a page count")
    pages = int(page_match.group(1))
    if not 12 <= pages <= 20:
        raise RuntimeError(f"foundations note has {pages} pages; expected a concise 12--20")
    validation: dict[str, Any] = {
        "schema_version": 1,
        "compiler": subprocess.check_output(["tectonic", "--version"], text=True).strip(),
        "compile_exit_status": compiled.returncode,
        "unresolved_references_or_citations": False,
        "page_count": pages,
        "pdf_sha256": _sha256(output_pdf),
        "generated_assets": [
            "generated/canonical-table.tex",
            "generated/frontier-figure.tex",
            "generated/provenance.json",
        ],
        **source_validation,
    }
    (paper / "validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return validation


def main() -> None:
    validation = build(repository_root())
    print(
        f"foundations paper passed: {validation['page_count']} pages, "
        f"PDF {str(validation['pdf_sha256'])[:12]}"
    )


if __name__ == "__main__":
    main()
