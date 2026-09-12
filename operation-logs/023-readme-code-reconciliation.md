# 023 · README 与代码一致性修复（死链、命令、host 表、许可证移除）

- **日期**: 2026-09-12
- **分支**: `260906-dev`
- **背景**: 用户发现 README 与当前代码存在多处不一致。排查后确认根因不是随机漂移，而是 fork 瘦身过程中**只清理了 README 的 host 表格，没有回头清理「删除文件」与「删除功能模块」这两类变更**所留下的引用。另有两个治理守卫因此损坏，其中 `examples/docs-governance-smoke.py` 已完全无法运行。因 `mkdocs.yaml:9` 把 `/README.md` 设为文档站首页，README 的问题会直接进入发布站点。

## 决策（用户确认）

1. **许可证**: 彻底移除（文档与元数据层；产品代码层记账，见「已知遗留」）。
2. **范围**: README + 两个 README 守卫 + 全部 docs 死链。
3. **上游链接**: 保留，只修死链（不把 GitHub 链接改指 fork）。
4. **host 表**: 补齐遗漏 host。
5. **Apache-2.0 声明**: 一并清掉，`packages/dsh-loopx-plugin/` 除外。

## 变更清单（30 文件，+69/−232，含 1 个整文件删除；本日志与索引另计）

### 1. README 内容修正

1. 版本号 `0.4.x` → `1.0.x`（L599）。真实版本为 `1.0.0`（`pyproject.toml:7`、`loopx/__init__.py:5`、`man/loopx.1:1`），与同文件 L34「LoopX 1.0」自相矛盾。**根因**: `examples/public_entry/readme-demo-surface-smoke.py:67` 把 `0.4.x` 列为必需断言，把错误字符串冻结了。
2. host 表补齐至与 `START_GOAL_HOST_SURFACES`（`loopx/bootstrap_command_pack.py:59`，10 项）一致：新增 **OpenCode 2** 与 **Ark Managed Agent** 两行；把原先合并的一行 DeepSeek Harness 拆为 `deepseek-harness`（headless turn）与 `deepseek-harness-native`（同会话 plugin）两个 surface，各自给出 `--host-surface` 取值。`shell、自有 runner` 行文本保持原样（smoke 断言该字符串）。
3. `direct-model` → `anthropic-api` / `openai-api`（L40）。`direct-model` 全库只出现于 README；真实内置 agent id 为 `anthropic-api`（Claude API）与 `openai-api`（OpenAI API），见 `loopx/chat_runtime.py:260,272,334-338`、`loopx/chat_providers.py:395`。
4. **7 条复制粘贴陷阱修复**（文档命令实际会 argparse 报错）：
   - 补全必需的 `--goal-id`：`todo claim`、`todo update`、`refresh-state`、`review-packet`、`heartbeat-prompt`；`reward-memory experiment-status` 另需 `--agent-id`。
   - 6 个命令组改为 `--help` 形式并标注「命令组」：`lark-kanban`、`issue-fix`、`content-ops`、`value-connectors`、`ml-experiment`、`benchmark`（均为 `add_subparsers(required=True)`，裸调用直接报错）。
   - `worker-bridge` → `worker-bridge contract`（无子命令时 handler exit 1）。
   - `--with-goal-bridge` 补出所属命令 `loopx slash-commands --install --surface opencode`（该 flag 仅在 opencode surface 生效）。
   - `opencode2-goal-worker` 补全必需的 `--directory`。
5. 删除 **Star 趋势** 整节：生成它的 `.github/workflows/` 在 fork 中已删除，`由仓库授权的 workflow 每 6 小时生成` 的机制声明不可能成立。
6. 删除 **License** 整节与 `.github/GOVERNANCE.md`、`.github/SUPPORT.md` 三处引用。

### 2. 治理守卫修复

7. `examples/public_entry/readme-demo-surface-smoke.py`: 版本断言 `0.4.x` → `1.0.x`；把冻结的简写命令（`` `loopx todo claim` ``、`` `loopx review-packet` ``）替换为修正后的真实命令。
8. `examples/docs-governance-smoke.py`（**修复前完全无法运行**）: 删除 `main()` 中 `.github/GOVERNANCE.md`/`.github/SUPPORT.md` 读取及依赖它们的断言循环；`assert_contributor_task_links_are_current()` 只保留两个仍存在的 `docs/book/chapters/*.md` 断言；`assert_technical_direction_governance_is_current()` 删除三个 `.github/` 读取与其断言；`DOCS_CATALOG_NAV_ALLOWLIST` 去 `project/licensing.md`（该函数会断言白名单路径必须存在）；`navigation_contracts["项目与社区"]` 去 `.github/GOVERNANCE.md`。

