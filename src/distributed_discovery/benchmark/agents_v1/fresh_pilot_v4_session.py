"""Deterministic AO-0010 v4 success-or-quarantine long-session control flow."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

CONTROL_STEPS = (
    "identity-verification",
    "cap-guard",
    "public-canary",
    "custody-creation",
    "custody-commitment",
    "private-prefix",
    "fixed-full-batch",
    "terminal-provider-response",
    "provider-phase-close",
    "output-lock",
    "commitment-verification",
    "protocol-classification",
    "protocol-invalid-outcomes-retained",
    "response-ledger-trace-correspondence",
    "complete-pairings",
    "method-a-b",
    "method-c",
    "metric-bounds",
    "independent-bound-reconstruction",
    "contamination",
    "redaction",
)
REGISTERED_FAILURE_POINTS = frozenset(
    {
        "public-canary",
        "custody-creation",
        "custody-commitment",
        "private-prefix",
        "fixed-full-batch",
        "cap-guard",
        "terminal-provider-response",
        "response-ledger-trace-correspondence",
        "complete-pairings",
        "method-a-b",
        "method-c",
        "metric-bounds",
        "independent-bound-reconstruction",
        "contamination",
        "redaction",
        "output-lock",
        "commitment-verification",
        "identity-verification",
    }
)
PROVIDER_CALL_STEPS = frozenset(
    {"public-canary", "private-prefix", "fixed-full-batch", "terminal-provider-response"}
)
PUBLIC_COMMITMENT_STEPS = {
    "custody-commitment": "custody",
    "commitment-verification": "output-lock",
}
ADMINISTRATIVE_CLOSEOUT_STEPS = (
    "reconcile-public-safe-status",
    "validation-wall",
    "update-draft-pr",
    "required-pr-checks",
    "mark-pr-ready",
    "squash-merge",
    "post-merge-ci-pages",
    "named-live-public-routes",
    "close-issue",
    "synchronize-main",
    "final-schema-valid-handoff",
)


class LongSessionStopRequired(RuntimeError):
    """Raised only when the v4 owner must decide a non-routine expansion or unsafe state."""


class RegisteredBatchFailure(RuntimeError):
    """A prospective acceptance failure that requires honest quarantine closeout."""

    def __init__(self, *, stage: str, failure_class: str) -> None:
        if stage not in REGISTERED_FAILURE_POINTS:
            raise ValueError(f"unregistered failure point: {stage}")
        self.stage = stage
        self.failure_class = failure_class
        super().__init__(f"{stage}:{failure_class}")


@dataclass(frozen=True)
class QuarantineCloseout:
    stage: str
    failure_class: str
    provider_phase_closed: bool
    retained_state_preserved: bool
    output_lock_created: bool
    output_lock_commitment: str | None
    minimum_unseal_safe: bool
    redacted_closeout: Mapping[str, object]


class LongSessionHooks(Protocol):
    """Injected task and repository operations used by the v4 coordinator."""

    def revalidate(self) -> None: ...

    def run_control_step(self, step: str) -> Mapping[str, object]: ...

    def publish_commitment(self, kind: str, result: Mapping[str, object]) -> None: ...

    def quarantine(self, failure: RegisteredBatchFailure) -> QuarantineCloseout: ...

    def run_administrative_step(
        self,
        step: str,
        *,
        decision: str,
        closeout: Mapping[str, object],
    ) -> Mapping[str, object]: ...


def _validate_quarantine(closeout: QuarantineCloseout) -> None:
    if not closeout.provider_phase_closed:
        raise LongSessionStopRequired("quarantine provider phase could not be closed")
    if not closeout.retained_state_preserved:
        raise LongSessionStopRequired("retained private state could not be preserved")
    if not closeout.output_lock_created or not closeout.output_lock_commitment:
        raise LongSessionStopRequired("retained private state could not be safely locked")
    forbidden = (
        "task_text",
        "answer",
        "raw_output",
        "ranking",
        "performance_comparison",
    )
    if any(closeout.redacted_closeout.get(field) not in {None, False} for field in forbidden):
        raise LongSessionStopRequired("quarantine closeout crossed the redaction boundary")


def run_long_session_control_flow(hooks: LongSessionHooks) -> Mapping[str, object]:
    """Run the one-gate v4 control flow without routine owner checkpoints."""

    hooks.revalidate()
    results: dict[str, Mapping[str, object]] = {}
    quarantine: QuarantineCloseout | None = None
    for step in CONTROL_STEPS:
        try:
            result = hooks.run_control_step(step)
        except RegisteredBatchFailure as failure:
            quarantine = hooks.quarantine(failure)
            _validate_quarantine(quarantine)
            hooks.publish_commitment(
                "output-lock",
                {
                    "output_lock_commitment": quarantine.output_lock_commitment,
                    "quarantined": True,
                },
            )
            break
        results[step] = result
        commitment = PUBLIC_COMMITMENT_STEPS.get(step)
        if commitment is not None:
            hooks.publish_commitment(commitment, result)

    if quarantine is None:
        decision = "fresh-pilot-v4-engineering-complete-no-scientific-evidence"
        closeout: Mapping[str, object] = {
            "status": "pass",
            "decision": decision,
            "provider_phase_closed": True,
            "output_lock_verified": True,
            "redaction_status": "pass",
        }
    else:
        decision = "fresh-pilot-v4-quarantined-engineering-only"
        closeout = quarantine.redacted_closeout

    administrative: dict[str, Mapping[str, object]] = {}
    for step in ADMINISTRATIVE_CLOSEOUT_STEPS:
        administrative[step] = hooks.run_administrative_step(
            step,
            decision=decision,
            closeout=closeout,
        )
    return {
        "status": "complete",
        "decision": decision,
        "quarantined": quarantine is not None,
        "control_steps_completed": list(results),
        "administrative_steps_completed": list(administrative),
        "final_handoff": administrative["final-schema-valid-handoff"],
    }
