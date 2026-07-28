from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_v3_quarantine_closeout_is_public_safe_and_terminal() -> None:
    closeout = yaml.safe_load(
        (ROOT / "reports/benchmark/treasurebench-agents-v1-fresh-pilot-v3-closeout.yml").read_text()
    )

    assert closeout["decision"] == "fresh-pilot-v3-quarantined-engineering-only"
    assert closeout["executed"] == {
        "stage": "fixed-full-batch",
        "failure_class": "fixed-full-batch-failure",
        "public_canary_complete": True,
        "custody_complete": True,
        "private_prefix_complete": True,
        "fixed_full_batch_complete": False,
        "partial_private_pairing_count": "not-published-quarantined-batch",
        "calls": 3067,
        "input_tokens": 2304303,
        "output_tokens": 444085,
        "cost_usd": "13.1861145",
        "provider_cost_usd": {"OpenAI": "4.5952575", "Anthropic": "8.590857"},
        "semantic_answer_retries": 0,
    }
    assert closeout["lock"] == {
        "output_lock_commitment": (
            "sha256:e52055b08ca3a8acb1cfb6ac608c6e601f3c618352900f92bf91c5ffc4718dbb"
        ),
        "objects_locked": 3576,
        "provider_phase_closed": True,
        "provider_calls_after_lock": 0,
        "output_lock_verified": True,
        "unsealed_before_lock": False,
        "minimum_unseal_performed": False,
    }
    assert closeout["redaction"]["status"] == "pass"
    assert not any(
        closeout["redaction"][key]
        for key in (
            "task_text_disclosed",
            "answer_disclosed",
            "seed_or_key_disclosed",
            "prompt_or_provider_output_disclosed",
            "raw_trace_disclosed",
            "task_level_performance_disclosed",
            "performance_comparison_created",
            "ranking_created",
            "composite_created",
        )
    )
    assert closeout["disposition"]["further_provider_calls_permitted"] is False
    assert closeout["disposition"]["campaign_and_batch_permanently_quarantined"] is True
    assert all(value is False for value in closeout["authority"].values())
