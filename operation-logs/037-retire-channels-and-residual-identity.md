# 037 · 移除发布快照/归档通道 + 残余身份收口（op 036 的 P5–P7）

- **日期**: 2026-09-14
- **分支**: `260906-dev`
- **背景**: op 036 完成 P1–P4（身份与版本、wheel 路径、两路口径、归档通道从 `self_update` 退役）。
  本批执行其 P5（删渠道脚本 + 改产品文案 + 退役守卫/文档）、P6（发布就绪文档）、P7（残余身份）。

## 用户确认的口径（延续 op 036 的 8 条决策）

- 两个渠道脚本都删，**周边机制与守卫一并退役**；
- 产品文案指向本地 wheel 重装，PyPI / install.sh / codeload 归零；
- 边界推定（用户批准方案时接受）：桌面端与公开首页**一并改**（不重建 52 个 dashboard 产物）；
  frontstage 分享包改为**不再要求 installer**；benchmark/desktop 中对已删脚本的引用一并清理。

## P5 `0afaa3c3d` · 移除发布快照与归档通道（56 文件，+408/−4693）

### 删除（19 个文件）

- `scripts/install-local.sh`、`scripts/install-from-github.sh`；
- 12 个渠道专属冒烟：`install-local-smoke`、`install-local-overwrite-smoke`、
  `fresh-clone-quickstart-smoke`、`claude-install-optin-smoke`、`codex-cli-packaged-install-smoke`、
  `codex-cli-tui-bootstrap-smoke-bundle-smoke`、`release/codex-cli-no-clone-release-verification-smoke`、
  `release/local-install-promotion-boundary-smoke`、`release/release-promotion-concurrency-smoke`、
  `canary/canary-promotion-readiness-smoke`、`canary/canary-promotion-readiness-writeback-smoke`、
  `canary/canary-promotion-readiness-boundary-smoke`、`canary/canary-promotion-no-write-contract-smoke`；
- `tests/test_release_smoke_archive_helpers.py`；
- `docs/product/runtimes/codex-cli/codex-cli-no-clone-release-verification.md`。

### 产品代码

- `loopx/install_contract.py` **重写**：删掉 `NO_CLONE_INSTALL_URL` / PyPI 安装命令 / 归档回退，
  改为 `install_repair_command()`（按当前安装形态：checkout 刷新 / wheel 重装 / 两路提示）与
  `wheel_install_command()`（`scripts/build-wheel.sh` + `--force-reinstall`）。
- `loopx/python_install_owner.py`：新增 `detect_running_install()`、`current_refresh_command()`、
  `wheel_convention_path()`、`INSTALL_PATHS_HINT`；`distribution_upgrade_command()` 不再回退到索引命令。
- `loopx/doctor.py`：删 `local_install_command` / `no_clone_upgrade_command` / `install_script` 检查与
  载荷字段；`fix` 文案改为两路；**索引安装与未知 owner 一律给两路提示，绝不输出索引命令**。
- `loopx/project_prompt.py`：两处 preflight 与生成的 bootstrap 消息改为两路（无 pip upgrade、无 curl），
  并补回 `workflow-skills --install` 步骤。
- `loopx/bootstrap.py`：`install_repair_command`/`wheel_install_command` 来自新助手，归档段改为
  "Local Wheel Install"。
- `loopx/claude_goal_mode/{README.md,scripts/install.py}`、`skills/loopx-project/SKILL.md`：
  不再引用 `install-local.sh`；skill 里那段**指向 op 032 已删脚本的 Windows/PowerShell 预检**一并删除。
- `promotion_readiness.py` / `promotion_gate.py`：那条"指向已删冒烟"的动作字符串改为明确的
  "release-snapshot promotion was retired in this fork (operation log 036)"。

### 守卫与文档

- canary 目录/planner 的脚本引用与删除**同一提交**更新（`quality_surface_catalog` 的 owner_paths
  改为 `loopx/python_install_owner.py`+`scripts/build-wheel.sh`，durable_smoke 改为 wheel 冒烟）。
