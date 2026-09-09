# 020 · 移除 Codex App 桌面宿主接缝（codex-app 心跳宿主）

- **日期**: 2026-09-08
- **分支**: `260906-dev`
- **背景**: 用户不需要 Codex App（OpenAI 桌面 Codex 应用）作为 LoopX 宿主，要求完整移除且不破坏其他功能。这是继 019（Codex App over SSH 适配器，75 文件）之后的同类完整宿主移除，但目标改为桌面宿主本身。**用户已确认**：(1) 范围 = 仅桌面宿主 seam（HostSurface `codex_app`、`codex_app_heartbeat` runtime profile、心跳自动化、`--codex-app` 旗标族、host command registry、`$CODEX_HOME` App 集成），**保留** Codex CLI 全部、`codex app-server` 传输（codex CLI 子命令；dashboard chat 后端 `codex_app_server` adapter、swe-marathon plain/goal/codex-cli 三臂无头驱动、deepswe/widesearch 依赖它，未动）、docs/archive|plans|update-notes、deprecate/、packages/（含 provider-routing，其 RUNBOOK 的 "SSH host Codex App Server" 是它自己的功能故事）；(2) `bootstrap --codex-app-heartbeat ask|yes|no` 旗标族**整体移除**（不重命名）。政策沿用：永久移除、文档彻底静默、直提 + op-log、全量基线对照。

## 变更清单（~150 文件）

**Scheduler 枚举手术 + blob 改名（最高风险，核心决策：`scheduler_hint.codex_app` 改名而不是删除）**
1. `control_plane/scheduler/execution_context.py`:删 `HostSurface.CODEX_APP`、`SchedulerRuntimeProfile.CODEX_APP_HEARTBEAT`、`GUIDED_START_TURN_RUNTIME_PROFILES`（删后为空）、contexts 条目、`_validation_errors` codex_app 块、渲染分支；applicability 重闸为 `codex_cli_applicable = (local_scheduler, host_automation, hosted_automation)`（该三元组本已合法），投影字段 `codex_app_applicability` → `codex_cli_applicability`；completion_reason 文案更新。
2. `control_plane/scheduler/scheduler_hint.py`:blob key `scheduler_hint.codex_app` → `scheduler_hint.codex_cli`（被 codex_cli_scheduler/probe_markdown/TS transport/execution_context continuation/quota_markdown/diagnose/ready_score 消费，存活路径必须保留改名而非硬删）；常量/kwarg/schema-version/函数名成对改名（`build_codex_app_scheduler_{ack,failure}_hint` → `build_codex_cli_*`、`codex_app_current_rrule`→`codex_cli_current_rrule` 等）；**fallback hint 整套删除**（`build_codex_app_scheduler_fallback_hint`、`build_projected_codex_app_automation_id`、`codex_app_automation_id` kwarg 链、`loopx-apply-rrule`）；`--codex-app-current-rrule` → **`--observed-host-rrule`**（failure-cache 按 `(target_rrule, observed_host_rrule)` 去重，硬删会静默降级 backoff）。
3. `control_plane/scheduler/state.py` + TS `state_store.ts`/`heartbeat_commit.ts`/`heartbeat_followup.ts`/`heartbeat_followup_cli.ts`/`quota/turn_envelope.ts`/`effect_program.ts`:常量 `CODEX_CLI_SURFACE`/`CODEX_CLI_STATEFUL_BACKOFF_STATE_KEY`、TS 字面默认值、`--observed-host-rrule`、`--codex-app` 布尔旗标删除。
4. `quota.py`/`scheduler_ack.py`/`should_run*.py`/`live_decision.py`:kwarg 链改名 + automation_id 参数删除；fallback 路由分支删除；ack/failure 分支保留。
5. `effect_program.py`/`settlement.py`:`build_codex_app_settlement_plan` 整删（含 re-export、`accountable_settlement.py` 分支、`interaction_contract.py` `heartbeat_turn_receipt_enabled` 谓词）；`presets.py` 两处 `--runtime-profile codex_app_heartbeat` → `generic_cli`。
6. `--begin-turn` 整套删除:flag、`quota_context.py`/`quota_request.py`/`bootstrap_command_pack.py`/`project_prompt.py`/`slot_accounting.py`/`slash_command_install.py` 校验与文案、`render_quota_guard_command` 参数。
7. `bootstrap.py` 旗标族:常量/`normalize_codex_app_heartbeat`/`heartbeat_opt_in_required`/`host_loop_activation_required`/`heartbeat_status`/`heartbeat_instruction` 与 ~30 处参数/载荷字段删除（`host_loop_activation_required` 载荷字段保留为 `bool(onboarding_scan)`；`normalize_onboarding_connection_validation` 复位）；`bootstrap_connect.py`/`chat_actions.py:875`/两个 demo 去掉 kwarg。
8. 宿主目录:`host_loop_activation.py`（SUPPORTED 14→13、catalog 条目、歧义 → `["codex-cli"]`、surface map 删 codex-app/chat-box、默认 → codex-cli、`_codex_app_activation` + 分发删）；`thread_agent_binding`/`_host_thread` 家族 → `{codex-cli-tui}`；`agent_onboarding`/`slash_command_install`/`slash_commands`/`start_contract`/`bootstrap_command_pack` 家族与文案；`upgrade.py` `load_codex_app_automation_manifest` + `resolve_codex_app_automation_rrule` + TOML/infer 助手整删，`load_installed_manifest(None)` → unavailable 响应（显式 `--installed-manifest` 唯一来源），字面量 → `codex_cli`；`registry_admin`/`support_control`/`support_control_heartbeat_registration` 旗标与字面量；`control_plane/heartbeat/host.py` 允许集 → `{generic_cli}`；`heartbeat/task_body.py`（rules.py 三规则去掉 fallback 措辞）；`help_surface`/`man/loopx.1`/`project_prompt.py`/`canary/planner.py`/`codex_cli_probe.py`/`presets.py`;`chat_actions.py` `heartbeat.bind` action + `_heartbeat_gate` + goal.create heartbeat 参数整删（`chat_action_store` 同步）。

