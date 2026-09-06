# Agent 管理可观测性 MVP

> [English](agent-management-observability-mvp.md)

本说明把 `agent_management_projection_v0` 变成 LoopX dashboard 的第一个具体产品切片。它刻意是可观测性 MVP，而不是新 scheduler、dispatcher、任务数据库或浏览器写路径。

## 决策

为真实 ops surface 使用成熟的 agent-console 方向，并把 LoopX 暗色 showcase 方向留给公开叙事页面。

MVP 应像密集 operator 控制台：行、窄徽章、时间戳、evidence 链接与稳定过滤器。暗色 showcase 风格可以在公开 frontstage 解释同一模型，但它不应成为实时多 agent 操作的默认，因为实时操作需要扫读胜过动效。

## 灵感来源与复用边界

最接近的公开参考是 NousResearch Hermes Agent：

- Hermes Kanban 文档：
  <https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/kanban.md>
- Hermes delegation 文档：
  <https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/delegation.md>
- Hermes license：
  <https://github.com/NousResearch/hermes-agent/blob/main/LICENSE>

Hermes Agent 以 MIT license 发布，所以如果 UI 代码确实公开、需要的归属保持、且复制代码隔离在呈现层，可以把它作为后面实现 PR 的复用候选。本 MVP 不复制 Hermes 源码。

值得借鉴的想法是：

- 密集的任务/agent 行；
- 可见的 assignee、status、workspace、timestamp 与 liveness；
- 事件尾部与尝试历史辅助；
- 作为可检查上下文的 comments 或 handoff 说明；
- fresh-context delegation 作为对隐藏继承假设的警告。

不该借进 LoopX runtime 的想法：

- 第二个持久任务数据库；
- 自动 dispatch、cancel、reclaim 或 retry；
- worker 档案 runtime；
- workspace 分配 runtime；
- 绕过 LoopX CLI/API 边界的浏览器写入。

LoopX 已有持久工作单元：`goal_id` 内的 `todo_id`。Dashboard 可以把 todo 渲染成任务式卡片以增加熟悉感，但产品与 runtime 名称应保持 `todo` 或 `work item`，避免暗示第二套状态机。

## MVP Surface

投影存在后，在 Personal Workspace 添加显式 Agent Management 区块。已弃用的 `/deprecated/frontstage/ops` 路由可以继续为诊断渲染旧投影，但不得接收产品实现。

首屏应回答五个问题：

1. 哪些注册 agent 对此 goal 活跃？
2. 每个 agent 当前 claim 在什么上？
3. Agent 在运行、等待、阻塞、监控、过期还是未知？
4. 什么 evidence 或 handoff 让下一步可评审？
5. Operator 应注意什么 quota、cadence 或 workspace 提示？

## Agent 行

每行应把一条 `agent_management_projection_v0.agents[]` 项映射为紧凑行或卡片。

必需可见字段：

- agent id 与角色；
- 状态徽章；
- 当前 todo 标题与优先级；
- claim owner 或"未认领"；
- 下一动作，一两行；
- 最后活动时间；
- evidence/handoff 链接数；
- 改变 operator 行为时的 quota 或 scheduler 提示。

可选可展开字段：

- 必需写范围；
- workspace 提示；
- 过期 claim 提示；
- 近期事件尾部；
- 阻塞于的决策；
- 相关 user todo 数量。

## 状态徽章

使用小型、稳定的徽章集：

| 状态 | 含义 | Operator 姿态 |
| --- | --- | --- |
| `running` | LoopX 预期 agent 继续工作。 | 观察 evidence 与 quota。 |
| `waiting` | 泳道稍后合格或等待另一状态转变。 | 无需立即动作。 |
| `blocked` | 无 blocker 解决就无法推进。 | 检查 blocker 并决定是否面向用户。 |
| `monitoring` | 这是持续监控泳道。 | 只显示实质转变。 |
| `scope_wait` | 当前条目在 agent 泳道或写范围之外。 | 检查指派或 handoff。 |
| `stale` | Claim 缺乏新鲜活动 evidence。 | 检查 evidence；不要自动 reclaim。 |
| `unknown` | 投影缺少足够数据。 | 显示 source warning。 |

