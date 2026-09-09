#!/usr/bin/env python3
"""Smoke-test the host integration plugin plan contract."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN = REPO_ROOT / "docs" / "reference" / "protocols" / "host-integration-plugin-plan-v0.md"
PROTOCOL_INDEX = REPO_ROOT / "docs" / "reference" / "protocols" / "README.md"
DOCS_INDEX = REPO_ROOT / "docs" / "README.md"


def require(text: str, snippets: list[str], *, source: Path) -> None:
    compact = " ".join(text.split())
    missing = [
        snippet
        for snippet in snippets
        if snippet not in text and " ".join(snippet.split()) not in compact
    ]
    assert not missing, f"{source}: missing {missing}"


def main() -> int:
    plan = PLAN.read_text(encoding="utf-8")
    protocol_index = PROTOCOL_INDEX.read_text(encoding="utf-8")
    docs_index = DOCS_INDEX.read_text(encoding="utf-8")

    require(
        plan,
        [
            "host_integration_plugin_plan_v0",
            "skill 级 LoopX slash-command 回退",
            "host 自有命令注册表",
            "不是已交付插件清单",
            "LoopX CLI 保持事实来源",
            "codex_cli_slash_commands",
            "host_integration_surface_v0",
            "session_runtime_loopx_projection_v0",
            "## 插件能力集",
            "## 分阶段路径",
            "### 阶段 0：Skill 回退",
            "### 阶段 1：Host 命令别名",
            "### 阶段 2：Heartbeat 安装器",
            "### 阶段 3：Scheduler 提示适配器",
            "### 阶段 4：受控写入工具",
            "## 验收矩阵",
            "loopx heartbeat-prompt --thin --goal-id <goal-id>",
            "stateful_backoff.apply_needed",
            "quota scheduler-ack-current",
            "最后应用的 RRULE",
            "不花费配额",
            "原始 transcript 提交给插件",
            "插件拒绝或脱敏载荷",
            "CLI 不可用",
            "安装/doctor blocker",
            "raw_transcripts_accepted",
            "credentials_accepted",
            "public_local_paths_allowed",
        ],
        source=PLAN,
    )
    require(
        plan,
        [
            "不替换 CLI",
            "存储原始 transcript",
            "不把聊天 slash 命令当作",
            "默认做隐藏无头执行",
            "未知 `/loopx-debug-me`",
            "以 `loopx slash-commands` 帮助失效关闭",
        ],
        source=PLAN,
    )
    assert plan.index("### 阶段 0：Skill 回退") < plan.index("### 阶段 1：Host 命令别名")
    assert plan.index("### 阶段 1：Host 命令别名") < plan.index("### 阶段 2：Heartbeat 安装器")
    assert plan.index("### 阶段 2：Heartbeat 安装器") < plan.index("### 阶段 3：Scheduler 提示适配器")
    assert plan.index("### 阶段 3：Scheduler 提示适配器") < plan.index("### 阶段 4：受控写入工具")
    assert "raw transcript material" not in plan.lower()

    require(
        protocol_index,
        ["host_integration_plugin_plan_v0", "host-integration-plugin-plan-v0.md"],
        source=PROTOCOL_INDEX,
    )
    require(
        docs_index,
        ["reference/README.md"],
        source=DOCS_INDEX,
    )
    print("host-integration-plugin-plan-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
