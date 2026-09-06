# decentralized_auto_research_state_v0

`decentralized_auto_research_state_v0` 是 LoopX 在不引入单一 leader agent 的情况下运行自主研究的协议。它借用 Arbor 公开设计中有用的部分，尤其是持久化假设状态、worktree 隔离、dev/held-out 评估与可重放证据，但把它们映射到 LoopX 的共享控制面：todos、claims、quota、run 历史、rollout 事件、gates 与只读投影。

目标是让多个 agent 并行探索研究假设，同时保留出处、所有权与提升规则。没有 agent 拥有完整研究树。事实来源是追加式状态图；每个 agent 通过 `quota should-run --agent-id ...` 看到一个作用域前沿。

## 需保留的 Arbor 信号

评审过的 Arbor 主要公开界面：

- `README.md`：Arbor 把工作描述为通过假设树细化的自主研究，带 Coordinator、Executors、worktrees、held-out 验证、报告、重放与 benchmark zoo。
- `docs/how-it-works.md`：六步循环为观察、构思、选择、实验、评估、反哺，然后合并或修剪。
- `src/coordinator/idea_tree.py`：每个节点记录假设、状态、洞察、结果、分数切分、测试分数、分支引用、grounding、相关工作审计、eval 状态、停止原因与尝试次数。
- `src/coordinator/tools/executor_run.py`：执行器结局区分已评分成功与 `needs_retry`（超时、max-turn、eval-crash 或不可解析报告），同时保留分支/报告/diff 供继续。
- `docs/search.md`：有 grounding 的构思与新颖性审计是独立 lane；为启发想法而抓取的文本不复用于认证新颖性。
- `arbor-zoo/algotune_knn`：展示 benchmark 打包了可编辑求解器、受保护 harness、dev/test 切分、出处与一行 `score:`。

LoopX 应保留这些产品教训，而非 Arbor 的集中式拓扑。

## 非目标

- 不添加拥有全部规划的 LoopX 全局「研究总监」agent。
- 不用第二个研究数据库替换 todos、run 历史或 rollout 事件。
- 不让展示 dashboard 修改源状态。
- 不把咨询性 grounded 搜索结果当作新颖性证明。
- 不无 held-out 证据或边界要求显式 gate 就合并或发布研究结果。

## 来源协议

源状态只能通过 LoopX 生命周期命令、项目自有状态文件或未来窄内核 API 写入。

伴随的 [auto_research_lane_contract_v1](auto-research-lane-contract-v1.md) 定义哪些去中心化 agent lane 可以创建、执行、评估、提升、退役或叙述这些记录。伴随的 [auto_research_role_state_machine_v0](auto-research-role-state-machine-v0.md) 定义常开数字员工角色映射与状态转换。本文件定义记录形状与投影；伴随契约在不引入 leader agent 的情况下定义能力所有权与转换证据。

| 源状态 | 既有或提议锚点 | 用途 |
| --- | --- | --- |
| `research_contract_v0` | 提议包、registry goal 元数据 | 公开安全目标、可编辑 scope、受保护 scope、指标方向、dev/held-out 命令、预算与停止条件。 |
| `todo_item_v0` | `loopx todo` | 正式可执行工作、用户 gate、blocker 或 monitor。研究工作保持有 todo 背书。 |
| `research_hypothesis_v0` | 提议 rollout 事件与可选领域包 | 链接到 todo、父假设、agent lane、机制家族与当前状态的假设节点。 |
| `research_evidence_event_v0` | 提议 `loopx_rollout_event_v0` 特化 | 尝试的追加式证据：分数、切分、命令标签、分支、工件引用、eval 状态与边界事实。 |
| `auto_research_terminal_decision_v0` | `validation` rollout 事件特化 | 绑定到一个证据图修订的显式 `promoted` 或 `retired` 结果；提升与退役候选不暗示该记录。 |
| `auto_research_peer_review_v0` | `validation` rollout 事件特化 | 绑定到一个终态决策与证据图修订的 approve、reject 或 needs-more-evidence 评审回执。 |
| `dataset_window_contract_v0` | `loopx/ml_experiment.py` | Train/dev/held-out 窗口或切分契约，包括缺失窗口策略。 |
| `agent_lane_next_action_v0` | `quota should-run --agent-id ...` | 当前 agent 的所选前沿项；它不取代全局状态图。 |
| `operator_gate` | `loopx operator-gate`、评审包 | 提升、合并、私有物料或发布决策。 |
| `human_reward` | `loopx reward` | 绑定 run 的 owner 判定，而非通用写权限。 |

### `research_contract_v0`

