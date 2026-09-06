#!/usr/bin/env python3
"""Validate the Codex CLI TUI continuation scheduling contract."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "product" / "runtimes" / "codex-cli" / "codex-cli-tui-continuation-priority.md"
PRODUCT_README = (
    REPO_ROOT / "docs" / "product" / "runtimes" / "codex-cli" / "README.md"
)
GETTING_STARTED = REPO_ROOT / "docs" / "guides" / "getting-started.md"


def normalize(text: str) -> str:
    return " ".join(text.split())


def assert_contract_doc() -> None:
    text = DOC.read_text(encoding="utf-8")
    normalized = normalize(text)

    must_have = (
        "Codex CLI TUI 延续优先级",
        "Frontstage 与 showcase 工作是很重要的支撑 surface",
        "不得排在可运行的 Codex CLI TUI 延续任务之前",
        "一条粘贴的 LoopX 消息启动 loop",
        "通过同一个可见 TUI 转向或恢复工作",
        "Codex CLI TUI 延续胜过 frontstage 打磨",
        "规划漂移",
        "same_tui_continuation_proven",
        "same_tui_continuation_blocked",
        "same_tui_continuation_gated",
        "带可见证明与 runtime idle evidence",
        "但不得读取原始 Codex transcripts、session 文件",
    )
    for phrase in must_have:
        assert phrase in normalized, phrase

    priority_index = normalized.index("调度规则")
    frontstage_index = normalized.index("frontstage 与 showcase 工作")
    assert priority_index < frontstage_index, text


def assert_indexes() -> None:
    product = PRODUCT_README.read_text(encoding="utf-8")
    getting_started = GETTING_STARTED.read_text(encoding="utf-8")

    link = "codex-cli-tui-continuation-priority.md"
    assert link in product, product
    assert f"../product/runtimes/codex-cli/{link}" in getting_started, getting_started
    assert "同一开 TUI 延续领先于" in product, product
    assert "frontstage 或 showcase 打磨" in getting_started, getting_started


def main() -> int:
    assert_contract_doc()
    assert_indexes()
    print("codex-cli-tui-continuation-priority-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
