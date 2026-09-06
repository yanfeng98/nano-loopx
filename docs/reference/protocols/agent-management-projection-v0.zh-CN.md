# agent_management_projection_v0
> [English](agent-management-projection-v0.md)

`agent_management_projection_v0` 是既有 LoopX agent、todo、quota、历史与证据状态之上的只读操作员视图。它存在的目的是让 dashboard 与评审包界面能显示哪些 agent 活动、每个 agent 认领了什么、以及什么证据使下一 Turn 安全。

它不引入运行时 `task` 对象。在 LoopX 中，`todo_id` 保持 `goal_id` 内唯一的持久化工作项身份。

## 目的

投影帮助操作员回答：

- 此 goal 存在哪些已注册 agent；
- 每个 agent 应把哪个 todo 视为当前工作项；
- agent 是运行中、等待、阻塞、监控，还是可能过期；
- 哪些证据、交接笔记、工作区、配额与下一动作解释该状态。

首个 dashboard 实现应是可观测性界面。它可以渲染成熟 agent 控制台布局或复用兼容公开 UI 代码，但不得成为分发器、lease 管理器、工作区管理器或写入队列。

## 事实来源

投影由以下内容派生：

- `loopx status --format json`；
- active-state 的 `Agent Todo` 与 `User Todo` 小节；
- 已注册 agent 与 claim 元数据；
- quota 的 `agent_lane_next_action`、`interaction_contract` 与 scheduler 提示；
- 紧凑 run 历史与 agent 作用域证据 ledger；
- 存在时的任务图、交接与评审包投影；
- 冷路径 `agent_material_frontiers` 输入上的可选预构建 `agent_material_frontier_v0` 包，仅当当前执行信封声明 goal 作用域 `material_lifecycle` capability 时消费。

投影在任何生命周期事件后过期，直到重算。消费者必须容忍缺失字段，并回退到既有 status/review-packet 载荷。

可用时，`loopx status --format json` 在顶层 `agent_management_projection` 键暴露该视图。消费者仍应把该键视为可选，使旧 status 生产者与缓存快照保持可读。

## 非目标

本契约有意不增加：

- 新 `task_id`；
- 可写 Kanban/任务表；
- 自动分发、取消或回收行为；
- 独立评论系统；
- 工作区分配运行时；
- 工具网关或 agent profile 运行时。

状态变更仍经既有 LoopX 生命周期命令，如 `loopx todo ...`、`loopx refresh-state ...`、`loopx quota ...`、evidence-log writeback，以及保留相同 event-ledger 语义的未来 API。

## 形状

```json
{
  "schema_version": "agent_management_projection_v0",
  "mode": "read_only",
  "goal_id": "loopx-meta",
  "generated_at": "2026-07-06T00:00:00Z",
  "style_hint": {
    "preferred": "mature_agent_console_or_loopx_dark_showcase",
    "license_boundary": "reuse_public_compatible_code_only"
  },
  "truth_contract": {
    "todo_is_runtime_work_item": true,
    "projection_is_writable": false,
    "introduces_task_runtime": false,
    "write_api": false
  },
  "agents": []
}
```

## Agent 行

每个 agent 行是一个已注册 agent 的紧凑卡片或表行。

必需字段：

- `agent_id`；
- `agent_model`：`peer_v1`；
- `state`：`running`、`waiting`、`blocked`、`monitoring`、`scope_wait`、`stale` 或 `unknown` 之一；
- `current_todo`：`todo_row_v0` 对象或 `null`；
- `next_action`：紧凑本地控制下一动作文本。允许私有项目引用；不允许内联凭据。可共享 sink 在导出前必须脱敏私有引用；
- `last_activity_at`：已知最佳 status、quota、todo 或 run 时间戳；
- `evidence_refs`：紧凑证据 id、文档路径、run id 或评审包引用。

可选字段：

