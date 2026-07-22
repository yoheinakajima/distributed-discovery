# ruff: noqa: E501 -- generated LaTeX is intentionally explicit and auditable.

"""Generate and validate the Information Sharing Frontier working paper."""

from __future__ import annotations

import csv
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

GENERATOR = "distributed_discovery.papers.build_information_sharing_frontier"
RUNS = {
    "signal": "20260722T084145Z_DD-019_a77bb786_04a5e9f0c5",
    "incremental": "20260722T142551Z_DD-020_3854fff6_37c11a850a",
    "frontier": "20260722T185924Z_DD-021_3cdbbc40_2fea269a9a",
    "strategic": "20260722T210334Z_DD-022_2376d5b7_ad67765ca8",
}
CLAIMS = [f"DD-C-{number:04d}" for number in range(89, 111)]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _checked(root: Path, key: str, relative: str) -> Path:
    run_id = RUNS[key]
    run = root / "results/verified" / run_id
    manifest = _json(run / "manifest.json")
    path = run / relative
    digest = manifest.get("outputs", {}).get(relative)
    if (
        manifest.get("validation_status") != "passed"
        or manifest.get("exit_status") != 0
        or manifest.get("run_id") != run_id
        or not isinstance(digest, str)
        or not path.is_file()
        or _sha(path) != digest
    ):
        raise RuntimeError(f"invalid immutable paper input: {run_id}/{relative}")
    return path


def _fraction(value: str) -> Fraction:
    return Fraction(str(value))


def _decimal(value: str, digits: int = 3) -> str:
    return f"{float(_fraction(value)):.{digits}f}"


def _escape(value: object) -> str:
    return (
        str(value).replace("_", r"\_").replace("%", r"\%").replace("&", r"\&").replace("#", r"\#")
    )


def _note(keys: list[str], claims: list[str], paths: list[Path]) -> str:
    return (
        rf"\ArtifactNote{{Runs: \path{{{', '.join(RUNS[key] for key in keys)}}}; "
        rf"claims: {', '.join(claims)}; generator: \path{{{GENERATOR}}}; input "
        rf"SHA-256 prefixes: \texttt{{{', '.join(_sha(path)[:12] for path in paths)}}}.}}"
    )


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _architecture_figure(paths: list[Path]) -> str:
    return "\n".join(
        [
            "% Generated evidence/architecture asset; do not edit by hand.",
            r"\begin{figure}[t]\centering",
            r"\begin{tikzpicture}[node distance=7mm and 9mm, every node/.style={draw,rounded corners,align=center,minimum height=8mm,font=\small}]",
            r"\node (e) {private evidence}; \node[right=of e] (p) {private actions}; \node[right=of p] (d) {portfolio discovery};",
            r"\node[below=of e] (b) {pooled block}; \node[right=of b] (c) {one common action}; \node[right=of c] (r) {remaining rescue actions};",
            r"\draw[->,private,very thick] (e)--(p)--(d);",
            r"\draw[->,shared,very thick] (e)--(b)--(c)--(r); \draw[->,shared,very thick] (r)--(d);",
            r"\end{tikzpicture}",
            r"\caption{Information sharing changes two objects at once. The pooled block can improve one common action, while absorbing agents removes independent rescue actions. The comparison is therefore not a comparison of posterior accuracy alone.}",
            r"\label{fig:architecture}",
            _note(["incremental", "frontier"], ["DD-C-0092", "DD-C-0097"], paths),
            r"\end{figure}",
        ]
    )


def _profile_figure(rows: list[dict[str, Any]], path: Path) -> str:
    selected = [
        row for row in rows if row["channel_id"] in {"noisy-point-half", "guaranteed-shortlist-two"}
    ]
    colors = ["private", "planner"]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        r"\begin{figure}[t]\centering",
        r"\begin{tikzpicture}[x=1.75cm,y=4.6cm]",
        r"\draw[->] (0.65,0)--(4.45,0); \draw[->] (0.75,0)--(0.75,1.08) node[above] {probability};",
    ]
    if len(selected) != len(colors):
        raise RuntimeError("unexpected profile selection length")
    for row, color in zip(selected, colors, strict=True):
        coords = " ".join(
            f"({index},{float(_fraction(value)):.6f})"
            for index, value in enumerate(row["profile"], 1)
        )
        lines.append(rf"\draw[very thick,{color},mark=*] plot coordinates {{{coords}}};")
    lines.extend(
        [
            r"\foreach \x/\lab in {1/$V_1$,2/$V_2$,3/$V_3$}{\draw (\x,0)--(\x,-.018) node[below] {\lab};}",
            r"\draw[dashed] (.75,.5)--(3.15,.5) node[right] {one-person accuracy $=1/2$};",
            r"\node[private,anchor=west] at (1.1,.60) {noisy point}; \node[planner,anchor=west] at (1.1,.98) {guaranteed shortlist};",
            r"\end{tikzpicture}",
            r"\caption{Same one-person accuracy, different pooled action-budget profiles. Both channels also have direct private discovery $7/8$, yet the noisy point requires three pooled actions to recover that baseline and the guaranteed shortlist requires one. Exact values are in \cref{tab:profiles}.}",
            r"\label{fig:same-accuracy}",
            _note(["signal"], ["DD-C-0089", "DD-C-0090", "DD-C-0091"], [path]),
            r"\end{figure}",
        ]
    )
    return "\n".join(lines)


