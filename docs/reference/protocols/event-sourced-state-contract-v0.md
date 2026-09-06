# event_sourced_state_contract_v0

`event_sourced_state_contract_v0` 定义 LoopX 如何在保持 `ACTIVE_GOAL_STATE.md` 为人/agent 工作台的同时，把规范的 todo 与历史事实移到追加式事件流。

这是产品/控制面契约，不是特定数据库的实现要求。实现可以把流存储为 JSONL、SQLite 行或另一种 local-first 追加式格式，只要重放、排序、隐私与幂等行为相同。

## 角色拆分

`ACTIVE_GOAL_STATE.md` 仍是人/agent 工作台。它是可读界面，agent 与用户可以在其中检查当前 goals、进度、todos、gates、验证界面与下一动作。当项目显式忽略本地状态时，它可以保留私有或项目局部上下文。

规范的 todo/历史事实归事件流：

- Markdown 编辑不是规范状态变更，除非由 LoopX 命令或迁移/回填工具转换成事件。
- Markdown 渲染器是投影。它们可以从事件重新生成，并可为 prompt 与评审预算压缩旧详情。
- 迁移期间，Markdown 解析器可以保持兼容回退，但事件投影应成为 status、quota、评审包、todo CLI 读取与 dashboard 导出的首选来源。

## 规范事件流

每个 goal 有一个有序事件流。每个事件必须包含：

- `schema_version`：事件 schema 版本，从 `loopx_state_event_v0` 开始；
- `event_id`：用于幂等追加与审计的稳定唯一 id；
- `goal_id`：所属 goal id；
- `event_type`：允许的生命周期事件类型之一；
- `recorded_at`：UTC 或带偏移 ISO-8601 的生产者时间戳；
- `append_sequence`：由本地 event store 分配的单调序列；
- `producer`：紧凑来源，如 `loopx.todo`、`loopx.refresh_state` 或 `agent.codex-product-capability`；
- `privacy`：`public_safe`、`local_private` 或 `private_pointer`；
- `projection_version`：写者期望的投影契约版本；
- `refs`：todo、gate、run、quota、PR、evidence 或父事件的紧凑 id；
- `payload`：事件特定的紧凑数据。

`append_sequence` 是最后的同优先级决胜者。若 planner 创建多个 P0 todo，planner 发出 `planner_order`，存储通过 append sequence 保留该顺序。UI 与 prompt 投影先按 priority 排序，有 `planner_order` 时再按它，然后按 `append_sequence`。

## 事件类型

首批受支持的 todo/历史事件类型：

| 事件类型 | 用途 |
| --- | --- |
| `todo_added` | 添加新 todo，带角色、优先级、标题、元数据与 planner 顺序。 |
| `todo_claimed` | 记录或续期所有权、lease 或 `claimed_by`。 |
| `todo_updated` | 更新不重写事件历史的紧凑元数据。 |
| `todo_blocked` | 用公开安全 blocker 原因与可选 gate 引用把 todo 标记为阻塞。 |
| `todo_deferred` | 用恢复条件把 todo 标记为推迟。 |
| `todo_completed` | 用验证/证据引用与完成理由关闭 todo。 |
| `gate_added` | 添加用户、owner、操作员或 controller gate。 |
| `gate_resolved` | 记录特定 gate 的 approve、reject 或 defer。 |
| `run_recorded` | 附加紧凑 run 历史状态、分类与投递结局。 |
| `refresh_recorded` | 记录仅状态或进度刷新摘要。 |
| `quota_spent` | 记录自动计算支出的记账。 |
| `evidence_attached` | 把紧凑公开安全证据引用附加到 todo、gate 或 run。 |
| `projection_rendered` | 记录生成的 Markdown/status/dashboard 投影校验和。 |
| `snapshot_compacted` | 声明派生的快照检查点，而不替换底层事件血统。 |

禁止的事件风格：

- 任何事件不得修改或删除先前事件；
- 任何事件不得在公开安全流中内嵌原始聊天 transcript、原始日志、凭据或私有源正文；
- 任何投影不得通过接受缺少匹配规范事件的状态而成为写 API。

