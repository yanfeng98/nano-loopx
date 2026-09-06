#!/usr/bin/env python3
"""Smoke-test the host integration surface protocol contract."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = REPO_ROOT / "docs" / "reference" / "protocols" / "host-integration-surface-v0.md"
PROTOCOL_INDEX = REPO_ROOT / "docs" / "reference" / "protocols" / "README.md"
DOCS_INDEX = REPO_ROOT / "docs" / "README.md"
ARCHITECTURE = REPO_ROOT / "docs" / "architecture.md"


def require(text: str, snippets: list[str], *, source: Path) -> None:
    compact = " ".join(text.split())
    missing = [
        snippet
        for snippet in snippets
        if snippet not in text and " ".join(snippet.split()) not in compact
    ]
    assert not missing, f"{source}: missing {missing}"


def main() -> int:
    protocol = PROTOCOL.read_text(encoding="utf-8")
    protocol_index = PROTOCOL_INDEX.read_text(encoding="utf-8")
    docs_index = DOCS_INDEX.read_text(encoding="utf-8")
    architecture = ARCHITECTURE.read_text(encoding="utf-8")

    require(
        protocol,
        [
            "Hook 激活",
            "MCP 适配器",
            "回环 server 适配器",
            "CLI 回退",
            "## 薄 Hook 激活",
            "## 生命周期读取",
            "## 受控写入",
            "## 紧凑状态投影",
            "## CLI 回退",
            "## 公开/私有边界",
            "薄 `/goal` 正文",
            "把可见 TUI 保持为主界面",
            "受控 todo/gate 写入",
            "可选显式 lease 写入",
            "它不证明任何适配器已安装",
            "也不授予超出既有 CLI 等价 LoopX 生命周期的写权限",
            "loopx --format json --registry",
            "loopx todo claim",
            "loopx todo complete",
            "loopx quota spend-slot",
            "task_graph_projection_v0",
            "cadence_hint_v0",
            "不增加图写权限",
            "task_lease_v0",
            "显式 `loopx task-lease acquire/renew/transfer/release/inspect`",
            "不被 `quota should-run` 强制",
            "获取硬 lease 不替换 todo claim",
            "浏览器/frontstage/server 写入默认保持非权威",
            "raw_transcripts_copied",
            "credentials_copied",
            "private_paths_copied",
            "remote_bind_default",
            "重复 todo claim",
            "daemon 下线情况失效关闭或回退到 CLI",
            "把可选投影标记为只读输入而非权限",
        ],
        source=PROTOCOL,
    )
    forbidden = [
        "替换用户可见 TUI/控制界面",
        "静默切换到隐藏 `codex exec`",
        "发明 host 特定权限规则",
        "默认远程绑定",
    ]
    require(protocol, forbidden, source=PROTOCOL)
    assert protocol.index("## 角色") < protocol.index("## 薄 Hook 激活")
    assert protocol.index("## 薄 Hook 激活") < protocol.index("## 生命周期读取")
    assert protocol.index("## 生命周期读取") < protocol.index("## 受控写入")
    assert protocol.index("## 受控写入") < protocol.index("## 紧凑状态投影")
    assert protocol.index("## 紧凑状态投影") < protocol.index("## CLI 回退")
    assert protocol.index("## CLI 回退") < protocol.index("## 公开/私有边界")

    require(
        protocol_index,
        ["Host 集成界面 v0", "host-integration-surface-v0.md"],
        source=PROTOCOL_INDEX,
    )
    require(
        docs_index,
        ["reference/README.md"],
        source=DOCS_INDEX,
    )
    require(
        architecture,
        [
            "host 集成面",
            "hook/MCP/server adapter",
            "host-integration-surface-v0",
            "可选派生投影保持只读",
            "CLI fallback 依然可用",
        ],
        source=ARCHITECTURE,
    )
    print("host-integration-surface-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
