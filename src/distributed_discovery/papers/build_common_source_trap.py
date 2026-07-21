# ruff: noqa: E501 -- generated LaTeX commands are kept intact for auditability.

"""Generate evidence assets and build The Common-Source Trap working paper."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import yaml

from distributed_discovery.validation.bootstrap import repository_root

GENERATOR = "distributed_discovery.papers.build_common_source_trap"
RUNS = {
    "two_agent": "20260721T141527Z_DD-008_0d11dc77_7e0c8f1d66",
    "finite_n": "20260721T163030Z_DD-008A_8b70668b_06307caab4",
    "analytic": "20260721T192412Z_DD-008B_649deb08_29dbeaf3a9",
    "mechanism": "20260721T165512Z_DD-006B_f022a1a5_3be21d0b9b",
    "atlas": "20260721T171249Z_DD-009_bc78d249_0c3851c41a",
    "experiment": "20260721T185647Z_DD-011_fa0271d9_fcaa647c55",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _checked_output(root: Path, run_key: str, relative: str) -> Path:
    run_id = RUNS[run_key]
    run = root / "results/verified" / run_id
    manifest = _json(run / "manifest.json")
    path = run / relative
    expected = manifest.get("outputs", {}).get(relative)
    if (
        manifest.get("validation_status") != "passed"
        or manifest.get("exit_status") != 0
        or manifest.get("run_id") != run_id
        or not isinstance(expected, str)
        or not path.is_file()
        or _sha256(path) != expected
    ):
        raise RuntimeError(f"invalid paper source: {run_id}/{relative}")
    return path


def _artifact_note(run_keys: list[str], claims: list[str], paths: list[Path]) -> str:
    run_text = ", ".join(RUNS[key] for key in run_keys)
    claim_text = ", ".join(claims)
    hashes = ", ".join(_sha256(path)[:12] for path in paths)
    return (
        rf"\ArtifactNote{{Source runs: \path{{{run_text}}}; claims: {claim_text}; "
        rf"generator: \path{{{GENERATOR}}}; input SHA-256 prefixes: "
        rf"\texttt{{{hashes}}}.}}"
    )


def _trap_region(paths: list[Path]) -> str:
    upper = []
    lower2 = []
    lower4 = []
    lower8 = []
    for numerator in range(1, 20):
        p = Fraction(numerator, 20)
        scale = float(p * (1 - p))
        x = float(p)
        upper.append(f"({x:.3f},{scale:.5f})")
        lower2.append(f"({x:.3f},{scale / 2:.5f})")
        lower4.append(f"({x:.3f},{3 * scale / 4:.5f})")
        lower8.append(f"({x:.3f},{7 * scale / 8:.5f})")
    return "\n".join(
        [
            "% Generated evidence asset; do not edit by hand.",
            "% Claims: DD-C-0051, DD-C-0057",
            r"\begin{figure}[t]\centering",
            r"\begin{tikzpicture}[x=10.3cm,y=17cm]",
            r"\draw[->] (0,0)--(1.02,0) node[right] {$p$};",
            r"\draw[->] (0,0)--(0,.275) node[above] {$c$};",
            r"\foreach \x/\lab in {.2/{.2},.4/{.4},.6/{.6},.8/{.8},1/{1}} {\draw (\x,0)--(\x,-.004) node[below] {\small $\lab$};}",
            r"\foreach \y/\lab in {.05/{.05},.10/{.10},.15/{.15},.20/{.20},.25/{.25}} {\draw (0,\y)--(-.008,\y) node[left] {\small $\lab$};}",
            rf"\draw[very thick,planner] plot[smooth] coordinates {{{' '.join(upper)}}};",
            rf"\draw[very thick,private] plot[smooth] coordinates {{{' '.join(lower2)}}};",
            rf"\draw[dashed,market] plot[smooth] coordinates {{{' '.join(lower4)}}};",
            rf"\draw[dotted,inktwo,very thick] plot[smooth] coordinates {{{' '.join(lower8)}}};",
            r"\node[planner,anchor=west] at (.73,.205) {planner $pq$};",
            r"\node[private,anchor=west] at (.73,.093) {$N=2$};",
            r"\node[market,anchor=west] at (.73,.132) {$N=4$};",
            r"\node[inktwo,anchor=west] at (.73,.163) {$N=8$};",
            r"\node[align=center,fill=white,draw,rounded corners] at (.50,.065) {all-common equilibrium below planner boundary\\between each $A_0(N,p)$ curve and $B_0(p)$};",
            r"\end{tikzpicture}",
            r"\caption{The exact all-common trap region. The upper curve is the planner's first-source threshold $B_0=p(1-p)$; lower curves are private thresholds $A_0=p(1-p)(N-1)/N$. The vertical width is $p(1-p)/N$.}",
            r"\label{fig:trap-region}",
            _artifact_note(["two_agent", "analytic"], ["DD-C-0051", "DD-C-0057"], paths),
            r"\end{figure}",
            "",
        ]
    )


def _selected_rows(census: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in census if row["accuracy"] == "2/3"]


def _grid_figure(
    rows: list[dict[str, Any]],
    value_name: str,
    caption: str,
    label: str,
    paths: list[Path],
) -> str:
    costs = ["0", "1/24", "1/12", "1/8", "1/6", "1/4"]
    by_key = {(int(row["agents"]), str(row["cost"])): row for row in rows}
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0052, DD-C-0057",
        r"\begin{figure}[t]\centering\small",
        r"\setlength{\tabcolsep}{7pt}",
        r"\begin{tabular}{c" + "c" * len(costs) + "}",
        r"\toprule $N\backslash c$ & " + " & ".join(f"${cost}$" for cost in costs) + r"\\\midrule",
    ]
    for n in range(2, 9):
        values = []
        for cost in costs:
            row = by_key[(n, cost)]
            if value_name == "equilibrium":
                value = min(int(cell["k"]) for cell in row["cells"] if cell["weak_equilibrium"])
            elif value_name == "planner":
                value = max(int(k) for k in row["planner_k"])
            else:
                value = int(row["independence_gap"])
            values.append(str(value))
        lines.append(f"{n} & " + " & ".join(values) + r"\\")
    lines.extend(
        [
            r"\bottomrule\end{tabular}",
            rf"\caption{{{caption}}}",
            rf"\label{{{label}}}",
            _artifact_note(["finite_n", "analytic"], ["DD-C-0052", "DD-C-0057"], paths),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _gap_grid(
    rows: list[dict[str, Any]], kind: str, caption: str, label: str, paths: list[Path]
) -> str:
    costs = ["0", "1/24", "1/12", "1/8", "1/6", "1/4"]
    by_key = {(int(row["agents"]), str(row["cost"])): row for row in rows}
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0052, DD-C-0057",
        r"\begin{figure}[t]\centering\scriptsize",
        r"\setlength{\tabcolsep}{5pt}",
        r"\begin{tabular}{c" + "c" * len(costs) + "}",
        r"\toprule $N\backslash c$ & " + " & ".join(f"${cost}$" for cost in costs) + r"\\\midrule",
    ]
    for n in range(2, 9):
        values = []
        for cost in costs:
            row = by_key[(n, cost)]
            equilibrium_k = min(int(cell["k"]) for cell in row["cells"] if cell["weak_equilibrium"])
            planner_k = max(int(k) for k in row["planner_k"])
            cells = {int(cell["k"]): cell for cell in row["cells"]}
            if kind == "discovery":
                value = Fraction(cells[planner_k]["gross_discovery"]) - Fraction(
                    cells[equilibrium_k]["gross_discovery"]
                )
            else:
                value = Fraction(cells[planner_k]["net_value"]) - Fraction(
                    cells[equilibrium_k]["net_value"]
                )
            values.append(f"${value}$")
        lines.append(f"{n} & " + " & ".join(values) + r"\\")
    lines.extend(
        [
            r"\bottomrule\end{tabular}",
            rf"\caption{{{caption}}}",
            rf"\label{{{label}}}",
            _artifact_note(["finite_n", "analytic"], ["DD-C-0052", "DD-C-0057"], paths),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _intervention_figure(mechanism: dict[str, Any], paths: list[Path]) -> str:
    return "\n".join(
        [
            "% Generated evidence asset; do not edit by hand.",
            "% Claims: DD-C-0051, DD-C-0053, DD-C-0057",
            r"\begin{figure}[t]\centering",
            r"\begin{tikzpicture}[node distance=7mm and 8mm,every node/.style={align=center,font=\small}]",
            r"\node[draw,rounded corners,fill=consensus!10,text width=3.2cm] (base) {Equal-split source choice\\all common can persist\\discovery $2/3$ at $p=2/3$};",
            r"\node[draw,rounded corners,fill=planner!10,text width=3.2cm,right=of base] (assign) {Assign one independent source\\planner count repaired\\discovery $8/9$};",
            r"\node[draw,rounded corners,fill=private!10,text width=3.2cm,right=of assign] (alloc) {Add differentiated allocation\\separate model reaches\\discovery $11/12$};",
            r"\draw[->,very thick] (base)--(assign);",
            r"\draw[->,very thick] (assign)--(alloc);",
            r"\node[draw,rounded corners,fill=market!8,text width=10.7cm,below=of assign] (reward) {DD-006B can strictly implement truthful differentiated behavior in 16 of 60 normalized rows, but requires external subsidy and does not itself solve endogenous source purchase.};",
            r"\draw[->] (reward)--(alloc);",
            r"\end{tikzpicture}",
            rf"\caption{{Interventions repair different margins. DD-006B's maximum exact strict margin is ${mechanism['maximum_margin']}$ and best strict discovery is ${mechanism['best_strict_discovery']}$; those results use a different two-agent observability/transfer model.}}",
            r"\label{fig:interventions}",
            _artifact_note(
                ["two_agent", "mechanism", "analytic"],
                ["DD-C-0051", "DD-C-0053", "DD-C-0057"],
                paths,
            ),
            r"\end{figure}",
            "",
        ]
    )


def _atlas_figure(rows: list[dict[str, Any]], paths: list[Path]) -> str:
    selected = [
        row
        for row in rows
        if row["architecture_id"] in {"A145", "A199", "A209", "A210", "A229", "A254"}
    ]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0054",
        r"\begin{figure}[t]\centering\scriptsize",
        r"\begin{tabularx}{\textwidth}{lXXXXX}",
        r"\toprule ID & Disclosure/allocation & Reward & Discovery & Net value & Boundary\\\midrule",
    ]
    for row in selected:
        boundary = (
            "strict subsidized"
            if row["truthfulness"] == "strict"
            else "weak mechanism"
            if row["truthfulness"] == "weak"
            else "protocol/selection"
        )
        lines.append(
            f"{row['architecture_id']} & {row['disclosure']}/{row['allocation']} & "
            f"{row['reward']} & ${row['discovery']}$ & ${row['social_net_value']}$ & "
            f"{boundary}\\\\"
        )
    lines.extend(
        [
            r"\bottomrule\end{tabularx}",
            r"\caption{Acquisition-related slice of the bounded DD-009 Architecture Atlas. Every row uses two independent channels and cost $1/4$; changing disclosure, allocation, timing, and rewards changes discovery, net value, and incentive status. This is not a universal architecture ranking.}",
            r"\label{fig:atlas-slice}",
            _artifact_note(["atlas"], ["DD-C-0054"], paths),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _experiment_map(hypotheses: list[dict[str, Any]], paths: list[Path]) -> str:
    primary = [row for row in hypotheses if row["role"] == "primary"]
    secondary = [row for row in hypotheses if row["role"] == "secondary"]
    return "\n".join(
        [
            "% Generated evidence asset; do not edit by hand.",
            "% Claim: DD-C-0056",
            r"\begin{figure}[t]\centering",
            r"\begin{tikzpicture}[node distance=8mm and 11mm,every node/.style={align=center,font=\small}]",
            r"\node[draw,rounded corners,fill=planner!10,text width=3.2cm] (factors) {20 treatment cells\\acquisition, attribution, disclosure, timing, reward};",
            rf"\node[draw,rounded corners,fill=private!10,text width=3.0cm,right=of factors] (primary) {{{len(primary)} primary hypotheses\\acquisition, truth, action diversity, discovery}};",
            rf"\node[draw,rounded corners,fill=market!10,text width=3.0cm,right=of primary] (secondary) {{{len(secondary)} secondary hypotheses\\precision and interaction}};",
            r"\draw[->,very thick] (factors)--(primary);",
            r"\draw[->,very thick] (primary)--(secondary);",
            r"\node[draw,rounded corners,fill=consensus!8,text width=9.6cm,below=of primary] (warning) {Synthetic response scenarios and power calculations only. No participants were recruited; no human data were collected; no experiment was conducted.};",
            r"\draw[->] (factors)--(warning); \draw[->] (primary)--(warning); \draw[->] (secondary)--(warning);",
            r"\end{tikzpicture}",
            r"\caption{DD-011 maps exact-model mechanisms into experimental predictions without turning them into empirical effects. The design is preregistration-ready, not preregistered or deployed.}",
            r"\label{fig:experiment-map}",
            _artifact_note(["experiment"], ["DD-C-0056"], paths),
            r"\end{figure}",
            "",
        ]
    )


def _evidence_table(paths: list[Path]) -> str:
    return "\n".join(
        [
            "% Generated evidence asset; do not edit by hand.",
            "% Claims: DD-C-0051, DD-C-0052, DD-C-0053, DD-C-0054, DD-C-0056, DD-C-0057, DD-C-0058",
            r"\begin{table}[t]\centering\small",
            r"\caption{Evidence layers used in this paper. Aggregation does not promote a claim's status.}",
            r"\label{tab:evidence-status}",
            r"\begin{tabularx}{\textwidth}{lXll}",
            r"\toprule Object & Result & Evidence category & Boundary\\\midrule",
            r"DD-008 & Two-agent trap interval & exact bounded grid & one frozen fixture family\\",
            r"DD-008A & $N=2,\ldots,8$ source counts & exact finite census & registered rational grid\\",
            r"DD-008B & decreasing thresholds and count characterization & analytic theorem & frozen homogeneous model\\",
            r"DD-008B & interior over-acquisition witness & exact negative result & one rational fixture\\",
            r"DD-006B & 16 strict mechanism rows & exhaustive exact class & subsidized, bounded transfers\\",
            r"DD-009 & 20 coherent architectures & bounded exact atlas & 288 declared cells only\\",
            r"DD-011 & design and power rows & synthetic estimate & no human experiment\\",
            r"\bottomrule\end{tabularx}",
            _artifact_note(
                ["two_agent", "finite_n", "analytic", "mechanism", "atlas", "experiment"],
                [
                    "DD-C-0051",
                    "DD-C-0052",
                    "DD-C-0053",
                    "DD-C-0054",
                    "DD-C-0056",
                    "DD-C-0057",
                    "DD-C-0058",
                ],
                paths,
            ),
            r"\end{table}",
            "",
        ]
    )


def _source_epoch(root: Path) -> str:
    manifest = _json(root / "results/verified" / RUNS["two_agent"] / "manifest.json")
    started = datetime.fromisoformat(str(manifest["started_utc"]).replace("Z", "+00:00"))
    return str(int(started.timestamp()))


def build(root: Path) -> dict[str, object]:
    paper = root / "papers/common-source-trap"
    generated = paper / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    sources = {
        "two_agent": _checked_output(root, "two_agent", "outputs/source-choice-grid.json"),
        "finite_n": _checked_output(root, "finite_n", "outputs/n-agent-census.json"),
        "analytic_thresholds": _checked_output(root, "analytic", "outputs/thresholds.json"),
        "analytic_summary": _checked_output(root, "analytic", "outputs/summary.json"),
        "mechanism": _checked_output(root, "mechanism", "outputs/joint-mechanism-summary.json"),
        "atlas": _checked_output(root, "atlas", "outputs/architectures.json"),
        "experiment": _checked_output(root, "experiment", "outputs/hypotheses.json"),
    }
    census = _json(sources["finite_n"])
    selected = _selected_rows(census)
    assets = {
        "trap-region.tex": _trap_region([sources["two_agent"], sources["analytic_thresholds"]]),
        "equilibrium-counts.tex": _grid_figure(
            selected,
            "equilibrium",
            "Minimum weak-equilibrium independent-source count on the registered $p=2/3$ DD-008A grid.",
            "fig:equilibrium-counts",
            [sources["finite_n"], sources["analytic_thresholds"]],
        ),
        "planner-counts.tex": _grid_figure(
            selected,
            "planner",
            "Maximum planner-optimal independent-source count on the same registered grid.",
            "fig:planner-counts",
            [sources["finite_n"], sources["analytic_thresholds"]],
        ),
        "independence-gap.tex": _grid_figure(
            selected,
            "gap",
            "Registered independence gap: maximum planner count minus minimum weak-equilibrium count.",
            "fig:independence-gap",
            [sources["finite_n"], sources["analytic_thresholds"]],
        ),
        "discovery-gap.tex": _gap_grid(
            selected,
            "discovery",
            "Gross discovery at the maximum planner count minus gross discovery at the minimum weak-equilibrium count. Negative cells are retained.",
            "fig:discovery-gap",
            [sources["finite_n"], sources["analytic_thresholds"]],
        ),
        "welfare-gap.tex": _gap_grid(
            selected,
            "welfare",
            "Planner net value minus net value at the minimum weak-equilibrium count. The planner definition makes every entry weakly nonnegative.",
            "fig:welfare-gap",
            [sources["finite_n"], sources["analytic_thresholds"]],
        ),
        "interventions.tex": _intervention_figure(
            _json(sources["mechanism"]),
            [sources["two_agent"], sources["mechanism"], sources["analytic_summary"]],
        ),
        "atlas-slice.tex": _atlas_figure(_json(sources["atlas"]), [sources["atlas"]]),
        "experiment-map.tex": _experiment_map(
            _json(sources["experiment"]), [sources["experiment"]]
        ),
        "evidence-status-table.tex": _evidence_table(list(sources.values())),
    }
    for name, content in assets.items():
        (generated / name).write_text(content, encoding="utf-8")
    shutil.copy2(root / "bibliography/references.bib", generated / "references.bib")

    source = (paper / "main.tex").read_text(encoding="utf-8")
    known_claims = {
        item["id"]
        for item in yaml.safe_load((root / "claims/claims.yml").read_text(encoding="utf-8"))[
            "claims"
        ]
    }
    missing_claims = (
        set(re.findall(r"DD-C-\d{4}", source + "\n".join(assets.values()))) - known_claims
    )
    bib = (generated / "references.bib").read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"^@\w+\{([^,]+),", bib, flags=re.MULTILINE))
    citations = {
        key.strip()
        for group in re.findall(r"\\cite[tp]?\{([^}]+)\}", source)
        for key in group.split(",")
    }
    required_sections = [
        "Introduction",
        "Related literature",
        "Model",
        "The two-agent Common-Source Trap",
        "Finite-team classification",
        "General finite-team thresholds",
        "Planner comparison",
        "Acquisition, discovery, and welfare gaps",
        "Institutional remedies",
        "Joint truth and allocation mechanisms",
        "Architecture Atlas implications",
        "Experimental predictions",
        "Limitations",
        "Conclusion",
    ]
    if missing_claims or citations - bib_keys:
        raise RuntimeError(
            f"unresolved paper references: claims={missing_claims}, citations={citations - bib_keys}"
        )
    if any(rf"\section{{{title}}}" not in source for title in required_sections):
        raise RuntimeError("required Common-Source Trap section missing")
    expected_inputs = [rf"\input{{generated/{name}}}" for name in assets]
    if any(item not in source for item in expected_inputs):
        raise RuntimeError("generated evidence asset is not included")

    build_dir = paper / "build"
    build_dir.mkdir(exist_ok=True)
    pdfs: list[bytes] = []
    logs: list[str] = []
    for _ in range(2):
        with tempfile.TemporaryDirectory(dir=build_dir) as temporary:
            result = subprocess.run(
                ["tectonic", "main.tex", "--outdir", temporary],
                cwd=paper,
                env={**os.environ, "SOURCE_DATE_EPOCH": _source_epoch(root)},
                capture_output=True,
                text=True,
            )
            log = result.stdout + result.stderr
            logs.append(log)
            if result.returncode or re.search(
                r"undefined (?:reference|citation)|overfull \\hbox", log, re.I
            ):
                raise RuntimeError("Common-Source Trap compilation failed\n" + log[-4000:])
            pdfs.append((Path(temporary) / "main.pdf").read_bytes())
    hashes = [hashlib.sha256(pdf).hexdigest() for pdf in pdfs]
    if hashes[0] != hashes[1]:
        raise RuntimeError("Common-Source Trap PDF is not byte reproducible")
    output = paper / "The_Common_Source_Trap.pdf"
    output.write_bytes(pdfs[-1])
    (paper / "build.log").write_text("\n\n===== deterministic rebuild =====\n\n".join(logs))
    info = subprocess.check_output(["pdfinfo", output], text=True)
    page_match = re.search(r"^Pages:\s+(\d+)$", info, re.M)
    if not page_match:
        raise RuntimeError("pdfinfo did not report page count")
    page_count = int(page_match.group(1))
    if page_count not in range(20, 33):
        raise RuntimeError(f"paper page count outside 20--32 target: {page_count}")
    provenance = {
        "schema_version": 1,
        "generator": GENERATOR,
        "source_runs": RUNS,
        "inputs": {str(path.relative_to(root)): _sha256(path) for path in sources.values()},
        "generated_assets": {name: _sha256(generated / name) for name in assets},
    }
    (generated / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n"
    )
    validation = {
        "schema_version": 1,
        "generator": GENERATOR,
        "compile_exit_status": 0,
        "page_count": page_count,
        "pdf_sha256": hashes[0],
        "byte_reproducible_two_builds": True,
        "unresolved_references_citations_or_overfull_boxes": False,
        "claim_ids_resolved": True,
        "citation_keys_resolved": True,
        "provenance_validated": True,
        "source_runs": RUNS,
        "generated_assets": sorted(assets),
        "inputs": provenance["inputs"],
    }
    (paper / "validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return validation


def main() -> None:
    validation = build(repository_root())
    print(
        "Common-Source Trap paper passed: "
        f"{validation['page_count']} pages, PDF {str(validation['pdf_sha256'])[:12]}"
    )


if __name__ == "__main__":
    main()
