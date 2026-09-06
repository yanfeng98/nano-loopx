# Agent 作用域用户 Gate 越界事件


日期:2026-06-24

读者对象:LoopX status/quota 所有者、项目 Agent 控制器作者、自修复维护者,
以及 benchmark/产品通道操作员。

## 摘要

一个用户 gate todo 被正确地用 `blocks_agent=<target-agent>` 限定到单个已注册
agent,但 `quota should-run --agent-id <other-agent>` 仍然把它当作当前 agent
的属主 gate。非目标 agent 有可运行的工作,但它的交互契约变成了 `user_gate`,
并且 `delivery_allowed=false`。

操作后果细微但严重:一个 agent 的正当用户决策阻塞了无关的 agent 通道。在
观察到的形态中,针对 Lark Kanban 目标的产品能力 gate 可能阻塞
main-control / benchmark 通道,即使 benchmark 通道有自己的已认领可执行 todo。

## Public-Safe 形态

本事件在记录时不包含原始活动状态载荷、私有日志、轨迹、本地路径、verifier
输出或内部链接。可复用的形态是:

```text
quota call = quota should-run --agent-id <agent-a>
raw quota state = operator_gate
open user todo = task_class=user_gate, blocks_agent=<agent-b>
agent A todo = claimed executable advancement todo
bad interaction = user_channel.action_required=true for agent A
bad agent channel = delivery_allowed=false for agent A
expected target-agent behavior = agent B remains blocked on the user gate
expected non-target behavior = agent A can continue bounded delivery
```

## 问题出在哪里

1. **`blocks_agent` 可见但非权威。** 用户 todo 摘要暴露了 `blocks_agent`,
   但阻塞摘要对每个 agent 身份都统计了所有打开的用户 gate。

2. **目标级 `operator_gate` 泄漏进了 agent 作用域的 quota。** 该目标确实在
   等待某条通道的用户决策。当前 agent 的 quota 视图在设置
   `requires_user_action=true` 之前,没有先询问该 gate 是否适用于当前 agent。

3. **这个失败看起来像一个属主 gate,而不是投影 bug。** 由于载荷包含具体的
   用户 todo,agent 可以持续报告该 gate,而不是注意到它属于另一个 agent。

4. **附近的 no-candidate 模式不是正确的修复。** 当前 agent 并没有工作耗尽。
   它有一个可运行的 todo。bug 在于另一个 agent 的 gate 覆盖了可运行通道。

## 期望语义

用户 todo 上的 `blocks_agent` 是硬性作用域边界:

| 视图 | 用户通道 | Agent 通道 |
| --- | --- | --- |
| 目标 agent | 通知具体用户 gate | 停止被 gate 的交付 |
| 有可运行工作的非目标 agent | 不需要用户动作 | 继续有界交付 |
| 无可运行工作的非目标 agent | 不需要用户动作 | 通过 agent 作用域路由归类为空 frontier |
| 无作用域的用户 gate | 通知具体用户 gate | 停止普通交付 |

非目标 agent 仍可以把其他 agent 的 gate 当作诊断上下文,但绝不能在自己的
阻塞 `open_count`、`gate_open_items` 或
`interaction_contract.user_channel.action_required` 中计入该 todo。

## 修复

持久修复落在 PR #629:

- 把设置了指向其他已注册 agent 的 `blocks_agent` 的 `user_todos` 从当前
  agent 的阻塞 quota 摘要中过滤掉;
- 保留这些 todo 作为诊断性的 `other_agent_scoped_items`;
- 当原始状态为 `operator_gate` 仅仅是因为其他 agent 的 gate,且当前 agent
  有可执行工作时,投影出一条合格的当前 agent 通道;
- 让目标 agent 继续保持对该具体用户 todo 的阻塞。

## 验证

- `examples/control_plane/quota-agent-scoped-user-gate-smoke.py` 覆盖:
  - 非目标 agent 可以运行;
  - 目标 agent 保持被用户 gate 阻塞;
  - 无作用域的用户 gate 仍是全局 gate。
- `examples/control_plane/work-lane-contract-smoke.py`
- `examples/control_plane/quota-action-scope-guard-smoke.py`
- `examples/protocol/protocol-action-packet-smoke.py`
- `examples/control_plane/quota-plan-smoke.py`
- 一次真实活动状态 quota 检查确认:非目标 agent 返回 `decision=run`、
  `requires_user_action=false`、`delivery_allowed=true`,而目标 agent 仍是
  `user_gate`。

## 相关模式

- `IP-003 Scoped Gate With Safe Fallback`:拥有 `blocks_agent` 作用域规则。
- `IP-022 Claimed Todo Visibility And Agent-Lane Next Action`:保持当前
  agent 的已认领工作可见,避免被作用域 gate 隐藏。
- `IP-026 Agent-Scoped No-Candidate Gap`:只适用于其他 agent 的 gate 被
  过滤后、当前 agent 也没有可运行 frontier 的情况。
- `agent_scoped_user_gate_overreach`:该失败模式的自修复模式。
