"""Policy-v3 staged runner for the wholly fresh AO-0011 pilot.

Completed responses are classified under protocol-validity policy v2.
Registered operational availability failures create one terminal missing
record and remain in every intended denominator. Contract or safety failures
and the frozen operational circuit breaker stop the campaign immediately.
"""

from __future__ import annotations

import json
import secrets
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

from distributed_discovery.benchmark.agents_v1.adapters import (
    AdapterRequest,
    AdapterResponse,
    AgentAdapter,
)
from distributed_discovery.benchmark.agents_v1.contamination import classify_text
from distributed_discovery.benchmark.agents_v1.evaluation import evaluate_run
from distributed_discovery.benchmark.agents_v1.models import (
    TaskInstance,
    canonical_json,
    sha256_hex,
)
from distributed_discovery.benchmark.agents_v1.orchestration import (
    ARCHITECTURES,
    run_architecture,
)
from distributed_discovery.benchmark.agents_v1.pilot import (
    AppendOnlyLedger,
    SealedObject,
    atomic_private_write,
    seal_object,
    unseal_object,
    validate_provider_route,
)
from distributed_discovery.benchmark.agents_v1.protocol_contract import (
    verify_metric_ranges,
    verify_protocol_contract,
)
from distributed_discovery.benchmark.agents_v1.protocol_validity import (
    PRIMARY_CONTRASTS,
)
from distributed_discovery.benchmark.agents_v1.protocol_validity_independent import (
    reconstruct_contrast_bounds,
    require_bound_agreement,
)
from distributed_discovery.benchmark.agents_v1.provider_outcome import (
    PROTOCOL_INVALID,
    PROTOCOL_VALID,
    PROVIDER_CONTRACT_OR_SAFETY_FAILURE,
    PROVIDER_OPERATIONAL_MISSING,
    MetricIntervalV3,
    OperationalCircuitBreaker,
    PairingClassificationV3,
    ProviderErrorClassification,
    architecture_contrast_bounds_v3,
    classify_pairing_v3,
    classify_provider_error,
    metric_intervals_v3,
)
from distributed_discovery.benchmark.agents_v1.provider_outcome_independent import (
    require_provider_outcome_agreement,
)
from distributed_discovery.benchmark.agents_v1.traces import build_trace
from distributed_discovery.benchmark.agents_v1.verification import verify_method_agreement


class ProviderOperationalMissingError(RuntimeError):
    """One intended pairing has no usable response after bounded attempts."""

    def __init__(
        self,
        *,
        provider: str,
        model: str,
        classification: ProviderErrorClassification,
        completed_calls: Sequence[Mapping[str, object]],
        terminal_call: Mapping[str, object],
    ) -> None:
        self.provider = provider
        self.model = model
        self.classification = classification
        self.completed_calls = tuple(dict(item) for item in completed_calls)
        self.terminal_call = dict(terminal_call)
        super().__init__(f"provider-operational-missing:{provider}:{classification.taxonomy_class}")


class ProviderContractSafetyError(RuntimeError):
    """One provider, request, route, retention, or authority invariant failed."""

    def __init__(
        self,
        *,
        provider: str,
        model: str,
        classification: ProviderErrorClassification,
        completed_calls: Sequence[Mapping[str, object]],
        terminal_call: Mapping[str, object],
    ) -> None:
        self.provider = provider
        self.model = model
        self.classification = classification
        self.completed_calls = tuple(dict(item) for item in completed_calls)
        self.terminal_call = dict(terminal_call)
        super().__init__(
            f"provider-contract-or-safety-failure:{provider}:{classification.taxonomy_class}"
        )


