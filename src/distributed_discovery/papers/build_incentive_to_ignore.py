# ruff: noqa: E501 -- generated LaTeX is kept readable and auditable.

"""Generate evidence assets and build The Incentive to Ignore working paper."""

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

GENERATOR = "distributed_discovery.papers.build_incentive_to_ignore"
RUNS = {
    "attention": "20260721T212943Z_DD-012_9ed0928e_4a3f1ba62b",
    "audience": "20260721T215811Z_DD-013_09c07448_cdac4fb512",
    "conditional": "20260721T222047Z_DD-014_f5f099a8_ea0276dd16",
    "experiment": "20260721T185647Z_DD-011_fa0271d9_fcaa647c55",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _checked(root: Path, key: str, relative: str) -> Path:
    run_id = RUNS[key]
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
        or _sha(path) != expected
    ):
        raise RuntimeError(f"invalid paper source: {run_id}/{relative}")
    return path


def _note(keys: list[str], claims: list[str], paths: list[Path]) -> str:
    return (
        rf"\ArtifactNote{{Source runs: \path{{{', '.join(RUNS[key] for key in keys)}}}; "
        rf"claims: {', '.join(claims)}; generator: \path{{{GENERATOR}}}; input "
        rf"SHA-256 prefixes: \texttt{{{', '.join(_sha(path)[:12] for path in paths)}}}.}}"
    )


def _find_cell(cells: list[dict[str, Any]], n: int, p: str, q: str) -> dict[str, Any]:
    return next(
        cell
        for cell in cells
        if int(cell["agents"]) == n
        and str(cell["private_accuracy"]) == p
        and str(cell["shared_accuracy"]) == q
    )


