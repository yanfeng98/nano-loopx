# 024 · 移除 Ark Managed Agent 宿主（`ark-managed-agent`）

- **日期**: 2026-09-12
- **分支**: `260906-dev`
- **背景**: 用户评估后决定移除。判定依据（实测，非印象）:专属实现仅 **81 行 / 17 文件**，却配 **688 行专属测试 + 2 份协议文档（123 行）**，并独占一整套调度子系统；上游最后改动停在 **2026-08-02**（移除时已 6 周）；唯一一次真实端到端资格验证（2026-07-29，14 次已认证 provider 交互）此后**从未复跑**；且它是云侧 host，本地不可运行。用户已在本分支连续移除 8 个 host（KunlunCode/ZCode/Codex IDE/Antigravity/Codex App×2/Gemini/Cursor/TraeX），Ark 是处置逻辑上的漏网者。
- **用户决策（3 项）**: ① 彻底移除 `LOOPX_ENTRY_HOST_SURFACE` 机制（不重绑 dsh-native）；② **不**加退役守卫测试，延续 016/018/021/022 做法；③ 两个 Ark 命名测试文件**改名保留共享测试**，只删 Ark 专属。
- **前置核实**: 本机 registry 无 ark goal（`~/.codex/loopx/registry.global.json` 唯一 goal 是 fixture `e2e-goal`，且无 `host_surface` 字段），故**不涉及既有状态迁移**。

## 三个必须避免的破坏点（本次最高风险）

1. **`NATIVE_GOAL_RUNTIME_PROFILES` 保留并收缩，不能删**。它原为 `{ARK_MANAGED_AGENT_GOAL, CODEX_CLI_VISIBLE}`，被三处**共享**代码消费（`heartbeat/host.py:32`、`quota/spend_sources.py:43`、`work_items/accountable_settlement.py:76`）。删除会直接打破 Codex CLI 可见 goal 的配额记账。已收缩为 `{CODEX_CLI_VISIBLE}`。（注:两份并行审计在此点给出**相反**结论，经读码亲自确认后取"保留"。）
2. **`ARK_MANAGED_AGENT_REQUIRED_SKILL_IDS` 是命名错误，必须改名而非删除**。它是**所有 host-managed 类型**（含 dsh-native、other-agent）的必需技能集。已改名 `REQUIRED_HOST_SKILL_IDS` 归位到 `skill_install_readback.py`，`agent_onboarding.py` 改为 re-export（保持同一对象，`tests/test_skill_delivery_parity.py` 的 `is` 恒等断言继续成立）。
3. **两个 Ark 命名测试文件里大部分是共享测试**。`test_ark_managed_agent_issue_fix_matrix.py` 5 个测试中仅 1 个 Ark 专属；整删会静默丢失 4 个无关 issue-fix 测试。已改名保留。

## 变更清单（42 文件，+236/−1803；含 4 整文件删除、1 改名。本日志与索引另计 2 文件）

**整文件删除（Ark 独占，零其他消费者）**
1. `loopx/ark_managed_agent_host.py`（59 行；唯一外部 importer 是 `heartbeat/builder.py`）
2. `docs/reference/protocols/ark-managed-agent-goal-continuity-qualification-v0.md`
3. `docs/reference/protocols/ark-managed-agent-issue-fix-qualification-v0.md`

**测试改名 + 裁切（陷阱 3）**
4. `tests/test_ark_managed_agent_host.py` → `tests/test_host_managed_skill_delivery.py`：删除 8 个 Ark 专属测试与 3 个专属 helper；保留并重指 5 个共享测试（文件系统 readback、3 个 skill readback、retire duplicate）。`_materialize_workflow_skills` 去掉 `host_surface` 参数即可。一处重指需注意：dsh-native 契约不投影 `filesystem_readback` 键（Ark 独有），改为断言实际投影路径 `status == "ready_for_host_load"` + `mode`/`owner`/`host_readback_required`，意图不变。
5. `tests/test_ark_managed_agent_issue_fix_matrix.py` → `tests/test_issue_fix_host_closure_boundary.py`：只删 1 个 Ark 测试，保留 4 个通用 issue-fix 测试。

