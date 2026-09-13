# 030 · 退役读 `.github/` 的 canary smoke，并修复自 020 起失效的 install smoke

- **日期**: 2026-09-13
- **分支**: `260906-dev`
- **背景**: 029 只清了 pytest 侧。同一根因（`6a9bebc75` 删整个 `.github/`）在 **canary 清单**
  里还挂着 6 个读 workflow 文件的 smoke——它们在 `examples/` 而不在 pytest 收集面内，
  所以全量 pytest 从不反映它们。盘点时另外发现：`examples/install-local-smoke.py`
  **自 op 020（`2f9a91f89`，2026-09-09）起就已经红了**，与 `.github/` 无关。
- **用户决策**: 按 029 同口径**退役守卫**；**不得破坏 LoopX 正常功能**。

## 实测现状（处理前，逐个实跑，非推断）

| smoke | exit | 首条错误 | 性质 |
| --- | --- | --- | --- |
| `examples/desktop-release-workflow-smoke.py` | 1 | `FileNotFoundError: .github/workflows/desktop-release-artifacts.yml` | 纯 CI |
| `examples/frontstage-pages-workflow-smoke.py` | 1 | `FileNotFoundError: .github/workflows/frontstage-pages.yml` | 纯 CI |
| `examples/full-public-smokes-workflow-smoke.py` | 1 | `FileNotFoundError: .github/workflows/full-public-smokes.yml` | 纯 CI |
| `examples/github-actions-runtime-smoke.py` | 1 | `AssertionError: missing workflow reference for actions/checkout` | 纯 CI |
| `examples/update-notes-archive-smoke.py` | 1 | 读 `WORKFLOW` 失败 | 混合 |
| `examples/install-local-smoke.py` | 1 | **`line 264` 断言 `outer host turn identity` 不在 help 里** | 混合，另有两条必失败断言 |

**"处理前"的取证方式**：把 4 个待删 smoke 从 `HEAD` 取出、以 `examples/zzz-precheck-*.py`
临时名放回 `examples/` 下实跑（保证 `Path(__file__).parents[1]` 解析出真实仓库根），
跑完即删；避免拿 `/tmp` 里的副本得出"路径不对"的假证据。

## 变更清单

### 删除（4 个纯 CI smoke + 1 个零引用配置）

`desktop-release-workflow-smoke`（138 行）、`frontstage-pages-workflow-smoke`（146 行）、
`full-public-smokes-workflow-smoke`（90 行）、`github-actions-runtime-smoke`（53 行）——
四者**唯一断言对象就是已删的 workflow 文件**（逐个读过：读文件 → 断言 YAML 内容 →
`full-public` 那个还拿 shard 矩阵容量对 smoke 清单）。连同 `sonar-project.properties`
（**全库 0 引用**，其消费者 SonarCloud workflow 已随 `.github/` 一起消失，且指向
上游 `huangruiteng_loopx` 项目）。

smoke 发现机制是**glob**（`loopx/canary/runner.py` 文档串：bounded to
`examples/**/*-smoke.py`），删文件即自动退出清单，**无需改任何注册表**；实测清单
498 → **494**，恰好 −4。

### 裁剪（2 个混合 smoke）

- `examples/update-notes-archive-smoke.py`：删 `WORKFLOW` 常量、`validate_project_automation()`
  里 9 条 workflow 断言、`main()` 路径表里的 `WORKFLOW`；**保留** generator 断言与四组
  文档/索引检查（这是该 smoke 的真实主体）。
- `examples/install-local-smoke.py`：见下节。

### 文档（3 处）

- `docs/product/surfaces/frontstage-two-surface-strategy.md`：删掉"用
  `frontstage-pages-workflow-smoke.py` 验证 Pages workflow 安全"这一条，并写明它随
  `.github/` 一起退役；
- `docs/update-notes/README.md`、`docs/update-notes/automation.md`：把"仓库随附第一版
  `.github/workflows/update-notes.yml`"改为"上游曾随附、**本 fork 已移除**、generator
  脚本仍在"。两处措辞**刻意保留 workflow 路径字符串**，因为
  `examples/update-notes-archive-smoke.py` 的 `validate_automation_plan()` 会断言它存在
  （改文案而不改该断言会立刻打破该 smoke）。

## 关键发现：install-local-smoke 的三条陈旧断言

1. **line 264（自 020 起红）**：断言安装出的 wrapper 的 `--help` 含
   `outer host turn identity`。该短语原本只存在于 `scripts/codex_app_apply_rrule.py`
   （Codex App fallback receipt identity 说明），**由本 fork 的 op 020（`2f9a91f89`）删除**；
   实测 `git grep 'outer host turn identity' 2f9a91f89^` 有两处、HEAD 只剩断言自身。
   020 当时确实改了本 smoke 的 14 行，但保留了这条断言 → 从那天起必失败。
   处置：锚点改为 CLI 自己的横幅
   `LoopX keeps long-running agent work moving with durable state and evidence.`
   （`loopx/help_surface.py:383`，同一句也被 `tests/test_cli_entrypoint.py:190` 断言），
   保留"安装出的 wrapper 能解析到发布树并打印真实 help"这一守卫意图。