- `profile_role`：咨询性功能标签，如 `reviewer`、`monitor` 或 `runtime-validation`；它不是等级或权限；
- `scope_summary`；
- `quota_state`；
- `scheduler_state`；
- `workspace_ref`；
- `handoff_refs`；
- `handoff_note`；
- `material_frontier`；
- `stale_claim_hint`；
- `blocked_on`；
- `recent_events`；
- `display_tone`。

当可运行推进工作与阻塞维护并存时，投影把可运行 todo 保持在 `current_todo`，可以最高优先级阻塞维护 todo 作为单独 `blocked_on` `todo_row_v0` 暴露。Blocker 保持可见，而无需改变 todo 所有权或使整个对等方看起来阻塞。

## Todo 行

`todo_row_v0` 是既有 LoopX todo 的 dashboard/评审包表示。它不是运行时任务对象。

必需字段：

- `todo_id`；
- `goal_id`；
- `role`；
- `status`；
- `priority`；
- `title`；
- `task_class`；
- `action_kind`；
- `claimed_by`。

可选字段：

- `required_write_scopes`；
- `required_capabilities`；
- `target_capabilities`；
- `blocks_agent`；
- `unblocks_todo_id`；
- `successor_todo_ids`；
- `resume_when`；
- `evidence_refs`；
- `handoff_refs`；
- `workspace_ref`；
- `updated_at`。

为操作员熟悉起见，行可以渲染为「task」卡片，但 API 与状态名应保持 `todo` 术语，避免暗示第二运行时模型。

## 交接笔记

Agent 间交接应作为附加到既有 todo、历史与证据引用的类型化笔记出现。无物料上下文的行保留既有 `handoff_note_v0` 形状：

```json
{
  "schema_version": "handoff_note_v0",
  "handoff_id": "handoff_123",
  "todo_id": "todo_abc",
  "from_agent": "codex-builder",
  "to_agent": "codex-reviewer",
  "intent": "review_before_merge",
  "summary": "Implementation and focused smoke are ready for review.",
  "evidence_refs": ["run_123", "docs/reference/protocols/example.md"],
  "unresolved_decisions": [],
  "blocked_on": null,
  "suggested_next_action": "Read the diff and smoke output before merge."
}
```

LoopX 从既有 todo、历史与证据行派生该笔记。当前信号包括 `blocks_agent`、`claimed_by`、`unblocks_todo_id`、`successor_todo_ids`、`resume_when`、`note`、`evidence` 与紧凑 rollout 事件引用。同一 `handoff_note_v0` 对象因此可以出现在 `agent_todo_summary` 项、`todo_index` 行或未来 dashboard 行中，而不引入第二任务模型。

投影可以在 agent 行中显示最新交接笔记，但该笔记不创建聊天流、分发器队列、批准机制或独立于源 todo 的运行时任务。

当冷路径还为同一 agent 收到完整 `agent_material_frontier_v0`，且调用方在 `available_capabilities` 中传 `material_lifecycle` 时，管理投影可以把类型化笔记富化为 `handoff_note_v1`：

```json
{
  "schema_version": "handoff_note_v1",
  "handoff_id": "handoff_123",
  "todo_id": "todo_abc",
  "from_agent": "codex-builder",
  "to_agent": "codex-reviewer",
  "material_frontier_summary": {
    "required_count": 5,
    "current_count": 1,
    "stale_count": 1,
    "missing_count": 0,
    "inaccessible_count": 1,
    "required_unread_count": 2
  },
  "material_ref_count": 5,
  "material_refs": [
    {
      "material_id": "runtime-contract",
      "relation": "required",
      "purpose": "review the current contract"
    }
  ],
  "material_refs_truncated": true
}
```

Agent 行上的 `material_frontier` 使用相同的有界摘要/引用形状，`schema_version=agent_material_handoff_projection_v0`。至多暴露四个引用。投影从不转发回执、观察或必需修订、边界可用性、gate 状态、权限、权限所有权或源正文。Successor 从当前 goal 权限与其自身 agent 作用域需求与回执重建自己的前沿。可选冷路径输入本身不创建 agent 行、claim 或任务。

