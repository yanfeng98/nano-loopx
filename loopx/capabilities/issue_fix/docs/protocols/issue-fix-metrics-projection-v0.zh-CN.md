# Issue-Fix 指标投影 v0

> [English](issue-fix-metrics-projection-v0.md)

## 目的

`loopx issue-fix metrics` 为长程 issue-fix goal 生成只读报告 packet。它回答两个
不同问题而不混淆:

1. 报告窗口内公开仓库如何变化;以及
2. 哪些产出可归因于已连接的 issue-fix goal。

该命令从 goal 现有的 feasibility 与 PR lifecycle 领域状态派生 agent 输出。它不
创建指标 ledger 或生命周期状态机。

## 仓库快照输入

期初与当前输入都使用 `issue_fix_repository_reporting_snapshot_v0`:

```json
{
  "schema_version": "issue_fix_repository_reporting_snapshot_v0",
  "repo": "owner/repo",
  "captured_at": "2026-08-01T00:00:00Z",
  "source_url": "https://github.com/owner/repo",
  "open_issues": 42,
  "open_pull_requests": 17
}
```

当前快照另外需要 `flow_since_baseline`:

```json
{
  "flow_since_baseline": {
    "issues_opened": 8,
    "issues_closed": 6,
    "pull_requests_opened": 12,
    "pull_requests_closed": 10,
    "pull_requests_merged": 9
  }
}
```

除非两个存量方程都能自洽,否则 LoopX 拒绝该快照:

```text
baseline open + opened - closed = current open
```

可选的 `issue_states` 与 `pull_request_states` 包含紧凑的公开当前状态。它们让
投影计算 issue-close 归因并刷新过期 PR 状态,而不重写生命周期历史。每个输出
清单行记录其当前状态来自生命周期 ledger 还是更新的仓库快照。

## 补充计数

`issue_fix_metrics_supplement_v0` 可以供应尚未原生进入 feasibility 或 PR
lifecycle 行的 public-safe 计数:

```json
{
  "schema_version": "issue_fix_metrics_supplement_v0",
  "counts": {
    "human_interventions": 2,
    "first_push_ci_passed": 5,
    "first_push_ci_total": 7,
    "loopx_capability_gaps_found": 3,
    "loopx_capability_gaps_fixed": 2,
    "memory_retrievals": 4,
    "memory_verified_patch_influence": 1,
    "memory_stale_results": 1,
    "issue_close_recommendations": 3,
    "issue_close_requests_published": 2,
    "issue_closes_observed": 1,
    "issue_reopens_observed": 0
  }
}
```

这是一个允许列表式的紧凑输入,不是 raw provider payload。缺失计数保持 `null`,
产生 `missing_data` reason code。缺失度量绝不被强制为零。

`loopx issue-fix metrics-supplement` 从 issue-fix 领域状态已拥有的证据与可选的
显式事件证据组成该输入:

```bash
loopx --format json issue-fix metrics-supplement \
  --goal-id public-issue-fix-goal \
  --project /path/to/project \
  --repo public-org/public-repo \
  --period-start 2026-07-01T00:00:00Z \
  --period-end 2026-08-01T00:00:00Z \
  --human-intervention-coverage-start 2026-07-01T00:00:00Z \
  --capability-gap-coverage-start 2026-07-01T00:00:00Z \
  --event-json /path/to/public-safe-events.json \
  --repository-memory-json /path/to/explicit-memory-read-result.json
```

Feasibility 与 lifecycle 行供应被筛选的 issues、triage 结果与自动 terminal
closeout。显式 repository-memory 读取结果供应 retrieval、已验证 patch-influence
与 stale-result 计数。可选 `issue_fix_metrics_event_batch_v0` 为 first-push CI、
人工介入、有用公开评论、重复外部写入与 capability-gap 的 `found` / `fixed` /
`real_callsite_verified` 转换供应稳定事件身份。它还接受四个显式 issue-close
阶段:`issue_close_recommended`、`issue_close_request_published`、
`issue_closed_observed` 与 `issue_reopened_observed`。报告期外的事件被忽略,
重复事件身份被拒绝,capability gap 每个 gap 身份只计数一次。

Issue-close 事件要求 `issue_ref`。已发布请求与 provider 观测到的 close/reopen
转换另外要求公开 HTTPS `evidence_url`;内部建议不需要。Composer 把重复事件折叠
成每个 issue 一行的 `issue_fix_issue_close_activity_v0`,只保留稳定事件身份、
阶段、时间戳与公开证据 URL。例如:

