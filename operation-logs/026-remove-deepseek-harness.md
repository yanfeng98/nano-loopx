# 026 · 移除 DeepSeek Harness 全部集成（两个 host + 插件包 + 可靠性诊断能力）

- **日期**: 2026-09-12
- **分支**: `260906-dev`
- **背景**: 用户明确不需要 DeepSeek Harness，要求完整移除且不破坏 LoopX 其他功能。
- **用户决策（6 项）**: ① **两个 host 都移除**（`deepseek-harness` headless 适配器 + `deepseek-harness-native` 同会话插件）；② **`reliability_diagnostics` 能力整体移除**（连同产品方向专章）；③ **`packages/dsh-loopx-plugin/` 整包删除**；④ **文档全部净删**（含设计文档与 showcase，只保留 changelog 类历史）；⑤ **`workflow-skills --host-surface` 参数及其唯一用途删除**；⑥ **两份 RFC 直接删除**（用户："归档没用，不影响 loopx 的能力就删除"）。
- **规模**: **152 文件（99 删除 / 53 修改），+54 / −36,028**。本系列最大的一次移除（对比 025 OpenCode：−5,425）。

## DeepSeek Harness 在本仓库有**三处独立耦合**（本次都移除）

1. **host 集成**：`deepseek-harness`（headless Turn 适配器，`loopx/dsh_goal_mode/` 1,075 行）与 `deepseek-harness-native`（同会话插件，`packages/dsh-loopx-plugin/` 51 个 tracked 文件 ≈25.9k 行）——同一产品的两种集成深度，因 v2 `Agent.followup` 与外部 Turn driver 的语义差异而必须两套机制。
2. **可靠性诊断能力**：`reliability-diagnostics` 是**通用内置能力**（origin `loopx-core`），但它**唯一**的 provider 是 `dsh-session-events`，由上述插件交付。移除插件后该能力没有任何实现。
3. **前端 showcase**：DSH × LoopX Replan 案例（catalog 条目 + 生成 HTML + 录屏 + `examples/dsh-loopx-demo/` 演示项目）。

## 必须避免的破坏点（本次最高风险）

1. **`START_GOAL_HOST_SURFACES` tuple ⇄ `host_descriptions` dict 是硬 KeyError 对**。`bootstrap_command_pack.py:369` 直接下标 `host_descriptions[host_surface]`，无 `.get()`。tuple 与 dict 单边改动必崩。已同改并验证 5 项键齐。
2. **`agent_onboarding.py` 的 `surface_by_type[agent_type]` 同样是硬下标**（`:243`），key 集合必须等价于 `AGENT_TYPE_CATALOG`。已同删两条 + 删除 `_start_instruction` 的两个 DSH 分支。
3. **`reliability-diagnostics` 是顶级 CLI 命令，且在 `MANPAGE_COMMAND_HELP_ONLY` 里**。`examples/cli-help-manpage-smoke.py:96` 断言 `parser_commands == manual_commands | MANPAGE_COMMAND_HELP_ONLY`——删命令必须同删 `help_surface.py:319` 的表项，否则 `stale_help_only` 失败。**实测 `man/loopx.1` 无变化**（help-only 命令不进 manpage），`render-manpage.py --check` 通过，未重新生成。
4. **`turn.py` 无条件 import `turn_dsh_host` → 后者无条件 import `dsh_goal_mode`**。任何走到 `turn.py` 的路径（包括只用 codex-cli 的用户）都依赖 `dsh_goal_mode` 存在。因此 import 切断与整包删除必须**同一提交**完成，不可分批。
5. **`docs/**` 链接守卫无豁免名单**。`docs-governance-smoke.py:280` 遍历 docs 下全部 `.md`/`.html` 断言每个相对链接都解析得到。全库唯一跨边界冲突是 `docs/architecture/rfcs/desktop-execution-frontends-v0.md:745` → 待删的 connector 文档；**随该 RFC 一起删除即自洽消失**。其余断裂链接两端都在删除集内（已脚本逐条验证）。
6. **showcase 生成产物禁止手改**。`docs/showcases/index.html` 由 catalog 生成，`examples/showcase-html-pages.py --check` 断言一致。删 catalog 条目后**用脚本重生成**，同批更新 `showcase-frontstage-prototype-smoke.py:42` 的硬编码 case id。
7. **canary profile 四处同步**：`canary/package_profiles.py`（唯一 profile）、`canary/premerge.py` 的 token 常量与 `mark()`、`examples/canary/premerge-validation-gate-smoke.py` 的逐字断言与调用点。`mark()` 第二参数必须等于 profile id。删掉唯一 profile 后 `PACKAGE_QUALIFICATION_PROFILES` 变空元组 → **整文件删除 `package_profiles.py`** 并清掉 `planner.py` 的 import 与 splice。
8. **三个假阳性，绝不可误删**：`deepseek-v4-flash` / `ark/deepseek-v4-flash` 是**模型/provider 名**（`experiments/planner_worker`、`loopx-codex-provider-routing`、`benchmark/widesearch`）；`handshake` / `qualifiedShadow` / `packetNeedsHostSelection` 是 `dsh` 子串；`DeepSeek-V3` 是 MoE 论文引用。搜索必须用 `deepseek[-_]harness` / `dsh-native` / `dsh_goal_mode` / `dsh-loopx` 这类精确词。
9. **`loopx/web/chat/assets/*.js` 是不可重建的构建产物**（35 个 bundle 含 `deepseek_harness` 下划线形式，即 showcase 的 `pattern_tags` 值——不是功能性的 `deepseek-harness`，后者 0 命中）。仓库内无前端源码，**处置：不动**，记入遗留。
10. **`workflow-skills --host-surface` 的 `elif host_surface:` 分支本就是死代码**：白名单只允许 `None | "deepseek-harness-native"`，非 None 的其它值在进入分支前就抛 `ValueError`。移除该参数因此无遗留语义。

