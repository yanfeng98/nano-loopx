# 029 · 退役 `.github/` 删除遗留的 CI-only 守卫

- **日期**: 2026-09-13
- **分支**: `260906-dev`
- **背景**: `c88509106`（2026-09-07 删 `LICENSE`/`LICENSE-MIT`）与 `6a9bebc75`（删整个
  `.github/`）之后，一批**唯一内容就是证明 CI wiring** 的守卫失去了被断言的对象。
  015–028 已把它们如实记为"既存失败"而未处置：022 把 `python_ci_workflow` 列进
  "4 预存 collection errors"，027 把 `.github/` 缺失族（`test_python_ci_workflow`、
  `test_sonarcloud_workflow` ×3、canary fleet health ×3）列进 `11 failed + 4 errors` 基线。
- **用户决策（1 项）**: **退役守卫，不恢复 `.github/`**。同一决策方向下的"不恢复许可证"
  沿用 028。

## 实测现状（处理前）

| 守卫 | 症状 | 证据 |
| --- | --- | --- |
| `tests/test_python_ci_workflow.py` | **收集期崩溃** | 模块级 `read_text` → `FileNotFoundError: .github/workflows/python-tests.yml` |
| `tests/test_sonarcloud_workflow.py` | 3 failed | `FileNotFoundError: .github/workflows/sonarcloud.yml` |
| `tests/canary/test_smoke_fleet_health.py` | 3 failed | `smoke_health.py` 读不到 workflow → `workflow_missing_scripts` 非空 → `ok=False` |

**关键不是"红几个测试"**：收集期抛错会让 pytest **整场中断**。实测
`pytest -q tests/canary/test_smoke_fleet_health.py tests/test_python_ci_workflow.py`
→ `Interrupted: 1 error during collection`，那 6.8 秒的 canary 测试**一个都没跑**。
与 028 形状相同：守卫在最前面就抛，其后的检查从未真正执行过。

## 变更清单

### pytest 侧

- 删除 `tests/test_python_ci_workflow.py`（119 行）——唯一主题是已删的
  `.github/workflows/python-tests.yml`（分片、coverage 门槛、触发范围）；
- 删除 `tests/test_sonarcloud_workflow.py`（40 行）——唯一主题是已删的
  `.github/workflows/sonarcloud.yml` 与它调用的 `python-tests.yml`；
- `tests/canary/test_smoke_fleet_health.py`：删去 `workflow_contract.missing_scripts == []`
  一条断言，其余 cadence / owner / receipt 断言原样保留。

### canary 契约

`loopx/canary/smoke_health.py`：

- 删 `PR_FAST_WORKFLOW` 常量、workflow 文件读取与 `workflow_missing_scripts`
  （含它在 `ok` 合取式里的那一项）；
- 删 `pr_fast_workflow_drift` 警告分支；
- 删 payload 的 `workflow_contract` 字段（**`schema_version` 保持
  `smoke_fleet_health_v0` 不变**，`release_commit_qualification.py:41` 的映射不受影响）；
- **保留** `PR_FAST_SCRIPTS` 与 `pr_fast` cadence，降级为 **tier 标签**，并加注释写明
  fork 原因与提交号（`6a9bebc75`）。

### 消费方

- `examples/canary/smoke-fleet-health-smoke.py`：删去同一条 `workflow_contract` 断言。

### 文档

- `docs/development/testing-and-quality.md`：把"`.github/workflows/python-tests.yml`
  会在相关 Python PR 上运行这条快速通道"改为 fork 事实（**这条快速通道在本 fork 没有
  CI 承载者，只能本地/隔离沙箱手工运行**），并把分片细节段落标注为
  **上游 CI（本 fork 不存在）**，保留以便合并上游时对照。

## 有意不改

- **`pr-fast:python-tests` owner 标签与 `pr_fast` cadence 保留**：两者描述的是"这一条属于
  快速门那一档"，不是对某个文件的断言；且 payload 的 cadence 集合与 `CADENCE_IDS`
  同上游 schema，改名会扩大分叉面。标签名里的 `python-tests` 是历史来源，非现行声明。
- `loopx/canary/premerge.py:65` 的 `.github/`、`loopx/canary/qualification_profiles.py:288`
  的同一路径：都是**惰性匹配 token**——若未来有人新增 `.github/` 文件仍应命中，且它们不
  产生任何假声明。按 028 口径（"理由是否仍成立"）判定保留。
- README、`docs/project/history.md`、`docs/project/technical-directions.md`、
  `docs/book/welcome-wagon.md` 中的 `.github/…` 链接：**指向 upstream 仓库**
  （`github.com/huangruiteng/loopx`），上游文件仍在，不是坏链。

## 验证

- **全量 pytest 基线对照**（口径同 015–028：跑 `tests/`，`--continue-on-collection-errors`）：

| | collected | passed | failed | skipped | errors |
| --- | --- | --- | --- | --- | --- |
| 基线（027 在同一环境测的干净 HEAD `e2fbeb689`） | 5597 | 5561 | 11 | 25 | 4 |
| 本树 | 5594 | 5564 | 5 | 25 | 3 |
| 差额 | **−3** | **+3** | **−6** | 0 | **−1** |

  **差额可逐项归因，且预测先于测量**：测量前先写下预期 `collected −3`（删掉的
  `test_sonarcloud_workflow.py` 含 3 个测试）、`failed −6`（sonarcloud ×3 + canary fleet
  health ×3）、`errors −1`（`test_python_ci_workflow.py`），**实测逐项命中**。
  基线取自 027 在同一环境测得的干净 HEAD 对照；其后的 `1a14fe558`（mkdocs 排除表）与
  `8ee7d9701`（hygiene smoke）不触碰 `tests/` 与 `loopx/`，基线对起点仍成立。