**`loopx/` 外科手术（17 文件）**
6. `control_plane/scheduler/execution_context.py`:删 `GOAL_RUNTIME_CONTINUATION_SCHEMA_VERSION`、`HostSurface.ARK_MANAGED_AGENT`、`SchedulerOwner.GOAL_RUNTIME`、`SchedulerRuntimeProfile.ARK_MANAGED_AGENT_GOAL`、`GoalRuntimeContinuationDisposition`、`GOAL_RUNTIME_DEFER_ACTIONS`、profile 映射项、两条双向校验规则（原 `:167-171`/`:197-201`）、`build_goal_runtime_continuation` 整函数、`frontier_recheck_after_seconds` 参数与其 emit；**`NATIVE_GOAL_RUNTIME_PROFILES` 收缩（陷阱 1）**。
7. `control_plane/scheduler/scheduler_hint.py`:删 `SCHEDULER_FRONTIER_IDENTITY_KEYS`、`GOAL_RUNTIME` 身份键分支、转发 kwarg；`_scheduler_identity_keys` 失去唯一参数并简化，3 处调用点同步收敛；连带删孤儿 import `SchedulerOwner`。**保留** `build_frontier_recheck_plan`（被 `todos/frontier_deadline.py`、`monitor_wait.py`、`todos/quota_summary.py` 共享）。
8. `host_loop_activation.py` 6 块:`HOST_MANAGED_SKILL_AGENT_TYPES` 成员（3→2）、profile 绑定、`SUPPORTED_AGENT_TYPES`（10→9）、`AGENT_TYPE_CATALOG` 整条（6 别名随派生表自动消失）、`HOST_SURFACE_TO_AGENT_TYPE` ×2、`scope_by_type` 行、`_ark_managed_agent_activation` 整函数 + 分发分支。
9. `skill_install_readback.py` + `agent_onboarding.py`:常量改名与 re-export（陷阱 2）。`agent_onboarding.py` 另删 Ark 投递块（含 `LOOPX_ENTRY_HOST_SURFACE`/`fixed_install_script`/`no_clone_install_command`）、surface 映射行、`_start_instruction` Ark 分支；连带删孤儿 import `NO_CLONE_INSTALL_URL`。dsh-native 投递路径完好（实测 owner 仍为 `dsh_loopx_plugin`）。
10. `doctor.py`:删 Ark 门控的 `host_skill_install_readback` 赋值与其 3 个守卫消费者、`skill_delivery.owner` 的 Ark 分支、Ark 专属修复文案、`host_skill_installation_readback` 检查项；连带 3 个孤儿 import（ruff `--fix`）。**保留** `agent_type_uses_host_managed_skills` 两条分支（dsh-native/自定义 host 仍用）。
11. `control_plane/heartbeat/host.py`:删 `uses_ark_managed_agent_goal_host` 整函数与 `uses_native_goal_host_loop` 内两行 Ark 分支。
12. `control_plane/heartbeat/builder.py`:删跨包 import、renderer 选择的 Ark 分支与参数、host_contract 注入、Ark 预算错误标签（收敛为单条 Codex 文案）。
13. `control_plane/heartbeat/task_body.py`:删 `render_ark_managed_agent_goal_task_body` 整函数；共享 `_render_goal_task_body` 保留另一调用方。
14. `heartbeat_prompt.py`:删 shim 重导出与 `__all__` 两项。
15. `bootstrap_command_pack.py`:`START_GOAL_HOST_SURFACES`（10→9）、host 描述、gate reason 文案。
16. `slash_command_install.py`:entry-skill 指令文本去 Ark、`materialize_loopx_entry_skill` allowlist 收缩为 `{None, "deepseek-harness-native"}`。
17. `control_plane/goals/start_contract.py`、`cli_commands/quota_registration.py`、`cli_commands/support_control_heartbeat_registration.py`、`cli_commands/workflow_skills.py`:枚举与 choices 行（`--host-surface` 5→4、`--scheduler-owner` 5→4、`workflow-skills --host-surface` 2→1）。