## 变更清单

### 整包 / 整文件删除（99 个）

- **Python**:`loopx/dsh_goal_mode/`（4）、`loopx/capabilities/reliability_diagnostics/`（9）、`loopx/cli_commands/{reliability_diagnostics,turn_dsh_host}.py`、`loopx/canary/package_profiles.py`、`scripts/dsh_turn_host_adapter.py`
- **npm**:`packages/dsh-loopx-plugin/`（51 个 tracked 文件）
- **测试**:`tests/test_dsh_goal_mode.py`、4 个 `dsh_goal_mode_*_runner.py`、`tests/capabilities/test_reliability_diagnostics{,_dsh_provider}.py`、`tests/fixtures/control_plane/reliability_diagnostics_public_safety_v0.json`
- **示例/smoke**:5 个 dsh 专属 smoke、`examples/dsh-loopx-demo/`（整目录）、`examples/reliability_diagnostics/`（整目录）、`examples/canary/dsh-loopx-plugin-validation.py`
- **文档**:两份 integrations 指南、`docs/plans/2026-08-20-dsh-native-skill-driver.md`、showcase 案例页与录屏目录、两份 RFC
- **配置**:`pyproject.toml` 的 `deepseek-harness` extra + `loopx.dsh_goal_mode` package-data

### `loopx/` 手术

- `host_loop_activation.py`（47 处引用）：`HOST_MANAGED_SKILL_AGENT_TYPES` 2→1、`scheduler_command_binding_for_agent_type` 去两行、`SUPPORTED_AGENT_TYPES` 7→5、两条 `AGENT_TYPE_CATALOG` 条目（别名随派生表自动消失，`AMBIGUOUS_AGENT_TYPE_INPUTS` **无需改**）、`HOST_SURFACE_TO_AGENT_TYPE` 去 4 键、`scope_by_type` 去两行、两个 `_deepseek_harness*_activation` 整函数、两处分发分支
- `agent_onboarding.py`：**`_skill_delivery_contract` 塌缩**——`dsh_native` 条件为假时 `other-agent` 的行为**完全不变**（它本来就取 else 分支），故塌缩是纯 no-op；`inspect_skill_install_readback` 在该文件的 import 移除（该函数在 `workflow_skill_install.py` 与 benchmark 仍有消费者，未变死）
- `bootstrap_command_pack.py` / `slash_command_install.py` / `slash_command_files.py` / `workflow_skill_install.py` / `help_surface.py` / `cli.py` / `cli_commands/{turn,turn_registration,workflow_skills}.py` / `control_plane/{turn_driver/driver,scheduler/execution_context,goals/start_contract}.py` / `capabilities/catalog.py`

