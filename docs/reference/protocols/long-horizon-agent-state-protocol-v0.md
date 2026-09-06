# long_horizon_agent_state_protocol_v0

`long_horizon_agent_state_protocol_v0` 是长程 LoopX agent 工作的共享生命周期图。它把持久化源状态与面向操作员的投影分离，然后展示启动、执行、结束、证据、关卡、人类反馈、交接与回滚应如何连接。

这不是新状态存储。事实来源仍是 registry、活动 goal 状态、todos、run 历史、rollout 事件、操作员 gates 与绑定 run 的人类奖励 overlay。本协议给这些既有界面一个面向实现的框架。

## 产品结局

本协议存在的目的是使 LoopX 支持这些结局：

1. 新项目可以快速连接而不覆盖既有控制面。
2. 用户在长 loop 开始前看到候选工作与关卡。
3. 多个 agent 可以在 lane 中工作而不丢失所有权、证据或评审责任。
4. 操作员可以从投影检查进展、关卡、风险与下个动作，而不是读每条聊天线程。
5. 失败或回滚的工作成为补偿状态迁移，而不是被抹除的历史。

## 来源协议

来源协议字段只能通过 LoopX 生命周期命令或项目自有状态文件写入。Dashboard 与展示 fixture 不得直接修改它们。

| 源状态 | 既有锚点 | 用途 |
| --- | --- | --- |
| `goal_identity` | registry、active state、agent profile docs | 稳定 `goal_id`、repo、已注册对等方、咨询 profile 与写边界。 |
| `connection_state` | `loopx connect`、`bootstrap`、`doctor`、`sync-global` | 仓库是否已连接、只读、已引导、过期或缺本地状态。 |
| `local_state_boundary` | `.gitignore`、`loopx check`、入门文档 | 把 `.loopx/`、`.codex/goals/`、`.local/`、原始日志、凭据与私有路径排除在公开提交外。 |
| `todo_item_v0` | `loopx todo`、active-state todo 小节、`loopx/status.py` | 带角色、状态、任务类别、动作种类、claim、依赖、恢复与证据元数据的正式工作单元。 |
| `suggested_todo` | `loopx todo suggest`、`todo_suggestion_prompt_v0` | 候选决策队列；在用户/controller 提升前不是正式 backlog。 |
| `interaction_contract_v0` | `loopx quota should-run`、`docs/quota-allocation.md` | 在自动化 Turn 花费计算之前拆分用户、agent 与 CLI 义务。 |
| `agent_lane_next_action_v0` | `loopx quota should-run --agent-id ...`、`docs/project-agent-todo-contract.md` | 每 agent 所选可运行 todo，而不替换 goal 级下一动作。 |
| `agent_workspace_guard_v1` | `loopx quota should-run`、所选 todo 与仓库策略 | 在当前对等方使用合规 worktree/分支之前阻塞仓库投递。 |
| `run_history` | `loopx/history.py`、`refresh-state`、`quota spend-slot` | 紧凑 run 分类、投递结局、推荐动作、证据与花费记录。 |
| `loopx_rollout_event_v0` | `loopx/rollout_event_log.py` | todo、验证、PR、交接、quota、修复与失败事件的追加式公开安全事件流。 |
| `operator_gate` | `loopx operator-gate`、`loopx/review_packet.py`、`loopx/status.py` | 带决策、原因、后续动作与可选交接命令的用户/controller 决策点。 |
| `human_reward` | `loopx reward`、`loopx/history.py`、`loopx/status.py` | 绑定 run 的人类判定 overlay；非通用写控制。 |
| `delivery_outcome` | `loopx/delivery_outcome.py`、`loopx/history.py`、`loopx/status.py` | 机器可读结果层级：仅界面、结局差距、结局进展或主 goal 结局。 |
| `rollback_packet_v0` | `docs/reference/protocols/rollback-packet-v0.md` | 连接 todo、commit、事件、决策、外部资源与验证计划的补偿动作记录。 |

## 投影协议

投影协议字段是只读视图。它们可以总结、排列与压缩状态，但不拥有真相或授予权限。

| 投影 | 既有锚点 | 显示用途 |
| --- | --- | --- |
| `status_contract_v2` | `loopx status`、`docs/status-data-contract.md` | CLI/dashboard 状态信封。 |
| `goal_channel_projection_v0` | `loopx/control_plane/goals/goal_channel_projection.py`、`loopx/status.py` | 首屏 goal 卡片：用户 todos、agent todos、开放 gates、活动 claims、最新事件、下一动作。 |
| `todo_index_v0` | `loopx/status.py` | 从关注队列与 rollout 事件生成的跨 goal todo index。 |
| `task_graph_projection_v0` | `docs/reference/protocols/task-graph-projection-v0.md` | blocks、validates、repairs、hands off 与 supersedes 的可选图。 |
| `review_packet` | `loopx review-packet`、`loopx/review_packet.py` | 面向操作员的 gate/评审/交接包。 |
| `global_manager_command_v0` | `docs/reference/protocols/global-manager-command-v0.md` | 关于进展、gates、todos、风险与下一动作的读取优先全局命令响应。 |
| `frontstage dashboard` | `apps/presentation/dashboard/src/views/frontstage-page.tsx` | 面向 lanes、gates、todos、近期证据与风险的密集操作员 UI。 |