### 3. docs 死链清零（19 处，扫描确认）

9. **退役 host / 已删基础设施引用整行删除**：`heartbeat-automation-prompt.md` × 8（`docs/README.md`、`docs/guides/getting-started.md` × 2、`docs/integrations/runtime-connector-catalog.md`、`docs/operations/README.md`）、`codex-multi-app-best-practices.md` × 1（`docs/guides/README.md`）、`.github/workflows/python-tests.yml` × 1（`docs/product/release-readiness.md`）、`.github/GOVERNANCE.md` × 3（`docs/README.md`、`docs/project/authors.md`、`docs/project/trademarks.md`）。前两份文档由 `2f9a91f89`（移除 Codex App desktop host）一并删除，描述的是已退役 host，无等价替代物。
10. **showcase HTML 由源重新生成**：`0623-agent-to-agent-pr-comments.html`、`0623-overnight-project-refactor.html` 是**过期生成产物**（`.md` 源已不含该引用）。经只读比对确认恰有这 2 页过期（catalog 与 stylesheet 已同步），运行 `examples/showcase-html-pages.py` 重新生成，未手改 HTML。

### 4. 许可证移除（文档与元数据层）

11. 删除 `tests/test_license_metadata.py`（4 个测试全部围绕已删文件与声明；修复前 2 failed / 2 passed）。
12. `pyproject.toml` 删除 `license` 与 `license-files`（后者指向三个不存在的文件）。
13. 清除 Apache-2.0 声明：根 `package.json`、`apps/presentation/{site,dashboard}/package.json`、两者 `package-lock.json` 中**仅根项目** `packages[""]` 一条（第三方依赖的 `Apache-2.0` 条目未动）、`packages/loopx-finance-value-discovery/pyproject.toml`、`packages/loopx-obelisk/pyproject.toml`。**`packages/dsh-loopx-plugin/` 保留**——它是唯一自带 `LICENSE`/`NOTICE` 的包，其声明指向自己的许可证文件。
14. 文档引用改写：`README.md`、`CONTRIBUTING.md`、`docs/README.md`、`docs/project/authors.md`、`docs/project/trademarks.md`、`docs/architecture/rfcs/shared-goal-authority-state-provider-v0.md`。
15. 经核实**未**改动 `packages/loopx-repo-health/smoke/repo_health_snapshot_smoke.py:29` 的 `"license": "Apache-2.0"`——它是上游 GitHub API 快照 fixture（owner 为 `huangruiteng`），不是本项目声明。

## 验证

- **两个 README 守卫**：`readme-demo-surface-smoke ok`；`docs-governance-smoke ok`（修复前为 `FileNotFoundError: .github/GOVERNANCE.md` 崩溃）。
- **README 命令全量校验**：脚本从 README 提取全部反引号与 `text` 代码块中的 `loopx` 调用（占位符归一化后逐条 `parse_args`，不执行 handler），**38 条 0 FAIL**（修复前 7 条失败）。
- **README 相对链接**：正则提取全部 markdown / `href` / `src` 目标，**0 断链**。
- **docs 相对链接**：复刻 `assert_local_doc_links_resolve` 全量扫描 `docs/**/*.md|html`，**19 → 0**。
- **showcase 同步**：`showcase-html-pages.py --check` → `ok`（修复前 `AssertionError: ... is not generated from the catalog`）。
- **public-safety 扫描**：`loopx check --scan-path README.md --scan-path docs/ --scan-path examples/` → errors=0, warnings=0, 898 文件。
- **ruff**：两个被改 smoke 文件 `All checks passed`。
- **canary 套件**（`--from-git-diff --git-diff-base HEAD`）：选中 **18 项，14 通过，4 失败**。4 项失败**全部在干净 HEAD worktree（`001b80980`）上同样失败**，非本次引入：
  ① `hot-path-interface-budget-smoke.py` 与 ③ `heartbeat-prompt-smoke.py` —— `heartbeat_prompt_json` 载荷 6334 字符超出 6200 预算（同一根因，与本地 registry goal 状态相关）；
  ② `local-state-write-correctness-contract-smoke.py` —— 找不到 `## Example Packet` 标记（中文文档转换漂移）；
  ④ `codex-cli-tui-bootstrap-smoke-bundle-smoke.py` —— 打包需 `LICENSE`，而 fork 已删除（与 022 记录的 ② 同源）。
  与本次改动直接相关的检查（product-entry、docs 治理、CLI command contract、install/update、benchmark boundary）全部通过。