### 共享测试的**改名/重指**（不是删除，按 015–025 先例）

| 文件 | 处理 |
|---|---|
| `tests/test_host_loop_activation.py` | 删 2 个 DSH 专属函数，其余 24 个不动 |
| `tests/test_thread_agent_binding.py` | 28 处 fixture 重指 `claude-code` / `claude-session-1`（`codex://` deep-link 的 fail-closed 语义保持） |
| `tests/test_host_parity_smoke.py` | 集合、`SUPPORTED_HOSTS` 精确相等、计数下限 7→5 |
| `tests/test_skill_delivery_parity.py` | `HOST_MANAGED_SKILL_AGENT_TYPES` 精确相等 |
| `tests/test_slash_command_install.py` | 删 2 个测试（`can_bind_dsh_native_surface`、参数已删的 `rejects_unknown_fixed_surface`）；断言改为实际 surface 枚举 |
| `examples/project/host-mode-plan-cli-smoke.py` | 测试重指 `codex-desktop`（概念保留） |
| `examples/host-mode-plan-smoke.py` | 非法身份字面量重指 |
| `examples/content-ops-layout-library-smoke.py` | demo slug 去 DSH 命名 |
| 其余 | `test_workflow_skill_install` / `test_start_goal_compact_projection` / `test_loopx_turn_driver` / `test_capability_extension_registry` / `test_heartbeat_prompt_support` / `test_update_feed` / `agent-onboard-host-loop-activation-smoke` / `capability-extension-registry-smoke` / `dev-book-publication-smoke`(↔ book 章节硬同步对) / `release-artifacts-smoke` / `showcase-frontstage-prototype-smoke` |

**逐字保留（历史记录，不改写）**：`docs/product/release-readiness.md`（v0.4.7/v0.5.1/v0.5.2 等 changelog 行）、`docs/architecture/rfcs/hierarchical-agent-stride-control-v0.md`（外部 upstream GitHub URL）、`docs/development/contributor-tasks.md` 的「最近的 Maintainer 进展」行（带 PR 号 #3188）、全部 `operation-logs/**`、`deprecate/**`、`docs/research/**`。

## 验证

- **零残留（精确词）**：`deepseek[-_]harness|dsh[-_]native|dsh_goal_mode|dsh-loopx|dsh_loopx|DSH_|DeepSeek Harness|dsh-session|dsh-turn` 全库扫描（排除 `.git/`、`node_modules/`、`__pycache__/`、`operation-logs/`、`deprecate/`、`loopx.egg-info/`、`loopx/web/chat/assets/`）→ **仅剩 3 个历史记录文件**：上述 changelog、外部 RFC 引用、交付记录行。产品代码为 0。
- **枚举收缩（实测）**：`SUPPORTED_AGENT_TYPES` 7→**5**；`AGENT_TYPE_CATALOG` 7→**5**；`HOST_SURFACE_TO_AGENT_TYPE` 11→**7**；`HOST_MANAGED_SKILL_AGENT_TYPES` 2→**1**；`START_GOAL_HOST_SURFACES` 7→**5**；`SUPPORTED_HOSTS` 4→**3**；`BUILTIN_CAPABILITIES` 20→**19**。
- **降级实测（替代退役守卫，per 018/021/022/024/025）**：11 个 DSH 别名（`dsh`/`dsh-native`/`dsh_native`/`dsh native`/`deepseek-harness`/`deepseek_harness`/`deepseek harness`/`deepseek-harness-native`/`deepseek_harness_native`/`deepseek harness native` 等）× 2 个解析器（`normalize_agent_type`、`agent_type_for_host_surface`）**全部抛 `AgentTypeError`**；`start-goal --host-surface deepseek-harness`、`agent-onboard --agent-type deepseek-harness-native`、`turn run-once --host dsh`、`workflow-skills --host-surface`、`reliability-diagnostics`、`capability show reliability-diagnostics` **均被 argparse / registry 拒绝**。
- **兄弟面完好**：`codex-cli`/`claude-code`/`pi` 的 runtime_profile 与 host_surface 解析不变；`manual`/`other-agent` 仍无 profile；`codex-cli-tui`/`pi`/`shell` 解析正确。
- **守卫全绿（10/10）**：`render-manpage.py --check`、`cli-help-manpage-smoke`、`docs-governance-smoke`、`showcase-catalog-smoke`、`showcase-frontstage-prototype-smoke`、`dev-book-publication-smoke`、`readme-demo-surface-smoke`、`readme-star-history-smoke`、`canary/premerge-validation-gate-smoke`、`capability-extension-registry-smoke`。
- **全量 pytest 基线对照（决定性，口径同 015–025：跑 `tests/`，`--continue-on-collection-errors`）**：

  | | collected | passed | failed | skipped | errors |
  |---|---|---|---|---|---|
  | 干净 HEAD worktree（`929ceb835`） | 5749 | 5713 | 11 | 25 | 4 |
  | 本树 | 5597 | 5561 | 11 | 25 | 4 |
  | 差额 | **−152** | **−152** | **0** | 0 | 0 |

  **失败集合逐条比对：逐字一致 → 0 新增失败**；4 个既有 collection errors 原样保留。
  **收集差额实测复核（不预测）**：用 `--collect-only` 取两侧完整测试 ID 集合做 `comm`——消失 **152** 个、新增 **0** 个；消失项分布为 `test_reliability_diagnostics.py` 72 + `test_dsh_goal_mode.py` 50 + `test_reliability_diagnostics_dsh_provider.py` 22 + 8 个共享文件里的专属函数，**与删除清单逐一对应，零附带损伤**；`passed` 差额恰为 152，三处数字互相印证。
