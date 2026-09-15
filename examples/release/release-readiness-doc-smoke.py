#!/usr/bin/env python3
"""Validate the public release-readiness doc wiring."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import tempfile


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "product" / "release-readiness.md"
TEMPLATE = ROOT / "docs" / "product" / "release-note-template.md"
README = ROOT / "README.md"
DOCS_INDEX = ROOT / "docs" / "README.md"
PRODUCT_INDEX = ROOT / "docs" / "product" / "README.md"
# The upstream install guide was removed from this fork; its still-live
# active-layer checklist moved into the editable dev loop doc.
ACTIVE_LAYER_DOC = ROOT / "docs" / "development" / "editable-dev-loop.md"

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

# Release notes are single-language (Chinese). The upstream bilingual contract was
# retired with the template rewrite: the primary sections and the former 中文摘要
# mirror were duplicates of each other once both were Chinese.
DECISION_HEADING = "## 发布决策"
DECISION_FIELDS = (
    "**谁需要升级:**",
    "**本版本解决了什么:**",
    "**破坏性变更:**",
    "**如何验证:**",
    "**贡献者:**",
)
USAGE_HEADING = "## 可选能力启用与使用"
USAGE_FIELDS = (
    "**启用:**",
    "**验证:**",
    "**停用 / 回退:**",
    "**权限边界:**",
    "**文档:**",
)
NO_CHANGES = "本版本未引入新的可选能力启用入口。"


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
    try:
        label = str(path.relative_to(ROOT))
    except ValueError:
        label = path.name
    for forbidden in FORBIDDEN_PUBLIC_STRINGS:
        if forbidden in text:
            raise AssertionError(f"{label} contains forbidden string {forbidden!r}")


def heading_level(line: str) -> int | None:
    match = re.match(r"^(#+)\s+", line)
    return len(match.group(1)) if match else None


def section(text: str, heading: str) -> str:
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError as exc:
        raise AssertionError(f"release notes missing heading {heading!r}") from exc

    level = heading_level(heading)
    assert level is not None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        candidate_level = heading_level(lines[index])
        if candidate_level is not None and candidate_level <= level:
            end = index
            break
    return "\n".join(lines[start + 1 : end])


def validate_surface_entry(
    *,
    usage_section: str,
    heading: str,
    required_fields: tuple[str, ...],
    language: str,
) -> None:
    entry = section(usage_section, heading)
    for field in required_fields:
        assert_contains(entry, field, f"{language} usage entry {heading!r}")
    if "```bash" not in entry:
        raise AssertionError(f"{language} usage entry {heading!r} has no runnable bash example")
    docs_field = re.escape(required_fields[-1])
    if not re.search(rf"{docs_field}[^\n]*https://[^)\s]+", entry):
        raise AssertionError(
            f"{language} usage entry {heading!r} has no canonical link in its docs field"
        )


def decision_field_value(decision: str, field: str, language: str) -> str:
    match = re.search(rf"^{re.escape(field)}\s*(.+)$", decision, re.MULTILINE)
    if not match:
        raise AssertionError(f"{language} release decision missing a value for {field!r}")
    value = match.group(1).strip()
    if len(value) < 8 or "<" in value or ">" in value:
        raise AssertionError(
            f"{language} release decision has an empty or placeholder value for {field!r}"
        )
    return value


def validate_release_decision(body: str) -> None:
    decision = section(body, DECISION_HEADING)
    values = {
        field: decision_field_value(decision, field, "release decision")
        for field in DECISION_FIELDS
    }
    breaking = values["**破坏性变更:**"]
    if not breaking.startswith(("无", "有", "否", "是")):
        raise AssertionError("breaking decision must start with 无/有/否/是")
    contributors = values["**贡献者:**"]
    if "@" not in contributors and not any(
        phrase in contributors for phrase in ("无社区贡献", "没有社区贡献")
    ):
        raise AssertionError(
            "contributors decision must name a handle or explicitly state "
            "that there was no community contribution"
        )
    if "```bash" not in decision:
        raise AssertionError("release decision has no runnable verification block")


def validate_release_notes(
    path: Path,
    *,
    surfaces: list[str],
    expect_no_optional_capability_changes: bool,
) -> None:
    validate_boundary(path)
    body = read(path)
    if body.count("```") % 2:
        raise AssertionError("release notes contain an unbalanced fenced code block")

    validate_release_decision(body)
    usage = section(body, USAGE_HEADING)

    if expect_no_optional_capability_changes:
        if surfaces:
            raise AssertionError(
                "--expect-no-optional-capability-changes cannot be combined with --surface"
            )
        assert_contains(usage, NO_CHANGES, "no-change declaration")
        return

    if not surfaces:
        raise AssertionError(
            "release-note validation requires at least one --surface or "
            "--expect-no-optional-capability-changes"
        )

    if len(set(surfaces)) != len(surfaces):
        raise AssertionError("release-note validation received duplicate --surface values")

    for surface in surfaces:
        validate_surface_entry(
            usage_section=usage,
            heading=f"### {surface}",
            required_fields=USAGE_FIELDS,
            language="release notes",
        )


def validate_release_notes_gate_self_test() -> None:
    def fixture(usage: str) -> str:
        return f"""# Example

