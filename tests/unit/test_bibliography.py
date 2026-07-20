import re
from pathlib import Path


def test_bibliography_has_unique_normalized_dois() -> None:
    root = Path(__file__).parents[2]
    text = (root / "bibliography/references.bib").read_text()
    dois = [value.lower() for value in re.findall(r"doi\s*=\s*\{([^}]+)\}", text)]
    assert len(dois) >= 10
    assert len(dois) == len(set(dois))
    assert all(doi.startswith("10.") and "/" in doi for doi in dois)


def test_every_bibliography_entry_has_a_year() -> None:
    root = Path(__file__).parents[2]
    text = (root / "bibliography/references.bib").read_text()
    entries = [
        entry
        for entry in re.split(r"(?=@(?:article|book|misc|inproceedings|incollection)\{)", text)
        if entry.startswith("@")
    ]
    assert entries
    assert all(re.search(r"\byear\s*=\s*\{[0-9]{4}\}", entry) for entry in entries)