2. **line 277 / 279**：断言发布树里有 `.github/workflows/update-notes.yml` 与 `LICENSE`。
   两者都已被本 fork 删除（`6a9bebc75` / `c88509106`）。**安装器本身没有坏**：
   `scripts/install-local.sh:239-245` 的 `copy_path()` 带 `[[ -e "$src" ]]` 守卫，
   源缺失即静默跳过（同一函数被用于 `loopx/`、`docs/`、`apps/` 等 12 个路径）。
   处置：删这两条断言并写明原因；保留紧随其后的
   `docs/development/contributor-tasks.md` 作为发布树载荷标志。

**功能未受影响，且被实测证明**：修复后 `examples/install-local-smoke.py` 端到端
**`install-local-smoke ok`（exit 0）**——它会真的跑一遍 `scripts/install-local.sh`
并在临时 HOME 里检查发布树、wrapper、`release.json` 清单与 doctor 输出。

## 验证

- **清单与注册表**：`build_smoke_fleet_health()` → `inventory 498 → 494`、`ok: True`，
  4 个已删 smoke **不在清单内**；`loopx canary smoke-health` 同源。
- **受影响的 smoke 全绿**：`examples/update-notes-archive-smoke.py` → `ok`；
  `examples/update-notes-generator-quality-smoke.py` → `ok`；
  `examples/install-local-smoke.py` → `ok`（exit 0）；
  `examples/canary/smoke-fleet-health-smoke.py` → `ok inventory=494 owners=327 owner_gaps=167`。
- **canary 目录其余 smoke**（`examples/canary/*.py` 共 **12** 个）：**9 绿 / 3 红**；
  3 个红的是 `catalog-planner-smoke`、`canary-promotion-readiness-smoke`、
  `pytest-smoke-suite-facade-smoke`，它们在**干净 HEAD worktree（`af704f2a3`）上
  逐字复现、两侧 exit 全部同为 1** → **与本轮无关的既存失败**。
- **静态与文档**：`ruff check` 两个改动文件 All checks passed；
  `docs-governance-smoke` → `ok`；`repository-hygiene-smoke` → `ok`；
  `mkdocs build --strict` → exit 0。
- **全量 pytest**（口径同 015–029）：

| | collected | passed | failed | skipped | errors |
| --- | --- | --- | --- | --- | --- |
| 029 后本树 | 5594 | 5564 | 5 | 25 | 3 |
| 本轮改动后 | 5594 | 5564 | 5 | 25 | 3 |
| 差额 | 0 | 0 | 0 | 0 | 0 |

  **预期就是 0 差额**：本轮只动 `examples/` 与 `docs/`，两者都不在 `pytest tests/` 的
  收集面内。实测两次运行的 8 条 `FAILED`/`ERROR` 行 `diff` **为空**（逐字一致）。
  这也是本 op 必须用**直接运行**而非全量 pytest 取证的原因——pytest 对 `examples/`
  的失效完全沉默。

## 有意不改

- `scripts/desktop_release_artifacts.py`：`desktop-release-workflow-smoke` 是它唯一的
  in-repo 消费者，删 smoke 后它成为孤立脚本。但它仍是**可用的发布助手**（手动发布路径
  需要它），删它不属于"退役已失效守卫"，故保留并在此记录。
- `loopx/canary/planner.py` 里 `install-local-smoke` / `update-notes-archive-smoke` 的
  profile check 条目：两个 smoke 仍在，无需改动。
- 上游 `.github/…` 链接（README、history、technical-directions、welcome-wagon）：
  指向 upstream 仓库，非坏链（同 029）。

## 与上游分叉

新增 fork 版本文件：`examples/install-local-smoke.py`、`examples/update-notes-archive-smoke.py`、
`docs/update-notes/{README,automation}.md`、`docs/product/surfaces/frontstage-two-surface-strategy.md`；
4 个 smoke 是整文件删除，上游 merge 会**带回**它们，届时处置：**保留删除**（其断言对象
`6a9bebc75` 起已不存在），并按 029 口径保留代码内提交号注释。

## 环境备注

无新增环境性失败。全量 pytest 的 3 个 collection error 与本机 site-packages 同名 `tests`
包遮蔽同源（见 029「环境备注」），与本轮无关。本轮验证产生的 `output/`（mkdocs 构建产物，
45MB）与 `/tmp` 副本已清理；`git worktree` 基线用后即删。

## 提交/推送

4 个提交，按评审逻辑拆分（smoke 退役 / install smoke 修复 / 文档 / 日志）：

- `408b3a089` test: retire the canary smokes that read this fork's deleted .github
- `566982775` fix: repair install-local-smoke assertions stale since op 020
- `8155d92b3` docs: point the update-notes and frontstage pages at fork reality
- `61abe071f` docs: record operation log 030 (workflow-reading smoke retirement)

按用户指示推送：`8ee7d9701..61abe071f`（与 029 的 3 个提交合并为一次 push）。
