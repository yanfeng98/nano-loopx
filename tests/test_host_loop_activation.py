from __future__ import annotations

from pathlib import Path

import pytest

from loopx.heartbeat_prompt import (
    build_heartbeat_prompt,
    uses_native_goal_host_loop,
)
from loopx.host_loop_activation import (
    AgentTypeError,
    agent_type_for_host_surface,
    build_host_loop_activation_packet,
    normalize_agent_type,
    scheduler_command_binding_for_agent_type,
)
from loopx.project_prompt import render_accountable_progress_refresh_command


@pytest.mark.parametrize(
    ("agent_type", "runtime_profile"),
    (
        ("codex-cli", "codex_cli"),
        ("claude-code", "claude_code"),
        ("opencode", "generic_cli"),
        ("pi", "generic_cli"),
    ),
)
def test_first_class_hosts_bind_one_runtime_profile(
    agent_type: str,
    runtime_profile: str,
) -> None:
    assert scheduler_command_binding_for_agent_type(agent_type) == {
        "runtime_profile": runtime_profile
    }


@pytest.mark.parametrize(
    ("runtime_profile", "expected"),
    (
        ("codex_cli", True),
        ("generic_cli", False),
        ("claude_code", False),
    ),
)
def test_native_goal_host_family_is_profile_driven(
    runtime_profile: str,
    expected: bool,
) -> None:
    assert uses_native_goal_host_loop(
        runtime_profile=runtime_profile,
        scheduler_execution_context=None,
    ) is expected


def test_pi_is_an_exact_host_type_with_visible_goal_extension_activation() -> None:
    assert normalize_agent_type("pi") == "pi"
    assert normalize_agent_type("Pi") == "pi"
    assert normalize_agent_type("pi-agent") == "pi"
    assert normalize_agent_type("pi_agent") == "pi"
    assert normalize_agent_type("earendil-pi") == "pi"
    assert agent_type_for_host_surface("pi") == "pi"
    assert agent_type_for_host_surface("pi-tui") == "pi"
    assert scheduler_command_binding_for_agent_type("pi") == {
        "runtime_profile": "generic_cli"
    }

    packet = build_host_loop_activation_packet(
        agent_type="pi",
        goal_id="fixture-goal",
        agent_id="pi-fixture",
        registered_agents=["pi-fixture"],
    )

    assert packet["host_surface"] == "pi_visible_goal_mode"
    assert packet["activation_method"] == "activate_loopx_pi_goal_extension"
    assert packet["setup_command"] == "loopx slash-commands --install --surface pi"
    assert packet["host_mutation"]["owner"] == "Pi LoopX goal extension"
    assert packet["host_mutation"]["host_tool"] == "loopx_goal_activate"
    assert packet["host_mutation"]["tool_argument_mapping"]["activationToken"] == (
        "pi_session_authority.token from the host startup/session packet"
    )
    assert packet["host_mutation"]["tool_argument_mapping"]["goalId"] == (
        "optional compatibility echo; host authority derives the value"
    )
    assert packet["host_mutation"]["tool_argument_mapping"]["objective"] == (
        "heartbeat_prompt.task_body"
    )
    assert "automation_update" not in str(packet)
    assert (
        "--runtime-profile generic_cli"
        in packet["commands"]["heartbeat_prompt"]
    )
    assert (
        packet["success_criteria"][0]
        == "The visible Pi session has a LoopX-backed goal bound through loopx_goal_activate."
    )


def test_pi_is_not_a_native_goal_host() -> None:
    # Pi's visible loop is extension-driven and gated by LoopX quota, so it is
    # not part of the native goal host family (like opencode, unlike codex-cli).
    assert scheduler_command_binding_for_agent_type("pi") == {
        "runtime_profile": "generic_cli"
    }


def test_deepseek_harness_is_an_exact_host_type_with_external_loop_activation() -> None:
    assert normalize_agent_type("dsh") == "deepseek-harness"
    assert normalize_agent_type("DeepSeek Harness") == "deepseek-harness"
    assert agent_type_for_host_surface("deepseek-harness") == "deepseek-harness"
    assert agent_type_for_host_surface("dsh") == "deepseek-harness"
    assert scheduler_command_binding_for_agent_type("deepseek-harness") == {
        "runtime_profile": "generic_cli"
    }

    packet = build_host_loop_activation_packet(
        agent_type="deepseek-harness",
        goal_id="fixture-goal",
        agent_id="dsh-fixture",
        registered_agents=["dsh-fixture"],
    )
    assert packet["host_surface"] == "deepseek_harness_automation_loop", packet
    assert packet["activation_method"] == "external_loop_driver", packet
    assert "--runtime-profile generic_cli" in packet["commands"]["heartbeat_prompt"], packet
    assert "--host dsh" in packet["entry_command_hint"], packet
    assert "loopx.dsh_goal_mode" in packet["entry_command_hint"], packet
    # The historical launcher stays a documented compatibility path.
    assert "scripts/dsh_turn_host_adapter.py" in packet["entry_command_hint"], packet


