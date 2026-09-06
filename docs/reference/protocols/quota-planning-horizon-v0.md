# quota_planning_horizon_v0

`quota_planning_horizon_v0` 是有界只读上下文，让 agent 可以在不内联 LoopX 完整 Todo 存储或任务图的情况下，超越一个局部选择的 Todo 进行推理。只有当当前所选工作具有类型化血统、等待/阻塞、计划观察或 goal 验收上下文时，它才出现在默认 `quota should-run` 路径上。扁平可运行备选仅保留在 `action_portfolio` 中，避免重复热路径视图。

它解决的问题比调度更窄。一个所选回归 gate 可以在本地可运行，而战略路径还包含事实来源、策略决策、运行时准入与逐目标验证。只显示 gate 或只显示两个备选动作，可能使模型优化可见叶子。规划 horizon 使该有界链可见。它不静默替换所选 Todo。

## 所有权

- 既有 Todo、claim、capability、goal-frontier 与 event-ledger 契约保持权威。
- Python 从 Todo 域状态行中选择一个规范规划来源：`items`、`deferred_items`、`blocker_items` 与 `monitor_open_items`。它不从呈现 lane 重建来源，也不从散文推断层级。
- TypeScript 把该来源一次性规范化为 `todo_planning_inventory_v0`，带正交的规划与 claim 状态、类型化关系、动作资格与来源完整性元数据。`action_portfolio` 与 `planning_horizon` 是该清单之上的两个独立 lens。
- `--include-detail agent-todos` 在有界 Todo 摘要旁暴露更大的仅规划清单 lens。`task_graph_projection_v0` 复用同一规范选择器，以终态前置项/证据行扩展它，并在增加 gate/证据数据时保持 agent 中立。
- Effect Program 把完成的观察传输进 TurnEnvelope。它不拥有 Todo 依赖、恢复或动作选择语义。
- `selected_todo` 与 `action_portfolio` 仍是仅有的动作选择权威。规划 horizon 项在 agent 执行既有显式选择/重新进入流程之前都是上下文。

## 形状

```json
{
  "schema_version": "quota_planning_horizon_v0",
  "mode": "read_only",
  "goal_id": "loopx-meta",
  "agent_id": "codex-main-control",
  "selected_todo_id": "todo_regression_gate",
  "selection_contract": {
    "selected_todo_authority": "$.selected_todo",
    "action_choice_authority": "$.action_portfolio",
    "horizon_changes_selection": false,
    "explicit_selection_required_for_other_work": true
  },
  "work_items": [],
  "relations": [],
  "acceptance_gaps": [],
  "attention_todo_ids": [],
  "completeness": {
    "schema_version": "quota_planning_horizon_completeness_v0",
    "source_context_todo_count": 8,
    "candidate_input_count": 7,
    "source_unrepresented_todo_count": 1,
    "omitted_candidate_todo_count": 2,
    "omitted_relation_count": 1,
    "omitted_acceptance_gap_count": 1,
    "compact_field_truncation_count": 0,
    "complete": false
  },
  "detail_refs": {
    "selected_todo": {
      "schema_version": "todo_detail_ref_v0",
      "goal_id": "loopx-meta",
      "role": "agent",
      "todo_id": "todo_regression_gate",
      "projection": "todo_detail_cold_path_v0"
    },
    "agent_todos": "quota should-run --goal-id loopx-meta --agent-id codex-main-control --include-detail agent-todos",
    "full_todo_list": "todo list --goal-id loopx-meta --role agent --status open --agent-id codex-main-control",
    "task_graph": "status --include-task-graph"
  }
}
```

## 界限与排序

共享清单从每个适配器 lane 至多接受 128 行，至多保留 64 个规范化 Todo 项，并把每次溢出报告为不完整，而不是拒绝一个原本只读的配额决策。horizon 随后至多投影：

- 5 个 Todo 上下文项；
- 8 条类型化关系；
- 2 个 goal 验收缺口；
- 3 个 `attention_todo_ids`。

所选 Todo 居首。所选 Todo 的类型化关联项其次，通过关系图向外排序。不相关的等待、阻塞或计划上下文随后，之后是更高优先级与其他可运行备选；动作组合已经在拥有扁平备选选择。该排序帮助 agent 重建战略链，同时保持所选 Todo 身份稳定。

