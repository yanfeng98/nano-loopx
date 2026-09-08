# 019 · 移除 Codex App over SSH 宿主适配器(codex-app-ssh)

- **日期**: 2026-09-08
- **分支**: `260906-dev`
- **背景**: 用户不需要 Codex App over SSH(`codex-app-ssh`),要求完整移除且不破坏
  LoopX 其他功能 —— 尤其 Codex 家族剩余成员(`codex-app`/`codex-cli`)与共享
  visible-goal / scheduler 机制。**本轮为本会话最复杂移除**:codex-app-ssh 拥有
  专属 scheduler 枚举成员(`HostSurface.CODEX_APP_SSH`、
  `SchedulerRuntimeProfile.CODEX_APP_SSH_VISIBLE`),牵出 57+ 文件,且是
  benchmark/swe-marathon 五臂研究的唯一 official treatment 臂(ssh-goal)。
  用户已确认 **benchmark 相关资产完整退役**(照 TraeX 先例 cc200f58)。
  政策沿用:永久移除、文档彻底静默、直提 + op-log。release-readiness/
  update-notes 无 codex-app-ssh changelog 条目;heartbeat 持久值 ValueError
  防护在 015 轮已就位,无需新增。

## 变更清单(~60 文件)

**Scheduler 枚举手术 + import-time 崩溃点(最高风险)**
1. `control_plane/scheduler/execution_context.py`:删 `HostSurface.CODEX_APP_SSH`、
   `SchedulerRuntimeProfile.CODEX_APP_SSH_VISIBLE`、`NATIVE_GOAL_RUNTIME_PROFILES`
   成员、`GUIDED_START_TURN_RUNTIME_PROFILES` 成员(留 `{CODEX_APP_HEARTBEAT}`)、
   `_SCHEDULER_RUNTIME_PROFILE_CONTEXTS` 条目、`_validation_errors`
   (cli_surfaces 成员 + 专属 if 块)、`scheduler_execution_context_for_turn`
   主机 map 行;函数体内 3 个解析点已有 except 防护,未动。
2. `control_plane/scheduler/scheduler_hint.py`(**删枚举后 import 即崩**):
   常量 `CODEX_APP_SSH_GOAL_RUNTIME_KEY` + 6 处引用(unchanged_poll/672 构建/
   888-892/detail/1076/1130)+ `ssh_goal_runtime_action` 参数与两个调用值;
   共享 `CODEX_NATIVE_GOAL_BLOCK_ACTION`/`RESUME_TRIGGER` 保留。
3. `control_plane/heartbeat/host.py`:仅 :44 集合删成员(留 codex_cli);不加防护。
4. 两处手工 `-H` choices:`support_control_heartbeat_registration.py` 与
   `quota_registration.py` 删 `"codex_app_ssh"`。

**行为簇(begin-turn 强制,成套删除)**
5. `control_plane/quota/spend_sources.py`:`visible_goal_turn_reentry_action`
   **整函数删**(该函数只对 app-ssh 生效 —— app-ssh 是唯一允许 begin-turn 的
   visible-goal host;简单去掉 profile 条件会让 codex-cli 也强制 begin-turn 然后
   在 quota_context 校验处报错,故必须整体删除)+ interaction_contract 的 import
   与调用点 + 残留 `SchedulerRuntimeProfile` import。
6. `project_prompt.py`:`render_quota_guard_command` 强制 begin_turn 的 app-ssh
   条件删(两半)。
7. `cli_commands/quota_context.py`:报错文案 →
   `"--begin-turn requires runtime-profile codex_app_heartbeat"`。

**核心 + 家族/帮助面**
8. `host_loop_activation.py` 10 处:binding/SUPPORTED(14→13)/catalog 条目(7 别名
   自动消失)/歧义三列表 → `[codex-app, codex-cli]`/surface key/selection prose/
   heartbeat scope/`_codex_app_ssh_activation`(共享 `_codex_goal_activation`
   保留,唯一存活调用方 = `_codex_cli_activation`)/分发 elif。
9. `agent_onboarding.py`、`bootstrap_command_pack.py`(成对删)、`_host_thread.py`、
   `thread_agent_binding.py`(家族 set 缩为 {codex-app, codex-cli-tui})、
   `cli_commands/slash_commands.py` choices、`slash_command_install.py`(枚举串/
   normalize set/7 处注释列表 → `["codex-cli", "codex-app"]`)、starter help、
   `help_surface.py` 条目、`canary/planner.py` trigger hints。