投影真相契约：

```json
{
  "schema_version": "long_horizon_agent_state_protocol_v0",
  "projection_is_writable": false,
  "source_of_truth": [
    "registry",
    "active_state",
    "todo_item_v0",
    "run_history",
    "rollout_event_log",
    "operator_gate",
    "human_reward"
  ],
  "write_apis": [
    "loopx todo",
    "loopx refresh-state",
    "loopx operator-gate",
    "loopx reward",
    "loopx quota spend-slot"
  ]
}
```

## 并发 Agent 的状态分区

并发对等方共享每个 goal 一个事实来源事件流。LoopX 不应仅仅因为对等方、benchmark 用例或 UI 视图想要更窄时间线就分叉真相。

规范来源：

- goal 一个 registry 条目与活动 goal 状态；
- 紧凑生命周期记录一个追加式 run 历史；
- todo、验证、PR、交接、quota、修复与失败事件一个追加式 `loopx_rollout_event_v0` 日志；
- 正式 todos 作为持久化工作单元，包括存在时的 `claimed_by`、`task_class`、`action_kind`、`resume_when` 与 `unblocks_todo_id`。

派生视图：

- 每 agent 视图按 `agent_id`、`lane.lane_id`、`claimed_by` 与所选 `agent_lane_next_action_v0` 过滤；
- 每 todo 视图按 `todo_id` 与生命周期转换事件过滤；
- 每 case 视图按 `case_id` 与验证/结果事件过滤；
- 每 run 视图按 `run_id`、`source_event_id` 与紧凑因果引用过滤。

派生视图是只读 index。它们可以缓存、排列或总结，但必须携带指回规范事件的来源引用，且必须可从 registry、active state、run 历史、rollout 事件与 reward overlay 重算。派生视图不得成为分离的 active-state 文件、替代 run 历史或 dashboard 自有写路径。

当 agent 共享同一 goal、仓库边界、todo backlog 与操作员策略，且只需要一个作用域化的下一动作或时间线时，使用 agent-lane 投影。只有当工作具有不同 `goal_id`、持久化目标、受保护边界、owner 策略或 backlog（压缩进父 goal 的 `Next Action` 会产生误导）时才使用独立状态文件。

Goal 级 `Next Action` 保持同等级工作间的稳定决胜器。当它携带类型化 todo 绑定且新增可执行 agent todo 时，只有新 todo 具有严格更高优先级且属于相同 agent lane（或替换未认领的生成路由）才可重绑它。手动或未类型化操作员文本以及已被另一 agent 拥有的路由保持权威。仅建议性的启动检查保持在具体任务之下；必需连接、权限或运行时设置必须表示为显式高优先级前置条件或 blocker。

每个应参与并发 agent 视图的新 rollout 事件都应尽量包含至少一个稳定关联键：`agent_id`、`todo_id`、`run_id`、`lane.lane_id` 或 `case_id`。无法暴露关联键的事件仍可记录，但投影应把从它们构建的任何桥标记为推断而非观察。

## 生命周期

### 启动

启动回答项目是否已连接、谁拥有工作、首个安全决策是什么。

必需源状态：

- 稳定 `goal_id`；
- 已注册对等身份与配置时的咨询 scope；
- 适配器状态与项目局部状态路径；
- 本地状态忽略边界；
- 可选建议 todo 队列；
- 可选首个正式可运行 todo。

投影要求：

- 显示 goal id、当前用户 gate、顶层 agent todo 与下一安全动作；
- 区分候选 todo 与正式 todo；
- 把本地状态忽略问题报告为警告；
- 只在已连接 goal 存在后安装 heartbeat。

### 执行

执行回答本 Turn 是否应运行、确切做什么、谁拥有它、何时可以花费计算。

必需源状态：

- `interaction_contract_v0.user_channel`；
- `interaction_contract_v0.agent_channel`；
- `interaction_contract_v0.cli_channel`；
- 所选 `agent_lane_next_action_v0`；
- 所选 `todo_item_v0`；
- 注册多个 agent 时的 claim 或 lane 所有权；
- 工作后的验证工件引用；
- 配额花费前的紧凑 writeback。

投影要求：

- 用户必需工作必须指名具体用户 todos 或问题；
- 无用户 todo 加 `agent_channel.must_attempt=true` 不得变成安静 no-op；
- 安全绕行工作必须保持阻塞 gate 可见；
- Monitor todos 保持可见，但不改写通用 heartbeat prompt；
- `delivery_outcome` 与活动计数分开显示。

### 结束

结束回答工作是否完成、暂停、失败、交接或必须回滚。

必需源状态：

