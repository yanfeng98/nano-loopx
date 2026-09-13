# 031 · 安装/开发文档改成「就地 editable 开发」口径 + doctor 不再推发布通道

- **日期**: 2026-09-13
- **分支**: `260906-dev`
- **背景**: 用户要**魔改**本 fork，开发方式固定为「clone 本 checkout → `pip install -e .` →
  改完就地验证」，不再走上游 PyPI 通道。但仓库里**没有任何一份文档**描述这条路（README
  `## 试用 LoopX` 是 PyPI 三步走，`CONTRIBUTING.md`、`getting-started.md` 的贡献者安装指向
  `scripts/install-local.sh`，`installing-loopx.md` 整篇是上游安装指南），而且运行时**还在
  主动把人推回旧路径**。
- **用户决策（4 项）**: ① README **彻底替换**成开发路径；② 文档为主、**允许一处小修**；
  ③ **新增**一篇本地开发文档；④ 循环深度取**最短 edit → verify**。

## 实测现状（处理前，非推断）

本机环境：`loopx` 已是 editable 安装（`Editable project location: <checkout>`），
`loopx version` = `1.0.0`（`loopx/__init__.py::__version__` 字面量），
`pip show loopx` = `0.5.4`（9/6 那次安装留下的陈旧元数据）。

`loopx doctor`（console script）实测输出：

| 字段 | 值 | 危害 |
| --- | --- | --- |
| `package.install_kind` | `live_checkout` | — |
| `install_freshness.status` | `repair_recommended`（`requires_upgrade: True`） | 因 `~/.codex/skills` 未装 LoopX skill |
| `install_freshness.upgrade_command` | `curl -fsSL https://huangruiteng.github.io/loopx/install.sh \| bash` … | **会在本机再装一份发布版** |
| `install_freshness.contributor_upgrade_command` | `<checkout>/scripts/install-local.sh` … | 同上（发布快照） |
| `payload["fix"]`（markdown 的 `## Fix` 段） | `Run <checkout>/scripts/install-local.sh … For no-clone repair, run curl … install.sh \| bash` | **`ok=False` 时打印，本机第一次跑 doctor 就命中** |

`loopx update plan`：`install_lifecycle.owner = source_checkout`、`loopx_apply_supported: False`、
`owner_upgrade_command = <checkout>/scripts/install-local.sh`。

**为什么这两条不能照抄（实测证据）**：本机 `PATH` 第一位是 `~/.local/bin`，而
`scripts/install-local.sh` 会往那里写 `loopx` / `loopx-canary` wrapper，并把 checkout 复制成
`~/.local/share/loopx/releases/<id>` 快照 → **跑一次就静默接管 editable 安装**。

## 变更清单

### 新增 `docs/development/editable-dev-loop.md`

就地开发闭环：一次性准备（含元数据陈旧的反直觉点与刷新命令）→ 最短 edit → verify →
**活改 / 重装 / 重建判定表**（`.py` 即时、`control_plane/**.ts` 即时、新 namespace 目录需重装、
`pyproject.toml` 需重装、`skills/**` 需重跑安装、前端源码需 `build:chat`）→ skills 重跑时机
（Codex 与 Claude 两个根）→ `doctor` 的已知边界（非只读、不扫 `~/.claude/skills`）→
cwd 遮蔽陷阱 → **不要运行的命令表** → 与上游合并的处置。

链接来源：`docs/development/README.md`（类别索引，必需）、`README.md`（3 处）、
`CONTRIBUTING.md`、`getting-started.md`；`mkdocs.yaml` 的 `Development:` 段加一行。

### README

- `## 试用 LoopX`：PyPI 块、PowerShell 块、`loopx update plan/apply` 段、"无需 clone"叙述
  全部移除，替换为 clone + editable 安装 + 两条 skills 命令 + 「本 fork 只走就地通道，不要
  在同一环境跑 PyPI/pipx/install-local.sh/curl 安装器」+ 链接新文档；
- 末尾「Clone 安装只面向需要 live canary wrapper 的贡献者」块 → 改为说明该通道只在需要
  canary wrapper 时使用、且会接管 `loopx`；
- `### 构建与评审 LoopX` 追加一条新文档链接。
- **保留不动**（守卫逐字锁定）：两个标题、host 表四行（Codex CLI 单元格逐字）、核心 tick 块、
  `### 首次运行反馈`（含上游 issue 模板链接）。