def test_deepseek_harness_native_is_distinct_same_session_host() -> None:
    assert normalize_agent_type("dsh-native") == "deepseek-harness-native"
    assert normalize_agent_type("DeepSeek Harness Native") == "deepseek-harness-native"
    assert agent_type_for_host_surface("deepseek-harness-native") == (
        "deepseek-harness-native"
    )
    assert scheduler_command_binding_for_agent_type("deepseek-harness-native") == {
        "runtime_profile": "generic_cli"
    }

    packet = build_host_loop_activation_packet(
        agent_type="deepseek-harness-native",
        goal_id="fixture-goal",
        agent_id="dsh-native-fixture",
        registered_agents=["dsh-native-fixture"],
    )
    assert packet["host_surface"] == "deepseek_harness_native_same_session"
    assert packet["activation_method"] == "same_session_plugin_driver"
    assert packet["host_mutation"]["host_loop_primitive"] == "exact live Agent.followup"
    assert "/loopx-init" in packet["entry_command_hint"]
    assert "loopx.dsh_goal_mode" not in packet["entry_command_hint"]

    from loopx.agent_onboarding import _skill_delivery_contract

    skill_delivery = _skill_delivery_contract("deepseek-harness-native")
    assert skill_delivery["owner"] == "dsh_loopx_plugin"
    assert skill_delivery["preferred_delivery"] == "dsh_loopx_init_command"
    assert skill_delivery["install_command"] == "/loopx-init"
    assert skill_delivery["entry_host_surface"] == "deepseek-harness-native"


@pytest.mark.parametrize(
    "runtime_profile",
    ("codex_cli",),
)
def test_goal_hosts_attribute_spend_to_current_progress_refresh(
    runtime_profile: str,
) -> None:
    payload = build_heartbeat_prompt(
        goal_id="goal-spend-attribution-fixture",
        thin=True,
        runtime_profile=runtime_profile,
    )
    task_body = payload["task_body"]
    refresh_command = f"`{payload['progress_refresh_state_command']}`"
    spend_command = f"`{payload['quota_spend_command']}`"

    assert task_body.index(refresh_command) < task_body.index(spend_command)
    assert "<PUBLIC_SAFE_PROGRESS_CLASSIFICATION>" in refresh_command
    assert "<ACTUAL_DELIVERY_BATCH_SCALE>" in refresh_command
    assert "<ACTUAL_DELIVERY_OUTCOME>" in refresh_command
    assert "--delivery-batch-scale multi_surface" not in refresh_command
    assert "--delivery-outcome outcome_progress" not in refresh_command
    normalized_task_body = " ".join(task_body.split())
    assert payload["quota_spend_command"].startswith("loopx --format json ")
    assert (
        "never default or upgrade them to `multi_surface` / `outcome_progress`"
        in normalized_task_body
    )
    assert "no pipe/retry" in normalized_task_body


def test_heartbeat_prompt_commands_keep_explicit_runtime_root() -> None:
    runtime_root = Path("/tmp/loopx-runtime-root-fixture")

    payload = build_heartbeat_prompt(
        goal_id="runtime-root-fixture",
        thin=True,
        runtime_root=runtime_root,
        runtime_profile="codex_cli",
        agent_id="runtime-agent",
        registered_agents=["runtime-agent"],
    )

    command_prefix = f"loopx --runtime-root {runtime_root}"

    assert payload["quota_guard_command"].startswith(
        f"{command_prefix} --format json quota should-run "
    )
    assert payload["quota_spend_command"].startswith(
        f"{command_prefix} --format json quota spend-slot "
    )
    assert payload["refresh_state_command"].startswith(
        f"{command_prefix} refresh-state "
    )
    assert payload["progress_refresh_state_command"].startswith(
        f"{command_prefix} refresh-state "
    )
    assert payload["thin_prompt_command"].startswith(
        f"{command_prefix} heartbeat-prompt "
    )
    assert '"$HOME/.codex/loopx/registry.global.json"' not in payload["task_body"]
    assert f"--runtime-root {runtime_root}" in payload["task_body"]


