# 025 · 移除 OpenCode 宿主（`opencode` v1 + `opencode2` v2 + `.opencode/skills` 投递面）

- **日期**: 2026-09-12
- **分支**: `260906-dev`
- **背景**: 用户不需要 OpenCode，要求完整移除且不破坏 LoopX 其他功能。
- **用户决策（4 项）**: ① **全部移除**——两个 host 变体**加上** `.opencode/skills` 项目技能投递面；② **connector id 改名为中性**（`opencode_goal_loop` → `generic_cli_visible_loop`）；③ **静默删除**（017/018 式，不写退役说明段落）；④ **先清理再移除**（先跑 uninstall 清掉本机 facade，再改代码）。

**OpenCode 在本仓库有两处独立耦合**（本次都移除）：
1. **host-loop goal 模式**：`opencode`（进程内 plugin bridge，858 行）与 `opencode2`（进程外 worker，1018 行）——同一产品的两个大版本，因 v2 的 plugin API 与 v1 硬性不兼容而必须两套机制。
2. **项目技能投递面** `.opencode/skills`（`PROJECT_SKILL_SURFACES` 之一），服务于 `loopx-material` / `loopx-change-quality`。

## 阶段 0 — 移除前清理（本机，无仓库改动）

`loopx slash-commands --uninstall --surface opencode`（不带 `--with-goal-bridge`，bridge 本就未装）：
- 退役 **22 个 LoopX 托管文件**（`~/.config/opencode/commands/` 11 个 + `skills/` 11 个），
  全部带 `loopx-managed-slash-command` 标记 → 逐条 `would_retire_managed_file`，**0 残留**
- 清理 12 个 LoopX 创建的空目录
- **未触碰** `package.json`、`node_modules/`、`opencode.json`、`oh-my-opencode.json`（第三方配置）及用户自有文件
- 用户自有的 `@opencode-ai/plugin: 1.15.10` 低于 LoopX 要求的 `>=1.17.15 <2`，再次证实 bridge 从未安装

## 变更清单（70 文件，+170 / −5259；13 整文件删除、57 修改。本日志与索引另计）

### 陷阱与破坏点（本次最高风险）

1. **`generic-cli` 的 connector id 与 Pi 共享，删行会废掉 Pi 的可见模式**。`SUPPORTED_TURN_HOST_IDENTITIES = sorted(VISIBLE_HOST_CONNECTOR_IDS)`——删掉 `generic-cli` 行会让 `pi → generic-cli` 的解析抛 `unsupported host_identity`。做法：**只改名不删行**，并同步重指 `host_mode_planner.py:745` 为 `VISIBLE_PI_ALIASES.get(raw_identity, raw_identity)`（原为 `.get(candidate, candidate)`，中间依赖已删的 `VISIBLE_OPENCODE_ALIASES`）。
   **实测验证**：`pi → pi_goal_loop`、`generic-cli → generic_cli_visible_loop`、`codex-cli`/`claude-code` 不变、`opencode`/`opencode2` 正确抛 `HostModePlanError`。
2. **`man/loopx.1` 有字节级守卫**（`examples/cli-help-manpage-smoke.py:135` 断言与 `render_manpage()` 逐字节相同），且同文件 `:96` 断言 `parser_commands == manual_commands | MANPAGE_COMMAND_HELP_ONLY`。三件事必须原子：删 `cli.py` 的 `opencode2-goal-worker` 子命令 → 删 `help_surface.py:318` 表项 → **用 `scripts/render-manpage.py` 重新生成**（禁手改）。
3. **`--surface all` 默认集变化是用户可见行为变更**：`["codex","claude-code","opencode"]` → `["codex","claude-code"]`。已同步 `slash_commands.py` 帮助文案与 `docs/guides/installing-loopx.md:112`。
4. **模块级 import 必须先于整包删除**（018 教训）：`slash_command_install.py:8` 的 `from .opencode_goal_mode import ...`、`cli.py:151-153` 均先删。
5. **`install_skill_facade` 是 022 的逆情形**：022 当年**特意保留**它，理由正是"OpenCode surface 仍用"。产品代码中它只有 2 处引用（import + OpenCode 块内唯一调用）。**已实测确认删除不丢产品面**——`codex`（`:633-635`）与 `claude-code`（`:737-739`）块**各自有内联循环**遍历全部 11 个 spec（含 `loopx-deepresearch`）写 `<name>/SKILL.md`；该 helper 只是给 OpenCode 用的同逻辑抽取版。
6. **`bootstrap_command_pack` 的 tuple 与 dict 成对**：`:349` 遍历 `START_GOAL_HOST_SURFACES` 并查 `host_descriptions`，单边改动会 `KeyError`。已同改并验证 7 项键齐。
7. **附带修正 024 残留**：`control_plane/goals/start_contract.py:200` 仍写着 "OpenCode bridge, **Ark one-shot**"——024 移除 Ark 时漏了这行，本次正好改同文件，按 018/021「附带修正」先例一并清理。

