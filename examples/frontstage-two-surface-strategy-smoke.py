#!/usr/bin/env python3
"""Smoke-test the frontstage public/ops surface strategy contract."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def compact(text: str) -> str:
    return " ".join(text.split())


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing strategy contract: {needle}")


def main() -> int:
    strategy = read("docs/product/surfaces/frontstage-two-surface-strategy.md")
    product_index = read("docs/product/README.md")
    surface_index = read("docs/product/surfaces/README.md")
    dashboard_readme = read("apps/presentation/dashboard/README.md")
    showcase_note = read("docs/showcases/frontend-surface.md")
    compact_strategy = compact(strategy)
    compact_dashboard_readme = compact(dashboard_readme)
    compact_showcase_note = compact(showcase_note)

    for needle in [
        "公开 showcase 与首页",
        "Personal Workspace",
        "不带 `mode=ops` 的 `/frontstage` 属于公开 showcase surface",
        "`/deprecated/frontstage/ops?statusUrl=...` 属于本地 ops 检查",
        "`apps/presentation/dashboard/src/views/deprecated/`",
        "`docs/showcases/showcase-catalog.json`",
        "`loopx serve-status --global-registry`",
        "公开 showcase surface 不得读取",
        "Ops surface 仍应默认只读",
        "公开视觉实验不得依赖实时状态",
        "showcase 模式忽略 `statusUrl`",
        "frontstage-private-status-trap.public.json",
        "`GH_FAKE_*` 标记",
        "`/frontstage/developer` 是只读 contributor cockpit",
        "阶段 1，公开 showcase 打磨",
        "阶段 2，本地 ops 数据层",
        "阶段 3，受控本地写辅助",
    ]:
        assert_contains(strategy, needle)

    for forbidden in [
        "公开 ops-mode URL",
        "远端实时 status 服务",
        "默认浏览器写权限",
        "没有公开 evidence 的营销声明",
    ]:
        assert_contains(compact_strategy, forbidden)

    assert_contains(product_index, "surfaces/README.md")
    assert_contains(surface_index, "frontstage-two-surface-strategy.md")

    for existing_contract in [
        "默认的 frontstage 路由是公开 showcase 模式",
        "忽略 `statusUrl`",
        "相对或回环 URL",
        "不要把 ops 模式 URL 当作公开链接",
        "两个组件面都没有浏览器写入权威",
        "frontstage-private-status-trap.public.json",
        "合成的 `GH_FAKE_*` 陷阱标记",
        "开发者扩展驾驶舱位于 `/frontstage/developer`",
    ]:
        assert_contains(compact_dashboard_readme, existing_contract)

    for public_source_contract in [
        "前端应读取 `showcase-catalog.json`",
        "不要渲染原始运行日志",
        "它是产品说明界面,不是本地操作者仪表盘",
    ]:
        assert_contains(compact_showcase_note, public_source_contract)

    route_row = "| 公开 showcase 与首页 | 通过 public-safe 案例、演示、动画与产品叙事解释 LoopX"
    ops_row = "| Personal Workspace | 帮助 operator 检查"
    assert_contains(compact_strategy, compact(route_row))
    assert_contains(compact_strategy, compact(ops_row))
    assert_contains(
        compact_strategy,
        "不得晋升到公开首页内容",
    )
    assert_contains(
        compact_strategy,
        "ops 模式只接受相对或 loopback feed",
    )
    assert_contains(
        compact_strategy,
        "不改变 Codex CLI/TUI loop 优先级",
    )

    print("frontstage-two-surface-strategy-smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