```json
{
  "event_id": "close-request-42",
  "event_type": "issue_close_request_published",
  "issue_ref": "issues_42",
  "occurred_at": "2026-07-12T00:00:00Z",
  "evidence_url": "https://github.com/owner/repo/issues/42#issuecomment-1"
}
```

没有显式事件批次时,composer 读取现有紧凑 LoopX run index,只计数改变路由的
`operator_gate_*` 决策,以及携带 `human_reward_lesson_v0` 修正的 run-bound
`human_reward` 条目。被动聊天、确认与普通正反馈不计入。只有
`--human-intervention-coverage-start` 证明该审计源覆盖整个报告期时,计数才被
发布。更晚或缺失的覆盖起点只把观测计数暴露在 `coverage.human_intervention`
下,并保持指标不可用,因此更早的未投影对话永远不会被重建或静默当作零。

Capability gaps 可以使用同样的不猜测路径,而无需手写事件批次。Agent 显式标记
一个已有 agent todo:

```bash
loopx todo update \
  --goal-id public-issue-fix-goal \
  --todo-id todo_gap_id \
  --role agent \
  --target-capability issue_fix_monthly_metrics \
  --capability-gap-status real_callsite_verified \
  --evidence 'PR merged and the original pilot callsite passed'
```

LoopX 追加一个 typed `capability_gap` rollout event;todo id 是稳定的 gap 身份,
现有 target-capability 元数据仍是人工工作 surface。Composer 每个 todo 折叠一次
`found`、`fixed` 与 `real_callsite_verified` 转换。只有当
`--capability-gap-coverage-start` 覆盖报告期时,才发布这三个计数;否则
`coverage.capability_gap` 暴露部分观测,计数保持不可用。回溯该覆盖只在审计并
补齐期内每个 gap todo 后有效。`fixed` 与 `real_callsite_verified` 标记要求
public-safe 证据;`found` 可以在修复 artifact 存在之前记录。

当公开元数据证明 PR 仍恰好只有一个 commit、且其 check rollup 处于 terminal
(`PASSING` 或 `FAILING`)时,PR lifecycle 收集也在不新增 ledger 的情况下捕获
first-push CI 证据。紧凑证据在后来的 lifecycle upsert 中保留。Supplement 报告
`coverage.first_push_ci`,并且只在报告组中的每个 PR 都有证据时发布
pass/total 计数。部分观测保持不可用,并暴露其观测/合格覆盖,而不是报告有偏
比率。

Composer 不执行 provider 调用,也不推断缺失事件。未提供显式 memory 结果时,只有
该 hook 记录 `read_performed=true`,它才可以使用紧凑 feasibility memory hook;
否则 memory 字段保持缺失。没有事件批次时,有用评论、重复写入与其他事件支撑的
字段保持缺失;只有覆盖门控的人工介入与 typed capability-gap rollout 证据可以
从现有 LoopX 源组成。两种情况下 `loopx issue-fix metrics` 都报告不可用证据,
而不强制为零。

## 归因契约

- 仓库 baseline 只含仓库存量。
- Goal 起点基线处的 agent 输出为零。
- Feasibility 行供应选中的 issues 与路由计数。
- PR lifecycle 行供应可归因 PR 清单、链接、receipts 与最后持久化状态。
- 报告窗口归因使用最新的已验证生命周期事件时间(存在时用当前公开快照的
  `created_at`;否则 `merged_at`、`closed_at` 或 `updated_at`),结合行观测时间。
  关联的 feasibility 决策随其可归因 PR 进入窗口,因此旧的或重放的观测时间戳
  不能抹掉真实产出。
- 无关联的 feasibility 或 lifecycle 行,若其可用事件时间都早于 baseline,则从
  期间排除,而不是迫使调用方重写历史。
- 更新的当前公开快照可以刷新状态,但不能把未归因 PR 加入清单。
- 仓库份额使用显式分子与分母,因此分母为零或证据缺失时,比率是
  `not_available`。
- 开放 PR 是在途工作,不是 terminal 结果。
- 建议是活动,不是关闭。已发布请求是外部可见的尝试,不是关闭。
  `issue_closes_observed` 需要后续 provider 观测到的关闭事件,或当前仓库快照中
  更晚的 `closed_at`。
