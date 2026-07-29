"""Prospective TreasureBench Agents v1 protocol-validity policy v2.

This module is new for AO-0010. It does not reinterpret historical campaigns.
It classifies future completed pairings before metric interpretation and
constructs registered all-eligible-pairing metric and contrast bounds.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import Literal

from distributed_discovery.benchmark.agents_v1.models import TaskInstance

BatchIntegrityStatus = Literal["batch-integrity-valid"]
PairingStatus = Literal[
    "provider-terminal-missing",
    "protocol-valid",
    "protocol-invalid",
]

BATCH_INTEGRITY_VALID: BatchIntegrityStatus = "batch-integrity-valid"
PROVIDER_TERMINAL_MISSING: PairingStatus = "provider-terminal-missing"
PROTOCOL_VALID: PairingStatus = "protocol-valid"
PROTOCOL_INVALID: PairingStatus = "protocol-invalid"
PAIRING_STATUSES = frozenset({PROVIDER_TERMINAL_MISSING, PROTOCOL_VALID, PROTOCOL_INVALID})

METRIC_IDS = (
    "group-discovery",
    "distinct-action-coverage",
    "duplication",
    "planner-regret",
    "private-baseline-regret",
    "recovery-budget-attainment",
    "source-diversity",
    "communication-induced-action-compression",
    "distance-from-best-registered-equilibrium",
    "distance-from-worst-registered-equilibrium",
    "invalid-action-rate",
    "protocol-compliance",
    "calls",
    "tokens",
    "cost",
)
METRIC_FIELD_NAMES = {
    "group-discovery": "group_discovery",
    "distinct-action-coverage": "distinct_action_coverage",
    "duplication": "duplication",
    "planner-regret": "planner_regret",
    "private-baseline-regret": "private_baseline_regret",
    "recovery-budget-attainment": "recovery_budget_attainment",
    "source-diversity": "source_diversity",
    "communication-induced-action-compression": "communication_action_compression",
    "distance-from-best-registered-equilibrium": "best_equilibrium_distance",
    "distance-from-worst-registered-equilibrium": "worst_equilibrium_distance",
    "invalid-action-rate": "invalid_action_rate",
    "protocol-compliance": "protocol_compliance",
    "calls": "calls",
    "tokens": "tokens",
    "cost": "cost_usd",
}
PRIMARY_CONTRASTS = (
    ("full-broadcast-shared-transcript", "isolated-private-agents"),
    ("designated-reader-selective-sharing", "full-broadcast-shared-transcript"),
    ("pooled-consensus", "isolated-private-agents"),
    ("portfolio-preserving-structured", "pooled-consensus"),
)
CONDITIONAL_DIAGNOSTIC_ROLE = "secondary-selection-conditioned-diagnostic-only"
FORBIDDEN_UNCONDITIONAL_LABELS = frozenset(
    {
        "unconditional-architecture-effect",
        "primary-architecture-effect",
        "all-pairing-architecture-effect",
        "complete-case-unconditional",
    }
)


@dataclass(frozen=True)
class PairingClassification:
    """Exactly one terminal policy-v2 classification for an intended pairing."""

    pairing_id: str
    model: str
    task_commitment: str
    architecture_id: str
    trace_id: str
    status: PairingStatus
    provider_response_completed: bool
    method_c_errors: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status not in PAIRING_STATUSES:
            raise ValueError("unregistered pairing status")
        if self.status == PROVIDER_TERMINAL_MISSING:
            if self.provider_response_completed:
                raise ValueError("provider-terminal-missing cannot have a completed response")
        elif not self.provider_response_completed:
            raise ValueError("protocol classification requires a completed provider response")
        if self.status == PROTOCOL_VALID and self.method_c_errors:
            raise ValueError("protocol-valid pairing cannot carry Method C errors")
        if self.status == PROTOCOL_INVALID and not self.method_c_errors:
            raise ValueError("protocol-invalid pairing requires a safe Method C error class")

    def serializable(self) -> dict[str, object]:
        return {
            "pairing_id": self.pairing_id,
            "model": self.model,
            "task_commitment": self.task_commitment,
            "architecture_id": self.architecture_id,
            "trace_id": self.trace_id,
            "status": self.status,
            "provider_response_completed": self.provider_response_completed,
            "method_c_errors": list(self.method_c_errors),
        }


@dataclass(frozen=True)
class MetricInterval:
    """Exact rational feasible interval for one metric-eligible pairing."""

    pairing_id: str
    model: str
    task_commitment: str
    architecture_id: str
    metric_id: str
    status: PairingStatus
    lower: Fraction
    upper: Fraction
    operational_credit: str
    exact_metric_defined: bool

    def __post_init__(self) -> None:
        if self.metric_id not in METRIC_IDS:
            raise ValueError("unregistered metric")
        if self.status == PROVIDER_TERMINAL_MISSING:
            raise ValueError("provider-terminal-missing is batch-quarantining, not bounded")
        if self.lower > self.upper:
            raise ValueError("metric interval lower bound exceeds upper bound")
        if self.status == PROTOCOL_VALID and self.lower != self.upper:
            raise ValueError("protocol-valid metric interval must be exact")
        if (
            self.status == PROTOCOL_INVALID
            and self.exact_metric_defined
            and self.metric_id
            not in {
                "invalid-action-rate",
                "protocol-compliance",
                "calls",
                "tokens",
                "cost",
            }
        ):
            raise ValueError("invalid action-dependent metric cannot be marked exact")

    def serializable(self) -> dict[str, object]:
        return {
            "pairing_id": self.pairing_id,
            "model": self.model,
            "task_commitment": self.task_commitment,
            "architecture_id": self.architecture_id,
            "metric_id": self.metric_id,
            "status": self.status,
            "lower": str(self.lower),
            "upper": str(self.upper),
            "operational_credit": self.operational_credit,
            "exact_metric_defined": self.exact_metric_defined,
        }


@dataclass(frozen=True)
class ContrastBound:
    """All-intended-eligible-pairing bound for one registered contrast."""

    model: str
    metric_id: str
    left_architecture: str
    right_architecture: str
    intended_eligible_pairs: int
    lower: Fraction
    upper: Fraction

    def serializable(self) -> dict[str, object]:
        return {
            "model": self.model,
            "metric_id": self.metric_id,
            "left_architecture": self.left_architecture,
            "right_architecture": self.right_architecture,
            "intended_eligible_pairs": self.intended_eligible_pairs,
            "lower": str(self.lower),
            "upper": str(self.upper),
        }


@dataclass(frozen=True)
class BatchAcceptanceInputs:
    """Integrity and acceptance observations independent of protocol rate."""

    both_public_canaries_pass: bool = True
    fresh_custody_pass: bool = True
    response_ledger_trace_identity_exact: bool = True
    contamination_zero: bool = True
    caps_hold: bool = True
    output_lock_pass: bool = True
    no_call_after_lock: bool = True
    post_lock_unseal_and_commitments_pass: bool = True
    method_a_b_agree_where_defined: bool = True
    method_c_classifies_every_pairing: bool = True
    independent_bounds_agree: bool = True
    corruptions_pass: bool = True
    redaction_pass: bool = True
    execution_identity_matches: bool = True
    retained_state_safe: bool = True


@dataclass(frozen=True)
class BatchDisposition:
    """Engineering completion or honest quarantine without a conformance threshold."""

    batch_integrity_status: BatchIntegrityStatus | None
    decision: Literal["engineering-complete", "quarantine"]
    intended_pairings: int
    protocol_valid: int
    protocol_invalid: int
    provider_terminal_missing: int
    quarantine_reasons: tuple[str, ...]

    @property
    def quarantined(self) -> bool:
        return self.decision == "quarantine"


def classify_completed_pairing(
    *,
    pairing_id: str,
    model: str,
    task_commitment: str,
    architecture_id: str,
    trace_id: str,
    provider_response_completed: bool,
    method_c_errors: Sequence[str],
) -> PairingClassification:
    """Apply provider-terminal precedence, then independent Method C."""

    errors = tuple(str(item) for item in method_c_errors)
    if not provider_response_completed:
        status: PairingStatus = PROVIDER_TERMINAL_MISSING
        errors = ()
    elif errors:
        status = PROTOCOL_INVALID
    else:
        status = PROTOCOL_VALID
    return PairingClassification(
        pairing_id=pairing_id,
        model=model,
        task_commitment=task_commitment,
        architecture_id=architecture_id,
        trace_id=trace_id,
        status=status,
        provider_response_completed=provider_response_completed,
        method_c_errors=errors,
    )


def validate_terminal_classifications(
    intended_pairing_ids: Iterable[str],
    classifications: Sequence[PairingClassification],
) -> dict[str, PairingClassification]:
    """Require exactly one unique terminal classification per intended pairing."""

    intended = tuple(str(item) for item in intended_pairing_ids)
    if len(set(intended)) != len(intended):
        raise ValueError("intended pairing registry contains duplicates")
    counts = Counter(item.pairing_id for item in classifications)
    duplicates = sorted(name for name, count in counts.items() if count != 1)
    actual = set(counts)
    expected = set(intended)
    if duplicates:
        raise ValueError("duplicate terminal pairing classification")
    if actual != expected:
        raise ValueError("missing or unexpected terminal pairing classification")
    return {item.pairing_id: item for item in classifications}


def _fraction(value: object) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, Decimal):
        return Fraction(value)
    if isinstance(value, int):
        return Fraction(value, 1)
    return Fraction(str(value))


def _eligible(task: TaskInstance, metric_id: str) -> bool:
    if metric_id == "recovery-budget-attainment":
        return task.baseline.recovery_budget is not None
    if metric_id == "source-diversity":
        return task.family_id == "common-source-acquisition"
    if metric_id == "distance-from-best-registered-equilibrium":
        return task.baseline.best_equilibrium is not None
    if metric_id == "distance-from-worst-registered-equilibrium":
        return task.baseline.worst_equilibrium is not None
    return True


def _invalid_bounds(task: TaskInstance, metric_id: str) -> tuple[Fraction, Fraction, str]:
    if metric_id in {
        "group-discovery",
        "distinct-action-coverage",
        "recovery-budget-attainment",
        "source-diversity",
    }:
        return Fraction(0), Fraction(1), "0-no-valid-action-credit"
    if metric_id == "duplication":
        return Fraction(0), Fraction(1), "none-no-valid-portfolio"
    if metric_id == "planner-regret":
        comparator = Fraction(task.baseline.planner_discovery)
        return comparator - 1, comparator, "none-no-valid-portfolio"
    if metric_id == "private-baseline-regret":
        comparator = Fraction(task.baseline.private_discovery)
        return comparator - 1, comparator, "none-no-valid-portfolio"
    if metric_id == "communication-induced-action-compression":
        return Fraction(-1), Fraction(1), "none-no-valid-paired-portfolio"
    if metric_id in {
        "distance-from-best-registered-equilibrium",
        "distance-from-worst-registered-equilibrium",
    }:
        return Fraction(0), Fraction(1), "none-no-valid-portfolio"
    if metric_id == "invalid-action-rate":
        return Fraction(1), Fraction(1), "1"
    if metric_id == "protocol-compliance":
        return Fraction(0), Fraction(0), "0"
    raise ValueError(f"operational metric requires an exact ledger value: {metric_id}")


def metric_intervals(
    *,
    task: TaskInstance,
    classification: PairingClassification,
    exact_metrics: Mapping[str, object],
) -> tuple[MetricInterval, ...]:
    """Create exact valid intervals or registered invalid feasible intervals."""

    if classification.status == PROVIDER_TERMINAL_MISSING:
        raise ValueError("provider-terminal-missing requires batch quarantine")
    normalized = dict(exact_metrics)
    if "tokens" not in normalized and {
        "input_tokens",
        "output_tokens",
    }.issubset(normalized):
        normalized["tokens"] = int(str(normalized["input_tokens"])) + int(
            str(normalized["output_tokens"])
        )
    intervals: list[MetricInterval] = []
    for metric_id in METRIC_IDS:
        if not _eligible(task, metric_id):
            continue
        field = METRIC_FIELD_NAMES[metric_id]
        if classification.status == PROTOCOL_VALID:
            if field not in normalized and metric_id not in normalized:
                raise ValueError(f"valid pairing is missing exact metric: {metric_id}")
            raw = normalized.get(field, normalized.get(metric_id))
            if raw is None:
                raise ValueError(f"valid eligible metric is undefined: {metric_id}")
            value = _fraction(raw)
            lower = upper = value
            credit = f"exact:{value}"
            exact_defined = True
        elif metric_id in {"calls", "tokens", "cost"}:
            if field not in normalized and metric_id not in normalized:
                raise ValueError(f"invalid pairing is missing operational metric: {metric_id}")
            raw = normalized.get(field, normalized.get(metric_id))
            value = _fraction(raw)
            lower = upper = value
            credit = f"exact-ledger:{value}"
            exact_defined = True
        else:
            lower, upper, credit = _invalid_bounds(task, metric_id)
            exact_defined = metric_id in {
                "invalid-action-rate",
                "protocol-compliance",
            }
        intervals.append(
            MetricInterval(
                pairing_id=classification.pairing_id,
                model=classification.model,
                task_commitment=classification.task_commitment,
                architecture_id=classification.architecture_id,
                metric_id=metric_id,
                status=classification.status,
                lower=lower,
                upper=upper,
                operational_credit=credit,
                exact_metric_defined=exact_defined,
            )
        )
    return tuple(intervals)


def architecture_contrast_bounds(
    intervals: Sequence[MetricInterval],
    *,
    contrasts: Sequence[tuple[str, str]] = PRIMARY_CONTRASTS,
) -> tuple[ContrastBound, ...]:
    """Bound every registered contrast over all intended metric-eligible pairs."""

    indexed: dict[tuple[str, str, str, str], MetricInterval] = {}
    for item in intervals:
        key = (item.model, item.task_commitment, item.architecture_id, item.metric_id)
        if key in indexed:
            raise ValueError("duplicate metric interval")
        indexed[key] = item
    models = sorted({item.model for item in intervals})
    metrics = [metric for metric in METRIC_IDS if any(i.metric_id == metric for i in intervals)]
    output: list[ContrastBound] = []
    for model in models:
        for metric_id in metrics:
            tasks = sorted(
                {
                    item.task_commitment
                    for item in intervals
                    if item.model == model and item.metric_id == metric_id
                }
            )
            for left_architecture, right_architecture in contrasts:
                lower_total = Fraction(0)
                upper_total = Fraction(0)
                included = 0
                for task_commitment in tasks:
                    left = indexed.get((model, task_commitment, left_architecture, metric_id))
                    right = indexed.get((model, task_commitment, right_architecture, metric_id))
                    if left is None and right is None:
                        continue
                    if left is None or right is None:
                        raise ValueError("metric-eligible intended contrast pairing is incomplete")
                    lower_total += left.lower - right.upper
                    upper_total += left.upper - right.lower
                    included += 1
                if not included:
                    continue
                output.append(
                    ContrastBound(
                        model=model,
                        metric_id=metric_id,
                        left_architecture=left_architecture,
                        right_architecture=right_architecture,
                        intended_eligible_pairs=included,
                        lower=lower_total / included,
                        upper=upper_total / included,
                    )
                )
    return tuple(output)


def valid_output_conditional_diagnostic(
    values: Sequence[object],
    *,
    label: str = CONDITIONAL_DIAGNOSTIC_ROLE,
) -> Mapping[str, object]:
    """Return only an explicitly secondary, selection-conditioned diagnostic."""

    if label in FORBIDDEN_UNCONDITIONAL_LABELS or label != CONDITIONAL_DIAGNOSTIC_ROLE:
        raise ValueError("complete-case estimate cannot be labeled unconditional")
    exact = tuple(_fraction(item) for item in values)
    return {
        "role": CONDITIONAL_DIAGNOSTIC_ROLE,
        "selection_condition": "protocol-valid-output",
        "n": len(exact),
        "estimate": (str(sum(exact, Fraction(0)) / len(exact)) if exact else None),
        "unconditional_architecture_effect": False,
    }


def assess_batch(
    *,
    intended_pairing_ids: Iterable[str],
    classifications: Sequence[PairingClassification],
    acceptance: BatchAcceptanceInputs | None = None,
) -> BatchDisposition:
    """Apply integrity/provider gates without any protocol-rate threshold."""

    if acceptance is None:
        acceptance = BatchAcceptanceInputs()
    intended = tuple(str(item) for item in intended_pairing_ids)
    reasons: list[str] = []
    try:
        classified = validate_terminal_classifications(intended, classifications)
    except ValueError:
        classified = {}
        reasons.append("missing-or-duplicate-pairing")
    counts = Counter(item.status for item in classified.values())
    if counts[PROVIDER_TERMINAL_MISSING]:
        reasons.append("provider-terminal-missing")
    flag_reasons = {
        "both_public_canaries_pass": "public-canary-failure",
        "fresh_custody_pass": "fresh-custody-failure",
        "response_ledger_trace_identity_exact": "response-ledger-trace-integrity-failure",
        "contamination_zero": "contamination",
        "caps_hold": "cap-breach",
        "output_lock_pass": "output-lock-failure",
        "no_call_after_lock": "call-after-lock",
        "post_lock_unseal_and_commitments_pass": "unseal-or-commitment-failure",
        "method_a_b_agree_where_defined": "method-a-b-disagreement",
        "method_c_classifies_every_pairing": "method-c-classification-failure",
        "independent_bounds_agree": "independent-bound-reconstruction-disagreement",
        "corruptions_pass": "corruption-acceptance",
        "redaction_pass": "redaction-failure",
        "execution_identity_matches": "execution-identity-mismatch",
        "retained_state_safe": "unsafe-retained-state",
    }
    integrity_keys = {
        "response_ledger_trace_identity_exact",
        "contamination_zero",
        "caps_hold",
        "output_lock_pass",
        "no_call_after_lock",
        "post_lock_unseal_and_commitments_pass",
        "method_a_b_agree_where_defined",
        "method_c_classifies_every_pairing",
        "independent_bounds_agree",
        "corruptions_pass",
        "redaction_pass",
        "execution_identity_matches",
        "retained_state_safe",
    }
    integrity_valid = bool(classified)
    for key, reason in flag_reasons.items():
        if not getattr(acceptance, key):
            reasons.append(reason)
            if key in integrity_keys:
                integrity_valid = False
    return BatchDisposition(
        batch_integrity_status=(BATCH_INTEGRITY_VALID if integrity_valid else None),
        decision=("quarantine" if reasons else "engineering-complete"),
        intended_pairings=len(intended),
        protocol_valid=counts[PROTOCOL_VALID],
        protocol_invalid=counts[PROTOCOL_INVALID],
        provider_terminal_missing=counts[PROVIDER_TERMINAL_MISSING],
        quarantine_reasons=tuple(dict.fromkeys(reasons)),
    )