- **残存失败与本次无关、逐条对得上 027 记录的既有清单**：`test_repository_change_window`
  （本机 git 不支持 `worktree list --porcelain -z`）、scheduler ack ×2、dashboard launcher、
  pr-program snapshot（5 failed）；`outbound_guidance` / `refresh_checkpoint_recovery` /
  `shared_goal_alignment_cli`（3 errors，本机 site-packages 遮蔽，见「环境备注」）。
  **`.github/` 缺失族已归零**。
- **canary 表面端到端**：`tests/canary/test_smoke_fleet_health.py` → **3 passed**；
  `examples/canary/smoke-fleet-health-smoke.py` → `ok inventory=498 owners=329 owner_gaps=169`；
  `loopx canary smoke-health`（CLI 真实入口）→ `ok: true`、`pr_fast: 1`、`inventory: 498`。
- **无残留引用（精确到字段语义）**：smoke-fleet payload 的 `workflow_contract` 字段与
  `pr_fast_workflow` 字串除本轮改动外 **0 命中**。`git grep workflow_contract` 仍有 4 处
  命中，但**全部是无关子串**：`issue_fix_workflow_contract_v0`（issue-fix 协议名，
  见 `loopx/capabilities/issue_fix/docs/protocols/…`、`examples/issue-fix-workflow-contract-smoke.py`）
  与 showcase 文案里作为普通词的 "workflow contract"——**不是**本次删掉的字段。
  同理 `missing_scripts` 仅剩两处同名而无关的局部量：`smoke_health.py:345` 的 receipt
  覆盖度（`inventory_scripts - observed_scripts`）与 `runner.py:399` 的脚本过滤，
  二者都不读 workflow 文件，**未误删**。
- **无外部消费方**：`workflow_contract` 只被本轮的测试与 example smoke 读取；含 fixtures
  与 dashboard 在内的 `.json` / `.ts` / `.tsx` / `.yml` 载体 0 命中（唯一的 `.html` 命中
  是上述 issue-fix showcase 文案）。
- **静态检查**：`ruff check` 三个改动文件 **All checks passed**；`mypy` →
  `Success: no issues found in 21 source files`。
- **文档守卫**：`examples/docs-governance-smoke.py` → `ok`；
  `examples/repository-hygiene-smoke.py` → `ok`（该文件是 028 的产物，本轮未触碰）。

## 与上游分叉

`loopx/canary/smoke_health.py`、`tests/canary/test_smoke_fleet_health.py`、
`examples/canary/smoke-fleet-health-smoke.py`、`docs/development/testing-and-quality.md`
现均为 **fork 版本**。未来 merge 上游若恢复 `workflow_contract` 或这两条断言，处置：
**保留 fork 版本 + 保留代码内的提交号注释**（`6a9bebc75`）。

## 未处理（建议转 030）

同一个 `6a9bebc75` 还让**另外 6 个在册 canary smoke** 失去断言对象（全部实测在 498 条
`daily_full_public` 清单内，本轮只做只读盘点、未执行也未改动）：

| smoke | 读的对象 | 备注 |
| --- | --- | --- |
| `examples/desktop-release-workflow-smoke.py` | `.github/workflows/desktop-release-artifacts.yml` | |
| `examples/frontstage-pages-workflow-smoke.py` | `.github/workflows/frontstage-pages.yml` | |
| `examples/full-public-smokes-workflow-smoke.py` | `.github/workflows/full-public-smokes.yml` | |
| `examples/github-actions-runtime-smoke.py` | `.github/workflows/` 目录 | |
| `examples/update-notes-archive-smoke.py` | 同一 workflow + 9 条断言 | 配套文档 `docs/update-notes/README.md:35`、`automation.md:22` 仍写"仓库随附" |
| `examples/install-local-smoke.py` | 发布树里的 `.github/workflows/update-notes.yml` **与 `LICENSE`** | 两条断言都是 `6a9bebc75`/`c88509106` 之后必然失败 |

因它们在 `examples/` 而不在 `pytest tests/` 的收集面内，**全量 pytest 不反映它们**；
本轮不擅自扩大手术范围，留待用户决定是否并案。

## 环境备注

本机 site-packages 存在同名 `tests` 包
（`~/miniconda3/lib/python3.12/site-packages/tests/__init__.py`）遮蔽仓库 `tests/`，
使 3 个 `from tests.… import` 文件在**本机**收集期报错
（`outbound_guidance`、`refresh_checkpoint_recovery`、`shared_goal_alignment_cli`；
`e34fd6b15` 已记录为"仅本机环境，CI 干净环境正常"）。与本次改动无关，
基线口径因此沿用 015–028 的 `--continue-on-collection-errors`。

## 提交/推送

3 个提交，按评审逻辑拆分（守卫退役 / 文档 / 日志），均带 DCO 结尾：

- `89e5e215a` test: retire CI-only guards invalidated by this fork's .github removal
- `4b39a392b` docs: state that the fast gate has no CI carrier in this fork
- `af704f2a3` docs: record operation log 029 (CI-only guard retirement)

按用户指示推送：`8ee7d9701..61abe071f`（含 030 的 4 个提交，一次 push 完成）。
