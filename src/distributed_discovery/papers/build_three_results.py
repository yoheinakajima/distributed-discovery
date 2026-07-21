"""Generate evidence assets and compile the Three Results synthesis paper."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.validation.bootstrap import repository_root

RUNS = {
    "roles": "20260720T200447Z_DD-001_6eb12861_ba766d1eba",
    "signatures": "20260720T221139Z_DD-001_b1d8d431_40bf5b06a5",
    "thresholds": "20260720T223829Z_DD-001_b2cc23f4_5e16a90ad1",
    "disclosure": "20260720T225848Z_DD-002_94607423_e29b1460ae",
    "sources": "20260720T232223Z_DD-003_2ea8dad5_ae62f6c1f1",
    "canonical": "20260721T012208Z_DD-000_8e4b55e2_e8321d1048",
}
GENERATOR = "distributed_discovery.papers.build_three_results"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _checked_output(root: Path, run_key: str, relative: str) -> Path:
    run_id = RUNS[run_key]
    run = root / "results/verified" / run_id
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    expected = manifest.get("outputs", {}).get(relative)
    path = run / relative
    if (
        manifest.get("validation_status") != "passed"
        or manifest.get("exit_status") != 0
        or manifest.get("run_id") != run_id
        or not isinstance(expected, str)
        or not path.is_file()
        or _sha256(path) != expected
    ):
        raise RuntimeError(f"invalid paper source artifact: {run_id}/{relative}")
    return path


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_epoch(root: Path) -> str:
    manifest = _json(root / "results/verified" / RUNS["canonical"] / "manifest.json")
    started = datetime.fromisoformat(str(manifest["started_utc"]).replace("Z", "+00:00"))
    if started.tzinfo is None:
        raise ValueError("source run timestamp must include a timezone")
    return str(int(started.timestamp()))


def _artifact_note(run_ids: list[str], claims: list[str], source_hashes: list[str]) -> str:
    runs = ", ".join(run_ids)
    claim_text = ", ".join(claims)
    checksums = ", ".join(value[:12] for value in source_hashes)
    return (
        rf"\ArtifactNote{{Source runs: \path{{{runs}}}; claims: {claim_text}; "
        rf"generator: \path{{{GENERATOR}}}; input SHA-256 prefixes: "
        rf"\texttt{{{checksums}}}.}}"
    )


def _roles_figure(role_row: dict[str, str], witness: dict[str, Any], hashes: list[str]) -> str:
    direct = Fraction(role_row["direct_fraction"])
    optimum = Fraction(role_row["optimum_fraction"])
    profile = witness["profile"]
    return "\n".join(
        [
            "% Generated evidence asset; do not edit by hand.",
            f"% Source runs: {RUNS['roles']}, {RUNS['thresholds']}",
            "% Claim IDs: DD-C-0021, DD-C-0026, DD-C-0027, DD-C-0028",
            f"% Generator: {GENERATOR}",
            f"% Input SHA-256: {', '.join(hashes)}",
            r"\begin{figure}[t]",
            r"\centering",
            r"\begin{tikzpicture}[x=1cm,y=1cm]",
            r"\draw[->] (0,0) -- (5.1,0) node[right] {policy};",
            r"\draw[->] (0,0) -- (0,4.25) node[above] {$G$};",
            r"\foreach \y/\lab in {2.5/{1/2},3/{3/5},3.5/{7/10},4/{4/5}} "
            r"{\draw (-.08,\y)--(.08,\y) node[left=2pt] {\small $\lab$};}",
            rf"\fill[consensus!70] (0.8,0) rectangle (2.1,{5 * float(direct):.8f});",
            rf"\fill[private!75] (2.9,0) rectangle (4.2,{5 * float(optimum):.8f});",
            rf"\node[above] at (1.45,{5 * float(direct):.8f}) "
            rf"{{\small $\frac{{{direct.numerator}}}{{{direct.denominator}}}$}};",
            rf"\node[above] at (3.55,{5 * float(optimum):.8f}) "
            rf"{{\small $\frac{{{optimum.numerator}}}{{{optimum.denominator}}}$}};",
            r"\node[below] at (1.45,0) {direct};",
            r"\node[below] at (3.55,0) {hybrid};",
            r"\begin{scope}[xshift=6.0cm,yshift=.25cm]",
            r"\node[draw,rounded corners,fill=private!8,text width=6.1cm,align=left,inner sep=8pt] "
            r"at (2.9,1.65) {\textbf{Exact witness}\quad $M=3,N=2,p=2/5$\\[3pt]"
            rf"Agent 1: \texttt{{{tuple(profile[0])}}} (territory 0)\\"
            rf"Agent 2: \texttt{{{tuple(profile[1])}}} (reroute signal 0)\\[3pt]"
            r"Gain: $7/10-16/25=3/50$.};",
            r"\end{scope}",
            r"\end{tikzpicture}",
            r"\caption{Roles can improve discovery without communication. The bars use the "
            r"exact unrestricted optimum at the displayed finite fixture; the schematic is "
            r"one optimal representative.}",
            r"\label{fig:roles}",
            _artifact_note(
                [RUNS["roles"], RUNS["thresholds"]],
                ["DD-C-0021", "DD-C-0026", "DD-C-0027", "DD-C-0028"],
                hashes,
            ),
            r"\end{figure}",
            "",
        ]
    )


def _disclosure_figure(witness: dict[str, Any], hashes: list[str]) -> str:
    return "\n".join(
        [
            "% Generated evidence asset; do not edit by hand.",
            f"% Source run: {RUNS['disclosure']}",
            "% Claim IDs: DD-C-0029, DD-C-0030, DD-C-0031",
            f"% Generator: {GENERATOR}",
            f"% Input SHA-256: {', '.join(hashes)}",
            r"\begin{figure}[t]",
            r"\centering",
            r"\begin{tikzpicture}[node distance=12mm and 18mm]",
            (
                r"\node[draw,rounded corners,fill=planner!7,text width=5.1cm,"
                r"align=center,inner sep=9pt]"
            ),
            rf"(less) {{\textbf{{Pooling $P00$}}\\selected $G={witness['selected_less']}$\\"
            rf"pure $G={witness['pure_less_values'][0]}$; planner $G={witness['planner_less']}$}};",
            (
                r"\node[draw,rounded corners,fill=market!8,text width=5.1cm,"
                r"align=center,inner sep=9pt,right=of less]"
            ),
            rf"(more) {{\textbf{{Refinement $P03$}}\\selected $G={witness['selected_more']}$\\"
            rf"pure $G={witness['pure_more_values'][0]}$; planner $G={witness['planner_more']}$}};",
            r"\draw[->,very thick] (less) -- node[above]{deterministic refinement} (more);",
            (
                r"\node[below=8mm of $(less)!0.5!(more)$,draw,fill=consensus!8,"
                r"rounded corners] "
                rf"{{selected change ${witness['selected_difference']}$; pure and planner "
                rf"values rise}};"
            ),
            r"\end{tikzpicture}",
            r"\caption{The bounded disclosure reversal is selection-dependent. The selected "
            r"anonymous-symmetric outcome falls, whereas every pure-equilibrium value and "
            r"the two-action planner value rise for the same witness.}",
            r"\label{fig:disclosure}",
            _artifact_note(
                [RUNS["disclosure"]],
                ["DD-C-0029", "DD-C-0030", "DD-C-0031"],
                hashes,
            ),
            r"\end{figure}",
            "",
        ]
    )


def _graph_edges(adjacency: list[list[int]], xshift: float) -> list[str]:
    edges: list[str] = []
    for source, row in enumerate(adjacency):
        for searcher, connected in enumerate(row):
            if connected:
                edges.append(
                    rf"\draw[inktwo!70] ({xshift + 0.9 + 1.2 * source:.2f},2.8) -- "
                    rf"({xshift + 0.3 + 0.9 * searcher:.2f},.8);"
                )
    return edges


def _sources_figure(
    counterexample: dict[str, Any], bounded_null: dict[str, Any], hashes: list[str]
) -> str:
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        f"% Source run: {RUNS['sources']}",
        "% Claim IDs: DD-C-0032, DD-C-0033, DD-C-0034",
        f"% Generator: {GENERATOR}",
        f"% Input SHA-256: {', '.join(hashes)}",
        r"\begin{figure}[t]",
        r"\centering",
        r"\begin{tikzpicture}[every node/.style={font=\small}]",
    ]
    for offset, label, adjacency, discovery in [
        (
            0.0,
            "Graph A",
            counterexample["left_adjacency"],
            counterexample["left_private_discovery"],
        ),
        (
            6.2,
            "Graph B",
            counterexample["right_adjacency"],
            counterexample["right_private_discovery"],
        ),
    ]:
        lines.append(rf"\node[font=\bfseries] at ({offset + 2.0:.2f},3.65) {{{label}}};")
        for source in range(2):
            lines.append(
                rf"\node[circle,draw,fill=planner!12,minimum size=7mm] "
                rf"at ({offset + 0.9 + 1.2 * source:.2f},2.8) {{$S_{source + 1}$}};"
            )
        for searcher in range(4):
            lines.append(
                rf"\node[circle,draw,fill=private!10,minimum size=7mm] "
                rf"at ({offset + 0.3 + 0.9 * searcher:.2f},.8) {{$A_{searcher + 1}$}};"
            )
        lines.extend(_graph_edges(adjacency, offset))
        lines.append(
            rf"\node[align=center] at ({offset + 2.0:.2f},0) "
            rf"{{mean agreement $={counterexample['matched_mean_pair_agreement']}$\\"
            rf"discovery $={discovery}$}};"
        )
    lines.extend(
        [
            (
                r"\node[draw,rounded corners,fill=market!7,text width=11.4cm,"
                r"align=center] at (5.1,-1.05)"
            ),
            (
                rf"{{Complete pairwise moments:"
                rf" {bounded_null['matched_pairwise_signature_group_count']}"
            ),
            rf"matched groups, {bounded_null['matched_groups_with_different_private_discovery']} "
            r"discovery differences---a bounded null, not a theorem.};",
            r"\end{tikzpicture}",
            r"\caption{Two nonisomorphic source networks have equal mean pair agreement but "
            r"different exact private discovery. Their complete pairwise moment matrices differ.}",
            r"\label{fig:sources}",
            _artifact_note(
                [RUNS["sources"]],
                ["DD-C-0032", "DD-C-0033", "DD-C-0034"],
                hashes,
            ),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _evidence_table(claims: dict[str, dict[str, Any]], source_hash: str) -> str:
    rows = [
        ("Policy-signature theorem", "DD-C-0023", "theorem", "derived"),
        ("Hybrid witness $7/10>16/25$", "DD-C-0021", "bounded exact", "independently reproduced"),
        ("Disclosure reversal", "DD-C-0030", "selected exact", "verified"),
        (
            "Complete pairwise-moment search",
            "DD-C-0033",
            "bounded null",
            "independently reproduced",
        ),
        (
            "Canonical private-team optimum",
            "DD-C-0036",
            "interval / open optimum",
            "verified / unresolved",
        ),
    ]
    for _, claim_id, _, expected in rows[:-1]:
        actual = str(claims[claim_id]["status"]).replace("-", " ")
        if actual != expected:
            raise RuntimeError(f"evidence table status mismatch for {claim_id}: {actual}")
    rendered = [
        "% Generated evidence asset; do not edit by hand.",
        "% Source: claims/claims.yml",
        "% Claim IDs: DD-C-0021, DD-C-0023, DD-C-0030, DD-C-0033, DD-C-0036",
        f"% Generator: {GENERATOR}",
        f"% Input SHA-256: {source_hash}",
        r"\begin{table}[H]",
        r"\centering\small",
        r"\caption{Evidence status is attached to each result, not to the paper as a whole.}",
        r"\label{tab:evidence}",
        r"\begin{tabularx}{\textwidth}{P{.23\textwidth}P{.16\textwidth}P{.19\textwidth}Y}",
        r"\toprule",
        r"Object & Evidence & Status & Boundary\\",
        r"\midrule",
        (
            r"Policy-signature theorem & DD-C-0023\newline theorem & derived & Analytic proof; "
            r"computation audits implementation.\\"
        ),
        (
            r"Hybrid witness $7/10>16/25$ & DD-C-0021\newline bounded exact & independently "
            r"reproduced & One finite fixture; refutes general direct optimality.\\"
        ),
        (
            r"Disclosure reversal & DD-C-0030\newline selected exact & verified & "
            r"Selection-dependent; pure equilibria and planner improve.\\"
        ),
        (
            r"Complete pairwise-moment search & DD-C-0033\newline bounded null & independently "
            r"reproduced & No counterexample in 51 graphs; no sufficiency theorem.\\"
        ),
        (
            r"Canonical private-team optimum & DD-C-0036\newline interval / open & verified / "
            r"unresolved & Exact endpoints; upper attainability and tightness unresolved.\\"
        ),
        r"\bottomrule",
        r"\end{tabularx}",
        (
            r"\ArtifactNote{Source: \path{claims/claims.yml}; claims: DD-C-0021, "
            r"DD-C-0023, DD-C-0030, DD-C-0033, DD-C-0036; generator: \path{"
            f"{GENERATOR}"
            r"}; input SHA-256 prefix: \texttt{"
            f"{source_hash[:12]}"
            r"}.}"
        ),
        r"\end{table}",
        "",
    ]
    return "\n".join(rendered)


def _bib_keys(text: str) -> set[str]:
    return set(re.findall(r"^@\w+\{([^,]+),", text, flags=re.MULTILINE))


def _citation_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for group in re.findall(r"\\cite[tp]?\{([^}]+)\}", text):
        keys.update(key.strip() for key in group.split(","))
    return keys


def _normalize_log(raw: str, root: Path) -> str:
    lines = raw.replace(str(root), "<repository>").splitlines()
    writing = sorted(line.rstrip() for line in lines if line.startswith("note: Writing "))
    normalized: list[str] = []
    inserted = False
    for line in lines:
        if line.startswith("note: Writing "):
            if not inserted:
                normalized.extend(writing)
                inserted = True
            continue
        normalized.append(line.rstrip())
    return "\n".join(normalized) + "\n"


def _validate_source(root: Path, paper: Path, bibliography: Path) -> dict[str, Any]:
    generated_sources = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted((paper / "generated").glob("*.tex"))
    )
    source = (paper / "main.tex").read_text(encoding="utf-8") + generated_sources
    bibliography_text = bibliography.read_text(encoding="utf-8")
    missing_citations = sorted(_citation_keys(source) - _bib_keys(bibliography_text))
    ledger = yaml.safe_load((root / "claims/claims.yml").read_text(encoding="utf-8"))["claims"]
    ledger_ids = {claim["id"] for claim in ledger}
    cited_claims = set(re.findall(r"DD-C-\d{4}", source))
    missing_claims = sorted(cited_claims - ledger_ids)
    required_sections = [
        "Introduction",
        "Framework and evidence discipline",
        "Private roles without communication",
        "Information disclosure under strategic search",
        "Correlated source networks",
        "Unified implications",
        "Limitations",
        "Research agenda",
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
        "citation_key_count": len(_citation_keys(source)),
        "claim_ids_resolved": True,
        "claim_id_count": len(cited_claims),
        "required_sections_present": True,
    }


def _compile(paper: Path, build_dir: Path, root: Path, epoch: str) -> tuple[bytes, str]:
    compiled = subprocess.run(
        ["tectonic", "main.tex", "--outdir", str(build_dir), "--keep-logs"],
        cwd=paper,
        env={**os.environ, "SOURCE_DATE_EPOCH": epoch},
        capture_output=True,
        text=True,
        check=False,
    )
    raw_log = (compiled.stdout + compiled.stderr).replace(str(build_dir), "<build>")
    log = _normalize_log(raw_log, root)
    warnings = re.findall(
        (
            r"(?:undefined (?:reference|citation)|citation .* undefined|"
            r"there were undefined|overfull \\hbox)"
        ),
        log,
        flags=re.IGNORECASE,
    )
    if compiled.returncode != 0 or warnings:
        (paper / "build.log").write_text(log, encoding="utf-8")
        raise RuntimeError("Three Results build failed; inspect papers/three-results/build.log")
    return (build_dir / "main.pdf").read_bytes(), log


def build(root: Path) -> dict[str, Any]:
    paper = root / "papers/three-results"
    generated = paper / "generated"
    build_dir = paper / "build"
    generated.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)

    roles_path = _checked_output(root, "roles", "outputs/tiny-phase-grid.csv")
    role_rows = list(csv.DictReader(roles_path.open(encoding="utf-8")))
    role_row = next(row for row in role_rows if row["case"] == "M3_N2_p2-5")
    witness_path = _checked_output(root, "thresholds", "outputs/known-witnesses.json")
    witness = next(
        item
        for item in _json(witness_path)
        if item["candidates"] == 3 and item["accuracy"] == "2/5"
    )
    disclosure_path = _checked_output(root, "disclosure", "outputs/selection-reversal-witness.json")
    disclosure = _json(disclosure_path)
    source_path = _checked_output(root, "sources", "outputs/mean-agreement-counterexample.json")
    source = _json(source_path)
    null_path = _checked_output(root, "sources", "outputs/pairwise-null-certificate.json")
    bounded_null = _json(null_path)
    supporting_paths = [
        _checked_output(root, "signatures", "outputs/canonical-state-space.json"),
        _checked_output(root, "thresholds", "outputs/threshold-certificate.json"),
        _checked_output(root, "thresholds", "outputs/anti-informative-counterexamples.json"),
        _checked_output(root, "disclosure", "outputs/refinement-comparisons.json"),
        _checked_output(root, "sources", "outputs/graph-registry.json"),
        _checked_output(root, "canonical", "outputs/canonical-exact-frontier-certificate.json"),
    ]
    claims_path = root / "claims/claims.yml"
    claim_records = yaml.safe_load(claims_path.read_text(encoding="utf-8"))["claims"]
    claims = {str(record["id"]): record for record in claim_records}

    assets = {
        "roles-figure.tex": _roles_figure(
            role_row, witness, [_sha256(roles_path), _sha256(witness_path)]
        ),
        "disclosure-figure.tex": _disclosure_figure(disclosure, [_sha256(disclosure_path)]),
        "sources-figure.tex": _sources_figure(
            source, bounded_null, [_sha256(source_path), _sha256(null_path)]
        ),
        "evidence-status-table.tex": _evidence_table(claims, _sha256(claims_path)),
    }
    for name, content in assets.items():
        (generated / name).write_text(content, encoding="utf-8")

    bibliography = generated / "references.bib"
    bibliography_source = (root / "bibliography/references.bib").read_text(encoding="utf-8")
    bibliography.write_text(bibliography_source, encoding="utf-8")
    source_paths = [
        roles_path,
        witness_path,
        disclosure_path,
        source_path,
        null_path,
        *supporting_paths,
        claims_path,
        root / "bibliography/references.bib",
    ]
    source_epoch = _source_epoch(root)
    provenance = {
        "schema_version": 1,
        "generator": GENERATOR,
        "source_runs": RUNS,
        "source_date_epoch": source_epoch,
        "inputs": {str(path.relative_to(root)): _sha256(path) for path in source_paths},
        "generated_assets": {
            name: {
                "sha256": _sha256(generated / name),
                "generator": GENERATOR,
            }
            for name in assets
        },
    }
    (generated / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    source_validation = _validate_source(root, paper, bibliography)
    with tempfile.TemporaryDirectory(prefix="first-", dir=build_dir) as first_dir:
        first_pdf, first_log = _compile(paper, Path(first_dir), root, source_epoch)
    first_hash = hashlib.sha256(first_pdf).hexdigest()
    with tempfile.TemporaryDirectory(prefix="second-", dir=build_dir) as second_dir:
        second_pdf, second_log = _compile(paper, Path(second_dir), root, source_epoch)
    second_hash = hashlib.sha256(second_pdf).hexdigest()
    if first_hash != second_hash:
        raise RuntimeError(
            f"Three Results PDF is not byte reproducible: {first_hash[:12]} != {second_hash[:12]}"
        )
    (paper / "build.log").write_text(second_log, encoding="utf-8")
    output_pdf = paper / "Three_Results_in_Distributed_Discovery.pdf"
    output_pdf.write_bytes(second_pdf)
    pdfinfo = subprocess.run(["pdfinfo", output_pdf], capture_output=True, text=True, check=True)
    page_match = re.search(r"^Pages:\s+(\d+)$", pdfinfo.stdout, flags=re.MULTILINE)
    if page_match is None:
        raise RuntimeError("pdfinfo did not report a page count")
    page_count = int(page_match.group(1))
    if not 12 <= page_count <= 20:
        raise RuntimeError(f"Three Results paper has {page_count} pages; expected 12--20")
    validation: dict[str, Any] = {
        "schema_version": 1,
        "compiler": subprocess.check_output(["tectonic", "--version"], text=True).strip(),
        "compile_exit_status": 0,
        "source_date_epoch": provenance["source_date_epoch"],
        "page_count": page_count,
        "pdf_sha256": second_hash,
        "byte_reproducible_two_builds": True,
        "normalized_compile_logs_identical": first_log == second_log,
        "unresolved_references_citations_or_overfull_boxes": False,
        "generated_assets": sorted([*assets, "provenance.json", "references.bib"]),
        "provenance_validated": True,
        **source_validation,
    }
    (paper / "validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return validation


def main() -> None:
    validation = build(repository_root())
    print(
        f"Three Results paper passed: {validation['page_count']} pages, "
        f"PDF {str(validation['pdf_sha256'])[:12]}"
    )


if __name__ == "__main__":
    main()