```json
{
  "schema_version": "research_contract_v0",
  "goal_id": "loopx-meta",
  "research_objective": "optimize a benchmark task under a protected evaluator",
  "editable_scope": ["solution.py"],
  "protected_scope": ["eval.py", "task.py", "data/**"],
  "metric": {"name": "speedup", "direction": "maximize"},
  "dev_eval": {"label": "eval_dev", "command_label": "bash eval.sh dev"},
  "holdout_eval": {"label": "eval_test", "command_label": "bash eval.sh test"},
  "promotion_policy": "requires_holdout_improvement_and_clean_boundary",
  "budget": {"max_attempts": 8, "max_parallel_lanes": 3}
}
```

### `research_hypothesis_v0`

```json
{
  "schema_version": "research_hypothesis_v0",
  "goal_id": "loopx-meta",
  "hypothesis_id": "hyp_0004",
  "parent_hypothesis_id": "hyp_0002",
  "todo_id": "todo_123",
  "lane_id": "agent:research-executor",
  "claimed_by": "research-executor",
  "mechanism_family": "vectorized_distance_kernel",
  "hypothesis": "Batch query points through a shared index to reduce per-query overhead.",
  "status": "active",
  "frontier_rank": 2,
  "source_refs": ["research_contract:knn_speedup"],
  "grounding_refs": [],
  "novelty_audit_ref": null
}
```

状态词表：

| 状态 | 含义 |
| --- | --- |
| `proposed` | 已草拟但尚未进入可执行工作。 |
| `active` | 可运行前沿项，通常由开放 agent todo 背书。 |
| `running` | 已认领尝试进行中。 |
| `needs_retry` | 尝试未产出可信分数，但留下可恢复证据。 |
| `supported` | Dev 证据支持假设；尚未提升。 |
| `contradicted` | 证据显示回归或 guardrail 失败。 |
| `promoted` | Held-out 证据与提升策略接受它进入当前最佳工件。 |
| `retired` | 不再值得探索，但保留为负面证据。 |

### `research_evidence_event_v0`

```json
{
  "schema_version": "research_evidence_event_v0",
  "goal_id": "loopx-meta",
  "hypothesis_id": "hyp_0004",
  "todo_id": "todo_123",
  "agent_id": "research-executor",
  "attempt": 1,
  "split": "dev",
  "metric": {"name": "speedup", "value": 11.4, "direction": "maximize"},
  "baseline_metric": 8.7,
  "primary_metric_status": "improved",
  "eval_status": "scored",
  "code_ref": "codex/research-hyp-0004",
  "artifact_refs": ["experiment:hyp_0004/report", "diff:hyp_0004"],
  "protected_scope_clean": true,
  "private_artifacts_recorded": false,
  "raw_logs_recorded": false
}
```

`needs_retry` 是一等证据，而非通用失败：

```json
{
  "schema_version": "research_evidence_event_v0",
  "hypothesis_id": "hyp_0005",
  "eval_status": "failed_to_run",
  "stop_reason": "max_turns",
  "attempt": 1,
  "code_ref": "codex/research-hyp-0005",
  "resume_policy": "resume_from_code_ref_or_retire",
  "primary_metric_status": "inconclusive"
}
```

## 投影协议

投影状态只读。它可为显示排列前沿，但必须携带来源引用并可从源状态重算。

| 投影 | 用途 |
| --- | --- |
| `decentralized_research_frontier_v0` | 在 quota、claim、capability 与边界检查后，每 agent 的可运行或阻塞假设队列。 |
| `research_evidence_graph_v0` | 连接假设、todos、尝试、分支、指标、gates 与提升决策的只读图。 |
| `auto_research_terminal_result_projection_v0` | 把终态决策与评审状态确定性投影进既有 Explore 节点、发现与血统边。 |

### `decentralized_research_frontier_v0`

```json
{
  "schema_version": "decentralized_research_frontier_v0",
  "goal_id": "loopx-meta",
  "agent_id": "research-executor",
  "selected": {
    "hypothesis_id": "hyp_0004",
    "todo_id": "todo_123",
    "reason": "current-agent claim and dev evidence gap",
    "allowed_action": "run_dev_attempt"
  },
  "blocked": [
    {
      "hypothesis_id": "hyp_0002",
      "blocked_by": "claimed_by:research-curator",
      "visible_as_context": true
    }
  ],
  "promotion_candidates": [
    {
      "hypothesis_id": "hyp_0004",
      "requires": ["holdout_eval", "boundary_scan"]
    }
  ]
}
```

该投影有意取代集中式 Coordinator 决策。内核只选择当前 agent 可以尝试的内容；agent 仍在其允许边界内做语义实现。

## 去中心化循环

Arbor 的循环映射为 LoopX 的分布式控制环：

| Arbor 概念 | LoopX 去中心化等价物 |
| --- | --- |
| 观察 | Agent 读取 `quota should-run`、active state、所选前沿、证据图与相关源文档。 |
| 构思 | 任何授权 lane 可以把 `research_hypothesis_v0` 提议为有 todo 背书的候选。 |
| 选择 | `quota should-run --agent-id` 按 claim、gate、capability 与边界过滤。 |
| 分发 | 所选 agent 在自己的 worktree 中工作并写入证据。 |
| 反哺 | 确定性投影把 supported/contradicted 教训总结进证据图；没有单一 agent 改写全局真相。 |
| 决策 | 提升策略加操作员 gate 决定合并、退役、重试或继续。 |

