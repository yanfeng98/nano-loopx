# Agent 作用域 Replan 优先级事件


日期:2026-07-03

读者对象:LoopX quota/state 所有者、goal 路由维护者、dreaming / replan
所有者、heartbeat 提示词维护者,以及多 Agent 控制器作者。

## 摘要

一个已注册的 side agent 达到了"停止回合"的状态:它没有当前或未认领的推进
todo,而更广泛的目标仍有可见工作和周期性规划压力。预期行为不是普通交付:
该 agent 不应窃取另一个 agent 已认领的任务。预期行为也不是无限期静默
monitor:当目标需要控制面 replan 时,被选中的 agent 必须收到一个有界的
replan 动作,能够改变 todo 图、路由或 blocker 状态。

坏例在于:LoopX 可以在同一个包(packet)家族中投影出规划压力与带作用域的
"无工作"信号,却没有一个权威的交互模式。取决于 surface,agent 看到的是
静默 monitor / 带作用域的等待,或者是作为建议上下文出现的 replan 义务。
在这两种形态下,agent 都可以诚实地保持安静,而目标仍然需要路由修复。

## Public-Safe 形态

本案例在记录时不包含原始活动状态体、私有路径、benchmark 日志、轨迹、
凭据或本地运行时工件。可复用的形态是:

```text
quota call = quota should-run --goal-id <goal-id> --agent-id <side-agent>
current-agent advancement candidates = 0
unclaimed advancement candidates = 0
other-agent advancement candidates > 0
user_todo_summary.open_count = 0
ordinary delivery should not run = true
replan pressure exists = periodic review / stale route / goal acceptance gap
bad interaction = quiet no-op or agent-scope wait wins over bounded replan
expected interaction = autonomous_replan_required wins, but only for
  control-plane replan/todo writeback, not ordinary delivery
```

这与较早的 monitor-only replan 停滞事件相邻,但更窄。旧事件的主张是:
replan 必须改变 frontier。本事件的主张是:当 replan 被要求时,quota 载荷
必须在任何其他静默等待之前,把 replan 设为被选中的 frontier。

## 问题出在哪里

1. **Replan 可见但未被选中。** Replan 压力可能作为建议载荷出现在
   `must_attempt=false`、`delivery_allowed=false` 或静默 monitor 建议
   旁边。这会给执行者造成自相矛盾的体验:agent 能看到规划工作已到期,却又
   被告知不要尝试工作。

2. **Agent 作用域等待过于"终局"。** 当当前 agent 没有作用域内的交付候选时,
   `agent_scope_wait` 是正确的。但当"没有候选"的成因本身就是控制面 replan
   应该修复的问题时,它就不够了。

3. **Monitor todo 没有经由 replan 的提升路径。** monitor 通道在有意观察
   期间应保持安静。一旦目标需要路由修复,转换应该是:monitor 证据 ->
   需要 replan -> todo 拆分/新增/退役/blocker。它不应仅仅因为当前 agent
   没有推进 todo 就停留在 monitor-only。

4. **目标完成不是一等路由输入。** 目标级验收标准,当只以散文或产品直觉的
   形式存在时,无法可靠触发 replan。路由层需要一个紧凑的按目标契约,说明
   当前阶段"足够完成"的含义,以及过时、不完整或矛盾的路由应如何修复。

5. **Dreaming 与 replan 的边界接近但连接不足。** Dreaming 是建议性的;
   自主 replan 是可执行的控制面义务。目标级路由契约应允许 dreaming 提出
   更好的验收标准或路由,但只有自主 replan 能在没有 operator 提升的情况下
   覆盖静默 monitor / 无候选状态。

## 期望语义

小规则是:

> 当 `autonomous_replan_obligation.required=true` 时,选中的交互模式必须是
> `autonomous_replan_required`,除非更硬的 gate 阻止它。

更硬的 gate 包括用户决策、私有材料、凭据、破坏性 git、生产操作、缺失的
仓库边界,或损坏的控制面健康状态。普通的 monitor 静默、agent 作用域等待,
以及当前 agent 交付 frontier 为空,都不是更硬的 gate。

载荷应保持显式,而不是省略字段。问题不在于存在 `must_attempt` 或交付字段;
问题在于它们的范围定得太粗。干净的契约应说明:

```text
interaction_contract.mode = autonomous_replan_required
agent_channel.must_attempt = true
agent_channel.delivery_allowed = true
agent_channel.allowed_action_scope = control_plane_replan
normal_delivery_allowed = false
cli_channel.spend_after_validation = true
primary_action = split/add/retire todos, write blocker, or record watch expiry
```

这保留了安全边界:agent 可以修复路由状态,但不能执行由另一个通道拥有的
普通任务。

## 按目标路由契约

持久修复应是一个小的按目标路由契约,而不是 auto-research 专属的完成系统。
该契约应存在于目标状态 / registry 投影中,并馈送 quota、status、replan 与
dreaming。

最小可用字段:

```json
{
  "schema_version": "goal_routing_contract_v0",
  "stage": "current public-safe stage name",
  "acceptance": [
    {
      "id": "short stable id",
      "description": "public-safe done condition",
      "required": true,
      "evidence_kind": "todo|run_history|smoke|artifact|operator_decision"
    }
  ],
  "replan_triggers": [
    "acceptance_gap",
    "stale_route",
    "no_current_agent_candidate"
  ],
  "dreaming_policy": {
    "advisory_only": true,
    "may_propose_acceptance_updates": true,
    "promotion_requires": "operator_or_controller_decision"
  }
}
```

这样机制保持小巧。目标契约定义当前路由与验收差距;自主 replan 修复可执行
frontier;dreaming 可以提出建议但不能静默执行。

## 后续工作

### P0:Quota 中的 Replan 优先级

当 status 或运行历史投影出 `autonomous_replan_obligation.required` 时,
quota 应在 `monitor_quiet_skip`、`agent_scope_wait` 或通用无候选等待之前
选择 `autonomous_replan_required`。载荷必须暴露允许的控制面 replan 动作,
以及验证 / 写回命令。普通交付可以继续保持阻塞。

### P1:最小目标路由契约

添加一个紧凑的 `goal_routing_contract_v0` 投影,包含验收检查与 replan
触发器。保持按目标且通用。它不应知道任何特定产品预设;auto-research 之后
可以把它作为其中一个示例使用。

### P1:规划通道回归

添加一个聚焦的 quota/status 回归:side agent 没有推进候选,另一个 agent
拥有交付工作,并且需要目标级自主 replan。期望结果:side agent 收到带
`allowed_action_scope=control_plane_replan` 的 `autonomous_replan_required`,
而不是静默 no-op。

## 相关模式

- `IP-013 Autonomous Replan Vs Advisory Dreaming`
- `IP-024 Repair Delta Contract`
- `IP-026 Agent-Scoped No-Candidate Gap`
- `IP-008 Monitor Quiet Skip`
- `monitor_replan_noop_loop`
- `agent_scoped_no_candidate_gap`