### 三份同步文档

- `CONTRIBUTING.md` 本地开发段 → editable 三连 + 链新文档；「常用聚焦检查」原样保留。
- `docs/guides/installing-loopx.md`：**只标注不重写**——顶部加 fork 偏差段与就地开发命令，
  正文保留为上游对照；并把因本次代码修复而失实的 `:183-186`（"对活动源码 checkout，它报告
  贡献者安装器"）改为"报告就地 editable 刷新命令"；`:237` canary 提示补半句。
- `docs/guides/getting-started.md`：「贡献者安装」段 → editable 三连 + 链新文档；
  「全局 Skill 安装、更新、修复与清理」段顶部加 fork 偏差说明（该段描述的 install-local.sh
  通道不是就地开发路径）。

### 小修 `loopx/doctor.py`（`self_update.py` 自动受益）

新增 `is_editable_source_checkout(repo_root, release_root)`（判据 `release_root is None and
(repo_root / ".git").exists()`）与 `editable_dev_refresh_command(...)`；在三处接入：

1. `contributor_upgrade_command`：checkout 时改为就地刷新命令；
2. `upgrade_command`：**改用 if/elif/else**（未知 installer 必须仍返回 `None`，`or` 链会把它
   降级成 curl 命令）；
3. `payload["fix"]`：checkout 时改为「Refresh this editable checkout in place: … Do not replace
   it with a release snapshot」。

两个 helper 放在 **`loopx/python_install_owner.py`**（该模块本就拥有"谁的安装 + 如何更新"），
不放 `doctor.py`：首版实现直接写进 `doctor.py` 后**打破了维护性 ratchet**——实测
`control-plane-maintainability-ratchet-smoke` 报
`unreviewed finding: module_metric_budget:loopx/doctor.py`（`doctor.py` 1518 行 > 1500 行预算）。
移出后 1491 行，ratchet 转绿且**无需新增 reviewed exception**。

用 `.git` 而非「`release_root is None`」作判据的回报：`tests/test_doctor_install_freshness.py`
里用无 `.git` 的 `tmp_path` 的两个既有用例**无需改动即保持绿**；Windows 侧
`loopx/windows_install.py` 的 `COPY_DIRECTORIES` 不含 `.git`，发布副本不会被误判。

### 测试

新增两个用例：`test_editable_checkout_never_recommends_release_channels`（断言两个字段含
`pip install -e . --no-deps --no-build-isolation`，且**不含** `install-local.sh` /
`install.sh` / `pip install --upgrade loopx`）与
`test_release_snapshot_keeps_reporting_the_snapshot_channels`（发布快照分支未被波及）。

## 验证

- **改前基线**：全量 pytest `5 failed / 5564 passed / 25 skipped / 3 errors`（与 029/030 后一致）。
- **改后实测 doctor/update**：`upgrade_command`、`contributor_upgrade_command`、`## Fix`、
  `update plan` 的 `owner_upgrade_command` **全部**变为
  `cd <checkout>` + `<python> -m pip install -e . --no-deps --no-build-isolation` +
  `loopx workflow-skills --install` + `loopx doctor`；`owner` 仍为 `source_checkout`、
  `loopx_apply_supported` 仍为 `False`（fail-closed 未动）。
- **文档守卫**（逐条实跑）：`docs-governance-smoke`、`public_entry/readme-demo-surface-smoke`、
  `readme-star-history-smoke`、`dashboard-installed-quickstart-doc-smoke`、
  `dev-book-publication-smoke`、`dev-book-welcome-wagon-smoke`、`update-notes-archive-smoke`、
  `showcase-catalog-smoke`、`long-task-cadence-policy-smoke`、`pr-review-command-smoke`、
  `codex-cli-first-run-rehearsal-smoke`、`cli-help-manpage-smoke`、`public-adoption-loop-doc-smoke`、
  `control_plane/check-public-boundary-smoke`、`loopx-turn-codex-cli-quickstart-smoke`、
  `issue-fix-capability-guide-smoke`、`repository-hygiene-smoke` —— **全绿**。
- **公共/私有边界**：改动文档与 `CONTRIBUTING.md` 内 0 处绝对家目录路径（`git grep '/home/'`
  为空），符合 `public_safe_outbound` 扫描规则。
