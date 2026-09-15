#!/usr/bin/env python3
"""Smoke-test the protocol action packet decision note."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DECISION_DOC = REPO_ROOT / "docs" / "reference" / "protocols" / "protocol-action-packet-decision-v0.md"
WRAPPER_SMOKE = REPO_ROOT / "examples" / "protocol" / "protocol-action-packet-codex-cli-wrapper-smoke.py"


def main() -> None:
    text = DECISION_DOC.read_text(encoding="utf-8")
    wrapper_smoke = WRAPPER_SMOKE.read_text(encoding="utf-8")

    required = [
        "保留 `protocol_action_packet_v0` 作为 `quota should-run` 的热路径协议简化契约",
        "`llm=no_api`",
        "只把 Codex CLI 包装器作为显式的冷路径 sidecar 实验",
        "将直接 LLM API 接入推迟",
        "它们不应调用 Codex CLI",
        "默认 smoke 路径保持假/无模型",
        "它不得持久化原始 stderr",
        "Terminal-Bench/Harbor 执行环境",
        "环境就绪 lane",
    ]
    for needle in required:
        assert needle in text, needle

    assert "--real-codex-cli" in wrapper_smoke
    assert "real_codex_cli_probe" in wrapper_smoke
    assert "fake_codex_cli_contract" in wrapper_smoke
    assert text.index("## 决策") < text.index("## 证据") < text.index("## 运行规则")
    assert text.index("## 运行规则") < text.index("## 后续工作")
    print("protocol-action-packet-decision-smoke ok")


if __name__ == "__main__":
    main()
