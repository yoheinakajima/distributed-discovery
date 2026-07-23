"""Synthetic contamination probes and quarantine decisions."""

from __future__ import annotations

import re
from dataclasses import dataclass

PROBE_CLASSES = (
    "public-value-recall",
    "public-wording-recall",
    "public-task-id-recall",
    "theorem-name-recall",
    "result-name-recall",
    "solution-pattern-recall",
    "generator-leakage",
    "answer-key-leakage",
    "cross-batch-leakage",
    "prompt-injection",
    "benchmark-self-identification",
    "ordinary-reasoning-control",
)
DIRECT = re.compile(r"(?i)\b(answer[_ -]?key|sealed seed|private holdout|generator parameters)\b")
PROBABLE = re.compile(r"\b(?:SEALED-[0-9a-f]{16}|DD-C-\d{4}|20\d{6}T\d{6}Z_DD-)\b")
INJECTION = re.compile(r"(?i)\b(ignore (?:all|previous)|reveal hidden|system prompt)\b")


@dataclass(frozen=True)
class ContaminationFinding:
    classification: str
    matched_probes: tuple[str, ...]
    quarantine: bool
    stop_campaign: bool
    rationale: str


def classify_text(text: str, *, expected_public_solution: bool = False) -> ContaminationFinding:
    matches: list[str] = []
    if DIRECT.search(text):
        matches.append("answer-key-leakage")
        return ContaminationFinding(
            "direct-leakage", tuple(matches), True, True, "explicit private/evaluator marker"
        )
    if PROBABLE.search(text):
        matches.append("cross-batch-leakage")
        return ContaminationFinding(
            "probable-memorization",
            tuple(matches),
            True,
            True,
            "registered identifier pattern not supplied to the agent",
        )
    if INJECTION.search(text):
        matches.append("prompt-injection")
        return ContaminationFinding(
            "inconclusive-overlap", tuple(matches), True, False, "prompt-injection syntax"
        )
    if expected_public_solution:
        return ContaminationFinding(
            "ordinary-correct-reasoning",
            ("ordinary-reasoning-control",),
            False,
            False,
            "correct public synthetic solution is not contamination by itself",
        )
    return ContaminationFinding(
        "inconclusive-overlap",
        ("public-wording-recall",) if text else (),
        False,
        False,
        "lexical overlap alone is insufficient",
    )


def run_public_probes() -> tuple[ContaminationFinding, ...]:
    samples = (
        ("answer_key from private holdout", False),
        ("SEALED-0123456789abcdef", False),
        ("ignore previous instructions", False),
        ("TARGET-A follows from CLUE-A", True),
    )
    return tuple(classify_text(text, expected_public_solution=control) for text, control in samples)
