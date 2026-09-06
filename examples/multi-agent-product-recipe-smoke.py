#!/usr/bin/env python3
"""Smoke-check the reusable multi-agent product recipe documentation."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "docs" / "guides" / "multi-agent-product-recipe.md"
DOCS_INDEX = ROOT / "docs" / "README.md"
GUIDES_INDEX = ROOT / "docs" / "guides" / "README.md"
AUTO_RESEARCH_GUIDE = ROOT / "demo" / "auto_research" / "README.md"


PRIVATE_MARKERS = [
    "byte" + "dance",
    "lark" + "office",
    "fei" + "shu.cn",
    "/" + "Users" + "/",
    "/" + "private" + "/",
    "/" + "tmp" + "/",
    "api" + "_key",
    "pass" + "word",
    "sec" + "ret",
]


def read(path: Path) -> str:
    assert path.is_file(), f"missing {path}"
    return path.read_text(encoding="utf-8")


def require(text: str, snippets: list[str], *, source: Path) -> None:
    compact = " ".join(text.split())
    missing = [
        snippet for snippet in snippets if snippet not in text and " ".join(snippet.split()) not in compact
    ]
    assert not missing, f"{source}: missing {missing}"


def assert_public_safe(text: str, label: str) -> None:
    lower = text.lower()
    leaked = [marker for marker in PRIVATE_MARKERS if marker.lower() in lower]
    assert not leaked, f"{label} leaks private markers: {leaked}"


def main() -> int:
    recipe = read(RECIPE)
    docs_index = read(DOCS_INDEX)
    guides_index = read(GUIDES_INDEX)
    auto_research_guide = read(AUTO_RESEARCH_GUIDE)

    assert_public_safe(recipe, "multi-agent product recipe")
    require(
        recipe,
        [
            "# 多 Agent 产品配方",
            "用户层",
            "产品预设",
            "多 Agent 内核",
            "仅把用户命令改短是不够的",
            "用户层与产品预设 都必须保持薄",
            "角色列表",
            "agent 范围",
            "worker 本地 skill 片段",
            "$loopx-project",
            "$loopx-doc-registry",
            "不应复制那些通用项目/doc-registry",
            "交接/todo 提示",
            "单命令启动",
            "附加、停止、重试",
            "loopx multi-agent launch",
            'loopx auto-research start "<open question>" --execute',
            "真实的交互式 Codex CLI TUI pane",
            "第一个动作是 pane 本地 A2A tick",
            "机器 JSON 写入公开 artifacts",
            "todos 与证据是唯一交接权威",
            "把现有预设 晋升为参考配方",
            "固定 prompt 唤醒、pane 本地 A2A tick、 runner 生命周期、紧凑状态与公开 artifact 路由仍留在通用多 Agent 内核中",
            "长出私有 launcher 或隐藏工作流驱动器",
            "演示同一单命令可见路径",
            "Auto-research 应保持为参考预设，而不是内核",
            "如果第二个产品需要同样的代码，就把那部分代码移进内核",
        ],
        source=RECIPE,
    )
    require(
        docs_index,
        ["guides/"],
        source=DOCS_INDEX,
    )
    require(
        guides_index,
        ["多 Agent 产品配方", "multi-agent-product-recipe.md"],
        source=GUIDES_INDEX,
    )
    require(
        auto_research_guide,
        [
            "multi-agent 产品配方",
            "multi-agent-product-recipe.md",
            "复制该模式而不复制 auto-research 代码",
            "经过验证的可见证明晋升到这条现有命令路径",
            "运营方运行一条命令",
            "通用多 agent 内核提供 runner、唤醒、面板本地 tick、状态",
            "固定 prompt 唤醒让每个面板运行其本地 A2A tick",
            "具体的 KNN 可见命令",
            "`--preset knn-demo` 是公开信号,表示 LoopX 应物化一个小型生成的 KNN benchmark 工作区",
            "可见面板获得仅一个可编辑文件 `solution.py`",
            "在可见角色撰写真实 public-safe 证据之前,不存在 dev/holdout uplift",
            "它不是\"可见 Codex 面板撰写了研究结果\"的声明。",
        ],
        source=AUTO_RESEARCH_GUIDE,
    )

    forbidden = [
        "auto-research owns the runner",
        "preset owns tmux",
        "hidden workflow engine",
        "auto-research private launcher",
        "raw JSON should be visible first",
    ]
    for phrase in forbidden:
        assert phrase not in recipe, f"forbidden phrase present: {phrase}"

    print("multi-agent-product-recipe-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
