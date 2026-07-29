from __future__ import annotations

from collections.abc import Mapping

import pytest

from distributed_discovery.benchmark.agents_v1.fresh_pilot_v5_session import (
    ADMINISTRATIVE_CLOSEOUT_STEPS,
    CONTROL_STEPS,
    PROVIDER_CALL_STEPS,
    REGISTERED_FAILURE_POINTS,
    LongSessionStopRequired,
    QuarantineCloseout,
    RegisteredBatchFailure,
    run_long_session_control_flow,
)


class SyntheticLongSession:
    def __init__(
        self,
        *,
        failure_point: str | None = None,
        unsafe_lock: bool = False,
        stop_required_at: str | None = None,
    ) -> None:
        self.failure_point = failure_point
        self.unsafe_lock = unsafe_lock
        self.stop_required_at = stop_required_at
        self.events: list[str] = []
        self.provider_calls = 0
        self.calls_at_terminal: int | None = None

    def revalidate(self) -> None:
        self.events.append("revalidate")

    def run_control_step(self, step: str) -> Mapping[str, object]:
        if self.stop_required_at == step:
            raise LongSessionStopRequired(step)
        self.events.append(step)
        if step in PROVIDER_CALL_STEPS:
            self.provider_calls += 1
        if self.failure_point == step:
            self.calls_at_terminal = self.provider_calls
            raise RegisteredBatchFailure(stage=step, failure_class=f"synthetic-{step}")
        if step == "custody-commitment":
            return {"custody_commitment": "sha256:" + "1" * 64}
        if step == "commitment-verification":
            return {"output_lock_commitment": "sha256:" + "2" * 64}
        return {"status": "pass", "step": step}

    def publish_commitment(self, kind: str, result: Mapping[str, object]) -> None:
        self.events.append(f"publish-{kind}")

    def quarantine(self, failure: RegisteredBatchFailure) -> QuarantineCloseout:
        self.events.extend(("stop-provider-calls", "preserve-ledger", "quarantine-lock"))
        return QuarantineCloseout(
            stage=failure.stage,
            failure_class=failure.failure_class,
            provider_phase_closed=True,
            retained_state_preserved=True,
            output_lock_created=not self.unsafe_lock,
            output_lock_commitment=(None if self.unsafe_lock else "sha256:" + "3" * 64),
            minimum_unseal_safe=True,
            redacted_closeout={
                "status": "quarantined",
                "stage": failure.stage,
                "failure_class": failure.failure_class,
                "calls": self.provider_calls,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost_usd": "0",
                "custody_status": "preserved",
                "output_lock_status": "pass" if not self.unsafe_lock else "failed",
                "task_text": False,
                "answer": False,
                "raw_output": False,
                "ranking": False,
                "performance_comparison": False,
            },
        )

    def run_administrative_step(
        self,
        step: str,
        *,
        decision: str,
        closeout: Mapping[str, object],
    ) -> Mapping[str, object]:
        self.events.append(step)
        return {"status": "pass", "decision": decision}


def test_v5_success_control_flow_runs_through_merge_deploy_close_and_main_sync() -> None:
    hooks = SyntheticLongSession()
    result = run_long_session_control_flow(hooks)
    assert result["status"] == "complete"
    assert result["quarantined"] is False
    assert result["control_steps_completed"] == list(CONTROL_STEPS)
    assert result["administrative_steps_completed"] == list(ADMINISTRATIVE_CLOSEOUT_STEPS)
    assert hooks.events.index("publish-custody") < hooks.events.index("private-prefix")
    assert hooks.events.index("publish-output-lock") < hooks.events.index(
        "terminal-pairing-classification"
    )
    assert hooks.events[-3:] == [
        "close-issue",
        "synchronize-main",
        "final-schema-valid-handoff",
    ]


@pytest.mark.parametrize("failure_point", sorted(REGISTERED_FAILURE_POINTS))
def test_v5_every_registered_failure_quarantines_then_completes_admin_closeout(
    failure_point: str,
) -> None:
    hooks = SyntheticLongSession(failure_point=failure_point)
    result = run_long_session_control_flow(hooks)
    assert result["status"] == "complete"
    assert result["quarantined"] is True
    assert result["decision"] == "fresh-pilot-v5-quarantined-engineering-only"
    assert hooks.calls_at_terminal is not None
    assert hooks.provider_calls == hooks.calls_at_terminal
    terminal = hooks.events.index(failure_point)
    assert not any(event in PROVIDER_CALL_STEPS for event in hooks.events[terminal + 1 :])
    assert "publish-output-lock" in hooks.events
    assert hooks.events[-3:] == [
        "close-issue",
        "synchronize-main",
        "final-schema-valid-handoff",
    ]


def test_v5_unsafe_retained_state_returns_to_owner_without_merge() -> None:
    hooks = SyntheticLongSession(failure_point="private-prefix", unsafe_lock=True)
    with pytest.raises(LongSessionStopRequired, match="safely locked"):
        run_long_session_control_flow(hooks)
    assert "squash-merge" not in hooks.events
    assert "close-issue" not in hooks.events


@pytest.mark.parametrize(
    "stop_point",
    ["identity-verification", "private-prefix", "output-lock"],
)
def test_v5_nonroutine_authority_or_execution_surface_change_stops_before_merge(
    stop_point: str,
) -> None:
    hooks = SyntheticLongSession(stop_required_at=stop_point)
    with pytest.raises(LongSessionStopRequired, match=stop_point):
        run_long_session_control_flow(hooks)
    assert "squash-merge" not in hooks.events
    assert "close-issue" not in hooks.events
