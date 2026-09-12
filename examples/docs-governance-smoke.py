#!/usr/bin/env python3
"""Smoke-test the public docs information architecture."""

from __future__ import annotations

from pathlib import Path
import re
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"

ROOT_DOCS = {
    "README.md",
    "architecture.md",
    "index.md",
    "integration.md",
    "project-agent-todo-contract.md",
    "public-private-boundary.md",
    "quota-allocation.md",
    "state-interaction-model.md",
    "status-data-contract.md",
}

PRODUCT_ROOT_DOCS = {
    "README.md",
    "domain-capability-packs.md",
    "public-adoption-loop.md",
    "release-note-template.md",
    "release-readiness.md",
    "scenario-capability-gap-map.md",
    "vision.md",
}

LOCAL_LINK_PATTERNS = (
    re.compile(r"!?\[[^\]]*\]\((<[^>]+>|[^)\s]+)"),
    re.compile(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", re.MULTILINE),
    re.compile(r"\b(?:href|src)=[\"']([^\"']+)[\"']"),
)


MOVED_PATHS = {
    "docs/commit-readiness-manifest-20260603.md": (
        "docs/archive/release-readiness/commit-readiness-manifest-20260603.md"
    ),
    "docs/commit-readiness-manifest-20260606.md": (
        "docs/archive/release-readiness/commit-readiness-manifest-20260606.md"
    ),
    "docs/outcome-floor-safe-bypass-incident-20260606.md": (
        "docs/archive/incidents/outcome-floor-safe-bypass-incident-20260606.md"
    ),
    "docs/protocol-action-packet-codex-cli-wrapper-v0.md": (
        "docs/reference/protocols/protocol-action-packet-codex-cli-wrapper-v0.md"
    ),
    "docs/protocol-action-packet-decision-v0.md": (
        "docs/reference/protocols/protocol-action-packet-decision-v0.md"
    ),
    "docs/protocol-action-packet-router-comparison-v0.md": (
        "docs/reference/protocols/protocol-action-packet-router-comparison-v0.md"
    ),
    "docs/codex-cli-long-run-benchmark-design.md": (
        "deprecate/benchmark-legacy/docs/research/long-horizon-agent-benchmarks/"
        "codex-cli-long-run-benchmark-design.md"
    ),
    "docs/codex-cli-long-run-regression.md": (
        "deprecate/benchmark-legacy/docs/research/long-horizon-agent-benchmarks/"
        "codex-cli-long-run-regression.md"
    ),
    "docs/project-skill-delivery.md": (
        "loopx/capabilities/project_skill_delivery/README.md"
    ),
    "CONTRIBUTOR_TASKS.md": "docs/development/contributor-tasks.md",
    "DESIGN.md": "docs/development/design.md",
    "AUTHORS.md": "docs/project/authors.md",
    "TRADEMARKS.md": "docs/project/trademarks.md",
}

# docs/index.md .md targets that stay outside mkdocs nav on purpose.
# Prefer fixing mkdocs.yaml nav for public hosted entry points instead.
DOCS_INDEX_NAV_ALLOWLIST: dict[str, str] = {}

# docs/README.md catalog .md targets that stay outside mkdocs top nav on purpose.
DOCS_CATALOG_NAV_ALLOWLIST = {
    "architecture/README.md": "architecture tree index; RFCs linked from Reference nav",
    "archive/README.md": "excluded from hosted site via exclude_docs",
    "community/open-strategy-reviews.md": "community process; catalog-only entry",
    "development/contributor-tasks.md": "contributor board; not a hosted docs primary page",
    "project/authors.md": "project meta linked from README community section",
    "project/brand-guide.md": "project meta linked from README community section",
    "project/history.md": "project meta linked from README community section",
    "project/trademarks.md": "project meta linked from README community section",
    "reference/effect-interpreter-packet.md": "deep packet doc reachable from Reference",
    "research/README.md": "research evidence index; not a top-nav primary",
    "update-notes/README.md": "dated progress notes; catalog-only entry",
}

# Stable README advanced-docs entry links under docs/ that must stay reachable.
STABLE_README_DOCS_ENTRY_LINKS = (
    "operations/README.md",
    "quota-allocation.md",
    "status-data-contract.md",
    "concepts/README.md",
    "product/foundations/README.md",
    "product/vision.md",
    "integration.md",
    "integrations/README.md",
    "development/README.md",
    "reference/README.md",
    "development/control-plane-course/README.md",
    "development/testing-and-quality.md",
    "public-private-boundary.md",
    "showcases/README.md",
    "research/README.md",
    "update-notes/README.md",
    "project/technical-directions.md",
    "development/contributor-tasks.md",
    "project/authors.md",
    "project/history.md",
    "project/trademarks.md",
    "project/brand-guide.md",
)

MD_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\((<[^>]+>|[^)\s]+)")



def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def compact(text: str) -> str:
    return " ".join(text.split())


def subsection(text: str, heading: str) -> str:
    marker = f"### {heading}"
    assert marker in text, marker
    body = text.split(marker, 1)[1]
    return body.split("\n### ", 1)[0].split("\n## ", 1)[0]


def _normalize_md_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return target.split("#", 1)[0].split("?", 1)[0]


def iter_relative_md_targets(text: str) -> list[str]:
    targets: list[str] = []
    for match in MD_LINK_RE.finditer(text):
        target = _normalize_md_target(match.group(1))
        if not target or not target.endswith(".md"):
            continue
        if target.startswith(("http://", "https://", "mailto:", "/")):
            continue
        targets.append(target)
    return targets


def mkdocs_nav_paths(mkdocs_text: str) -> set[str]:
    assert "\nnav:\n" in mkdocs_text or mkdocs_text.startswith("nav:\n"), mkdocs_text
    nav_body = mkdocs_text.split("nav:", 1)[1]
    return set(re.findall(r"([A-Za-z0-9_./-]+\.md)", nav_body))


def generated_docs_site_sources() -> dict[str, Path]:
    repo_root = str(REPO_ROOT)
    docs_dir = str(DOCS)
    for path in (repo_root, docs_dir):
        if path not in sys.path:
            sys.path.insert(0, path)
    from capability_docs import documentation_maps

    site_to_source, _source_to_site = documentation_maps()
    return {site.as_posix(): source for site, source in site_to_source.items()}


def resolve_docs_relative_target(source_docs_rel: str, target: str) -> Path:
    source = DOCS / source_docs_rel
    return (source.parent / target).resolve()


def assert_path_in_nav_or_allowlisted(
    *,
    source_label: str,
    docs_relative: str,
    nav_paths: set[str],
    allowlist: dict[str, str],
) -> None:
    if docs_relative in nav_paths:
        return
    reason = allowlist.get(docs_relative)
    assert reason, (
        f"{source_label} links to {docs_relative}, which is missing from "
        "mkdocs.yaml nav and has no allowlist reason"
    )
    assert reason.strip(), f"{docs_relative}: empty allowlist reason"


def assert_hosted_docs_nav_parity() -> None:
    """Catch broken or orphaned hosted-docs entry points without touching README UI."""
    mkdocs_text = read("mkdocs.yaml")
    nav_paths = mkdocs_nav_paths(mkdocs_text)
    assert nav_paths, "mkdocs.yaml nav must list hosted pages"
    assert "book/**" in mkdocs_text, "Developer Book stays on its own MkDocs configs"

    generated_sources = generated_docs_site_sources()
    for nav_path in sorted(nav_paths):
        target = DOCS / nav_path
        if target.is_file():
            continue
        generated_source = generated_sources.get(nav_path)
        assert generated_source is not None and generated_source.is_file(), (
            f"orphaned mkdocs nav entry (missing file): {nav_path}"
        )

    docs_index = read("docs/index.md")
    for raw_target in iter_relative_md_targets(docs_index):
        resolved = resolve_docs_relative_target("index.md", raw_target)
        assert resolved.exists(), f"broken docs/index.md link: {raw_target}"
        docs_relative = str(resolved.relative_to(DOCS.resolve()))
        assert_path_in_nav_or_allowlisted(
            source_label="docs/index.md",
            docs_relative=docs_relative,
            nav_paths=nav_paths,
            allowlist=DOCS_INDEX_NAV_ALLOWLIST,
        )

    docs_catalog = read("docs/README.md")
    for raw_target in iter_relative_md_targets(docs_catalog):
        if raw_target.startswith("../"):
            resolved = (DOCS / raw_target).resolve()
            assert resolved.exists(), f"broken docs catalog link: {raw_target}"
            continue
        resolved = resolve_docs_relative_target("README.md", raw_target)
        assert resolved.exists(), f"broken docs catalog link: {raw_target}"
        try:
            docs_relative = str(resolved.relative_to(DOCS.resolve()))
        except ValueError:
            continue
        assert_path_in_nav_or_allowlisted(
            source_label="docs/README.md",
            docs_relative=docs_relative,
            nav_paths=nav_paths,
            allowlist=DOCS_CATALOG_NAV_ALLOWLIST,
        )

    for allowlist_path, reason in {
        **DOCS_INDEX_NAV_ALLOWLIST,
        **DOCS_CATALOG_NAV_ALLOWLIST,
    }.items():
        assert reason.strip(), f"{allowlist_path}: empty allowlist reason"
        assert allowlist_path not in nav_paths, (
            f"{allowlist_path} is in mkdocs nav; remove the stale allowlist entry"
        )
        assert (DOCS / allowlist_path).is_file(), (
            f"allowlisted docs path missing: {allowlist_path}"
        )

    for docs_relative in STABLE_README_DOCS_ENTRY_LINKS:
        assert (DOCS / docs_relative).is_file(), (
            f"stable README docs entry missing: {docs_relative}"
        )
        assert_path_in_nav_or_allowlisted(
            source_label="README stable docs entry",
            docs_relative=docs_relative,
            nav_paths=nav_paths,
            allowlist=DOCS_CATALOG_NAV_ALLOWLIST,
        )

    book_index = read("docs/book/index.md")
    assert "/loopx/docs/book/en/" not in book_index, (
        "docs/book/index.md must not cross-link the deleted English edition"
    )


def assert_local_doc_links_resolve() -> None:
    for source in DOCS.rglob("*"):
        if source.suffix.lower() not in {".md", ".html"}:
            continue
        text = source.read_text(encoding="utf-8")
        for pattern in LOCAL_LINK_PATTERNS:
            for match in pattern.finditer(text):
                raw_target = match.group(1)
                if raw_target.startswith("<") and raw_target.endswith(">"):
                    raw_target = raw_target[1:-1]
                if not raw_target or raw_target.startswith(
                    (
                        "#",
                        "/",
                        "http://",
                        "https://",
                        "mailto:",
                        "data:",
                        "javascript:",
                    )
                ):
                    continue
                relative_target = raw_target.split("#", 1)[0].split("?", 1)[0]
                if not relative_target:
                    continue
                resolved = (source.parent / relative_target).resolve()
                assert resolved.exists(), (
                    f"broken local docs link: {source.relative_to(REPO_ROOT)} "
                    f"-> {raw_target}"
                )


def assert_effect_interpreter_docs_are_canonical() -> None:
    public_lecture_url_fragments = (
        "6a01d501000000003700c5de",
        "6a02f388000000003502b2d6",
        "6a057524000000003701f6aa",
    )
    packet_doc = compact(read("docs/reference/effect-interpreter-packet.md"))
    for required in (
        "EffectRequest",
        "EffectInterpretation",
        "EffectObservation",
        "EffectNext",
        "EffectTurn",
        "Around 语义",
        "execution_mode",
        "interpret_turn_result_packet",
    ):
        assert required in packet_doc, required

    rfc = compact(read("docs/architecture/rfcs/agent-loop-effect-interpreter-v0.md"))
    for required in (
        "组合与 Around 语义",
        "Handler 是数据，不是 Callable",
        "通用 Effect-Program 抽象",
        "M6 通用 effect-program 抽象",
        "里程碑状态",
    ):
        assert required in rfc, required

    architecture = compact(read("docs/architecture.md"))
    assert "控制面即 Effect Interpreter" in architecture

    lecture = compact(
        read("docs/development/control-plane-course/01-agent-loop-effectful-program.md")
    )
    assert "Around 是数据，不是回调" in lecture
    assert "CLI 是更高密度的 effect" in lecture
    for fragment in public_lecture_url_fragments:
        assert fragment in rfc, fragment
        assert fragment in lecture, fragment


def assert_contributor_task_board_is_current() -> None:
    tasks = compact(read("docs/development/contributor-tasks.md"))
    for required in (
        "四个 canonical 全局 manager CLI 命令已交付",
        "`/loop-goal-summary` 仍是 host-only，不属于这个贡献者切片",
        "共用的 typed Effect Program 驱动 quota、Turn、task-lease 与 todo-completion settlement",
        "Scheduler 仍在 settlement 之外",
        "M7 parity fixture 外加只读 journal 检查/`interpret_turn_journal` lens 已交付",
        "在两个 adapter 共享执行属主之前不要抽取共用 executor",
    ):
        assert required in tasks, required
    for stale in (
        "Implement `/loopx-global-todos` or `/loopx-global-risks` next",
        "Implement `/loopx-global-risks` next",
        "Implement the remaining canonical `/loopx-global-risks` command",
        "global risks and goal summary stay host-only",
        "Add one negative fixture proving fail-closed legacy upgrade",
        "| GH-C82 |",
        "| GH-C59 |",
        "| GH-C61 |",
        "| GH-C83 |",
        "| GH-C84 |",
        "| GH-C92 |",
        "| GH-C93 |",
        "| GH-C49 |",
        "| GH-C60 |",
        "| GH-C62 |",
        "| GH-C64 |",
        "| GH-C71 |",
        "| GH-C74 |",
        "| GH-C75 |",
        "| GH-C76 |",
        "| GH-C80 |",
        "| GH-C85 |",
        "| GH-C95 |",
        "| GH-C97 |",
    ):
        assert stale not in tasks, stale


def assert_contributor_task_links_are_current() -> None:
    for path in (
        "docs/book/chapters/source-protocol-map.md",
        "docs/book/chapters/source-validation-to-pr.md",
    ):
        assert "docs/development/contributor-tasks.md" in read(path), path


def assert_technical_direction_governance_is_current() -> None:
    direction = read("docs/project/technical-directions.md")
    rfc_index = read("docs/architecture/rfcs/README.md")
    tasks = read("docs/development/contributor-tasks.md")

    for required in (
        "长程 Benchmark 与证据",
        "Operator Surface 与 IM Integration",
        "Shared Goal Authority 与跨 Host 协作",
        "架构与研究孵化器",
        "稳定基础：控制面可靠性",
        "frontend-control-plane-im-prototype-rfc",
        "@maxliux5",
        "NoKV 是位于 LoopX authority 之后",
        "#3243",
        "#3244",
        "#3245",
        "#3246",
    ):
        assert required in direction, required

    for required in (
        "## 控制面内核、状态与迁移",
        "## 规划、研究与自适应智能",
        "## Runtime、能力与协同集成",
        "## 操作者体验与可观测性",
        "## Benchmark 与可靠性工程",
        "当前技术方向",
    ):
        assert required in rfc_index, required
    assert "## Status matrix" not in rfc_index

    for required in (
        "长程 Benchmark 与证据",
        "Operator Surface 与 IM 集成",
        "共享 Goal 权威与跨 Host 协调",
        "架构与研究孵化器",
    ):
        assert required in tasks, required


def main() -> int:
    docs_index = read("docs/README.md")
    root_readme = read("README.md")
    auto_research_command_path = read("demo/auto_research/README.md")
    codex_cli_tui_loop = read("docs/product/runtimes/codex-cli/codex-cli-tui-loop.md")
    project_agent_contract = read("docs/project-agent-todo-contract.md")
    status_contract = read("docs/status-data-contract.md")
    compact_auto_research_command_path = compact(auto_research_command_path)
    compact_codex_cli_tui_loop = compact(codex_cli_tui_loop)
    compact_project_agent_contract = compact(project_agent_contract)
    compact_status_contract = compact(status_contract)

    for retired_root_policy in (
        "GOVERNANCE.md",
        "MAINTAINERS.md",
        "SECURITY.md",
        "SUPPORT.md",
        "COMMUNICATIONS.md",
    ):
        assert not (REPO_ROOT / retired_root_policy).exists(), retired_root_policy

    for required in [
        "## 选择你的路径",
        "## 核心参考",
        "## 按主题浏览",
        "## 文档策略",
        "architecture/README.md",
        "concepts/README.md",
        "operations/README.md",
        "integrations/README.md",
        "product/README.md",
        "development/README.md",
        "reference/README.md",
        "showcases/README.md",
        "development/testing-and-quality.md",
        "project/technical-directions.md",
    ]:
        assert required in docs_index, required

    navigation_contracts = {
        "使用与运维": [
            "docs/operations/README.md",
            "docs/quota-allocation.md",
            "docs/status-data-contract.md",
        ],
        "理解控制面": [
            "docs/concepts/README.md",
            "docs/product/foundations/README.md",
            "docs/product/vision.md",
        ],
        "集成与扩展": [
            "docs/integration.md",
            "docs/integrations/README.md",
        ],
        "构建与评审 LoopX": [
            "docs/development/README.md",
            "docs/reference/README.md",
            "docs/development/control-plane-course/README.md",
            "docs/development/testing-and-quality.md",
            "docs/public-private-boundary.md",
        ],
        "查看结果与证据": [
            "docs/showcases/README.md",
            "docs/research/README.md",
            "docs/update-notes/README.md",
        ],
        "项目与社区": [
            "docs/project/technical-directions.md",
            "CONTRIBUTING.md",
            "docs/development/contributor-tasks.md",
            "docs/project/authors.md",
            "docs/project/history.md",
            "docs/project/trademarks.md",
            "docs/project/brand-guide.md",
            "ADOPTERS.md",
        ],
    }
    for heading, required_links in navigation_contracts.items():
        section = subsection(root_readme, heading)
        for required in required_links:
            assert required in section, f"{heading}: {required}"

    assert "### Validate and Govern" not in root_readme
    assert "### 验证与治理" not in root_readme
    advanced_docs = root_readme.split("## 进阶文档", 1)[1].split("\n## ", 1)[0]
    for deep_link in [
        "benchmark/README.md",
        "deprecate/benchmark-legacy/README.md",
        "docs/product/foundations/project-level-reward-model.md",
        "loopx/capabilities/reward_memory/README.md",
    ]:
        assert deep_link not in advanced_docs

    for path in [
        "docs/archive/README.md",
        "docs/archive/incidents/README.md",
        "docs/archive/release-readiness/README.md",
        "docs/architecture/README.md",
        "docs/architecture/rfcs/README.md",
        "docs/architecture/rfcs/agent-im-openviking-collaboration-v0.md",
        "docs/concepts/README.md",
        "docs/operations/README.md",
        "docs/product/README.md",
        "docs/product/release-note-template.md",
        "docs/product/foundations/README.md",
        "docs/product/migrations/README.md",
        "docs/product/roadmaps/README.md",
        "docs/product/runtimes/README.md",
        "docs/product/runtimes/codex-cli/README.md",
        "docs/product/surfaces/README.md",
        "docs/product/use-cases/README.md",
        "docs/development/README.md",
        "docs/development/documentation-layout.md",
        "docs/development/testing-and-quality.md",
        "docs/guides/README.md",
        "demo/auto_research/README.md",
        "docs/guides/multi-agent-product-recipe.md",
        "docs/integrations/README.md",
        "docs/reference/README.md",
        "docs/reference/contracts/README.md",
        "docs/reference/protocols/README.md",
        "docs/research/README.md",
        "docs/showcases/README.md",
        "docs/product/runtimes/codex-cli/codex-cli-tui-loop.md",
        "docs/project/technical-directions.md",
        "docs/project/brand-guide.md",
    ]:
        assert (REPO_ROOT / path).is_file(), path

    assert (REPO_ROOT / "ADOPTERS.md").is_file()

    developer_index = read("docs/development/README.md")
    quality_guide = read("docs/development/testing-and-quality.md")
    for required in [
        "testing-and-quality.md",
        "Model behavior qualification v0",
        "Benchmark 研究",
    ]:
        assert required in developer_index, required
    for required in [
        "质量分层",
        "Agent 输出预算",
        "Issue #2191",
        "Doubao 模型行为门",
        "Benchmark 研究证据",
    ]:
        assert required in quality_guide, required

    root_markdown = {path.name for path in DOCS.glob("*.md")}
    assert root_markdown == ROOT_DOCS, sorted(root_markdown)

    product_root_markdown = {
        path.name for path in (DOCS / "product").glob("*.md")
    }
    assert product_root_markdown == PRODUCT_ROOT_DOCS, sorted(product_root_markdown)

    assert not (DOCS / "outreach").exists(), (
        "retired marketing and launch drafts must stay out of the active docs tree"
    )

    assert_local_doc_links_resolve()
    assert_hosted_docs_nav_parity()
    assert_effect_interpreter_docs_are_canonical()
    assert_contributor_task_board_is_current()
    assert_contributor_task_links_are_current()
    assert_technical_direction_governance_is_current()

    collaboration_rfc = read(
        "docs/architecture/rfcs/agent-im-openviking-collaboration-v0.md"
    )
    for forbidden in [
        "/Users/",
        ".local/research/",
        "source-synthesis.md",
        "minutes scopes",
        "目标群完整消息",
        "逐字稿",
    ]:
        assert forbidden not in collaboration_rfc, forbidden
    for required in [
        "直达 LoopX 的 runtime 路径是主路径",
        "OpenViking 接收 scoped 资源",
        "公开参考",
    ]:
        assert required in collaboration_rfc, required

    for old_path, new_path in MOVED_PATHS.items():
        assert not (REPO_ROOT / old_path).exists(), old_path
        assert (REPO_ROOT / new_path).is_file(), new_path

    combined_public_indexes = "\n".join(
        [
            read("README.md"),
            read("docs/development/contributor-tasks.md"),
            read("docs/README.md"),
            read("docs/archive/README.md"),
            read("docs/product/README.md"),
            read("docs/product/runtimes/codex-cli/README.md"),
            read("docs/reference/README.md"),
            read("docs/reference/protocols/README.md"),
            read("docs/research/README.md"),
            read("benchmark/README.md"),
            read("deprecate/benchmark-legacy/README.md"),
            read("docs/showcases/README.md"),
        ]
    )
    for old_path in MOVED_PATHS:
        assert old_path not in combined_public_indexes, old_path
    for new_path in MOVED_PATHS.values():
        basename = Path(new_path).name
        assert (
            new_path in combined_public_indexes
            or basename in combined_public_indexes
            or new_path.startswith("docs/archive/")
            or new_path.startswith("deprecate/benchmark-legacy/")
        ), new_path

    for required in [
        "不要在已验证的 `outcome_progress` 切片后再追加一个目标级 `surface_only` 同步",
        "--delivery-outcome outcome_progress",
    ]:
        assert required in compact_project_agent_contract, required

    for required in [
        "最佳首次运行体验是一条 TUI 设置消息",
        "Session-Attached 自动化",
        "Headless 禁止边界",
    ]:
        assert required in compact_codex_cli_tui_loop, required

    for required in [
        "后来的 `surface_only` 项目级同步会成为最新非 Agent lane run",
        "agent_lane_recommendation",
    ]:
        assert required in compact_status_contract, required

    for required in [
        "从干净工作区开始",
        "loopx-auto-research-demo",
        "auto-research demo-e2e",
        "auto-research demo-supervisor",
        "auto-research worker-loop",
        "research-curator",
        "hypothesis-proposer",
        "research-executor",
        "evaluator-promoter",
        "tmux attach -t loopx-auto-research",
        "tmux kill-session -t loopx-auto-research",
        "不是 leader agent",
    ]:
        assert required in compact_auto_research_command_path, required

    multi_agent_product_recipe = read("docs/guides/multi-agent-product-recipe.md")
    compact_multi_agent_product_recipe = compact(multi_agent_product_recipe)
    for required in [
        "多 Agent 产品配方",
        "产品预设",
        "多 Agent 内核",
        "角色列表",
        "agent 范围",
        "worker skill 片段",
        "交接/todo 提示",
        "单命令启动",
        "附加、停止、重试",
        "Auto-research 应保持为参考预设，而不是内核",
    ]:
        assert required in compact_multi_agent_product_recipe, required

    print("docs-governance-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
