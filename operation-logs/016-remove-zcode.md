# 016 · 移除 ZCode 宿主适配器

- **日期**: 2026-09-08
- **分支**: `260906-dev`
- **背景**: 用户不需要 ZCode(外部终端编码 agent 宿主,zcode.z.ai),要求完整移除其
  skill-facade 适配器且不破坏 LoopX 其他功能;ZCode 专用测试一并删除、不纳入
  TraeX 退役守卫测试 —— ZCode 之后永久不存在。

## 变更清单(14 文件,+1 / −198)

**整文件删除**
1. `loopx/zcode_goal_mode/` 整个包(README.md + __init__.py;无 pyproject 入口、
   package-data 或 console script 引用,常量仅被同步删除的 import 使用)。
2. `tests/test_zcode_host_surface.py`(170 行,100% zcode 专用;共享 helper
   `tests/host_surface_cli_probes.py` 保留 —— agy/gemini/cursor 测试也在用)。

**核心代码手术式编辑**
3. `host_loop_activation.py`:删 runtime-profile 绑定
   (`"zcode": GENERIC_CLI_AGENT_LOOP`,共享枚举本身保留)、`SUPPORTED_AGENT_TYPES`
   条目、`AGENT_TYPE_CATALOG["zcode"]` 条目(4 个别名 zcode/z_code/z code/z-code
   由 alias 派生表自动消失)、`HOST_SURFACE_TO_AGENT_TYPE` 两 key、heartbeat
   scope_by_type 行、`_zcode_activation` 构建器(共享的
   `_skill_facade_cli_activation` 保留,gemini/cursor/agy 依赖)与分发 elif 分支。
4. `slash_command_install.py`(耦合最重):先删模块级 import
   `from .zcode_goal_mode import zcode_home`(不删则删包后整个 import 链崩溃,
   连带 `cli_commands/slash_commands.py` 与 `windows_install.py`);再删
   `_normalize_surfaces` elif、签名参数 `zcode_home/zcode_agents_home` 与无条件
   `zcode_root` 计算、`"zcode" in effective_surfaces` 安装分支、summary payload
   `zcode_skill_dir` key、notes 条目与 markdown 渲染读取。
5. `cli_commands/slash_commands.py`:删 `--surface` choices 两值、help 措辞、
   `--zcode-home` 与 hidden `--zcode-agents-home` 参数及其转发。
6. `agent_onboarding.py`:删 `_surface_install_command` if 分支、`surface_by_type`
   key(该 dict 为直查无 fallback,须与 catalog 同 commit)、`_start_instruction`
   分支。
7. `bootstrap_command_pack.py`:`START_GOAL_HOST_SURFACES` 元素与 `host_descriptions`
   key 成对删除(selection gate 直查,防 KeyError;三个消费方全部迭代派生自动收缩)。
8. `control_plane/goals/start_contract.py` + `slash_commands.py`:删嵌入式文档 map 行。

**测试与文档**
9. `tests/control_plane/test_start_goal_compact_projection.py`:删有序全量快照中
   `"zcode"`(cursor-agent 与 agy 之间)。
10. `README.md`:删 host 表格 ZCode 行。
11. 本次不新增守卫测试,亦不改写 `tests/test_retired_host_interfaces.py`(TraeX
    守卫,不含 zcode)。

**刻意保留**(历史记录,不改写):`docs/product/release-readiness.md:198`(v0.5.3
changelog "添加 ZCode 与 Antigravity CLI Goal 界面")、`operation-logs/015` 中
zcode 叙述。`man/loopx.1`、`help_surface.py`、docs/book、`apps/presentation/site`、
`pyproject.toml` 本就无 zcode,零改动。

## 验证

1. 残留 grep(全类型文件,排除 git-ignored):产品代码 0 残留;仅剩
   `release-readiness.md` v0.5.3 changelog、`operation-logs/015` 叙述与本日志本身。
2. `compileall` 0 失败;显式导入高危模块(`slash_command_install`、
   `cli_commands/slash_commands`、`windows_install`、`host_loop_activation`、
   `bootstrap_command_pack`、`agent_onboarding`、`start_contract`)0 失败。
3. 旧输入明确报错(实测):4 个别名 `zcode/z-code/z_code/z code` →
   `AgentTypeError: unsupported agent_type`;`agent_type_for_host_surface` 与
   `build_host_loop_activation_packet` 同样拒绝;`slash-commands --install
   --surface zcode` 与 `start-goal --host-surface zcode` → argparse invalid
   choice;`agent-onboard --agent-type zcode` → `ambiguous_or_unsupported`。
   兄弟 host 路径完好:`normalize_agent_type("agy")`、`_surface_install_command
   ("agy", ...)`、agy activation packet 均正常。
4. 聚焦测试:`tests/control_plane/test_start_goal_compact_projection.py` +
   `tests/test_slash_command_install.py` 98 passed;受影响面扫描(host surface/
   bootstrap/start-goal/activation/onboarding/catalog/parity 等 347 项)
   347 passed / 2 skipped / 0 failed;ruff 全过;`git diff --check` 干净。
   整树收集 3 个 error 均为 015 已记录的环境预存问题(.github 缺失、
   tests.* 包导入模式,tests/ 无 __init__.py)。
5. **全量 + HEAD 基线对照(决定性)**:整树排除预存收集 error 后
   `15 failed / 5940 passed / 25 skipped`;15 个失败文件全部与 zcode 无引用
   关系,且在基线 worktree(移除前 `051f5720`,PYTHONPATH 指向该 worktree)
   上**逐一完全复现**(fleet_health ×3 = TS effect runtime 预存、
   sonarcloud ×3 = .github 被删、registry_git_probe/repository_change_window
   = git 环境、license_metadata、retained_cases、lark collector 等),证明
   移除引入 0 回归。
6. 环境步骤:子进程 onboarding 测试需 `pip install -e .`(015 同款);补装后
   `test_pi_onboarding_install_command_...` 5 passed,与 zcode 移除无关。

## 环境备注

- 与 015 同环境:TS Effect runtime 生命周期缺陷(孤儿 `effect_runtime_server`
  进程)仍可能使 TS 侧测试失败,属预存问题,与本次移除无关。
- 运行跨 cwd 的 onboarding 子进程测试前需 `pip install -e .`(015 同款
  环境步骤);本次已验证可编辑安装后相关测试全绿。
- 本次改动按计划直接提交到 `260906-dev`。