## 排序与幂等

重放顺序为：

1. `append_sequence`；
2. `recorded_at`；
3. `event_id` 作为确定性最终决胜者。

追加对 `event_id` 幂等：用相同规范化正文重追加同一事件 id 是 no-op；用不同正文重追加是冲突。消费者应忽略重复的相同事件，并在冲突重复上失效关闭。

Todo id、gate id 与 evidence id 是稳定引用。事件可以通过 `refs.parent_event_id` 指向父事件，但子事件不得改写父载荷。

## 投影规则

事件投影渲染：

- 按角色与优先级分组的当前活动 todos；
- 已完成 todo 摘要与归档候选；
- 用户与 controller gate 收件箱；
- run 历史与刷新时间线摘要；
- 配额花费摘要；
- 评审包证据引用；
- 兼容 Markdown 的 `ACTIVE_GOAL_STATE.md` 小节。

投影输出必须携带：

- `schema_version`；
- `goal_id`；
- `generated_at`；
- `source_event_count`；
- `last_event_id`；
- `last_append_sequence`；
- `projection_version`；
- `source_checksum` 或等价完整性标记。

投影在任何生命周期事件后都可能过期。写者应先追加事件，再渲染投影输出。读者应只在投影的 `last_append_sequence` 与 event store 头匹配时优先使用最新投影。

## 隐私边界

LoopX 应支持独立流或分区记录：

- `public_safe`：可提交或在公开文档中展示的紧凑状态；
- `local_private`：本地状态，如项目私有活动 Markdown、私有 todo 详情或仅本地证据笔记；
- `private_pointer`：指向私有物料的紧凑指针，而不把物料复制进公开状态。

当项目把 `ACTIVE_GOAL_STATE.md` 排除在 git 之外时，它可以携带私有详情。公开文档、fixture、dashboard 与 PR 包不得复制这些详情。公开投影应只包含紧凑标签、id、脱敏摘要、省略说明与验证引用。

被跟踪的输出在投影私有流信息之前需要显式脱敏或紧凑指针。项目级 LoopX config 可以设置默认值，如：

```json
{
  "state_privacy": {
    "active_state": "local_private",
    "public_projection": "public_safe",
    "allow_private_links_in_ignored_state": true,
    "require_redaction_for_tracked_outputs": true
  }
}
```

## 迁移与兼容

迁移应分阶段：

1. 定义本契约并 smoke 测试重放/隐私恒等式。
2. 为 todo/历史事件添加最小 event store 与投影 API。
3. 双写 `loopx todo`、`refresh-state`、配额花费与 gate 命令。
4. 通过 `event_store_migration_bridge_v0` 把事件投影与当前 Markdown 解析对比。
5. 在 status、quota、评审包、dashboard 与 slash-command 帮助中优先事件投影。
6. 把 Markdown 渲染保留为工作台与兼容导出。
7. 只在真实本地 goal 上重放与幂等检查干净后，退役 Markdown 作为规范。

迁移工具可以从既有 Markdown 回填事件，但每个回填事件应标记 `producer=loopx.backfill`，并包含足够来源引用以解释出处，而不把私有原始物料复制进公开流。

## 验收检查

一个有效实现或 fixture 必须证明：

- Markdown 保持工作台/投影，而非规范 todo/历史事实；
- `todo_added`、`todo_claimed`、`todo_updated`、`todo_blocked`、`todo_deferred` 与 `todo_completed` 重放成确定性 todo 投影；
- 相同优先级 todo 保留 planner 顺序与追加顺序；
- 重复相同 `event_id` 追加幂等；
- 重复冲突 `event_id` 追加失效关闭；
- 先前事件永不被修改或删除；
- 投影暴露 `last_event_id`、`last_append_sequence` 与 `projection_version`；
- 公开投影不包含本地绝对路径、凭据、原始 transcript、原始日志或私有源正文；
- 被忽略/私有活动状态可引用私有链接，而被跟踪输出需要显式脱敏或紧凑指针。