- **预存 collection errors（既有，与本轮无关）**：`outbound_guidance`、`refresh_checkpoint_recovery`、`shared_goal_alignment_cli`（均 `ModuleNotFoundError: No module named 'tests.*'`，仓库无 `tests/__init__.py`）、`python_ci_workflow`（`.github/` 缺失）。与 022 记录的 4 项基线完全一致。
- **全量 pytest（`--continue-on-collection-errors`）**：**11 failed / 5805 passed / 25 skipped / 4 errors**。
  11 项失败在干净 HEAD worktree（`001b80980`）上逐条复现，**失败集合 diff 为空（完全一致）**，即本轮引入 **0 回归**：`test_smoke_fleet_health.py` × 2、`test_repository_change_window.py` × 1、`test_scheduler_ack_current_host_binding.py` × 2、`test_dashboard_command.py` × 1、`test_pr_program_snapshot_diff.py` × 1、`test_sonarcloud_workflow.py` × 3（后三者读已删的 `.github/workflows/`，与 4 个 collection error 同源）。
- **文档相关测试**：`test_capability_documentation.py`、`test_nokv_shadow_provider_probes.py`、`test_control_plane_import_boundaries.py`、`test_dependency_security_boundaries.py` 共 **23 passed**；showcase/presentation 相关 **133 passed**；`tests/test_windows_install.py` 本环境 4 skipped。

## 复查（第二轮）

首轮扫描范围是 README + `docs/`。复查把范围扩到**全仓库**并复核首轮结论，新发现并修复以下问题：

1. **`docs/product/release-note-template.md` 两处「许可证」占位小节**：首轮计划已列出该文件却漏做（内容在引用块/反引号内，链式扫描未命中的原因同下）。两节内容全部是 `v0.4.8` 的 Apache-2.0 迁移说明并引用已删的 `licensing.md`，本仓库已无对应政策，整节删除。经确认该文件无守卫断言这两节。
2. **`CONTRIBUTING.md` 3 处死链**：`CODE_OF_CONDUCT.md` ×2（L11、L22）与 `.github/GOVERNANCE.md` ×1（L172）。均改为不依赖已删文件的表述，保留实质内容（举报渠道、归属记录入口）。
3. **`packages/loopx-codex-provider-routing/RUNBOOK.md:4`**：配套文档指向已删的 `docs/guides/codex-multi-app-best-practices.md`，删除该配套块。
4. **`benchmark/README.md:11`**：把**发布站点路径**当作仓库相对路径书写（`../docs/capabilities/benchmark-toolkit/README.md`），仓库内真实位置是 `loopx/capabilities/benchmark_toolkit/README.md`（`docs/capabilities/` 由 mkdocs 生成，不经仓库路径解析）。已改为真实路径。
5. **`examples/showcase-catalog-smoke.py`（第三个 README 守卫）**：同样被 `c88509106` 的删除打红——它断言 README 仍含 `### 真实项目中的使用` 及 3 个外部用户案例链接。022 修好了姊妹文件 `readme-demo-surface-smoke.py`（其注释明确写该小节 "removed deliberately"）却漏了这一个。按同样口径对齐：移除 README 面断言，**保留** 3 份 case 文档与 showcase 索引断言（那些文档仍在磁盘上）。
6. **showcase 生成器源数据归属错误（由首轮重新生成暴露）**：`2f9a91f89` 把 `examples/showcase-html-pages.py` 的源路径从 `heartbeat-automation-prompt.md` 换成 `quota-allocation.md`，但**未同步标签与正文归属**，且未重新生成 HTML。首轮重新生成后页面出现「`heartbeat prompt contract` → `docs/quota-allocation.md`」的标签/路径错配，以及把「非平凡完成创建 typed successor todo 或写 no-follow-up rationale」错误归给 quota 文档。经核实该 claim 的真实出处是 **`docs/project-agent-todo-contract.md:320-324`**。已将证据归属改到真实出处、修正标签（`peer completion contract` / `peer continuation contract`）、并把两处把 "heartbeat prompt" 列为公开证据的叙述改为实际存活的证据，随后重新生成。
7. **文风修正**：`docs/project/authors.md` 首轮改写留下了句子碎片（「LoopX 的统一开源核心，版权由…」），改为完整句并顺带简化悬空的「不改变任一许可证」；`docs/project/trademarks.md` 的悬空许可证表述改为通用许可原则；两节标题相应调整（`## 归属`、`## 版权与项目身份`）。经确认无任何文件引用这两节锚点。
8. **排除的误报**（经核实非缺陷，未改动）：`apps/presentation/dashboard/index.html` 引用的 `manifest.webmanifest` / `pwa/icon-*.png` 走 Vite `public/` 约定（源文件在 `public/` 下，构建期映射到站点根）；`docs/community/github-maintenance-ops-best-practices.md` 的 "star-history" 是运维通用举例而非对本仓库的声明。

