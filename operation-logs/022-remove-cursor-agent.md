# 022 · 移除 Cursor 宿主（cursor-agent skill-facade）

- **日期**: 2026-09-09
- **分支**: `260906-dev`
- **背景**: 用户不需要 Cursor 作为 LoopX 宿主，要求完整移除且不破坏其他功能。Cursor 走 **skill-facade** 表面(`cursor` 安装面、`CURSOR_HOME/skills` 技能写入 + `CURSOR_HOME/mcp.json` LoopX MCP server 注册),agent_type `cursor-agent`、表面 `cursor`/`cursor-agent`/`cursor-cli`。与 021 同构,政策沿用(016/018):永久移除、纯删除优先、零残留、op-log + 基线对照。**关键差异**:gemini 移除时 cursor-agent 仍是 `_skill_facade_cli_activation` / `test_cursor_host_surfaces.py` 的使用者,共享 helper 与测试文件保留;本次 cursor-agent 是**最后一个** skill-facade 宿主,因此 `_skill_facade_cli_activation` 整函数删除,`tests/test_cursor_host_surfaces.py` + `tests/host_surface_cli_probes.py` 整文件删除;共享 `install_skill_facade`(slash_command_files.py)保留(OpenCode surface 仍用)。

## 变更清单(27 文件,+39/−935;另 1 新增 op-log;2 整文件删除)

**宿主目录(核心)**
1. `host_loop_activation.py` 8 个删除块:`scheduler_command_binding_for_agent_type` 行、`SUPPORTED_AGENT_TYPES` 行(11→10)、`AGENT_TYPE_CATALOG["cursor-agent"]` 整条(6 个别名随 `AGENT_TYPE_ALIASES` 派生自动消失;`build_agent_type_catalog`/doctor/`agent-onboard` 等消费方自适配)、`HOST_SURFACE_TO_AGENT_TYPE` 两行(`cursor-agent`/`cursor`)、`_heartbeat_commands` scope 行、`_skill_facade_cli_activation` 整函数(本次必删:最后使用者即 `_cursor_agent_activation`)、`_cursor_agent_activation` 整函数、分发 `elif` 分支。

**安装器/表面管线**
2. `slash_command_install.py` ~13 块:instruction 串 token、`_cursor_home()` 助手、`_normalize_surfaces` 分支、`CURSOR_MCP_KEY`/`CURSOR_MCP_MARKER_NAME`/`CURSOR_MCP_MARKER_SCHEMA_VERSION` 常量、`_loopx_mcp_command()`(唯一调用方 `_merge_cursor_mcp`,连带其 `claude_install` 函数体 import)、`_cursor_mcp_marker_path`+`_read_cursor_mcp_marker`、`_write_json_atomic`(所有调用方在 `_merge_cursor_mcp` 内)、`_merge_cursor_mcp` 整函数、`install_slash_commands` 的 `cursor_home` kw-only 参数(调用点全部在范围内)、`cursor_root` 行、`if "cursor" in effective_surfaces` 整块、summary 两键、notes 串、render_markdown 两行;连带删 `contextlib`/`sys`/`tempfile` 三个未使用 import。`claude_goal_mode/scripts/install.py` 的 `provision_mcp_python`/`MCP_PROBE` 保留(Claude adapter 自己在用),仅注释示例改通用表述。
3. `cli_commands/slash_commands.py` 3 块:`--surface` choices 两项、help 文案(`pi` is opt-in)、`--cursor-home` 参数块 + pass-through。

**激活/合约**
4. `agent_onboarding.py` 3 块、`bootstrap_command_pack.py` 2 块(`START_GOAL_HOST_SURFACES` 11→10,`--host-surface` argparse choices 派生收缩、`host_descriptions` 行)、`control_plane/goals/start_contract.py` 1 行、`slash_commands.py` 1 行。

