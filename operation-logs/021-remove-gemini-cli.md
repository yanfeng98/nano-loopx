# 021 · 移除 Gemini CLI 宿主（gemini-cli skill-facade）

- **日期**: 2026-09-09
- **分支**: `260906-dev`
- **背景**: 用户不需要 Gemini CLI 作为 LoopX 宿主，要求完整移除且不破坏其他功能。Gemini CLI 走 **skill-facade** 表面（`gemini` 安装面、`GEMINI_HOME/skills` 技能写入），与 cursor-agent 共享 `_skill_facade_cli_activation` / `_install_skill_facade` / `generic_cli` profile——**cursor-agent 保留**，只删 gemini 专属分支。政策沿用 016（共用 skill-facade 的整宿主移除）与 019/020：永久移除、纯删除优先、op-log + 基线对照、残留 grep 为零。

## 变更清单（~14 修改 + 1 重命名 + 1 新增 op-log + INDEX 1 行）

**宿主目录（核心）**
1. `host_loop_activation.py` 6 个删除块:`scheduler_command_binding_for_agent_type` 行、`SUPPORTED_AGENT_TYPES` 行(12→11)、`AGENT_TYPE_CATALOG["gemini-cli"]` 整条(8 个别名随 `AGENT_TYPE_ALIASES` 派生自动消失;`build_agent_type_catalog`/`doctor`/`starter_bootstrap` 等消费方自适配)、`HOST_SURFACE_TO_AGENT_TYPE` 两行、`_heartbeat_commands` scope 行、`_gemini_cli_activation` 整函数 + 分发 `elif` 分支(共享 `_skill_facade_cli_activation`/`_cursor_agent_activation` 保留)。

**安装器/表面管线**
2. `slash_command_install.py` 9 块:instruction 串 token、`_gemini_home()` 助手、`_normalize_surfaces` 两行分支、`install_slash_commands` 的 `gemini_home` kw-only 参数(4 个调用点全部在范围内)、`gemini_root` 行、`if "gemini" in effective_surfaces` 整块(含注释)、summary 键 `gemini_skill_dir`、notes 串、render_markdown 两行。
3. `cli_commands/slash_commands.py` 4 块:`--surface` choices 两项、help 文案、`--gemini-home` 参数块、pass-through。

**激活/合约**
4. `agent_onboarding.py` 3 块、`bootstrap_command_pack.py` 2 块(`START_GOAL_HOST_SURFACES` 12→11 + `host_descriptions` 行)、`control_plane/goals/start_contract.py` 1 行、`slash_commands.py` 1 行。

**测试（1 改名 + 5 编辑）**
5. `tests/test_gemini_cursor_host_surfaces.py` → **`tests/test_cursor_host_surfaces.py`**（git mv;全库零引用该文件名）,内部改 `NEW_HOSTS=("cursor-agent",)`(4 参数化案例收缩)、映射键、GEMINI_HOME env、home 路径。
6. `test_host_parity_smoke.py` 6 处删/改(含 `len(types) >= 12` → `>= 11` 唯一硬计数)。
7. `test_slash_command_install.py` 删两个 gemini 安装/卸载测试;`test_gemini_and_cursor_are_opt_in_not_part_of_all` 改名 cursor 版。
8. `test_deepresearch_command.py` skill-facade 代表面 gemini → cursor。
9. `test_start_goal_compact_projection.py` 精确 gate choices 列表删行。

**文档/操作日志**
10. `docs/development/contributor-tasks.md` 2 处枚举去 `Gemini`(+ 顺带删除 020 漏网的 "P2 鉴定 Codex App heartbeat…" 行——Codex App 已退役)。
11. 新增 `operation-logs/021-remove-gemini-cli.md` + `000-INDEX.md` 行 021。

**附带修正**:`test_start_goal_compact_projection.py` 三处 CLI 传参 `--host-surface codex-cli` → `codex-cli-tui`(020 漏网;START_GOAL_HOST_SURFACES 只接受 codex-cli-tui,该三个测试在移除前即失败)。

## 验证

- **基线(同环境顺序复测)**:`edeee904`(干净,前后各测一次避免 TS runtime 可用性波动)**5872 collected + 4 预存 collection errors**(outbound_guidance、refresh_checkpoint_recovery、shared_goal_alignment_cli、python_ci_workflow(.github 缺失))。
- **新树**:5872 → **5864**(差 8 = 2 删函数 + 5 参数化收缩 + 1 参数化行),同 4 errors。
- **聚焦 pytest 全绿**:`test_cursor_host_surfaces.py`(6)、`test_host_parity_smoke.py`(34)、`test_slash_command_install.py`(37)、`test_deepresearch_command.py::test_skill_facade…`、`test_start_goal_compact_projection.py`(56,含附带修正)、`test_skill_delivery_parity.py`;`compileall` 0 错误。
- **残留 grep** 0:`grep -rni gemini`(排除 .git/operation-logs/deprecate/docs-research/__pycache__/node_modules)空;`find -iname "*gemini*"`(同排除)空(含测试文件改名)。
- **降级实测**:`normalize_agent_type("gemini")`/`agent_type_for_host_surface("gemini")` → AgentTypeError(11 suggestions);`--surface gemini`/`--gemini-home`/`--host-surface gemini-cli`/`doctor --agent-type gemini-cli` → argparse 错误;`install_slash_commands(gemini_home=…)` → TypeError;`_gemini_home`/`_gemini_cli_activation` 不存在;`agent-onboard --list-agent-types` 11 项;doctor 与 `--agent-type cursor-agent` 正常;`--surface all` dry-run 仍 `["codex","claude-code","opencode"]`。
- `npm run test:control-plane` 未受影响(TS Effect runtime 环境备注同 020)。

## 环境备注

TS Effect runtime 服务端在本环境不可用(与 019/020 同源,全量对照以失败文件集合一致为准);`.github/` 缺失致 `test_python_ci_workflow.py` collection error(预存)。**本次移除无 benchmark 臂**(活动 benchmark 树零 gemini 引用);`deprecate/benchmark-legacy` 与 `docs/research` 中的 Gemini 为历史性 Google 产品/模型审计文本,保留;operation-logs 016-018 中 gemini 字串为当时上下文,保留。
