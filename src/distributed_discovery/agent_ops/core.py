"""Core Agent Operations rendering and fail-closed owner-gate logic."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[3]
AGENT_OPS_DOCS = ROOT / "docs/agent-ops"
REQUIRED_PROHIBITIONS = {
    "provider-calls-outside-manifest",
    "credential-read",
    "unauthorized-private-access",
    "scientific-mutation-outside-contract",
    "cap-increase",
    "consequential-action-by-gate-engine",
}


class AgentOpsError(RuntimeError):
    """Raised when Agent Operations must fail closed."""


@dataclass(frozen=True)
class GateObservation:
    """Observed live state used to validate a committed owner-gate manifest."""

    branch: str
    commit: str
    remote_commit: str
    tracked_clean: bool
    pull_request_number: int
    pull_request_state: str
    pull_request_head_sha: str
    observed_at_utc: datetime


def _run(command: list[str], *, cwd: Path = ROOT, check: bool = True) -> str:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "command failed"
        raise AgentOpsError(f"{' '.join(command)}: {detail}")
    return result.stdout.strip()


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping."""

    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AgentOpsError(f"expected YAML mapping: {path}")
    return value


def load_schema(name: str) -> dict[str, Any]:
    """Load one Agent Operations JSON Schema."""

    value = json.loads((AGENT_OPS_DOCS / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AgentOpsError(f"expected JSON Schema mapping: {name}")
    return value


def validate(instance: dict[str, Any], schema_name: str) -> None:
    """Validate a mapping with format checks enabled."""

    jsonschema.Draft202012Validator(
        load_schema(schema_name),
        format_checker=jsonschema.FormatChecker(),
    ).validate(instance)


def sha256_file(path: Path) -> str:
    """Return the prefixed SHA-256 of one file."""

    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def hash_path(path: Path) -> str:
    """Hash a file or a directory inventory deterministically."""

    if path.is_file():
        return sha256_file(path)
    if not path.is_dir():
        raise AgentOpsError(f"hash path does not exist: {path}")
    digest = hashlib.sha256()
    files = sorted(
        candidate
        for candidate in path.rglob("*")
        if candidate.is_file() and "__pycache__" not in candidate.parts
    )
    for candidate in files:
        relative = candidate.relative_to(path).as_posix().encode()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        content = candidate.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return f"sha256:{digest.hexdigest()}"


def _safe_repo_path(relative: str) -> Path:
    candidate = (ROOT / relative).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError as error:
        raise AgentOpsError(f"path escapes repository: {relative}") from error
    return candidate


def _contract_path(task_path: str | Path) -> Path:
    path = Path(task_path)
    return path if path.is_absolute() else _safe_repo_path(path.as_posix())


def _git_state() -> dict[str, Any]:
    tracked_status = _run(["git", "status", "--porcelain", "--untracked-files=no"])
    return {
        "branch": _run(["git", "branch", "--show-current"]),
        "commit": _run(["git", "rev-parse", "HEAD"]),
        "tree": _run(["git", "rev-parse", "HEAD^{tree}"]),
        "base_main": _run(["git", "rev-parse", "origin/main"]),
        "tracked_clean": not tracked_status,
        "untracked_count": len(
            [
                line
                for line in _run(["git", "status", "--porcelain"]).splitlines()
                if line.startswith("??")
            ]
        ),
    }


def _github_observation(contract: dict[str, Any]) -> dict[str, Any]:
    github = contract["github"]
    repository = github["repository"]
    issue = github["issue"]
    branch = github["branch"]
    observation: dict[str, Any] = {
        "mode": "live-observation-not-authority",
        "issue": None,
        "pull_request": None,
    }
    if issue:
        raw = _run(
            [
                "gh",
                "issue",
                "view",
                str(issue),
                "--repo",
                str(repository),
                "--json",
                "number,state,title,url",
            ]
        )
        observation["issue"] = json.loads(raw)
    raw_pr = _run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            str(repository),
            "--head",
            str(branch),
            "--state",
            "all",
            "--limit",
            "1",
            "--json",
            "number,state,isDraft,headRefOid,baseRefName,url",
        ]
    )
    pulls = json.loads(raw_pr)
    if isinstance(pulls, list) and pulls:
        observation["pull_request"] = pulls[0]
    return observation


