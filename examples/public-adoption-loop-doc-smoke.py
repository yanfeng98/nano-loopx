#!/usr/bin/env python3
"""Validate the docs-first public adoption loop contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "product" / "public-adoption-loop.md"
DOCS_INDEX = ROOT / "docs" / "README.md"
PRODUCT_INDEX = ROOT / "docs" / "product" / "README.md"

FORBIDDEN_PUBLIC_STRINGS = [
    "/Users/",
    "/private/tmp/",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "raw_thread",
    "session_history",
    "verifier_output_tail",
    "ACTIVE_GOAL_STATE.md:",
]


def read(path: Path) -> str:
    if not path.exists():
        raise AssertionError(f"missing expected file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def compact(text: str) -> str:
    return " ".join(text.split())


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label} missing {needle!r}")


def validate_boundary(path: Path) -> None:
    text = read(path)
    label = str(path.relative_to(ROOT))
    for forbidden in FORBIDDEN_PUBLIC_STRINGS:
        if forbidden in text:
            raise AssertionError(f"{label} contains forbidden string {forbidden!r}")


def main() -> None:
    for path in [DOC, DOCS_INDEX, PRODUCT_INDEX]:
        validate_boundary(path)

    doc = compact(read(DOC))
    for required in [
        "状态:文档优先的产品契约。",
        "## Issue 模板文案",
        "## 讨论模板文案",
        "## 分诊标签",
        "adoption:try-loopx",
        "workflow:issue-fix",
        "privacy:needs-redaction",
        "## 轻量指标",
        "workflow_type",
        "attention_cost",
        "would_repeat",
        "## 提升为 GitHub 模板",
        "owner 批准的边界决策",
    ]:
        assert_contains(doc, required, "public adoption loop doc")

    docs_index = read(DOCS_INDEX)
    product_index = read(PRODUCT_INDEX)
    assert_contains(docs_index, "product/README.md", "docs index")
    assert_contains(product_index, "public-adoption-loop.md", "product index")

    print("public-adoption-loop-doc-smoke ok")


if __name__ == "__main__":
    main()
