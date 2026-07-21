import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "results/verified/20260721T032358Z_DD-003_84238b76_2cbc13e66a"


def test_heterogeneous_run_manifest_and_independent_verification_pass() -> None:
    manifest = json.loads((RUN / "manifest.json").read_text(encoding="utf-8"))
    validation = json.loads((RUN / "validation.json").read_text(encoding="utf-8"))
    verification = json.loads(
        (RUN / "outputs/independent-verification.json").read_text(encoding="utf-8")
    )
    assert manifest["validation_status"] == "passed"
    assert manifest["exit_status"] == 0
    assert validation["passed"] is True
    assert validation["git_clean_at_start"] is True
    assert verification["passed"] is True
    assert verification["corruption_test"]["rejected"] is True
    for relative, expected in manifest["outputs"].items():
        assert hashlib.sha256((RUN / relative).read_bytes()).hexdigest() == expected


def test_colored_census_and_pairwise_counterexample_are_exact() -> None:
    certificate = json.loads(
        (RUN / "outputs/colored-census-certificate.json").read_text(encoding="utf-8")
    )
    witness = json.loads(
        (RUN / "outputs/pairwise-moment-counterexample.json").read_text(encoding="utf-8")
    )
    assert certificate["base_labeled_colored_object_count"] == 41612
    assert certificate["base_orbit_count"] == 671
    assert certificate["expansion_labeled_colored_object_count"] == 12966
    assert certificate["expansion_orbit_count"] == 168
    assert certificate["total_orbit_count"] == 839
    assert certificate["matched_complete_moment_group_count"] == 163
    assert certificate["networks_in_matched_complete_moment_groups"] == 485
    assert certificate["matched_groups_with_different_private_discovery"] == 111
    assert witness["complete_first_and_pairwise_moments_equal"] is True
    assert Fraction(witness["left_private_discovery"]) == Fraction(3, 4)
    assert Fraction(witness["right_private_discovery"]) == Fraction(2, 3)
    assert Fraction(witness["private_discovery_difference"]) == Fraction(1, 12)
