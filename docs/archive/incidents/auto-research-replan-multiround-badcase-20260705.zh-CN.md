# 自动研究 Replan 与多轮演示坏例

> [English](auto-research-replan-multiround-badcase-20260705.md)

日期:2026-07-05

读者对象:LoopX auto-research 所有者、quota/status 维护者、todo/replan
所有者,以及多 Agent 演示维护者。

## 摘要

一个可见的 auto-research 演示进入了这样的状态:operator 期望多 Agent 研究与
改进继续推进,但活动通道没有进入 replan。可见的体验看起来也像一次短暂的单次
遍历,而不是持续数分钟的角色化研究。更早的状态更新可能把 worker-loop 管道、
摘要工件或 pane 内的 tick 当作"有意义的多轮研究"证明,从而使情况看起来比
实际好。

可复用的失败包含两部分:

1. 一次完成的 auto-research 推进没有为当前 agent 留下可运行的继任者,但
   quota 仍选择静默 monitor,而不是有界的 replan 动作。
2. 演示对"研究机制已推进"与"可见研究改进了工件"的区分太弱,内部循环或
   摘要可能被误认为真正的协作研究。

本记录是 public-safe 的。它不包含原始活动状态体、本地运行时路径、原始日志、
轨迹、凭据、私有工件或 operator 专属规划上下文。

## 观察到的 Public-Safe 形态

相关 quota 形态是:

```text
quota should-run --goal-id <goal-id> --agent-id <side-agent>
should_run = false
effective_action = monitor_quiet_skip
interaction_contract.mode = monitor_quiet_skip
user_todo_summary.open_count = 0
current_agent_claimed_advancement_count = 0
current_agent_claimed_monitor_count > 0
first_executable_items = 0
goal_frontier_projection.replan_required = false
agent_todo_summary.todo_succession_warning =
  completed_advancement_without_successor
```

重要细节是:LoopX 确实注意到了继任问题,但只是作为一个告警。被选中的交互
仍然告诉 agent 保持安静。这对纯 monitor 通道是合理的;当 monitor-only 形态
是由一个丢失了下一步可执行步骤的未完成推进切片造成时,它就是错的。

## 为什么没有进入 Replan

LoopX 选择了最容易服从的局部事实:没有用户 todo、没有当前 agent 推进候选,
剩余已认领工作是 monitor 或 blocker 类。按这种视图,`monitor_quiet_skip`
是合法的 no-spend 动作。

缺失的规则是:当以下条件全部为真时,当前 agent 的
`completed_advancement_without_successor` 告警应提升为可执行的路由修复:

```text
completed advancement was tracked for successor continuity
no current-agent advancement candidate exists
goal or operator intent still expects follow-up advancement
no harder safety gate is present
```

在这种状态下,quota 不应要求 agent 做普通交付。它应要求一个受限的控制面
replan:新增/链接一个继任 todo,用带原因的 `no_followup=true` 标记,或把
下一个 frontier 显式移交给另一个 agent。

## 为什么看起来像单轮研究

实现已经修正了一条早期"假路径":`demo/auto_research/worker_runtime.py`
中真实的研究动作现在返回"需要手动研究"的结果,而不是静默编造研究输出。
这是正确的事实性边界。

但可见的产品问题仍在:几个 surface 仍用机制性词汇描述进展,如 worker-loop
轮次、pane 内 tick、紧凑摘要或预计算的指标摘要。这些都是有用的管道信号,但
不等同于可见的角色化研究。高质量的演示应展示:角色阅读契约、提出假设、改变
或评估工件、记录证据、审阅它,然后路由下一个 frontier。如果这条链只发生一次,
UI 就应说发生了一次可见的研究遍历,而不应暗示有多轮改进。

KNN 演示可以是真实的:生成的 workspace 通过
`demo/auto_research/knn_demo_workspace.py` 提供基线方案、可编辑作用域、
受保护作用域和 eval 命令。当预设创建该契约时,问题文本不需要承载基线。坏例
不在于 KNN 缺少基线,而在于可见流程没有让连续的角色化研究与改进足够明显,
控制面又放任后续 frontier 消失。

一个具体的可见运行子案例是:evaluator pane 在 executor 追加证据之前醒来。
这不是添加中央工作流驱动器的理由。正确的第一版演示形态是:外部由 Codex CLI
pane/goal 驱动,内部由 LoopX state/frontier 驱动:evaluator todo 应能在 executor
的证据步骤上恢复,所以 evaluator 应该等待,而不是记录 `evidence=0` 并提前
关闭自己。

一次后续可见运行确认了较小的修复路径:

