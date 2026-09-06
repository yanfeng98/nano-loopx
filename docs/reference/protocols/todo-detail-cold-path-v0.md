# todo_detail_cold_path_v0

`todo_detail_cold_path_v0` 是 LoopX todo 的冷路径详情契约。它让 dashboard、评审工具与 agent 在不让 `status`、`quota should-run`、heartbeat prompt 或交接包超出热路径预算的情况下检查完整 todo。

热路径仍是 `todo_summary_v0` 加持界 lane，例如 `first_open_items`、`executable_backlog_items` 与 claim 感知 lane。这些 lane 回答分发问题：「当前执行者现在应该看哪个 todo？」它们不是归档 todo 存储。

## 热路径引用

当消费者需要下钻目标时，热路径生产者只可附加一个紧凑引用：

```json
{
  "schema_version": "todo_detail_ref_v0",
  "goal_id": "loopx-meta",
  "role": "agent",
  "todo_id": "todo_1234abcd",
  "projection": "todo_detail_cold_path_v0",
  "page_size_hint": 20
}
```

该引用是可选的。它不得复制 notes、evidence 正文、原始日志、私有路径、verifier 输出或完整同级 todo 列表。引用缺失时消费者仍可从紧凑摘要路由。

## 冷路径形状

分页详情响应应使用如下形状：

```json
{
  "schema_version": "todo_detail_cold_path_v0",
  "goal_id": "loopx-meta",
  "role": "agent",
  "todo_id": "todo_1234abcd",
  "generated_at": "2026-06-27T00:00:00Z",
  "source": {
    "kind": "active_state_todo",
    "state_updated_at": "2026-06-27T00:00:00Z"
  },
  "todo": {
    "schema_version": "todo_item_v0",
    "todo_id": "todo_1234abcd",
    "role": "agent",
    "status": "open",
    "priority": "P1",
    "title": "Design cold-path todo detail.",
    "task_class": "advancement_task",
    "action_kind": "todo_projection_pagination",
    "claimed_by": "codex-main-control"
  },
  "pages": {
    "current": {
      "kind": "todo_detail",
      "items": []
    },
    "next_page_token": null
  },
  "related": {
    "sibling_open_count": 12,
    "blocked_by_user_todo_ids": [],
    "unblocks_todo_ids": [],
    "successor_todo_ids": []
  },
  "truth_contract": {
    "source_of_truth": "active_goal_state_and_event_ledger",
    "projection_is_writable": false,
    "write_api": false,
    "refresh_rule": "Requery after any todo, gate, reward, refresh-state, or quota lifecycle event."
  }
}
```

## 分页规则

- `todo` 携带规范解析后的 todo item，而不是 markdown 摘录。
- `pages.current.items` 可包含紧凑公开安全详情记录，例如 notes、证据摘要、收尾摘要与相关生命周期事件引用。
- 大型 note/evidence 正文必须摘要化。原始任务文本、transcript、本地文件路径、凭据、私有链接、原始 verifier 输出与原始 benchmark 轨迹都不是合法 page item。
- `next_page_token` 是不透明的。消费者不得解析它或从中推断排序。
- 生产者应使第一页足以供人类检查一个 todo。跨 todo 列表浏览应放在带过滤的列表端点或 dashboard 视图中，而不是单个 todo 详情响应中。

## 排序与新鲜度

详情响应是投影。它应在已知时保留 active-state todo 排序元数据（`index`、`source_section`、`priority` 与 `role`），但不得成为第二个可写排序存储。消费者必须在任何生命周期事件之后把详情视为过期，并在做出新的分发或合并决策之前重新查询。

## 验收检查

一个有效的公开 fixture 或实现必须证明：

- `schema_version` 恰好是 `todo_detail_cold_path_v0`；
- 热路径界面至多携带 `todo_detail_ref_v0`，绝不携带完整详情响应；
- `truth_contract.projection_is_writable=false`；
- `truth_contract.write_api=false`；
- 响应恰好引用一个 `goal_id`、`role` 与 `todo_id`；
- page token 不透明且可选；
- 不投影本地绝对路径、凭据、原始日志、原始 transcript、原始 benchmark 轨迹或原始 verifier 输出；
- 缺失时消费者可以安全忽略 `todo_detail_ref_v0` 与 `todo_detail_cold_path_v0`。