def _social_frontier(cells: list[dict[str, Any]], paths: list[Path]) -> str:
    cell = _find_cell(cells, 4, "1/2", "3/4")
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0059, DD-C-0060, DD-C-0061",
        r"\begin{figure}[t]\centering",
        r"\begin{tikzpicture}[x=1.45cm,y=6cm]",
        r"\draw[->] (0,0)--(4.35,0) node[right] {$k$};",
        r"\draw[->] (0,.40)--(0,1.02) node[above] {$G_4(k)$};",
    ]
    coordinates = []
    for row in cell["profiles"]:
        coordinates.append(f"({row['attenders']},{float(Fraction(row['discovery'])):.6f})")
    lines.extend(
        [
            rf"\draw[very thick,planner,mark=*] plot coordinates {{{' '.join(coordinates)}}};",
            r"\draw[dashed] (1,.40)--(1,1.0);",
            r"\node[anchor=west,planner] at (1.1,.79) {one reader is optimal};",
            r"\node[anchor=west,consensus] at (2.1,.51) {duplicate shared use destroys channels};",
            r"\foreach \x in {0,...,4} {\draw (\x,0)--(\x,-.015) node[below] {\x};}",
            r"\end{tikzpicture}",
            r"\caption{Restricted social discovery by the number $k$ of shared-signal followers for $N=4$, $p=1/2$, and $q=3/4$. First use raises discovery; every duplicate use lowers it.}",
            r"\label{fig:social-frontier}",
            _note(["attention"], ["DD-C-0059", "DD-C-0060", "DD-C-0061"], paths),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _attention_phase(cells: list[dict[str, Any]], paths: list[Path]) -> str:
    selected = [cell for cell in cells if int(cell["agents"]) == 4]
    accuracies = ["1/3", "1/2", "2/3", "3/4", "5/6"]
    by_key = {(cell["private_accuracy"], cell["shared_accuracy"]): cell for cell in selected}
    label = {
        "efficient-attention": "E",
        "excessive-attention": "X",
        "insufficient-attention": "I",
        "mixed-attention-wedge": "M",
    }
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0060, DD-C-0061",
        r"\begin{figure}[t]\centering\scriptsize",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{c" + "c" * 5 + "}",
        r"\toprule $p\backslash q$ & "
        + " & ".join(f"${value}$" for value in accuracies)
        + r"\\\midrule",
    ]
    for p in accuracies:
        values = []
        for q in accuracies:
            cell = by_key[(p, q)]
            equilibrium = ",".join(str(value) for value in cell["equilibria"])
            optimum = ",".join(str(value) for value in cell["social_optima"])
            values.append(
                f"{label.get(cell['category'], cell['category'][0].upper())}$_{{{equilibrium};{optimum}}}$"
            )
        lines.append(f"${p}$ & " + " & ".join(values) + r"\\")
    lines.extend(
        [
            r"\bottomrule\end{tabular}}",
            r"\caption{Attention-wedge phase map at $N=4$. Each cell reports category$_{\text{weak equilibrium counts};\text{planner counts}}$. E is efficient; X is excessive shared-signal use; M records equilibrium multiplicity with a discovery difference.}",
            r"\label{fig:attention-phase}",
            _note(["attention"], ["DD-C-0060", "DD-C-0061"], paths),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _equilibrium_optimum(cells: list[dict[str, Any]], paths: list[Path]) -> str:
    rows = [
        cell
        for cell in cells
        if cell["private_accuracy"] == "1/2" and cell["shared_accuracy"] == "3/4"
    ]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0059, DD-C-0060, DD-C-0061",
        r"\begin{figure}[t]\centering\small",
        r"\begin{tabular}{rrrrl}",
        r"\toprule $N$ & planner $k$ & weak equilibrium $k$ & all-attend equilibrium? & exact discovery wedge\\\midrule",
    ]
    for cell in rows:
        profiles = {int(row["attenders"]): Fraction(row["discovery"]) for row in cell["profiles"]}
        optimum = int(cell["social_optima"][0])
        best_equilibrium = max(cell["equilibria"], key=lambda count: profiles[int(count)])
        wedge = profiles[optimum] - profiles[int(best_equilibrium)]
        lines.append(
            f"{cell['agents']} & {optimum} & {','.join(str(v) for v in cell['equilibria'])} & "
            f"{'yes' if int(cell['agents']) in cell['equilibria'] else 'no'} & ${wedge}$\\\\"
        )
    lines.extend(
        [
            r"\bottomrule\end{tabular}",
            r"\caption{Planner and weak equal-split attention counts along the registered $p=1/2,q=3/4$ slice. The table separates multiplicity from the best-equilibrium discovery gap.}",
            r"\label{fig:equilibrium-optimum}",
            _note(["attention"], ["DD-C-0059", "DD-C-0060", "DD-C-0061"], paths),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _audience_frontier(cells: list[dict[str, Any]], paths: list[Path]) -> str:
    cell = _find_cell(cells, 4, "1/2", "3/4")
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0062, DD-C-0065",
        r"\begin{figure}[t]\centering\small",
        r"\begin{tabular}{rrrrrr}",
        r"\toprule audience & discovery & quality & distinct actions & voluntary weak use & binding optimum?\\\midrule",
    ]
    for row, voluntary in zip(cell["binding_audiences"], cell["voluntary_audiences"], strict=True):
        lines.append(
            f"{row['audience']} & ${row['discovery']}$ & ${row['action_quality']}$ & ${row['expected_distinct_actions']}$ & "
            f"{','.join(str(value) for value in voluntary['weak_equilibria'])} & {'yes' if row['audience'] in cell['binding_optima'] else 'no'}\\\\"
        )
    lines.extend(
        [
            r"\bottomrule\end{tabular}",
            r"\caption{Binding audience frontier and voluntary use for $N=4$, $p=1/2$, $q=3/4$. Audience, use, and action assignment are distinct institutional variables.}",
            r"\label{fig:audience-frontier}",
            _note(["audience"], ["DD-C-0062", "DD-C-0065"], paths),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _precision_publicity(cells: list[dict[str, Any]], paths: list[Path]) -> str:
    cell = _find_cell(cells, 4, "1/2", "3/4")
    rows = [row for row in cell["garbling_rows"] if row["audience"] in {1, 2, 4}]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0062, DD-C-0063",
        r"\begin{figure}[t]\centering\small",
        r"\begin{tabular}{rrrrl}",
        r"\toprule delivered accuracy $g$ & audience & discovery & binding optimum & relation\\\midrule",
    ]
    for row in rows:
        lines.append(
            f"${row['delivered_accuracy']}$ & {row['audience']} & ${row['discovery']}$ & ${cell['binding_audiences'][1]['discovery']}$ & "
            f"{'strictly below' if row['strictly_dominated_by_binding_optimum'] else 'ties'}\\\\"
        )
    lines.extend(
        [
            r"\bottomrule\end{tabular}",
            r"\caption{Precision versus publicity on a registered slice. Garbling does not repair over-publicity within the declared symmetric family; full precision to one recipient weakly dominates every listed design.}",
            r"\label{fig:precision-publicity}",
            _note(["audience"], ["DD-C-0062", "DD-C-0063"], paths),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _conditional_map(cells: list[dict[str, Any]], paths: list[Path]) -> str:
    selected = [cell for cell in cells if int(cell["agents"]) == 4]
    accuracies = ["1/3", "1/2", "2/3", "3/4", "5/6"]
    by_key = {(cell["private_accuracy"], cell["shared_accuracy"]): cell for cell in selected}
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0066, DD-C-0067, DD-C-0068",
        r"\begin{figure}[t]\centering\scriptsize",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{c" + "c" * 5 + "}",
        r"\toprule $p\backslash q$ & "
        + " & ".join(f"${value}$" for value in accuracies)
        + r"\\\midrule",
    ]
    for p in accuracies:
        values = []
        for q in accuracies:
            cell = by_key[(p, q)]
            planner = "/".join(
                "".join(str(v) for v in counts) for counts in cell["planner_profiles"]
            )
            marker = "W" if Fraction(cell["equilibrium_wedge"]) > 0 else "E"
            values.append(f"{marker}$_{{{planner}}}$")
        lines.append(f"${p}$ & " + " & ".join(values) + r"\\")
    lines.extend(
        [
            r"\bottomrule\end{tabular}}",
            r"\caption{Conditional-policy phase map at $N=4$. Planner profiles are triples (private-dominant, public-dominant, contrarian); W marks a positive best-equilibrium wedge and E marks zero. Long entries record exact planner ties at uninformative private accuracy.}",
            r"\label{fig:conditional-map}",
            _note(["conditional"], ["DD-C-0066", "DD-C-0067", "DD-C-0068"], paths),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _mechanisms(
    attention: list[dict[str, Any]], audience: list[dict[str, Any]], paths: list[Path]
) -> str:
    a = _find_cell(attention, 4, "1/2", "3/4")
    b = _find_cell(audience, 4, "1/2", "3/4")
    rows = []
    for name, outcome in a["reward_equilibria"].items():
        weak = (
            outcome.get("weak")
            if outcome.get("weak") is not None
            else outcome.get("binding_implemented_counts")
        )
        rows.append((name, ",".join(str(value) for value in weak), "DD-012 reward/access rule"))
    rows.append(
        (
            "binding exclusive delivery",
            ",".join(str(value) for value in b["binding_optima"]),
            "DD-013 access assignment",
        )
    )
    rows.append(
        (
            "public universal pooling",
            ",".join(str(value) for value in b["mechanisms"]["public_universal_pooling"]["weak"]),
            "DD-013 ex-post balanced public rule",
        )
    )
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0061, DD-C-0064",
        r"\begin{figure}[t]\centering\scriptsize",
        r"\begin{tabularx}{\textwidth}{lclY}",
        r"\toprule rule/institution & implemented or weak counts & evidence & boundary\\\midrule",
    ]
    for name, counts, boundary in rows:
        lines.append(f"{name.replace('-', ' ')} & {counts} & exact & {boundary}\\\\")
    lines.extend(
        [
            r"\bottomrule\end{tabularx}",
            r"\caption{Mechanism comparison on $N=4$, $p=1/2$, $q=3/4$. Identical count outcomes can rely on different access, observability, commitment, and budget assumptions.}",
            r"\label{fig:mechanisms}",
            _note(["attention", "audience"], ["DD-C-0061", "DD-C-0064"], paths),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _experiment_map(paths: list[Path]) -> str:
    rows = [
        (
            "Broadcast versus one reader",
            "public-signal use; discovery",
            "broadcast increases use; one-reader access raises discovery when $q>p$",
            "prediction from DD-C-0059/DD-C-0062",
        ),
        (
            "Recommendation versus license",
            "attention count; compliance",
            "nonbinding advice need not implement the optimum; binding access does",
            "institutional prediction",
        ),
        (
            "Equal split versus pooling",
            "attention count; payoff",
            "pooling aligns unilateral count changes with discovery",
            "theorem DD-C-0064",
        ),
        (
            "Conditional recommendation",
            "policy category; discovery",
            "conditional policies do not universally remove the wedge",
            "bounded prediction DD-C-0067",
        ),
    ]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0056, DD-C-0059, DD-C-0062, DD-C-0064, DD-C-0067",
        r"\begin{figure}[t]\centering\scriptsize",
        r"\begin{tabularx}{\textwidth}{YYYY}",
        r"\toprule contrast & outcomes & directional prediction & evidence label\\\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(row) + r"\\")
    lines.extend(
        [
            r"\bottomrule\end{tabularx}",
            r"\caption{Experimental treatment map. These are model-derived predictions and registered contrasts, not observations. No participants were recruited and no human experiment was conducted.}",
            r"\label{fig:experiment-map}",
            _note(
                ["attention", "audience", "conditional", "experiment"],
                ["DD-C-0056", "DD-C-0059", "DD-C-0062", "DD-C-0064", "DD-C-0067"],
                paths,
            ),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _evidence_table(paths: list[Path]) -> str:
    rows = [
        ("One-reader discovery", "DD-C-0059", "theorem", "verified"),
        ("Equal-split thresholds", "DD-C-0060", "theorem", "verified"),
        ("Reward census", "DD-C-0061", "bounded exact", "independently reproduced"),
        ("Audience and garbling", "DD-C-0062--0063", "theorems", "verified"),
        ("Universal pooling", "DD-C-0064", "theorem", "verified"),
        ("Voluntary audience", "DD-C-0065", "bounded exact", "independently reproduced"),
        ("Conditional planner", "DD-C-0066", "theorem", "verified"),
        ("Conditional equilibrium", "DD-C-0067", "bounded exact", "independently reproduced"),
        ("Raw-policy boundary", "DD-C-0068", "negative result", "independently reproduced"),
        ("Treatment effects", "none", "prediction", "not observed"),
    ]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0059 through DD-C-0068",
        r"\begin{table}[t]\centering\scriptsize",
        r"\begin{tabularx}{\textwidth}{YYll}",
        r"\toprule result & claim & evidence category & status\\\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(row) + r"\\")
    lines.extend(
        [
            r"\bottomrule\end{tabularx}",
            r"\caption{Evidence status attaches to each statement, not to the paper as a whole.}",
            r"\label{tab:evidence-status}",
            _note(["attention", "audience", "conditional"], ["DD-C-0059--DD-C-0068"], paths),
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def _source_epoch(root: Path) -> str:
    manifest = _json(root / "results/verified" / RUNS["attention"] / "manifest.json")
    started = datetime.fromisoformat(str(manifest["started_utc"]).replace("Z", "+00:00"))
    return str(int(started.timestamp()))


def build(root: Path) -> dict[str, object]:
    paper = root / "papers/incentive-to-ignore"
    generated = paper / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    sources = {
        "attention_census": _checked(root, "attention", "outputs/attention-census.json"),
        "attention_phase": _checked(root, "attention", "outputs/phase-map.json"),
        "attention_summary": _checked(root, "attention", "outputs/summary.json"),
        "audience_frontier": _checked(root, "audience", "outputs/audience-frontier.json"),
        "audience_summary": _checked(root, "audience", "outputs/summary.json"),
        "conditional_census": _checked(root, "conditional", "outputs/policy-census.json"),
        "conditional_phase": _checked(root, "conditional", "outputs/policy-phase-map.json"),
        "conditional_summary": _checked(root, "conditional", "outputs/summary.json"),
        "experiment_hypotheses": _checked(root, "experiment", "outputs/hypotheses.json"),
    }
    attention_census = _json(sources["attention_census"])
    attention_phase = _json(sources["attention_phase"])
    audience = _json(sources["audience_frontier"])
    conditional_phase = _json(sources["conditional_phase"])
    assets = {
        "social-frontier.tex": _social_frontier(attention_census, [sources["attention_census"]]),
        "attention-phase.tex": _attention_phase(attention_phase, [sources["attention_phase"]]),
        "equilibrium-optimum.tex": _equilibrium_optimum(
            attention_census, [sources["attention_census"]]
        ),
        "audience-frontier.tex": _audience_frontier(audience, [sources["audience_frontier"]]),
        "precision-publicity.tex": _precision_publicity(audience, [sources["audience_frontier"]]),
        "conditional-map.tex": _conditional_map(conditional_phase, [sources["conditional_phase"]]),
        "mechanisms.tex": _mechanisms(
            attention_phase, audience, [sources["attention_phase"], sources["audience_frontier"]]
        ),
        "experiment-map.tex": _experiment_map(
            [
                sources["attention_summary"],
                sources["audience_summary"],
                sources["conditional_summary"],
                sources["experiment_hypotheses"],
            ]
        ),
        "evidence-status.tex": _evidence_table(
            [
                sources["attention_summary"],
                sources["audience_summary"],
                sources["conditional_summary"],
            ]
        ),
    }
    for name, content in assets.items():
        (generated / name).write_text(content, encoding="utf-8")
    shutil.copy2(root / "bibliography/references.bib", generated / "references.bib")
    source = (paper / "main.tex").read_text(encoding="utf-8")
    claims = {
        item["id"]
        for item in yaml.safe_load((root / "claims/claims.yml").read_text(encoding="utf-8"))[
            "claims"
        ]
    }
    mentioned = set(re.findall(r"DD-C-\d{4}", source + "\n".join(assets.values())))
    bib = (generated / "references.bib").read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"^@\w+\{([^,]+),", bib, flags=re.MULTILINE))
    citations = {
        key.strip()
        for group in re.findall(r"\\cite[tp]?\{([^}]+)\}", source)
        for key in group.split(",")
    }
    sections = [
        "Introduction",
        "Related literature",
        "Model",
        "First-use value and duplicate-use loss",
        "Private attention equilibrium",
        "The attention wedge",
        "Audience design",
        "Information firewalls and implementation",
        "Conditional attention",
        "Institutional implications",
        "Experimental predictions",
        "Limitations",
        "Conclusion",
    ]
    if mentioned - claims or citations - bib_keys:
        raise RuntimeError(
            f"unresolved paper references: claims={mentioned - claims}, citations={citations - bib_keys}"
        )
    if any(rf"\section{{{title}}}" not in source for title in sections):
        raise RuntimeError("required Incentive to Ignore section missing")
    if any(rf"\input{{generated/{name}}}" not in source for name in assets):
        raise RuntimeError("generated paper asset is not included")
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
                raise RuntimeError("Incentive to Ignore compilation failed\n" + log[-5000:])
            pdfs.append((Path(temporary) / "main.pdf").read_bytes())
    hashes = [hashlib.sha256(pdf).hexdigest() for pdf in pdfs]
    if hashes[0] != hashes[1]:
        raise RuntimeError("Incentive to Ignore PDF is not byte reproducible")
    output = paper / "The_Incentive_to_Ignore.pdf"
    output.write_bytes(pdfs[-1])
    (paper / "build.log").write_text(
        "\n\n===== deterministic rebuild =====\n\n".join(logs), encoding="utf-8"
    )
    info = subprocess.check_output(["pdfinfo", output], text=True)
    match = re.search(r"^Pages:\s+(\d+)$", info, re.M)
    if not match:
        raise RuntimeError("pdfinfo did not report page count")
    pages = int(match.group(1))
    if pages not in range(20, 33):
        raise RuntimeError(f"paper page count outside 20--32 target: {pages}")
    provenance = {
        "schema_version": 1,
        "generator": GENERATOR,
        "source_runs": RUNS,
        "inputs": {str(path.relative_to(root)): _sha(path) for path in sources.values()},
        "generated_assets": {name: _sha(generated / name) for name in assets},
    }
    (generated / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    validation = {
        "schema_version": 1,
        "generator": GENERATOR,
        "compile_exit_status": 0,
        "page_count": pages,
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
    result = build(repository_root())
    print(
        f"Incentive to Ignore paper passed: {result['page_count']} pages, PDF {str(result['pdf_sha256'])[:12]}"
    )


if __name__ == "__main__":
    main()
