# 仅 Monitor Replan 停滞事件

> [English](monitor-only-replan-stall-incident-20260621.md)

日期:2026-06-21

读者对象:LoopX 维护者、heartbeat 提示词生成器所有者、status/quota 所有者、
自修复 skill 所有者,以及 side-agent 控制器作者。

## 摘要

一个 side-agent 交付目标进入了停滞状态:控制面反复记录 monitor-only 或
replan/自修复风格的运行,但工作 frontier 实际上没有变化。用户通道没有被
阻塞:没有打开的用户 todo,也没有用户问题。预期状态是以下之一:

- 保持安静,因为该目标只是在等待一个实质的外部信号;或
- 当 monitor 无法再推进目标时,提升一个具体的可运行 agent todo、blocker、
  继任者或取代性路由。

实际上,系统在静默 monitor 状态与自主 replan 措辞之间徘徊。这主要不是缺少
用户回答,而是控制面质量问题:agent 看到了足够多的"动作感"语言而继续尝试,
但不足以逃出循环的机器可验证状态变化。

## Public-Safe 形态

本案例有意不包含原始项目路径、私有任务名、内部文档链接、benchmark 轨迹或
本地活动状态载荷。可复用的形态是:

```text
quota.effective_action = monitor_quiet_skip
interaction_contract.user_channel.action_required = false
user_todo_summary.open_count = 0
agent_todo_summary.open_count = 1 monitor-style item
recent_history = repeated quota_monitor_poll / replan / repair-adjacent runs
observable problem = no new runnable todo, blocker, successor, or supersede
```

后续运行最终把目标移回可执行的 `normal_run` 形态,但这个事件之所以重要,
是因为控制面在让真正的下一步变得明显之前先耗掉了几个 turn。

## 问题出在哪里

1. **Monitor-only 状态太容易被读成动作。** Monitor quiet skip 是一条关注
   通道,不是交付通道。如果 status 或 diagnose 以 `waiting_on=codex` 和动作
   严重度呈现它,心怀善意的 agent 就会持续尝试本应保持安静、或应转为具体
   blocker 的工作。

2. **自修复缺少 delta 契约。** 修复循环可以写一条新的 run record、刷新散文、
   或确认一次 replan,但验收测试不要求机器可见的 frontier 变化,例如新的可运行
   todo、变化后的 `effective_action`、用户 gate、blocker、被取代的 todo,或
   显式的关注通道收尾。

3. **Replan 太接近散文。** Replan 应修复 todo 图:拆分工作、退役过时的
   monitor-only 工作、创建继任者,或记录 blocker。仅仅说"发生过 replan"
   不足以解除未来执行者的阻塞。

4. **持续 monitor 项没有过时阈值。** 相同建议的重复 monitor 轮询对存活状态
   有用,但超过阈值后,它们应成为三种结果之一的证据:继续静默关注、写一个
   具体 blocker,或用可运行路由取代该 monitor。

5. **Agent 行为是近因,但 LoopX 承担产品责任。** 更强的 agent 或许能更早停止
   或写下 blocker。更强的控制面应让正确行为比错误行为更容易。

## 为什么自修复与 Replan 没有完全起作用

自修复与 replan 只有在改变下一个控制面决策时才有用。在这个事件中,它们可以
诊断或重述情况,但不总能证明下一个 tick 会以不同方式路由。一次成功的修复应
通过一个小不变量:

```text
after repair/replan, at least one must change:
- quota.effective_action
- interaction_contract.agent_channel / user_channel
- runnable agent todo set
- open user todo / user question
- blocker state
- superseded todo / successor todo
- monitor target, expiry, or watch-lane rationale
```

如果这些都没有改变,修复应归类为 no-op,下一个 turn 不应再在同一循环上花费
交付槽位。

## 期望语义

LoopX 应区分三种在散文上相似、但执行含义不同的状态:

| 状态 | 用户通道 | Agent 通道 | 期望写回 |
| --- | --- | --- | --- |
| 静默 monitor | 不通知 | 可选 no-spend 轮询,然后保持安静 | 仅 monitor-poll |
| 失效 monitor | 除非需要所有者输入,否则不立即询问用户 | 需要 blocker、取代或继任者 | 具体转换 |
| Replan 义务 | 除非提升为用户决策,否则不打断 | 更新 todo 图,然后 ACK | 结构化 replan ACK 加变化的 frontier |

关键产品规则很简单:**只有当下一个 agent 能看到不同的、可操作的控制面状态时,
一次修复或 replan 才算完成。**

## 后续工作

### P1:自修复 Delta 契约

添加机器可见的修复验收规则。一次自修复或自主 replan 运行,只有改变了被选中的
工作 frontier、用户 gate、blocker 状态、可运行 todo 集、能力 gate 或 monitor
目标时才视为成功。否则把它标记为 `repair_noop` / `replan_noop`,并保持过时
条件可见。

### P1:失效 Monitor 检测器

检测针对同一 monitor 目标的重复 monitor-only 轮询且无实质转换。超过阈值后,
要求其中之一:带过期的显式关注通道继续、具体 blocker、`todo supersede`,或
后继可运行 todo。

### P1:Replan 到 Todo 契约

加强自主 replan,使其必须落在 todo 生命周期操作上:拆分/新增/更新、
`todo supersede`、`todo complete --next-agent-todo`,或结构化 blocker。
没有变化的 frontier 的 replan ACK 不应关闭该义务。

### P2:坏例目录与 Dashboard 文案

用本事件作为交互目录与 dashboard 文案的 public-safe 坏例。Monitor-only 通道
应渲染为关注状态,而不是即时的 Codex 工作或用户/控制器 gate。

## 相关模式

- `IP-008 Monitor Quiet Skip`:静默 monitor 工作是关注通道,不是交付通道。
- `IP-013 Autonomous Replan Vs Advisory Dreaming`:replan 收尾必须显式且
  结构化。
- `IP-020 Todo Claim / Supersede / Successor Lifecycle`:过时工作应被取代,或
  在带继任者的情况下完成,而不是通过散文隐没。
- `monitor_replan_noop_loop`:用于不改变机器可见工作 frontier 的
  monitor/replan 循环的自修复模式。