`planning_state` 是 `selected`、`runnable`、`waiting`、`blocked`、`scheduled` 或 `context` 之一。它独立于 `claim_state`，后者是 `current_agent`、`unclaimed` 或 `other_agent` 之一。特别是，`planning_state=runnable` 加 `claim_state=unclaimed` 意为该工作只能在既有 claim 流程之后前进；horizon 为所选或可运行的未认领工作携带 `claim_required_before_work=true`。`context_reasons` 解释为何保留一个非所选项，例如 `related_to_selected`、`higher_priority_than_selected` 或 `runnable_alternative`。

每个省略的来源、候选、关系、缺口或压缩文本字段都被计数。只有全部这些计数为零时 `complete=true` 才有效。当答案依赖被省略上下文时，消费者必须跟随 `detail_refs`；它不得把五个可见项当作整个 Goal。`source_context_todo_count` 计入当前开放加已推迟 Todos；完成历史有意排除在本规划视图之外。

详情路径刻意有不同的 scope：

- `planning_horizon` 是默认热路径摘要；
- `quota should-run ... --include-detail agent-todos` 增加 `agent_todo_planning_inventory.schema_version=todo_planning_inventory_detail_v0`。它为更大的有界清单暴露规划/claim 状态、资格标志、关系与完整性，同时 `item_detail_ref=$.agent_todo_summary` 避免重复 Todo 文本、scope 与 capability；
- `todo list ... --role agent --status open` 读取完整当前 Todo 来源，而不是假装有界配额包是穷尽的；
- `status --include-task-graph` 增加 agent 中立的图、gate 与证据上下文。

当同一观察嵌套在 `loopx_turn_envelope_v0` 中时，传输可以把重复的 `detail_refs` 对象替换为 `detail_refs_ref="$.detail_ref"`。Turn 信封的顶层冷路径随后拥有那些读取。这只是传输压缩：它不改变 TypeScript reducer 输出、完整性记账或动作权威。

## 关系语义

v0 关系种类：

- `successor`：从 `successor_todo_ids` 派生，`enforcement=lineage_only`；
- `unblocks`：从 `unblocks_todo_id` 派生，带类型化生命周期语义；
- `resumes_when`：从 `resume_when` 派生，带类型化条件语义；
- `superseded_by`：仅持久化血统；
- `routes_via`：对既有 route id/键的只读引用。

血统与强制之间的区分是有意的。successor 链接不会仅仅因为规划视图能画出链就升级为硬依赖。v0 不从「after」「requires」或「blocked by」之类的措辞推断 `depends_on`。未来硬依赖需要单独的类型化 Todo 契约与迁移策略。

## Effect Program 边界

Effect Program 增加一个可空 `planning_horizon` 观察，使每个消费 TurnEnvelope 的 host 都能收到同一领域自有投影。这是传输扩展，不是通用规划 reducer。Todo 恢复仍是 Todo 局部 reducer/ACK 语义，配额选择保持在既有类型化边界内。

horizon 存在时，TurnEnvelope 动作签名覆盖推进到 `turn_envelope_action_dimensions_v3`。CLI 差异资格只识别配对迁移 `none -> quota_planning_horizon_v0` 与 v0/v1/v2 动作覆盖到 v3。该转换获得一次有界 JSON 增长配额。v0 进入 base 后，普通热路径增长限制重新适用。

## 验收检查

一个符合的实现必须证明：

- TypeScript reducer 拥有验证、排序、去重与界限；
- Python 适配器消费规范 Todo 状态行，且不创建第二存储或呈现 lane 并集；
- 组合、horizon 与 agent-Todo 详情消费同一类型化清单；
- 任务图消费同一规范 Todo 选择器加终态证据行，而不获得 agent 作用域选择或 claim 权限；
- horizon 从不改变 `selected_todo` 或动作组合资格；
- 可运行的未认领工作保留 `claim_required_before_work=true`；
- 类型化 successor/resume/route 关系在默认紧凑路径上存续；
- 仅散文的依赖主张不创建关系；
- 超过遗留解码器限制的源大小降级为显式不完整，而不是使配额失败；
- 截断与来源不完整在清单与 horizon 上都显式；
- 所选 Todo 详情与可选完整任务图仍可达；
- 完整配额与 TurnEnvelope 动作签名覆盖同一 horizon；
- 确定性变更测试在实时模型花费前拒绝缺失或生产者漂移的 horizon；
- 实时模型证据只作为有界回执保留，绝不保留原始 prompt、响应、凭据或本地路径。
