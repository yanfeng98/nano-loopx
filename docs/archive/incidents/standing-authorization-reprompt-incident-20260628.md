# Standing Authorization 重复询问事件


日期:2026-06-28

读者对象:LoopX status/quota 所有者、决策作用域 runtime 所有者、用户 gate
投影所有者、benchmark 操作员,以及自修复维护者。

## 摘要

一条 benchmark 重跑通道需要用现成的私有反向通道桥作为不透明执行材料。所有者
先前已批准预期路由,后来预期这类桥的使用由该授权覆盖。LoopX 仍投影了一个新的
用户 gate,询问 agent 是否可以使用该桥。

直接的 gate 本身没有害处:它保留了私有边界,没有暴露桥材料。坏例在于:LoopX
把一个"类批准"决策当作一次性 todo 完成处理,而不是可复用、带作用域的能力
授予。Agent 也没有在再次询问所有者之前检查先前的决策和已定的路由。

因此根本问题是混合的:

- **LoopX 产品缺口:** 决策作用域作为协议目标存在,但热路径还没有把常驻授权
  (standing authorization)、语义去重或"gate 到 todo 释放"建模为一等运行时
  行为。
- **Agent 流程缺口:** 该 agent 本应检索先前的批准状态,识别路由已定,并在重新
  询问所有者之前运行自修复。

## Public-Safe 形态

本事件在记录时不包含原始桥命令、环境值、主机名、本地路径、截图、私有
benchmark 日志、verifier 输出或任务文本。可复用的形态是:

```text
user intent = continue the benchmark rerun through the approved route
approved route = /loopx goal-start plus reverse channel
protected material = private bridge configuration used only as opaque execution
required boundary = no read, no print, no log, no commit of bridge contents
bad interaction = owner is asked again for a materially equivalent bridge-use gate
expected interaction = LoopX says the action is covered by an existing scoped
  authorization, or asks only when the requested action exceeds that scope
```

## 问题出在哪里

1. **批准被存为 todo 结果,而不是可复用的授予。** 系统可以勾掉一个用户 gate,
   但没有持久对象说明"在该边界下,这个 agent 可以为这条通道不透明执行该桥
   类型"。
2. **决策作用域覆盖没有涵盖常驻授权。** `decision_scope_v0` 契约说用户决策应
   点名它们覆盖的权威。本例中,桥使用动作需要结构化作用域,如
   `resource:lane:reverse_channel_bridge_opaque_execute`,但热路径依赖散文与
   todo 状态。
3. **Gate 去重是文本级而非语义级。** 当新 gate 请求同一个动作类时(在同一
   benchmark 通道和私有边界规则内不透明使用现有反向通道桥),即使措辞不同,
   仍可能被投影出来。
4. **路由决策与执行授权混为一谈。** 所有者已经选择了 `/loopx goal-start +
   reverse channel`。后来的提示词部分听起来像又一次路由决策,而真正缺失的
   权威更窄:把现有私有桥用作不透明执行材料。
5. **Gate 完成没有自动释放被阻塞的工作。** 所有者回答后,链接的 benchmark todo
   仍需要手动状态修复,才能成为被选中的可运行动作。这让操作员付了两次:一次
   回答 gate,再一次恢复 todo 通道。
6. **Agent 没有先做先前决策审计。** 鉴于所有者近期澄清了路由与桥策略,该 agent
   本应在要求另一次批准前,检查当前用户 todo 历史、决策作用域元数据、活动状态
   注释与运行历史。

## 期望语义

LoopX 应区分一次性 gate 与可复用、带作用域的授权。

| 情形 | 期望行为 |
| --- | --- |
| 相同 agent、相同通道、相同桥类型、相同 no-read/no-print/no-log/no-commit 边界 | 使用常驻授权并继续。 |
| 相同桥类型但操作更宽,如读取或持久化桥材料 | 询问一个新的具体用户 gate。 |
| 相同批准措辞但 agent、通道、benchmark 或外部写边界不同 | 继续前要求显式作用域比较。 |
| Gate 已完成并链接到一个被阻塞的 todo | 重新计算该 todo 的可运行状态与选择,无需手动修复。 |
| 先前的批准有歧义 | 问一个精确的问题,并说明现有作用域为何不能覆盖它。 |

Status 与 quota 应把它作为数据而不是散文呈现:

