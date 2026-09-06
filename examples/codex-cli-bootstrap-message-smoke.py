#!/usr/bin/env python3
"""Smoke-test Codex CLI TUI bootstrap message generation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from loopx.project_prompt import build_codex_cli_bootstrap_message  # noqa: E402


PROJECT = Path("/tmp/public-codex-cli-project")
GOAL_ID = "public-codex-cli-goal"
AGENT_ID = "codex-side-bypass"

MUST_HAVE = (
    "one-message setup",
    "Codex CLI TUI",
    "setup/bootstrap instruction",
    "thin task_body",
    "/goal <thin task_body>",
    "heartbeat automation",
    "host loop surface",
    "hidden headless `codex exec`",
    "current goal id",
    "top user todo",
    "top agent todo",
    "next safe action",
    "shared global registry",
    "source_registry",
    "route collision",
    "goal is absent",
    "loopx bootstrap",
    "heartbeat-prompt --thin",
    "quota should-run",
    "--agent-id codex-side-bypass",
    "interaction_contract",
    "workspace_guard",
    "independent worktree",
    "raw Codex transcripts",
    "refresh-state",
    "quota spend-slot",
    "Do not spend quota for a setup-only turn",
    "python3 -m pip install --upgrade loopx",
    "workflow-skills --install",
    "huangruiteng.github.io/loopx/install.sh",
)


def assert_message_contract(payload: dict[str, object]) -> None:
    assert payload["ok"] is True, payload
    assert payload["schema_version"] == "codex_cli_bootstrap_message_v1", payload
    assert payload["invocation_mode"] == "codex_cli_setup_then_goal_mode", payload
    assert payload["goal_id"] == GOAL_ID, payload
    assert payload["agent_id"] == AGENT_ID, payload
    assert "python3 -m pip install --upgrade loopx" in str(payload["install_repair_command"]), payload
    assert "workflow-skills --install" in str(payload["install_repair_command"]), payload
    assert "huangruiteng.github.io/loopx/install.sh" in str(payload["install_repair_command"]), payload
    assert payload["existing_goal_probe_command"] == payload["quota_guard_command"], payload
    assert "heartbeat-prompt --thin" in str(payload["heartbeat_prompt_command"]), payload
    assert "heartbeat-prompt --thin" in str(payload["heartbeat_prompt_json_command"]), payload
    assert "--format json heartbeat-prompt" in str(payload["heartbeat_prompt_json_command"]), payload
    assert payload["codex_cli_goal_prefix"] == "/goal ", payload
    assert payload["codex_app_loop_surface"] == "heartbeat automation task_body", payload
    assert payload["codex_app_default_heartbeat_cadence"] == "initially 3 minutes, then follow quota scheduler_hint", payload
    assert "--agent-scope 'Codex CLI /goal visible TUI loop'" in str(payload["heartbeat_prompt_command"]), payload
    checklist = payload["first_run_validation_checklist"]
    assert isinstance(checklist, list) and len(checklist) >= 5, payload
    assert any("bootstrap/connect completed" in item for item in checklist), payload
    assert any("thin heartbeat task_body generated" in item for item in checklist), payload
    assert any("host loop surface activated" in item for item in checklist), payload
    assert any("registry/quota identity alone" in item for item in checklist), payload
    assert any("no raw Codex transcripts" in item for item in checklist), payload
    progress_refresh = str(payload["progress_refresh_command"])
    quota_spend = str(payload["quota_spend_command"])
    state_only_refresh = str(payload["refresh_command"])
    assert "--classification <PUBLIC_SAFE_PROGRESS_CLASSIFICATION>" in progress_refresh, payload
    assert "--delivery-batch-scale <ACTUAL_DELIVERY_BATCH_SCALE>" in progress_refresh, payload
    assert "--delivery-outcome <ACTUAL_DELIVERY_OUTCOME>" in progress_refresh, payload
    assert "--delivery-batch-scale multi_surface" not in progress_refresh, payload
    assert "--delivery-outcome outcome_progress" not in progress_refresh, payload
    assert "--agent-id codex-side-bypass" in progress_refresh, payload
    assert "--progress-scope agent_lane" in progress_refresh, payload
    message = str(payload["message"])
    normalized = " ".join(message.split())
    assert message.startswith("Install and connect LoopX for this repo"), message
    assert not message.startswith("/goal "), message
    for phrase in MUST_HAVE:
        assert phrase in normalized, (phrase, message)
    assert normalized.index("install or repair LoopX") < normalized.index("bootstrap/connect this project"), message
    assert normalized.index("probe whether this goal already exists") < normalized.index("bootstrap/connect this project"), message
    assert normalized.index("shared global registry for this goal") < normalized.index("loopx bootstrap"), message
    assert normalized.index("bootstrap/connect this project") < normalized.index("heartbeat-prompt --thin"), message
    assert normalized.index("quota should-run") < normalized.index("interaction_contract"), message
    assert message.index(progress_refresh) < message.index(quota_spend), message
    assert message.index(quota_spend) < message.rindex(state_only_refresh), message
    assert "must not carry a delivery outcome" in normalized, message
    assert "Do not append another accountable progress refresh after spend" in normalized, message
    assert "Never default or upgrade them to `multi_surface` / `outcome_progress`" in message, message
    assert "do not run `loopx bootstrap` for the same `goal_id`" in normalized, message
    assert "Only run bootstrap when the probe clearly says the goal is absent" in normalized, message
    assert "registry/quota identity alone" in normalized, message
    assert "Headless fallback should never be the only way" not in message, message
    assert "quota spend-slot --goal-id public-codex-cli-goal" in message, message
    assert "--source heartbeat --execute --agent-id codex-side-bypass" in message, message


def run_cli(*extra_args: str) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "loopx.cli", *extra_args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def assert_docs_surface_codex_cli_quickstart() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    getting_started = (REPO_ROOT / "docs/guides/getting-started.md").read_text(encoding="utf-8")
    product_contract = (REPO_ROOT / "docs/product/runtimes/codex-cli/codex-cli-tui-loop.md").read_text(encoding="utf-8")

    assert "Codex CLI" in readme, readme[:500]
    assert "可见 `/goal <task_body>`；默认不走隐藏 headless 执行" in readme
    assert "docs/product/runtimes/codex-cli/codex-cli-packaged-install.md" in readme
    assert "docs/product/runtimes/codex-cli/loopx-turn-codex-cli-quickstart.md" in readme
    assert "loopx codex-cli-bootstrap-message" in readme

    for text in (getting_started, product_contract):
        assert "Codex CLI" in text and "TUI" in text, text[:500]
        assert "Connect this repo to LoopX" in text, text[:500]
        assert "Do not clone the" in text, text[:500]
        assert "do not create or overwrite a goal" in text, text[:500]
        assert "heartbeat" in text, text[:500]
    for text in (getting_started, product_contract):
        assert "loopx codex-cli-bootstrap-message --project . --goal-id <goal-id>" in text, text[:500]

    normalized_getting_started = " ".join(getting_started.split())
    normalized_product_contract = " ".join(product_contract.split())
    assert "<project repo URL or current repo>" not in readme, readme
    assert "<project repo URL or current repo>" not in getting_started, getting_started
    assert "<项目仓库链接或当前 repo>" not in readme, readme
    assert "<项目仓库链接或当前 repo>" not in getting_started, getting_started
    assert "Connect the current project to LoopX." in getting_started, getting_started
    assert "不提供 headless 回退" in normalized_getting_started
    assert "一条 TUI 设置消息" in normalized_product_contract
    assert "安装或复用 LoopX" in normalized_getting_started
    assert "从 3 分钟开始" in normalized_getting_started
    assert (
        "把当前 Codex CLI goal 设置为 `/goal <thin task_body>`"
        in normalized_product_contract
        or "把当前 Codex CLI goal 设置为 `/goal <thin task_body>`"
        in normalized_getting_started
    ), product_contract
    assert "reuse it" in normalized_getting_started, getting_started
    assert "loopx codex-cli-bootstrap-message --project . --goal-id <goal-id>" not in readme, readme
    assert (
        "report the active state id, current user gate, top agent todo, and next safe action"
        in normalized_getting_started
    ), getting_started
    assert "首次运行路径不应要求你理解 registry 路径" in normalized_getting_started, getting_started
    assert 'App 上手体验的"先设置"改写' in normalized_getting_started, getting_started
    assert "Codex App 得到从 3 分钟开始" in normalized_getting_started, getting_started
    assert "无记录验证清单" in normalized_getting_started, getting_started
    assert "立即安装薄的 LoopX goal/heartbeat 正文" in normalized_product_contract, product_contract
    assert "设置路径可用后的可选自动化检查" in normalized_getting_started, getting_started
    assert "第一个有用的 TUI 响应应当是控制面快照" in normalized_product_contract, product_contract
    assert "纯设置工作" in normalized_product_contract, product_contract
    assert "loopx codex-cli-session-probe" in getting_started, getting_started
    assert "loopx codex-cli-exec-handoff --project . --goal-id <goal-id>" in getting_started, getting_started
    assert "无 headless 边界" in normalized_getting_started, getting_started
    assert "该命令不再打印可运行的 `codex exec` 交接脚本" in product_contract, product_contract


def main() -> int:
    payload = build_codex_cli_bootstrap_message(
        project=PROJECT,
        goal_id=GOAL_ID,
        agent_id=AGENT_ID,
        cli_bin="loopx",
    )
    assert_message_contract(payload)

    cli_json = json.loads(
        run_cli(
            "--format",
            "json",
            "codex-cli-bootstrap-message",
            "--project",
            str(PROJECT),
            "--goal-id",
            GOAL_ID,
            "--agent-id",
            AGENT_ID,
        )
    )
    assert_message_contract(cli_json)

    cli_markdown = run_cli(
        "codex-cli-bootstrap-message",
        "--project",
        str(PROJECT),
        "--goal-id",
        GOAL_ID,
        "--agent-id",
        AGENT_ID,
    )
    assert "# Codex CLI LoopX Bootstrap Message" in cli_markdown, cli_markdown
    assert "Copy the block below into Codex CLI TUI" in cli_markdown, cli_markdown
    assert "setup message, not the reusable heartbeat body" in cli_markdown, cli_markdown
    assert "`/goal <thin task_body>`" in cli_markdown, cli_markdown
    assert "Codex App loop: set heartbeat automation initially every 3 minutes" in cli_markdown, cli_markdown
    assert "heartbeat-prompt --thin" in cli_markdown, cli_markdown
    assert "Fresh Repo Install Repair" in cli_markdown, cli_markdown
    assert "Post-Bootstrap Thin Loop Prompt" in cli_markdown, cli_markdown
    assert "Transcript-Free Validation Checklist" in cli_markdown, cli_markdown
    assert "huangruiteng.github.io/loopx/install.sh" in cli_markdown, cli_markdown
    assert "python3 -m pip install --upgrade loopx" in cli_markdown, cli_markdown

    cli_message_only = run_cli(
        "codex-cli-bootstrap-message",
        "--project",
        str(PROJECT),
        "--goal-id",
        GOAL_ID,
        "--agent-id",
        AGENT_ID,
        "--message-only",
    )
    assert cli_message_only == str(payload["message"]) + "\n", cli_message_only
    assert "# Codex CLI LoopX Bootstrap Message" not in cli_message_only, cli_message_only
    assert "Fresh Repo Install Repair" not in cli_message_only, cli_message_only
    assert cli_message_only.startswith("Install and connect LoopX for this repo"), cli_message_only
    assert not cli_message_only.startswith("/goal "), cli_message_only

    cli_copy_only = run_cli(
        "codex-cli-bootstrap-message",
        "--project",
        str(PROJECT),
        "--goal-id",
        GOAL_ID,
        "--agent-id",
        AGENT_ID,
        "--copy-only",
    )
    assert cli_copy_only == cli_message_only, cli_copy_only
    assert_docs_surface_codex_cli_quickstart()

    print("codex-cli-bootstrap-message-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