**benchmark（仅认领模式退役；app-server 传输保留）**
9. `swe-marathon/runtime/modes/profiles.py` `HEARTBEAT_CLAIM_APP` Mode + resolver claim 分支删；`run_mode.py` `--claim-codex-app` 删；`session.py` bootstrap `--codex-app-heartbeat no` 删 + `scheduler_obligations` 读 `codex_cli`；`agents/codex_loopx_agent.py` `WEN_CLAIM_CODEX_APP`/`--codex-app-heartbeat` 门禁删；SKILL.md 披露改写。`data.json`/scoring 不动（claim 模式不在四臂内）。

**脚本/文档/站点/技能**
10. 删 `scripts/codex_app_apply_rrule.py` + `scripts/loopx-apply-rrule` + `install-local.sh` 引用。
11. 文档净删 7 文件: `docs/product/runtimes/codex-app/`（2）、`docs/book/chapters/06-codex-app.md` + `docs/book/mkdocs.zh.yaml` 导航行、`docs/reference/protocols/codex-app-host-command-registry-v0.md`、`docs/heartbeat-automation-prompt.md` + `mkdocs.yaml` 导航行、`docs/guides/codex-multi-app-best-practices.md`；`docs/reference/protocols/README.md`/`docs/product/runtimes/README.md`/`docs/product/README.md` 索引行。外科编辑 ~45 个文档/技能/站点文件（README 表格行、getting-started/newcomer、codex-cli-automation-driver 基线矩阵改写、book 02/03/04/05/07/11/00/index/appendix/state-substrate/work-graph、quota-allocation 8 处、status-data-contract、interface-budget、loopx-goal-command/turn/plugin-plan/host-integration-surface/model-behavior-qualification/evidence-ledger/effect-interpreter-packet/dashboard-budget-governance、operations/new-project-codex-prompt、rule-seam-map、state-machine 心跳状态机三行 → HostLoopRequired/ManualLoopOnly、cross-runtime-demo、controls/personal-workspace/periodic_report、CONTRIBUTING、control-plane-board.svg、swe-marathon-copy.json、dashboard README、skills/loopx-project/SKILL.md、skills/loopx-self-repair/*）。按先例保留:docs/development、docs/archive/plans/update-notes、docs/architecture*/state-interaction-model、roadmaps、release-readiness、docs/guides/README.md:17（provider-routing 包）。