**测试(2 删除 + 4 编辑)**
5. `tests/test_cursor_host_surfaces.py` + `tests/host_surface_cli_probes.py` 整文件删除(全库零其他引用;后者的唯一 import 方即前者)。
6. `test_host_parity_smoke.py` 5 处:`"cursor-agent" in types`、`>= 11`→`>= 10` 唯一硬计数、surface mapping 参数行删、runtime profile 行删、generic list 收缩。
7. `test_slash_command_install.py` 删除文件尾部整段 cursor 专项测试(11 个测试 + `_stub_mcp_command` 助手;opt-in 语义已有 `test_pi_install_does_not_touch_default_all_surfaces` 覆盖);连带删未使用 `json`/`from loopx import slash_command_install` 导入。
8. `test_deepresearch_command.py` skill-facade 代表面 cursor → opencode(仅存的 `_install_skill_facade` surface)。
9. `test_start_goal_compact_projection.py` 精确 gate choices 列表删行。

**文档/示例/操作日志**
10. README 3 行(副标题/图/宿主表格)、`examples/public_entry/readme-demo-surface-smoke.py`(硬编码 README 校验行同步 + 附带修正,见「复查」)。
11. docs 10 文件枚举去 Cursor:index、getting-started×2、minimal-custom-runtime-example、frontend-surface、session-runtime-loopx-projection-v0、contributor-tasks×2、saas-opportunity-assessment×2、long-horizon-harness-benchmark-research-program-v0、server-client-product-shape、naming-decision-packet×2。
12. 新增 `operation-logs/022-remove-cursor-agent.md` + `000-INDEX.md` 行 022。

## 验证

