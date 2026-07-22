# ruff: noqa: E501 -- generated LaTeX is kept readable and auditable.

"""Generate evidence assets and build the Threshold Discovery working paper."""

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

GENERATOR = "distributed_discovery.papers.build_threshold_discovery"
RUNS = {
    "threshold": "20260722T021526Z_DD-016_00271ff8_123b2809e3",
    "equilibrium": "20260722T024032Z_DD-017_033452f6_3d2c74fdfb",
    "dynamic": "20260722T043713Z_DD-015_92d53ac1_0e7cf1ec0a",
    "dynamic_threshold": "20260722T044453Z_DD-015_34bc4379_33e1da478b",
    "mechanisms": "20260722T051847Z_DD-018_a193f602_3b3ddac173",
    "benchmark": "20260722T054447Z_DD-010_d265e480_6930915b02",
    "experiment": "20260722T061958Z_DD-011_5743ccba_19b6517655",
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


def _decimal(value: str) -> str:
    return f"{float(Fraction(value)):.4f}"


def _threshold_phase(rows: list[dict[str, Any]], path: Path) -> str:
    series = {
        "private": "private_clue_following",
        "common": "common_deterministic_mode_discovery",
        "mixed": "tied_mode_mixed_discovery",
        "planner": "planner_discovery",
    }
    colors = {"private": "private", "common": "consensus", "mixed": "market", "planner": "planner"}
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0073, DD-C-0074",
        r"\begin{figure}[t]\centering",
        r"\begin{tikzpicture}[x=1.05cm,y=6.8cm]",
        r"\draw[->] (0.7,0)--(8.45,0) node[right] {$\tau$};",
        r"\draw[->] (0.8,0)--(0.8,.91) node[above] {discovery};",
    ]
    for name, field in series.items():
        coordinates = " ".join(
            f"({row['threshold']},{float(Fraction(row[field])):.6f})" for row in rows
        )
        lines.append(
            rf"\draw[very thick,{colors[name]},mark=*] plot coordinates {{{coordinates}}};"
        )
    lines.extend(
        [
            r"\foreach \x in {1,...,8} {\draw (\x,0)--(\x,-.012) node[below] {\x};}",
            r"\node[anchor=west,private] at (1.1,.88) {private clue-following};",
            r"\node[anchor=west,planner] at (3.7,.64) {planner};",
            r"\node[anchor=west,consensus] at (5.0,.43) {common mode};",
            r"\node[anchor=west,market] at (5.0,.31) {selected tied-mode mix};",
            r"\end{tikzpicture}",
            r"\caption{Exact canonical threshold phase diagram for $M=16$, $N=8$, and clue accuracy $1/5$. Common mode and the registered tied-mode mixture trail private clue-following at thresholds one and two, then exceed it at thresholds three through eight. The deterministic planner remains the comparison frontier.}",
            r"\label{fig:threshold-phase}",
            _note(["threshold"], ["DD-C-0073", "DD-C-0074"], [path]),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _threshold_table(rows: list[dict[str, Any]], path: Path) -> str:
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0073, DD-C-0074",
        r"\begin{table}[t]\centering\scriptsize",
        r"\begin{tabular}{rrrrrrl}",
        r"\toprule $\tau$ & private & common & mixed & planner & viable teams & planner relation\\\midrule",
    ]
    for row in rows:
        relation = (
            "strictly higher" if row["diversification_dominates_common_mode"] else "ties common"
        )
        lines.append(
            f"{row['threshold']} & {_decimal(row['private_clue_following'])} & {_decimal(row['common_deterministic_mode_discovery'])} & {_decimal(row['tied_mode_mixed_discovery'])} & {_decimal(row['planner_discovery'])} & {_decimal(row['expected_viable_candidates'])} & {relation}\\\\"
        )
    lines.extend(
        [
            r"\bottomrule\end{tabular}",
            r"\caption{Displayed decimals summarize exact rational values. Exact fractions in the immutable source determine every comparison.}",
            r"\label{tab:threshold-phase}",
            _note(["threshold"], ["DD-C-0073", "DD-C-0074"], [path]),
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def _equilibrium_census(summary: dict[str, Any], path: Path) -> str:
    rows = [
        ("Registered games", summary["game_count"], "bounded exact census"),
        ("Occupancy states", summary["occupancy_state_count"], "primary enumeration"),
        ("Labeled profiles", summary["labeled_profiles"], "independent reproduction"),
        (
            "Games with zero worst-equilibrium discovery",
            summary["zero_worst_equilibrium_games"],
            "DD-C-0077",
        ),
        (
            "Games with no pairwise-strict-stable equilibrium",
            summary["no_pairwise_stable_equilibrium_games"],
            "DD-C-0078",
        ),
        (
            r"Games with no exact-size-$\tau$-stable equilibrium",
            summary["no_tau_stable_equilibrium_games"],
            "DD-C-0078",
        ),
        (
            "Registered tied-mode failures",
            summary["tied_mode_mixed_failures"],
            r"all at $\tau=1$",
        ),
    ]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0075 through DD-C-0078",
        r"\begin{figure}[t]\centering\small",
        r"\begin{tabularx}{\textwidth}{Yrr}",
        r"\toprule quantity & count & interpretation\\\midrule",
    ]
    lines.extend(f"{label} & {value} & {meaning}\\\\" for label, value, meaning in rows)
    lines.extend(
        [
            r"\bottomrule\end{tabularx}",
            r"\caption{The equilibrium problem is not a single selection rule. Weak pure Nash, one symmetric mixture, pairwise blocking, and exact-size minimum-team blocking are separate registered objects.}",
            r"\label{fig:equilibrium-census}",
            _note(["equilibrium"], ["DD-C-0075", "DD-C-0076", "DD-C-0077", "DD-C-0078"], [path]),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _dynamic_summary(dynamic: dict[str, Any], threshold: dict[str, Any], paths: list[Path]) -> str:
    rows = [
        ("Baseline parameter cells", dynamic["grid_cells"], "exact"),
        (
            "Baseline labeled paths",
            dynamic["labeled_target_signal_paths"],
            "independently reproduced",
        ),
        (
            "Planner-better objective rows",
            dynamic["planner_strictly_better_rows"],
            "bounded result",
        ),
        (
            "Stopping reduces expected actions",
            dynamic["stopping_reduces_expected_actions_rows"],
            "all baseline cells",
        ),
        (
            "Visibility increases fixed-budget herding",
            dynamic["visibility_increases_herding_fixed_rows"],
            "bounded negative result",
        ),
        (
            "Visibility increases fixed-budget discovery",
            dynamic["visibility_increases_discovery_fixed_rows"],
            "none",
        ),
        (
            "Threshold-two parameter cells",
            threshold["parameter_cells"],
            "separate planner-only extension",
        ),
        (
            "Threshold-two labeled paths",
            threshold["labeled_target_signal_paths"],
            "independently reproduced",
        ),
    ]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0079 through DD-C-0082",
        r"\begin{figure}[t]\centering\small",
        r"\begin{tabularx}{\textwidth}{Yrr}",
        r"\toprule dynamic object & count & evidence boundary\\\midrule",
    ]
    lines.extend(f"{label} & {value} & {boundary}\\\\" for label, value, boundary in rows)
    lines.extend(
        [
            r"\bottomrule\end{tabularx}",
            r"\caption{Dynamic attention results preserve two distinct games. The autonomous baseline has full duplicate credit; the threshold-two extension is planner-only and does not establish a threshold-game equilibrium.}",
            r"\label{fig:dynamic-summary}",
            _note(
                ["dynamic", "dynamic_threshold"],
                ["DD-C-0079", "DD-C-0080", "DD-C-0081", "DD-C-0082"],
                paths,
            ),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _mechanism_table(rows: list[dict[str, Any]], path: Path) -> str:
    names = []
    for name in dict.fromkeys(str(row["name"]) for row in rows):
        group = [row for row in rows if row["name"] == name]
        implemented = sum(bool(row["implements_planner_portfolio"]) for row in group)
        strict = sum(row["strict_unilateral_obedience"] is True for row in group)
        pair = sum(row["pairwise_strict_stable"] is True for row in group)
        multiplicities = [
            row["equilibrium_multiplicity"]
            for row in group
            if isinstance(row["equilibrium_multiplicity"], int)
        ]
        multiplicity = (
            "n/a" if not multiplicities else f"{min(multiplicities)}--{max(multiplicities)}"
        )
        names.append((name.replace("-", " "), implemented, strict, pair, multiplicity))
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0083 through DD-C-0086",
        r"\begin{table}[t]\centering\scriptsize",
        r"\begin{tabularx}{\textwidth}{Yrrrr}",
        r"\toprule mechanism & planner rows & strict unilateral & pair stable & pure multiplicity range\\\midrule",
    ]
    lines.extend(
        f"{name} & {implemented}/5 & {strict}/5 & {pair}/5 & {multiplicity}\\\\"
        for name, implemented, strict, pair, multiplicity in names
    )
    lines.extend(
        [
            r"\bottomrule\end{tabularx}",
            r"\caption{Exact five-fixture mechanism census. Authoritative and binding-within-pair rows use not-applicable labels where unilateral obedience is not a meaningful test. Common-posterior input also makes report truthfulness not applicable.}",
            r"\label{tab:mechanisms}",
            _note(["mechanisms"], ["DD-C-0083", "DD-C-0084", "DD-C-0085", "DD-C-0086"], [path]),
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def _integration_table(
    benchmark: dict[str, Any], experiment: dict[str, Any], paths: list[Path]
) -> str:
    rows = [
        ("DiscoveryBench v3 tasks", benchmark["task_count"], "exact registry"),
        ("DiscoveryBench v3 protocols", benchmark["protocol_count"], "capability declared"),
        ("DiscoveryBench v3 metrics", benchmark["metric_count"], "no composite score"),
        ("Compatible exact pairs", benchmark["compatible_pairs"], "independently reproduced"),
        ("Explicit exclusions", benchmark["excluded_pairs"], "not imputed"),
        ("Synthetic treatment cells", experiment["treatment_cells"], "no human data"),
        ("Synthetic power rows", experiment["power_rows"], "seeded Monte Carlo"),
        (
            "Retained large-sample failures",
            experiment["calibration_failures_retained"],
            "published negative calibration",
        ),
    ]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0087, DD-C-0088",
        r"\begin{figure}[t]\centering\small",
        r"\begin{tabularx}{\textwidth}{Yrr}",
        r"\toprule integration object & count & status\\\midrule",
    ]
    lines.extend(f"{label} & {value} & {status}\\\\" for label, value, status in rows)
    lines.extend(
        [
            r"\bottomrule\end{tabularx}",
            r"\caption{Benchmark and experimental integration preserve capability exclusions and calibration failures. The synthetic package supplies conditional predictions only; it is not behavioral or empirical evidence.}",
            r"\label{fig:integration}",
            _note(["benchmark", "experiment"], ["DD-C-0087", "DD-C-0088"], paths),
            r"\end{figure}",
            "",
        ]
    )
    return "\n".join(lines)


def _prediction_table(
    power_rows: list[dict[str, Any]], hypotheses: list[dict[str, Any]], paths: list[Path]
) -> str:
    selected = [
        row
        for row in power_rows
        if row.get("scenario_id") == "S1-rational"
        and int(row.get("sample_size", 0)) == 960
        and row.get("hypothesis_id") in {f"H{index}" for index in range(15, 21)}
    ]
    selected.sort(key=lambda row: int(str(row["hypothesis_id"])[1:]))
    outcomes = {
        str(row["hypothesis_id"]): str(row["outcome"]).replace("_", " ") for row in hypotheses
    }
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claim: DD-C-0088",
        r"\begin{table}[t]\centering\small",
        r"\begin{tabular}{llll}",
        r"\toprule hypothesis & registered outcome & $N$ & estimated power\\\midrule",
    ]
    for row in selected:
        contrast = outcomes[str(row["hypothesis_id"])]
        lines.append(
            f"{row['hypothesis_id']} & {contrast} & {row['sample_size']} & {row['power']}\\\\"
        )
    lines.extend(
        [
            r"\bottomrule\end{tabular}",
            r"\caption{Program V4 synthetic predictions in the favorable rational-response scenario. Power is conditional on declared effects and a normal approximation; it is not evidence that any effect occurs in people.}",
            r"\label{tab:predictions}",
            _note(["experiment"], ["DD-C-0088"], paths),
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def _evidence_table(paths: list[Path]) -> str:
    rows = [
        ("Planner value and payoff identities", "DD-C-0071--0072", "theorem/identity", "verified"),
        (
            "Canonical threshold census",
            "DD-C-0073--0074",
            "bounded exact",
            "independently reproduced",
        ),
        ("Pure and selected mixed equilibrium", "DD-C-0075--0076", "theorems", "verified"),
        (
            "Welfare and coalition census",
            "DD-C-0077--0078",
            "bounded exact",
            "independently reproduced",
        ),
        ("Dynamic attention", "DD-C-0079--0082", "proof/exact/negative", "verified or reproduced"),
        ("Minimum-team mechanisms", "DD-C-0083--0086", "bounded exact", "verified"),
        ("DiscoveryBench v3", "DD-C-0087", "bounded exact", "independently reproduced"),
        ("Synthetic predictions", "DD-C-0088", "Monte Carlo estimate", "verified"),
        ("Human behavior", "none", "empirical", "not studied"),
    ]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        "% Claims: DD-C-0071 through DD-C-0088",
        r"\begin{table}[t]\centering\scriptsize",
        r"\begin{tabularx}{\textwidth}{YYll}",
        r"\toprule result family & claim IDs & evidence category & status\\\midrule",
    ]
    lines.extend(" & ".join(row) + r"\\" for row in rows)
    lines.extend(
        [
            r"\bottomrule\end{tabularx}",
            r"\caption{Evidence status attaches to statements, not to the paper as a whole.}",
            r"\label{tab:evidence-status}",
            _note(list(RUNS), ["DD-C-0071--DD-C-0088"], paths),
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def _source_epoch(root: Path) -> str:
    manifest = _json(root / "results/verified" / RUNS["threshold"] / "manifest.json")
    started = datetime.fromisoformat(str(manifest["started_utc"]).replace("Z", "+00:00"))
    return str(int(started.timestamp()))


def build(root: Path) -> dict[str, object]:
    paper = root / "papers/threshold-discovery"
    generated = paper / "generated"
    generated.mkdir(parents=True, exist_ok=True)
    sources = {
        "threshold_phase": _checked(root, "threshold", "outputs/threshold-phase-diagram.json"),
        "threshold_metrics": _checked(root, "threshold", "outputs/canonical-metrics.json"),
        "equilibrium_summary": _checked(root, "equilibrium", "outputs/summary.json"),
        "dynamic_summary": _checked(root, "dynamic", "outputs/summary.json"),
        "dynamic_threshold_summary": _checked(
            root, "dynamic_threshold", "outputs/threshold-two-summary.json"
        ),
        "mechanism_summary": _checked(root, "mechanisms", "outputs/summary.json"),
        "mechanism_census": _checked(root, "mechanisms", "outputs/mechanism-census.json"),
        "benchmark_summary": _checked(root, "benchmark", "outputs/benchmark-summary.json"),
        "experiment_summary": _checked(root, "experiment", "outputs/synthetic-summary.json"),
        "experiment_hypotheses": _checked(root, "experiment", "outputs/hypotheses.json"),
        "experiment_power": _checked(root, "experiment", "outputs/power-table.json"),
    }
    threshold_rows = _json(sources["threshold_phase"])
    equilibrium = _json(sources["equilibrium_summary"])
    dynamic = _json(sources["dynamic_summary"])
    dynamic_threshold = _json(sources["dynamic_threshold_summary"])
    mechanisms = _json(sources["mechanism_census"])
    benchmark = _json(sources["benchmark_summary"])
    experiment = _json(sources["experiment_summary"])
    hypotheses = _json(sources["experiment_hypotheses"])
    power = _json(sources["experiment_power"])
    power_rows = power.get("rows", power) if isinstance(power, dict) else power
    assets = {
        "threshold-phase.tex": _threshold_phase(threshold_rows, sources["threshold_phase"]),
        "threshold-table.tex": _threshold_table(threshold_rows, sources["threshold_phase"]),
        "equilibrium-census.tex": _equilibrium_census(equilibrium, sources["equilibrium_summary"]),
        "dynamic-summary.tex": _dynamic_summary(
            dynamic,
            dynamic_threshold,
            [sources["dynamic_summary"], sources["dynamic_threshold_summary"]],
        ),
        "mechanism-table.tex": _mechanism_table(mechanisms, sources["mechanism_census"]),
        "integration-table.tex": _integration_table(
            benchmark, experiment, [sources["benchmark_summary"], sources["experiment_summary"]]
        ),
        "prediction-table.tex": _prediction_table(
            power_rows,
            hypotheses,
            [sources["experiment_power"], sources["experiment_hypotheses"]],
        ),
        "evidence-status.tex": _evidence_table(list(sources.values())),
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
        "Threshold discovery model",
        "Minimum viable teams",
        "Strategic equilibrium and selection",
        "Dynamic attention",
        "Mechanisms for team formation",
        "Benchmark and synthetic predictions",
        "Institutional implications",
        "Limitations",
        "Conclusion",
    ]
    if mentioned - claims or citations - bib_keys:
        raise RuntimeError(
            f"unresolved paper references: claims={mentioned - claims}, citations={citations - bib_keys}"
        )
    if any(rf"\section{{{title}}}" not in source for title in sections):
        raise RuntimeError("required Threshold Discovery section missing")
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
            log = re.sub(r"`[^`]+/build/tmp[^/]+/main\.pdf`", "`<build>/main.pdf`", log)
            logs.append(log)
            if result.returncode or re.search(
                r"undefined (?:reference|citation)|overfull \\hbox", log, re.I
            ):
                raise RuntimeError("Threshold Discovery compilation failed\n" + log[-5000:])
            pdfs.append((Path(temporary) / "main.pdf").read_bytes())
    hashes = [hashlib.sha256(pdf).hexdigest() for pdf in pdfs]
    if hashes[0] != hashes[1]:
        raise RuntimeError("Threshold Discovery PDF is not byte reproducible")
    output = paper / "Threshold_Discovery.pdf"
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
        f"Threshold Discovery paper passed: {result['page_count']} pages, PDF {str(result['pdf_sha256'])[:12]}"
    )


if __name__ == "__main__":
    main()