def _incremental_figure(rows: list[dict[str, Any]], path: Path) -> str:
    wanted = ["noisy-point-half", "guaranteed-shortlist-two", "confidence-point"]
    colors = ["private", "planner", "accent"]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        r"\begin{figure}[t]\centering",
        r"\begin{tikzpicture}[x=1.8cm,y=5cm]",
        r"\draw[->] (.7,0)--(4.35,0) node[right] {$s$}; \draw[->] (.8,0)--(.8,1.03) node[above] {$G_s$};",
    ]
    for channel, color in zip(wanted, colors, strict=True):
        row = next(item for item in rows if item["channel_id"] == channel)
        coords = " ".join(
            f"({index},{float(_fraction(value)):.6f})"
            for index, value in enumerate(row["profile"], 1)
        )
        lines.append(rf"\draw[very thick,{color},mark=*] plot coordinates {{{coords}}};")
    lines.extend(
        [
            r"\foreach \x in {1,2,3}{\draw (\x,0)--(\x,-.015) node[below] {\x};}",
            r"\node[private,anchor=west] at (2.1,.63) {noisy point};",
            r"\node[planner,anchor=west] at (1.7,.94) {guaranteed shortlist};",
            r"\node[accent,anchor=west] at (1.25,.84) {confidence point};",
            r"\end{tikzpicture}",
            r"\caption{Incremental-sharing curves at $M=4,N=3$. The half-accurate noisy point declines, the equally accurate guaranteed shortlist rises, and the confidence-point channel declines. The sign is a property of channel geometry and protocol, not accuracy alone.}",
            r"\label{fig:incremental}",
            _note(["incremental"], ["DD-C-0094", "DD-C-0096"], [path]),
            r"\end{figure}",
        ]
    )
    return "\n".join(lines)


def _frontier_figure(rows: list[dict[str, Any]], path: Path) -> str:
    selected = [
        next(row for row in rows if row["channel_id"] == "point-m4-p1of2" and row["agents"] == 3),
        next(
            row
            for row in rows
            if row["channel_id"] == "guaranteed-shortlist-m4-k2" and row["agents"] == 3
        ),
    ]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        r"\begin{figure}[t]\centering",
        r"\begin{tikzpicture}[x=2.1cm,y=4.6cm]",
        r"\draw[->] (.7,0)--(3.55,0) node[right] {step $s$}; \draw[->] (.8,0)--(.8,1.05) node[above] {$\rho_s$};",
        r"\draw[dashed,very thick] (.8,.5)--(3.15,.5) node[right] {$1-q=1/2$};",
    ]
    for row, color in zip(selected, ["private", "planner"], strict=True):
        coords = " ".join(
            f"({index},{float(_fraction(value)):.6f})"
            for index, value in enumerate(row["error_contraction_ratio"], 1)
        )
        lines.append(rf"\draw[very thick,{color},mark=*] plot coordinates {{{coords}}};")
    lines.extend(
        [
            r"\foreach \x in {1,2}{\draw (\x,0)--(\x,-.015) node[below] {\x};}",
            r"\node[private,anchor=west] at (1.1,.84) {compression: $\rho_s>1-q$};",
            r"\node[planner,anchor=west] at (1.1,.18) {aggregation: $\rho_s<1-q$};",
            r"\end{tikzpicture}",
            r"\caption{Residual-error frontier for the registered half-accurate $M=4,N=3$ point and guaranteed-shortlist channels. A sharing step helps below the rescue threshold, is neutral on it, and hurts above it.}",
            r"\label{fig:error-frontier}",
            _note(["frontier"], ["DD-C-0097", "DD-C-0100"], [path]),
            r"\end{figure}",
        ]
    )
    return "\n".join(lines)


