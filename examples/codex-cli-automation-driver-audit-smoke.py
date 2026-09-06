#!/usr/bin/env python3
"""Smoke-test the public Codex CLI automation driver audit contract."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/runtimes/codex-cli/codex-cli-automation-driver.md"
RUNTIME_INDEX = REPO_ROOT / "docs/product/runtimes/codex-cli/README.md"


def main() -> int:
    doc = DOC.read_text()
    index = RUNTIME_INDEX.read_text()

    required_contracts = [
        "loopx_turn_v0",
        "loopx turn plan",
        "loopx turn run-once",
        "interactive-visible",
        "isolated-headless",
        "绝不能把 `interactive-visible` 回退切换",
        "独立校验",
        "持久写回",
        "quota",
        "scheduler 状态",
        "generic-cli",
        "类型化候选结果",
    ]
    for phrase in required_contracts:
        assert phrase in doc, phrase

    boundary_terms = [
        "原始 host 资料留在 LoopX 状态之外",
        "原始任务文本",
        "原始轨迹",
        "凭据",
        "本地 artifact 路径",
    ]
    for phrase in boundary_terms:
        assert phrase in doc, phrase

    unfinished_boundaries = [
        "`interactive-visible` 在集齐 attach、idle、interruption 与 takeover 证据之前还不能成为受支持的",
        "Trae 等非 Codex 对话式 CLI 还需要一个",
        "周期性外部调度必须组合",
        "benchmark 晋升仍需要",
    ]
    for phrase in unfinished_boundaries:
        assert phrase in doc, phrase

    assert "codex-cli-automation-driver.md" in index, "runtime index link"

    print("codex-cli-automation-driver-audit-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
