# Frontstage Channel 与 Lease 路线图

> [English](frontstage-channel-lease-roadmap.md)

LoopX 不应该变成一个聊天产品。它的持久价值在 backstage 控制面：registry、活跃状态、append-only 事件历史、quota、gates、leases 与可审计恢复。缺失的产品层是 frontstage 投影，让人在不读原始 CLI 转储的情况下理解和协调该控制面。

本说明把产品方向表述为：

```text
frontstage channel UX + backstage LoopX ledger
```

Channel 是视图。Ledger 是 truth。

## 产品边界

LoopX 应该借用协作语言，但把事实源留出聊天历史：

- **Goal 可以投影成 channel**：一条时间线，包含最新状态、下一个动作、user todos、agent todos、gates、artifacts、quota 与 run 事件。
- **Agent 可以投影成 workspace 成员**：controller、executor、reviewer、monitor、critic 或 dreaming/规划提案者，各有 scope 与最后动作。
- **任务 claim 默认为每 todo 的软路由**。当具体争用案例需要排他性时，可选的硬 lease 为一个 `todo_id` 增加 TTL、写范围、幂等性与冲突处理。
- **聊天或 channel 线程是投影**：对人类协作有用，但绝不是唯一的持久 authority。

关键产品教训不是"加 Slack 式聊天"。而是：人类以 channel、成员、任务与审批思考，而 agent 需要 registry、状态、历史、quota、gates 与 leases。

## 最小 Schema

### `goal_channel_projection_v0`

这是对既有 LoopX 状态的只读、面向人的投影。它让 frontstage 把 goal 渲染成 channel，而不让 channel 成为新的事实源。Append-only run ledger、活跃状态与 registry 保持权威；投影只携带紧凑来源引用与新鲜度元数据。

```json
{
  "schema_version": "goal_channel_projection_v0",
  "goal_id": "loopx-meta",
  "display_name": "LoopX Meta",
  "generated_at": "2026-06-20T00:00:00Z",
  "source_refs": {
    "status_generated_at": "2026-06-20T00:00:00Z",
    "active_state_updated_at": "2026-06-20T00:00:00Z",
    "latest_run_generated_at": "2026-06-19T23:55:00Z",
    "review_packet_generated_at": null
  },
  "waiting_on": "codex",
  "latest_status": "terminal_bench_case_running",
  "next_action": "compact-poll the active benchmark job",
  "decision_frame": {
    "user_action_required": false,
    "agent_action_required": true,
    "quiet_noop_allowed": false
  },
  "quota": {
    "state": "eligible",
    "reason": "1 compute quota",
    "spend_policy": "spend after validated writeback"
  },
  "user_todos": [
    {
      "todo_id": "todo_user_1",
      "title": "Review the bounded delivery packet.",
      "status": "open",
      "priority": "P0"
    }
  ],
  "agent_todos": [
    {
      "todo_id": "todo_agent_1",
      "title": "Advance the first executable safe side path.",
      "status": "open",
      "priority": "P1",
      "claimed_by": "codex-side-bypass"
    }
  ],
  "open_gates": [
    {
      "gate_id": "gate_owner_decision",
      "kind": "operator_gate",
      "status": "waiting_on_user",
      "blocks": ["todo_user_1"]
    }
  ],
  "artifacts": [
    {
      "kind": "doc",
      "label": "latest public review packet",
      "path": "docs/showcases/README.md"
    }
  ],
  "active_leases": [
    {
      "todo_id": "todo_agent_1",
      "owner_agent": "codex-side-bypass",
      "lease_until": "2026-06-20T00:30:00Z",
      "write_scope": ["docs/**"]
    }
  ],
  "recent_events": [
    {
      "generated_at": "2026-06-19T23:55:00Z",
      "classification": "validated_progress",
      "summary": "public-safe compact progress event"
    }
  ],
  "source_warnings": []
}
```

v0 来源映射应保持平淡且可检查：