def _program_due_items() -> list[str]:
    registry = load_yaml(ROOT / "docs/program-memory/registry.yml")
    due = []
    for record in registry["records"]:
        if record["status"] in {"evidence-dependent", "deferred"}:
            due.append(
                f"{record['idea_id']}: {record['status']}; review trigger={record['review_after']}"
            )
    return due


def relevant_instructions(scope_paths: list[str]) -> list[Path]:
    """Resolve root and scoped instructions for every declared task path."""

    instructions = {ROOT / "AGENTS.md"}
    for raw_path in scope_paths:
        parts = Path(raw_path).parts
        current = ROOT
        for part in parts[:-1] if Path(raw_path).suffix else parts:
            current /= part
            candidate = current / "AGENTS.md"
            if candidate.is_file():
                instructions.add(candidate)
    return sorted(instructions)


def _acceptance_profile(name: str) -> dict[str, Any]:
    profiles = load_yaml(AGENT_OPS_DOCS / "acceptance-profiles.yml")["profiles"]
    profile = profiles.get(name)
    if not isinstance(profile, dict):
        raise AgentOpsError(f"unknown acceptance profile: {name}")
    return profile


def _write_generated(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def render_context(
    task_path: str | Path,
    *,
    live_github: bool = False,
    output: Path | None = None,
) -> Path:
    """Render an ignored, explicitly non-authoritative task context snapshot."""

    path = _contract_path(task_path)
    contract = load_yaml(path)
    validate(contract, "task-contract.schema.json")
    exec_plan = _safe_repo_path(contract["exec_plan"])
    if not exec_plan.is_file():
        raise AgentOpsError(f"missing ExecPlan: {exec_plan}")
    instructions = relevant_instructions(contract["scope"]["paths"])
    profile = _acceptance_profile(contract["acceptance_profile"])
    git_state = _git_state()
    github: dict[str, Any]
    if live_github:
        try:
            github = _github_observation(contract)
        except (AgentOpsError, json.JSONDecodeError) as error:
            github = {
                "mode": "live-observation-unavailable-not-authority",
                "error": str(error),
            }
    else:
        github = {
            "mode": "offline-contract-references-only-not-authority",
            "issue": contract["github"]["issue"],
            "pull_request": contract["github"]["pull_request"],
        }
    lines = [
        "# Generated Agent Operations context",
        "",
        "> Generated observation only. This file is ignored and is not authority.",
        "",
        f"- generated at UTC: {datetime.now(UTC).isoformat()}",
        f"- repository folder: {ROOT}",
        f"- task: {contract['task_id']} — {contract['title']}",
        f"- task contract: {path.relative_to(ROOT)} ({sha256_file(path)})",
        f"- ExecPlan: {exec_plan.relative_to(ROOT)}",
        f"- task type: {contract['task_type']}",
        f"- acceptance profile: {contract['acceptance_profile']}",
        "",
        "## Git observation",
        "",
        "```yaml",
        yaml.safe_dump(git_state, sort_keys=True).rstrip(),
        "```",
        "",
        "## GitHub observation",
        "",
        "```yaml",
        yaml.safe_dump(github, sort_keys=True).rstrip(),
        "```",
        "",
        "## Program-memory review queue",
        "",
    ]
    due_items = _program_due_items()
    lines.extend(f"- {item}" for item in due_items)
    lines.extend(["", "## Acceptance targets", ""])
    lines.extend(f"- `make {target}`" for target in profile["make_targets"])
    lines.extend(["", "### Invariants", ""])
    lines.extend(f"- {item}" for item in profile["invariants"])
    lines.extend(["", "## Relevant instructions", ""])
    for instruction in instructions:
        relative = instruction.relative_to(ROOT)
        lines.extend(
            [
                f"### `{relative}` ({instruction.stat().st_size} bytes)",
                "",
                instruction.read_text(encoding="utf-8").rstrip(),
                "",
            ]
        )
    task_type = contract["task_type"]
    lines.extend(["## Authority invariants", ""])
    lines.append("- Workflow metadata cannot create scientific truth or external service state.")
    if task_type.startswith("scientific"):
        lines.append(
            "- Study, run, claim, proof, and evidence policy remain independently required."
        )
    elif task_type == "private-evaluation":
        lines.append(
            "- Exact owner authorization and custody precede any private access, call, or spend."
        )
    elif task_type == "release-external-publication":
        lines.append(
            "- Exact release authorization and direct post-action verification are required."
        )
    else:
        lines.append(
            "- Scientific, private, provider, and release state remain unchanged by default."
        )
    target = output or ROOT / "build/agent-ops/context" / f"{contract['task_id']}.md"
    rendered = "\n".join(lines).rstrip() + "\n"
    if ".env" in rendered or "api_key" in rendered.lower():
        raise AgentOpsError("generated context contains a forbidden secret-path marker")
    return _write_generated(target, rendered)


def _true_permissions(contract: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for section in (
        "permissions",
        "external_action_permissions",
        "scientific_mutation_permissions",
        "private_data_permissions",
    ):
        values = contract[section]
        result.extend(f"{section}.{key}" for key, allowed in values.items() if allowed)
    return result


def render_prompt(
    task_path: str | Path,
    *,
    resume: bool = False,
    output: Path | None = None,
) -> Path:
    """Render a compact task bootstrap or candidate-registration prompt."""

    path = _contract_path(task_path)
    value = load_yaml(path)
    kind = value.get("kind")
    if kind == "task-contract":
        validate(value, "task-contract.schema.json")
        instructions = relevant_instructions(value["scope"]["paths"])
        instruction_list = ", ".join(str(item.relative_to(ROOT)) for item in instructions)
        lines = [
            f"Work in {ROOT}.",
            f"Task contract: {path.relative_to(ROOT)}.",
            f"Living ExecPlan: {value['exec_plan']}.",
            f"Read the applicable instructions: {instruction_list}.",
            "Verify live Git and GitHub state; generated observations are not authority.",
            (
                f"Use issue #{value['github']['issue']}, branch "
                f"`{value['github']['branch']}`, base `{value['github']['base']}`, and the "
                "single pull request observed for that branch."
            ),
            "Continue from the first incomplete ExecPlan milestone and preserve failed checks.",
            f"Objective: {value['objective']}",
        ]
        if not resume:
            lines.append("Task-specific owner decisions:")
            lines.extend(f"- {decision}" for decision in value["owner_decisions"])
            lines.append("Authorized true permissions:")
            lines.extend(f"- {permission}" for permission in _true_permissions(value))
            lines.append("Task-specific non-goals:")
            lines.extend(f"- {item}" for item in value["non_goals"])
        lines.extend(
            [
                f"Next gate: {value['next_gate']}",
                (
                    "Finish the turn with a schema-valid Agent Operations handoff naming "
                    "the exact next command and file."
                ),
                "Do not copy stable policy into the response or treat chat as canonical.",
            ]
        )
        slug = value["task_id"]
    elif kind == "task-delta":
        validate(value, "task-delta.schema.json")
        lines = [
            f"Work in {ROOT}.",
            f"Candidate task delta: {path.relative_to(ROOT)}.",
            "Read AGENTS.md and docs/agent-ops/README.md.",
            (
                "This candidate has no committed task contract, ExecPlan, issue, branch, "
                "or authorization."
            ),
            "Verify live state and register nothing unless the owner separately selects this gate.",
            f"Objective: {value['objective']}",
            "Task-specific owner decisions:",
        ]
        lines.extend(f"- {decision}" for decision in value["owner_decisions"])
        lines.extend(
            [
                f"Next gate: {value['next_gate']}",
                f"Expected input: {value.get('expected_input') or path.relative_to(ROOT)}",
                "Return a typed checkpoint handoff; do not execute the candidate task.",
            ]
        )
        slug = path.stem
    else:
        raise AgentOpsError(f"unsupported task artifact kind: {kind}")
    rendered = "\n".join(lines).rstrip() + "\n"
    line_limit = 30 if resume else 120
    if len(rendered.splitlines()) > line_limit:
        raise AgentOpsError(f"rendered prompt exceeds {line_limit} lines")
    if len(rendered.encode()) > 12 * 1024:
        raise AgentOpsError("rendered prompt exceeds 12 KiB")
    suffix = "-resume" if resume else ""
    target = output or ROOT / "build/agent-ops/prompts" / f"{slug}{suffix}.md"
    return _write_generated(target, rendered)


def render_handoff(
    task_path: str | Path,
    *,
    status: str = "legitimate-checkpoint",
    decision: str = "Continue from the first incomplete milestone.",
    validation_result: str = "pending",
    pull_request: int | None = None,
    last_completed_gate: str = "Task registration and current recorded milestones.",
    blocker: str | None = None,
    output_dir: Path | None = None,
) -> tuple[Path, Path]:
    """Render schema-valid YAML plus a compact human handoff."""

    path = _contract_path(task_path)
    contract = load_yaml(path)
    validate(contract, "task-contract.schema.json")
    git_state = _git_state()
    github = contract["github"]
    handoff: dict[str, Any] = {
        "schema_version": "agent-ops-handoff-v1",
        "status": status,
        "repository": github["repository"],
        "task_id": contract["task_id"],
        "issue": github["issue"],
        "pull_request": pull_request if pull_request is not None else github["pull_request"],
        "branch": git_state["branch"],
        "base_main": git_state["base_main"],
        "head_merge_sha": git_state["commit"],
        "task_contract": str(path.relative_to(ROOT)),
        "exec_plan": contract["exec_plan"],
        "last_completed_gate": last_completed_gate,
        "next_gate": contract["next_gate"],
        "decision": decision,
        "external_calls_cost": {
            "calls": 0,
            "cost": contract["budget"]["cumulative_spend"],
            "currency": contract["budget"]["currency"],
        },
        "private_state_change": "none",
        "scientific_state_change": "none",
        "validation": {
            "profile": contract["acceptance_profile"],
            "result": validation_result,
        },
        "owner_action": "" if status != "owner-gate-required" else "Authorize the exact gate.",
        "exact_next_command": f"make agent-context TASK={path.relative_to(ROOT)}",
        "exact_next_file": contract["exec_plan"],
        "blocker": blocker,
    }
    validate(handoff, "handoff.schema.json")
    directory = output_dir or ROOT / "build/agent-ops/handoffs"
    yaml_path = directory / f"{contract['task_id']}.yml"
    md_path = directory / f"{contract['task_id']}.md"
    _write_generated(yaml_path, yaml.safe_dump(handoff, sort_keys=False))
    human = [
        f"status: {handoff['status']}",
        f"repository: {handoff['repository']}",
        f"task: {handoff['task_id']} | issue: {handoff['issue']} | PR: {handoff['pull_request']}",
        f"branch: {handoff['branch']} | base/main: {handoff['base_main']}",
        f"head/merge SHA: {handoff['head_merge_sha']}",
        f"task contract: {handoff['task_contract']}",
        f"ExecPlan: {handoff['exec_plan']}",
        f"last completed gate: {handoff['last_completed_gate']}",
        f"next gate: {handoff['next_gate']}",
        f"decision: {handoff['decision']}",
        "external calls/cost: 0 / 0",
        "private-state change: none",
        "scientific-state change: none",
        (f"validation: {handoff['validation']['profile']} / {handoff['validation']['result']}"),
        f"owner action: {handoff['owner_action'] or 'none'}",
        f"exact next command: {handoff['exact_next_command']}",
        f"exact next file: {handoff['exact_next_file']}",
        f"blocker: {handoff['blocker'] or 'none'}",
    ]
    if len(human) >= 50:
        raise AgentOpsError("human handoff must remain below 50 lines")
    _write_generated(md_path, "\n".join(human) + "\n")
    return yaml_path, md_path


def _permission_allowed(contract: dict[str, Any], dotted: str) -> bool:
    section, key = dotted.split(".", 1)
    values = contract.get(section)
    return isinstance(values, dict) and values.get(key) is True


def _decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as error:
        raise AgentOpsError(f"invalid decimal value: {value}") from error


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise AgentOpsError(f"timestamp is not timezone aware: {value}")
    return parsed.astimezone(UTC)


def validate_gate_surface(
    gate: dict[str, Any],
    contract: dict[str, Any],
    observation: GateObservation,
    *,
    root: Path = ROOT,
) -> None:
    """Validate a gate against contract and exact observations."""

    validate(gate, "owner-gate.schema.json")
    validate(contract, "task-contract.schema.json")
    if gate["branch"] != observation.branch or gate["branch"] != contract["github"]["branch"]:
        raise AgentOpsError("owner gate branch mismatch")
    if gate["commit"] != observation.commit:
        raise AgentOpsError("owner gate commit mismatch")
    if observation.remote_commit != observation.commit:
        raise AgentOpsError("remote branch head does not match local commit")
    if not observation.tracked_clean:
        raise AgentOpsError("tracked tree is not clean")
    pull = gate["pull_request"]
    if pull["number"] != observation.pull_request_number:
        raise AgentOpsError("pull request number mismatch")
    if observation.pull_request_state != pull["expected_state"]:
        raise AgentOpsError("pull request is stale or not open")
    if pull["head_sha"] != observation.pull_request_head_sha:
        raise AgentOpsError("pull request head mismatch")
    if pull["head_sha"] != gate["commit"]:
        raise AgentOpsError("pull request does not point to gate commit")
    if gate["issue"] != contract["github"]["issue"]:
        raise AgentOpsError("owner gate issue mismatch")
    contract_path = (root / gate["task_contract"]["path"]).resolve()
    try:
        contract_path.relative_to(root.resolve())
    except ValueError as error:
        raise AgentOpsError("task contract path escapes repository") from error
    if sha256_file(contract_path) != gate["task_contract"]["sha256"]:
        raise AgentOpsError("task contract hash changed")
    for relative, expected in gate["tree_hashes"].items():
        candidate = (root / relative).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError as error:
            raise AgentOpsError(f"tree hash path escapes repository: {relative}") from error
        if hash_path(candidate) != expected:
            raise AgentOpsError(f"relevant tree changed: {relative}")
    if observation.observed_at_utc >= _parse_time(gate["expires_at_utc"]):
        raise AgentOpsError("owner gate expired")
    for group in ("irreversible_actions", "private_actions", "external_actions"):
        for action in gate[group]:
            if not _permission_allowed(contract, action["permission"]):
                raise AgentOpsError(f"hidden or unauthorized permission: {action['permission']}")
    prohibitions = set(gate["explicit_prohibitions"])
    if not prohibitions.issuperset(REQUIRED_PROHIBITIONS):
        raise AgentOpsError("owner gate is missing an explicit prohibition")
    for cap_state in ("cumulative_state", "hard_caps", "remaining_caps"):
        if gate[cap_state]["currency"] != contract["budget"]["currency"]:
            raise AgentOpsError("gate currency mismatch")
    cumulative = gate["cumulative_state"]
    hard = gate["hard_caps"]
    remaining = gate["remaining_caps"]
    if _decimal(cumulative["spend"]) + _decimal(remaining["spend"]) != _decimal(hard["spend"]):
        raise AgentOpsError("remaining spend does not reconcile to hard cap")
    if cumulative["calls"] + remaining["calls"] != hard["calls"]:
        raise AgentOpsError("remaining calls do not reconcile to hard cap")
    if _decimal(hard["spend"]) > _decimal(contract["budget"]["hard_cap"]):
        raise AgentOpsError("owner gate increases contract spend cap")
    if hard["calls"] > contract["budget"].get("call_cap", 0):
        raise AgentOpsError("owner gate increases contract call cap")
    category_keys = (
        set(cumulative["category_spend"])
        | set(hard["category_spend"])
        | set(remaining["category_spend"])
    )
    for key in category_keys:
        cumulative_value = _decimal(cumulative["category_spend"].get(key, "0"))
        hard_value = _decimal(hard["category_spend"].get(key, "0"))
        remaining_value = _decimal(remaining["category_spend"].get(key, "0"))
        if cumulative_value + remaining_value != hard_value:
            raise AgentOpsError(f"remaining category cap does not reconcile: {key}")
        contract_cap = contract["budget"]["category_caps"].get(key)
        if contract_cap is None or hard_value > _decimal(contract_cap):
            raise AgentOpsError(f"owner gate increases or hides category cap: {key}")
    expected_symbolic = (
        f"XDG_CONFIG_HOME/distributed-discovery/agent-ops/authorizations/{gate['gate_id']}.yml"
    )
    if gate["authorization_output_symbolic_path"] != expected_symbolic:
        raise AgentOpsError("unsafe authorization output path")


def collect_gate_observation(gate: dict[str, Any]) -> GateObservation:
    """Collect exact live state for an owner-gate CLI invocation."""

    branch = _run(["git", "branch", "--show-current"])
    commit = _run(["git", "rev-parse", "HEAD"])
    remote_line = _run(["git", "ls-remote", "--heads", "origin", f"refs/heads/{gate['branch']}"])
    remote_commit = remote_line.split()[0] if remote_line else ""
    tracked_clean = not _run(["git", "status", "--porcelain", "--untracked-files=no"])
    repository = load_yaml(_safe_repo_path(gate["task_contract"]["path"]))["github"]["repository"]
    raw = _run(
        [
            "gh",
            "pr",
            "view",
            str(gate["pull_request"]["number"]),
            "--repo",
            str(repository),
            "--json",
            "number,state,headRefOid",
        ]
    )
    pull = json.loads(raw)
    return GateObservation(
        branch=branch,
        commit=commit,
        remote_commit=remote_commit,
        tracked_clean=tracked_clean,
        pull_request_number=int(pull["number"]),
        pull_request_state=str(pull["state"]),
        pull_request_head_sha=str(pull["headRefOid"]),
        observed_at_utc=datetime.now(UTC),
    )


def authorization_challenge(gate: dict[str, Any]) -> str:
    """Return the exact required challenge phrase."""

    return f"AUTHORIZE {gate['gate_id']} {gate['commit'][:7]}"


def authorization_surface(gate: dict[str, Any]) -> str:
    """Render the complete owner confirmation surface."""

    return yaml.safe_dump(
        {
            "gate_id": gate["gate_id"],
            "issue": gate["issue"],
            "pull_request": gate["pull_request"],
            "branch": gate["branch"],
            "commit": gate["commit"],
            "task_contract": gate["task_contract"],
            "tree_hashes": gate["tree_hashes"],
            "purpose": gate["purpose"],
            "irreversible_actions": gate["irreversible_actions"],
            "private_actions": gate["private_actions"],
            "external_actions": gate["external_actions"],
            "cumulative_state": gate["cumulative_state"],
            "hard_caps": gate["hard_caps"],
            "remaining_caps": gate["remaining_caps"],
            "owner_confirmation_statements": gate["owner_confirmation_statements"],
            "explicit_prohibitions": gate["explicit_prohibitions"],
            "expires_at_utc": gate["expires_at_utc"],
            "next_milestone": gate["next_milestone"],
        },
        sort_keys=False,
    )


def _authorization_digest(value: dict[str, Any]) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return f"sha256:{hashlib.sha256(canonical).hexdigest()}"


def write_authorization(
    gate: dict[str, Any],
    challenge: str,
    *,
    config_root: Path | None = None,
    now: datetime | None = None,
) -> tuple[Path, Path | None]:
    """Write a validated mode-0600 authorization outside Git."""

    expected_challenge = authorization_challenge(gate)
    if challenge != expected_challenge:
        raise AgentOpsError("owner challenge mismatch")
    timestamp = now or datetime.now(UTC)
    if timestamp >= _parse_time(gate["expires_at_utc"]):
        raise AgentOpsError("owner gate expired before authorization write")
    base = config_root
    if base is None:
        configured = os.environ.get("XDG_CONFIG_HOME")
        base = Path(configured) if configured else Path.home() / ".config"
    output = (
        base / "distributed-discovery" / "agent-ops" / "authorizations" / f"{gate['gate_id']}.yml"
    ).resolve()
    try:
        output.relative_to(ROOT.resolve())
    except ValueError:
        pass
    else:
        raise AgentOpsError("authorization output must remain outside Git")
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    output.parent.chmod(0o700)
    prior: Path | None = None
    if output.exists():
        prior_bytes = output.read_bytes()
        history = output.parent / "history"
        history.mkdir(mode=0o700, exist_ok=True)
        history.chmod(0o700)
        stamp = timestamp.strftime("%Y%m%dT%H%M%SZ")
        prior = (
            history
            / f"{gate['gate_id']}-{stamp}-{hashlib.sha256(prior_bytes).hexdigest()[:12]}.yml"
        )
        if prior.exists():
            raise AgentOpsError("prior authorization history destination already exists")
        output.replace(prior)
        prior.chmod(0o600)
    authorization: dict[str, Any] = {
        "schema_version": "agent-ops-owner-authorization-v1",
        "kind": "owner-authorization",
        "synthetic": False,
        "gate_id": gate["gate_id"],
        "issue": gate["issue"],
        "pull_request": gate["pull_request"]["number"],
        "branch": gate["branch"],
        "commit": gate["commit"],
        "task_contract_sha256": gate["task_contract"]["sha256"],
        "tree_hashes": gate["tree_hashes"],
        "authorized_at_utc": timestamp.isoformat(),
        "expires_at_utc": gate["expires_at_utc"],
        "challenge": challenge,
        "owner_confirmation_statements": gate["owner_confirmation_statements"],
    }
    authorization["authorization_digest"] = _authorization_digest(authorization)
    validate(authorization, "owner-authorization.schema.json")
    temporary = output.with_suffix(".tmp")
    if temporary.exists():
        raise AgentOpsError("authorization temporary path already exists")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            yaml.safe_dump(authorization, stream, sort_keys=False)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    temporary.chmod(0o600)
    temporary.replace(output)
    output.chmod(0o600)
    loaded = load_yaml(output)
    validate(loaded, "owner-authorization.schema.json")
    mode = stat.S_IMODE(output.stat().st_mode)
    if mode != 0o600:
        raise AgentOpsError(f"authorization mode is not 0600: {oct(mode)}")
    return output, prior


def execute_owner_gate(gate_path: str | Path, challenge: str | None = None) -> dict[str, Any]:
    """Validate, display, challenge, and authorize without performing the action."""

    path = _contract_path(gate_path)
    gate = load_yaml(path)
    contract = load_yaml(_safe_repo_path(gate["task_contract"]["path"]))
    observation = collect_gate_observation(gate)
    validate_gate_surface(gate, contract, observation)
    surface = authorization_surface(gate)
    print(surface)
    expected = authorization_challenge(gate)
    print(f"Required challenge: {expected}")
    supplied = challenge if challenge is not None else input("Challenge: ").strip()
    output, prior = write_authorization(gate, supplied)
    print(gate["generated_resume_message"])
    return {
        "status": "authorized-no-consequential-action-performed",
        "authorization": str(output),
        "prior_authorization_preserved": str(prior) if prior else None,
        "resume_message": gate["generated_resume_message"],
    }


def copy_authorization_for_test(source: Path, destination: Path) -> None:
    """Test helper that preserves an authorization byte-for-byte."""

    shutil.copyfile(source, destination)
