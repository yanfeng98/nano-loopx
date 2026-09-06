# event_store_migration_bridge_v0

`event_store_migration_bridge_v0` 是 Markdown active-state 读模型与未来事件投影读模型之间的失效关闭桥。

它不使事件投影成为权威。它记录在经评审的运行时变更可以优先用事件投影读取 status、quota、评审包、dashboard 或 slash-command 之前必须干净的关卡。

## 契约

桥包由 `loopx.control_plane.runtime.event_store_migration_bridge.build_event_store_migration_bridge` 构建，并携带：

- `source_of_truth`：当前为 `markdown_active_state`；
- `candidate_source`：当前为 `event_projection`；
- `stage`：`wait_for_event_read_path`、`dual_read_shadow`、`bounded_canary` 或 `promotion_candidate` 之一；
- `promotion_allowed`：本桥契约中始终为 `false`；
- `promotion_candidate`：仅在所有前置迁移检查干净时为 `true`；
- `checks`：面向读路径、一致性、回滚、canary、幂等、投影头与公共边界就绪性的紧凑布尔值；
- `missing_for_shadow`、`missing_for_canary` 与 `missing_for_promotion`；
- `dual_read`、`rollback` 与 `canary` 子契约。

## 阶段

`wait_for_event_read_path` 表示事件读路径或结构化 active-state 投影尚未就绪。唯一安全的动作是完成这些前置条件。

`dual_read_shadow` 表示两个读模型可以对比，但 Markdown 仍然是事实来源。任何一致性差异都必须优先 Markdown，并记录紧凑差异，而不是静默提升事件投影。

`bounded_canary` 表示一致性、回滚、幂等、投影头与公共边界检查已干净到足以运行小型只读 canary。canary 使用有限的 goal 集与时长，事件写入偏好仍被禁用。

`promotion_candidate` 表示桥已有足够证据提出一个单独的、经评审的运行时 PR。它不是自动迁移状态。

## 必要关卡

迁移要求以下全部干净：

- 事件读路径就绪；
- active-state 结构化投影就绪；
- 双读一致性在 todo id、状态、priority/planner 顺序、`claimed_by`、gate 引用与投影头序列上干净；
- 事件投影头与 event store 头一致；
- 回滚计划已记录；
- 受限 canary 通过；
- 幂等冲突干净；
- 公共边界干净。

## 回滚

回滚是必须的。在后续经评审的写路径变更改变事实来源之前，回退来源始终是 Markdown active-state 解析器。

回滚触发包括：

- 一致性差异；
- 投影头不匹配；
- 事件追加冲突；
- 公共边界警告；
- canary 回归。

回滚动作是禁用事件投影偏好，并保留 Markdown 解析器作为权威读取回退。

## Canary

受限 canary 是只读的：

- 小 goal 上限，默认 1；
- 短时长，默认 30 分钟；
- 事件写路径已禁用；
- 读取偏好仍为 Markdown；
- 观察 status todo 摘要、quota 所选 todo、评审包 todo 引用、dashboard/frontstage 投影与事件投影头序列。

成功要求：无一致性差异、无幂等冲突、无私有边界警告，并且回滚一条命令即可安全完成。