## 搜索 Lane

LoopX 应采纳 Arbor 的搜索 lane 分离：

| Lane | 何时 | 权限 | 写入 |
| --- | --- | --- | --- |
| `grounded_ideation` | 假设提议之前或期间 | 对候选假设的咨询输入。 | 假设上的 `grounding_refs`。 |
| `novelty_audit` | 假设有真实证据之后 | 咨询性贡献/重叠检查。 | `novelty_audit_ref` 与证据笔记。 |

两个 lane 不得共享抓取文本作为证明。若来源塑形了想法，它可以被引用为 grounding，但后续新颖性审计必须运行独立来源遍历才能声明新颖性。

## 提升策略

研究假设只有在以下条件满足时才能提升：

1. 可编辑/受保护 scope 边界干净；
2. dev 证据已评分且公开安全；
3. held-out 证据满足指标方向与边距；
4. 必需用户/controller gate 已解决；
5. 提升工件有分支或提交引用；
6. 证据图为接近备选记录负面证据。

提升是状态转换，不是聊天结论。它应写入一次 todo 完成、证据事件与可选提升 gate/reward overlay。

## 与既有 LoopX 集成

已可用：

- `todo_item_v0` 有 claims、task classes、action kinds、blockers、user gates 与 resume 条件。
- `agent_lane_next_action_v0` 按已注册 agent 作用域工作。
- `loopx/ml_experiment.py` 已有 `hypothesis_ledger_v0`、`dataset_window_contract_v0` 与咨询结果包。
- `long_horizon_agent_state_protocol_v0` 已定义来源/投影分离与并发 lane 视图。
- `loopx auto-research frontier --fixture <public.json> --agent-id <agent>` 现在渲染 fixture 支撑的 `decentralized_research_frontier_v0` 与 `research_evidence_graph_v0`，而不启动实验或依赖 leader agent。
- `loopx auto-research frontier --goal-id <goal> --agent-id <agent>` 现在从 LoopX status 投影为当前 agent 渲染实时 todo/quota 支撑前沿。
- Auto-research worker 路径现在为 smoke/demo 证据使用内置轻量指标内核，而非交付的领域特定 starter pack。
- `loopx auto-research evidence --contract <research_contract.json> --eval-result <eval.json>...` 现在构建包含公开安全 `research_hypothesis_v0` 与切分感知 `research_evidence_event_v0` 记录的 `auto_research_evidence_packet_v0`。它保留 `needs_retry`、负面证据、`protected_scope_clean` 与分支/工件引用，而不记录原始日志或私有工件。
- `loopx auto-research append-evidence --packet <packet.json>` 把该包作为一条 `research_hypothesis` 事件加每条切分一条 `research_evidence` 事件追加进既有 `loopx_rollout_event_v0` 日志。重跑同一包会跳过既有事件 id，因此 heartbeat 重试不会重复证据。
- `loopx auto-research frontier --goal-id <goal> --agent-id <agent>` 把 `research_hypothesis` 与 `research_evidence` rollout 事件读回 `research_evidence_graph_v0`，并为实时前沿派生提升/退役候选。
- `loopx auto-research decide` 对照当前证据验证候选，然后记录证据修订绑定的终态决策。
- `loopx auto-research review` 记录评审回执；带 `--require-independent` 时，评审者必须是既不同于生产者又不同于决策 agent 的已注册对等方。
- `loopx auto-research results` 按假设 id 返回精确当前与历史终态。`project-results` 写入确定性既有 Explore 节点/发现事件，重复执行幂等。

下一步需要：

- 让 pane 级 worker 直接从其 Codex TUI 消费前沿；
- 在独立产品界面有意消费紧凑证据图之前，把产品叙述与公开发布主张排除在内核之外。

## 验收检查

一个实现在以下条件下可接受：

- 不要求单一 agent 拥有或修改完整假设图；
- 每个可执行假设链接到 todo 与 claim；
- 每 agent 前沿选择从 quota/status 推导，而非聊天记忆；
- `needs_retry` 保留可恢复证据，而非坍缩为 `done`；
- grounded 构思与新颖性审计分离；
- held-out 提升显式；
- 终态决策与提升、退役候选保持分离；
- 同 agent 评审保持可见，但不能确认或驳回发现；
- 过期证据修订与冲突终态决策失效关闭；
- 面向用户的研究摘要从紧凑前沿与证据图引用推导，而非定制内核包；
- 公开投影不包含原始日志、私有路径、凭据或原始私有文档；
- 公开叙述可从公开安全证据引用渲染。
