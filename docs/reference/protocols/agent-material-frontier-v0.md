# agent_material_frontier_v0

`agent_material_frontier_v0` 是 goal 自有物料权限之上的、agent 作用域的只读视图。它回答 agent 需要哪些已注册物料引用、它观察到哪个修订，以及每个引用是 current、stale、missing、unread 还是 inaccessible。

该前沿不是第二个物料注册表。物料 id、修订、主题、新鲜度、边界与关卡仍归 goal 的规范 `authority_registry.project_materials` 与 `topic_authority` 映射所有。

## 输入

纯构建器接受六个有界输入组：

- 规范 goal 权限：物料元数据与主题到物料的映射；
- agent profile 需求：显式物料引用或默认物料主题；
- todo 需求：当前工作的显式物料引用；
- 一个 agent vision 需求集；
- successor 继承的 handoff 物料引用；
- 所选 agent 与 todo 的 `material_usage_receipt_v0` 行。

需求优先级为：

```text
显式 todo 或 handoff > vision > profile 主题默认值
```

同一物料的多个绑定保留在 `bound_by` 中。最高优先级绑定选择关系与目的，而当前修订与边界总是从 goal 权限重新读取。

## 形状

```json
{
  "schema_version": "agent_material_frontier_v0",
  "goal_id": "example-goal",
  "agent_id": "agent-reviewer",
  "generated_at": "2026-07-19T00:00:00Z",
  "summary": {
    "required_count": 2,
    "current_count": 1,
    "stale_count": 0,
    "missing_count": 0,
    "inaccessible_count": 0,
    "required_unread_count": 1
  },
  "items": [],
  "required_reads": [],
  "truth_contract": {
    "authority_is_goal_owned": true,
    "projection_is_read_only": true,
    "introduces_task_runtime": false,
    "grants_cross_agent_authority": false,
    "evidence_log_implies_material_read": false,
    "raw_source_body_recorded": false
  }
}
```

每个 item 可包含：

- `material_id` 与权威派生的 `topics`；
- `relation`：`required`、`producer`、`reviewer`、`maintainer` 或 `watcher`；
- `bound_by`：紧凑的 `profile`、`todo`、`vision` 或 `handoff` 引用；
- `purpose` 与 `todo_id`；
- `required_revision` 与 `observed_revision`；
- `state`；
- `boundary` 与 `gate_status`；
- 一个紧凑 `receipt_ref` 与 `last_verified_at`。

投影从不复制源 URL、文档正文、评论、凭据、本地绝对路径或另一个 agent 的展开事件流。

## 状态规则

状态按此顺序推导：

1. 物料 id 不出现在规范权限中：`missing`。
2. 其边界或关卡对当前执行环境不可用：`inaccessible`。
3. 当前 agent 与 todo 没有匹配回执：`required_unread`。
4. 权限新鲜度过期或观察到修订与权限修订不同：`stale`。
5. 观察到修订等于当前权限修订：`current`。

紧凑权限摘要不足以推导前沿。构建器在规范 `project_materials` 缺失时失效关闭，因此投影计数永远不会被误认为空权限注册表。省略的边界也被视为 inaccessible，而非默认为公开。

证据与回执有不同的语义。run 历史或证据日志行可以证明 agent 更改或验证了工件，但它不证明 agent 消费了某个物料修订。只有匹配的 `material_usage_receipt_v0` 才能把物料从 unread 或 stale 移到 current。缺少回执 schema、agent、goal、todo、稳定 id、结局与时间戳的回执式证据失效关闭。

## Handoff 语义

successor 可以通过 handoff 接收一个有界物料引用集，然后从 goal 权限加自己的 profile、todo 与 vision 需求重建完整前沿。前任的回执不会让 successor 变 current，handoff 也不转移来源权限或权限所有权。

这支持持久化交接，而无需引入分发器或 agent 自有物料缓存。

有界 handoff 投影发出：

- `schema_version=agent_material_handoff_projection_v0`；
- 六个前沿摘要计数；
- `material_ref_count` 与 `material_refs_truncated`；
- 至多四个只包含 `material_id`、`relation` 与可选公开安全 `purpose` 的引用。

它刻意省略观察与必需修订、回执引用、边界、关卡状态、权限元数据与可用权限。有界引用是上下文，不是完整物料清单。successor 用自己的 profile、todo、vision 与 handoff 需求，对当前 goal 权限重建完整前沿。

当类型化 `handoff_note_v0` 与完整前沿同时存在时，agent 读模型层可以通过附加 `material_frontier_summary` 与有界引用发出 `handoff_note_v1`。无前沿行的遗留 todo handoff 生产者保持不变。

## 当前投递边界

实现包括纯前沿构建器、有界物料 handoff 投影器与可选 agent-management 冷路径消费者。消费者从 `status.agent_material_frontiers` 读取预构建包；它不自行加载规范权限或物料正文。消费者只在其当前执行信封声明 goal 作用域 `material_lifecycle` capability 时发出物料字段。缺失 capability 会静默地把物料前沿排除在 agent 投影之外；它不变成用户关卡。

实现有意不增加：

- profile/todo 物料需求编写命令；
- 物料正文缓存；
- 回执追加命令；
- 自动授权或关卡创建；
- 跨 agent 分发器；
- MA 或运行时特定字段。

## 验收检查

一个持久化 fixture 应证明：

- profile 主题与显式需求确定性合并；
- todo 或 handoff 需求覆盖 profile watcher 关系；
- unread、current、stale、missing 与 inaccessible 状态彼此不同；
- 权限修订变更使旧回执过期；
- 另一个 agent 的回执永远不能满足当前 agent；
- successor 获得相同物料引用而不继承权限；
- 紧凑权限摘要失效关闭；
- 发出的包不包含原始源物料或私有路径。
