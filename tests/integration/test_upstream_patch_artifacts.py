import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATCH = (
    ROOT
    / "integrations/shared-discovery-paradox/patches/0001-distributed-discovery-additions.patch"
)
VALIDATION = ROOT / "papers/upstream-extension/preview/validation.json"


def test_review_patch_is_additive_and_scoped() -> None:
    patch = PATCH.read_text(encoding="utf-8")
    assert "Distributed Discovery: Information Frontiers and Protocol Loss" in patch
    assert "A research program in distributed discovery" in patch
    assert "Private-team frontier" in patch
    assert "-\\title{" not in patch
    assert "-\\begin{abstract}" not in patch
    assert "-\\begin{proposition}" not in patch
    assert "-\\begin{theorem}" not in patch


def test_compiled_preview_validation_passed() -> None:
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    assert validation["upstream_commit"] == "5025cc8e8f2f8ca015dff2066f08f81ad5715a51"
    assert validation["patch_applies"] is True
    assert validation["compile_exit_status"] == 0
    assert validation["required_content_present"] is True
    assert validation["original_title_preserved"] is True