class OperationalCircuitBreakerError(RuntimeError):
    """The frozen sequence-only availability guard fired."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"operational-circuit-breaker:{reason}")


# Compatibility name for callers that imported the v4 exception. Under v3,
# only a registered operational-missing outcome uses this path.
ProviderTerminalMissingError = ProviderOperationalMissingError


class _CaptureProviderOutcome:
    """Capture safely completed calls and stop at one terminal provider error."""

    def __init__(self, adapter: AgentAdapter, *, provider: str, model: str) -> None:
        self.adapter = adapter
        self.provider = provider
        self.model = model
        self.manifest = adapter.manifest
        self.completed_calls: list[dict[str, object]] = []

    @staticmethod
    def _call_record(
        request: AdapterRequest,
        response: AdapterResponse,
        *,
        retain_output: bool,
    ) -> dict[str, object]:
        return {
            "agent_id": request.prompt.agent_id,
            "round_number": request.round_number,
            "schema_retry": request.schema_retry,
            "final_required": request.final_required,
            "provider_response_completed": response.error_class is None,
            "raw_output": response.raw_output if retain_output else None,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "cost_usd": str(response.usage.cost_usd),
            },
            "declared_tool_calls": [dict(item) for item in response.declared_tool_calls],
            "operational_metadata": dict(response.operational_metadata),
        }

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        response = self.adapter.respond(request)
        if response.error_class is None:
            self.completed_calls.append(self._call_record(request, response, retain_output=True))
            return response
        classification = classify_provider_error(
            provider=self.provider,
            error_class=response.error_class,
            operational_metadata=response.operational_metadata,
        )
        terminal = self._call_record(request, response, retain_output=False)
        terminal["provider_error"] = classification.serializable()
        error_type: type[ProviderOperationalMissingError | ProviderContractSafetyError]
        error_type = (
            ProviderOperationalMissingError
            if classification.disposition == PROVIDER_OPERATIONAL_MISSING
            else ProviderContractSafetyError
        )
        raise error_type(
            provider=self.provider,
            model=self.model,
            classification=classification,
            completed_calls=self.completed_calls,
            terminal_call=terminal,
        )


class ProtocolValidityPilotRunner:
    """Run fixed stages under protocol-v2 plus provider-outcome policy v3."""

    def __init__(
        self,
        *,
        state_root: Path,
        ledger: AppendOnlyLedger,
        trace_key: bytes,
        campaign_id: str,
        batch_id: str,
        models: Sequence[str],
        providers: Sequence[str],
    ) -> None:
        if len(models) != len(providers) or not models:
            raise ValueError("exact model/provider routes must align")
        self.state_root = state_root
        self.ledger = ledger
        self.trace_key = trace_key
        self.campaign_id = campaign_id
        self.batch_id = batch_id
        self.models = tuple(models)
        self.providers = tuple(providers)
        self.trace_root = state_root / "encrypted-traces"
        self.classification_root = state_root / "encrypted-terminal-classifications"
        self.bound_root = state_root / "encrypted-metric-bounds"
        self.outcome_root = state_root / "encrypted-provider-outcomes"
        for root in (
            self.trace_root,
            self.classification_root,
            self.bound_root,
            self.outcome_root,
        ):
            root.mkdir(parents=True, exist_ok=True, mode=0o700)
            root.chmod(0o700)
        self._outcome_history = self._load_outcome_history()
        self._breaker = OperationalCircuitBreaker()
        self._reconstruct_breaker()

    def _sealed_value(self, path: Path) -> object:
        stored = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(stored, Mapping):
            raise ValueError("existing policy-v3 sealed record is malformed")
        manifest = stored.get("manifest")
        if not isinstance(manifest, Mapping):
            raise ValueError("existing policy-v3 sealed manifest is malformed")
        sealed = SealedObject(
            domain=str(manifest["domain"]),
            nonce_hex=str(manifest["nonce_hex"]),
            ciphertext=bytes.fromhex(str(stored["ciphertext_hex"])),
            ciphertext_sha256=str(manifest["ciphertext_sha256"]),
            associated_data_sha256=str(manifest["associated_data_sha256"]),
        )
        return unseal_object(
            sealed,
            key=self.trace_key,
            campaign_id=self.campaign_id,
            batch_id=self.batch_id,
        )

    def _seal_record(self, root: Path, *, domain: str, name: str, value: object) -> None:
        path = root / f"{sha256_hex(name.encode())}.sealed"
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise PermissionError("existing policy-v3 record is unsafe")
            if canonical_json(self._sealed_value(path)) != canonical_json(value):
                raise PermissionError("existing policy-v3 record content changed")
            return
        sealed = seal_object(
            domain=domain,
            value=value,
            key=self.trace_key,
            nonce=secrets.token_bytes(12),
            campaign_id=self.campaign_id,
            batch_id=self.batch_id,
        )
        atomic_private_write(
            path,
            canonical_json(
                {
                    "manifest": sealed.manifest(),
                    "ciphertext_hex": sealed.ciphertext.hex(),
                }
            )
            + b"\n",
        )

    def _load_outcome_history(self) -> dict[str, dict[str, object]]:
        records: list[dict[str, object]] = []
        for path in self.outcome_root.glob("*.sealed"):
            value = self._sealed_value(path)
            if not isinstance(value, Mapping):
                raise ValueError("provider-outcome history record is malformed")
            records.append({str(name): item for name, item in value.items()})
        records.sort(key=lambda item: int(str(item["sequence"])))
        if [int(str(item["sequence"])) for item in records] != list(range(len(records))):
            raise ValueError("provider-outcome sequence is not contiguous")
        output: dict[str, dict[str, object]] = {}
        for record in records:
            pairing_id = str(record["pairing_id"])
            if pairing_id in output:
                raise ValueError("duplicate provider-outcome pairing history")
            output[pairing_id] = record
        return output

    @staticmethod
    def _history_classification(
        record: Mapping[str, object],
    ) -> PairingClassificationV3:
        status = str(record["terminal_operational_status"])
        pairing_id = str(record["pairing_id"])
        common = {
            "pairing_id": pairing_id,
            "provider": str(record["provider"]),
            "model": str(record["model"]),
            "task_commitment": str(record["task_commitment"]),
            "architecture_id": str(record["architecture_id"]),
            "trace_id": str(record["trace_id"]),
        }
        if status == "provider-response-completed":
            return PairingClassificationV3(
                **common,
                status=PROTOCOL_VALID,
                provider_response_completed=True,
                protocol_compliance="pass",
                method_c_errors=(),
            )
        if status not in {
            PROVIDER_OPERATIONAL_MISSING,
            PROVIDER_CONTRACT_OR_SAFETY_FAILURE,
        }:
            raise ValueError("unregistered terminal operational history status")
        history_status = (
            PROVIDER_OPERATIONAL_MISSING
            if status == PROVIDER_OPERATIONAL_MISSING
            else PROVIDER_CONTRACT_OR_SAFETY_FAILURE
        )
        return PairingClassificationV3(
            **common,
            status=history_status,
            provider_response_completed=False,
            protocol_compliance="not-applicable",
            method_c_errors=(),
            provider_error_class=str(record["provider_error_class"]),
        )

    def _reconstruct_breaker(self) -> None:
        for record in sorted(
            self._outcome_history.values(),
            key=lambda item: int(str(item["sequence"])),
        ):
            snapshot = self._breaker.observe(
                self._history_classification(record),
                sequence=int(str(record["sequence"])),
            )
            recorded = record.get("circuit_breaker")
            if not isinstance(recorded, Mapping):
                raise ValueError("provider-outcome history lacks circuit state")
            if snapshot.serializable() != dict(recorded):
                raise ValueError("provider-outcome circuit history changed")

    def _record_outcome(
        self,
        *,
        classification: PairingClassificationV3,
        terminal_operational_status: str,
    ) -> object:
        existing = self._outcome_history.get(classification.pairing_id)
        expected_identity = {
            "provider": classification.provider,
            "model": classification.model,
            "task_commitment": classification.task_commitment,
            "architecture_id": classification.architecture_id,
            "trace_id": classification.trace_id,
            "terminal_operational_status": terminal_operational_status,
            "provider_error_class": classification.provider_error_class,
        }
        if existing is not None:
            if any(existing.get(name) != value for name, value in expected_identity.items()):
                raise PermissionError("provider-outcome replay identity changed")
            return existing["circuit_breaker"]
        if self._breaker.snapshot().fired:
            raise OperationalCircuitBreakerError(self._breaker.snapshot().reason or "already-fired")
        sequence = len(self._outcome_history)
        snapshot = self._breaker.observe(classification, sequence=sequence)
        record: dict[str, object] = {
            "schema_version": "treasurebench-agents-v1-provider-outcome-history-v1",
            "sequence": sequence,
            "pairing_id": classification.pairing_id,
            **expected_identity,
            "circuit_breaker": snapshot.serializable(),
        }
        self._seal_record(
            self.outcome_root,
            domain=f"fresh-v5-provider-outcome/{classification.pairing_id}",
            name=classification.pairing_id,
            value=record,
        )
        self._outcome_history[classification.pairing_id] = record
        return record["circuit_breaker"]

    def _operational_metrics(
        self,
        *,
        model: str,
        task_commitment: str,
        architecture_id: str,
    ) -> Mapping[str, object]:
        records = [
            record
            for record in self.ledger.records
            if record.get("event_type") == "provider-call"
            and record.get("model") == model
            and record.get("task_commitment") == task_commitment
            and record.get("architecture_id") == architecture_id
        ]
        if not records:
            raise RuntimeError("pairing has no exact provider-attempt ledger records")
        call_keys = {str(item["call_key"]) for item in records}
        transport_retries = sum(int(str(item.get("transport_attempt", 0))) > 0 for item in records)
        schema_repairs = len(
            {str(item["call_key"]) for item in records if item.get("schema_retry") is True}
        )
        return {
            "calls": len(records),
            "input_tokens": sum(int(str(item.get("input_tokens", 0))) for item in records),
            "output_tokens": sum(int(str(item.get("output_tokens", 0))) for item in records),
            "cost_usd": sum(
                (Decimal(str(item.get("cost_usd", "0"))) for item in records),
                Decimal("0"),
            ),
            "retry_count": transport_retries + schema_repairs,
            "logical_requests": len(call_keys),
        }

    @staticmethod
    def _missing_trace(
        *,
        stage: str,
        pairing_id: str,
        task: TaskInstance,
        architecture: str,
        error: ProviderOperationalMissingError | ProviderContractSafetyError,
    ) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_version": "treasurebench-agents-v1-terminal-missing-trace-v1",
            "stage": stage,
            "pairing_id": pairing_id,
            "task_instance_commitment": f"sha256:{task.commitment}",
            "architecture_id": architecture,
            "completed_prior_calls": list(error.completed_calls),
            "terminal_call": dict(error.terminal_call),
            "completed_prior_call_count": len(error.completed_calls),
            "action_created_for_missing_agent": False,
            "action_credit": False,
            "replacement_or_regeneration": False,
            "hidden_reasoning_stored": False,
        }
        value["trace_hash"] = f"sha256:{sha256_hex(canonical_json(value))}"
        return value

    @staticmethod
    def _require_independent_provider_agreement(
        classification: PairingClassificationV3,
        error: ProviderOperationalMissingError | ProviderContractSafetyError,
    ) -> None:
        source = {
            "pairing_id": classification.pairing_id,
            **error.classification.serializable(),
        }
        require_provider_outcome_agreement(
            (classification.serializable(),),
            (source,),
        )

    def run_stage(
        self,
        *,
        stage: str,
        tasks: Sequence[TaskInstance],
        adapters: Mapping[str, AgentAdapter],
        verify_metrics: bool = True,
        analyze: bool = True,
        persist_traces: bool = True,
        persist_analysis: bool = True,
        return_private_bounds: bool = False,
    ) -> Mapping[str, object]:
        if stage not in {"private-prefix", "fixed-full-batch"}:
            raise ValueError("unknown policy-v3 private stage")
        if set(adapters) != set(self.models):
            raise PermissionError("both exact frozen model routes are required")
        if not analyze and (verify_metrics or persist_analysis or return_private_bounds):
            raise ValueError("pre-lock execution cannot perform or persist analysis")
        if self._breaker.snapshot().fired:
            raise OperationalCircuitBreakerError(self._breaker.snapshot().reason or "already-fired")

        classifications: list[PairingClassificationV3] = []
        intervals: list[MetricIntervalV3] = []
        method_disagreements = 0
        metric_range_errors = 0
        invalid_final_cardinalities = 0
        contamination_findings = 0
        protocol_valid = 0
        protocol_invalid = 0
        provider_operational_missing = 0
        provider_contract_or_safety_failure = 0
        runs = 0
        for model, provider in zip(self.models, self.providers, strict=True):
            validate_provider_route(provider, model)
            for task in tasks:
                for architecture in ARCHITECTURES:
                    trace_id = f"{stage}/{model}/{task.task_id}/{architecture}"
                    pairing_id = f"{model}/{task.commitment}/{architecture}"
                    guarded = _CaptureProviderOutcome(
                        adapters[model],
                        provider=provider,
                        model=model,
                    )
                    try:
                        run = run_architecture(task, architecture, guarded)
                    except (
                        ProviderOperationalMissingError,
                        ProviderContractSafetyError,
                    ) as error:
                        missing_trace = self._missing_trace(
                            stage=stage,
                            pairing_id=pairing_id,
                            task=task,
                            architecture=architecture,
                            error=error,
                        )
                        if persist_traces:
                            self._seal_record(
                                self.trace_root,
                                domain=f"fresh-v5-terminal-missing-trace/{trace_id}",
                                name=trace_id,
                                value=missing_trace,
                            )
                        classification = classify_pairing_v3(
                            pairing_id=pairing_id,
                            provider=provider,
                            model=model,
                            task_commitment=task.commitment,
                            architecture_id=architecture,
                            trace_id=trace_id,
                            provider_response_completed=False,
                            provider_error=error.classification,
                        )
                        self._require_independent_provider_agreement(
                            classification,
                            error,
                        )
                        classifications.append(classification)
                        runs += 1
                        if classification.status == PROVIDER_OPERATIONAL_MISSING:
                            provider_operational_missing += 1
                        else:
                            provider_contract_or_safety_failure += 1
                        self._seal_record(
                            self.classification_root,
                            domain=(f"fresh-v5-terminal-classification/{pairing_id}"),
                            name=pairing_id,
                            value=classification.serializable(),
                        )
                        breaker_value = self._record_outcome(
                            classification=classification,
                            terminal_operational_status=classification.status,
                        )
                        if not isinstance(breaker_value, Mapping):
                            raise ValueError("circuit-breaker state is malformed") from error
                        if classification.status == (PROVIDER_CONTRACT_OR_SAFETY_FAILURE):
                            raise error
                        if analyze:
                            pairing_intervals = metric_intervals_v3(
                                task=task,
                                classification=classification,
                                exact_metrics=self._operational_metrics(
                                    model=model,
                                    task_commitment=task.commitment,
                                    architecture_id=architecture,
                                ),
                            )
                            intervals.extend(pairing_intervals)
                            if persist_analysis:
                                self._seal_record(
                                    self.bound_root,
                                    domain=f"fresh-v5-metric-bounds/{pairing_id}",
                                    name=pairing_id,
                                    value=[item.serializable() for item in pairing_intervals],
                                )
                        if breaker_value.get("fired") is True:
                            raise OperationalCircuitBreakerError(
                                str(breaker_value["reason"])
                            ) from error
                        continue

                    trace = build_trace(run)
                    if trace.audit["hidden_reasoning_stored"] is not False:
                        raise PermissionError("hidden reasoning storage is prohibited")
                    if persist_traces:
                        self._seal_record(
                            self.trace_root,
                            domain=f"fresh-v5-raw-trace/{trace_id}",
                            name=trace_id,
                            value=trace.raw,
                        )
                    runs += 1
                    completed_for_breaker = classify_pairing_v3(
                        pairing_id=pairing_id,
                        provider=provider,
                        model=model,
                        task_commitment=task.commitment,
                        architecture_id=architecture,
                        trace_id=trace_id,
                        provider_response_completed=True,
                    )
                    self._record_outcome(
                        classification=completed_for_breaker,
                        terminal_operational_status="provider-response-completed",
                    )
                    if not analyze:
                        continue
                    contract = verify_protocol_contract(task, run)
                    classification = classify_pairing_v3(
                        pairing_id=pairing_id,
                        provider=provider,
                        model=model,
                        task_commitment=task.commitment,
                        architecture_id=architecture,
                        trace_id=trace_id,
                        provider_response_completed=True,
                        method_c_errors=contract.errors,
                    )
                    classifications.append(classification)
                    invalid_final_cardinalities += contract.invalid_final_records
                    contamination_findings += sum(
                        classify_text(turn.response.raw_output).classification
                        in {"direct-leakage", "probable-memorization"}
                        for turn in run.turns
                    )
                    if classification.status == PROTOCOL_VALID:
                        protocol_valid += 1
                        metrics = asdict(evaluate_run(task, run))
                        if verify_metrics:
                            method_disagreements += len(verify_method_agreement(metrics, task, run))
                            metric_range_errors += len(verify_metric_ranges(metrics))
                        metrics.update(
                            self._operational_metrics(
                                model=model,
                                task_commitment=task.commitment,
                                architecture_id=architecture,
                            )
                        )
                    elif classification.status == PROTOCOL_INVALID:
                        protocol_invalid += 1
                        metrics = dict(
                            self._operational_metrics(
                                model=model,
                                task_commitment=task.commitment,
                                architecture_id=architecture,
                            )
                        )
                    else:
                        raise AssertionError("completed response has a non-protocol status")
                    pairing_intervals = metric_intervals_v3(
                        task=task,
                        classification=classification,
                        exact_metrics=metrics,
                    )
                    intervals.extend(pairing_intervals)
                    if persist_analysis:
                        self._seal_record(
                            self.classification_root,
                            domain=(f"fresh-v5-terminal-classification/{pairing_id}"),
                            name=pairing_id,
                            value=classification.serializable(),
                        )
                        self._seal_record(
                            self.bound_root,
                            domain=f"fresh-v5-metric-bounds/{pairing_id}",
                            name=pairing_id,
                            value=[item.serializable() for item in pairing_intervals],
                        )

        expected_runs = len(tasks) * len(ARCHITECTURES) * len(adapters)
        if runs != expected_runs:
            raise RuntimeError("architecture/model pairing is incomplete")
        if not analyze:
            return {
                "stage": stage,
                "tasks": len(tasks),
                "runs": runs,
                "provider_operational_missing": provider_operational_missing,
                "provider_contract_or_safety_failure": (provider_contract_or_safety_failure),
                "analysis": "deferred-until-post-lock-unseal",
                "raw_traces_persisted": runs if persist_traces else 0,
                "terminal_missing_classifications_persisted": (provider_operational_missing),
                "metric_bounds_persisted": 0,
                "circuit_breaker": self._breaker.snapshot().serializable(),
            }

        if method_disagreements:
            raise RuntimeError("Method A/B disagreement requires quarantine")
        if metric_range_errors:
            raise RuntimeError("metric-range failure requires quarantine")
        if contamination_findings:
            raise RuntimeError("direct or probable contamination requires quarantine")

        primary = architecture_contrast_bounds_v3(intervals)
        primary_records = [item.serializable() for item in primary]
        independent = reconstruct_contrast_bounds(
            [item.serializable() for item in intervals],
            PRIMARY_CONTRASTS,
        )
        require_bound_agreement(primary_records, independent)
        classification_payload = [item.serializable() for item in classifications]
        result: dict[str, object] = {
            "stage": stage,
            "tasks": len(tasks),
            "runs": runs,
            "terminal_pairings_classified": len(classifications),
            "protocol_valid": protocol_valid,
            "protocol_invalid": protocol_invalid,
            "provider_operational_missing": provider_operational_missing,
            "provider_contract_or_safety_failure": (provider_contract_or_safety_failure),
            "method_disagreements": method_disagreements,
            "method_c_classification_failures": 0,
            "invalid_final_cardinalities": invalid_final_cardinalities,
            "metric_range_errors": metric_range_errors,
            "metric_bound_disagreements": 0,
            "incomplete_pairings": 0,
            "contamination_findings": contamination_findings,
            "metric_intervals": len(intervals),
            "architecture_contrast_bounds": len(primary),
            "classification_hash": (f"sha256:{sha256_hex(canonical_json(classification_payload))}"),
            "bound_hash": (f"sha256:{sha256_hex(canonical_json(primary_records))}"),
            "independent_provider_outcome_agreement": True,
            "independent_bound_agreement": True,
            "protocol_invalid_alone_quarantines": False,
            "isolated_provider_operational_missing_alone_quarantines": False,
            "circuit_breaker": self._breaker.snapshot().serializable(),
        }
        if return_private_bounds:
            result["_private_primary_contrast_bounds"] = primary_records
            result["_private_independent_contrast_bounds"] = list(independent)
        return result
