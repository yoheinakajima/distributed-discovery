import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_every_project_paper_visual_review_matches_its_pdf() -> None:
    reviewed = 0
    for review in sorted((ROOT / "papers").glob("*/visual-qa.md")):
        pdfs = list(review.parent.glob("*.pdf"))
        assert len(pdfs) == 1
        match = re.search(r"[0-9a-f]{64}", review.read_text(encoding="utf-8"))
        assert match is not None
        assert hashlib.sha256(pdfs[0].read_bytes()).hexdigest() == match.group(0)
        reviewed += 1
    assert reviewed == 6
