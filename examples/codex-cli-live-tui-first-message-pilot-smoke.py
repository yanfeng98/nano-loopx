#!/usr/bin/env python3
"""Validate the Codex CLI live TUI first-message pilot record."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "product" / "runtimes" / "codex-cli" / "codex-cli-live-tui-first-message-pilot.md"
FIRST_RUN = REPO_ROOT / "docs" / "product" / "runtimes" / "codex-cli" / "codex-cli-first-run-rehearsal.md"
PRODUCT_README = (
    REPO_ROOT / "docs" / "product" / "runtimes" / "codex-cli" / "README.md"
)
GOAL_ID = "public-live-tui-pilot-goal"
AGENT_ID = "codex-side-bypass"


def normalize(text: str) -> str:
    return " ".join(text.split())


def run_cli(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "loopx.cli", *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def assert_doc() -> None:
    text = DOC.read_text(encoding="utf-8")
    normalized = normalize(text)

    must_have = (
        "Codex CLI 实时 TUI 首消息试点",
        "状态：已记录 blocker；手动 TUI 引导保持为主要路径。",
        "记录时间：2026-06-21。",
        "一次性的 public-safe 仓库",
        "codex [OPTIONS] [PROMPT]",
        "--no-alt-screen",
        "--cd <DIR>",
        "resume",
        "remote-control",
        "codex doctor",
        "在手动中断前没有产生有界输出",
        "没有有界的首响应或完成信号",
        "捕获输出超出自动化预算",
        "仍保持活跃",
        "进程命令行",
        "live_tui_first_message_blocked_by_bounded_visible_completion_missing",
        "手动 TUI 引导保持为主要路径",
        "用户粘贴一条 LoopX 开始消息",
        "而不通过进程参数泄露项目特定 prompt 文本",
        "不读 transcript、不读 session 文件",
        "Codex CLI 有界可见 pilot adapter",
    )
    for phrase in must_have:
        assert phrase in normalized, phrase

    assert "LoopX 不应把自动化 `codex [PROMPT]` 启动宣传" in text
    assert "原始 TUI 输出、Codex transcript、session 文件" in normalized, text
    assert "不读 transcript、不读 session 文件" in normalized, text


def assert_indexes() -> None:
    product = PRODUCT_README.read_text(encoding="utf-8")
    first_run = FIRST_RUN.read_text(encoding="utf-8")
    assert "codex-cli-live-tui-first-message-pilot.md" in product, product
    assert "Codex CLI 实时 TUI 首条消息试点" in product, product
    assert "实时 TUI 试点说明" in first_run, first_run
    assert (
        "自动化实时启动需要先有有界的可见完成证据。" in first_run
    ), first_run


def assert_bootstrap_message_still_copy_first() -> None:
    message = run_cli(
        "codex-cli-bootstrap-message",
        "--project",
        "/tmp/loopx-live-tui-pilot.public",
        "--goal-id",
        GOAL_ID,
        "--agent-id",
        AGENT_ID,
        "--message-only",
    )
    normalized = normalize(message)
    assert message.startswith("Install and connect LoopX for this repo"), message
    assert not message.startswith("/goal "), message
    assert "Codex CLI TUI" in normalized, message
    assert "setup/bootstrap instruction" in normalized, message
    assert "/goal <thin task_body>" in normalized, message
    assert "raw Codex transcripts" in normalized, message
    assert "watch, steer, review, and take over" in normalized, message


def main() -> int:
    assert_doc()
    assert_indexes()
    assert_bootstrap_message_still_copy_first()
    print("codex-cli-live-tui-first-message-pilot-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