- **canary 套件**：30 选中 / 20 通过 / **10 失败，全部在干净 HEAD worktree（`929ceb835`）上逐条复现同样失败**（install-local、codex-cli-packaged-install、hot-path-interface-budget、cli-output-budget、monitor-poll-writeback、local-state-write-correctness、onboarding-no-scan-projection、heartbeat-prompt、codex-cli-tui-bootstrap-bundle、catalog-planner）。
- **ruff**：68 个改动 `.py` 文件 **All checks passed**；`git diff --check` 干净。
- **保全面差分测试（二次复查新增，最强证据）**：对 HEAD 与本树同时构建同一组探针输出——5 个 agent type 的 `build_host_loop_activation_packet` + `scheduler_command_binding_for_agent_type`、5 个 host surface 的 `build_loopx_bootstrap_command_pack`、4 个 visible 身份的 `build_host_mode_plan`、`build_agent_type_catalog` + 其 markdown 渲染、以及 `_command_prompt_specs`——共 22 个键。递归叶子级比对（归一化临时路径、剔除 DSH 专属结构）后，**全部差异仅 3 处且都是本次意图内**：① catalog markdown 少 2 行 DSH 条目；② `goal_start_contract.host_surfaces` 少 `deepseek-harness-native` 一行（pack 的 `serialized_bytes` 同步 −116 字节，即该行序列化长度，5 个 pack 差额一致因共享该子结构）；③ `prompt_specs[0].instructions[1]` 的 surface 枚举字符串（刻意订正）。**无任何意外行为变更。**
- **`_skill_delivery_contract` 塌缩实测**：HEAD 与本树对 5 个保留 agent type（含项目技能激活）的输出**逐字节一致**，证实塌缩对 `other-agent` 等是纯 no-op。

## 过程记录（自查发现并修正的问题）