**`scripts/install-local.sh`（决策 1）**
18. 删 usage 行、`LOOPX_ENTRY_HOST_SURFACE` 变量与硬守卫（原仅接受 `ark-managed-agent`）、两处 pass-through；`host_surface` 改用函数默认值。`preflight_workflow_skills()` 因守卫消失成为空操作，整函数与其调用点一并删除。**注意**:脚本为 `set -euo pipefail`，删变量必须同步删所有引用。期间一次替换曾误重复 `validate_release_candidate` 块，已即时修正并核对为「1 定义 + 1 调用」。

**测试断言收缩（12 文件）**
19. 硬计数:`test_host_parity_smoke.py` `>= 10` → `>= 9`（本仓唯一硬 agent-type 计数；022 有 11→10 先例）。精确集合:`test_skill_delivery_parity.py` 的 `HOST_MANAGED_SKILL_AGENT_TYPES` 字面量去 Ark（`len(REQUIRED_HOST_SKILL_IDS) == 7` 不变，值存活）。
20. `test_scheduler_execution_context.py`:删 14 个 Ark 测试、`VALID_COMBINATIONS` 去 Ark 元组、`FIRST_CLASS_RUNTIME_PROFILES` 去 Ark 行。两个借用 Ark profile 作 context 的 frontier-deadline 测试**重指到 `codex_cli` 并只删 continuation 断言**（`frontier_deadline` 共享覆盖全库仅存于此文件，不可丢失）。
21. `test_start_goal_compact_projection.py`（16 项同源失败）:8 处 fixture 值重指 `codex-cli-tui`、硬编码 10 项列表去 Ark 行、删 1 个 Ark 专属测试。
22. 重指而非删除（host-neutral 契约）:`test_runtime_capability_reentry.py`、`test_effect_interpreter_packet.py`、`test_fine_grained_turn_mode.py`。
23. `test_host_loop_activation.py` 7 处;`test_heartbeat_prompt_support.py` 删 Ark 块与 import;`test_slash_command_install.py` 文案断言改指存活表面、删 1 个 Ark 专属测试（dsh-native 孪生测试已覆盖同一路径）。

**示例与文档（6 文件）**
24. `examples/control_plane/agent-onboard-host-loop-activation-smoke.py`、`examples/release/local-install-promotion-boundary-smoke.py`:**EDIT 而非删除**（删除会静默打断 `loopx/canary/planner.py`、`quality_surface_catalog.py`、`release-readiness-doc-smoke.py`、`peer-agent-runtime-v1-smoke.py` 的引用）。前者另修正一处**既有**错误期望（`suggestions` 期望值是重复列表 `["codex-cli","codex-cli"]`，实际为单元素；HEAD 上同样失败，已实测确认）。
25. `docs/reference/protocols/README.md` 去两条索引（必须同 commit，否则 `docs-governance-smoke` 的链接解析失败）；`host-integration-surface-v0.md` 删 Ark 整段但**保留并重新归档**两段仍成立的共享内容（安装器所有权、`runtime_capability_reentry_v0` —— 后者与 Codex 共享，是它唯一的散文记录）；`loopx-goal-command-v0.md` 家族句由复数改写为单成员、删激活条目与表行、reentry 末句去 Ark 分句；`README.md` 删 host 表 Ark 行。
26. **保留** `docs/product/release-readiness.md` 的历史 changelog（先例:`:187` 仍写「Pi 与 TraeX」）。

**不要动（同名不同义，「Ark」指火山方舟 LLM）**:`capabilities/public_safe_outbound/scanner.py` 的 `ark_api_key`、`worker_bridge.py` 的 `ARK_API_KEY`、`control_plane/testing/model_tool_behavior.py` 的 "Ark" function-tool transport;以及 `botmux_runtime.py` 的 `goal_runtime_revision`、`factorial_contrast.py` 的局部变量、`benchmark/tests/test_native_codex_goal.py` 的 Codex 侧 `test_goal_runtime_*`。

