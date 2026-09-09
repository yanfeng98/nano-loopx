from __future__ import annotations

from collections.abc import Mapping

from ...turn_identity import normalize_turn_instance_id
from ..quota.settlement import (
    SettlementPlan,
    build_turn_scoped_cli_settlement_plan,
)
from ..scheduler.execution_context import (
    NATIVE_GOAL_RUNTIME_PROFILES,
    SchedulerExecutionContextResolution,
    SchedulerRuntimeProfile,
    resolve_scheduler_execution_context,
)


def _hosted_scheduler_action(
    *,
    runtime_profile: SchedulerRuntimeProfile | None,
    scheduler_execution_context: Mapping[str, object]
    | SchedulerExecutionContextResolution
    | None,
) -> bool:
    """True when the explicit hosted-automation context owns this settlement.

    The removed Codex App profile used to carry this boundary; the surviving
    explicit (local_scheduler, host_automation, hosted_automation) context is
    its successor and keeps the bounded turn-scoped settlement semantics.
    """

    if runtime_profile is not None:
        return False
    resolution = resolve_scheduler_execution_context(scheduler_execution_context)
    return bool(
        resolution.ok
        and resolution.context is not None
        and resolution.context.codex_cli_applicable
    )


def build_accountable_work_item_settlement_plan(
    *,
    runtime_profile: SchedulerRuntimeProfile | None,
    scheduler_execution_context: (
        Mapping[str, object] | SchedulerExecutionContextResolution | None
    ) = None,
    goal_id: str,
    agent_id: str,
    todo_id: str | None,
    replan_obligation_id: str | None,
    scoped_cli_args: str,
    lifecycle_actor_args: str,
    turn_instance_id: str | None,
    delivery_boundary: str | None = None,
    command_prefix: str = "loopx",
) -> SettlementPlan | None:
    if _hosted_scheduler_action(
        runtime_profile=runtime_profile,
        scheduler_execution_context=scheduler_execution_context,
    ):
        normalized_turn_instance_id = normalize_turn_instance_id(turn_instance_id)
        turn_instance_id_ref = normalized_turn_instance_id or "${LOOPX_TURN:?}"
        return build_turn_scoped_cli_settlement_plan(
            goal_id=goal_id,
            agent_id=agent_id,
            command_prefix=command_prefix,
            todo_id=todo_id,
            replan_obligation_id=replan_obligation_id,
            scoped_cli_args=scoped_cli_args,
            lifecycle_actor_args=lifecycle_actor_args,
            turn_instance_id=turn_instance_id_ref,
            delivery_boundary=delivery_boundary,
            quota_spend_source="heartbeat",
        )
    if runtime_profile in NATIVE_GOAL_RUNTIME_PROFILES:
        normalized_turn_instance_id = normalize_turn_instance_id(turn_instance_id)
        if normalized_turn_instance_id is None:
            return None
        return build_turn_scoped_cli_settlement_plan(
            goal_id=goal_id,
            agent_id=agent_id,
            command_prefix=command_prefix,
            todo_id=todo_id,
            replan_obligation_id=replan_obligation_id,
            scoped_cli_args=scoped_cli_args,
            lifecycle_actor_args=lifecycle_actor_args,
            turn_instance_id=normalized_turn_instance_id,
            delivery_boundary=delivery_boundary,
            quota_spend_source="visible-goal",
        )
    if runtime_profile is not SchedulerRuntimeProfile.GENERIC_CLI_AGENT_LOOP:
        return None
    normalized_turn_instance_id = normalize_turn_instance_id(turn_instance_id)
    if normalized_turn_instance_id is None:
        return None
    return build_turn_scoped_cli_settlement_plan(
        goal_id=goal_id,
        agent_id=agent_id,
        command_prefix=command_prefix,
        todo_id=todo_id,
        replan_obligation_id=replan_obligation_id,
        scoped_cli_args=scoped_cli_args,
        lifecycle_actor_args=lifecycle_actor_args,
        turn_instance_id=normalized_turn_instance_id,
        delivery_boundary=delivery_boundary,
    )
