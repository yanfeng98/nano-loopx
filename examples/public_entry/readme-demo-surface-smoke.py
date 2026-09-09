#!/usr/bin/env python3
"""Validate the public README and cross-runtime demo surface."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def compact(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    readme = read("README.md")
    demo = read("docs/product/use-cases/cross-runtime/cross-runtime-impl-review-demo.md")
    product_index = read("docs/product/README.md")
    cross_runtime_index = read("docs/product/use-cases/cross-runtime/README.md")
    getting_started = read("docs/guides/getting-started.md")
    compact_readme = compact(readme)
    compact_no_space_readme = "".join(readme.split())
    compact_demo = compact(demo)
    auto_research = readme.split("### Auto Research", 1)[1].split(
        "### 真实项目中的使用", 1
    )[0]

    for required in [
        '<div align="center">',
        "docs/assets/loopx-social-preview.png",
        "LoopX Loop Engineering 展示图",
        "面向长程 Agent 的开放、有状态、Provider-neutral 控制面。",
        "跨工具、跨 agent 的工作可审阅、可恢复、可接力",
        "持久保存目标、gate、todo、证据、quota 与交接状态",
        "## 为什么需要 LoopX",
        "目标 / issue / project",
        "LoopX state：objective + gate + todo + scope + evidence + quota",
        "## 试用 LoopX",
        "### 从你已经在用的 Agent 启动",
        "Codex CLI",
        "Claude Code",
        "Cursor、shell、自有 runner",
        "docs/product/use-cases/cross-runtime/cross-runtime-impl-review-demo.md",
        "## 进阶路径",
        "200+ 小时自然时长",
        "超过 200 小时的公开贡献轨迹",
        "经过脱敏的 owner-run showcase",
        "不是连续模型执行时长或无人值守的生产自治",
        "docs/assets/long-running-loop-openviking-trajectory.png",
        "docs/assets/long-running-loop-ml-experiment-trajectory.png",
        "### Preset 与 Auto Research",
        "### 审阅 Agent 工作",
        "### App 与 Projection",
        '<a id="快速开始"></a>',
        '<a id="看几个例子"></a>',
        "## 能力",
        "## 用户群与反馈",
        "`0.4.x` 已经是一套可用的长程 Agent 本地控制面",
        "docs/assets/loopx-lark-developer-group.png",
        "docs/assets/loopx-wechat-contact.png",
        "微信：<code>huangrt00</code>",
        "loopx configure-goal --goal-id <goal-id>",
        "loopx preset show daily-triage",
    ]:
        assert required in readme, required

    first_screen = readme.split("## 为什么需要 LoopX", 1)[0]
    assert "docs/assets/loopx-logo.png" not in first_screen

    for required in [
        "不是连续模型执行时长或无人值守的生产自治",
        "公司或雇主背书",
        "第三方独立复现",
    ]:
        assert required.replace(" ", "") in compact_no_space_readme, required

    for required in [
        "可复现的公开 KNN demo",
        "deterministic CPU evaluator",
        "docs/product/use-cases/auto-research/decentralized-auto-research-showcase.md",
    ]:
        assert required in auto_research, required
    assert "redacted" not in auto_research.lower()
    assert "脱敏" not in auto_research

    for required in [
        "`$loopx <复杂任务>`",
        "`loopx todo claim`",
        "`loopx review-packet`",
    ]:
        assert required in compact_readme, required

    for required in [
        "# 跨 Runtime 实现/评审演示",
        "Claude Code 拥有一个实现 todo",
        "Codex 拥有一个评审 todo",
        "LoopX 拥有 todo claims、gates、evidence、quota 与下一个 handoff",
        "loopx todo add --goal-id <goal> --role agent",
        "loopx demo impl-review --preset claude-codex --dry-run",
        "loopx --format json quota should-run --goal-id <goal> --agent-id claude-code-impl",
        "loopx review-packet --goal-id <goal>",
        "cross_runtime_impl_review_demo_packet_v0",
        "评审判定契约",
        "禁止的 evidence",
        "原始 Claude 或 Codex transcripts",
    ]:
        assert required in demo, required

    for required in [
        "verdict",
        "blockers",
        "suggestions",
        "verifier",
        "handoff",
        "文档加夹具验证",
    ]:
        assert required in compact_demo, required

    assert "use-cases/README.md" in product_index
    assert "cross-runtime-impl-review-demo.md" in cross_runtime_index
    assert "### 恢复历史索引碰撞" in getting_started
    assert "history rebuild-index-collisions" in getting_started
    assert "--review-plan-json reviewed-plan.json" in getting_started

    print("readme-demo-surface-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
