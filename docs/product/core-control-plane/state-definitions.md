# State 定义


LoopX state 应当小而可观察、可复用。只有当未来的 agent 或产品界面能够回答以下问题时,state 定义才有效:这个 state 来自哪里,谁可以改变它,它允许什么转换?

本文件保留交互目录与状态机使用的核心 state 体与运行时 state 的公开安全定义。

## 规范 State 体

| State 体 | 真相源 | 主要写入者 | 含义 | 不得意指 |
| --- | --- | --- | --- | --- |
| 注册表 | 项目/全局注册表 | `connect`、项目设置、注册表同步 | Goal 身份、active 状态路径、运行时根、注册的 agent、主 owner 与运行时路由。 | 自动化已经运行的承诺。 |
| Active 状态工作台 | Active goal 状态投影或 Markdown 工作台 | LoopX 生命周期命令与受控 agent 写回 | 人类可读的当前 goal、进度、todo、gate、校验注记与下一步动作。 | 当事件/todo 投影另有说法时的规范真相。 |
| Todo | Todo 投影或事件流 | `loopx todo` 与兼容的生命周期写入者 | 最小的可执行或等待单元,含角色、优先级、状态、任务类别、动作类型、能力提示与 evidence 引用。 | 完整的项目计划或隐藏的聊天提醒。 |
| Claim | Todo 元数据、租约投影或事件流 | `loopx todo claim`、owner 重新分配、租约刷新 | 一个 agent 或车道的软所有权与路由信号。 | 允许忽略更好 evidence 或当前 gate 的锁。 |
| Gate / Decision Scope | 用户 todo、运维者 gate 或配额交互契约 | 用户/控制器决策写入者 | 仍然需要的具体权威,包括它阻碍的范围与如何解决。 | 除非显式标记为全局,否则不是全局停止牌。 |
| Dependency / Resume | Todo 元数据与事件引用 | Todo 生命周期写入者 | 等待条件、解除阻碍关系、后继关系或取代链。 | 等待后丢失原任务的理由。 |
| Evidence Bundle | Todo/run/事件引用 | Agent 写回、归约器、校验工具 | 紧凑证据、产物引用、来源引用、校验结果、阻碍或回滚锚点。 | 原始私有日志、转录、凭据或未经支持的声明。 |
| Run Snapshot | 运行历史 | 适配器、refresh-state、执行包装器 | 一个有界 Turn 看到、尝试、推荐并交付了什么。 | 整个项目记忆。 |
| Event Ledger | 仅追加事件 | LoopX 生命周期命令 | Todo、gate、run、evidence、配额、投影与回滚的有序生命周期事实。 | 可变的笔记文件。 |
| Projection | 状态、配额、前场、评审包、dashboard | 投影构建器 | 面向一个消费者的源事实只读渲染。 | 写 API 或真相源。 |

## 派生的运行时 State

这些 state 由上表 state 体派生。它们对状态、配额、调度器、前场、评审包与 agent 提示有用。

