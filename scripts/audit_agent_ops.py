#!/usr/bin/env python3
"""Audit Agent Operations schemas, renderers, instructions, and corruptions."""

from __future__ import annotations

import copy
import json
import tempfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from distributed_discovery.agent_ops.core import (
    ROOT,
    AgentOpsError,
    GateObservation,
    authorization_challenge,
    hash_path,
    load_schema,
    load_yaml,
    render_context,
    render_handoff,
    render_prompt,
    sha256_file,
    validate,
    validate_gate_surface,
    write_authorization,
)

DOCS = ROOT / "docs/agent-ops"
FIXTURES = ROOT / "tests/fixtures/agent-ops"


def _expect_reject(action: Callable[[], object], label: str) -> None:
    try:
        action()
    except (AgentOpsError, jsonschema.ValidationError, KeyError, ValueError):
        return
    raise AssertionError(f"corruption was not rejected: {label}")


def _validate_schema_file(path: Path) -> None:
    schema = json.loads(path.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)


def _hydrate_gate() -> tuple[dict[str, Any], dict[str, Any], GateObservation]:
    gate = load_yaml(FIXTURES / "valid-owner-gate.yml")
    contract = load_yaml(ROOT / gate["task_contract"]["path"])
    commit = "1" * 40
    gate["commit"] = commit
    gate["pull_request"]["head_sha"] = commit
    gate["task_contract"]["sha256"] = sha256_file(ROOT / gate["task_contract"]["path"])
    gate["tree_hashes"]["docs/agent-ops"] = hash_path(DOCS)
    observation = GateObservation(
        branch=gate["branch"],
        commit=commit,
        remote_commit=commit,
        tracked_clean=True,
        pull_request_number=gate["pull_request"]["number"],
        pull_request_state="OPEN",
        pull_request_head_sha=commit,
        observed_execution_commit=commit,
        execution_commit_is_ancestor=True,
        observed_at_utc=datetime(2026, 7, 25, tzinfo=UTC),
    )
    return gate, contract, observation


