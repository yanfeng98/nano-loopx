# 028 · 裁剪 repository-hygiene smoke 的「公开项目门面」断言

- **日期**: 2026-09-13
- **分支**: `260906-dev`
- **背景**: `examples/repository-hygiene-smoke.py` 是上游用于**公开 OSS 仓库形态**的薄守卫，6 项检查里 4 项是"这个 checkout 像不像一个规范的公开项目"。本 fork 在 2026-09-07 主动剥掉了这套门面 —— `c88509106` 删除 `LICENSE`（Apache-2.0）+ `LICENSE-MIT`，`6a9bebc75` 删除整个 `.github/`（CI workflows、`CODEOWNERS`、`GOVERNANCE.md`、dependabot、PR 模板、issue 模板）—— 因此这 4 项断言必然失败。**后果不只是"红一个 smoke"**：它在第一个断言处即抛错，导致其后的 **public/private boundary 扫描在本 fork 从未真正执行过**。
- **用户决策（2 项）**: ① **只裁剪守卫，不恢复许可证**；② **接受与上游守卫分叉**。

## 实测现状（处理前，逐项复刻该 smoke 的判定）

| # | 断言 | 状态 |
| --- | --- | --- |
| ① | `LICENSE` 被跟踪 | ❌（`c88509106` 已删） |
| ② | `SECURITY.md` 或 `.github/SECURITY.md` | ❌ |
| ③ | `.github/PULL_REQUEST_TEMPLATE.md` | ❌ |
| ④ | `.github/ISSUE_TEMPLATE/` 下至少一个模板 | ❌ |
| ⑤ | public/private boundary 扫描干净 | ✅（直调 `scan_public_boundary`：`ok=True`、`hits=0`、`scanned_files=2567`） |
| ⑥⑦ | release timeline 文档存在且覆盖所有 `v≥0.1.3` tag | ✅（本 fork 无 tag） |

## 变更清单

### `examples/repository-hygiene-smoke.py`

- `REQUIRED_TRACKED_FILES`：`("LICENSE", "CONTRIBUTING.md")` → `("CONTRIBUTING.md",)`；
- 删除 `SECURITY_FILES`、`ISSUE_TEMPLATE_DIR`、`PR_TEMPLATE` 三个常量及其三段断言（`validate_required_tracked_files` 的一句 docstring 之外的其余检查按 fork 现实保留）；
- 模块 docstring：`LoopX's own public checkout` → `this fork's checkout`；
- 新增注释说明**为什么**裁掉而不是拿占位文件满足它，并写明两个上游提交号（`c88509106`、`6a9bebc75`），供未来 merge 冲突时判断。

### `docs/development/testing-and-quality.md`

「仓库卫生 smoke 是 LoopX 自身公共 checkout 的薄基线」→「是本 checkout 的薄基线」，并补一句说明本 fork 已移除公开门面、对应断言随之裁掉。（该 smoke **不在任何 canary profile 中**，此处文档是它唯一的对外描述面。）

## 有意不改

- `loopx/canary/runner.py:34` 的 `GIT_REQUIRED_SCRIPTS` 条目：其理由 "requires git ls-files and git tag" 在裁剪后**依然准确**（`CONTRIBUTING.md` 走 `git ls-files`，release timeline 走 `git tag`），无误改。
- `docs/product/release-readiness.md:215`：只在发布清单里列这条命令，不描述断言内容。
- `docs/development/contributor-tasks.md:94`：上游历史记录（含 PR 号 #3249），逐字保留。

## 未处理的风险（用户明确选择）

**许可证仍未恢复。** 仓库今天在别处仍声明 Apache-2.0：`docs/project/brand-guide.md:135`（"Apache 和历史 MIT license 按各自条款覆盖代码和文档"）、`apps/desktop/loopx-control-plane/package.json:5`、`apps/desktop/loopx-control-plane/src-tauri/Cargo.toml:7`。上游为 Apache-2.0 + MIT 双许可，Apache-2.0 §4 要求衍生分发保留许可证文本与 NOTICE；本 fork 发布在 `github.com/yanfeng98/nano-loopx`。本次按用户决定**不动**，记录在案。

## 验证

- **smoke 转绿**：`repository-hygiene-smoke ok`（exit 0）—— 其 public/private boundary 扫描在本 fork **首次真正执行**并通过。
- **守卫仍有牙齿**（函数级实测，不改仓库）：`validate_required_tracked_files({"CONTRIBUTING.md"})` → 通过；`validate_required_tracked_files(set())` → 正确抛 `missing tracked repository-hygiene files: ['CONTRIBUTING.md']`。
- **无残留引用**：`SECURITY_FILES` / `ISSUE_TEMPLATE_DIR` / `PR_TEMPLATE` 三词在该文件内 0 命中。
- **`ruff check`**：通过。
- **影响面**：该 smoke 被 `loopx/canary/runner.py` 发现但**不属于任何 canary profile**（实测 6 个 profile 的结果中均无它），故本次改动不改变 canary 套件结果；`tests/` 内无任何测试引用它（全库 grep 确认）；因为它在 `examples/` 而不在 `pytest tests/` 的收集面内，全量 pytest 无法反映它 —— 本条的验证以直接运行为准。

## 与上游分叉

该文件现为 fork 版本（连同 `examples/docs-governance-smoke.py`，见 027）。未来 merge 上游若恢复这 4 项断言，处置：**保留 fork 版本 + 保留理由注释**。

## 环境备注

无新增环境性失败；本轮未触碰 `tests/`、`loopx/` 交付代码与任何配置。