**复查后的链接核验**：全仓库 **402 个 md 文件 + `docs/` 全部 md/html** 的仓库内相对链接（含带 title 的链接、引用式定义、`href`/`src`/`poster`）**0 断链**；README 内部锚点全部有效；已删小节（Star 趋势 / License / 许可证政策）无残留引用。**增量改动后重跑守卫**：`readme-demo-surface-smoke ok`、`docs-governance-smoke ok`、`showcase-html-pages --check ok`、`showcase-catalog-smoke ok`、ruff 全部通过。

## 复查（第三轮）：全量守卫回归对照

前两轮是**反应式**修守卫——修一个是一个。第三轮改为系统性做法：先枚举**所有引用 README.md 的 smoke**（共 **81 个**），在改动树与干净 HEAD worktree（`001b80980`）上**各跑一遍并逐条 diff**。

### 发现并修复：一处由本人引入的回归

**`examples/readme-star-history-smoke.py` 在 HEAD 上通过、在我的树上失败 → 这是我引入的真实回归。** 该 smoke（`:101-112`）要求 README 依次含 `## 当前状态`、`## Star 趋势`、`## License`，并要求 Star 趋势是最后一节且其内含 star 图与 `width="800"`。我第二轮曾判断"它只测生成器脚本、不读 README"，**该判断是错的**，导致我删除 Star 趋势小节时未察觉破坏。

修复方式经过成本权衡后选择**恢复该小节**而非改写守卫，依据是：`c88509106`（fork README 精简）在删除 Trendshift 徽章与徽章行的同时**特意保留了 Star 趋势小节**，说明维护者有意留下它；且该图与 stargazers 链接指向上游、仍可解析，符合既定的"保留上游链接"决策。恢复时**修正了原描述中已失实的机制声明**（原文称"由仓库授权的 workflow 每 6 小时…生成"，而 `.github/workflows/` 在本 fork 已删除）——改为说明该快照由上游生成发布、本仓库内的确定性渲染脚本是 `scripts/render-star-history.py`。同时把守卫中的 `## License` 期望去掉（该节按许可证决策合法删除），并把 `width="800"` 的断言切片从 `[positions[1]:positions[2]]` 改为 `[positions[1]:]`。

### 系统性根因：三个 README 守卫从未被 canary 覆盖

`loopx/canary/planner.py` **只在 `:767` 与 `:920` 注册了 `readme-demo-surface-smoke.py` 一个 README 守卫**。`readme-star-history-smoke.py`、`showcase-catalog-smoke.py`、`docs-governance-smoke.py` **不在任何 canary profile 中**，因此 `loopx canary smoke-suite` 永远选不到它们——这正是 `docs-governance-smoke.py`（崩溃）与 `showcase-catalog-smoke.py`（失败）能在 HEAD 上长期无人发现的原因，也是本轮回归未被 `--from-git-diff` 选中的原因。**是否把这三个守卫注册进 canary profile 属于改变项目验证契约，未在本轮擅自改动，建议单独决策。**

### 最终回归对照（81 个 smoke，改动树 vs 干净 HEAD）

| 结果 | 数量 | 说明 |
| --- | --- | --- |
| 回归 | **0** | 无任何"HEAD 通过 → 本树失败"项 |
| 修复 | **2** | `docs-governance-smoke.py`（HEAD 崩溃）、`showcase-catalog-smoke.py`（HEAD 失败） |
| 两侧同失败（既有） | **23** | 见下方分类 |

**23 项既有失败按根因分类**（均与本轮改动无关，且均属"留待单独处理"范畴）：

