# RFC：Provider-Neutral Turn-Start Inbox Hook（v0）


| 字段 | 值 |
|---|---|
| 状态 | 已在显式 provider 配置后实现 |
| 日期 | 2026-08-26 |
| 决策边界 | 新鲜的外部收件箱证据如何在 Agent 选择常规 Goal 工作前到达它 |
| 核心 owner | Hook 准入、排序、有界公开 receipt 与 Agent 读取义务 |
| Provider owner | 外部读取、provider schema 校验、私有 cursor 与本地收件箱持久化 |
| Agent owner | 语义分诊与持久的 Goal/Todo/effect 写回 |

## 决策

LoopX 增加一个 provider-neutral 的 `turn_start` capability-hook 阶段。启用的
provider hook 在状态与 quota 投影之前运行。它可以执行有界的外部读取、修改已声明
的 owner 私有 inbox/cursor 状态，并且——仅当 provider 注册显式请求了
`provider_message_reaction` 时——对被捕获、仍待处理、且 hook 已读取进 Agent
turn-start 处理链的人工消息添加一个幂等确认 reaction。这种读取确认独立于提及、
回复、问题与其他注意力分类。公开结果包含计数、布尔值、状态与错误码；它不能包含
消息内容、provider 载荷、凭证、目的地、profile 名或私有 cursor 值。

只有当新鲜证据被路由到 Agent 读取时，hook 才算完成。带新观察的结果必须设置
`agent_read_required=true`。其注册声明一个有界的、公开安全的 `required_read`
描述符。通用 hook 内核验证该描述符、按命令去重，并以 `ordering=before_work`
把它投影进 Agent 与 CLI 交互通道。新鲜普通材料的读取发出非阻塞用户通知，同时保留
已选定的工作 lane。如果该材料在下一 Turn 仍持久待处理，材料审阅 lane 会抢占工作
进行恢复。直接问题或已验证回复仍在第一个 Turn 抢占。Agent 读取消息并选择一个
typed 语义处置：

- `steer_current_turn`：更新选定工作，不改动持久 Goal frontier；
- `replan_goal`：在继续前更新 Todo/vision/priority 状态；
- `record_context`：提交持久的领域 effect 或证据记录；
- `continue_current_work`：记录消息已被考虑，但不改变当前计划；或
- `no_follow_up`：显式处置无关或重复材料。

Provider 代码绝不选择这些结果。Core 绝不解释私有消息文本。Agent 拥有语义判断，
并且必须在 inbox ACK 之前把任何材料结果绑定到持久 effect receipt。

## 排序

```text
provider-neutral turn_start dispatch
  -> provider read + owner-private inbox commit/readback
  -> first Agent-read receipt independent of optional provider reaction
  -> retry optional reaction from durable pending reads
  -> fresh status + quota projection
  -> generic kernel projects the registered required read before selected work
  -> private drain into the active Agent turn (ordinary selection may remain)
  -> semantic disposition + durable settlement
  -> ACK and resume the prior lane when appropriate
```

在 quota 选择之后运行 hook 是错误的，因为新鲜的 steering 可能在常规工作已选定
之后才到达。在公开 hook 结果中返回原始内容也是错误的，因为共享注册表与 Turn
journal 是公开安全的控制面界面。CLI 请求校验在 hook 分发之前运行，因此无效的
quota 请求不执行任何 provider 读取或 owner 私有写入；有效请求仍在状态收集与
quota 选择之前分发 hook。

## 失败与重放

- `empty` 表示读取到的 provider 成功 envelope 有效，且本次分发中没有待处理消息
  收到其首次 Agent 拥有的 turn-start 读取。
- `provider_contract_error` 表示成功 envelope 与其声明的 schema 不匹配；它绝不能
  降级为 `empty`。
- Provider 权限与可用性失败仍是严格类型化的、隔离的。
- 重复的 hook 身份只运行一次；重复消息按 provider 消息身份折叠，独立的私有
  读取/effect receipt 防止重复的 Agent 读取观察与重复 provider reaction。
- 仅收集（collector-only）的捕获不执行任何 provider 写入。确认只在 turn-start hook
  读取并确认待处理消息后才被准入。
- Reaction 停用绝不取消首读义务。失败的 effect 从 owner 私有 pending-read 集合
  重试，而不是依赖有界的 provider 重叠窗口；不确定的 effect 在 create 前
  fail closed。重放受每次分发一个聚合尝试预算的约束。私有 collector-scoped cursor
  在多次分发间轮换路由优先级，而每条路由保留私有的 round-robin 消息 cursor。
  因此大型或失败中的确认积压不会无限期阻塞 turn 准入，且每次待处理读取跨路由与
  消息保持合格。
- 注意力分类影响调度与回复策略，永不决定成功读取的待处理消息是否收到确认。
- Provider 自有的 self-message 过滤器只能在 inbox 摄入前，以一个 typed sender 与
  为配置 profile 验证过的精确身份运行；身份未决时 fail open 到捕获，且不能使用
  display-name 或正文启发式。
- Provider 本地 cursor 是 single-flight 的，只在 inbox 与 cursor readback 后推进。
  历史摄入与确认重放使用独立 cursor 位置：旧话题的新回复由其新的 provider 消息
  身份准入，即使较旧确认欠账仍然存在。
- `partial` 多路由成功仍然要求对已接受观察执行 Agent 读取，同时对不完整路由保留
  紧凑失败码。

该 hook 不授予仓库、生产、出站消息或任意外部写入权限。其唯一允许的本地写入是
已注册的 owner 私有 inbox 与 cursor 范围。其唯一准入的外部写入是显式
`provider_message_reaction` 范围：对被 Agent turn-start hook 读取过的捕获、仍待处理
消息执行一个配置 reaction。Realtime 收集不能消耗该范围。公开 receipt 必须暴露
`external_writes_performed`；provider 或私有 receipt 失败是 `partial`，绝不是虚假
成功，也不能丢弃已捕获的 inbox 事件。
