# 015 · 移除 KunlunCode 宿主适配器

- **日期**: 2026-09-07
- **分支**: `260906-dev`
- **背景**: 用户不需要 KunlunCode(外部 CLI 编码 agent 宿主),要求完整移除其适配器,
  且不破坏 LoopX 其他功能(Codex / Claude Code / DeepSeek Harness / 自定义 runner、
  scheduler、registry、quota、文档站点)。

## 变更清单(32 文件,+16 / −5630)

**整包/整文件删除**
1. `loopx/kunluncode_goal_mode/` 整个包(9 文件:__init__/cli/runtime/app_server/
   server/context/control_plane/guards/README);
2. `examples/kunluncode-app-server-goal-pro-smoke.py`(canary 按 glob 发现,无 manifest)
3. `tests/test_kunluncode_goal_mode.py`(1576 行);
4. `docs/guides/kunluncode-adapter.md` + `.html`(不在 mkdocs nav,无悬空链接)。
5. `pyproject.toml`:删除 `loopx-kunluncode` 入口与 `kunluncode_goal_mode` package-data。

**核心代码手术式编辑**
6. `host_loop_activation.py`:删除 scheduler runtime-profile 绑定、"kunluncode"
   SUPPORTED_AGENT_TYPES 条目、`AGENT_TYPE_CATALOG` 条目(含 5 个别名,alias 自动派生)、
   `_kunluncode_activation` 构建器与分发分支;`HOST_MANAGED_SKILL_AGENT_TYPES` 等其余
   集合本就不含 kunluncode,未动。
7. `cli_runtime.py` + `cli.py`:整段删除 `enforce_native_controller_guard`
   (仅 `LOOPX_KUNLUNCODE_OUTER_CONTROLLER=1` 时生效)及其两处调用与 import。
8. `control_plane/scheduler/execution_context.py`:删除 `HostSurface.KUNLUNCODE`、
   `SchedulerRuntimeProfile.KUNLUNCODE_VISIBLE`、`_SCHEDULER_RUNTIME_PROFILE_CONTEXTS`
   条目、`cli_surfaces` 集合成员。
9. `control_plane/heartbeat/host.py`:`resolve_exact_heartbeat_turn_identity` 对
   `SchedulerRuntimeProfile(runtime_profile)` 增加 try/except ValueError 防护
   (失败落入原有检查,文案与行为完全不变;旧 `runtime_profile=kunluncode` 从此走同一
   显式文案而非裸 ValueError)。
10. `help_surface.py` + `man/loopx.1`:删除 host 条目与 help 行。
11. `cli_commands/support_control_heartbeat_registration.py`:`--host-surface` choices
    删 `kunluncode`(与 HostSurface 枚举逐值同步)。
12. `goal_mode_mcp.py` / `goal_mode_context.py`:共享代码只做措辞中性化
    (MCP SDK 报错文案、docstring),不删除参数/逻辑(Claude Code adapter 共用)。

**测试与文档**
13. `tests/test_host_loop_activation.py`:删 2 处精确断言、1 处参数化条目、
    `test_kunluncode_activation_...` 整测试;
    `tests/control_plane/test_scheduler_execution_context.py`:删除 surface 元组
    与 FIRST_CLASS_RUNTIME_PROFILES 条目(其余参数化随枚举自动缩减,无计数断言);
    `tests/test_dsh_goal_mode.py`:仅注释措辞。
    不用改但纳入回归:`test_host_parity_smoke.py`(下限 >=13,19→18 仍过)、
    `test_skill_delivery_parity.py`、`test_cli_output_budget.py`。
14. `README.md`(host 表格行 + 链接与语序)、`docs/guides/README.md`(索引两条)、
    `docs/book/chapters/00-reading-guide.md`(Host runtime 行)、
    `docs/book/chapters/02-session-goal-loopx.md`(Host 兼容矩阵行,
    **必须与 `examples/dev-book-publication-smoke.py` L330 标记元组同步**,否则
    zh_concepts 硬校验失败)。

**刻意保留**(历史记录,不改写):`docs/product/release-readiness.md:194`
(v0.4.9 changelog)、`operation-logs/**` 既有条目。

## 验证

1. 残留 grep(全类型文件,排除 git-ignored):仅剩 `release-readiness.md:194`。
2. `compileall` + 900 模块全量导入 0 失败;`loopx --help`/help surface/man 无残留;
   `git diff --check` 干净;dev-book-publication-smoke 与 511 个 canary smoke 通过。
3. 受影响测试(375+)在 TS runtime 健康时全绿,含 zcode gate。
4. 旧输入四路径优雅降级(实测):`normalize_agent_type("kunlun")` → `AgentTypeError`;
   `scheduler_execution_context_for_runtime_profile("kunluncode")` →
   `unsupported scheduler runtime profile`;`uses_native_goal_host_loop` → False;
   turn-identity → 原有显式文案。
5. **HEAD 基线对照(决定性)**:同一环境下对干净 HEAD(kunluncode 完整存在)跑全量
   `362 failed / 5686 passed / 10 errors`——失败文件 48 个(zcode、dsh、turn_*、
   status_server_*、fleet_health、scheduler_execution_context 等),与移除后失败
   集合同源同文件,失败名单中 kunlun 引用 0 处。三类根因均为环境/上游预存问题:
   - TypeScript Effect runtime 生命周期缺陷(本机堆积 113 个孤儿
     `effect_runtime_server` 进程,共用同一 fingerprint/info 路径互相覆盖,
     连接被拒;HEAD 基线同样失败);
   - `.github/` 被更早提交整体删除 → `test_python_ci_workflow.py` 收集报错;
   - `tests.*` 包导入模式在整树收集时 4 个预存错误。

## 环境备注

- 清理命令(仅 WSL 内 127.0.0.1 loopback,不涉及宿主机网络配置):
  `pkill -f effect_runtime_server && rm -rf /tmp/loopx-effect-runtime-*`。
- 要在本机获得全绿全量,需先修 `loopx/control_plane/effect_runtime.py` 的
  runtime 驻留/校验竞态(上游独立问题,不在本次范围内)。
- `loopx.egg-info/` 为 git-ignored 生成物,`pip install -e .` 后自动清掉
  残留 `loopx-kunluncode` 入口。
- 本次改动留存在工作区,尚未提交。
