# 018 · 移除 Antigravity CLI 宿主适配器

- **日期**: 2026-09-08
- **分支**: `260906-dev`
- **背景**: 用户不需要 Antigravity CLI(Google 终端编码 agent,二进制 `agy`),
  要求完整移除且不破坏 LoopX 其他功能 —— 尤其 Gemini CLI(共享 `~/.gemini`
  父目录但读 `GEMINI_HOME/skills`,机制独立)、共享 `_skill_facade_cli_activation`
  (gemini/cursor 仍用)与共享 `GENERIC_CLI_AGENT_LOOP` profile。政策沿用前三轮:
  永久移除(专用测试整删、不纳入守卫测试)、文档彻底静默、直提 + op-log。

## 变更清单(13 文件,+1 / −326)

**整包/整文件删除(先清级联 import)**
1. 两个模块级 import 先删(删包前):`host_loop_activation.py:6`
   `from .agy_goal_mode import AGY_ACCEPTED_INPUTS, agy_activation_extras` 与
   `slash_command_install.py:11` `from .agy_goal_mode import agy_home as _agy_home`
   —— 不删则删包后 import 链崩溃。
2. `loopx/agy_goal_mode/` 整个包(README.md 79 行 + __init__.py 118 行;常量
   `AGY_ACCEPTED_INPUTS`/`agy_activation_extras()`/`agy_home()` 仅被同步删除的
   import 与测试使用;无 pyproject/package-data 引用)。
3. `tests/test_agy_host_surface.py`(253 行、8 个测试函数,100% agy);共享
   `tests/host_surface_cli_probes.py` 保留(gemini/cursor 测试仍用)。

**核心手术(`host_loop_activation.py`,8 处成对删除)**
4. runtime-profile 绑定 key(共享 `GENERIC_CLI_AGENT_LOOP`/`generic_cli` 保留,
   无枚举手术、无持久值风险)、`SUPPORTED_AGENT_TYPES` 条目(15→14;parity 下限
   `>=13` 仍过)、`AGENT_TYPE_CATALOG["agy"]` 条目(6 别名 agy/antigravity/
   antigravity-cli/antigravity_cli/antigravity cli/google antigravity 由 alias
   派生表自动消失)、`HOST_SURFACE_TO_AGENT_TYPE` 三 key、heartbeat scope_by_type
   行、`_agy_cli_activation` 构建器(**共享 `_skill_facade_cli_activation` 保留**,
   gemini/cursor 仍调用)与分发 elif。

**家族/共享结构**
5. `agent_onboarding.py`:`_surface_install_command` agy 分支、`surface_by_type`
   key(直查无 fallback,与 catalog 同 commit)、`_start_instruction` agy 分支
   (native /goal + schedule + 两 token + advisory 措辞整段)。
6. `bootstrap_command_pack.py`:`START_GOAL_HOST_SURFACES` 成员与 `host_descriptions`
   key **成对删**(selection gate 直查防 KeyError;start-goal/bootstrap-command-pack
   choices 迭代派生自动收缩)。
7. `cli_commands/slash_commands.py`:`--surface` choices 两值(旧调用 fail-closed)
   与 help 措辞。
8. `slash_command_install.py`:skill 指令枚举串、`_normalize_surfaces` elif、
   签名参数 `agy_home` 与无条件 `agy_root` 计算(唯一传入方为已删的 agy 测试;
   windows_install 与其余调用方从不传)、agy 安装块(含 flat=True)、summary
   `agy_skill_dir` key(渲染端本就无对应行)、notes 条目。
9. `control_plane/goals/start_contract.py` + `loopx/slash_commands.py`:嵌入式
   文档 map 行。

**测试与文档**
10. `tests/control_plane/test_start_goal_compact_projection.py`:有序快照删
    `"agy"`(cursor-agent 与 deepseek-harness 之间)。