**附加修正（smoke/全量对照驱动发现的产品正确性修复）**
- `upgrade.load_installed_manifest` 接受 `str`（CLI `--installed-manifest` 为字符串；显式 manifest 路径因此可解析——原 App 自动发现路径掩盖了该缺陷）。
- `heartbeat/task_body.py` 两个薄模板把 `safe_bypass_allowed=true -> one validated step` 前置到首个 `should_run=false` 之前：codex_cli 渲染的 thin body 此前触发 `should_run_false_before_safe_bypass` policy warning（该 warning 在 App profile 渲染下不存在；移除后默认 codex_cli 渲染暴露），upgrade-plan 的默认晋升门禁因此将把新生成提示标记为需重生成。
- `cli_commands/quota.py` 恢复 `_requested_quota_action_todo_id`：显式 hosted 上下文（-H local_scheduler -O host_automation -M hosted_automation）把 `--todo-id` 视为同一轮显式动作选择（继承 App 别名语义）；其余 host surface 保持 `--todo-id` 仅为结算目标。
- `work_items/accountable_settlement.py` + interaction_contract 调用点：显式 hosted 上下文重新走 bounded turn-scoped 结算计划（原 `CODEX_APP_HEARTBEAT` 分支语义迁移；此前 profile=None 导致 settlement_plan/replan_settlement_contract 缺失）。
- `scheduler_hint.py` ack/failure hint 的 CLI args 中 `-A` 发射改为显式 `-H/-O/-M` 三分组（旗标已删；保留 `-A` 会让生成的 ack/fail 命令对 CLI 立即 argparse 失败）。
- `canary/quality_surface_catalog.py` scheduler-ack-route 单元契约引用删除两个已删 TS 测试文件（quality drift 门禁因此失败）。
- `tests/fixtures/.../public_safe_decision_replay_v0.json` 三 case 的 `expected`（scheduler_* 字段）按通用 profile 语义重生成（原 App profile 值）。
- `loopx/control_plane/testing/*` 5 个行为 actor 与 `tests/` 内 4 处 thread-bind/host-surface fixture 规范化到 `codex-cli-tui`/显式 hosted 上下文。

