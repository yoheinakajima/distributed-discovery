import re
from pathlib import Path

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