11. `tests/test_deepresearch_command.py:1018`:陈旧注释("…and agy once its
    surface PR merges" —— agy 早已合并现又被移除)措辞清理。
12. `README.md`:删 host 表格 `Antigravity CLI（agy）` 行(Pi 与 DeepSeek Harness
    行之间)。

**刻意保留**(历史,不改写):`docs/product/release-readiness.md:198`(v0.5.3
changelog "添加 ZCode 与 Antigravity CLI Goal 界面" —— 016 已确立保留先例,
同行使含已删的 ZCode)、`operation-logs/016`/`017` 中 agy 叙述。
**零改动**(已核实无 agy):docs/ 全树(guides/protocols/book/integrations/
update-notes)、man/loopx.1、site App.tsx、dashboard normalizer、mkdocs、
pyproject、apps/、TS control plane、examples/dev-book-publication-smoke(标记
元组无 agy,chapter 02 矩阵本无 agy 行)、example smoke、windows_install、
`test_host_parity_smoke.py` 等 parity 测试。

## 验证

0. **对抗式自查(提交后复查,未发现问题、无需修复)**:逐 hunk 重读完整 diff
   (host_loop_activation 29 行纯删除、agent_onboarding/bootstrap 成对删、
   安装器 8 处、README 行均与计划逐行对应,无连带损伤);扩展残留模式补查
   agy 专属 token(`Antigravity CLI`/`antigravity-cli`/`antigravity_cli`/
   `agy_agent_loop`/`agy_cli_skills`/`AGY_GOAL`/`<!-- GOAL_COMPLETE -->`/
   `<!-- GOAL_CANCELLED -->`/`MaxIterations`/`DurationSeconds`)全类型扫描:
   **仅剩 release-readiness v0.5.3 历史行**(区分大小写精确扫描后,小写
   `goal_complete` 命中均为 pi/dsh/opencode 自有机制,与 agy 无关);
   共享 `_skill_facade_cli_activation` 恰好 2 个存活调用方(gemini/cursor);
   工作树干净、提交含全部 15 路径。
1. 残留 grep(全类型,排除 git-ignored 与 op-log):产品代码与文档 **0 残留**;
   仅剩 release-readiness v0.5.3 历史行(pnpm-lock hash 与 showcase base64
   为误报,已人工滤除)。
2. `compileall` 0 失败;显式导入 7 个改动产品模块 0 失败(模块级 import 为最高
   风险点,已先行删除)。
3. 旧输入明确报错 + 兄弟路径完好(实测):`normalize_agent_type("agy"/
   "antigravity"/"antigravity-cli"/"antigravity_cli"/"google antigravity")`
   → AgentTypeError;`start-goal --host-surface agy` / `slash-commands --install
   --surface agy` / `agent-onboard --agent-type agy` → invalid choice/unsupported;
   对照 gemini-cli 与 cursor-agent normalize + activation packet(经共享
   `_skill_facade_cli_activation`)正常。
4. 聚焦测试 272 passed(compact projection、gemini/cursor host-surface 系列、
   thread binding、retired hosts、slash install、skill delivery、deepresearch、
   parity);example smoke exit=0;ruff 改动文件全过;`git diff --check` 干净。
5. **全量 + 基线对照(决定性)**:整树排除已知预存收集 error 后
   `15 failed / 5927 passed / 25 skipped`;15 个失败与 017 轮基线
   (`3efba79a`) 已确认的环境失败文件**逐一相同**(fleet_health ×3、sonarcloud
   ×3、license ×2、registry_git_probe ×2、retained_cases ×2、lark ×1、
   pr_program ×1、repository_change_window ×1);passed 差 5935→5927 恰为被删
   的 8 个 agy 测试函数(实测计数,非探索预估的 10),移除引入 0 回归。

## 环境备注

- 同 015–017 环境:TS Effect runtime 生命周期缺陷与 `.github/` 缺失、`tests.*`
  整树收集模式仍可能产生预存失败,与本次移除无关。
- 本次改动按计划直接提交到 `260906-dev`。
