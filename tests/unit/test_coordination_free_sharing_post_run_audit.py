import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "20260722T210334Z_DD-022_2376d5b7_ad67765ca8"
RUN = ROOT / "results/verified" / RUN_ID


def test_dd022_manifest_and_output_hashes() -> None:
    manifest = json.loads((RUN / "manifest.json").read_text())
    assert manifest["run_id"] == RUN_ID
    assert manifest["study_id"] == "DD-022"
    assert manifest["git_commit"].startswith("2376d5b7")
    assert manifest["validation_status"] == "passed"
    assert manifest["exit_status"] == 0
    for relative, expected in manifest["outputs"].items():
        assert hashlib.sha256((RUN / relative).read_bytes()).hexdigest() == expected


def test_dd022_immutable_registry_and_certificate() -> None:
    registry = json.loads((RUN / "outputs/registry.json").read_text())
    summary = json.loads((RUN / "outputs/summary.json").read_text())
    validation = json.loads((RUN / "validation.json").read_text())
    certificate = json.loads((RUN / "outputs/threshold-certificate.json").read_text())
    assert len(registry) == summary["cells"] == 42
    assert summary["gain_class_counts"] == {"negative": 18, "neutral": 18, "positive": 6}
    assert validation["passed"] is True and validation["all_corruptions_rejected"] is True
    assert certificate["polynomial_coefficients"] == [24, 17, -16]
    assert certificate["endpoint_signs"] == ["-2251/1562500", "111/15625"]
    assert all(certificate["checks"].values())


def test_dd022_canonical_correspondence_and_gap() -> None:
    registry = json.loads((RUN / "outputs/registry.json").read_text())
    canonical = {Fraction(row["dependence"]): row for row in registry if row["accuracy"] == "3/5"}
    assert canonical[Fraction(1, 2)]["gain_class"] == "negative"
    assert canonical[Fraction(3, 4)]["gain_class"] == "positive"
    assert canonical[Fraction(1)]["gain_class"] == "neutral"
    assert all(
        row["private_correspondence"]["best_pure_discovery"] == "1" for row in canonical.values()
    )
    assert all(
        Fraction(row["shared_metrics"]["implementation_gap"]) > 0 for row in canonical.values()
    )
