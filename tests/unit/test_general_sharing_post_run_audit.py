import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "20260722T185924Z_DD-021_3cdbbc40_2fea269a9a"
RUN = ROOT / "results/verified" / RUN_ID


def _fraction(value: str) -> Fraction:
    return Fraction(value)


def _load(name: str) -> object:
    return json.loads((RUN / "outputs" / name).read_text())


def test_manifest_hashes_and_independent_row_identities() -> None:
    manifest = json.loads((RUN / "manifest.json").read_text())
    assert manifest["run_id"] == RUN_ID
    assert manifest["git_dirty"] is False
    assert manifest["exit_status"] == 0
    assert manifest["validation_status"] == "passed"
    for relative, expected in manifest["outputs"].items():
        assert hashlib.sha256((RUN / relative).read_bytes()).hexdigest() == expected

    rows = _load("registry.json")
    assert isinstance(rows, list) and len(rows) == 177
    sharing_classes: Counter[str] = Counter()
    full_classes: Counter[str] = Counter()
    budgets: Counter[str] = Counter()
    for row in rows:
        q = _fraction(row["q"])
        pooled = tuple(map(_fraction, row["pooled_accuracy"]))
        errors = tuple(map(_fraction, row["pooled_error"]))
        discovery = tuple(map(_fraction, row["sharing_discovery"]))
        increments = tuple(map(_fraction, row["sharing_increments"]))
        profile = tuple(map(_fraction, row["action_budget_profile"]))
        private = _fraction(row["private_discovery"])
        agents = int(row["agents"])

        assert private == 1 - (1 - q) ** agents
        assert all(
            discovery[index] == 1 - errors[index] * (1 - q) ** (agents - index - 1)
            for index in range(agents)
        )
        assert increments == tuple(
            discovery[index + 1] - discovery[index] for index in range(agents - 1)
        )
        assert all(
            (increments[index] > 0) == (errors[index + 1] < (1 - q) * errors[index])
            and (increments[index] == 0) == (errors[index + 1] == (1 - q) * errors[index])
            for index in range(agents - 1)
        )
        assert profile[0] == pooled[-1]
        assert profile[-1] >= private
        expected_budget = next(index for index, value in enumerate(profile, 1) if value >= private)
        assert row["recovery_budget"] == expected_budget
        sharing_classes[row["sharing_class"]] += 1
        full_classes[row["full_sharing_class"]] += 1
        budgets[str(expected_budget)] += 1

    assert sharing_classes == {
        "strict-compression-dominated": 126,
        "strict-aggregation-dominated": 16,
        "all-neutral": 35,
    }
    assert full_classes == {
        "B-shared-discovery-paradox": 78,
        "C-strict-aggregation-dominated-consensus": 16,
        "D-boundary": 83,
    }
    assert budgets == {"1": 51, "2": 55, "3": 64, "4": 7}


def test_certificate_witnesses_and_bounded_null() -> None:
    certificate = _load("method-agreement-certificate.json")
    corruptions = _load("corruption-tests.json")
    witnesses = _load("minimal-witnesses.json")
    assert certificate["method_agreement"] is True
    assert certificate["witness_minimality_agreement"] is True
    assert all(corruptions.values())
    assert witnesses["mixed_sharing_curve"] is None
    assert witnesses["mixed_sharing_bounded_null"] is True

    opposite = witnesses["same_baseline_opposite_sign"]
    assert (opposite["left"]["targets"], opposite["left"]["agents"]) == (4, 2)
    assert {tuple(opposite[side]["sharing_increments"]) for side in ("left", "right")} == {
        ("-1/4",),
        ("1/12",),
    }
    recovery = witnesses["same_accuracy_different_recovery"]
    assert (recovery["left"]["targets"], recovery["left"]["agents"]) == (3, 2)
    assert {recovery[side]["recovery_budget"] for side in ("left", "right")} == {1, 2}