- 归因关闭转化要求发布请求发生在观测关闭之时或之前。这是有界的运营养归因规则,
  不是关于维护者为何关闭 issue 的因果声明。
- 之后观测到的 reopen 是逆转。Packet 分别报告毛归因转化、reopen 逆转与净转化。
  每项度量对唯一 issue refs 计数,因此重试与重复评论不能放大它。
- PR 关联的 issue 关闭与 close-activity 转化是重叠视图;它们不能作为独立
  terminal 结果相加。

## 边界契约

投影不执行网络读取,也不执行外部写。输入是调用方提供的紧凑公开元数据。输出排除
本地路径、凭据、raw issue 正文、评论、provider 响应、transcripts 与工具日志。

每日公开快照采集与 Kanban/dashboard 渲染是本 packet 之上的独立适配器。它们不得
成为第二事实源。

`loopx issue-fix repository-snapshot` 是有界的公开 GitHub collector。它读取仓库
存量/流量,以及 goal 的 issue-fix 领域状态中已有 issue/PR 引用的当前状态。提供
`--supplement-json` 时,collector 还刷新 supplement 的建议、已发布请求、观测关闭
与观测重开活动中的每个去重 issue ref。这让后续转化/逆转投影使用完整当前状态
快照,而无需维护第二个 issue 列表。该命令从不保留 raw provider payloads。使用
`--retain-material-snapshot` 时,它每天最多写入一行到现有
`issue_fix/repository-snapshots.jsonl` 流,并在存量、流量、issue 状态、PR 状态、
CI 与 review 未变时跳过写入:

```bash
loopx --format json issue-fix repository-snapshot \
  --goal-id public-issue-fix-goal \
  --project /path/to/connected/project \
  --repo owner/repo \
  --repository-baseline-json baseline.json \
  --supplement-json metrics-supplement.json \
  --fetch-public-github \
  --retain-material-snapshot
```

返回的 `snapshot` 对象可以直接作为 `--repository-current-json` 传给
`loopx issue-fix metrics`。调度仍是普通 LoopX `continuous_monitor` todo;
collector 不安装第二个 scheduler,也不发明另一个工作流状态机。

## Monthly Impact 投影

Metrics packet 包含仓库健康、交付、质量、自主性、能力与记忆的稳定 `impact_rows`。
每行保留其 baseline、当前值、delta、适用的分子/分母、公开来源 URL、新鲜度时间戳
与缺失数据原因。

Issue-close 交付为建议、已发布请求、agent 追索的关闭、归因转化、reopen 逆转、
净转化与转化率设置独立行。显式事件批次不覆盖报告期,或尝试过的 issue 既无当前
issue 状态也无 provider 观测的 close/reopen 证据时,这些行保持不可用。

Capability delta 由三个独立行表示:发现的 gaps、修复的 gaps 与在真实 callsite
上验证的 gaps。这保持发现量、交付与产品路径证明可区分,而不是把三者折叠成一个
成功计数。每行在其自身证据支撑的计数存在前保持 `not_available`。

仓库记忆影响同样由三个独立行表示:检索的结果、验证会影响 patch 的结果与验证
过期的结果。这分开使用量与已证明的工程杠杆及检索质量;零作为证据保留,而缺失
计数保持 `not_available`。

通用 Lark sink 把这些行渲染进 `Monthly Impact` 视图,而不存储另一个指标 ledger:

```bash
loopx --format json issue-fix metrics \
  --goal-id public-issue-fix-goal \
  --project /path/to/connected/project \
  --repo owner/repo \
  --repository-baseline-json baseline.json \
  --repository-current-json current.json \
| loopx --format json lark-kanban sync-projection \
  --projection-file - \
  --goal-id public-issue-fix-goal \
  --sink-visibility shared \
  --execute
```

`sync-projection` 接受文件、有界内联对象或 stdin。Setup 是幂等的:已有 boards
通过正常 schema-reconciliation 路径获得指标字段与 `Monthly Impact` 视图。

## 验证

```bash
python3 examples/issue-fix-metrics-projection-smoke.py
python3 examples/issue-fix-repository-snapshot-smoke.py
python3 examples/issue-fix-metrics-supplement-smoke.py
python3 examples/issue-fix-capability-gap-metrics-smoke.py
```
