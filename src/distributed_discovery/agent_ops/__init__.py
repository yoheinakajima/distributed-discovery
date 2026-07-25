"""Repository-native task contracts, context, owner gates, and handoffs."""

from distributed_discovery.agent_ops.core import (
    AgentOpsError,
    GateObservation,
    hash_path,
    render_context,
    render_handoff,
    render_prompt,
    validate_gate_surface,
    write_authorization,
)

__all__ = [
    "AgentOpsError",
    "GateObservation",
    "hash_path",
    "render_context",
    "render_handoff",
    "render_prompt",
    "validate_gate_surface",
    "write_authorization",
]
