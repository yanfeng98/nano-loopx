#!/usr/bin/env python3
"""Smoke-test the Codex App control-plane hook/cache experiment contract."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/product/runtimes/codex-app/codex-app-control-plane-hook-cache.md"
RUNTIME_INDEX = REPO_ROOT / "docs/product/runtimes/codex-app/README.md"


def main() -> int:
    doc = DOC.read_text(encoding="utf-8")
    index = RUNTIME_INDEX.read_text(encoding="utf-8")
    normalized_doc = " ".join(doc.split())

    required_phrases = [
        "状态：实验性设计说明，默认关闭。",
        "enabled_by_default: false",
        "mode: advisory_hint",
        "host-runtime 提示",
        "LoopX 保持权威",
        "缺失、过期或不匹配的提示回退到 CLI",
        "quiet_wait_cache_lab",
        "guard_projection_lab",
        "default_candidate",
        "Evidence Gates",
        "零误判运行、零误判 quiet-skip 决策",
        "public/private 扫描",
        "回退 CLI 路径",
        "把全部交付、写回、发布与 quota spend 决策留在既有 CLI guard 上",
    ]
    for phrase in required_phrases:
        assert phrase in doc or phrase in normalized_doc, phrase

    forbidden_default_claims = [
        "enabled_by_default: true",
        "default enabled",
        "enable automatically",
        "replace quota should-run",
    ]
    lowered = doc.lower()
    for phrase in forbidden_default_claims:
        assert phrase not in lowered, phrase

    assert "codex-app-control-plane-hook-cache.md" in index, "runtime index link"

    print("codex-app-control-plane-hook-cache-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