- **发布通道未被波及**：`examples/install-local-smoke.py`、`examples/fresh-clone-quickstart-smoke.py`
  的 release-snapshot 断言（含 curl 命令）保持通过。
- **premerge 门**（`loopx canary premerge --from-git-diff --git-diff-base HEAD`，仓内标准门）：
  - catalog canaries **8 条：7 通过 / 1 失败**，失败的 `codex-cli-packaged-install-smoke` 是
    **既存失效**（见下）；`install-local-smoke`、`loopx-update-smoke`、
    `control-plane-maintainability-ratchet-smoke` 与 4 条 issue-fix 全通过；
  - risk profile smokes 8/8 通过；direct checks（含 `py_compile`）通过；
  - public boundary：扫描 12 个改动路径 + 全仓库 → `ok`。
- **全量 pytest（改后 vs 改前基线）**：`5 failed / 5566 passed / 25 skipped / 3 errors`
  vs `5 failed / 5564 passed / 25 skipped / 3 errors` → **失败集合 `diff` 为空**，
  `passed` 差额 **+2** 恰为新增的两个用例。第二轮复查修复后又完整跑了一遍（`after2`）：
  `5 / 5566 / 25 / 3`，与改前基线与首轮改后**两次 `diff` 均为空**。
- **premerge 门（复查修复后重跑）**：仍是 catalog canaries 8 条 7 过 1 失败（同一条既存失败），
  risk profile 8/8、direct checks、public boundary 全通过。
- **`mkdocs build --strict`**：exit 0（仅 2 条既有的 MkDocs-2 弃用横幅）。
- **editable 语义自证**：本轮全部代码改动**没有重装**，`loopx doctor` / `loopx update plan` /
  `loopx workflow-skills --format json` 立即反映新代码——这本身就是"改完即生效"的实测证据。

### 门运行期间不要编辑仓库文件（本轮踩到的假阳性）

首轮 premerge 门报 `failures: 7`，状态全是 `failed_tracked_side_effect`。**原因是我在门运行期间
编辑了 tracked 文件 `operation-logs/000-INDEX.md`**：guard 在门开始时抓 `tracked_before`，
每条 canary 之后比对 `tracked_after - tracked_before`，于是门中途新增的改动被归给了后续每条
smoke。空跑确认：重新在**不改任何文件**的情况下跑门 → `tracked_side_effect_failure_count: 0`，
`tracked_after - tracked_before` 为空。结论：这个字段只能在"跑门期间零编辑"的前提下解读。

### 对抗式复查（第二轮，换角度取证）

**三个新角度**（每个都带可复现证据，不重复首轮检查）：

1. **判据的语义边界**（函数级探针，不改仓库）：`is_editable_source_checkout` 在真 checkout →
   `True`、给了发布快照 → `False`、目录无 `.git` → `False`；并核实
   `repo_root = Path(__file__).resolve().parent.parent`（`doctor.py:927`）确实是 **LoopX 自己的
   checkout**，**不是**用户项目目录——否则判据会在任何 git 项目里误触发，那是灾难性错误。
   同时确认 `release_root` 来自默认命令的解析结果（`command_release_root`）或
   `LOOPX_RELEASE_ROOT` 覆盖，故"快照安装"不会被误判为 checkout。
2. **穷举消费面**：全库 12 个引用 `install_freshness` 的文件逐个排查——
   `loopx/ready_score.py` 只读 `status` 字段（与本次改的字段无关，`ready-score-smoke` 绿）；
   `upgrade_hint` 只在 `install-local-smoke` 做 dict 同一性断言；`payload["fix"]` 只被 markdown
   渲染器读取。补跑三条此前**未跑过**的守卫：`ready-score-smoke` ✅、
   `agent-onboard-host-loop-activation-smoke` ✅、`release/release-version-contract-smoke` ✅。
3. **命令可执行性**：把 doctor 输出的第二条命令原样实跑
   （`python3 -m pip install -e . --no-deps --no-build-isolation --dry-run`）→
   `Would install loopx-1.0.0`、exit 0、无 tracked 变动。

**复查发现并修复的 3 个问题**：