- 断言旧字符串的守卫改写：`catalog-planner-smoke`、`catalog-run-e2e-smoke`、`smoke-suite-runner-smoke`、
  `status-markdown-smoke`、`runtime-freshness-warning-readmodel-smoke`、`promotion-gate-smoke`、
  `heartbeat-prompt-smoke`、`codex-cli-bootstrap-message-smoke`、`codex-cli-first-run-rehearsal-smoke`、
  `release-readiness-doc-smoke`、`tests/test_doctor_install_freshness.py`（7 处）。
- 文档约 20 处改为两路口径：README 的禁令段与 canary 段、`editable-dev-loop` 的"不要运行这些"表、
  `getting-started`（整个上游 canary 章节删除）、`integration`、`new-project-codex-prompt`、
  `release-readiness`、`status-data-contract`、codex-cli 三篇、`book/05`、`CONTRIBUTING`。
- frontstage 分享包与 installer **解耦**：`export-frontstage-share-bundle.mjs` 不再复制
  `install-from-github.sh`，`frontstage-share-bundle-smoke.mjs` 删除字节一致断言与 manifest 字段断言。

## P6 `528e6b3b8` · 发布就绪文档改写（2 文件，+35/−142）

- `docs/product/release-readiness.md`：晋升矩阵 / `stable` 引用 / clone-plus-canary / PyPI Trusted
  Publisher / `gh attestation --repo huangruiteng/loopx` 全部改写为两路口径；回滚定义为"放回上一个
  wheel 或 checkout 提交"；"已合并不等于运行时活动"改用本 fork 实际有的证据（`install_path` /
  `wheel_path` / manifest 血缘），不再提 `--ref main` 与已删的 `--installed-doctor-json`；
  贡献者归属去掉上游创始人特例。**发布日期时间线原样保留**（`repository-hygiene-smoke` 要求至少一条
  "于 20…" 的带日期条目，且它们是历史记录）。
- `examples/release-artifacts-smoke.py`：删除断言 `.github/workflows/release-artifacts.yml` 的整块
  （该文件在本 fork 不存在，是既存红灯的根因）→ **该冒烟由红转绿**。

## P7 `62e9af34a` · 残余身份（14 文件，+24/−24）

- 桌面端：`tauri.conf.json` 与 `maintenance.rs` 的更新源、`bundled_runtime.rs` 的 `LOOPX_REPO`
  改指 `yanfeng98/nano-loopx`；`scripts/desktop_update_feed.py` 生成 fork 命名空间的下载 URL。
- 公开首页：`App.tsx` 的安装命令改为就地 editable 安装、GitHub 链接改指 fork，
  `SweMarathonBrief.tsx` / `swe-marathon-copy.json` 的**源码链接**改指 fork（PR 评论引用保留，
  它们是已发布简报的证据而非安装路径）。
- `demo/auto_research/README.md` 与 `scripts/macos-dashboard-launchagent.sh` 不再教已删安装器；
  `scripts/update_notes_release_job.py` 指向 fork 的 PR。
- 同提交更新断言这两个生产者输出的守卫：`tests/desktop/test_update_feed.py`、
  `examples/update-notes-generator-quality-smoke.py`。

## 验证

- **全套 pytest**：三个提交后各跑一次，**失败集合与基线（推送点 `45d30e98`）逐条一致**。
  ⚠️ **该检查后来被证明无效**（见 op 038）：`heartbeat-prompt-smoke` 首个断言失败即
  终止，本批实际引入的 2 个回归藏在它从不执行的尾部断言里；按测试名比对集合查不出。
  本批的验证结论请以 op 038 的探针集合差为准。
- **冒烟**：wheel-install、loopx-update、docs-governance、release-artifacts（**由红转绿**）、
  repository-hygiene、update-notes-generator-quality、catalog-run-e2e、smoke-suite-runner、
  codex-cli-first-run-rehearsal、readme-demo-surface、dev-book-publication 全绿。
