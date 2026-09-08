# 017 · 移除 Codex IDE plugin 宿主适配器

- **日期**: 2026-09-08
- **分支**: `260906-dev`
- **背景**: 用户不需要 Codex IDE plugin(`codex-ide-plugin`,外部 Codex 官方 IDE 插件
  host),要求完整移除且不破坏 LoopX 其他功能 —— 尤其 Codex 家族其余成员
  (`codex-app`/`codex-app-ssh`/`codex-cli`)与共享 visible-goal / skill-facade 机制。
  用户政策:彻底静默 —— 所有文档(含稳定协议文档)净删不留"已移除"叙述;专用测试
  删除,不纳入 TraeX 退役守卫测试。

## 变更清单(22 文件,+1 / −220)

**核心手术(`loopx/host_loop_activation.py`,9 处成对删除)**
1. runtime-profile 绑定 key(共享 `CODEX_CLI_VISIBLE` 枚举保留)、`SUPPORTED_AGENT_TYPES`
   条目、`AGENT_TYPE_CATALOG["codex-ide-plugin"]` 条目(12 个别名含 codex-ide/
   codex-vscode/vscode-codex 由 alias 派生表自动消失)、`AMBIGUOUS_AGENT_TYPE_INPUTS`
   三个家族条目各删一成员 → `[codex-app, codex-app-ssh, codex-cli]`、
   `HOST_SURFACE_TO_AGENT_TYPE` 两 key(`codex-ide-plugin` 与 catalog 之外的
   `codex-ide` 直查别名)、selection-rule prose、heartbeat scope_by_type 行、
   `_codex_ide_activation` 构建器(**共享 `_codex_goal_activation` 保留** ——
   codex-cli / codex-app-ssh 仍调用)与分发 elif。
2. 家族/共享结构:`agent_onboarding.py`(`_surface_install_command`/`_project_skill_surface`
   家族 set、`surface_by_type` key —— 直查无 fallback 须同 commit、`_start_instruction`
   分支)、`bootstrap_command_pack.py`(`START_GOAL_HOST_SURFACES` 成员与
   `host_descriptions` key **成对删**防 selection gate KeyError、gate reason prose)、
   `cli_commands/_host_thread.py` 与 `thread_agent_binding.py` 家族 set(深链家族
   扫描自动收缩;持久化 binding 为不透明 token 不受影响)、`cli_commands/slash_commands.py`
   `--surface` choices 两值(旧调用 argparse fail-closed)、
   `cli_commands/starter_bootstrap_registration.py` help 字符串。
3. `slash_command_install.py`:skill 指令枚举串、`_normalize_surfaces` set 两成员、
   7 处 payload `host_surfaces` 注释列表统一删 `codex-ide-plugin`。
4. `control_plane/testing/onboarding_model_behavior_qualification.py`:删 ide 专属
   oracle 块(`codex_ide_requires_*`;其余 visible-goal 家族本就走通用路径)。

**测试(4 文件 + 1 断言)**
5. `tests/test_host_loop_activation.py`:删整测试、2 处参数化行,歧义建议断言改 3 成员
   (测试名同步改)。
6. `tests/test_host_parity_smoke.py`:歧义等值断言与 scheduler-binding 期望 dict
   (`len >= 13` 边界 16→15 仍过)。
7. `tests/control_plane/test_start_goal_compact_projection.py`:有序快照删行、
   rerun 断言改指 codex-cli-tui、删整测试(含 legacy `codex-ide` 变体)。
8. `tests/control_plane/test_onboarding_model_behavior_qualification.py`:共享 fixture
   换键为存活 visible-goal host(`codex-app-ssh` ↔ `codex_app_ssh_visible_goal_mode`),
   删 ide 专属 oracle 测试。