def _audit_corruptions() -> dict[str, str]:
    gate, contract, observation = _hydrate_gate()
    validate_gate_surface(gate, contract, observation)
    outcomes: dict[str, str] = {"valid": "accepted"}

    manifest_commit = "2" * 40
    descendant_manifest = GateObservation(
        **{
            **observation.__dict__,
            "commit": manifest_commit,
            "remote_commit": manifest_commit,
            "pull_request_head_sha": manifest_commit,
        }
    )
    validate_gate_surface(gate, contract, descendant_manifest)
    outcomes["committed-manifest-descendant"] = "accepted"

    changed_observation = copy.copy(observation)
    wrong_branch = GateObservation(**{**changed_observation.__dict__, "branch": "wrong-branch"})
    _expect_reject(
        lambda: validate_gate_surface(gate, contract, wrong_branch),
        "wrong-branch",
    )
    outcomes["wrong-branch"] = "rejected"

    wrong_commit = copy.deepcopy(gate)
    wrong_commit["commit"] = "2" * 40
    _expect_reject(
        lambda: validate_gate_surface(wrong_commit, contract, observation),
        "wrong-commit",
    )
    outcomes["wrong-commit"] = "rejected"

    nonancestor = GateObservation(
        **{**descendant_manifest.__dict__, "execution_commit_is_ancestor": False}
    )
    _expect_reject(
        lambda: validate_gate_surface(gate, contract, nonancestor),
        "nonancestor-execution-commit",
    )
    outcomes["nonancestor-execution-commit"] = "rejected"

    stale_live_head = GateObservation(
        **{**descendant_manifest.__dict__, "pull_request_head_sha": "3" * 40}
    )
    _expect_reject(
        lambda: validate_gate_surface(gate, contract, stale_live_head),
        "stale-live-head",
    )
    outcomes["stale-live-head"] = "rejected"

    changed_tree = copy.deepcopy(gate)
    changed_tree["tree_hashes"]["docs/agent-ops"] = f"sha256:{'0' * 64}"
    _expect_reject(
        lambda: validate_gate_surface(changed_tree, contract, observation),
        "changed-tree",
    )
    outcomes["changed-tree"] = "rejected"

    changed_contract = copy.deepcopy(gate)
    changed_contract["task_contract"]["sha256"] = f"sha256:{'0' * 64}"
    _expect_reject(
        lambda: validate_gate_surface(changed_contract, contract, observation),
        "changed-task-contract",
    )
    outcomes["changed-task-contract"] = "rejected"

    stale_pr = GateObservation(**{**observation.__dict__, "pull_request_state": "CLOSED"})
    _expect_reject(
        lambda: validate_gate_surface(gate, contract, stale_pr),
        "stale-pr",
    )
    outcomes["stale-pr"] = "rejected"

    expired = copy.deepcopy(gate)
    expired["expires_at_utc"] = "2020-01-01T00:00:00Z"
    _expect_reject(
        lambda: validate_gate_surface(expired, contract, observation),
        "expired-gate",
    )
    outcomes["expired-gate"] = "rejected"

    cap_increase = copy.deepcopy(gate)
    cap_increase["hard_caps"]["spend"] = "1"
    cap_increase["remaining_caps"]["spend"] = "1"
    _expect_reject(
        lambda: validate_gate_surface(cap_increase, contract, observation),
        "cap-increase",
    )
    outcomes["cap-increase"] = "rejected"

    hidden_permission = copy.deepcopy(gate)
    hidden_permission["external_actions"][0]["permission"] = (
        "external_action_permissions.provider_calls"
    )
    _expect_reject(
        lambda: validate_gate_surface(hidden_permission, contract, observation),
        "hidden-permission",
    )
    outcomes["hidden-permission"] = "rejected"

    missing_prohibition = copy.deepcopy(gate)
    missing_prohibition["explicit_prohibitions"].remove("credential-read-outside-manifest")
    _expect_reject(
        lambda: validate_gate_surface(missing_prohibition, contract, observation),
        "missing-prohibition",
    )
    outcomes["missing-prohibition"] = "rejected"

    synthetic_authorization = load_yaml(FIXTURES / "invalid-synthetic-authorization.yml")
    _expect_reject(
        lambda: validate(synthetic_authorization, "owner-authorization.schema.json"),
        "synthetic-authorization",
    )
    outcomes["synthetic-authorization"] = "rejected"

    unsafe_path = copy.deepcopy(gate)
    unsafe_path["authorization_output_symbolic_path"] = "/tmp/authorization.yml"
    _expect_reject(
        lambda: validate_gate_surface(unsafe_path, contract, observation),
        "unsafe-output-path",
    )
    outcomes["unsafe-output-path"] = "rejected"

    _expect_reject(
        lambda: write_authorization(gate, "AUTHORIZE WRONG 0000000"),
        "challenge-mismatch",
    )
    outcomes["challenge-mismatch"] = "rejected"

    with tempfile.TemporaryDirectory(prefix="agent-ops-audit-") as temporary:
        config_root = Path(temporary)
        challenge = authorization_challenge(gate)
        first, first_prior = write_authorization(
            gate,
            challenge,
            config_root=config_root,
            now=datetime(2026, 7, 25, 1, tzinfo=UTC),
        )
        assert first.is_file() and first_prior is None
        second, second_prior = write_authorization(
            gate,
            challenge,
            config_root=config_root,
            now=datetime(2026, 7, 25, 2, tzinfo=UTC),
        )
        assert second.is_file() and second_prior is not None and second_prior.is_file()
        assert oct(second.stat().st_mode & 0o777) == "0o600"
        assert oct(second_prior.stat().st_mode & 0o777) == "0o600"
    outcomes["prior-authorization-replacement"] = "preserved-history"

    registry = load_yaml(FIXTURES / "corruptions.yml")["corruptions"]
    registered = {item["id"] for item in registry}
    assert registered == set(outcomes) - {"valid", "committed-manifest-descendant"}
    return outcomes