- evaluator 种子 todo 通过 `resume_when` 等待 executor 的 dev-evidence todo,
  因此第一个 evaluator turn 报告等待状态,而不是在 `evidence=0` 上关闭。
- 修复后的 wake 广播器必须只在被请求的 tmux session 内解析 pane,并锁定
  稳定的 lane 元数据,而不是可变的 Codex pane 标题或宿主机上所有 tmux pane。
- 长时间运行的 Codex TUI pane 在捕获窗口中可能只显示底部输入提示。醒来就绪
  与提交重试必须识别这种 footer 形态,并在固定提示尾部仍留在输入框时重试。

有了这些修复,一次真实可见的 KNN 运行通过 executor 证据、evaluator 审阅和
curator 继任者交接继续推进,而没有隐藏的工作流驱动器。剩余的产品问题是:这些
状态中有多少应被总结为紧凑的 `research_contract_v0` 投影,使未来运行能在不读
pane 转录的情况下解释当前阶段。

## 责任划分

这部分是 LoopX 控制面缺口:

- 没有继任者的已完成推进被投影为告警,而不是可执行的 replan 义务。
- 静默 monitor 优先于"修复缺失的继任者",即使当前通道没有剩余推进 frontier。
- Auto-research 状态还没有紧凑的研究契约投影,用以说明当前研究阶段、需要
  哪些证据,以及何时必须投影下一个角色 todo。

它也是 agent/流程失败:

- 我把机制证据当作产品证据,夸大了 worker-loop 或 tick 型进展的意义。
- 我在没有先确保继任 todo、显式 `no_followup` 理由或交接的情况下,就关闭或
  静默处理了该切片。
- 我没有足够早质疑矛盾:operator 想要持续可见的研究,而 quota 允许
  monitor-only no-op。

## 期望语义

Auto-research 需要一个小的状态级契约,而不是什么研究专属大框架。一个最小
契约应当足够:

```json
{
  "schema_version": "research_contract_v0",
  "question": "public-safe research question",
  "current_stage": "contract|hypothesis|dev_eval|holdout_eval|review|replan",
  "target": {
    "visible_rounds_min": 2,
    "evidence_required": ["hypothesis", "dev_eval", "holdout_eval", "review"]
  },
  "frontier": {
    "next_role": "research-executor",
    "next_action": "run_dev_eval",
    "claim_boundary": "public-safe editable/protected scope"
  },
  "gates": {
    "user_required": false,
    "private_material_required": false
  }
}
```

该契约应是状态,而不是用户层或 auto-research 入口层的额外业务逻辑。用户
surface 保持薄:启动一个话题,并可选地选择一个 preset/workspace。
Auto-research 也保持薄:创建契约与角色 frontier。通用的 todo/quota/replan
机制让下一个可执行步骤保持存活。

## 后续工作

### P0:把缺失继任者提升为 Replan

当当前 agent 完成的推进具有 `succession_tracked=true`,且没有继任者或显式
`no_followup` 理由时,quota 应选择一个有界的 replan/writeback 动作,而不是
`monitor_quiet_skip`。允许的动作只是控制面修复:新增/链接继任 todo、记录
终局理由,或移交给正确的角色。

### P0:让自动研究继任状态为状态驱动

在 LoopX state 中引入最小有用的 `research_contract_v0` 投影。它应标识当前
研究阶段、期望证据、下一角色、下一动作与 gate 状态。如果契约未满足且没有
可运行 frontier,replan 必须投影下一个角色 todo。

### P0:停止仅凭管道声称多轮研究

可见的多轮验证必须要求可见的角色化证据,以及至少两次通过角色集的集体遍历。
Worker-loop 摘要、pane 内 tick 计数和通用评估摘要可以支持诊断,但绝不能单独
作为研究改进呈现。

### P1:改善可见 Pane 体验

每个研究 pane 的首屏应强调角色实际的研究内容:假设、编辑/评估结果、证据、
审阅决策与下一 frontier。除非角色确实处于修复模式,否则不应把 quota JSON、
转录路径或诊断命令作为前景。

### P1:收紧无后续完成

Auto-research 完成应避免默认设置终局 `no_followup=true`。只有当研究契约已
满足、存在更硬的 gate,或完成时记录了 public-safe 的终局理由,角色才能在没有
继任者的情况下关闭 todo。

## 相关模式

- `monitor_replan_noop_loop`
- `agent_scoped_replan_broadcast_gap`
- `todo_succession_gap`
- `tiny_turn_under_delivery`
- `agent_scoped_no_candidate_gap`
- `agent_scoped_replan_precedence_gap`