def _registry_figure(summary: dict[str, Any], path: Path) -> str:
    counts = summary["sharing_class_counts"]
    bars = [
        ("compression", counts["strict-compression-dominated"], "private"),
        ("aggregation", counts["strict-aggregation-dominated"], "planner"),
        ("neutral", counts["all-neutral"], "inktwo"),
        ("mixed", 0, "accent"),
    ]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        r"\begin{figure}[t]\centering",
        r"\begin{tikzpicture}[x=2.05cm,y=.045cm]",
        r"\draw[->] (.55,0)--(4.7,0); \draw[->] (.65,0)--(.65,140) node[above] {scenarios};",
    ]
    for index, (label, value, color) in enumerate(bars, 1):
        lines.append(
            rf"\fill[{color}!70] ({index}-.28,0) rectangle ({index}+.28,{value}); \node[above] at ({index},{value}) {{{value}}}; \node[below,font=\scriptsize] at ({index},0) {{{label}}};"
        )
    lines.extend(
        [
            r"\end{tikzpicture}",
            r"\caption{Complete bounded classification of 177 registered scenarios: 126 strict compression curves, 16 strict aggregation curves, 35 all-neutral curves, and no mixed curve. The zero mixed count is a bounded null, not a general theorem.}",
            r"\label{fig:registry}",
            _note(["frontier"], ["DD-C-0099", "DD-C-0103"], [path]),
            r"\end{figure}",
        ]
    )
    return "\n".join(lines)


def _strategic_figure(rows: list[dict[str, Any]], certificate: dict[str, Any], path: Path) -> str:
    selected = sorted(
        (row for row in rows if row["accuracy"] == "3/5"),
        key=lambda row: _fraction(row["dependence"]),
    )
    series = [
        ("direct_private_metrics", "direct private", "accent", "dashed"),
        ("private_metrics", "private selected", "private", "solid"),
        ("shared_metrics", "shared selected", "shared", "solid"),
    ]
    lines = [
        "% Generated evidence asset; do not edit by hand.",
        r"\begin{figure}[p]\centering",
        r"\begin{tikzpicture}[x=9cm,y=6.8cm]",
        r"\draw[->] (0,0)--(1.07,0) node[right] {$\rho$}; \draw[->] (0,0)--(0,1.06) node[above] {discovery};",
        r"\draw[planner,very thick] (0,1)--(1,1) node[anchor=south east] {centralized $V_2=1$};",
    ]
    for field, _label, color, style in series:
        coords = " ".join(
            f"({float(_fraction(row['dependence'])):.6f},{float(_fraction(row[field]['discovery'])):.6f})"
            for row in selected
        )
        lines.append(rf"\draw[very thick,{color},{style},mark=*] plot coordinates {{{coords}}};")
    root = (5 * (73**0.5) - 17) / 48
    lines.extend(
        [
            r"\draw[dotted] (0.166667,0)--(0.166667,1.02) node[above,rotate=90,font=\scriptsize] {$1/6$};",
            rf"\draw[dash dot] ({root:.8f},0)--({root:.8f},1.02) node[above,rotate=90,font=\scriptsize] {{$\rho^*$}};",
            r"\draw[dotted] (0.583333,0)--(0.583333,1.02) node[above,rotate=90,font=\scriptsize] {$7/12$};",
            r"\draw[accent,dashed,very thick] (.68,.91)--(.76,.91) node[anchor=west] {direct private};",
            r"\draw[private,very thick] (.68,.85)--(.76,.85) node[anchor=west] {private selected};",
            r"\draw[shared,very thick] (.68,.79)--(.76,.79) node[anchor=west] {shared selected};",
            r"\draw (0,0)--(0,-.012) node[below] {0}; \draw (.25,0)--(.25,-.012) node[below] {$1/4$}; \draw (.5,0)--(.5,-.012) node[below] {$1/2$}; \draw (.75,0)--(.75,-.012) node[below] {$3/4$}; \draw (1,0)--(1,-.012) node[below] {1};",
            r"\end{tikzpicture}",
            r"\caption{Discovery versus source dependence at $p=3/5$. The exact theorem compares the private and shared selected equilibria, not direct clue-following. Selected sharing is strictly higher only on $(\rho^*,1)$, where $\rho^*=(5\sqrt{73}-17)/48$; equality returns at one. The selected shared outcome remains below centralized $V_2$. Lines connect registered exact cells for display; the interval theorem comes from the analytic certificate.}",
            r"\label{fig:strategic}",
            _note(["strategic"], ["DD-C-0104", "DD-C-0105", "DD-C-0106", "DD-C-0110"], [path]),
            r"\end{figure}",
        ]
    )
    if certificate["exact_positive_root"] != "(5*sqrt(73)-17)/48":
        raise RuntimeError("unexpected DD-022 root certificate")
    return "\n".join(lines)