- **许可证移除同类（3）**：`codex-cli-packaged-install-smoke.py`、`codex-cli-tui-bootstrap-smoke-bundle-smoke.py`、`release-promotion-concurrency-smoke.py` —— 均 `FileNotFoundError: LICENSE`，与「已知遗留」所列 5 个打包 smoke 同源。
- **`.github/` 缺失同类（2）**：`update-notes-archive-smoke.py`（缺 `.github/workflows/update-notes.yml`）、`codex-cli-no-clone-release-verification-smoke.py`。
- **中文化漂移（13）**：这些 smoke 断言**英文标题/文案**，而对应文档已在 `3ddec0839`/`f314a2680` 中文化 —— `quota-contract`（缺 `## Allocation Contract`）、`rollback-packet-protocol`（缺 `Commit And Todo Linkage`）、`agent-management-observability-mvp`、`agent-management-projection-contract`、`event-sourced-state-contract`、`local-state-write-correctness-contract`（缺 `## Example Packet`）、`task-graph-projection-fixture`、`todo-detail-cold-path-contract`、`goal-vision-replan-contract`、`session-runtime-control-plane-adapter-doc`、`global-manager-command-protocol`、`release-readiness-doc`（缺 `Status: v0.x maintainer contract.`）、`catalog-planner`（从中文 `interaction-pattern-catalog.md` 解析出 `archetype_count: 0`）。
- **其他既有（5）**：`bootstrap-command-pack`、`codex-cli-bootstrap-message`、`onboarding-connect-candidates`（`KeyError: 'heartbeat_opt_in_required'`）、`onboarding-no-scan-projection`（022 已记录：向 `connect` 传已删 positional）、`shared-goal-authority-e2e/ladder.py`（辅助模块，非 smoke，直接执行必非零退出）。

### 补查：被既有失败「掩盖」的断言

既有失败会让其**之后的断言根本执行不到**，从而掩盖新引入的失败。对两个相关 smoke 做了绕过掩盖的手工核验：

1. **`release-readiness-doc-smoke.py`**：在 DOC 段（`Status: v0.x maintainer contract.`）即失败，其后的 **TEMPLATE 段断言不可达**——而本轮删过 `docs/product/release-note-template.md` 的两个「许可证」小节。核验方式：从该 smoke 导入其全部常量，把 TEMPLATE 段要求逐条对当前模板文件比对。结果：所有**中文**必需项（`## 中文摘要`、`### 发布验证`、中文决策/使用标题与字段等）与 `### 许可证` 无关项均在位；报告缺失的全是**英文**标题（`## State Kernel & Control Plane`、`## Release Decision` 等），根因是该模板已被 `3ddec0839` 完整中文化（现为 `## 状态内核与控制面`、`## 发布决策`），属既有中文漂移。**结论：本轮对模板的删改安全。**
2. **`docs/product/release-readiness.md`**：核对其 DOC 段的 40+ 条必需短语，**无一条**落在本轮改写的那句（第 315 行「Ruff 命名空间选择与包覆盖下限…」）上；该 smoke 的失败点为 `状态:v0.x 维护者契约。`（中文）对应英文断言，同属中文漂移。

### 补查：引用「本轮改动的其他文件」的守卫

第三轮首轮只覆盖「引用 README.md」的 smoke。补查改为**枚举所有引用本轮任意改动文件的守卫**（30 个改动文件 → 28 个引用方），得到 10 个此前未运行的守卫并逐一执行：

- 通过（7 个 smoke + 2 个测试）：`auto-research-skill-contract`、`canary/smoke-suite-runner`、`cross-runtime-impl-review-demo`、`issue-fix-discovered-issue-promotion`、`issue-fix-repository-context`，以及 `tests/control_plane/test_local_authority_shadow_config.py`、`tests/test_public_package_lock_boundary.py`（**8 passed**，确认本轮对 `package-lock.json` 的 `packages[""]` 许可字段删除未越界到第三方依赖条目）。
- 失败且经 HEAD 复现为既有（2）：`repository-hygiene-smoke.py`（缺 `LICENSE`）、`frontstage-pages-workflow-smoke.py`（缺 `.github/workflows/frontstage-pages.yml`）。
- **环境前置未满足（1，非本轮所致）**：`frontstage-share-bundle-smoke.mjs` 失败于 `apps/presentation/site/node_modules is missing; run 'npm ci'`——检查点在 Vite 构建之前，本轮对 `package-lock.json` 的改动不参与该判定；未在本环境安装 site 依赖。（该 smoke 一度被我误判为通过，此处按实测更正。）