{DECISION_HEADING}
**谁需要升级:** 受 scheduler 修复影响的 operator 应立即升级。
**本版本解决了什么:** 本版本避免到期 monitor 错过下一次唤醒。
**破坏性变更:** 无。已有持久状态保持兼容。
**如何验证:** 升级后运行下方 identity 与 behavior 检查。
**贡献者:** 由 maintainer @example 准备，本版本无社区贡献。
```bash
loopx --version
loopx doctor
```

{USAGE_HEADING}

{usage}

### 验证
"""
    valid = fixture(
        """### Example Surface
**启用:** 启用示例。
**验证:** 读回示例。
**停用 / 回退:** 停用示例。
**权限边界:** 不授予额外权限。
**文档:** https://example.com/docs。
```bash
loopx example --check
```"""
    )
    no_changes = fixture(NO_CHANGES)

    def assert_rejected(path: Path, body: str, message: str) -> None:
        path.write_text(body, encoding="utf-8")
        try:
            validate_release_notes(
                path,
                surfaces=["Example Surface"],
                expect_no_optional_capability_changes=False,
            )
        except AssertionError:
            return
        raise AssertionError(message)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        valid_path = tmp_path / "valid.md"
        no_changes_path = tmp_path / "no-changes.md"
        valid_path.write_text(valid, encoding="utf-8")
        no_changes_path.write_text(no_changes, encoding="utf-8")
        validate_release_notes(
            valid_path,
            surfaces=["Example Surface"],
            expect_no_optional_capability_changes=False,
        )
        validate_release_notes(
            no_changes_path,
            surfaces=[],
            expect_no_optional_capability_changes=True,
        )
        assert_rejected(
            tmp_path / "missing-rollback.md",
            valid.replace("**停用 / 回退:**", "", 1),
            "release-note gate accepted a missing rollback field",
        )
        assert_rejected(
            tmp_path / "ambiguous-breaking.md",
            valid.replace(
                "**破坏性变更:** 无。",
                "**破坏性变更:** 查看兼容性说明。",
                1,
            ),
            "release-note gate accepted an ambiguous breaking decision",
        )
        assert_rejected(
            tmp_path / "missing-contributors.md",
            valid.replace(
                "**贡献者:** 由 maintainer @example 准备，本版本无社区贡献。",
                "**贡献者:** 见提交历史。",
                1,
            ),
            "release-note gate accepted an unspecified contributor decision",
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release-notes",
        type=Path,
        help="Validate an exact final GitHub release body stored in this file.",
    )
    parser.add_argument(
        "--surface",
        action="append",
        default=[],
        help="New or materially changed optional capability/workflow/host surface. Repeatable.",
    )
    parser.add_argument(
        "--expect-no-optional-capability-changes",
        action="store_true",
        help="Require explicit bilingual declarations that this release adds no optional surface.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for path in [DOC, TEMPLATE, README, DOCS_INDEX, PRODUCT_INDEX, ACTIVE_LAYER_DOC]:
        validate_boundary(path)

    doc = compact(read(DOC))
    for required in [
        "状态:v0.x 维护者契约。",
        "## 受支持的安装与更新路径",
        "loopx update check",
        "loopx update plan",
        "loopx update apply",
        "包获取、host 材料交付、核心运行时激活",
        "就地开发闭环的活动层检查清单",
        "## 命名版本契约",
        "版本来源是 `loopx.__version__`，由 `pyproject.toml` 镜像",
        "examples/release/release-version-contract-smoke.py",
        "## 兼容 gate",
        "examples/release/release-readiness-doc-smoke.py",
        "loopx canary release-qualification",
        "exact_release_commit_qualification_manifest_v0",
        "相同 Git 提交、Git tree id、包版本与版本 tag",
        "## Canary 模型",
        "目录知情的就绪度切片",
        "近 E2E",
        "不要仅为描述校验 bundle 而添加新 IP",
        "python3 -m loopx.cli canary smoke-suite --profile public-smoke-watch --jobs 4 --timeout-seconds 60",
        "python3 examples/run-smokes.py --suite full-public --jobs 4 --timeout-seconds 60",
        "## 可安全依赖的内容",
        "loopx doctor",
        "quota should-run",
        "/loopx-global-summary",
        "benchmark runner 行为、评分、上传",
        "## 发布说明清单",
        "[发布说明模板](release-note-template.md)",
        "`## 发布决策`",
        "`**谁需要升级:**`",
        "`**本版本解决了什么:**`",
        "`**破坏性变更:**`",
        "`**如何验证:**`",
        "`**贡献者:**`",
        "显眼的 `## 社区贡献者` 部分",
        "在产品分组之后",
        "从 tag 到 tag 的 Git 范围与合并 PR 元数据",
        "没有合格贡献者时省略本节。",
        "没有符合条件的贡献时省略本节",
        "在产品分组之后、兼容性或校验材料之前添加 `## 社区贡献者`",
        "每位符合条件的贡献者与其具体贡献范围",
        "可选能力激活",
        "若不存在持久开关",
        "最终 GitHub 发布正文",
        "--release-notes <final-release-body.md>",
        "--expect-no-optional-capability-changes",
        "公开/私有扫描",
        "发布必须保留这些分组边界",
        "**启用:**",
        "**验证:**",
        "**停用 / 回退:**",
        "**权限边界:**",
        "**文档:**",
    ]:
        assert_contains(doc, required, "release-readiness doc")

    active_layer_doc = compact(read(ACTIVE_LAYER_DOC))
    for required in [
        "## 验证各激活层",
        "{#verify-the-active-layers}",
        "loopx update check",
        "skill_delivery.status",
        "loopx doctor --deep",
        "loopx extension doctor --all-enabled --execute --format json",
        "不要在同一个环境里混用 editable、pip、pipx 与归档路径",
    ]:
        assert_contains(active_layer_doc, required, "active-layer doc")

    root_readme = read(README)
    docs_index = read(DOCS_INDEX)
    product_index = read(PRODUCT_INDEX)
    assert_contains(root_readme, "docs/product/release-readiness.md", "root README")
    assert_contains(docs_index, "product/release-readiness.md", "docs index")
    assert_contains(product_index, "release-readiness.md", "product index")
    assert_contains(product_index, "release-note-template.md", "product index")

    template = read(TEMPLATE)
    for required in [
        "## 一目了然",
        DECISION_HEADING,
        *DECISION_FIELDS,
        "## 状态内核与控制面",
        "## 能力与工作流",
        "## 质量与测试",
        "## 基准与集成",
        "## 文档与兼容性",
        "## 社区贡献者",
        USAGE_HEADING,
        *USAGE_FIELDS,
        NO_CHANGES,
        "## 安装 / 更新",
        "## 发布验证",
    ]:
        assert_contains(template, required, "release-note template")

    validate_release_notes_gate_self_test()
    if args.release_notes is not None:
        validate_release_notes(
            args.release_notes,
            surfaces=args.surface,
            expect_no_optional_capability_changes=(
                args.expect_no_optional_capability_changes
            ),
        )
    elif args.surface or args.expect_no_optional_capability_changes:
        raise AssertionError(
            "--surface and --expect-no-optional-capability-changes require --release-notes"
        )

    print("release-readiness-doc-smoke ok")


if __name__ == "__main__":
    main()