- `mkdocs build --strict` exit 0；边界扫描 errors=0，861 文件（875 − 14 个删除；P5 后即为此数）。
- **既存红灯（同断言、基线同样失败）**：`release-readiness-doc-smoke`（断言该文档约 50 条**英文**短语，
  中文转换后全失效——重写该期望列表属改变验证契约，未在本批处理）、`heartbeat-prompt-smoke`
  （compact 提示词超出 6200 预算；基线 6334，现在 6403，多出的 69 字符来自两路 preflight，
  我选择保留准确指引而不是为一条既存失败砍掉它）、`catalog-planner-smoke`（archetype 层在基线即产出 0）、
  `pytest-smoke-suite-facade-smoke`、`frontstage-share-bundle-smoke.mjs`（需
  `apps/presentation/site/node_modules`）。

## 自查中抓到并修掉的问题

1. **按行区间删除时误删了 doctor.py 的 5 个无关函数**（`user_local_bin`、`codex_home`、
   `codex_skill_roots`、`command_release_root`、`current_script_invocation_path`）——`py_compile` 与当时
   跑过的测试都测不出，是 AST 未定义名扫描抓到的；已从 HEAD 恢复。
2. **`detect_running_install()` 的 repo root 少算了一级**（`parents[1].parent` 应为 `parents[1]`），
   导致形态判定失败、回退到通用提示（守卫的 `workflow-skills --install` 断言把它暴露出来）。
3. preflight 改写时**漏掉 skills 交付步骤**；`python_install_owner.py` 漏导入
   `PackageNotFoundError`/`distribution`（同为 AST 扫描发现）。
4. 我的 skill 改写一度**撑破心跳提示词预算**，删掉其中的 Windows 预检段与压缩两路文案后回到基线水平。
5. `distribution_upgrade_command` 一度被写成**同名双定义**（后者静默覆盖前者），已清理。

## 已知遗留（未处理，需单独决策）

1. **桌面端 `bundled_runtime.rs:101` 仍以 `scripts/install-local.sh` 安装其暂存运行时**——该脚本本批已删，
   所以桌面壳的捆绑运行时安装路径现在是坏的。改它需要重写 Rust 打包器，而本机 `cargo check --offline`
   无法解析其依赖（`command-group` 未缓存），无法编译验证，故未擅动。
2. **promotion 产品面**（`promotion_gate` + `promotion_readiness` + `loopx promotion-gate` /
   `promotion-readiness` CLI + status/doctor/quota 的"晋升就绪"警告）在没有发布快照后已无晋升对象；
   本批只消除死指针、未动 status 契约。整块退役会改状态载荷与约 15 个冒烟。
3. **用户declined项**（继续保留）：`loopx/web/chat/assets/*.js` 52 个打包产物仍含上游 URL、
   `apps/presentation/dashboard` 的 frontstage 展示与 fixtures、`packages/loopx-repo-health` 与
   `packages/loopx-community-discussion` 的上游数据源、`docs/project/*` 与 `docs/community/*` 的
   上游 tracker/署名链接、`benchmark/swe-marathon/agents/codex_loopx_agent.py` 的行号注释。

## 提交/推送

- `0afaa3c3d` refactor(install): remove the release-snapshot and archive channels
- `528e6b3b8` docs: rewrite the release-readiness contract for the two-path fork
- `62e9af34a` chore: point the desktop shell, homepage and demo at this fork

本批三个提交已推送至 `origin/260906-dev`（推送区间 `96e0a5b89..d00f061f0`，
与 op 038 的 `8a82aa62a` / `d00f061f0` 一并）。

**更正**：本行原记"含 op 036 的 P1–P4 尚未推送"，实为**已推送**——本次推送的起点
`96e0a5b89` 正是 op 036 的日志提交，说明 op 036 的代码与其日志当时已在远端；
本批的推送区间之所以从它开始，只是因为 op 036 的日志之后才是本批的 P5–P7。