**测试/example smoke**
12. 整删 4 测试文件（`test_codex_app_apply_rrule.py`、`test_scheduler_native_launcher.py` + canary quality_surface_catalog 条目、TS `scheduler_heartbeat_followup_cli.test.ts`、`scheduler_heartbeat_commit_cli.test.ts`）+ 3 example smoke（`codex-app-host-command-registry-smoke`、`codex-app-control-plane-hook-cache-smoke`、`codex-app-thread-agent-identity-smoke`）；tsconfig include 两行删。
13. ~40 测试文件迁移:app 专属整函数删（`test_quota_settlement(_cli)` 的 codex_app settlement/begin-turn 测试、`test_codex_app_*` 等）；`scheduler_execution_context_for_runtime_profile("codex_app_heartbeat")` → 显式 hosted 上下文 dict/`HOSTED_SCHEDULER_CONTEXT`；fixture 换键 `codex_app`→`codex_cli`/`codex-cli-tui`/`generic_cli`；`--codex-app` → `-H local_scheduler -O host_automation -M hosted_automation` 三分组（11+ 个测试/example）；两个 JSON fixture（replay/state-store characterization）换键 + 两个导出的哈希字面量（`codex_cli-64d91e65…/b514e306…`）；host_parity 计数 13→12 级重测。
14. ~46 example smoke 迁移:同款换键 + 删除 `heartbeat-automation-prompt.md` 依赖（`heartbeat_prompt_fixtures` DOC 删、`heartbeat-prompt-smoke` doc 断言改指 SKILL/getting-started、showcase-html-pages doc 路径改 quota-allocation、docs-governance 列表行删）；`upgrade-plan-smoke` 全面改写为显式 `--installed-manifest` JSON 流（App automation TOML 写器 → `write_installed_manifest`，`installed_manifest_source` 断言语义改为 None）；`install-local-smoke`/`cli-help-manpage-smoke`/`readme-demo-surface-smoke`/`bootstrap-command-pack-smoke`/`agent-onboard-host-loop-activation-smoke` 等按新输出修；浏览器 smoke（personal-workspace）删 heartbeat.bind 流（mock 分支 + 英文/中文 heartbeat 场景 + gate 文案）；chat-actions smoke 删 heartbeat.bind 预览/门禁/生命周期。

## 验证

- **基线**: c09b1b4a 净土 worktree `/tmp/loopx-baseline`（`git worktree add`；该树 pytest 导入走可编辑安装路径解析到基线代码）。`pytest --collect-only -q`: **5981 collected + 4 预存 collection errors**（outbound_guidance、refresh_checkpoint_recovery、shared_goal_alignment_cli、python_ci_workflow(.github 缺失)）。
- **全量基线对照**: 本环境 TS Effect runtime 不可用（node 子进程 ConnectionRefused；019 环境备注同源），故基线全量（`--continue-on-collection-errors`）为 **326 failed / 5624 passed / 25 skipped / 10 errors**（330 个失败文件与运行时记录：turn_driver×57、turn_executor×52、loop_controller×41 … 全为 EffectRuntimeStartupError 链）。npm `test:control-plane`（不经受管 socket）**新树 612 pass / 1 fail（postgresql 集成，无 PG 环境）**，基线（c09b1b4a 净土）**624 pass / 1 fail** —— 差 12 = 两个删除的 CLI 子测试文件；`typecheck:control-plane` 因 node_modules 缺失不可运行（tsc 未装）。
- **新树**: `pytest --collect-only -q`: **5872 collected + 同 4 预存 errors**（collect 差 109 = 删除节点数）。聚焦集群（修复收敛后终态）:scheduler 核心 + host_loop_activation/parity/goal_activation/public_safe_replay/quality_catalog/quota_settlement(_cli)/effect_program/m6/budget/turn_envelope/thread_binding/onboarding/slash_install/effect_interpreter 等 **488 passed / 1 failed（ack_decision_table 断言语义在 hint 发射 -H/-O/-M 后同步，随后 6/6 通过）**;6 个行为 actor 测试文件 **94 passed**;upgrade-plan/host-integration-plugin-plan 等纯 smoke 通过（baseline catalog/docs-governance smoke 因 `.github` 缺失同为环境失败）。偶发跨 run 翻转（如 actor/quota_settlement_cli 在一轮 17 failed、另一轮全绿）与 TS Effect runtime 服务瞬时可用性一致:直接探针 `effect_runtime_result('rrule_for_minutes',...)` 在环境失败态必败、基线同态。降级输入实测: `scheduler_execution_context_for_runtime_profile("codex_app_heartbeat")` → unsupported；旧 `host_surface:"codex_app"` → ok=False；`normalize_agent_type("codex-app"/"codex app"/"chat-box"/"codex-desktop")` → AgentTypeError；旧 `scheduler_hint.codex_app` 载荷 → 默认 cadence 不崩。
- **残留 grep**（排除 leave-list:codex_app_server、docs/development|archive|plans|update-notes|architecture、state-interaction-model、roadmaps、release-readiness、packages/provider-routing、operation-logs、deprecate、.git）: **0**（基准串 `codex[_-]app`(非 _server)、`Codex App`、`codex_app_heartbeat`、`--codex-app-heartbeat`、`CODEX_APP_`、`--begin-turn`、`loopx-apply-rrule`、`heartbeat-automation-prompt`、`codex-app-host-command-registry`、`heartbeat.bind`）。
- **ruff**: 新树 59 errors vs 基线 70（均为先例内 E402/sys.path 风格与既有 F841；两处 F821 已在提交前修复: bootstrap `normalize_onboarding_connection_validation`、upgrade-plan-smoke `write_registered_fixture` —— 均从基线恢复）。
- **compileall**: loopx/scripts/benchmark/tests/examples/demo 0 编译错误。