### 整文件删除（13）

`loopx/opencode_goal_mode/`（4：`__init__.py`、`loopx-goal.js`、`goal-bridge-runtime.mjs`、`README.md`）、
`loopx/opencode2_goal_mode/`（3：`__init__.py`、`opencode2-goal-worker.mjs`、`README.md`）、
`loopx/cli_commands/opencode2_goal_worker.py`、
`tests/test_opencode_goal_bridge.py`、`tests/test_opencode2_goal_worker.py`、`tests/test_opencode2_goal_worker_cli.py`、
`tests/opencode_goal_bridge_runtime.test.mjs`、`tests/opencode2_goal_worker.test.mjs`。
`pyproject.toml` 的两条 package-data 一并删除。**`tests/pi_goal_loop_runtime.test.mjs` 保留**（Pi 独立运行时）。

### `loopx/` 手术（含 7 处函数级删除）

- `slash_command_install.py` 大幅收缩：删 `_opencode_command_body`、`_opencode_home`、`_opencode_plugin_name`、`_opencode_direct_goal_plugin_conflicts`、`_target_package_dependencies`、`OPENCODE_GOAL_DEPENDENCIES`、整个 `if "opencode" in effective_surfaces:` 安装块（199 行）、goal-bridge 守卫块、`with_goal_bridge`/`opencode_home` 参数与 payload/notes/render 项；默认集收缩。连带孤儿 import（`json`、`front_matter`）
- `slash_command_files.py`：删 `install_skill_facade`（至 EOF）；`skill_body` 因 `slash_command_install` 仍在用而保留
- `cli.py`：删 import / register / dispatch 三处，`opencode2-goal-worker` 子命令消失（子命令总数 120 → 119）
- `cli_commands/slash_commands.py`：`--surface` choices 去 `opencode`，删 `--with-goal-bridge` 与 `--opencode-home` 两个公开参数及 pass-through（二者现为 argparse 拒绝）
- `host_mode_planner.py`：connector 改名 + 删 `VISIBLE_OPENCODE_ALIASES` 整表 + 重指解析器 + 2 处注释去 OpenCode
- `host_loop_activation.py` 8 处配对删除：scheduler 绑定、`SUPPORTED_AGENT_TYPES`（9→7）、两条 `AGENT_TYPE_CATALOG`（别名随派生表自动消失，`AMBIGUOUS_AGENT_TYPE_INPUTS` **无需改**）、四个 `HOST_SURFACE_TO_AGENT_TYPE` 键、scope 行、`_opencode_activation` 与 `_opencode2_activation` 整函数、分发分支
- `help_surface.py` 3 处 + `man/loopx.1` 重新生成
- `capabilities/project_skill_delivery/core.py`：`PROJECT_SKILL_SURFACE_ROOTS` 去 `opencode`（4 → 3），下游 choices 派生自动收缩
- 注释类：`pi_goal_mode/pi-goal-loop-runtime.mjs`、`control_plane/quota/host_poll_receipts.py`

### 示例、安装器、benchmark、文档

