import re
from pathlib import Path

import pytest

from distributed_discovery.papers.build_foundations import _normalized_build_log, _source_date_epoch

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "papers/foundations/main.tex"


def test_foundations_note_has_required_scope_and_calibration() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert "not a claim that the phrase" in text
    assert "\\section{Limitations}" in text
    assert "Restated canonical results" in text
    assert "questions rather than conclusions" in text
    assert len(re.findall(r"% Claims: DD-C-", text)) >= 10


def test_numeric_assets_are_generated_inputs() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert r"\input{generated/canonical-table.tex}" in text
    assert r"\input{generated/frontier-figure.tex}" in text


def test_source_date_epoch_comes_from_immutable_run_manifest(tmp_path: Path) -> None:
    (tmp_path / "manifest.json").write_text(
        '{"started_utc": "1970-01-01T00:00:42Z"}\n', encoding="utf-8"
    )
    assert _source_date_epoch(tmp_path) == "42"

    (tmp_path / "manifest.json").write_text(
        '{"started_utc": "1970-01-01T00:00:42"}\n', encoding="utf-8"
    )
    with pytest.raises(ValueError, match="timezone"):
        _source_date_epoch(tmp_path)


def test_build_log_normalizes_parallel_write_order(tmp_path: Path) -> None:
    raw = (
        f"note: start {tmp_path}\nnote: Writing `z.pdf`\nnote: Writing `a.log`\nwarning: retained\n"
    )
    assert _normalized_build_log(raw, tmp_path) == (
        "note: start <repository>\n"
        "note: Writing `a.log`\n"
        "note: Writing `z.pdf`\n"
        "warning: retained\n"
    )