9. `tests/test_slash_command_install.py`:删空洞的否定断言("use codex-ide for the
   IDE" not-in —— 主语已不存在,残留即真空断言)。

**Example smoke(共享文件,编辑而非删除)**
10. `examples/control_plane/agent-onboard-host-loop-activation-smoke.py`:歧义等值
    断言、host-surface 映射断言、packet 构建段、CLI 建议列表、ide onboarding
    流程段(346–356)逐一移除。

**文档:彻底静默净删(5 文件,不留退役说明)**
11. `docs/guides/getting-started.md`(标题 "CLI / IDE / App"、host 引导段含遗留
    `codex-ide` 别名句)、`docs/guides/newcomer-command-path.md`(替换值列表 + 专属
    两句)、`docs/reference/protocols/loopx-goal-command-v0.md`(激活条目、歧义理由、
    家族句与矩阵行 "Codex App SSH / Codex CLI / Codex IDE" → "… / Codex CLI";
    **不加**退役说明;既有 TraeX L40–43 说明为 TraeX 范围,保留)、
    `docs/reference/protocols/codex-app-host-command-registry-v0.md`(家族搜索集、
    非猜测列表与定义句、遗留别名句、CLI 示例行)、
    `docs/book/chapters/02-session-goal-loopx.md`(反例列表;dev-book 标记元组本就
    不含 ide,smoke 无需动)。

**刻意保留**(零改动):README host 表(本就没有 ide 行)、`man/loopx.1`、
`help_surface.py`、site `App.tsx`、dashboard normalizer(`codex` 前缀分支覆盖家族,
历史 goal 显示 "Codex")、release-readiness/update-notes(无 ide changelog 条目)、
`apps/`、`tests/control_plane_ts/`、TraeX 退役说明与其守卫测试。

## 验证

0. **对抗式自查(提交后复查,未发现问题、无需修复)**:逐 hunk 重读完整 diff
   (9 处核心删除/家族结构/测试/文档均与计划逐行对应,无连带损伤);
   扩展残留模式补查中文措辞变体 —— `IDE 插件`/`IDE plugin`/`codex ide`/
   `codex_ide`/`codex-ide`/`ide-plugin`/`codex-vscode`/`vscode-codex`/
   `ide_visible`/`visible IDE`/`composer` 全类型扫描(排除 git-ignored 与
   operation-logs):**0 命中**(composer 命中均为无关的聊天 UI 资产);
   git-tracked 文件扫描同 0;docs 家族枚举与代码三成员集逐处一致;
   `examples/dev-book-publication-smoke.py`(chapter 02 已编辑)ok;
   ruff 改动文件干净(整树 6 个预存 F401/F841/F541 均在我未触碰文件);
   `git diff --check` 干净;工作树干净。
1. 残留 grep(全类型,排除 git-ignored 与操作日志):产品代码与文档 **0 残留**
   (含 `tests/test_slash_command_install.py` 的真空否定断言一并删除)。
2. `compileall` 0 失败;显式导入 9 个改动产品模块 0 失败。
3. 旧输入明确报错 + 兄弟路径完好(实测):6 个别名
   (`codex-ide-plugin`/`codex-ide`/`codex_ide`/`codex-vscode`/`vscode-codex`/
   "codex ide plugin")→ AgentTypeError;两个 surface 直查同样拒绝;歧义 `codex`
   建议 = `[codex-app, codex-app-ssh, codex-cli]`;CLI 三入口(`start-goal
   --host-surface` / `slash-commands --install --surface` / `agent-onboard
   --agent-type`)→ invalid choice/ambiguous_or_unsupported。对照:codex-app
   → `codex_app_heartbeat_automation`、codex-app-ssh → `codex_app_ssh_visible_goal_mode`、
   codex-cli → `codex_cli_visible_goal_mode`(经共享 `_codex_goal_activation`)
   全部正常。
4. 聚焦测试:4 个改动测试文件 148 passed;thread binding、retired hosts、skill
   delivery、agy/gemini-cursor surfaces、onboarding 全绿;example smoke exit=0;
   改动文件 ruff 全过(整树 6 个预存 F401/F841/F541 均在我未触碰文件,基线即存在;
   顺手清掉 example 中基线就有的 F841 死变量);`git diff --check` 干净。
5. **全量 + 基线对照(决定性)**:整树排除已知预存收集 error 后
   `15 failed / 5935 passed / 25 skipped`;15 个失败与 016 轮基线 worktree
   (`214b0c4d`) 已复现的环境失败文件**逐一相同**(fleet_health ×3、sonarcloud ×3、
   license ×2、registry_git_probe ×2、retained_cases ×2、lark ×1、
   pr_program ×1、repository_change_window ×1;其中被日志截断的 4 个已单跑复现);
   passed 数 5940→5935 恰为被删 5 个测试用例(host_loop_activation ×3 +
   compact projection ×1 + qualification ×1),移除引入 0 回归。

## 环境备注

- 同 015/016 环境:TS Effect runtime 生命周期缺陷与 `.github/` 缺失、`tests.*`
  整树收集模式仍可能产生预存失败,与本次移除无关。
- 运行跨 cwd 的 onboarding 子进程测试前需 `pip install -e .`(已就绪)。
- 本次改动按计划直接提交到 `260906-dev`。