这些徽章只读。它们不执行生命周期转变。

## Evidence 与 Handoff 链接

Evidence 链接应可见但纤细：

- 最新 run 或 refresh-state 记录；
- 关联文档或协议文件；
- 验证命令标签；
- handoff 说明 id；
- review packet 引用；
- public-safe source warnings。

不要内联原始日志、原始轨迹、私有文档、本地绝对路径、凭据或 status JSON blob。行应显示 evidence 存在并让 operator 下钻到安全引用。

Handoff 说明应渲染为 todos/历史/evidence 的类型化附件：

- 来自 agent；
- 发送到 agent；
- 意图；
- 未解决决策数；
- 建议下一动作；
- evidence 引用。

它们不是聊天流，也不是批准。

## Quota、Cadence 与 Workspace 提示

Agent 行应只在 quota/cadence 改变 operator 决策时显示：

- 现在合格；
- 被限流或等待；
- no-spend monitor 轮询；
- 应用了 scheduler backoff；
- 因缺失活动 evidence 而过期。

Workspace 提示仅显示：

- `canonical_checkout`；
- `worktree`；
- `external`；
- `unknown`。

托管或公开 surface 应避免本地绝对路径。本地 loopback ops surface 只有在 status 载荷已暴露路径且 surface 显式本地/仅 operator 时才能显示路径。

## 只读 Operator 动作

MVP 可以暴露只读动作：

- 复制 review packet 命令；
- 复制 status/quota 命令；
- 打开安全 evidence 引用；
- 按 agent、状态或优先级过滤；
- 折叠监控行；
- 高亮过期或阻塞行；
- 在表格与泳道视图间切换。

MVP 不得暴露：

- claim/reclaim；
- cancel；
- dispatch；
- unblock；
- 优先级变更；
- workspace 创建；
- reward 追加；
- 外部生产动作。

未来写动作必须经独立 capability gate 引入，并调用类型化 LoopX CLI/API 转变。

## 实现形态

偏好薄的投影 adapter，而不是新 runtime 模型：

```text
loopx status/review-packet/evidence ledger
  -> agent_management_projection_v0
  -> dashboard read model
  -> rows/cards/timeline
```

Dashboard 应容忍投影缺失。缺失时，显示当前 ops dashboard 与 source warning；不要阻塞页面其余部分。

第一个前端 PR 应被允许只构建 fixture 支撑的读模型加浏览器可见锚点。实时 status 消费可以在夹具验证交互模型之后跟进。

## 验收检查

第一个实现应证明：

- surface 在投影存在时消费 `agent_management_projection_v0`；
- 投影缺失时 dashboard 仍工作；
- 不渲染任何浏览器写辅助；
- `todo_id` 保持为显示的工作项身份；
- 过期 claim 只是警告；
- evidence 与 handoff 链接渲染为引用，而不是原始日志；
- 公开夹具不含凭据、私有文档、原始轨迹或本地绝对路径；
- 复制或改编的外部 UI 代码带 license/归属说明，或实现是 LoopX 原生代码。

## 已实现切片

`apps/presentation/dashboard` 现在在实时 status 暴露时从 `agent_management_projection_v0` 渲染只读 Agent Management 面板。面板显示 agent 行、当前 todos、evidence 引用、类型化 handoff 说明、quota 提示与仅显示的 workspace/过期 claim 警告。这些提示不暴露 reclaim、cancel、dispatch、unblock 或 workspace 写动作。

捆绑 dashboard 示例由 `examples/control_plane/export-agent-management-status-example.py` 从 public-safe 实时 LoopX `loopx-meta` agent 切片刷新。它在安全处保留真实 agent id、todo id、状态与时间戳，脱敏私有本地文本，并在实时投影没有这些字段时不杜撰 workspace 或 handoff 字段。合成 smoke 仍覆盖 workspace、handoff 与过期 claim 渲染，作为契约夹具。

## 下一个切片

在面板积累足够真实 operator 使用后，添加 agent 状态、claim 新鲜度与 workspace 种类的过滤器。