- **基线(同环境顺序复测)**:当前 HEAD(干净)**5916 collected + 4 预存 collection errors**(outbound_guidance、refresh_checkpoint_recovery、shared_goal_alignment_cli、python_ci_workflow(.github 缺失))。
- **新树**:5916 → **5897**(差 19 = 删文件 6+11 测试 + 1 参数化行 + 1 catalog 派生参数化收缩),同 4 errors。
- **聚焦 pytest 全绿 193**:`test_host_parity_smoke.py`、`test_slash_command_install.py`(25)、`test_deepresearch_command.py`、`test_start_goal_compact_projection.py`、`test_skill_delivery_parity.py`、`test_agent_onboarding_unconnected_project.py`、`test_host_loop_runtime_parity.py`、`test_thread_agent_binding.py`、`test_agent_onboarding_pi_host.py`;`compileall` 0 错误;`ruff` 全部触碰文件通过(examples/* smoke 等 53 项为未触碰文件的预存告警)。
- **残留 grep 0**:`grep -rniE "cursor[-_ ]agent|cursor-cli|CURSOR_HOME|surface[ -]cursor|cursor_skills|cursor_mcp"`(排除 `.git/ operation-logs/ deprecate/ docs/research/ __pycache__/ node_modules/ loopx.egg-info/`)空。
- **降级实测**:`normalize_agent_type("cursor"/"cursor-agent"/"cursor-cli")`/`agent_type_for_host_surface("cursor")` → AgentTypeError(10 suggestions);`--surface` choices 收缩为 `{all,codex,codex-cli,claude-code,opencode,pi}`,`--surface cursor`/`--cursor-home`/`--host-surface cursor-agent` 全部 argparse 拒绝;`install_slash_commands(cursor_home=…)` → TypeError;`surfaces=["cursor"]`(execute=True 亦)0 installed、无写入无副作用(未知表面透传为既有设计,同 021);`--surface all` dry-run 仍 `["codex","claude-code","opencode"]`;`_cursor_home`/`_cursor_agent_activation`/`_skill_facade_cli_activation`/`_merge_cursor_mcp`/`_loopx_mcp_command`/`_write_json_atomic` 均不存在;`agent-onboard --list-agent-types` 10 项;`doctor --agent-type claude-code` 正常。
- `npm run test:control-plane`:613 tests / 612 pass / 1 fail —— 与 021 基线 **612+1 不变**(唯一失败 = `postgresql_authority_store.integration.test.ts`,需真实 PostgreSQL 服务,本环境预存;TS 侧仅数据游标字段,无宿主引用)。

## 复查(第二轮)

- **全量 diff 审读**:27 文件 +39/−935(含附带修正注释),删除为主体;删除函数无残留调用方(`_loopx_mcp_command`/`_write_json_atomic`/`_merge_cursor_mcp` 等全库零引用);`contextlib`/`sys`/`tempfile` 随所属函数一并清理;`tests/test_slash_command_install.py` 连带清掉因删测试而未使用的 `json`/`from loopx import slash_command_install`(ruff F401,HEAD 版无此告警)。
- **扩大对照(导入被改模块的全部 27 个测试文件)**:逐文件隔离重跑,**590 passed + 1 skipped 全绿**(含 `test_start_goal_compact_projection` 56、`test_loopx_turn_driver` 61、`test_turn_envelope` 30、`test_host_loop_activation` 36、`test_retired_host_interfaces` 12、`test_deepresearch_command` 24、`test_ark_managed_agent_host` 13、capabilities/control_plane model-behavior 批次等)。此前的批次内失败经定位全部为 **TS Effect runtime 间歇不可用**(019-021 同源环境问题):不可用窗口内以 `git stash` 回到 HEAD 同批重跑,失败集合一致(交集 176;唯一差集 `test_turn_envelope[monitor_quiet_skip]` 在 HEAD 单独跑同样失败 → 预存);runtime 恢复后同一批全绿。
- **CLI 面复核**:`loopx slash-commands` catalog、`slash-commands --help`、`start-goal --host-surface` choices(10 项)、`agent-onboard --help` 均零 cursor;`--surface` choices 收缩正确;10 个受支持 agent type 全部 `loopx doctor --agent-type X` ok=True;guided `start-goal` 预览 gate 恰 10 项;`--surface pi --dry-run` summary 无 cursor 键。最终宿主面批次 **235 passed**(并入 `test_host_loop_activation`/`test_retired_host_interfaces`)。
- **残留 grep 覆盖面**:除既有排除项外,补查 `man/`、`skills/`、`apps/`、`demo/`、`benchmark/`、`regression/`、`packages/`、`docs/` —— 均 0。
- **附带修正(020/021 同类做法)**:`examples/public_entry/readme-demo-surface-smoke.py`(canary default tier)自 `c8850910`(fork README 精简)起一直红灯(HEAD 与本树同样失败,非本次改动引入)。该提交有意删除「学习 LoopX/真实项目中的使用/更多可检查入口」小节、`<a id="快速开始">` 锚点与跨 runtime 链接,smoke 期望未同步。本次把期望对齐到现行 README(保留守卫意图):去跨 runtime 链接期望(docs 索引断言仍在)、`200+ 小时自然时长` → `200+ 小时自然时间窗口`、免责声明两处改为现行措辞「不代表连续算力执行、独立复现、生产结果」、去 `快速开始` 锚点、Auto Research 分节分隔符 `### 真实项目中的使用` → `## 试用 LoopX`(原分隔符已不存在,切片会吞掉整个 README 后半段导致 `脱敏` 负断言误报);并加注释记录对齐依据。实测 `readme-demo-surface-smoke ok`(exit 0)、相邻 `cross-runtime-impl-review-demo-smoke ok`、ruff 通过、`loopx check` 仍全清。

- **canary 套件(仓库自有治理工具)**:`loopx canary smoke-suite --from-git-diff --git-diff-base HEAD` 按本 diff 选中 **18 项,14 通过**;4 项失败**全部在 HEAD(stash 后)复现,非本次改动引入**,根因均为 fork 与上游 smoke 的既有漂移:① `install-local-smoke.py` 断言 `loopx` fallback help 含 "outer host turn identity"(该短语全库已不存在,fork 重写了帮助文案);② `codex-cli-packaged-install-smoke.py` 打包含 `LICENSE`,而 fork 已删 LICENSE/NOTICE(c8850910);③ `global-manager-command-protocol-smoke.py` 缺 contract 文案 'Only `/loop-goal-summary` remains host-only';④ `onboarding-no-scan-projection-smoke.py` 向 `connect` 传已不存在的 positional `no` → argparse exit 2。其中与本次改动直接相关的检查(maintainability ratchet、CLI output budget、CLI command contract、slash-command catalog、install/update、product-entry、benchmark boundary)全部通过。以上 4 项留待单独处理,不属于本次移除范围。

## 环境备注

TS Effect runtime 服务端在本环境间歇不可用(与 019-021 同源,全量对照以失败文件集合一致为准);`.github/` 缺失致 `test_python_ci_workflow.py` collection error(预存);`postgresql_authority_store.integration.test.ts` 需真实 PostgreSQL(预存)。operation-logs 016-018/021 中 cursor 字串为当时上下文,保留;`deprecate/benchmark-legacy` 与 `docs/research` 无宿主引用,未涉及。