| 运行时 State | 派生自 | 含义 | Agent 行为 | 用户行为 |
| --- | --- | --- | --- | --- |
| `eligible` | 注册表 + active 状态 + todo + 配额 | 存在可运行或可修复的工作,且没有活动 gate 覆盖所选动作。 | 交付一个有界分段,校验,写回。 | 通常无需打断。 |
| `bounded_delivery` | `eligible` 加所选 todo | 当前 Turn 应创建产物、阻碍、evidence 观察或 state 更新。 | 必须尝试;只在已验证写回后花费。 | 仅当结果需要批准时才评审。 |
| `user_gate` / `operator_gate` | Gate + 决策范围 + 交互契约 | 人/控制器决策阻碍所选动作。 | 询问或通知具体 gate;不要运行被 gate 覆盖的路径。 | 回答、延迟、拒绝或重定向该决策。 |
| `scoped_user_gate_fallback` | Gate + 独立 todo + 决策范围 | Gate 仍打开,但另一动作独立且安全。 | 呈现 gate,只运行独立的 fallback,校验。 | 看到 gate 而无需在 fallback 工作前被迫回答。 |
| `agent_scope_wait` | Todo 认领、blocks_agent、交接 gate、agent id | 当前 agent 没有范围内的可运行候选,或另一 owner 持有阻碍。 | 保持活跃而安静;等待重新分配、解除阻碍或新的范围工作。 | 通常无需打断。 |
| `successor_replan_required` | Dependency / Resume + Handoff + Todo 生命周期 | 延迟或交接 gate 已清除,但当前 agent 仍没有稳定的后继、取代链接或不跟进理由可运行。 | 暂不运行常规交付;重开、取代、创建后继或记录不跟进,然后重跑护栏。 | 除非后继决策由用户持有,否则通常无需打断。 |
| `waiting` / `external_evidence_observation` | 等待元数据、monitor todo、外部句柄 | 工作依赖终结性外部 evidence 或紧凑观察。 | 只观察有界的公开安全句柄;若无句柄则写阻碍。 | 只在被具体询问时提供缺失句柄。 |
| `monitor_quiet_skip` | 连续 monitor todo + 节奏元数据 | Monitor 未到期或没有实质性转换。 | 契约允许时最多追加一次无花费轮询,然后保持安静。 | 无需打断。 |
| `focus_wait` | 结果下限、交接就绪度、交付结果 | 车道在常规交付前需要结果尺度的 evidence、干净基线或新的 owner evidence。 | 恢复命名的 evidence 或报告阻碍。 | 只在阻碍由 owner 持有时才决策。 |
| `blocked_health` | 注册表/投影/边界检查 | 控制面健康已坏到交付不安全。 | 若允许则修复;否则以具体阻碍停止。 | 只评审具体修复 gate。 |
| `workspace_guard` | Agent 配置 + 当前工作树 + 请求的 goal | Agent 在错误的 checkout 中或缺少所需的隔离车道。 | 在配额工作前迁移或写入具体的工作区阻碍。 | 除非迁移需要 owner 动作,否则无需打断。 |
| `capability_gate` | Todo 必需能力 + host/运行时能力 | 某些候选需要当前 host 缺失的能力。 | 运行可运行候选、修复桥接,或请求 owner 持有的能力。 | 只通过具体 gate 提供凭据或受保护访问。 |
| `throttled` / `paused` | 配额台账或显式暂停 | Goal 现在不应花费自动算力。 | 保持安静。 | 如需可恢复或增加配额。 |
| `writeback_spend` | 已验证产物/阻碍/evidence + 配额契约 | 该 Turn 产生了持久价值,可以计一次花费。 | 写入 state/历史,然后恰好花费一次。 | 无需打断。 |
| `done` / `archived` | Todo/goal 终结 state | 该单元没有剩余必要工作。 | 仅在需要时停止或创建后继。 | 如果呈现则评审最终摘要。 |
| `projection_gap` | 投影不匹配、陈旧 sink、缺失具体 todo | 展示或提示投影不完整,或与源 state 冲突。 | 使用陈旧视图前修复源/投影。 | 不要含糊 gate;只请求缺失的具体用户输入。 |

## 通道不变量

用户与 agent 通道可以不一致而不矛盾。例如,`scoped_user_gate_fallback` 刻意含义是:

```text
user_channel.action_required = true
agent_channel.must_attempt = true
agent_channel.selected_action = independent_fallback
```

用户通道命名未决决策。Agent 通道命名不依赖该决策的安全工作。当投影把这些折叠成一个布尔值,要么阻碍全部工作要么隐藏 gate 时,投影就是错的。

## 定义清单

新增 state 名称之前:

1. 确定源 state 体或投影字段。
2. 确定谁能写入源头。
3. 确定合法的下一步转换。
4. 确定用户必须被打断、通知还是不受打扰。
5. 确定公开安全的 evidence 形态与校验路径。

若任一项缺失,优先精化目录模式或投影字段,而不是新增 state。