@pytest.mark.parametrize(
    "runtime_profile",
    ("codex_cli",),
)
def test_goal_hosts_share_narrow_runtime_skill_routing(
    runtime_profile: str,
) -> None:
    payload = build_heartbeat_prompt(
        goal_id="goal-runtime-routing-fixture",
        thin=True,
        runtime_profile=runtime_profile,
    )
    task_body = " ".join(payload["task_body"].split())

    assert (
        "Normal turns use CLI `interaction_contract`; use `loopx-project` for "
        "lifecycle/registry and `loopx-self-repair` for runtime/projection drift."
        in task_body
    )
    assert "A bounded segment is progress within this Goal" in task_body
    assert "do not create a successor merely to continue" in task_body


def test_goal_hosts_reuse_thin_dispatch_and_stay_compact() -> None:
    shared_rules = (
        "use selection_command when required",
        "No learning queue unless asked.",
    )
    common = {
        "goal_id": "goal-prompt-composition-fixture",
        "thin": True,
        "agent_id": "codex-main-control",
        "agent_scopes": ["visible goal delivery lane"],
        "registered_agents": ["codex-main-control"],
    }
    generic = build_heartbeat_prompt(
        **common,
        runtime_profile="generic_cli",
    )
    goal_hosts = [
        build_heartbeat_prompt(**common, runtime_profile="codex_cli"),
    ]

    for rule in shared_rules:
        assert rule in generic["task_body"]
    for payload in goal_hosts:
        for rule in shared_rules:
            assert rule in payload["task_body"]
        assert payload["interface_budget"]["budget_char_count"] <= 3_000
        assert payload["interface_budget"]["within_budget"] is True


def test_native_codex_goal_wait_rule_matches_blocked_resume_contract() -> None:
    cli_body = build_heartbeat_prompt(
        goal_id="cli-wait-fixture",
        thin=True,
        runtime_profile="codex_cli",
    )["task_body"]
    for body in (cli_body,):
        assert "call `update_goal` with `status=blocked`" in body
        assert "Only user `/goal resume`" in body
        assert "reactivates it; rerun quota after resume" in body


@pytest.mark.parametrize(
    ("runtime_profile", "expected_host"),
    (
        ("codex_cli", "visible Codex /goal task body"),
    ),
)
def test_native_goal_budget_error_names_the_actual_host(
    runtime_profile: str,
    expected_host: str,
) -> None:
    with pytest.raises(ValueError, match=expected_host):
        build_heartbeat_prompt(
            goal_id="oversized-native-goal",
            thin=True,
            runtime_profile=runtime_profile,
            permission_rule="x" * 4_000,
        )


def test_accountable_refresh_preserves_explicit_validated_turn_semantics() -> None:
    command = render_accountable_progress_refresh_command(
        "validated-turn-fixture",
        classification="contract_only_preparation",
        delivery_batch_scale="single_surface",
        delivery_outcome="surface_only",
    )

    assert "--classification contract_only_preparation" in command
    assert "--delivery-batch-scale single_surface" in command
    assert "--delivery-outcome surface_only" in command
    assert "multi_surface" not in command
    assert "outcome_progress" not in command


def test_new_agent_onboarding_defaults_to_fresh_identity() -> None:
    packet = build_host_loop_activation_packet(
        agent_type="codex-cli",
        goal_id="fixture-goal",
        registered_agents=["codex-existing"],
        fresh_agent_default=True,
    )

    assert packet["activation_state"] == "fresh_agent_registration_required"
    assert packet["activation_allowed"] is False
    gate = packet["identity_selection_gate"]
    assert gate["default_action"] == "register_fresh_agent"
    assert gate["fresh_agent_registration"]["recommended"] is True
    assert "register-agent --goal-id fixture-goal" in gate[
        "fresh_agent_registration"
    ]["preview_command"]
    assert "--require-new" in gate["fresh_agent_registration"]["preview_command"]
    assert gate["fresh_agent_registration"]["execute_command"].endswith(
        "--execute"
    )
    continuation = gate["fresh_agent_registration"]["continuation_contract"]
    assert continuation["requires_execute_result"] is True
    assert continuation["required_result"] == {
        "ok": True,
        "changed": True,
        "written": True,
        "global_sync": {"ok": True},
        "registration_readback": {"verified": True},
    }
    assert "preview as advisory" in gate["fresh_agent_registration"]["continuation"]
    assert len(gate["choices"]) == 1
    takeover = gate["choices"][0]
    assert takeover["agent_id"] == "codex-existing"
    assert takeover["mode"] == "takeover_existing_agent"
    assert takeover["requires_explicit_takeover_intent"] is True


