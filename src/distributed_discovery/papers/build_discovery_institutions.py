"""Build the evidence-backed Discovery Stack synthesis paper."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

from distributed_discovery.validation.bootstrap import repository_root

GENERATOR = "distributed_discovery.papers.build_discovery_institutions"
RUNS = {
    "adaptation": "20260721T050038Z_DD-004_8ab02e7f_71d84de7c4",
    "coverage": "20260721T050706Z_DD-005_be3b544c_98698dee2f",
    "rewards": "20260721T140745Z_DD-006_401ad624_c942f43e42",
    "measurement": "20260721T052307Z_DD-007_af4ea130_72fb89c5fc",
    "acquisition": "20260721T141527Z_DD-008_0d11dc77_7e0c8f1d66",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _checked(root: Path, key: str, relative: str) -> Path:
    run = root / "results/verified" / RUNS[key]
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    path = run / relative
    if (
        manifest.get("validation_status") != "passed"
        or manifest.get("exit_status") != 0
        or manifest.get("outputs", {}).get(relative) != _sha256(path)
    ):
        raise RuntimeError(f"invalid source artifact: {run.name}/{relative}")
    return path


def _table(schedule: object, coverage: object, reward: object, acquisition: object) -> str:
    def count(value: object, names: tuple[str, ...]) -> object:
        if isinstance(value, dict):
            for name in names:
                if name in value:
                    return value[name] if not isinstance(value[name], list) else len(value[name])
        return len(value) if isinstance(value, list) else "registered"

    schedule_count = count(schedule, ("schedules",))
    coverage_count = count(coverage, ("frontiers",))
    reward_count = count(reward, ("frontier_rows", "row_count", "rows"))
    acquisition_count = count(
        acquisition, ("common_source_trap_cells", "common_source_trap_count", "trap_count")
    )
    return "\n".join(
        [
            "% Generated evidence asset; do not edit by hand.",
            rf"% Source runs: {', '.join(RUNS.values())}",
            r"\begin{table}[t]\centering\small",
            (
                r"\caption{Evidence inventory for the Discovery Stack. Each row is a bounded "
                r"registered result, not a universal institutional law.}"
            ),
            r"\label{tab:stack-evidence}",
            r"\begin{tabularx}{\textwidth}{lXrr}",
            r"\toprule Margin & Registered object & Evidence & Claim\\\midrule",
            (
                rf"Adapt & {schedule_count} schedule records under perfect "
                r"elimination & exact fixture & DD-C-0045\\"
            ),
            (
                rf"Cover & {coverage_count} coverage-frontier records & "
                r"bounded witnesses & DD-C-0046, DD-C-0047\\"
            ),
            (
                rf"Reward & {reward_count} "
                r"normalized-transfer rows & exhaustive class & DD-C-0050\\"
            ),
            (
                rf"Acquire & {acquisition_count} common-source trap cells "
                r"& exact source-choice grid & DD-C-0051\\"
            ),
            (
                r"Measure & synthetic event generator and recovery checks & synthetic-only "
                r"& DD-C-0049\\"
            ),
            r"\bottomrule\end{tabularx}",
            (
                rf"\par\footnotesize Generator: \texttt{{\detokenize{{{GENERATOR}}}}}; "
                r"inputs are checksum-validated from immutable manifests."
            ),
            r"\end{table}",
            "",
        ]
    )


def build(root: Path) -> dict[str, object]:
    paper, generated = (
        root / "papers/discovery-institutions",
        root / "papers/discovery-institutions/generated",
    )
    generated.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "schedule": _checked(root, "adaptation", "outputs/schedule-frontier.json"),
        "coverage": _checked(root, "coverage", "outputs/coverage-frontiers.json"),
        "reward": _checked(root, "rewards", "outputs/general-transfer-summary.json"),
        "acquisition": _checked(root, "acquisition", "outputs/source-choice-summary.json"),
        "measurement": _checked(root, "measurement", "outputs/synthetic-recovery-grid.json"),
    }
    values = {
        name: json.loads(path.read_text(encoding="utf-8")) for name, path in artifacts.items()
    }
    (generated / "stack-evidence-table.tex").write_text(
        _table(values["schedule"], values["coverage"], values["reward"], values["acquisition"]),
        encoding="utf-8",
    )
    shutil.copy2(root / "bibliography/references.bib", generated / "references.bib")
    source = (paper / "main.tex").read_text(encoding="utf-8") + (
        generated / "stack-evidence-table.tex"
    ).read_text(encoding="utf-8")
    known_claims = {
        item["id"]
        for item in yaml.safe_load((root / "claims/claims.yml").read_text(encoding="utf-8"))[
            "claims"
        ]
    }
    missing_claims = set(re.findall(r"DD-C-\d{4}", source)) - known_claims
    bib = (generated / "references.bib").read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"^@\w+\{([^,]+),", bib, flags=re.MULTILINE))
    citations = {
        key.strip()
        for group in re.findall(r"\\cite[tp]?\{([^}]+)\}", source)
        for key in group.split(",")
    }
    if missing_claims or citations - bib_keys:
        raise RuntimeError("unresolved paper claim or citation")
    required = [
        "The Discovery Stack",
        "Acquisition",
        "Disclosure and allocation",
        "Adaptation",
        "Coverage",
        "Rewards",
        "Measurement",
        "Institutional implications and limitations",
        "Research agenda",
    ]
    if any(rf"\section{{{title}}}" not in source for title in required):
        raise RuntimeError("required synthesis sections missing")
    build_dir = paper / "build"
    build_dir.mkdir(exist_ok=True)
    pdfs: list[bytes] = []
    for _ in range(2):
        with tempfile.TemporaryDirectory(dir=build_dir) as temporary:
            result = subprocess.run(
                ["tectonic", "main.tex", "--outdir", temporary],
                cwd=paper,
                env={**os.environ, "SOURCE_DATE_EPOCH": "1784664000"},
                capture_output=True,
                text=True,
            )
            if result.returncode or re.search(
                r"undefined (?:reference|citation)|overfull \\hbox",
                result.stdout + result.stderr,
                re.I,
            ):
                raise RuntimeError("Discovery Stack compilation failed")
            pdfs.append((Path(temporary) / "main.pdf").read_bytes())
    hashes = [hashlib.sha256(pdf).hexdigest() for pdf in pdfs]
    if hashes[0] != hashes[1]:
        raise RuntimeError("PDF is not byte reproducible")
    output = paper / "Institutions_for_Distributed_Discovery.pdf"
    output.write_bytes(pdfs[-1])
    info = subprocess.check_output(["pdfinfo", output], text=True)
    match = re.search(r"^Pages:\s+(\d+)$", info, re.M)
    if not match:
        raise RuntimeError("pdfinfo failed")
    validation = {
        "schema_version": 1,
        "generator": GENERATOR,
        "compile_exit_status": 0,
        "page_count": int(match.group(1)),
        "pdf_sha256": hashes[0],
        "byte_reproducible_two_builds": True,
        "unresolved_references_citations_or_overfull_boxes": False,
        "claim_ids_resolved": True,
        "citation_keys_resolved": True,
        "source_runs": RUNS,
        "inputs": {str(path.relative_to(root)): _sha256(path) for path in artifacts.values()},
    }
    (paper / "validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return validation


def main() -> None:
    validation = build(repository_root())
    print(f"Discovery Stack paper passed: {validation['page_count']} pages")


if __name__ == "__main__":
    main()
