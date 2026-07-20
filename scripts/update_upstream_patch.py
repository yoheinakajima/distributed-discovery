"""Generate, apply-check, and compile the additive upstream paper patch."""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

from distributed_discovery.validation.bootstrap import repository_root

UPSTREAM = Path(".cache/upstream/shared-discovery-paradox")
TEX = Path("paper/The_Shared_Discovery_Paradox.tex")
PATCH = Path(
    "integrations/shared-discovery-paradox/patches/0001-distributed-discovery-additions.patch"
)
FRAGMENTS = Path("papers/upstream-extension/fragments")
PREVIEW = Path("papers/upstream-extension/preview")


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected one {label} anchor, found {count}")
    return text.replace(old, new, 1)


def _read(root: Path, name: str) -> str:
    return (root / FRAGMENTS / name).read_text(encoding="utf-8").strip()


def build_patched_source(root: Path, original: str) -> str:
    text = original
    keyword_old = (
        r"\noindent\textbf{Keywords:} collective discovery, organizational search, consensus, "
        r"congestion games, price of anarchy, information aggregation, correlated signals.\\"
    )
    keyword_new = rf"\noindent\textbf{{Keywords:}} {_read(root, 'keywords.txt')}.\\"
    text = _replace_once(text, keyword_old, keyword_new, "keywords")

    intro_anchor = "The paper develops four layers of the benchmark.\n"
    intro = _read(root, "introduction.tex")
    text = _replace_once(text, intro_anchor, f"{intro}\n\n{intro_anchor}", "introduction")

    title = _read(root, "framework-section-title.txt")
    text = _replace_once(
        text,
        r"\section{Information value and protocol loss}",
        rf"\section{{{title}}}",
        "framework section",
    )

    matrix_anchor = (
        "The comparison with private clue-following changes both the information architecture "
        "and the assignment authority, so it is a combined organizational benchmark rather "
        "than a unique causal decomposition.\n"
    )
    matrix = _read(root, "institutional-matrix.tex")
    text = _replace_once(text, matrix_anchor, f"{matrix_anchor}\n{matrix}\n", "matrix")

    dictionary_anchor = "\\midrule\nOne-action value $V_1(\\F)$"
    dictionary = _read(root, "benchmark-dictionary.tex")
    text = _replace_once(
        text,
        dictionary_anchor,
        f"\\midrule\n{dictionary}\nOne-action value $V_1(\\F)$",
        "dictionary",
    )

    research_anchor = "\\section{Limitations and extensions}"
    research = _read(root, "research-program.tex")
    text = _replace_once(
        text, research_anchor, f"{research}\n\n{research_anchor}", "research program"
    )
    return text


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    root = repository_root()
    upstream = root / UPSTREAM
    lock = yaml.safe_load(
        (root / "integrations/shared-discovery-paradox/upstream.lock").read_text()
    )
    commit = subprocess.check_output(
        ["git", "-C", upstream, "rev-parse", "HEAD"], text=True
    ).strip()
    if commit != lock["commit"]:
        raise RuntimeError("upstream cache does not match upstream.lock")
    if subprocess.check_output(["git", "-C", upstream, "status", "--porcelain"], text=True).strip():
        raise RuntimeError("upstream cache must be clean")
    source_path = upstream / TEX
    source_date_epoch = subprocess.check_output(
        ["git", "-C", upstream, "show", "-s", "--format=%ct", commit], text=True
    ).strip()
    original = source_path.read_text(encoding="utf-8")
    patched = build_patched_source(root, original)
    patch_text = "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            patched.splitlines(keepends=True),
            fromfile=f"a/{TEX}",
            tofile=f"b/{TEX}",
        )
    )
    patch_path = root / PATCH
    patch_path.write_text(patch_text, encoding="utf-8")

    preview = root / PREVIEW
    preview.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dd-upstream-patch-") as temporary:
        temporary_path = Path(temporary)
        worktree = temporary_path / "upstream"
        subprocess.run(
            ["git", "-C", upstream, "worktree", "add", "--detach", str(worktree), commit],
            check=True,
            capture_output=True,
            text=True,
        )
        try:
            subprocess.run(["git", "-C", worktree, "apply", "--check", patch_path], check=True)
            subprocess.run(["git", "-C", worktree, "apply", patch_path], check=True)
            # Tectonic resolves \graphicspath relative to the input file, while the
            # upstream source keeps figures at repository root for its LaTeX build.
            # Stage them only inside the disposable worktree.
            shutil.copytree(worktree / "figures", worktree / "paper/figures")
            build_dir = temporary_path / "build"
            build_dir.mkdir()
            compiled = subprocess.run(
                [
                    "tectonic",
                    TEX.name,
                    "--outdir",
                    str(build_dir),
                    "--keep-logs",
                ],
                cwd=worktree / TEX.parent,
                env={**os.environ, "SOURCE_DATE_EPOCH": source_date_epoch},
                capture_output=True,
                text=True,
                check=False,
            )
            raw_log = (compiled.stdout + compiled.stderr).replace(temporary, "<temporary>")
            sanitized_log = "\n".join(line.rstrip() for line in raw_log.splitlines()) + "\n"
            (preview / "build.log").write_text(sanitized_log, encoding="utf-8")
            if compiled.returncode != 0:
                raise RuntimeError("patched paper failed to compile; inspect preview/build.log")
            built_pdf = build_dir / "The_Shared_Discovery_Paradox.pdf"
            shutil.copy2(built_pdf, preview / "The_Shared_Discovery_Paradox-patched.pdf")
            patched_text = (worktree / TEX).read_text(encoding="utf-8")
            required = [
                "Distributed Discovery: Information Frontiers and Protocol Loss",
                "Private-team frontier",
                "A research program in distributed discovery",
            ]
            if not all(value in patched_text for value in required):
                raise RuntimeError("patched source is missing required additive content")
            validation = {
                "schema_version": 1,
                "upstream_commit": commit,
                "upstream_clean_before": True,
                "patch_applies": True,
                "compiler": subprocess.check_output(["tectonic", "--version"], text=True).strip(),
                "compile_exit_status": compiled.returncode,
                "required_content_present": True,
                "original_title_preserved": r"\title{\textbf{The Shared Discovery Paradox}"
                in patched_text,
                "pdf_sha256": _sha256(preview / "The_Shared_Discovery_Paradox-patched.pdf"),
            }
            (preview / "validation.json").write_text(
                json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
        finally:
            subprocess.run(
                ["git", "-C", upstream, "worktree", "remove", "--force", str(worktree)],
                check=True,
                capture_output=True,
                text=True,
            )
    if subprocess.check_output(["git", "-C", upstream, "status", "--porcelain"], text=True).strip():
        raise RuntimeError("upstream cache changed during validation")
    print(f"validated patch: {PATCH}")


if __name__ == "__main__":
    main()