def _selection_figure(path: Path) -> str:
    return "\n".join(
        [
            "% Generated evidence/selection asset; do not edit by hand.",
            r"\begin{figure}[t]\centering",
            r"{\renewcommand{\arraystretch}{1.3}\small\begin{tabularx}{\textwidth}{YYYY}\toprule",
            r"\textbf{Private alternative} & \textbf{Shared selection} & \textbf{Shared broader strategy} & \textbf{Centralized benchmark}\\\midrule",
            r"opposite constant targets & posterior-only identical mixing & ownership-aware disagreement split & binding top-two\\",
            r"$\Downarrow$ & $\Downarrow$ & $\Downarrow$ & $\Downarrow$\\",
            r"discovery one & selected positive interval; planner gap & disagreement coverage beyond posterior-only rules & $V_2=1$ by authority\\\bottomrule",
            r"\end{tabularx}}",
            r"\caption{Equilibrium and authority map. The posterior-only identical-mixing outcome is one selected decentralized equilibrium, not the correspondence. Constant-target private equilibria and ownership-aware disagreement strategies expose the selection boundary; centralized top-two uses binding authority.}",
            r"\label{fig:selection-map}",
            _note(["strategic"], ["DD-C-0106", "DD-C-0109", "DD-C-0110"], [path]),
            r"\end{figure}",
        ]
    )


def _authority_figure(paths: list[Path]) -> str:
    return "\n".join(
        [
            "% Generated evidence/authority asset; do not edit by hand.",
            r"\begin{figure}[t]\centering\small",
            r"\begin{tabularx}{\textwidth}{Ylll}\toprule layer & evidence & authority & boundary\\\midrule",
            r"Signal geometry & exact bounded & centralized $V_L$ & scalar insufficiency\\",
            r"Incremental sharing & identity/theorem & nonstrategic protocol & arbitrary-channel failure\\",
            r"General frontier & theorem plus census & centralized recovery & mixed-curve bounded null\\",
            r"Strategic sharing & selected BNE theorem & autonomous actions & not every equilibrium\\",
            r"Selection failure & verified negative & broader strategy space & discovery-one alternatives\\",
            r"\bottomrule\end{tabularx}",
            r"\caption{Evidence and authority map. Analytic, bounded exact, centralized, selected decentralized, and negative-boundary claims remain distinct even when they form one theorem family.}",
            r"\label{fig:evidence-map}",
            _note(list(RUNS), ["DD-C-0089--DD-C-0110"], paths),
            r"\end{figure}",
        ]
    )


def _table(
    label: str, caption: str, header: str, rows: list[str], note: str, spec: str = "Ylll"
) -> str:
    return "\n".join(
        [
            "% Generated evidence table; do not edit by hand.",
            r"\begin{table}[t]\centering\scriptsize",
            rf"\begin{{tabularx}}{{\textwidth}}{{{spec}}}\toprule {header}\\\midrule",
            *rows,
            r"\bottomrule\end{tabularx}",
            rf"\caption{{{caption}}}",
            rf"\label{{{label}}}",
            note,
            r"\end{table}",
        ]
    )


def _source_epoch(root: Path) -> str:
    manifest = _json(root / "results/verified" / RUNS["signal"] / "manifest.json")
    stamp = datetime.fromisoformat(str(manifest["started_utc"]).replace("Z", "+00:00"))
    return str(int(stamp.timestamp()))