**复核后的最终判定：本轮改动在 81 个 README 相关 smoke + 10 个其他引用方守卫、全量 pytest（11 failed/5805 passed，失败集合与 HEAD 逐字一致）、全仓库链接、`loopx check`、ruff 五个维度上均为 0 回归。**

## 已知遗留（本次**未**处理，留待单独跟进）

- **产品代码仍依赖已删的 `LICENSE` 与 `.github/`**：`loopx/windows_install.py:27` 的 `COPY_FILES` 含 `LICENSE`、`COPY_DIRECTORIES` 含 `.github`；该模块由 `scripts/install-windows.ps1:32` 调用，即 **`docs/guides/installing-loopx.md:70` 记录的原生 Windows checkout 安装路径会因缺文件失败**。注意区分：README 的 `py -3.11 -m pip install` 代码块走 PyPI，**不受影响**；`tests/test_windows_install.py` 在本环境 4 skipped，故未暴露该缺陷。`scripts/desktop_runtime_bundle.py:22` 的文件清单同样含 `.github` 与 `LICENSE`。
- **因缺 `LICENSE` 而失败的守卫（4，实测）**：`codex-cli-packaged-install-smoke.py`、`codex-cli-tui-bootstrap-smoke-bundle-smoke.py`、`release/release-promotion-concurrency-smoke.py`（三者均 `FileNotFoundError: LICENSE`）、`repository-hygiene-smoke.py`（`REQUIRED_TRACKED_FILES` 含 `LICENSE`，报 `missing tracked repository-hygiene files: ['LICENSE']`）。
- **引用了 `LICENSE` 但在更早断言处失败（4，实测，非 LICENSE 直接所致）**：`install-local-smoke.py`（实际失败于 `:271` 的 `"outer host turn identity"` help 文案漂移，即 022 已记录的失败①，**未到达** `:284` 的 `.github` 与 `:286` 的 `LICENSE` 断言）、`release/codex-cli-no-clone-release-verification-smoke.py`（先失败于 doc phrase 断言）、`issue-fix-validated-memory-writeback-smoke.py`（先失败于 schema 断言）、`control_plane/agent-management-observability-mvp-smoke.py`（先失败于中文漂移）。
- **因 `.github/` 被删而失败的守卫**：`update-notes-archive-smoke.py`（缺 `.github/workflows/update-notes.yml`）、`frontstage-pages-workflow-smoke.py`（缺 `.github/workflows/frontstage-pages.yml`）、`repository-hygiene-smoke.py`（另需 `.github/SECURITY.md`、`.github/ISSUE_TEMPLATE/`、`.github/PULL_REQUEST_TEMPLATE.md`）。`install-local-smoke.py` 与 `release/*` 虽断言 `.github` 路径，但在更早断言处即失败，故不在此列。
- **引用 README 的 81 个 smoke 中有 23 项既有失败**保持现状（分类见「复查（第三轮）」）：许可证同类 3、`.github/` 同类 2、中文化漂移 13、其他既有 5。与 022 的"留待单独处理"一致。
- **canary 未覆盖三个 README 守卫**：`loopx/canary/planner.py` 只在 `:767`、`:920` 注册了 `readme-demo-surface-smoke.py`；`readme-star-history-smoke.py`、`showcase-catalog-smoke.py`、`docs-governance-smoke.py` 不在任何 profile，致其腐烂无法被发现（本轮回归亦未被 `--from-git-diff` 选中）。补注册会改变项目验证契约，建议单独决策。
- **上游导向链接按决策保留**：README 中全部 GitHub 链接（含 L270 的 clone URL）仍指 `huangruiteng/loopx` 而非本 fork `yanfeng98/nano-loopx`。这是决策结果，不是遗漏。
- `README.md:257-258` 的 issue 模板 CTA（`issues/new?template=first_run.yml`）与 `loopx first-run-report` 生成的 URL **经核实不是死链**：它们指向 upstream，而 upstream 上 `.github/ISSUE_TEMPLATE/` 仍存在。按「保留上游链接」决策未改动。
- `loopx/pr_review.py:444` 的 `"LICENSE"` 只是路径分类器（`public_entry_or_policy`），无害，未动。

## 环境备注

`origin/main`（fork main）为 **1.0.3、英文文档**，仍包含 Cursor/KunlunCode/ZCode/Antigravity/Codex App 等 host 表行与全部许可证文件——本次 host 移除与中文化均只存在于 `260906-dev`，尚未进入 main。`/tmp/loopx-baseline` worktree 为 022 基线对照遗留，非本次创建。
