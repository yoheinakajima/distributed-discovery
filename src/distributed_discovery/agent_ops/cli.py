"""CLI integration for Agent Operations."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from distributed_discovery.agent_ops.core import (
    execute_owner_gate,
    render_context,
    render_handoff,
    render_prompt,
)


def configure(parser: argparse.ArgumentParser) -> None:
    """Configure the `distributed-discovery agent-ops` command."""

    commands = parser.add_subparsers(dest="agent_ops_command", required=True)
    context = commands.add_parser("render-context")
    context.add_argument("--task", required=True)
    context.add_argument("--live-github", action="store_true")
    context.add_argument("--output", type=Path)

    prompt = commands.add_parser("render-prompt")
    prompt.add_argument("--task", required=True)
    prompt.add_argument("--resume", action="store_true")
    prompt.add_argument("--output", type=Path)

    gate = commands.add_parser("owner-gate")
    gate.add_argument("--gate", required=True)
    gate.add_argument("--challenge")

    handoff = commands.add_parser("render-handoff")
    handoff.add_argument("--task", required=True)
    handoff.add_argument(
        "--status",
        choices=[
            "complete",
            "owner-gate-required",
            "legitimate-checkpoint",
            "stop-by-policy",
            "inconsistent-state",
        ],
        default="legitimate-checkpoint",
    )
    handoff.add_argument("--decision", default="Continue from the first incomplete milestone.")
    handoff.add_argument("--validation-result", default="pending")
    handoff.add_argument("--pull-request", type=int)
    handoff.add_argument(
        "--last-completed-gate",
        default="Task registration and current recorded milestones.",
    )
    handoff.add_argument("--blocker")
    handoff.add_argument("--output-dir", type=Path)


def execute(args: argparse.Namespace) -> dict[str, Any]:
    """Execute one Agent Operations subcommand."""

    if args.agent_ops_command == "render-context":
        path = render_context(
            args.task,
            live_github=args.live_github,
            output=args.output,
        )
        return {"status": "rendered-non-authoritative-context", "path": str(path)}
    if args.agent_ops_command == "render-prompt":
        path = render_prompt(args.task, resume=args.resume, output=args.output)
        return {
            "status": "rendered-thin-prompt",
            "path": str(path),
            "lines": len(path.read_text(encoding="utf-8").splitlines()),
            "bytes": path.stat().st_size,
        }
    if args.agent_ops_command == "owner-gate":
        return execute_owner_gate(args.gate, challenge=args.challenge)
    yaml_path, markdown_path = render_handoff(
        args.task,
        status=args.status,
        decision=args.decision,
        validation_result=args.validation_result,
        pull_request=args.pull_request,
        last_completed_gate=args.last_completed_gate,
        blocker=args.blocker,
        output_dir=args.output_dir,
    )
    return {
        "status": "rendered-typed-handoff",
        "yaml": str(yaml_path),
        "markdown": str(markdown_path),
    }
