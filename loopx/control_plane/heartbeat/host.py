"""Heartbeat host detection helpers inside the heartbeat bounded context."""

from __future__ import annotations

import shlex
from typing import Any

from ...turn_identity import normalize_turn_instance_id
from ..scheduler.execution_context import (
    ExecutionMode,
    HostSurface,
    NATIVE_GOAL_RUNTIME_PROFILES,
    SchedulerOwner,
    SchedulerRuntimeProfile,
    resolve_scheduler_execution_context,
    scheduler_runtime_profile_for_execution_context,
)

HEARTBEAT_PROMPT_SCHEMA_VERSION = "loopx_heartbeat_prompt_v0"


def uses_native_goal_host_loop(
    *,
    runtime_profile: str | None,
    scheduler_execution_context: dict[str, Any] | None,
) -> bool:
    if runtime_profile:
        try:
            profile = SchedulerRuntimeProfile(runtime_profile)
        except ValueError:
            return False
        return profile in NATIVE_GOAL_RUNTIME_PROFILES
    if scheduler_execution_context is None:
        return False
    resolution = resolve_scheduler_execution_context(scheduler_execution_context)
    if not resolution.ok or resolution.context is None:
        return False
    context = resolution.context
    if context.execution_mode is not ExecutionMode.INTERACTIVE:
        return False
    return (
        context.host_surface is HostSurface.CODEX_CLI
        and context.scheduler_owner is SchedulerOwner.AGENT_CLI_LOOP
    )


def resolve_exact_heartbeat_turn_identity(
    *,
    turn_instance_id: str | None,
    agent_id: str | None,
    runtime_profile: str | None,
    scheduler_execution_context: dict[str, Any] | None,
) -> tuple[str | None, str, dict[str, str]]:
    """Validate and project an optional receipt-producing heartbeat identity."""

    normalized = normalize_turn_instance_id(turn_instance_id)
    if normalized is None:
        return None, "", {}
    if not agent_id:
        raise ValueError("--turn-instance-id requires exact --agent-id identity")
    try:
        profile = (
            SchedulerRuntimeProfile(runtime_profile)
            if runtime_profile is not None
            else scheduler_runtime_profile_for_execution_context(
                scheduler_execution_context
            )
        )
    except ValueError:
        profile = None
    if profile is not SchedulerRuntimeProfile.GENERIC_CLI_AGENT_LOOP:
        raise ValueError(
            "--turn-instance-id requires runtime-profile generic_cli "
            "so quota guard creates a heartbeat receipt"
        )
    return normalized, f" --turn-instance-id {shlex.quote(normalized)}", {
        "schema_version": HEARTBEAT_PROMPT_SCHEMA_VERSION,
        "turn_instance_id": normalized,
    }