def audit() -> dict[str, Any]:
    """Run the complete Agent Operations audit."""

    schema_paths = sorted(DOCS.glob("*.schema.json")) + [DOCS / "task-types/task-type.schema.json"]
    for path in schema_paths:
        _validate_schema_file(path)

    validate(load_yaml(DOCS / "task-contract-template.yml"), "task-contract.schema.json")
    active_contract = load_yaml(ROOT / "tasks/agent-operations-v1.yml")
    task_contracts = sorted((ROOT / "tasks").glob("*.yml"))
    for task_contract_path in task_contracts:
        validate(load_yaml(task_contract_path), "task-contract.schema.json")
    validate(load_yaml(DOCS / "task-delta-template.yml"), "task-delta.schema.json")
    preview = load_yaml(ROOT / "reports/agent-ops/next-task-treasurebench-fresh-pilot.yml")
    validate(preview, "task-delta.schema.json")
    validate(load_yaml(DOCS / "owner-gate-template.yml"), "owner-gate.schema.json")
    validate(load_yaml(DOCS / "handoff-template.yml"), "handoff.schema.json")

    acceptance = load_yaml(DOCS / "acceptance-profiles.yml")
    jsonschema.validate(acceptance, load_schema("acceptance-profiles.schema.json"))
    assert acceptance["authority"] == "validation-defaults-only-never-permission"
    profile_names = set(acceptance["profiles"])

    task_type_schema = json.loads(
        (DOCS / "task-types/task-type.schema.json").read_text(encoding="utf-8")
    )
    task_type_paths = sorted(path for path in (DOCS / "task-types").glob("*.yml") if path.is_file())
    task_types = []
    for path in task_type_paths:
        profile = load_yaml(path)
        jsonschema.validate(profile, task_type_schema)
        assert profile["profile_grants_authority"] is False
        assert profile["default_acceptance_profile"] in profile_names
        task_types.append(profile["task_type"])
    assert len(set(task_types)) == 7

    for relative in active_contract["canonical_destinations"]:
        assert (ROOT / relative).exists(), relative
    assert (ROOT / active_contract["exec_plan"]).is_file()
    for reference in active_contract["authority_references"]:
        if not str(reference["path"]).startswith("https://"):
            assert (ROOT / reference["path"]).exists(), reference
    assert not any(active_contract["scientific_mutation_permissions"].values())
    assert not any(active_contract["private_data_permissions"].values())
    assert active_contract["external_action_permissions"]["provider_calls"] is False
    assert active_contract["external_action_permissions"]["spend"] is False

    instruction_paths = sorted(ROOT.rglob("AGENTS.md"))
    instruction_paths = [
        path
        for path in instruction_paths
        if ".git" not in path.parts and ".cache" not in path.parts
    ]
    instruction_sizes = {
        str(path.relative_to(ROOT)): path.stat().st_size for path in instruction_paths
    }
    assert instruction_sizes["AGENTS.md"] <= 8 * 1024
    assert all(
        size <= (8 * 1024 if relative == "AGENTS.md" else 6 * 1024)
        for relative, size in instruction_sizes.items()
    )
    assert sum(instruction_sizes.values()) <= 32 * 1024
    for path in instruction_paths:
        lowered = path.read_text(encoding="utf-8").lower()
        assert "start another codex session" not in lowered
        assert "launch another codex session" not in lowered

    issue_form = yaml.safe_load(
        (ROOT / ".github/ISSUE_TEMPLATE/agent-task.yml").read_text(encoding="utf-8")
    )
    ids = {item.get("id") for item in issue_form["body"]}
    assert {
        "task_type",
        "task_contract",
        "objective",
        "owner_decisions",
        "permissions",
        "expected_outcomes",
        "owner_gates",
        "scientific_mutation",
        "external_private_actions",
        "next_gate",
    } <= ids
    pr_template = (ROOT / ".github/PULL_REQUEST_TEMPLATE/agent-task.md").read_text(encoding="utf-8")
    for heading in (
        "Issue",
        "Task contract and ExecPlan",
        "Decision",
        "Scientific mutations",
        "Private and external actions",
        "Owner gates",
        "Validation profile",
        "Checkpoint or completion",
        "Next gate",
    ):
        assert f"## {heading}" in pr_template

    context_path = render_context(
        "tasks/agent-operations-v1.yml",
        output=ROOT / "build/agent-ops/audit/context.md",
    )
    prompt_path = render_prompt(
        "tasks/agent-operations-v1.yml",
        output=ROOT / "build/agent-ops/audit/prompt.md",
    )
    resume_path = render_prompt(
        "tasks/agent-operations-v1.yml",
        resume=True,
        output=ROOT / "build/agent-ops/audit/resume.md",
    )
    preview_prompt = render_prompt(
        "reports/agent-ops/next-task-treasurebench-fresh-pilot.yml",
        output=ROOT / "build/agent-ops/audit/fresh-pilot-preview-prompt.md",
    )
    handoff_yaml, handoff_markdown = render_handoff(
        "tasks/agent-operations-v1.yml",
        pull_request=195,
        validation_result="audit-agent-ops-pass",
        output_dir=ROOT / "build/agent-ops/audit/handoff",
    )
    validate(load_yaml(handoff_yaml), "handoff.schema.json")
    assert len(handoff_markdown.read_text(encoding="utf-8").splitlines()) < 50
    assert len(prompt_path.read_text(encoding="utf-8").splitlines()) <= 120
    assert prompt_path.stat().st_size <= 12 * 1024
    assert len(resume_path.read_text(encoding="utf-8").splitlines()) <= 30
    assert len(preview_prompt.read_text(encoding="utf-8").splitlines()) <= 120
    assert preview_prompt.stat().st_size <= 12 * 1024
    generated = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (context_path, prompt_path, resume_path, preview_prompt, handoff_markdown)
    )
    assert ".env.txt" not in generated
    assert "api_key" not in generated.lower()
    assert "XDG_STATE_HOME/distributed-discovery/treasurebench" not in generated

    assert "cannot create scientific truth" in (DOCS / "README.md").read_text(encoding="utf-8")
    corruptions = _audit_corruptions()
    return {
        "schemas": len(schema_paths),
        "task_contracts": len(task_contracts),
        "task_types": len(task_types),
        "acceptance_profiles": len(profile_names),
        "scoped_instructions": len(instruction_paths) - 1,
        "instruction_bytes": sum(instruction_sizes.values()),
        "prompt_lines": len(prompt_path.read_text(encoding="utf-8").splitlines()),
        "prompt_bytes": prompt_path.stat().st_size,
        "resume_lines": len(resume_path.read_text(encoding="utf-8").splitlines()),
        "preview_prompt_lines": len(preview_prompt.read_text(encoding="utf-8").splitlines()),
        "preview_prompt_bytes": preview_prompt.stat().st_size,
        "owner_gate_corruptions": corruptions,
        "scientific_authority": "unchanged",
        "private_paths_or_secrets": 0,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