- **示例 EDIT 而非删除**（canary planner 等注册了它们）：`install-local-smoke.py`、`slash-command-install-smoke.py`、`agent-onboard-host-loop-activation-smoke.py`、`host-mode-plan-smoke.py`、`project/host-mode-plan-cli-smoke.py`
- **硬同步对**：`examples/dev-book-publication-smoke.py` 的 `assert_zh_concepts` 元组 ↔ `docs/book/chapters/02-session-goal-loopx.md` 表格行，同一次改动
- `scripts/install-local.sh`：删 usage 行与整个 `LOOPX_INSTALL_OPENCODE` 块，**含 heredoc 里的 `$opencode_line`**（脚本 `set -euo pipefail`，未定义变量会中止安装）
- `benchmark/swe-marathon` 两处 `LOOPX_INSTALL_OPENCODE: "0"`；`.gitignore` 的 `.opencode/goals/`（变死条目）；`README.md` host 表两行；`apps/presentation/site/src/App.tsx` 5 处（先例 `051f57202` 退役 TraeX 时改的就是这文件）
- 文档净删（**无退役段落**，017/018 式）：`docs/index.md`、`docs/guides/{getting-started,installing-loopx,newcomer-command-path,custom-agent-runner-integration}.md`、`docs/book/chapters/00-reading-guide.md`、`docs/community/github-maintenance-ops-best-practices.md`、`docs/development/contributor-tasks.md`(5)、`docs/reference/protocols/{agent-scoped-evidence-ledger-v0,loopx-goal-command-v0}.md`、`docs/integrations/runtime-connector-catalog.md`（`opencode_goal_loop` 行改名并改写为 host-neutral、`opencode2_goal_worker` 行删除、`generic-cli` 映射段改写）、`docs/reference/protocols/host-mode-plan-v0.md`、`loopx/capabilities/{project_skill_delivery,material_lifecycle,change_quality}/README.md`、`skills/loopx-{material,change-quality}/SKILL.md`

**逐字保留（历史记录，不改写）**：`docs/product/release-readiness.md`（3 处 v0.1.8/v0.2.9/v0.4.7 changelog）、`docs/architecture/rfcs/goal-usage-token-cost-v0.md`（4 处 RFC 设计分析）、`docs/community/ecosystem-adoption.md`（1 处记录外部贡献者 kit 的采用条目，021 有同类先例）、全部 `operation-logs/**`、`deprecate/**`、`docs/research/**`。

## 验证

- **零残留 grep**：`opencode|open-code|open_code` 全库扫描（排除 `.git/`、`node_modules/`、`__pycache__/`、`operation-logs/`、`deprecate/`、`research/`、各项缓存）→ **仅剩上述 3 个历史记录文件共 8 处**，产品代码为 0。
- **import + 编译闸门**：`compileall` 0 失败；6 个高风险模块逐一显式 import 成功；`build_parser()` 可构建。
- **陷阱 1 行为验证**：见上（4 个身份解析 + 2 个拒绝）。
- **降级实测（替代退役守卫，per 018/021/022/024）**：8 个别名（`opencode`/`open-code`/`open_code`/`open code`/`opencode2`/`opencode-2`/`opencode_2`/`opencode-v2`）经 `normalize_agent_type` 与 `agent_type_for_host_surface` **全部抛 `AgentTypeError`**；`agent-onboard --agent-type opencode`、`start-goal --host-surface opencode2`、`slash-commands --install --surface opencode`、`--with-goal-bridge`、`--opencode-home` **均被 argparse 拒绝**；`project-skill --surface opencode` 拒绝。
- **枚举收缩**：`SUPPORTED_AGENT_TYPES` 9→7；catalog 条目 9→7；`START_GOAL_HOST_SURFACES` 9→7（本分支 Ark 移除后口径）；`--surface` choices 6→5；`PROJECT_SKILL_SURFACES` 4→3；`--host-identity` choices 去 `opencode`。
- **陷阱 5 验证**：`codex`/`claude-code` 块各自内联遍历 11 个 spec 写 skill，`/loopx-deepresearch` 投递路径未丢。
- **聚焦 pytest**：10 个相关文件 **240 passed / 0 failed**。
- **守卫全绿**：`cli-help-manpage-smoke`、`dev-book-publication-smoke`、`docs-governance-smoke`、`readme-demo-surface-smoke`、`slash-command-install-smoke`、`host-mode-plan-smoke`、`host-mode-plan-cli-smoke`、`agent-onboard-host-loop-activation-smoke`、`showcase-catalog-smoke`、`readme-star-history-smoke`、`showcase-html-pages --check`、`render-manpage.py --check`。唯一失败为 `catalog-planner-smoke`（**预存**：从中文 `interaction-pattern-catalog.md` 解析出 `archetype_count: 0`，与本轮无关）。
- **全量 pytest 基线对照（决定性）**：collected **5773 → 5749**（差额 **−24**，与计划预测完全一致）；含 `opencode` 的测试 ID 从 28 归零；**11 failed / 5713 passed / 25 skipped / 4 errors**，**失败文件集合与基线逐字一致 → 0 新增失败**。4 个既有 collection errors 原样保留。
- **canary 套件**：20 选中 / 13 通过 / **7 失败，全部在干净 HEAD worktree（`4c0b51faf`）上逐条复现同样失败**（install-local 的 help 文案漂移、两个 LICENSE 打包、cli-output-budget、global-manager 合同文案、onboarding positional、heartbeat budget）。
- **ruff**：32 个改动 .py 文件 **All checks passed**；`git diff --check` 干净。

