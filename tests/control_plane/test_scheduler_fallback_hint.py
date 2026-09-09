from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from loopx.control_plane.heartbeat.rules import (
    SCHEDULER_HINT_APPLICATION_RULE,
    SCHEDULER_HINT_COMPACT_RULE,
    SCHEDULER_HINT_THIN_RULE,
)
from loopx.control_plane.quota.live_decision import (
    bind_scheduler_followup_cli_routes,
)
from loopx.control_plane.quota.scheduler_ack import (
    record_quota_scheduler_ack_for_decision,
)
from loopx.control_plane.scheduler.scheduler_hint import build_scheduler_hint

GOAL_ID = "failure-hint-goal"
AGENT_ID = "codex-fixture"
APP_CONTEXT = {
    "host_surface": "local_scheduler",
    "scheduler_owner": "host_automation",
    "execution_mode": "hosted_automation",
    "source": "explicit",
}


def _active_decision() -> dict:
    return {
        "goal_id": GOAL_ID,
        "agent_identity": {"agent_id": AGENT_ID},
        "should_run": True,
        "effective_action": "normal_run",
        "recommended_action": "run the next bounded segment",
        "heartbeat_recommendation": {
            "recommended_mode": "steering_audit_then_one_step",
            "notify": "DONT_NOTIFY",
        },
        "execution_obligation": {
            "must_attempt_work": True,
            "kind": "work_lane_contract",
            "contract_obligation": "advance_one_bounded_segment",
        },
        "interaction_contract": {
            "schema_version": "loopx_interaction_contract_v0",
            "mode": "bounded_delivery",
            "user_channel": {"action_required": False, "notify": "DONT_NOTIFY"},
            "agent_channel": {
                "must_attempt": True,
                "delivery_allowed": True,
                "quiet_noop_allowed": False,
            },
        },
        "automation_liveness": {
            "keep_active": True,
            "automation_action": "execute_bounded_work",
            "spend_policy": "spend once only after validated writeback",
        },
        "capability_gate": {
            "action": "run",
            "available": ["shell", "filesystem_read", "filesystem_write"],
        },
    }


def _hint(
    decision: dict,
    *,
    scheduler_state: dict | None = None,
    host_rrule: str | None = None,
) -> dict:
    return build_scheduler_hint(
        decision,
        codex_cli_scheduler_state=scheduler_state,
        codex_cli_current_rrule=host_rrule,
        scheduler_execution_context=APP_CONTEXT,
    )


def _ack_state(
    hint: dict,
    *,
    runtime_root: Path,
    applied_rrule: str,
    generated_at: datetime,
) -> dict:
    event = record_quota_scheduler_ack_for_decision(
        {"goal_id": GOAL_ID, "scheduler_hint": hint},
        runtime_root=runtime_root,
        goal_id=GOAL_ID,
        agent_id=AGENT_ID,
        execute=True,
        applied_rrule=applied_rrule,
        generated_at=generated_at.isoformat(),
    )
    assert event["ok"] is True, event
    return event["scheduler_ack_event"]["scheduler_state"]


def test_apply_needed_projects_failure_hint_without_fallback() -> None:
    hint = _hint(
        _active_decision(),
        host_rrule="FREQ=MINUTELY;INTERVAL=15",
    )
    codex_app = hint["codex_cli"]
    assert codex_app["stateful_backoff"]["apply_needed"] is True

    assert "fallback_hint" not in codex_app
    assert codex_app["failure_hint"]["cli_args"][0] == "quota"
    assert "--observed-host-rrule" in codex_app["failure_hint"]["cli_args"]


def test_settled_cadence_omits_failure_hint(tmp_path: Path) -> None:
    now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    first = _hint(_active_decision())
    applied_rrule = first["codex_cli"]["recommended_rrule"]
    settled = _ack_state(
        first,
        runtime_root=tmp_path,
        applied_rrule=applied_rrule,
        generated_at=now,
    )

    second = _hint(
        _active_decision(),
        scheduler_state=settled,
        host_rrule=applied_rrule,
    )
    assert second["codex_cli"]["stateful_backoff"]["apply_needed"] is False
    assert "failure_hint" not in second["codex_cli"]


def test_scheduler_followup_routes_preserve_turn_lineage(tmp_path: Path) -> None:
    payload = {
        "scheduler_hint": {
            "codex_cli": {
                "ack_hint": {
                    "cli_args": [
                        "quota",
                        "scheduler-ack-current",
                        "--execute",
                    ],
                    "args": {},
                },
                "failure_hint": {
                    "cli_args": [
                        "quota",
                        "scheduler-fail-current",
                        "--execute",
                    ]
                },
            }
        }
    }
    turn_instance_id = "turn-scheduler-followup-001"

    bind_scheduler_followup_cli_routes(
        payload,
        registry_path=tmp_path / "registry.json",
        runtime_root=tmp_path / "runtime",
        turn_instance_id=turn_instance_id,
    )

    codex_app = payload["scheduler_hint"]["codex_cli"]
    for hint_name in ("ack_hint", "failure_hint"):
        hint = codex_app[hint_name]
        assert hint["cli_args"][-3:] == [
            "--turn-instance-id",
            turn_instance_id,
            "--execute",
        ]
        assert hint["route_binding"]["turn_instance_bound"] is True
    assert codex_app["ack_hint"]["args"]["turn_instance_id"] == turn_instance_id


def test_heartbeat_scheduler_rules_name_the_failure_path() -> None:
    for rule in (
        SCHEDULER_HINT_APPLICATION_RULE,
        SCHEDULER_HINT_COMPACT_RULE,
        SCHEDULER_HINT_THIN_RULE,
    ):
        assert "failure_hint" in rule
        assert "fallback_hint" not in rule
    assert "automation_update" in SCHEDULER_HINT_APPLICATION_RULE
