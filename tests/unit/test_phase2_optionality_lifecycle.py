from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

from distributed_discovery.site.build import _lifecycle_banner

ROOT = Path(__file__).resolve().parents[2]


def _audit(script: str) -> dict[str, object]:
    path = ROOT / "scripts" / script
    spec = importlib.util.spec_from_file_location(script.removesuffix(".py"), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.audit()


def test_ai_only_boundary_has_separated_roles_and_no_human_workflow() -> None:
    source = yaml.safe_load((ROOT / "docs/ai-lab-operating-boundary.yml").read_text())
    assert source["operating_model"] == "ai-powered-research-lab"
    assert source["human_pi"]["final_gate_authority"] is True
    assert len(source["internal_roles"]) == 10
    assert source["human_engagement"]["authorized"] is False
    assert source["current_task"] == {
        "model_or_provider_calls": False,
        "cross_model_evaluation": False,
        "ai_reviews_executed": False,
    }
    assert not list((ROOT / "reports/external-review").glob("*"))


def test_optionality_translation_lifecycle_roles_and_recomposition_audits() -> None:
    assert _audit("audit_optionality_portfolio.py") == {
        "options": 9,
        "first_option": "WS-1",
        "scientific_score": False,
    }
    assert _audit("audit_translation_concordance.py") == {
        "objects": 14,
        "formulations": 56,
    }
    lifecycle = _audit("audit_paper_lifecycle.py")
    assert lifecycle == {
        "records": 8,
        "canonical": "shared-discovery-paradox",
        "local": 7,
        "archived_or_superseded": 0,
    }
    roles = _audit("audit_paper_claim_roles.py")
    assert roles["claims"] == 110
    assert sum(roles["roles"].values()) >= 110
    assert _audit("audit_paper_recomposition.py") == {
        "records": 8,
        "workflow_steps": 11,
    }


def test_gate_c_and_minimal_ledger_schema_fixtures() -> None:
    assert _audit("audit_phase2_prospectus_schemas.py") == {
        "gate_c_dimensions": 11,
        "minimal_ledger_valid": True,
        "minimal_ledger_invalid_rejected": True,
    }


def test_archive_banner_uses_a_real_registry_replacement_without_fake_paper() -> None:
    records = {
        "replacement": {
            "paper_id": "replacement",
            "title": "Replacement",
            "route": "publications/replacement.html",
        }
    }
    banner = _lifecycle_banner(
        {
            "lifecycle_class": "superseded",
            "superseded_by": "replacement",
            "archive_reason": "Absorbed after claim-role transfer",
        },
        records,
    )
    assert "Superseded" in banner
    assert "../publications/replacement.html" in banner
    assert "Absorbed after claim-role transfer" in banner
    assert (
        _lifecycle_banner(
            {
                "lifecycle_class": "active-working-paper",
                "superseded_by": None,
                "archive_reason": None,
            },
            records,
        )
        == ""
    )