物料投影默认关闭。没有 `material_lifecycle` 时，LoopX 忽略 `agent_material_frontiers`，并省略 `material_frontier`、`handoff_note_v1` 与 `source_summary.material_frontier_count`。能力缺失是观察到的运行时条件，不是用户 gate：它不创建 todo、通知或权限请求。

Status 支撑的 CLI 入口点保留相同执行信封：`status`、`quota` 与 `review-packet` 接受可重复 `--available-capability` 值并通过 status 集合透传。投影缓存身份包括规范化能力集，因此默认关闭快照不能满足启用请求，启用快照也不把物料字段泄漏进默认请求。

冷路径关联按 `(goal_id, agent_id)` 作用域，而非仅 agent 身份。显式 status goal 过滤器优先，其次当前 todo 的 goal，然后单一无歧义行的 goal。当多 goal agent 行没有唯一 goal 上下文时，LoopX 省略物料富化，而非按输入顺序选择前沿。

## 过期 Claim 提示

`stale_claim_hint` 是可观测性警告，不是自动回收规则。它表示某已认领 todo 相对预期节奏没有近期活动，或投影无法为运行中 claim 找到新鲜证据。

```json
{
  "state": "suspected_stale",
  "claimed_by": "codex-value-explorer",
  "last_activity_at": "2026-07-06T00:00:00Z",
  "reason": "last activity is older than expected cadence",
  "recommended_operator_action": "inspect evidence or ask the same agent to resume"
}
```

Dashboard 可以把它显示为警告徽章。LoopX 不应仅凭该投影自动清除 claim、重新分配工作或丢弃证据。

## 工作区引用

`workspace_ref` 是预期工作发生位置的显示提示：

```json
{
  "kind": "canonical_checkout|worktree|external|unknown",
  "label": "codex/value-explorer",
  "path_safe": false,
  "branch": "codex/value-explorer-post702",
  "write_scope": ["docs/**", "apps/presentation/dashboard/**"]
}
```

公开或托管 dashboard 应避免本地绝对路径。本地回环 dashboard 在源载荷已公开路径且界面显式本地/仅操作员时，可以显示路径。

## 前端样式与代码复用

产品界面可以从两个视觉方向借鉴：

- 成熟 agent 控制台风格：密集行、清晰的 owner/state/timestamp 列、克制徽章与快速扫描；
- LoopX 暗色展示风格：暗色导轨、轻动效点缀、证据轨迹与高对比 agent lane。

从 Hermes 或另一项目复制实现代码前，agent 必须验证：

- 来源公开或对此仓库显式批准；
- 许可证与 LoopX 发行兼容；
- 复制代码保留所需署名或声明文本；
- 私有/内部标识符、注释、截图、URL 与测试数据被移除或泛化；
- 复制代码不导入违反本投影契约的运行时分发器、profile 系统、工具网关或任务数据库。

这些检查不满足时，只借用交互模式并编写原生 LoopX 实现。

## 验收检查

一个有效实现或 fixture 应证明：

- `schema_version` 恰好是 `agent_management_projection_v0`；
- `mode` 是 `read_only`；
- `truth_contract.projection_is_writable=false`；
- `truth_contract.introduces_task_runtime=false`；
- 每个 `current_todo.todo_id` 引用既有 LoopX todo；
- 本投影不暴露任何可写任务、分发器、取消、回收或工作区动作；
- 过期 claim 仅渲染为警告；
- 交接笔记引用既有 todo/历史/证据 id；
- 无观察到的 `material_lifecycle` capability 时物料前沿字段缺席，存在时保留其有界形状；
- 公开 fixture 不包含凭据、原始日志、私有文档、原始轨迹、本地绝对路径或仅内部源物料；
- 投影缺席时 dashboard 消费者仍可用。