**benchmark 完整退役(用户确认;经子代理执行,~25 文件)**
10. `benchmark_toolkit/native_codex_profile.py` 整删 + `__init__.py` import/__all__
    清理 + `native_codex_isolation.py` 错误码改名(`native_codex_profile_root_*`
    → `profile_root_*`)+ toolkit README;`benchmark/tests/test_native_codex_profile.py`
    整删;`benchmark/native_codex_goal.py` re-export 清理。
11. `benchmark/swe-marathon/`:modes/profiles.py SSH_GOAL 删(MODES = codex-cli/
    heartbeat + claim 变体)、profile_install.py 重写(原 100% 包装被删模块 → 自含
    install-local.sh 安装,同一 run_mode 契约)、loopx_native_codex.py 重指 +
    `codex_cli` 渲染、codex_loopx_agent.py(默认模式/doctor agent-type →
    codex-cli)、session/run_mode/turn_runner 措辞、scoring 四文件(ARMS 5→4/
    ARM_ROLE 重编号/case_insights 修剪)、data.json 与 case_insights.json 重生成
    (75→60 trials,存活 4 臂字节级一致)、README/RUNTIME.md/SKILL.md/deepswe
    README 净删。
12. `benchmark/widesearch/`:run 脚本重指共享 profile_install + 内联 env 帮助,
    测试 monkeypatch 目标更新。
13. 站点 `apps/presentation/site/`:SweMarathonBrief.tsx 与 swe-marathon-copy.json
    删 ssh-goal 臂行/armOrder/labels/metrics 句(75→60 trials,四臂保留)。
14. `examples/benchmark-native-goal-installed-profile-smoke.py` 整删(整个示例
    驱动被删模块,canary 按 glob 发现)。
15. `tests/capabilities/test_native_codex_isolation.py`:错误码断言更新为改名后值。

**测试(删专属/删行/换键三类,~15 文件)**
16. 整删:`tests/test_visible_goal_terminal_settlement.py`(30 行全 app-ssh)、
    compact projection 两个 app-ssh ambient-thread CLI 测试(codex-app twin 已存在)、
    `test_quota_settlement.py` 三个 app-ssh 专属测试、
    `test_quota_settlement_cli.py` **7 个整测试**(1528-1584/1586-1645/1692-1778/
    1780-1838/1907-2018/2019-2068/2729-2779 —— 均以 ssh profile + begin-turn
    驱动已被产品删除的 unbound visible-goal guided-turn 行为,共 479 行)。
17. 删行/参数化:`test_host_loop_activation.py`(6 处参数化行/条目 + 歧义断言 →
    `[codex-app, codex-cli]` + 测试名改;goal-host 参数化 ssh 行 → `codex_cli`
    保持覆盖)、`test_host_parity_smoke.py`(歧义 2 成员/binding 行)、
    `test_scheduler_execution_context.py`(VALID_COMBINATIONS/FIRST_CLASS/
    monitor 参数化行)、`test_quota_settlement_cli.py` 两参数化 → `["codex-app"]`
    + 文案断言;example smokes 两文件(歧义/映射/packet 段/onboarding 段 83 行/
    RUNTIME_KEYS + cold-path 断言)。
18. fixture 换键:`test_onboarding_model_behavior_qualification.py`
    (017 轮换到 app-ssh,再换 → `codex-cli`/`codex_cli_visible_goal_mode`)、
    `test_thread_agent_binding.py` → codex-app、`test_attached_session_broker.py`
    与 `test_attached_session_cli.py` → codex-app。

**文档彻底静默净删(10 文件)**
19. README host 表行;getting-started(枚举 + SSH 说明句);newcomer(成员 + 句);
    loopx-goal-command-v0(激活条目/歧义理由/家族句 → "Codex CLI 与 Ark"/
    矩阵行 → "Codex CLI"/专属段整删;**TraeX 退役说明保留**);
    codex-app-host-command-registry-v0(5 处:CODEX_THREAD_ID 句/家族搜索集/
    非猜测列表 + 定义句/权限句/CLI 示例行);book ch02 矩阵行 + prose;
    runtime-connector-catalog.md `codex_app_ssh_goal` 行(与代码同 commit;
    host-mode-plan smoke 校验 emitted ids 存在于 catalog —— 删后无代码再 emit);
    quota-allocation.md 6 处(JSON 两行/contains 成员/三段散文);man/loopx.1 两条;
    skills/loopx-project/SKILL.md 整段 + loopx-self-repair repair-patterns 两行。