| 投影字段 | 来源 surface |
| --- | --- |
| `goal_id`、`display_name`、`waiting_on`、`latest_status` | `loopx status` 项目资产与 registry 元数据 |
| `next_action`、`user_todos`、`agent_todos`、`open_gates` | 活跃状态 todo/gate 区块加上 `review-packet` 摘要 |
| `decision_frame` | 来自 `quota should-run` 的 `interaction_contract` 与 review-packet 路由 |
| `quota` | `quota should-run`，含 spend policy 与引入时的 capability/workspace guard |
| `artifacts` | 已由 `goal_boundary` 允许的 public-safe 文档、紧凑 run artifacts、review packets 或 showcase 资产 |
| `active_leases` | 当前软 claim 与显式提供的可选 `task_lease_v0` 行 |
| `recent_events` | 仅紧凑 run-history 行，不是原始日志或 transcript |
| `source_warnings` | 过期状态、todo 投影缺口、私有边界遗漏或缺失 authority 来源 |

投影必须排除原始聊天 transcript、原始 benchmark 任务文本、原始轨迹、凭据、生产日志、私有文档 URL、本地绝对路径与可写命令。如果某个有用 frontstage 字段需要上述来源之一，就输出一个紧凑 `source_warnings` 项，而不是复制原始材料。

Frontstage 消费方应把它当作输入快照：

- 从 LoopX 刷新它，而不是在 UI 中编辑；
- 把受控动作渲染为指向 CLI/review-packet 流程的链接，而不是隐藏的写 authority；
- 在受影响的卡片附近显示过期或缺失来源警告；
- 保持事件详情下钻绑定到紧凑 run artifacts；以及
- 绝不让 channel 视图覆盖 `goal_boundary`、operator gates、quota、必需 capability、workspace guard 或 task leases。

首个产品路径读模型位于
`loopx/control_plane/goals/goal_channel_projection.py`，由 `examples/project/goal-channel-projection-smoke.py` 与 `examples/project/goal-channel-frontstage-fixture-smoke.py` 覆盖。它有意保持只读：调用方传入已经紧凑的 status、quota、run-history、review-packet、artifact 与 lease/claim 载荷；构建器在出现原始或疑似私有字段时发出 `source_warnings`，而不是把这些值复制进 channel。`loopx/presentation/renderers/goal_channel_html.py` 中的静态 HTML 渲染器与 `examples/goal-channel-frontstage-fixture.py` 中的夹具把这个投影渲染成语义面板，带 `data-panel` 标记、无写控件，以及可见的 truth 契约。`loopx --format json status` 与 loopback
`serve-status` feed 现在在 `attention_queue.items[].goal_channel_projection` 上暴露同一只读投影，让 dashboard 无需重算项目 truth 就能渲染 channel。

### `agent_profile_v1` 与 `agent_member_v1`

由 registry 拥有的 `agent_profile_v1` 契约定义在
[`docs/product/foundations/agent-profile-contract.md`](../foundations/agent-profile-contract.md)。
用它作为注册 agent id 与建议性 capability、scope、动作偏好的事实源。Runtime authority 仍来自 peer 身份、任务 claim/lease、边界、仓库策略与显式延续策略。Channel 路线图只需要只读成员投影。

这是参与某 goal 的行动者的身份与活动投影：

```json
{
  "schema_version": "agent_member_v1",
  "agent_id": "codex-local-controller",
  "agent_model": "peer_v1",
  "profile_role": "reviewer",
  "profile_role_is_advisory": true,
  "goal_id": "loopx-meta",
  "current_claims": ["todo_abc123"],
  "last_action": "refresh_state",
  "handoff_assignment_status": "task_policy_selected"
}
```

Profile role 应保持在产品级且可移植：executor、reviewer、monitor、critic、dreaming proposer。它们引导 UI 文案与发现，而不是身份排名或默认权限。具体 authority 来自 `goal_boundary`、claims/leases、类型化任务策略与活跃状态 todos。

### `task_lease_v0`

这个可选的文件支撑本地并发契约通过 `loopx task-lease acquire|renew|transfer|release|inspect` 发布。它不替换默认软 `claimed_by` 路由，也不参与 quota 决策。PENDING 键按 todo：`(goal_id, todo_id)`。不要因为一个 todo 被 claim 就序列化整个 goal；当 gates 与写范围允许时，同一 goal 下相互独立的 todos 应保持可独立认领。
在这个 runtime 模型中，LoopX 没有单独的 issue 对象：`goal_id` 命名控制面边界，`todo_id` 命名该边界内的工作项。
Peer 控制面保持显式指派：`claimed_by` 或 task lease 拥有一个 todo，而写仓库的 peers 在任务或 goal 策略要求时使用隔离 worktree。小到符合 AGENTS 的变更可以在有 evidence 时自合入；否则完成会创建一个独立后继，或在独立交接上创建显式评审动作，可选排除作者。