1. **删除函数时误吃下一个函数的 `parametrize` 装饰器**（025 记录过的同类陷阱，本次再犯一次）：`tests/test_host_loop_activation.py` 中删除两个 DSH 函数时，边界查找只匹配 `^def `，把 `test_goal_hosts_attribute_spend_to_current_progress_refresh` 的 `@pytest.mark.parametrize("runtime_profile", ("codex_cli",))` 一起删掉。**已恢复**；此后所有函数删除改为同时匹配 `^@` 与 `^def`。
2. **showcase catalog 删条目时边界检测吃掉文件末尾 `}`**：首次用"`rstrip()` 等于 `},` 或 `}`"向下找边界，命中了嵌套对象的行首缩进 `}`,把数组结束符一起删掉。**JSON 校验拦住了（磁盘未写入）**，改用"下一个同级 `    {` 行"定位后成功；删除 116 行、case 数 12→11。
3. **两处断言主体随托管面消失，选择删除而非重指**：`test_onboarding_projects_verified_filesystem_readback` 断言的是 dsh-native 独有的 filesystem-verified readback（`owner=dsh_loopx_plugin`、`status=ready_for_host_load`）。`other-agent` 从未有过此路径，重指只会退化成"测试塌缩是否发生"，故按"主体是 vendor host 则删"的先例删除。同理 `test_host_materialization_rejects_unknown_fixed_surface` 因 `host_surface` 形参已删而必 `TypeError`，一并删除。
4. **ruff 两处 F401**：删除测试后 `import pytest` 与 `_skill_delivery_contract` 变为未用，已清理。
5. **二次对抗式复查发现一处漏网残留**：`skills/loopx-self-repair/references/repair-patterns.md`（**随 `skills/` 打包、安装进宿主的活文档**，`pyproject.toml:104-105` data-files、`PACKAGED_HOST_SKILL_IDS` 成员、`doctor.py:67` 引用）第 20 行 `host_plugin_system_python_mutation_gap` 的"需读证据"列写着"下游 **Driver/GoalBar** 命令解析"——`Driver` 与 `GoalBar` 正是被删插件的两个组件。首轮残留扫描的关键词表（`deepseek[-_]harness|dsh[-_]native|dsh_goal_mode|dsh-loopx|DSH_|...`）**不覆盖间接组件名**，故漏过。已改为中性的"下游各插件界面命令行解析"（该文档自述为"每当真实事件教给一个可复用的控制面教训时添加一行"的**活知识库**，教训本身通用，仅组件名专有）。已复核表格结构完好（184 行 × 5 列）且 `self-repair-upstream-issue-escalation-smoke` 不受影响。
   **教训**：host 移除的残留扫描必须包含**间接组件名**（UI/模块专有名），不能只搜品牌名。

## 已知遗留（不在本次范围）

- **`loopx/web/chat/assets/*.js`**（35 个 bundle）含 showcase 的 `deepseek_harness` 标签字符串。仓库内无前端源码，**不可重建**；残留是压缩产物数据岛里的死字符串，无功能影响。
- `loopx.egg-info/` 构建产物含 `[deepseek-harness]` 与 `loopx/dsh_goal_mode/*` 路径，下次 `pip install -e .` 自愈。
- 上游已发布的 GitHub release tag `dsh-loopx-plugin-v0.1.1-beta.4` 不因源码删除而撤销。
- `examples/release-artifacts-smoke.py` 在 HEAD 上**已是既有失败**（本 fork 的 `.github/` 已被整体删除，该 smoke 读取 `.github/workflows/release-artifacts.yml`）。本次删除其中一行 DSH 断言以免日后复活该声明，但**未修复该 smoke 的既有失败**。
- **本机环境既有限制**：`tests/capabilities/test_repository_change_window.py::test_reconcile_repairs_dirty_linked_worktrees_and_keeps_paths_private` 失败，根因是 `repository.py:127-130` 调用 `git worktree list --porcelain -z` 而本机 git 不支持该组合（已手工复现同一报错 `unknown switch 'z'`）。**该失败在干净 HEAD worktree 上完全一致**，与本次改动无关。
- `loopx/thread_agent_binding.py` 不校验 `host_surface` 白名单（025 已记，仍未处理）。
- `benchmark/swe-marathon/runtime/modes/profile_install.py` 的 7-id 技能集影子副本（024 已记）。

## 环境备注

基线对照口径同 015–025（跑 `tests/`，`--continue-on-collection-errors`）。本环境 4 个既有 collection errors（`outbound_guidance`、`refresh_checkpoint_recovery`、`shared_goal_alignment_cli`、`python_ci_workflow`）原样保留。移除后 `--host-identity` 合法值仍为 `codex-cli`/`claude-code`/`generic-cli`/`pi`；`--host-surface`（start-goal）合法值为 `codex-cli-tui`/`claude-code`/`pi`/`shell`/`other-agent`；`turn run-once --host` 合法值为 `codex-cli`/`claude-code`/`generic-cli`。