**刻意保留**:operation-logs/017 与 000-INDEX 叙述(历史,017 当时称其为存活成员,
被本轮历史性取代,不改写);TraeX 退役说明;release-readiness 通用 Codex 行。

## 验证

0. **对抗式自查(提交后复查,未发现问题、无需修复)**:逐项复核 ——
   ① `visible_goal_turn_reentry_action` 从产品与其唯一调用方
   (interaction_contract)import/调用点彻底消失;② TraeX 退役说明完好(line 38);
   ③ benchmark 语义:profile_install.py 重写自洽且 host-neutral(install-local.sh
   + skill readback 校验,契约 install/inspect/env/receipt 完整)、data.json
   n_trials=60/arms=4、scoring ARMS 四元组一致、case_insights 有效,scoring 16 +
   widesearch 11 + native_codex_goal 17 passed;④ host_loop_activation diff
   39 行纯删除(+ 行仅为歧义列表/散文改写);⑤ 扩展残留扫描(含中文措辞变体
   "SSH 上的 Codex/通过 SSH 附加/附着到远程" 等,排除 op-log)= 0;
   ⑥ 平价 smoke 全绿:agent-onboard、quota-scheduler-hint-compaction、
   host-mode-plan(catalog 行删除与 emitted ids 一致)、
   codex-app-host-command-registry(协议文档净删后 JSON 断言仍绿);
   ⑦ isolation + scheduler context 155 passed;⑧ 工作树干净、commit 含全部
   75 路径、`git diff --check` 干净。
5. **全量 + 基线对照(决定性)**:最终树整树排除已知预存收集 error 后
   `15 failed / 5889 passed / 25 skipped`;15 个失败与 018 轮基线
   (`a0b2963a`) 环境失败文件**逐一相同**(fleet_health ×3、sonarcloud ×3、
   license ×2、registry_git_probe ×2、retained_cases ×2、lark ×1、
   pr_program ×1、repository_change_window ×1)。passed 差 5927→5889 = **38**,
   与 `pytest --collect-only` 基线对照(5967 vs 5929 收集项,基线 worktree
   `a0b2963a`)完全一致 —— 38 项全为本次删除的测试(7 个整函数 479 行 +
   参数化行 + 整文件),零意外丢失。首轮 16 failed 中的 isolation 失败为
   子代理错误码改名与测试同步的时序竞态,断言更新后单跑 4 passed、终跑消失。

1. 残留 grep(全类型,排除 git-ignored 与 op-log):产品代码、文档、benchmark、
   站点、skills、man **0 残留**(含中文措辞变体与 error-code 改名断言同步)。
2. `compileall` 0 失败;显式导入全部改动模块 0 失败(import-time 崩溃点
   scheduler_hint 已解除)。
3. 降级路径(实测):`uses_native_goal_host_loop("codex_app_ssh_goal")` → False
   (不崩,走既有 try/except);`scheduler_execution_context_for_runtime_profile`
   与 `_for_turn("codex-app-ssh")` → explicit unsupported;别名
   (`codex-app-ssh`/`codex_app_ssh`/`codex ssh`/`codex-app-remote`)全部
   AgentTypeError;兄弟 codex-app/codex-cli packet 正常(共享构建器)。
4. 聚焦:409 passed(10 个改动测试文件)+ example smokes 两文件 exit=0 +
   isolation 4 passed;ruff 改动文件全过(8 个 F401 自动清理);`git diff --check` 干净。
5. 全量 + 基线对照:整树排除已知预存收集 error;首轮 16 failed(15 基线 +
   1 个 isolation 断言时序失败 —— 子代理改名与测试同步的竞态,修复后单跑
   4 passed),已在最终树重跑全量。
6. benchmark 子代理独立验证:compileall/imports/scoring 16 + widesearch 11 +
   native_codex_goal 17 passed;JSON 有效;站点 TSX 纯删除。

## 环境备注

- 同 015-018:TS Effect runtime 与 `.github/` 缺失、`tests.*` 整树收集模式为
  预存失败源。
- `_build_viz.py` 导入即读 `viz/data.json`(checkout 缺失)为预存脚本模块行为,
  与本次无关。
- 本次改动按计划直接提交到 `260906-dev`。