## 环境备注

TS Effect runtime 服务端在本环境不可用（`effect_runtime.py` spawn 的 node 服务写入 info 后端口拒绝连接；npm test 直跑通过）——**与 019 相同**；全量对照以"失败文件集合一致"为准。`.github/` 缺失导致 `test_python_ci_workflow.py` collection error（预存）。`typecheck:control-plane` 需要 node_modules（未安装，非本次回归）。

## 复查修正（97887786）

用户要求复查后追加的修复：dashboard 前端与后端契约同步（router/chat.ts/model.ts/page.tsx/context-drawer/schedule-row/frontstage 移除 heartbeat.bind 能力、意图路由、"设置 Heartbeat" 按钮与 goal.create 的 heartbeat 参数——否则前端会向后端已删除的动作发请求、Goal 创建因 `_allowed_parameters` 语义必然报错；smoke 断言按新语义重写，router smoke 实测通过）；`starter_bootstrap_registration` 的 `--host-surface` 默认值由与 choices 矛盾的 codex-cli 改为 codex-cli-tui。

## 复查修正 2（9fcac2ca：tsc 化修复 + bundle 重建）

用户第二轮复查要求后:97887786 的 page.tsx 替换边界曾损坏组件结构
(tsc 全量 TS2451/TS2304 大面积报错)。以 2f9a91f8 干净版为基重做
personal-workspace-page.tsx 心跳移除(每步唯一锚点),并**首次完成前端
tsc --noEmit 全量 0 error 验证**(此前所有前端修改仅靠静态审查)。
dashboard smoke:personal-workspace-router/chat-route/goal-order/
presentation-surface-schema/frontstage-operator-state 通过;home-route/
frontstage-route/action-packet 三 smoke 的失败断言经 c09b1b4a 源码比对
为基线即过时项(buildPersonalHomeModel 第三参、README signal strip),
非本任务回归。重建内置 chat bundle(vite.chat.config.ts):新入口
index-CAwwD9nG.js 心跳绑定 0 命中,index.html 指向新入口;旧哈希资产
按 emptyOutDir:false 既有设计保留(防在飞页面白屏)。

## 复查 e2e 冒烟（无 runtime 路径全绿）

bootstrap(real/dry)/connect/status/agent-onboard(list+codex-cli)/preset(list;
0 codex_app_heartbeat,10 generic_cli)/heartbeat-prompt(fail-closed→注册后
ok)/start-goal(host_surface_selection gate)/upgrade-plan(--installed-manifest
CLI str 路径 ok)/bind-agent-thread 全部 EXIT 0;status --project 与基线同拒绝;
cli-help-manpage-smoke 基线同断言失败(中文 .1 vs 英文 renderer,预存)。

## 文件统计

~255 修改 + 15 删除 + 1 新增 + 复查修正 10 文件（`git diff --stat`: 245 文件, +1600/−6800 量级）。
