#!/usr/bin/env python3
"""Validate the monorepo-owned LoopX Developer Book publication contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import tomllib


REPO_ROOT = Path(__file__).resolve().parents[1]
BOOK = REPO_ROOT / "docs" / "book"
CONTROL_PLANE_COURSE = REPO_ROOT / "docs" / "development" / "control-plane-course"
MKDOCS = REPO_ROOT / "mkdocs.yaml"
MKDOCS_ZH = BOOK / "mkdocs.zh.yaml"
BRAND_STYLES = REPO_ROOT / "docs" / "stylesheets" / "loopx.css"
HOMEPAGE = REPO_ROOT / "apps" / "presentation" / "site" / "src" / "App.tsx"

CHAPTERS = (
    "00-reading-guide",
    "01-from-session-to-loop",
    "02-session-goal-loopx",
    "state-substrate",
    "work-graph-and-authority",
    "03-one-turn",
    "04-runtime-boundaries",
    "05-connect-existing-project",
    "06-codex-app",
    "07-codex-cli",
    "source-protocol-map",
    "source-trace-protocol-chain",
    "source-change-control-plane-rule",
    "source-validation-to-pr",
    "08-extension-placement",
    "09-extension-scaffold",
    "10-extension-lifecycle",
    "11-engineering-boundaries",
    "12-control-plane-course",
    "appendix-reference",
)

COURSE_PAGES = (
    "00-concept-primer",
    "01-agent-loop-effectful-program",
    "02-goal-control-plane-architecture",
    "03-first-real-loop",
    "04-state-substrate",
    "05-work-graph-and-peers",
    "06-quota-decision-kernel",
    "07-host-scheduler-and-heartbeat",
    "08-evidence-refresh-and-self-repair",
    "09-engineering-a-control-plane-rule",
    "10-autonomous-agent-quality-gates",
    "11-extension-layer",
    "topic-long-horizon-convergence",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def compact(text: str) -> str:
    return " ".join(text.split())


def markdown_link_targets(markdown: str) -> list[str]:
    return re.findall(r"(?<!!)\[[^]]+\]\(([^)]+)\)", markdown)


def semantic_checkpoints(markdown: str) -> list[str]:
    return re.findall(
        r"<!-- community-casebook:([a-z0-9-]+(?::(?:start|end))?) -->",
        markdown,
    )


def marked_section(markdown: str, section_id: str) -> str:
    start = f"<!-- community-casebook:{section_id}:start -->"
    end = f"<!-- community-casebook:{section_id}:end -->"
    assert start in markdown, start
    assert end in markdown, end
    return markdown.split(start, 1)[1].split(end, 1)[0]


def assert_zh_concepts(
    zh_path: str,
    markers: tuple[str, ...],
) -> None:
    zh_text = compact(read(BOOK / zh_path))
    for marker in markers:
        assert marker in zh_text, f"{zh_path}: missing semantic marker {marker}"


def assert_community_casebook() -> None:
    protocol_map_zh = read(BOOK / "chapters" / "source-protocol-map.md")
    validation_zh = read(BOOK / "chapters" / "source-validation-to-pr.md")

    expected_protocol_checkpoints = [
        "signal-to-bounded-work:start",
        "question-before-fix",
        "user-idea-to-contract",
        "claim-before-code",
        "signal-to-bounded-work:end",
        "rfc-review-lab:start",
        "rfc-status",
        "rfc-community-proposal",
        "rfc-output",
        "rfc-review-lab:end",
    ]
    expected_validation_checkpoints = [
        "small-pr:start",
        "small-pr-problem",
        "small-pr-scope",
        "small-pr-lesson",
        "small-pr:end",
        "review-repair:start",
        "review-repair-problem",
        "review-repair-response",
        "review-repair-lesson",
        "review-repair:end",
    ]
    assert semantic_checkpoints(protocol_map_zh) == expected_protocol_checkpoints
    assert semantic_checkpoints(validation_zh) == expected_validation_checkpoints

    for zh_text, section_id, required_targets in (
        (
            protocol_map_zh,
            "signal-to-bounded-work",
            (
                "https://github.com/huangruiteng/loopx/discussions/3069",
                "https://github.com/huangruiteng/loopx/issues/2353",
                "https://github.com/huangruiteng/loopx/issues/3549",
                "https://github.com/huangruiteng/loopx/blob/main/docs/development/contributor-tasks.md",
            ),
        ),
        (
            protocol_map_zh,
            "rfc-review-lab",
            (
                "https://github.com/huangruiteng/loopx/blob/main/docs/architecture/rfcs/README.md",
                "https://github.com/huangruiteng/loopx/discussions/3157",
                "https://github.com/huangruiteng/loopx/blob/main/docs/community/open-strategy-reviews.md",
            ),
        ),
        (
            validation_zh,
            "small-pr",
            ("https://github.com/huangruiteng/loopx/pull/3540",),
        ),
        (
            validation_zh,
            "review-repair",
            ("https://github.com/huangruiteng/loopx/pull/3529",),
        ),
    ):
        zh_targets = markdown_link_targets(marked_section(zh_text, section_id))
        for target in required_targets:
            assert zh_targets.count(target) == 1, target


def validate_rendered_site(site_dir: Path) -> None:
    routes = {
        "index.html": ("LoopX Developer Book", "MkDocs Material"),
        "chapters/00-reading-guide/index.html": (
            "Dev Book 与 Control-Plane Course 如何配合",
            "/loopx/docs/development/control-plane-course/06-quota-decision-kernel/",
        ),
        "chapters/01-from-session-to-loop/index.html": (
            "从一次会话到长程任务",
        ),
        "chapters/05-connect-existing-project/index.html": (
            "快速阅读路线",
            "让 Agent 帮你接入",
        ),
    }
    for relative_path, markers in routes.items():
        target = site_dir / relative_path
        assert target.is_file(), f"missing rendered Developer Book route: {relative_path}"
        html = read(target)
        for marker in markers:
            assert marker in html, f"{relative_path}: missing rendered marker {marker}"
        assert ":::: tip" not in html, f"{relative_path}: unrendered VitePress container"
        assert 'data-md-color-scheme="slate"' in html, f"{relative_path}: not dark by default"
        if relative_path == "index.html":
            chapter_links = set(re.findall(r'href="[^"]*chapters/[^"#?]+/?(?:index\.html)?"', html))
            assert len(chapter_links) == len(CHAPTERS), (
                f"{relative_path}: expected {len(CHAPTERS)} Chinese chapter links, "
                f"found {len(chapter_links)}"
            )
        else:
            assert html.count("md-nav__item--active md-nav__item--section") == 1, (
                f"{relative_path}: expected exactly one expanded Chinese Part"
            )
        assert "English Chapters" not in html
        assert "Part I — Control-plane foundations" not in html

    main_docs_dir = site_dir.parent
    for page in COURSE_PAGES:
        target = main_docs_dir / "development" / "control-plane-course" / page / "index.html"
        assert target.is_file(), f"missing rendered Control-Plane Course route: {page}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", type=Path)
    args = parser.parse_args()

    assert not (BOOK / "labs").exists(), "Dev Book publication must not include Labs"
    assert not (REPO_ROOT / "mkdocs.book.zh.yaml").exists()
    assert not (REPO_ROOT / "mkdocs.book.en.yaml").exists()

    mkdocs = read(MKDOCS)
    assert "book/chapters/" not in mkdocs
    assert "book/en/chapters/" not in mkdocs
    assert "book/**" in mkdocs
    docs_home = read(REPO_ROOT / "docs" / "index.md")
    docs_readme = read(REPO_ROOT / "docs" / "README.md")
    assert "Developer Book](/loopx/docs/book/)" in docs_home
    assert "Developer Book](/loopx/docs/book/)" in docs_readme
    assert "/loopx/docs/book/en/" not in docs_readme

    zh_config = read(MKDOCS_ZH)
    assert "INHERIT: ../../mkdocs.yaml" in zh_config
    assert zh_config.index("scheme: slate") < zh_config.index("scheme: default")
    assert "navigation.sections" in zh_config
    assert "navigation.expand" not in zh_config
    assert "docs_dir: ." in zh_config
    assert "site_dir: ../../output/docs-book-zh" in zh_config
    assert "language: zh" in zh_config
    assert "en/**" in zh_config

    for chapter in CHAPTERS:
        assert f"chapters/{chapter}.md" in zh_config, chapter

    styles = read(BRAND_STYLES)
    for marker in (
        "#050914",
        "#091425",
        "#6eabff",
        "#96c8ff",
        "Iowan Old Style",
        "SFMono-Regular",
        ".md-sidebar",
        ".md-nav__item--section",
        ".md-typeset .grid.cards",
    ):
        assert marker in styles, marker

    homepage = read(HOMEPAGE)
    for path in (
        "docs/book/",
        "chapters/01-from-session-to-loop/",
        "chapters/05-connect-existing-project/",
        "chapters/source-protocol-map/",
    ):
        assert path in homepage

    book_index = read(BOOK / "index.md")
    assert "layout: home" not in book_index
    assert "theme: brand" not in book_index
    assert "VitePress" not in book_index
    assert "MkDocs Material" in book_index
    assert "/loopx/docs/book/" in book_index
    assert "/loopx/docs/book/en/" not in book_index

    project_version = tomllib.loads(read(REPO_ROOT / "pyproject.toml"))["project"]["version"]
    release_tag = f"v{project_version}"
    # Historical migration milestones must not move with the package version.
    migration_baseline_tag = "v0.5.4"
    release_markers = {
        "index.md": (
            f"LoopX 发布锚点：`{release_tag}`",
            "TypeScript Control-Plane Migration RFC",
        ),
        "chapters/00-reading-guide.md": (
            f"release `{release_tag}`",
            "transaction-payoff phase",
        ),
    }
    for relative_path, markers in release_markers.items():
        text = read(BOOK / relative_path)
        for marker in markers:
            assert marker in text, f"{relative_path}: missing release-baseline marker {marker}"

    for page in COURSE_PAGES:
        assert (CONTROL_PLANE_COURSE / f"{page}.md").is_file(), page

    assert_community_casebook()

    reading_guides = (
        read(BOOK / "chapters" / "00-reading-guide.md"),
    )
    for guide in reading_guides:
        assert "/loopx/docs/development/control-plane-course/" in guide
        for page in COURSE_PAGES:
            assert f"/loopx/docs/development/control-plane-course/{page}/" in guide, page

    assert_zh_concepts(
        "index.md",
        (
            f"LoopX 发布锚点：`{release_tag}`",
            "运行时前提：Python 3.11+ 与 Node.js 22.6+",
            "TypeScript owner",
            "这不是两套可独立演进的 控制面",
        ),
    )
    assert_zh_concepts(
        "chapters/00-reading-guide.md",
        (
            "语义镜像",
            "Python 3.11+",
            "Node.js 22.6+",
            "用户不需要手工维护 daemon",
            "TypeScript 已拥有",
            "Python CLI 仍负责",
            "不能再实现第二套独立 decision",
            "transaction-payoff phase",
            "Stage 3 的第一个 receipt-bound scheduler follow-up 切片",
            "Stage 4 distribution cleanup 仍是后续方向",
            "安装 Provider 不会改变默认本地 authority",
        ),
    )
    assert_zh_concepts(
        "chapters/02-session-goal-loopx.md",
        (
            "OpenCode 1/2",
            "Pi",
            "KunlunCode Goal Pro",
            "DeepSeek Harness",
            "Runtime Connector Catalog",
        ),
    )
    assert_zh_concepts(
        "chapters/03-one-turn.md",
        (
            f"`{migration_baseline_tag}` 仍提供",
            "显式 opt-in 集成",
            "Turn settlement",
            "Todo completion",
            "Host Todo settlement",
            "spend/void/monitor-poll commit",
            "本地 task-lease 完整生命周期",
            "Vision refresh",
            "receipt-bound scheduler follow-up",
            "Python 已被移除",
            "TypeScript Control-Plane Migration RFC",
        ),
    )
    assert_zh_concepts(
        "chapters/state-substrate.md",
        (
            f"`{migration_baseline_tag}` 的 shared-authority 工作",
            "provider-neutral TypeScript `AuthorityStore` contract",
            "不自动获得 runtime authority",
            "不应倒推成",
        ),
    )
    assert_zh_concepts(
        "chapters/05-connect-existing-project.md",
        (
            "Node.js 22.6",
            "Windows PowerShell 7",
            "loopx doctor --deep",
            "用户不需要手工维护 daemon",
            "`missing`、`unsupported` 或 `probe_failed`",
        ),
    )
    assert_zh_concepts(
        "chapters/source-protocol-map.md",
        (
            f"在 `{migration_baseline_tag}` 的迁移基线上",
            "bounded context 和实现语言是两个维度",
            "本地 task-lease lifecycle",
            "receipt-bound scheduler follow-up",
            "Python facade",
            "loopx capability list --format json",
            "仅有 目录或 README 不证明能力已经发布",
        ),
    )
    assert_zh_concepts(
        "chapters/11-engineering-boundaries.md",
        (
            "loopx doctor --deep",
            "loopx capability list --format json",
            "TypeScript migration RFC",
            "facade exit condition",
        ),
    )
    assert_zh_concepts(
        "chapters/appendix-reference.md",
        (
            "loopx todo list --goal-id <goal-id> --thin --format json",
            f"`{migration_baseline_tag}` 新增的 `todo list --thin`",
            "不改变默认 list 的选择、排序、quota 或 lifecycle 语义",
        ),
    )

    integrated_mechanisms = {
        "chapters/01-from-session-to-loop.md": (
            "PR Issue Fix",
            "Single-Agent Auto ML",
            "Multi-Agent Auto Research",
            "/loopx/docs/development/control-plane-course/02-goal-control-plane-architecture/",
        ),
        "chapters/03-one-turn.md": (
            "Decision Pipeline",
            "identity",
            "capability and workspace eligibility",
            "/loopx/docs/development/control-plane-course/06-quota-decision-kernel/",
        ),
        "chapters/04-runtime-boundaries.md": (
            "Material Evidence Delta",
            "Goal / Acceptance",
            "六条收敛不变量",
            "/loopx/docs/development/control-plane-course/topic-long-horizon-convergence/",
        ),
    }
    for relative_path, markers in integrated_mechanisms.items():
        chapter = read(BOOK / relative_path)
        for marker in markers:
            assert marker in chapter, f"{relative_path}: missing integrated mechanism {marker}"

    all_markdown = "\n".join(
        read(path) for path in BOOK.rglob("*.md")
    )
    for forbidden in (
        "cocolord.github.io/loopx-book",
        "cocolord/loopx-book-labs",
        "站点生成器：VitePress",
        "Site generator: VitePress",
        "当前站点使用 VitePress",
        "The site uses VitePress",
        ":::: tip",
        ":::: warning",
        ":::: info",
    ):
        assert forbidden not in all_markdown, forbidden

    if args.site_dir is not None:
        validate_rendered_site(args.site_dir)

    print("dev-book-publication-smoke: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
