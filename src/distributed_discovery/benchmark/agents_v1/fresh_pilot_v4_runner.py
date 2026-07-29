"""Policy-v2 staged runner for the wholly fresh AO-0010 pilot.

Completed protocol-invalid outputs are preserved, classified, bounded, and
retained. Provider-terminal missingness and integrity failures still stop the
stage for honest whole-batch quarantine.
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
    PROTOCOL_INVALID,
    PROTOCOL_VALID,
    MetricInterval,
    PairingClassification,
    architecture_contrast_bounds,
    classify_completed_pairing,
    metric_intervals,
)
from distributed_discovery.benchmark.agents_v1.protocol_validity_independent import (
    reconstruct_contrast_bounds,
    require_bound_agreement,
)
from distributed_discovery.benchmark.agents_v1.traces import build_trace
from distributed_discovery.benchmark.agents_v1.verification import verify_method_agreement


class ProviderTerminalMissingError(RuntimeError):
    """A completed transport attempt set produced no usable provider response."""

    def __init__(self, *, provider: str, model: str, error_class: str) -> None:
        self.provider = provider
        self.model = model
        self.error_class = error_class
        super().__init__(f"provider-terminal-missing:{provider}:{error_class}")


class _StopOnProviderTerminal:
    """Stop before any later logical call after a terminal provider response."""

    def __init__(self, adapter: AgentAdapter, *, provider: str, model: str) -> None:
        self.adapter = adapter
        self.provider = provider
        self.model = model
        self.manifest = adapter.manifest

    def respond(self, request: AdapterRequest) -> AdapterResponse:
        response = self.adapter.respond(request)
        if response.error_class is not None:
            raise ProviderTerminalMissingError(
                provider=self.provider,
                model=self.model,
                error_class=response.error_class,
            )
        return response


class ProtocolValidityPilotRunner:
    """Run a fixed stage with Method C classification before metric handling."""

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
        self.classification_root = state_root / "encrypted-protocol-classifications"
        self.bound_root = state_root / "encrypted-metric-bounds"
        for root in (self.trace_root, self.classification_root, self.bound_root):
            root.mkdir(parents=True, exist_ok=True, mode=0o700)
            root.chmod(0o700)

    def _seal_record(self, root: Path, *, domain: str, name: str, value: object) -> None:
        path = root / f"{sha256_hex(name.encode())}.sealed"
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise PermissionError("existing policy-v2 record is unsafe")
            stored = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(stored, Mapping):
                raise ValueError("existing policy-v2 sealed record is malformed")
            manifest = stored.get("manifest")
            if not isinstance(manifest, Mapping):
                raise ValueError("existing policy-v2 sealed manifest is malformed")
            sealed = SealedObject(
                domain=str(manifest["domain"]),
                nonce_hex=str(manifest["nonce_hex"]),
                ciphertext=bytes.fromhex(str(stored["ciphertext_hex"])),
                ciphertext_sha256=str(manifest["ciphertext_sha256"]),
                associated_data_sha256=str(manifest["associated_data_sha256"]),
            )
            if sealed.domain != domain:
                raise PermissionError("existing policy-v2 record domain changed")
            existing = unseal_object(
                sealed,
                key=self.trace_key,
                campaign_id=self.campaign_id,
                batch_id=self.batch_id,
            )
            if canonical_json(existing) != canonical_json(value):
                raise PermissionError("existing policy-v2 record content changed")
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
        return {
            "calls": len(records),
            "input_tokens": sum(int(str(item.get("input_tokens", 0))) for item in records),
            "output_tokens": sum(int(str(item.get("output_tokens", 0))) for item in records),
            "cost_usd": sum(
                (Decimal(str(item.get("cost_usd", "0"))) for item in records),
                Decimal("0"),
            ),
        }

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
            raise ValueError("unknown policy-v2 private stage")
        if set(adapters) != set(self.models):
            raise PermissionError("both exact frozen model routes are required")
        if not analyze and (verify_metrics or persist_analysis or return_private_bounds):
            raise ValueError("pre-lock execution cannot perform or persist analysis")

        classifications: list[PairingClassification] = []
        intervals: list[MetricInterval] = []
        method_disagreements = 0
        metric_range_errors = 0
        invalid_final_cardinalities = 0
        contamination_findings = 0
        protocol_valid = 0
        protocol_invalid = 0
        runs = 0
        for model in self.models:
            provider = self.providers[self.models.index(model)]
            validate_provider_route(provider, model)
            guarded = _StopOnProviderTerminal(
                adapters[model],
                provider=provider,
                model=model,
            )
            for task in tasks:
                for architecture in ARCHITECTURES:
                    trace_id = f"{stage}/{model}/{task.task_id}/{architecture}"
                    pairing_id = f"{model}/{task.commitment}/{architecture}"
                    run = run_architecture(task, architecture, guarded)
                    trace = build_trace(run)
                    if trace.audit["hidden_reasoning_stored"] is not False:
                        raise PermissionError("hidden reasoning storage is prohibited")
                    if persist_traces:
                        self._seal_record(
                            self.trace_root,
                            domain=f"fresh-v4-raw-trace/{trace_id}",
                            name=trace_id,
                            value=trace.raw,
                        )
                    runs += 1
                    if not analyze:
                        continue
                    contract = verify_protocol_contract(task, run)
                    classification = classify_completed_pairing(
                        pairing_id=pairing_id,
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
                        metrics.update(
                            self._operational_metrics(
                                model=model,
                                task_commitment=task.commitment,
                                architecture_id=architecture,
                            )
                        )
                        if verify_metrics:
                            method_disagreements += len(verify_method_agreement(metrics, task, run))
                            metric_range_errors += len(verify_metric_ranges(metrics))
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
                        raise AssertionError("provider terminal status must raise immediately")
                    pairing_intervals = metric_intervals(
                        task=task,
                        classification=classification,
                        exact_metrics=metrics,
                    )
                    intervals.extend(pairing_intervals)
                    if persist_analysis:
                        self._seal_record(
                            self.classification_root,
                            domain=f"fresh-v4-protocol-classification/{pairing_id}",
                            name=pairing_id,
                            value=classification.serializable(),
                        )
                        self._seal_record(
                            self.bound_root,
                            domain=f"fresh-v4-metric-bounds/{pairing_id}",
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
                "provider_terminal_missing": 0,
                "analysis": "deferred-until-post-lock-unseal",
                "raw_traces_persisted": runs if persist_traces else 0,
                "protocol_classifications_persisted": 0,
                "metric_bounds_persisted": 0,
            }

        if method_disagreements:
            raise RuntimeError("Method A/B disagreement requires quarantine")
        if metric_range_errors:
            raise RuntimeError("metric-range failure requires quarantine")
        if contamination_findings:
            raise RuntimeError("direct or probable contamination requires quarantine")

        primary = architecture_contrast_bounds(intervals)
        primary_records = [item.serializable() for item in primary]
        independent = reconstruct_contrast_bounds(
            [item.serializable() for item in intervals],
            PRIMARY_CONTRASTS,
        )
        require_bound_agreement(primary_records, independent)
        classification_payload = [item.serializable() for item in classifications]
        bound_payload = primary_records
        result: dict[str, object] = {
            "stage": stage,
            "tasks": len(tasks),
            "runs": runs,
            "terminal_pairings_classified": len(classifications),
            "protocol_valid": protocol_valid,
            "protocol_invalid": protocol_invalid,
            "provider_terminal_missing": 0,
            "method_disagreements": method_disagreements,
            "method_c_classification_failures": 0,
            "invalid_final_cardinalities": invalid_final_cardinalities,
            "metric_range_errors": metric_range_errors,
            "metric_bound_disagreements": 0,
            "incomplete_pairings": 0,
            "contamination_findings": contamination_findings,
            "metric_intervals": len(intervals),
            "architecture_contrast_bounds": len(primary),
            "classification_hash": f"sha256:{sha256_hex(canonical_json(classification_payload))}",
            "bound_hash": f"sha256:{sha256_hex(canonical_json(bound_payload))}",
            "independent_bound_agreement": True,
            "protocol_invalid_alone_quarantines": False,
        }
        if return_private_bounds:
            result["_private_primary_contrast_bounds"] = primary_records
            result["_private_independent_contrast_bounds"] = list(independent)
        return result
