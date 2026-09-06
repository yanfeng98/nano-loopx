#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
GUIDE = (ROOT / "docs" / "reference" / "extensions.md").read_text(encoding="utf-8")

for anchor in (
    "## 能力与扩展放置",
    "loopx/capabilities/<capability>/",
    "loopx/extensions/",
    "packages/<package-id>/",
    "capability id、provider id",
    "公共能力按调用方结果命名",
):
    assert anchor in AGENTS, anchor

for anchor in (
    "## 面向 Agent 的放置决策",
    "## 仓库布局",
    "packages/<package-id>/",
    "刻意没有",
    "正在添加或改变的是什么用户结果与调用方可见合同?",
    "实现是否需要独立的安装",
    "扩展拥有的命令与 packet 合同可以保持为独立扩展 runtime",
    "`value-connectors` 是现有的兼容性 CLI",
    "独立扩展(如 `loopx-finance-value-discovery`)",
    "loopx extension run <extension-id>",
    "直接 provider 二进制是实现与调试 surface",
    "capability_id: <existing-or-new-contract>",
    "独立扩展使用 `capability_id: none`",
    "reason: <why the nearest existing owner is or is not sufficient>",
):
    assert anchor in GUIDE, anchor

print("capability-extension-placement-doc-smoke: ok")