- `delivery_outcome`；
- 已完成、被接替、被阻塞或被推迟的 todo 状态；
- successor todo 或显式 no-follow-up 理由；
- 验证证据或 blocker 证据；
- 代码变更时的 PR/commit 引用；
- 另一个 agent 应继续时的交接目标与停止条件；
- 状态需补偿时的未来 `rollback_packet_v0`。

投影要求：

- 显示活动量前先显示结果层级；
- 保持失败外部资源设置为部分成功状态，当存在可用资源时；
- 显示交接/评审所有权，而非把每个开放 todo 当作全局；
- 暴露回滚候选而不自动执行回滚。

## 证据、关卡、奖励、交接

证据字段应紧凑且公开安全：

- `artifact_refs`：文档、smoke 文件、fixture 文件、PR、commits、dashboard；
- `validation_commands`：命令标签或公开安全路径，而非原始日志；
- `source_refs`：issue/PR id、公开社交 id、脱敏私有 connector id、实验 run 句柄；
- `boundary`：证明原始日志、凭据、私有路径与原始 transcript 缺席的布尔值。

关卡字段必须包括：

- gate owner 类别：`user`、`controller`、已注册 `agent` 或外部系统；
- 被阻塞 todo 或 scope；
- 所需问题或决策；
- approved/deferred/rejected 状态；
- 解决时的解除阻塞 todo 或下一安全动作。

奖励字段必须保持绑定 run：

- 被判定 run id 或生成时间戳；
- 决策标签与奖励极性；
- 公开安全原因摘要；
- 后续动作；
- 可选 active-state 摘要。

交接字段必须包括：

- 源 agent 与目标 agent；
- 被转移 todo id 或 scope；
- 停止条件；
- 目标需要的证据引用；
- 是否允许评审或自合并。

## 实现对齐

已对齐：

- `loopx quota should-run` 发出 `interaction_contract_v0` 与 `agent_lane_next_action_v0`。
- `loopx todo` 支持正式 todos、claims、deferred 状态、`resume_when=todo_done:<todo_id>`、`unblocks_todo_id` 与建议。
- `loopx status` 发出 `goal_channel_projection_v0`、`todo_index_v0`、紧凑操作员 gates、紧凑人类奖励、投递结局与 rollout-event todo 索引。
- `loopx_rollout_event_v0` 可以为新事件携带 lane、转换、因果、交接与代码引用。
- `examples/fixtures/long-horizon-self-iteration-rollout.public.json` 给前端与协议测试一个带 gate、交接、验证、deferred-resume、证据、状态分区、派生视图与推断显示桥覆盖的紧凑公开安全 fixture。
- `rollback_packet_v0` 定义在任何受保护动作前如何表示回滚、fix-forward、外部清理、支持请求与 todo 补偿。

部分对齐：

- 较旧 rollout 事件可能缺 before/after、因果与交接字段，因此任何动画或时间线必须显式标记推断桥。
- `task_graph_projection_v0` 已规定但还不是稳定 dashboard 输入。
- 提交到 todo 关联是基于 PR 文本、提交消息、todo 证据与 rollout 引用的约定。
- `todo suggest` 为用户 agent 产生 prompt 包；它不是全自主仓库分析器。
- 外部资源部分成功还不是通用协议。

尚未对齐：

- `rollback_packet_v0` 已规定并 smoke 测试，但尚无命令发出或执行包。
- PR 生命周期恢复条件限于结构化 rollout 事件证据：`resume_when=pr_merged:#532` 与 `resume_when=pr_merged:owner/repo#532` 可以在匹配 `pr_merge` 事件出现在本地 rollout 日志之后唤醒推迟 todos。无资格引用绑定到 todo 的 GitHub `task_repository`；跨仓库依赖必须使用有资格引用。缺失仓库身份以显式歧义诊断失效关闭。LoopX 不从散文推断。
- `global_manager_command_v0` 已规定并 smoke 测试，但尚无 host 集成或 CLI 命令发出它。
- 历史人类 gate 影响必须从公开安全证据推断。
- Frontstage 尚未从真实 status 加 rollout 事件渲染完整多 lane 自迭代时间线。

## 验收检查

一个协议实现或 fixture 只有在证明以下条件时可接受：

- 源与投影状态分离；
- 投影显式只读；
- 每个正式执行步骤映射到 todo、gate、run、event 或 reward；
- 候选 todos 不被静默提升；
- 可以为已注册 agent 选择至少一个 lane 感知的下一动作；
- 每 agent、每 todo、每 case 与每 run 视图是单一规范事件流之上的只读派生 index；
- agent-lane 投影不与独立状态文件混淆；
- 验证与 writeback 先于配额花费；
- 人类 gates 指名它们阻塞与解除阻塞什么；
- 交接指名源 agent、目标 agent、todo scope 与停止条件；
- 回滚表示为未来补偿动作，而非隐藏删除；
- 公开 fixture 不包含原始日志、原始 transcript、凭据或本地绝对路径；
- `python3 examples/long-horizon-self-iteration-rollout-fixture-smoke.py` 在 fixture 用作 UI 输入前通过。
