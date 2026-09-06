#!/usr/bin/env python3
"""Validate the public Codex CLI first-run rehearsal route."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "product" / "runtimes" / "codex-cli" / "codex-cli-first-run-rehearsal.md"
PRODUCT_README = (
    REPO_ROOT / "docs" / "product" / "runtimes" / "codex-cli" / "README.md"
)
DOCS_README = REPO_ROOT / "docs" / "README.md"
GETTING_STARTED = REPO_ROOT / "docs" / "guides" / "getting-started.md"
GOAL_ID = "public-codex-cli-goal"
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
        "Codex CLI 首次运行彩排",
        "PyPI 安装/更新，带打包 workflow skills 与归档兜底",
        "一条消息的 Codex CLI TUI 引导",
        "供之后可见自动化使用的 proof-capture 夹具",
        "Start LoopX for this repo",
        "python3 -m pip install --upgrade loopx",
        "loopx workflow-skills --install",
        "loopx codex-cli-bootstrap-message --project . --goal-id <goal-id> --message-only",
        "loopx codex-cli-tui-bootstrap-smoke-bundle",
        "loopx --format json codex-cli-visible-attach-acceptance",
        "仍未证明 same-open-TUI 自动化",
        "在证明路径通过之前，Same-TUI 自动化保持可选",
        "该首次运行路径不得",
        "要求克隆 LoopX 仓库",
        "读取原始 Codex transcript、session 文件、stdout、stderr、凭据或私有路径",
        "在验证写回之前 spend LoopX quota",
        "把 headless `codex exec` 当作默认用户体验",
    )
    for phrase in must_have:
        assert phrase in normalized, phrase

    first_response_index = normalized.index("当前 goal id")
    later_automation_index = normalized.index("Same-TUI 自动化保持可选")
    assert first_response_index < later_automation_index, text


def assert_indexes() -> None:
    product = PRODUCT_README.read_text(encoding="utf-8")
    docs = DOCS_README.read_text(encoding="utf-8")
    getting_started = GETTING_STARTED.read_text(encoding="utf-8")

    link = "codex-cli-first-run-rehearsal.md"
    assert link in product, product
    assert "product/README.md" in docs, docs
    assert f"../product/runtimes/codex-cli/{link}" in getting_started, getting_started
    assert "PyPI" in product, product
    assert "单消息 TUI 引导" in product, product
    assert "证明捕获夹具" in getting_started, getting_started


def assert_cli_surfaces_align() -> None:
    message = run_cli(
        "codex-cli-bootstrap-message",
        "--project",
        "/tmp/public-codex-cli-project",
        "--goal-id",
        GOAL_ID,
        "--agent-id",
        AGENT_ID,
        "--message-only",
    )
    normalized = normalize(message)
    assert message.startswith("Install and connect LoopX for this repo"), message
    assert not message.startswith("/goal "), message
    assert "setup/bootstrap instruction" in normalized, message
    assert "/goal <thin task_body>" in normalized, message
    assert "python3 -m pip install --upgrade loopx" in normalized, message
    assert "workflow-skills --install" in normalized, message
    assert "Codex CLI TUI" in normalized, message
    assert "quota should-run" in normalized, message
    assert "quota spend-slot" in normalized, message
    assert "raw Codex transcripts" in normalized, message

    bundle = run_cli(
        "codex-cli-tui-bootstrap-smoke-bundle",
        "--project",
        "/tmp/public-codex-cli-project",
        "--goal-id",
        GOAL_ID,
        "--agent-id",
        AGENT_ID,
    )
    normalized_bundle = normalize(bundle)
    assert "Codex CLI TUI Bootstrap Smoke Bundle" in normalized_bundle, bundle
    assert "runs_codex: `False`" in normalized_bundle, bundle
    assert "requires_loopx_repo_clone: `False`" in normalized_bundle, bundle


def main() -> int:
    assert_doc()
    assert_indexes()
    assert_cli_surfaces_align()
    print("codex-cli-first-run-rehearsal-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
