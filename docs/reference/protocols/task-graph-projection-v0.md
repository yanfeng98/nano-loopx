# task_graph_projection_v0
> [English](task-graph-projection-v0.md)

`task_graph_projection_v0` 是既有 LoopX 状态之上的可选只读图视图。它帮助 agent 与操作员看到依赖、gate、验证、修复与交接关系，而无需创建第二个任务存储。

事实来源仍为：

- 追加式事件 ledger 与紧凑 run index；
- 活动 goal 状态及其 todos；
- 操作员 gate 与用户 todos；
- lease 或 todo claim；
- quota 与状态投影；
- run 历史证据与 blocker writeback。

图的 Todo 节点从构建 `todo_planning_inventory_v0` 时使用的同一权威域状态行中选择：`items`、`deferred_items`、`blocker_items` 与 `monitor_open_items`。图启用了选择器的终态行扩展，使已完成的前置项与证据保持可见；规划库存排除这些行。这防止图、horizon 与组合消费者在假装每个 lens 具有相同 scope 的前提下发明各自的可见性 lane 并集。它不使图变成 agent 作用域：图可以增加 gate、证据、验证与交接上下文，但从不分配 `current_agent` claim 含义，也不拥有动作选择。

该投影可以出现在 `loopx --format json status --include-task-graph` 的 `attention_queue.items[].task_graph_projection` 下。默认 status 输出把这个对象保持在冷路径上，使 dashboard 热路径保持在其接口预算内。完整 `loopx --format json review-packet --goal-id <goal-id>` 输出可以为操作员评审包含同一对象。仅交接的 review-packet 界面应保持紧凑，除非未来接口预算明确允许，否则省略该图。

## 形状

```json
{
  "schema_version": "task_graph_projection_v0",
  "mode": "read_only",
  "goal_id": "loopx-meta",
  "generated_at": "2026-06-21T12:00:00Z",
  "derived_from": {
    "source_of_truth": [
      "event_ledger",
      "active_goal_state",
      "todos",
      "gates",
      "leases",
      "run_history"
    ],
    "status_item_goal_id": "loopx-meta",
    "active_state_updated_at": "2026-06-21T11:55:00Z",
    "run_history_window": "compact_latest_runs"
  },
  "truth_contract": {
    "event_ledger_is_source_of_truth": true,
    "projection_is_writable": false,
    "write_api": false,
    "recompute_rule": "Recompute from status, active state, gates, leases, and run history after each lifecycle event."
  },
  "limits": {
    "user_gate_node_limit": 2,
    "user_gate_open_count": 5,
    "user_gate_truncated_count": 3
  },
  "nodes": [],
  "edges": []
}
```

`limits` 说明热路径截断。任务图只能展开前 `user_gate_node_limit` 个开放用户 gate 节点。当更多用户 gate 开放时，`user_gate_open_count` 与 `user_gate_truncated_count` 必须如实说明。需要完整 gate 列表的消费者应使用用户 todo 详情路径或完整 review-packet 字段，而不是把图当作穷举存储。

## 节点

每个节点必须紧凑且必须指回持久化 LoopX id。允许的 `kind` 值有：

- `deliverable`：有 todo 背书的工件或实现步骤；
- `gate`：用户、owner 或操作员决策点；
- `gate_summary`：用于用户 gate 被图热路径截断时的紧凑「还有更多 gate」节点；
- `lease`：活动 claim 或 worker 所有权信号；
- `validation`：smoke、检查、CI 结果或评审证明；
- `repair`：自修复或 blocker 恢复步骤；
- `handoff`：从一个 agent 或界面到另一个的转换；
- `evidence`：紧凑 run 历史证据项。

必需节点字段：

- `node_id`：本投影内稳定；
- `kind`；
- `title`；
- `state`：`open`、`ready`、`blocked`、`done`、`waiting` 或 `unknown` 之一；
- `refs`：紧凑引用，如 `todo_ids`、`gate_ids`、`lease_ids`、`goal_ids`、`run_ids` 或 `review_packet_ids`。

节点不得复制原始任务文本、transcript、日志、凭据、私有文件路径或大型 run 工件。它们应只总结分发或评审所需的关系。

## 边

边描述一个节点为何影响另一个。允许的 `relation` 值有：

- `depends_on`；
- `blocks`；
- `validates`；
- `repairs`；
- `audits`；
- `continues`；
- `hands_off_to`；
- `supersedes`。

每条边必须指明 `from_node_id`、`to_node_id`、`relation` 与紧凑公开安全 `reason`。边可以携带与节点相同的紧凑 `refs` 对象。边不授予运行命令或修改状态的权限。

`repairs`、`audits` 与 `continues` 是血统关系，不是生命周期命令。它们从既有 run 历史、todo/gate 元数据与紧凑 blocker 或验证 writeback 推导：

- `repairs` 表示一个修复或 replan 节点旨在恢复某个所选工作 lane。
- `audits` 表示紧凑 run 历史证据评审、检查或界定某个所选工作 lane。
- `continues` 表示紧凑 run 历史证据是某个所选工作 lane 的延续。

这些关系可以帮助 dashboard 或评审者解释某个工作项为何仍活动、过期、已修复或可安全交接。它们不得创建图恢复命令、修改 todo 状态，或取代针对当前 quota、gates、claims 与 run 历史的新鲜度检查。

## 写入边界

`task_graph_projection_v0` 没有写权限。它绝不暴露图写入命令、浏览器写入控件、隐藏 scheduler 或替代 lease 存储。状态变更继续通过既有 LoopX 生命周期命令：

- `loopx todo ...`；
- `loopx operator-gate ...`；
- `loopx reward ...`；
- `loopx refresh-state ...`；
- `loopx quota spend-slot ...`；
- 保留相同 event-ledger 语义的未来 server/MCP 写 API。

消费者应在任何生命周期事件后把图视为过期，直到它从当前状态与 run 历史窗口重算。

## 验收检查

一个有效的公开 fixture 或实现必须证明：

- `schema_version` 恰好是 `task_graph_projection_v0`；
- `mode` 是 `read_only`；
- `truth_contract.projection_is_writable=false`；
- `truth_contract.write_api=false`；
- `limits.user_gate_node_limit` 存在；
- `limits.user_gate_open_count` 存在；
- `limits.user_gate_truncated_count` 存在；
- 每个节点 id 唯一；
- 每条边的端点引用既有节点；
- 每个节点与边引用既有 LoopX id，而非原始私有物料；
- repair、audit 与继续关系只渲染为既有 todos、gates、leases 与紧凑 run id 之上的派生只读血统；
- 不投影本地绝对路径、凭据、原始 transcript 或原始日志；
- 缺失时 status/review-packet 消费者可以安全忽略该字段。
