#!/usr/bin/env python3
"""Smoke-test the public session-runtime control-plane adapter docs."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOC = REPO_ROOT / "docs" / "integrations" / "session-runtime-control-plane-adapter.md"
DOCS_INDEX = REPO_ROOT / "docs" / "README.md"
INTEGRATIONS_INDEX = REPO_ROOT / "docs" / "integrations" / "README.md"
ARCHITECTURE = REPO_ROOT / "docs" / "architecture.md"

def require(text: str, snippets: list[str], *, source: Path) -> None:
    missing = [snippet for snippet in snippets if snippet not in text]
    assert not missing, f"{source}: missing {missing}"


def main() -> int:
    doc = DOC.read_text(encoding="utf-8")
    docs_index = DOCS_INDEX.read_text(encoding="utf-8")
    integrations_index = INTEGRATIONS_INDEX.read_text(encoding="utf-8")
    architecture = ARCHITECTURE.read_text(encoding="utf-8")

    require(
        doc,
        [
            "宿主会话日志是原始事实来源。",
            "LoopX 运行历史是紧凑控制投影。",
            "阶段 1:只读投影",
            "阶段 2:受控写回",
            "build_session_runtime_readonly_projection",
            "python3 examples/session_runtime/session-runtime-readonly-projection-smoke.py",
            "作为 scheduler 提示的配额决策,而不是计费",
            "这些指标是 goal 控制指标,不是模型质量分数。",
        ],
        source=DOC,
    )
    require(
        docs_index,
        ["integrations/README.md"],
        source=DOCS_INDEX,
    )
    require(
        integrations_index,
        ["Session runtime 控制面适配器"],
        source=INTEGRATIONS_INDEX,
    )
    require(
        architecture,
        [
            "会话运行时平台",
            "目标级控制投影",
            "session-runtime-control-plane-adapter.md",
        ],
        source=ARCHITECTURE,
    )

    print("session-runtime-control-plane-adapter-doc-smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