## 过程记录（自查发现并修正的问题）

1. **两处行级脚本误伤**：① `tests/test_project_skill_cli.py` 删 `"opencode",` 行后留下悬空 `--surface`（被测试捕获）；② 删除函数时装饰器块残留并错误挂到下一个函数（`test_slash_command_install.py` 与 `test_host_mode_activation` 各一次）。两处均已修正并复跑通过。
2. **`install-local.sh` 删除边界多留一个 `fi`**：内层 `if/fi` 嵌套导致首匹配命中内层 `fi`，`bash -n` 立即暴露，已修正。
3. **三处断言重指需实测而非推测**：① `test_default_and_all_surfaces_*` 原本断言 `codex/prompts/loopx.md`，实测 codex 块只写 `skills/`（`codex_prompt_dir` 为 None），改为断言实际的 skills 路径；② 计划中预测的 collected 差额 `−24` 与实测吻合；③ Plan agent 曾提出「删除 `install_skill_facade` 会让 `/loopx-deepresearch` 失去唯一投递路径」并要求用户决策，**经读码实测证伪**（codex/claude 各有内联循环），故未打扰用户。

## 已知遗留（不在本次范围）

- **OpenCode 老用户的手工清理**（本机已由阶段 0 解决；文档净删策略下不再提供退役段落）：`~/.config/opencode/commands/loopx*.md`、`~/.config/opencode/skills/<spec>/`；若曾装 bridge 还需 `plugins/loopx-goal.js`、`loopx/goal-bridge-runtime.mjs`，以及 `package.json` 中可选的 `@opencode-ai/plugin` / `opencode-goal-plugin` 依赖（uninstall 设计上保留 `package.json` 依赖，可能被用户自有 plugin 共享）；项目内 `.opencode/goals/`；状态目录 `$XDG_STATE_HOME/loopx/opencode2/`；临时缓存 `/tmp/loopx/opencode2-goal-worker/`。
- `loopx/thread_agent_binding.py` 不校验 `host_surface` 白名单（只当 compact public-safe token），理论上既有 registry 可能残留 opencode 绑定（本机已确认无），移除后无法再新建。
- `benchmark/swe-marathon/runtime/modes/profile_install.py` 有一份 7-id 技能集影子副本（024 已记，仍未处理）。
- `catalog-planner-smoke` 的中文漂移失败（预存，本轮未处理）。

## 环境备注

基线对照口径同 015–024（跑 `tests/`）。本环境 4 个既有 collection errors（`outbound_guidance`、`refresh_checkpoint_recovery`、`shared_goal_alignment_cli`、`python_ci_workflow`）与既有 failed 集合与前几轮一致。移除后 `--host-identity` 合法值为 `codex-cli`/`claude-code`/`generic-cli`/`pi`；`--surface` 合法值为 `all`/`codex`/`codex-cli`/`claude-code`/`pi`。