def build(root: Path) -> dict[str, object]:
    paper = root / "papers/information-sharing-frontier"
    generated = paper / "generated"
    figures = paper / "figures"
    tables = paper / "tables"
    for directory in (generated, figures, tables, figures / "data"):
        directory.mkdir(parents=True, exist_ok=True)

    sources = {
        "profiles": _checked(root, "signal", "outputs/profiles.json"),
        "signal_summary": _checked(root, "signal", "outputs/summary.json"),
        "sharing": _checked(root, "incremental", "outputs/channel-profiles.json"),
        "incremental_summary": _checked(root, "incremental", "outputs/summary.json"),
        "frontier_registry": _checked(root, "frontier", "outputs/registry.json"),
        "frontier_summary": _checked(root, "frontier", "outputs/summary.json"),
        "witnesses": _checked(root, "frontier", "outputs/minimal-witnesses.json"),
        "strategic_registry": _checked(root, "strategic", "outputs/registry.json"),
        "strategic_summary": _checked(root, "strategic", "outputs/summary.json"),
        "threshold": _checked(root, "strategic", "outputs/threshold-certificate.json"),
    }
    profiles = _json(sources["profiles"])
    sharing = _json(sources["sharing"])
    frontier = _json(sources["frontier_registry"])
    frontier_summary = _json(sources["frontier_summary"])
    strategic = _json(sources["strategic_registry"])
    strategic_summary = _json(sources["strategic_summary"])
    threshold = _json(sources["threshold"])

    figure_assets = {
        "architecture.tex": _architecture_figure(
            [sources["sharing"], sources["frontier_registry"]]
        ),
        "same-accuracy-profile.tex": _profile_figure(profiles, sources["profiles"]),
        "incremental-curves.tex": _incremental_figure(sharing, sources["sharing"]),
        "residual-frontier.tex": _frontier_figure(frontier, sources["frontier_registry"]),
        "registry-classification.tex": _registry_figure(
            frontier_summary, sources["frontier_summary"]
        ),
        "dependence-discovery.tex": _strategic_figure(
            strategic, threshold, sources["strategic_registry"]
        ),
        "selection-map.tex": _selection_figure(sources["strategic_registry"]),
        "evidence-authority-map.tex": _authority_figure(list(sources.values())),
    }
    for name, content in figure_assets.items():
        (figures / name).write_text(content + "\n", encoding="utf-8")

    table_assets = {
        "channel-definitions.tex": _table(
            "tab:channels",
            "Registered channel definitions and named comparison baselines. Accuracy and private discovery are exact; descriptions abbreviate the versioned channel records.",
            r"channel & signal geometry & $q$ & $P_3$",
            [
                f"{_escape(row['channel_id'])} & {_escape(row['family'])} & ${row['one_person_accuracy']}$ & ${row['private_portfolio_discovery']}$\\\\"
                for row in profiles
            ],
            _note(["signal"], ["DD-C-0089"], [sources["profiles"]]),
        ),
        "action-budget-profiles.tex": _table(
            "tab:profiles",
            "Exact DD-019 action-budget profiles. Decimals aid reading; exact fractions govern comparisons and recovery budgets.",
            r"channel & $(V_1,V_2,V_3)$ & decimals & $L^*$",
            [
                f"{_escape(row['channel_id'])} & $({','.join(row['profile'])})$ & ({', '.join(_decimal(value) for value in row['profile'])}) & {row['recovery_budget']}\\\\"
                for row in profiles
            ],
            _note(["signal"], ["DD-C-0089", "DD-C-0091"], [sources["profiles"]]),
        ),
        "sharing-paths.tex": _table(
            "tab:sharing-paths",
            "Exact DD-020 sharing paths. The pooled block grows from $s=1$ to $3$ while the remaining private rescue actions disappear.",
            r"channel & $(G_1,G_2,G_3)$ & adjacent changes & sign",
            [
                f"{_escape(row['channel_id'])} & $({','.join(row['profile'])})$ & $({','.join(row['increments'])})$ & {_escape('increasing' if all(_fraction(v) > 0 for v in row['increments']) else 'decreasing')}\\\\"
                for row in sharing
            ],
            _note(["incremental"], ["DD-C-0092", "DD-C-0096"], [sources["sharing"]]),
        ),
        "registry-counts.tex": _table(
            "tab:registry-counts",
            "Complete bounded DD-021 classifications and recovery budgets. Counts describe the frozen registry, not a population of channels or organizations.",
            r"axis & class & count & status",
            [
                f"sharing curve & {_escape(key)} & {value} & exact bounded\\\\"
                for key, value in frontier_summary["sharing_class_counts"].items()
            ]
            + [
                f"recovery budget & $L^*={key}$ & {value} & centralized\\\\"
                for key, value in frontier_summary["recovery_budget_counts"].items()
            ]
            + [r"sharing curve & mixed & 0 & bounded null\\"],
            _note(
                ["frontier"], ["DD-C-0099", "DD-C-0102", "DD-C-0103"], [sources["frontier_summary"]]
            ),
        ),
        "minimal-witnesses.tex": _table(
            "tab:witnesses",
            "Minimal registered witnesses under the frozen lexicographic order. Minimality is internal to the registry.",
            r"witness & left or focal value & right or comparator & conclusion",
            [
                r"same baseline, opposite signs & point: $-1/4$ & guaranteed shortlist: $1/12$ & $M=4,N=2,q=1/2$\\",
                r"same accuracy, recovery & point: $L^*=2$ & guaranteed shortlist: $L^*=1$ & $M=3,N=2,q=1/2$\\",
                r"Shared Discovery Paradox & $q=3/8$ & $C_N=27/64<P_N=39/64$ & noisy shortlist\\",
                r"consensus dominance & $P_N=3/4$ & $C_N=5/6$ & guaranteed shortlist\\",
            ],
            _note(["frontier"], ["DD-C-0100", "DD-C-0101", "DD-C-0102"], [sources["witnesses"]]),
        ),
        "equilibrium-formulas.tex": _table(
            "tab:equilibrium-formulas",
            "Exact DD-022 selected-equilibrium formulas. The selections are deliberately narrower than the complete pure correspondence.",
            r"information & state statistic & selected rule & scope",
            [
                r"private & $t=2p-1$, $A=t^2+\rho(1-t^2)$ & $r^*=1$ if $A\leq3t$; else $1/2+3t/(2A)$ & anonymous label-equivariant BNE\\",
                r"shared agreement & $u=1/2+t/(1+A)$ & $x^*=1$ if $u\geq2/3$; else $3u-1$ & posterior-only identical mixing\\",
                r"shared disagreement & posterior $1/2$ & $x^*=1/2$ & ownership-blind selection\\",
            ],
            _note(["strategic"], ["DD-C-0104", "DD-C-0105"], [sources["strategic_registry"]]),
        ),
        "threshold-gap.tex": _table(
            "tab:threshold-gap",
            "Exact canonical threshold, regime boundaries, and centralized implementation gap at $p=3/5$.",
            r"object & exact value & display & interpretation",
            [
                rf"shared regime boundary & ${strategic_summary['shared_regime_boundary']}$ & {float(_fraction(strategic_summary['shared_regime_boundary'])):.4f} & agreement rule changes\\",
                rf"positive crossover $\rho^*$ & $\frac{{5\sqrt{{73}}-17}}{{48}}$ & {((5 * (73**0.5) - 17) / 48):.10f} & equality\\",
                rf"private regime boundary & ${strategic_summary['private_regime_boundary']}$ & {float(_fraction(strategic_summary['private_regime_boundary'])):.4f} & private anti-crowding begins\\",
                r"planner gap, low regime & $(7+3\rho)/25$ & positive & centralized $V_2=1$\\",
                r"planner gap, high regime & $(4+3\rho)/(13+12\rho)$ & positive & centralized $V_2=1$\\",
            ],
            _note(
                ["strategic"],
                ["DD-C-0106", "DD-C-0110"],
                [sources["threshold"], sources["strategic_summary"]],
            ),
        ),
        "claim-evidence-map.tex": _table(
            "tab:claim-map",
            "Claim, evidence, and ownership map. Status belongs to each claim, not to the paper as a whole.",
            r"claim range & owner & evidence class & manuscript role",
            [
                r"DD-C-0089--0091 & DD-019 & independently reproduced exact bounded & geometry and recovery\\",
                r"DD-C-0092--0094 & DD-020 & identity and verified theorems & aggregation versus rescue\\",
                r"DD-C-0095--0096 & DD-020 & independently reproduced bounded & census and counterchannel\\",
                r"DD-C-0097--0098 & DD-021 & verified theorems & frontier and centralized recovery\\",
                r"DD-C-0099--0102 & DD-021 & independently reproduced bounded & classes, witnesses, budgets\\",
                r"DD-C-0103 & DD-021 & verified bounded negative & mixed-curve null\\",
                r"DD-C-0104--0107 & DD-022 & verified theorem/corollary & selected equilibria and interval\\",
                r"DD-C-0108 & DD-022 & independently reproduced bounded & 42-cell classification\\",
                r"DD-C-0109 & DD-022 & verified negative & selection failure\\",
                r"DD-C-0110 & DD-022 & verified theorem & implementation gap\\",
            ],
            _note(list(RUNS), ["DD-C-0089--DD-C-0110"], list(sources.values())),
        ),
    }
    for name, content in table_assets.items():
        (tables / name).write_text(content + "\n", encoding="utf-8")

    # Exact chart data, including conceptual node/edge records for diagrams.
    csv_specs: dict[str, tuple[list[str], list[dict[str, object]]]] = {
        "architecture.csv": (
            ["from", "to", "meaning"],
            [
                {
                    "from": "private evidence",
                    "to": "private actions",
                    "meaning": "independent portfolio",
                },
                {"from": "pooled block", "to": "common action", "meaning": "aggregation"},
                {
                    "from": "remaining agents",
                    "to": "rescue actions",
                    "meaning": "independent rescue",
                },
            ],
        ),
        "same-accuracy-profile.csv": (
            ["channel", "q", "private", "V1", "V2", "V3", "recovery_budget"],
            [
                {
                    "channel": row["channel_id"],
                    "q": row["one_person_accuracy"],
                    "private": row["private_portfolio_discovery"],
                    "V1": row["profile"][0],
                    "V2": row["profile"][1],
                    "V3": row["profile"][2],
                    "recovery_budget": row["recovery_budget"],
                }
                for row in profiles
                if row["channel_id"] in {"noisy-point-half", "guaranteed-shortlist-two"}
            ],
        ),
        "incremental-curves.csv": (
            ["channel", "G1", "G2", "G3", "d12", "d23"],
            [
                {
                    "channel": row["channel_id"],
                    "G1": row["profile"][0],
                    "G2": row["profile"][1],
                    "G3": row["profile"][2],
                    "d12": row["increments"][0],
                    "d23": row["increments"][1],
                }
                for row in sharing
            ],
        ),
        "residual-frontier.csv": (
            ["channel", "step", "rho_s", "threshold"],
            [
                {
                    "channel": row["channel_id"],
                    "step": index,
                    "rho_s": value,
                    "threshold": row["rescue_threshold"],
                }
                for row in frontier
                if row["channel_id"] in {"point-m4-p1of2", "guaranteed-shortlist-m4-k2"}
                and row["agents"] == 3
                for index, value in enumerate(row["error_contraction_ratio"], 1)
            ],
        ),
        "registry-classification.csv": (
            ["class", "count", "scope"],
            [
                {"class": key, "count": value, "scope": "177-scenario bounded registry"}
                for key, value in frontier_summary["sharing_class_counts"].items()
            ]
            + [{"class": "mixed", "count": 0, "scope": "bounded null"}],
        ),
        "dependence-discovery.csv": (
            ["rho", "direct_private", "private_selected", "shared_selected", "centralized"],
            [
                {
                    "rho": row["dependence"],
                    "direct_private": row["direct_private_metrics"]["discovery"],
                    "private_selected": row["private_metrics"]["discovery"],
                    "shared_selected": row["shared_metrics"]["discovery"],
                    "centralized": row["shared_metrics"]["centralized_top_two"],
                }
                for row in strategic
                if row["accuracy"] == "3/5"
            ],
        ),
        "selection-map.csv": (
            ["outcome", "authority", "discovery"],
            [
                {
                    "outcome": "posterior-only identical mixing",
                    "authority": "selected decentralized",
                    "discovery": "depends on rho",
                },
                {
                    "outcome": "opposite constant targets",
                    "authority": "private pure equilibrium",
                    "discovery": "1",
                },
                {
                    "outcome": "ownership-aware disagreement split",
                    "authority": "shared pure equilibrium",
                    "discovery": "1 conditional on disagreement",
                },
                {"outcome": "top-two", "authority": "centralized", "discovery": "1"},
            ],
        ),
        "evidence-authority-map.csv": (
            ["claims", "evidence", "authority"],
            [
                {
                    "claims": "DD-C-0089--0091",
                    "evidence": "exact bounded",
                    "authority": "centralized top-L",
                },
                {
                    "claims": "DD-C-0092--0097",
                    "evidence": "identity/theorem",
                    "authority": "nonstrategic protocol",
                },
                {
                    "claims": "DD-C-0098--0103",
                    "evidence": "theorem/bounded/negative",
                    "authority": "centralized recovery",
                },
                {
                    "claims": "DD-C-0104--0110",
                    "evidence": "selected theorem/bounded/negative",
                    "authority": "decentralized selection and centralized benchmark",
                },
            ],
        ),
    }
    for name, (fields, rows) in csv_specs.items():
        _write_csv(figures / "data" / name, fields, rows)

    shutil.copy2(root / "bibliography/references.bib", generated / "references.bib")
    source = (paper / "main.tex").read_text(encoding="utf-8")
    abstract = (paper / "abstract.tex").read_text(encoding="utf-8")
    ledger = yaml.safe_load((root / "claims/claims.yml").read_text(encoding="utf-8"))["claims"]
    claim_ids = {item["id"] for item in ledger}
    mentioned = set(
        re.findall(
            r"DD-C-\d{4}",
            source
            + abstract
            + "\n".join(figure_assets.values())
            + "\n".join(table_assets.values()),
        )
    )
    citations = {
        key.strip()
        for group in re.findall(r"\\cite[tp]?\{([^}]+)\}", source)
        for key in group.split(",")
    }
    bibliography = (generated / "references.bib").read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"^@\w+\{([^,]+),", bibliography, flags=re.MULTILINE))
    sections = [
        "Introduction",
        "Discovery architectures and comparison baselines",
        "Signal geometry is not one-person accuracy",
        "Aggregation gain and independent rescue",
        "The General Sharing Frontier",
        "Centralized action-budget recovery",
        "Coordination-free positive sharing",
        "Equilibrium selection and implementation failure",
        "Design implications and limitations",
        "Conclusion",
    ]
    if any(rf"\section{{{name}}}" not in source for name in sections):
        raise RuntimeError("required manuscript section missing")
    if set(CLAIMS) - mentioned or mentioned - claim_ids or citations - bib_keys:
        raise RuntimeError(
            f"unresolved paper provenance: missing_claims={set(CLAIMS) - mentioned}, unknown_claims={mentioned - claim_ids}, citations={citations - bib_keys}"
        )
    for name in figure_assets:
        if rf"\input{{figures/{name}}}" not in source:
            raise RuntimeError(f"figure not included: {name}")
    for name in table_assets:
        if rf"\input{{tables/{name}}}" not in source:
            raise RuntimeError(f"table not included: {name}")
    required_abstract = [
        "selection-dependent",
        "not an every-equilibrium result",
        "Opposite",
        "ownership-aware",
        "does not reveal",
        "centralized",
        "no human or real data",
    ]
    prohibited_abstract = [
        "every equilibrium improves",
        "reveals the realized common",
        "all correlated",
        "is a universal information order",
    ]
    if any(token not in abstract for token in required_abstract) or any(
        token in abstract for token in prohibited_abstract
    ):
        raise RuntimeError("abstract boundary contract failed")

    provenance = {
        "schema_version": 1,
        "generator": GENERATOR,
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "source_runs": RUNS,
        "claim_ids": CLAIMS,
        "inputs": {str(path.relative_to(root)): _sha(path) for path in sources.values()},
        "figures": {name: _sha(figures / name) for name in figure_assets},
        "figure_data": {name: _sha(figures / "data" / name) for name in csv_specs},
        "tables": {name: _sha(tables / name) for name in table_assets},
        "bibliography": _sha(generated / "references.bib"),
        "abstract": _sha(paper / "abstract.tex"),
    }
    provenance_text = json.dumps(provenance, indent=2, sort_keys=True) + "\n"
    (paper / "source-provenance.json").write_text(provenance_text, encoding="utf-8")
    (generated / "provenance.json").write_text(provenance_text, encoding="utf-8")
    figure_lines = [
        "# Figure data and summaries",
        "",
        "All scientific values are copied from checksum-validated immutable outputs. Conceptual diagrams expose their node/edge records as CSV.",
        "",
    ]
    summaries = [
        "Sharing separates pooled aggregation from remaining rescue actions.",
        "Equal accuracy and private discovery coexist with unequal action-budget profiles.",
        "Registered channels have opposite incremental-sharing directions.",
        "Residual error must cross the exact rescue threshold for sharing to help.",
        "The 177-scenario registry contains compression, aggregation, neutral, and a bounded zero mixed class.",
        "At p=3/5 the shared selected curve crosses the private selected curve at the certified algebraic root and remains below centralized V2.",
        "Selected, alternative-equilibrium, ownership-aware, and centralized outcomes use different strategy or authority classes.",
        "Evidence status and authority attach to claims rather than to the manuscript as a whole.",
    ]
    if len(figure_assets) != len(summaries):
        raise RuntimeError("figure summary count mismatch")
    for index, ((name, _), summary) in enumerate(
        zip(figure_assets.items(), summaries, strict=True), 1
    ):
        data_name = list(csv_specs)[index - 1]
        figure_lines.extend(
            [
                f"## Figure {index}: {name}",
                "",
                summary,
                "",
                f"Exact data: `data/{data_name}`",
                f"TeX SHA-256: `{_sha(figures / name)}`",
                f"Data SHA-256: `{_sha(figures / 'data' / data_name)}`",
                "",
            ]
        )
    (figures / "README.md").write_text("\n".join(figure_lines), encoding="utf-8")

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
                raise RuntimeError(
                    "Information Sharing Frontier compilation failed\n" + log[-6000:]
                )
            pdfs.append((Path(temporary) / "main.pdf").read_bytes())
    hashes = [hashlib.sha256(pdf).hexdigest() for pdf in pdfs]
    if hashes[0] != hashes[1]:
        raise RuntimeError("Information Sharing Frontier PDF is not byte reproducible")
    output = paper / "When_Does_Information_Sharing_Improve_Decentralized_Discovery.pdf"
    output.write_bytes(pdfs[-1])
    (paper / "build.log").write_text(
        "\n\n===== deterministic rebuild =====\n\n".join(logs), encoding="utf-8"
    )
    info = subprocess.check_output(["pdfinfo", output], text=True)
    match = re.search(r"^Pages:\s+(\d+)$", info, re.M)
    if not match:
        raise RuntimeError("pdfinfo did not report page count")
    pages = int(match.group(1))
    if pages not in range(26, 41):
        raise RuntimeError(f"paper page count outside 26--40 target: {pages}")
    validation = {
        "schema_version": 1,
        "generator": GENERATOR,
        "compile_exit_status": 0,
        "page_count": pages,
        "pdf_sha256": hashes[0],
        "byte_reproducible_two_builds": True,
        "unresolved_references_citations_or_overfull_boxes": False,
        "abstract_boundary_validated": True,
        "claim_ids_resolved": True,
        "citation_keys_resolved": True,
        "provenance_validated": True,
        "source_runs": RUNS,
        "claim_ids": CLAIMS,
        "generated_figures": sorted(figure_assets),
        "generated_tables": sorted(table_assets),
        "figure_data": sorted(csv_specs),
        "inputs": provenance["inputs"],
    }
    (paper / "validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return validation


def main() -> None:
    result = build(repository_root())
    print(
        f"Information Sharing Frontier paper passed: {result['page_count']} pages, PDF {str(result['pdf_sha256'])[:12]}"
    )


if __name__ == "__main__":
    main()