## 验证

- **零残留 grep**:`ark[-_ ]?managed|ARK_MANAGED` 全库扫描（排除 `.git/`/`node_modules`/`__pycache__`/`deprecate/`/`operation-logs/`，并排除 `benchmark`/`remark`/`marker`/`markdown` 误报）→ 仅剩 `docs/product/release-readiness.md` 的历史 changelog。
- **陷阱 1 行为验证（本次最关键的"不破坏"证明）**:已实测脚本断言 `{p.value for p in NATIVE_GOAL_RUNTIME_PROFILES} == {"codex_cli"}` **且** `quota_spend_source_for_execution_context(scheduler_execution_context_for_runtime_profile("codex_cli")) == "visible-goal"`。**注**:profile 真实值是 `codex_cli`（非 `codex_cli_visible`），传错值会**静默回落**到默认 `heartbeat`；该路径**全库无任何直接测试覆盖**，故此行为断言是唯一守护手段。
- **降级实测（替代退役守卫）**:6 个别名（`ark-managed-agent`/`ark_managed_agent`/`Ark Managed Agent`/`managed-agent`/`managed_agent`/`managed agent`）经 `normalize_agent_type` 与 `agent_type_for_host_surface` 均抛 `AgentTypeError`;`agent-onboard --agent-type ark-managed-agent` 与 `quota should-run -H ark_managed_agent` 均 argparse 拒绝;`workflow-skills --host-surface ark-managed-agent` 拒绝。
- **枚举收缩**:`SUPPORTED_AGENT_TYPES` 10→9;`HOST_MANAGED_SKILL_AGENT_TYPES` 3→2;`--host-surface` 5→4;`--scheduler-owner` 5→4;`START_GOAL_HOST_SURFACES` 10→9;`start-goal --host-surface` choices 9 项无 ark;`--list-agent-types` 无 ark。
- **聚焦 pytest**:Ark 相关的 14 个测试文件 **319 passed / 0 failed**。
- **守卫全绿**:`readme-demo-surface-smoke`、`docs-governance-smoke`、`showcase-catalog-smoke`、`readme-star-history-smoke`、`showcase-html-pages --check`、两个被 EDIT 的示例 smoke（`agent-onboard-host-loop-activation-smoke` 与 `local-install-promotion-boundary-smoke` 均 exit 0）。
- **ruff**:本轮改动文件 0 新增错误（既有错误 `loopx/chat_acp.py` F841、`scripts/qualify-doubao-*.py` E402、`tests/control_plane/test_goal_activation.py` F401 均经 HEAD 对照确认为预存）。

## 已知遗留（不在本次范围）

- **`thread_agent_binding.py` 不校验 host_surface 白名单**（只当 compact public-safe token），理论上的既有 registry 可能残留 ark 绑定（本机已确认为无），移除后无法再新建。
- **`benchmark/swe-marathon/runtime/modes/profile_install.py`** 有一份 7-id 技能集的影子副本（独立定义），未随改名更新——不阻塞，但属漂移隐患。
- **两个 fixture 附带修正**已记录:① `agent-onboard-host-loop-activation-smoke.py` 的重复期望值（既有 bug）;② 无其他。
- 移除期间发现 `docs/reference/protocols/host-integration-surface-v0.md` 的 Ark 段是本 fork 中 `runtime_capability_reentry_v0` 契约**唯一**的散文记录;已重新归档保留，勿在后续清理中误删。

## 环境备注

基线对照口径见 015–023。本环境 4 个既有 collection errors（`outbound_guidance`、`refresh_checkpoint_recovery`、`shared_goal_alignment_cli`、`python_ci_workflow`）与既有 failed 集合与上一轮一致。移除后 `--runtime-profile` 合法值为 `codex_cli`/`claude_code`/`generic_cli`/`outer_controller`。