```json
{
  "standing_authorization": {
    "schema_version": "decision_scope_grant_v0",
    "actor": "codex-main-control",
    "operation": "opaque_execute",
    "resource_kind": "reverse_channel_bridge",
    "lane": "skillsbench_goal_start",
    "boundary": ["no_read", "no_print", "no_log", "no_commit"],
    "state": "active"
  },
  "scope_relation": {
    "state": "grant_covers_action",
    "matched_grant_id": "<public-safe-grant-id>",
    "user_channel": "no_user_action_required",
    "agent_channel": "run"
  }
}
```

## 后续工作

### 短期:记录当前常驻授权

为当前桥使用类型创建一个紧凑、public-safe 的常驻授权记录:

- actor:main-control agent;
- action:仅不透明执行;
- resource 类型:反向通道桥;
- lane:SkillsBench `/loopx goal-start` 重跑;
- boundary:不读取、打印、日志、持久化或提交桥内容;
- 撤销:所有者可通过新增用户 gate 或关闭该授予来撤销。

活动 benchmark todo 应声明匹配的 `required_decision_scopes`,quota 应显示
`grant_covers_action`,而不是投影另一个用户 todo。

### 短期:添加 Gate 到 Todo 释放

用户 gate 完成后,LoopX 应重新计算列出匹配 `required_decision_scopes` 或
`unblocks_todo_id` 的确切链接 agent todos。如果 gate 释放选中的 P0 通道,下一次
quota 投影应选择它,而无需单独自修复 turn。

### 短期:收敛 Gate 提示词文案

Gate 提示词应只询问缺失的权威。本例中,提示词本应说:

```text
Use the existing reverse-channel bridge as opaque execution material for this
SkillsBench /loopx goal-start rerun, without reading, printing, logging, or
committing bridge contents?
```

它不应重新打开已定的路由选择。

### 中期:把常驻授予设为运行时原语

引入一等 `decision_scope_grant_v0`,或扩展 `decision_scope_v0` 以带授予状态:

- `grant_id`;
- `actor`;
- `operation`;
- `resource_kind`;
- `scope_key`;
- `granularity`;
- `boundary_rules`;
- `created_from_decision_id`;
- `expires_at` 或 `revoked_at`;
- `audit_summary`。

Quota 应分别计算 `missing_decision_scopes`、`covered_by_gate` 与
`covered_by_grant`,使未解决的 gate 与活动授权不会坍缩进同一个面向用户的
"所有者 gate"桶。

### 中期:语义重复 Gate 检测

在添加用户 gate 之前,归一化其动作指纹:

```text
actor + operation + resource_kind + lane + boundary_rules + scope_key
```

如果活动授予或等价的开放 gate 已覆盖该指纹,LoopX 应复用或更新其证据,而不是
创建另一个用户 todo。

### 中期:作用域感知的 Gate UI

面向操作员的 surface 应渲染计算出的关系:

- 由先前授权覆盖;
- 被开放 gate 阻塞;
- 作用域不匹配;
- 授权已过期;
- 需要投影修复。

这能让所有者判断:LoopX 是在问一个真正新的问题,还是未能复用早期的决策。

### 长期:事件溯源权威 Ledger

把 gate 与授权状态移向事件流:

- `gate_requested`;
- `gate_answered`;
- `authorization_granted`;
- `authorization_used`;
- `authorization_expired`;
- `authorization_revoked`;
- `todo_released_by_authorization`。

Status/quota 应从那本 ledger 投影,而不是依赖活动 Markdown 散文、最新运行文本
或聊天记忆。

### 长期:受保护资源的策略引擎

桥的使用、凭据、远程执行、公开发布与生产动作都应由同一个策略引擎检查。策略
引擎应做三个独立决策:

- 该动作是否受保护;
- 常驻授予是否覆盖它;
- 该动作是否会暴露受保护材料。

引擎应在暴露问题上 fail-closed,但当所有者已授予相同的不透明操作时避免重新
询问。

## 验证目标

为这些行为添加强聚焦 smokes:

- 已完成的常驻授权阻止同一动作指纹的重复 gate 投影;
- 不同操作(如读取桥内容)不被不透明执行授予覆盖;
- 完成一个 gate 立即使在 quota 中释放链接的 agent todo;
- 路由决策 gate 与执行授权 gate 渲染为不同提示词;
- `quota should-run --agent-id <agent>` 对被覆盖动作报告 `covered_by_grant`,
  且不需要用户通知。

## 相关模式

- `decision-scope-v0`:用户/控制器决策需要结构化作用域与动作依赖。
- Agent 作用域用户 Gate 越界事件:gate 必须只阻塞它们实际覆盖的 agent 与 lane。
- 默认工作流规划器缺口事件:运行时路由决策与执行授权应是显式模式计划状态,
  而不是通过重复提示词反复发现。