```json
{
  "schema_version": "task_lease_v0",
  "goal_id": "loopx-meta",
  "todo_id": "todo_123",
  "owner": "codex-local-controller",
  "idempotency_key": "loopx-meta:todo_123:20260615T1230Z",
  "write_scopes": ["docs/product/roadmaps/frontstage-channel-lease-roadmap.md"],
  "version": 1,
  "lease_epoch": 1,
  "acquired_at": "2026-06-15T12:00:00Z",
  "updated_at": "2026-06-15T12:00:00Z",
  "expires_at": "2026-06-15T12:30:00Z",
  "status": "active"
}
```

当前实现是本地、文件支撑的，带按 goal 的锁、续期、转移、释放、注册 owner 校验与过期 owner 失效。一个具体的同 agent/多进程完成竞态确立了第一个生命周期采用案例：lease 生效时，`todo complete` 必须呈现获取时的幂等键与当前版本，并在 Todo 与后继写回期间持有 lease 锁。这对组合围栏住共享同一注册 `agent_id` 的执行实例；续期、转移、释放与终端写回都要求当前版本。`lease_epoch` 是 authority 拥有的代际：acquire 与 transfer 推进它，而普通续期只推进 `version`。

释放与已提交的终端写回在同一 per-todo 路径保留非活跃的 `status=released` 记录。这个单记录墓碑保留最后版本与代际，所以重新获取不能重置到版本 1。复用刚退役的执行键会被拒绝；新执行键接收下一个版本与代际。Active-lease 投影忽略墓碑，而精确的释放重试返回其原始终端结果。已完成的 Todo 保持终端幂等，所以过期回放不能在规范完成提交后再追加第二个后继。将来的 server 可以拥有相同 schema 与协调 surface。
冲突应当通过 `(goal_id, todo_id)` 加重叠写范围检查检测：另一 agent 可以认领同一 goal 中的不同 todo，但对同一 todo 的第二个 pending claim 必须 fail closed、续期或显式转移所有权。

## 优先级

P1：

- 保持已发布的可选 `task_lease_v0` runtime、生命周期围栏与冲突冒烟稳定。已验证的同 agent 完成竞态证明 lease 生效时围栏 `todo complete` 的必要性；不要默认把 lease 获取变成 quota gate。
- 把已发布的 React `/frontstage` 路由当作基线 `goal_channel_projection_v0` 读取器。未来工作应打磨视觉验收、operator onboarding 与本地夹具真实性，同时保持"CLI/status 导出是来源、浏览器无写权限"的不变量。

P2：

- 在一个采用案例证明额外信号有用之后，再决定活跃硬 lease 行是否应加入现有 agent-member status/review 投影。
- 构建 Raft 风格的本地 frontstage 视图，从 LoopX 投影渲染 channel 时间线与成员活动。
- 让 dreaming/规划提案作为独立 channel 泳道或徽章出现。
- 添加桥接 adapter，可以向协作工具发布 channel 摘要，同时保留 LoopX 作为记录 ledger。

## 非目标

- 不把对话历史当作唯一项目状态。
- 不让 UI 成员标签覆盖 `goal_boundary`、operator gates 或 run 权限。
- 不为第一个 schema 要求 server；CLI 必须保持可用 fallback/client。
- 不让后台 dreaming 在未经正常 `quota should-run` 与 lease 路径的情况下认领交付工作。

## 验收框架

第一个成功切片应证明：人类打开一个 goal 视图就能看到：

- 这个 goal 是什么；
- 当前谁或什么负责；
- 哪个任务被认领、截止何时；
- 该 claim 可以触及哪些文件/surface；
- 哪个事件让当前状态成立；
- 下一个安全动作是什么。

对应 agent 应当能够读取机器投影，避免双重运行、双重 spend 或越界写入。
