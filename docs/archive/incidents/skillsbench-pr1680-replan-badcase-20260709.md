# SkillsBench PR #1680 Replan 坏例

> [English](skillsbench-pr1680-replan-badcase-20260709.md)

日期:2026-07-09

读者对象:LoopX 维护者、quota/status 所有者、todo 投影所有者、benchmark
runner 所有者,以及 heartbeat 自动化所有者。

## 摘要

SkillsBench Goal xhigh 工作因 benchmark egress 代理修复合并后停止。benchmark
runner 不是直接阻塞点。控制面继续暴露一条安静 monitor 通道,其持久下一个动作
仍说:保持 PR #1680 处于 review-required 状态,并在审阅/合并后重跑
verifier/bootstrap 失败的案例。

该外部条件早已满足。GitHub 报 PR #1680 已于 `2026-07-08T18:14:59Z`
(`2026-07-09T02:14:59+08:00`) 合并。后续 LoopX quota/status 读取仍然选择了:

```text
quota.should_run = false
quota.effective_action = monitor_quiet_skip
goal_frontier_projection.replan_required = false
agent_monitor_due_count = 0
active_state_next_action = keep PR #1680 in review-required state; after
  maintainer review/merge, rerun verifier/bootstrap-failure SkillsBench cases
```

结果是"存活但闲置"的自动化:heartbeat 保持活动且安静,但没有投影出任何可运行
的 SkillsBench 重跑 todo。

## Public-Safe 形态

本记录有意排除原始 SkillsBench 任务文本、原始轨迹、verifier 输出、私有启动
材料、凭据与本地工件路径。可复用的形态是:

```text
external_evidence.state = merged
durable_next_action = wait for that same external merge/review condition
quota.effective_action = monitor_quiet_skip
interaction_contract.agent_channel.must_attempt = false
goal_frontier_projection.replan_required = false
ready_successor_count = 0
observable problem = no runnable rerun todo after the unblock signal landed
```

公开证据足以重现这个控制面矛盾:

```bash
gh pr view 1680 --repo huangruiteng/loopx \
  --json state,mergedAt,reviewDecision,headRefName,mergeCommit

loopx --format json quota should-run \
  --goal-id loopx-meta \
  --agent-id codex-main-control
```

## 问题出在哪里

1. **外部合并证据没有成为实质转换。** PR #1680 变为 `state=MERGED` 应关闭等待
   条件,并暴露可运行的重跑 frontier 或具体 blocker。
2. **持久下一个动作保持过时。** 合并后,活动状态仍指示 agent 保持 PR 处于
   review-required 状态。这让目标看起来像在有意等待,即使它指名的解锁条件已经
   落地。
3. **静默 monitor 语义掩盖了过时条件。** `monitor_quiet_skip` 只在没有实质变化
   时才正确。本例中一个公开外部依赖发生了变化,但 monitor 通道报告没有应到的
   monitor,也没有 replan 需求。
4. **没有投影继任重跑 todo。** 更广泛的 SkillsBench 工作本应以关于
   verifier/bootstrap 重跑的推进 todo 恢复,遵循必需的 benchmark egress 代理与
   benchmark_core 紧凑 ledger 标准。而可见的可运行 frontier 退到了无关或缺失
   能力的旧工作上。
5. **Agent 行为助长了停滞。** Agent 遵循 CLI 事实源并保持安静,但它本应把
   "等待 PR #1680 合并"与"PR #1680 已合并"之间的不匹配当作自修复触发,而不是
   等着用户指出。

## 为什么 Replan 没有恢复

Replan 没有触发,因为状态投影说没有自主 replan 义务:

```text
goal_frontier_projection.replan_required = false
monitor_only_lanes.quiet_until_material_transition = true
deferred_successors.ready_count = 0
acceptance_gaps = []
```

这是核心产品缺口。安静 monitor 通道需要一种方式去重新检查它正在等待的外部
事实。如果该事实已经为真,该通道就不能继续作为未变化的 monitor-only 状态。

这个案例特别微妙,因为 GitHub 仍可能在已合并 PR 上报告
`reviewDecision=REVIEW_REQUIRED`。LoopX 必须把终局 PR 状态作为更强信号:
`state=MERGED` 满足合并等待,无论过时的审阅决策元数据如何。

## 期望语义

当持久下一个动作或 todo `resume_when` 条件点名一个外部公开依赖时,LoopX 应把
终局依赖转换当作实质 frontier 变化。

| 条件 | 期望的 LoopX 行为 |
| --- | --- |
| PR 等待目标是 open | 静默 monitor 可继续直至到期或过期 |
| PR 等待目标是 merged | 关闭或取代该 monitor,然后投影继任者动作 |
| PR 状态与审阅元数据矛盾 | 合并等待优先取终局 `state=MERGED` |
| 继任者无法运行 | 记录带缺失能力或缺失材料的具体 blocker |
| 没有继任者存在 | 发出 `autonomous_replan_required`,而不是 monitor quiet skip |

## 后续契约

### P0:外部依赖恢复投影

为引用公开 PR 依赖的持久下一个动作与 todo `resume_when` 条件添加 public-safe
投影规则。PR 合并后,被阻塞或推迟的工作应变为就绪、被带全新继任者的取代,或
产生具体 blocker。

### P0:Monitor Quiet 矛盾防护

当持久下一个动作说等待某个外部条件,而一次廉价的公开读取证明该条件已满足时,
`monitor_quiet_skip` 应是非法的。这种情况下,quota/status 应暴露
`autonomous_replan_required` 或可运行的继任者。

### P1:终局 PR 状态优先

对于 PR 合并等待,终局 PR 状态必须胜过审阅元数据。一个已合并但 `reviewDecision`
仍为 `REVIEW_REQUIRED` 的 PR,在工作流目的上就是已合并。

### P1:坏例回归 Smoke

添加一个聚焦 fixture,其中:

```text
active_state_next_action references "after PR #1680 review/merge"
public_pr_state.state = MERGED
public_pr_state.reviewDecision = REVIEW_REQUIRED
monitor_due_count = 0
```

期望的 quota/status 结果不是 `monitor_quiet_skip`;而是可运行继任者、具体
blocker 或自主 replan 义务。

## 责任归属

主要产品归属是 LoopX 控制面投影:状态模型没能把公开外部解锁事件转译成新的
可运行 frontier。Agent 也有流程责任:当 CLI 说安静、但公开证据与持久下一个
动作矛盾时,agent 应调用自修复并写一个坏例记录,而不是等待。