| # | 问题 | 处置 |
| --- | --- | --- |
| 1 | **Windows 上的引号不成立**：`shlex.quote` 产出单引号，cmd.exe 不认（模块内 `doctor.py` 的 `local_install_command` / `no_clone_upgrade_command` 都有 `os.name == "nt"` 分支，新函数却没有） | 新增 `_quote_local_path`：nt 用双引号（cmd 与 PowerShell 都接受），POSIX 仍走 `shlex.quote`。**nt 分支本机无法执行**，属推理性修复，已在代码注释说明 |
| 2 | **测试夹具失真**：`tests/test_self_update_runtime_activation.py` 仍注入旧的 `install-local.sh` 形状，不再代表生产形态 | 夹具改为生产形状（`cd …` + pip -e + skills + doctor），并补 `assert "install-local.sh" not in install_command` |
| 3 | **我的改动造成信息损失**：canary 用户原本能从 `## Fix` 看到 `scripts/install-local.sh`，改后完全消失 | `fix` 文本在 `canary_root` 存在时追加一句「在线 canary wrapper 仍由 `scripts/install-local.sh` 管理」。本机无 canary → 该分支未端到端执行，只做了表达式级合成探针 |

复查期间 doctor.py 一度到 1497 行（预算 1500，仅剩 3 行余量），已把 canary 提示压成单行，
最终 **1496 行**。

### 既存失败（与本轮无关，均经干净 HEAD 实测对照）

1. `examples/codex-cli-packaged-install-smoke.py`：打 tar 时 `FileNotFoundError: <checkout>/LICENSE`
   （该 smoke 的打包清单仍列 `LICENSE`，而本 fork 已在 `c88509106` 删除它）。
   基线与本树**同为 exit=1**，连续 3 次复现稳定。
2. `examples/codex-cli-bootstrap-message-smoke.py`：要求生成消息含 `heartbeat automation`，
   该短语在生成器里已不存在；基线与本树同为 exit=1。
3. `examples/release/codex-cli-no-clone-release-verification-smoke.py`（第二轮复查新发现）：
   要求 `docs/product/runtimes/codex-cli/codex-cli-no-clone-release-verification.md` 含标题
   `Codex CLI No-Clone Release Verification`——该短语**全库仅存在于断言自身**。
   在真基线 `e685f97a3` worktree 上 exit=1 逐字复现，且本轮从未改过它读的三个文件。

三条都属 030 那样的"fork 既存失效"清单，本轮**未动**（超出本次批准范围）。

## 有意不改

- `loopx/install_contract.py` 的 `install_repair_command` / `archive_fallback_install_command`
  静态常量（bootstrap 与 host 消息用）：仍指向上游包通道，改动会牵动 4 个 smoke 与
  `skills/loopx-project/SKILL.md`，超出"小修"范围。新文档注明"忽略它"。
- `codex_skill_roots()` 不扫 `~/.claude/skills`：扩它会改变 `route_conflict` /
  `managed_externally` 语义，本轮只写进文档。
- `docs/book/welcome-wagon.md`：`dev-book-welcome-wagon-smoke` 硬断言其含 PyPI 三连，不动。
- `examples/release/release-readiness-doc-smoke.py` 对 `installing-loopx.md` 的英文断言：
  该 smoke 在更早的 `release-readiness.md` 断言处即已红（中英漂移，见 op-log 023），不追。

## 与上游分叉

新增/改写为 fork 版本：`docs/development/editable-dev-loop.md`（新文件）、`README.md` 试用段、
`CONTRIBUTING.md` 本地开发段、`docs/guides/installing-loopx.md` 顶部与一处正文、
`docs/guides/getting-started.md` 贡献者安装段、`loopx/doctor.py`、`mkdocs.yaml`、
`tests/test_doctor_install_freshness.py`。合并上游时：**保留 fork 版本**；上游若恢复
"checkout 报告贡献者安装器"的行为，按 `is_editable_source_checkout` 的判据与注释重新施加。

## 环境备注

`loopx doctor` 首次运行会创建 `~/.local/share/loopx`（探针写路径），本轮验证即是它的首次运行。
无新增环境性失败。

## 提交/推送

3 个提交，按评审逻辑拆分（文档 / 小修 / 日志），均带 DCO 结尾：

- `463427156` docs: make in-place editable development this fork's only install path
- `36cdb0fda` fix: stop doctor and update from offering release installs for a checkout
- 本日志（`docs: record operation log 031`）