@pytest.mark.parametrize(
    "agent_type",
    (
        "codex-cli",
        "claude-code",
        "opencode",
        "manual",
        "other-agent",
    ),
)
def test_identity_selection_preserves_v0_prompt_fields(
    agent_type: str,
) -> None:
    packet = build_host_loop_activation_packet(
        agent_type=agent_type,
        goal_id="v0-identity-selection-fixture",
        registered_agents=["agent-main", "agent-reviewer"],
    )

    choice = packet["identity_selection_gate"]["choices"][0]
    assert choice["heartbeat_prompt_json"]
    assert choice["heartbeat_prompt"]
    assert choice["activation_input_command"] == choice["heartbeat_prompt_json"]


def test_new_agent_onboarding_gates_an_empty_agent_registry() -> None:
    packet = build_host_loop_activation_packet(
        agent_type="codex-cli",
        goal_id="fixture-goal",
        registered_agents=[],
        fresh_agent_default=True,
    )

    gate = packet["identity_selection_gate"]
    assert packet["activation_allowed"] is False
    assert gate["default_action"] == "register_fresh_agent"
    assert gate["choices"] == []


def test_explicit_identity_preserves_existing_agent_continuation() -> None:
    packet = build_host_loop_activation_packet(
        agent_type="codex-cli",
        goal_id="fixture-goal",
        agent_id="codex-existing",
        registered_agents=["codex-existing"],
        fresh_agent_default=True,
    )

    assert packet["activation_state"] == "selected"
    assert packet["activation_allowed"] is True
    assert packet["agent_id"] == "codex-existing"
    assert packet["identity_selection_gate"] is None


def test_opencode_activation_uses_bridge_tool_and_generic_cli_quota() -> None:
    packet = build_host_loop_activation_packet(
        agent_type="opencode",
        goal_id="fixture-goal",
        agent_id="opencode-fixture",
        registered_agents=["opencode-fixture"],
    )

    assert packet["host_surface"] == "opencode_visible_goal_mode"
    assert packet["activation_method"] == "activate_loopx_opencode_goal_bridge"
    assert packet["host_mutation"]["host_tool"] == "loopx_goal_activate"
    assert packet["setup_command"].endswith(
        "--surface opencode --with-goal-bridge"
    )
    assert "--runtime-profile generic_cli" in packet["commands"]["heartbeat_prompt"]


def test_opencode2_activation_starts_the_goal_worker() -> None:
    packet = build_host_loop_activation_packet(
        agent_type="opencode2",
        goal_id="fixture-goal",
        agent_id="opencode2-fixture",
        registered_agents=["opencode2-fixture"],
    )

    assert packet["host_surface"] == "opencode2_goal_worker_mode"
    assert packet["activation_method"] == "start_opencode2_goal_worker"
    assert packet["host_mutation"]["host_tool"] == "opencode2-goal-worker"
    assert packet["host_mutation"]["cli_can_mutate_directly"] is True
    assert any(
        "opencode2-goal-worker" in str(step) for step in packet["activation_steps"]
    )
    assert "--runtime-profile generic_cli" in packet["commands"]["heartbeat_prompt"]


def test_standard_heartbeat_omits_inactive_visible_goal_host() -> None:
    payload = build_heartbeat_prompt(goal_id="standard-heartbeat-fixture", thin=True)

    assert "visible_goal_host" not in payload


def test_generic_cli_prompt_keeps_external_loop_semantics() -> None:
    payload = build_heartbeat_prompt(
        goal_id="generic-cli-fixture",
        thin=True,
        runtime_profile="generic_cli",
    )

    assert payload["interface_budget"]["mode"] == "thin"
    assert "--turn-instance-id" in payload["quota_guard_command"]
    assert "visible TraeX `/goal` task" not in payload["task_body"]


def test_ambiguous_codex_requires_explicit_cli_selection() -> None:
    with pytest.raises(AgentTypeError) as caught:
        normalize_agent_type("codex")

    assert caught.value.suggestions == ["codex-cli"]
