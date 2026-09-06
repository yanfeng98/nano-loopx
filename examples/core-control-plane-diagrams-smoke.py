#!/usr/bin/env python3
"""Validate the public core-control-plane diagram docs stay linked and safe."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_DIR = ROOT / "docs" / "product" / "core-control-plane"

FILES = [
    DOC_DIR / "README.md",
    DOC_DIR / "interaction-catalog.md",
    DOC_DIR / "state-definitions.md",
    DOC_DIR / "state-machine.md",
]

FORBIDDEN_PUBLIC_STRINGS = [
    "bytedance",
    "la" + "rk" + "office",
    "EAAt" + "dvU1bokXbyxXdv7cDAAbnSb",
    "/Users/",
    "/private/tmp",
    "127.0.0.1",
    "localhost",
    "appSecret",
    "accessToken",
]


def read(path: Path) -> str:
    assert path.exists(), f"missing doc: {path}"
    return path.read_text(encoding="utf-8")


def main() -> None:
    docs = {path.name: read(path) for path in FILES}
    combined = "\n".join(docs.values())

    for text in FORBIDDEN_PUBLIC_STRINGS:
        assert text.lower() not in combined.lower(), f"private marker leaked: {text}"

    readme = docs["README.md"]
    for filename in ("interaction-catalog.md", "state-definitions.md", "state-machine.md"):
        assert f"]({filename})" in readme, f"README does not link {filename}"

    assert "interaction_pattern_lens_v0" in docs["interaction-catalog.md"]
    assert "核心模式图" in docs["interaction-catalog.md"]
    assert "State 定义" in docs["state-definitions.md"]
    assert "规范 State 体" in docs["state-definitions.md"]
    assert "派生的运行时 State" in docs["state-definitions.md"]
    assert "状态机" in docs["state-machine.md"]
    for section in (
        "Todo 生命周期机器",
        "配额/运行时机器",
        "Gate 决策范围机器",
        "Owner 路由/多 Agent 交接机器",
        "Evidence/上线/回滚机器",
        "调度器/心跳机器",
        "投影 Sink 机器",
        "Agent 接入/自动化启用机器",
        "Agent 愿景/重规划机器",
    ):
        assert section in docs["state-machine.md"], f"missing state machine: {section}"
    assert "```mermaid" in combined


if __name__ == "__main__":
    main()
