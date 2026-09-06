# 前端 Kernel 到心智模型映射

> [English](frontend-kernel-mental-model-map.md)

LoopX 需要一个富内核，因为长程 agent 工作有真实失败模式：漂移的 goal、隐藏 gate、重复工作、过期 evidence、丢失 handoff 与失控的算力。前端不应把那个内核当作用户的日常词表暴露。

产品规则是：

> 为正确性保留内核的显式性，但把它压缩成更小的日常操作心智模型。

## 五个用户概念

默认管理 surface 只教五个概念。

| 用户概念 | 用户问题 | 主要 UI 职责 |
| --- | --- | --- |
| Goal | 我们现在试图达成什么？ | 显示当前目标、边界与选中锚点。 |
| 下一步 | Agent 接下来会做什么？ | 显示一个有界动作，并在有用时显示几个邻近候选。 |
| Blocker / 权限 | 哪里需要人类判断、哪里被禁止？ | 显示具体决策、gates 与安全边界。 |
| Evidence | 我凭什么相信进展发生了？ | 显示紧凑验证、artifacts 与置信度。 |
| 继续状态 | 我能把它交回给 agent 吗？ | 显示 run/wait/observe/repair/handoff 就绪度。 |

Ops surface 中每个顶级卡片、导航标签与空状态都应映射到其中一个概念。

## Kernel 概念

Kernel 可以保留其为正确性所需的概念。

| Kernel 概念 | 为什么存在 | 默认暴露 |
| --- | --- | --- |
| `goal_state` | 关于目标、边界与当前信念的持久 truth。 | 压缩为 **Goal**。 |
| `user_gate` | Agent 无法跨越的人类决策边界。 | 仅当需要动作时可见，位于 **Blocker / 权限** 下。 |
| `todo` | 可执行工作单元与 owner/用户任务。 | 可见为 **下一步** 加一个小队列。 |
| `claim` | 多 agent 冲突避免。 | 默认隐藏；显示为泳道 owner 或诊断详情。 |
| `scope` | 特定 agent 能做什么、不能做什么。 | 在 agent 泳道或 blocker 详情下总结。 |
| `evidence` | 状态转变可信的证明。 | 可见为紧凑 **Evidence**。 |
| `run_history` | 审计日志与重放/调试基底。 | 折叠在 evidence 或诊断背后。 |
| `quota` | 自动 Turn 现在是否可以 spend 算力。 | 渲染为 **继续状态**，而不是原始计数。 |
| `handoff` | 给下一个 loop 或 agent 的上下文包。 | 仅在复制、恢复或调试时渲染。 |

这些对象不是冗余的。它们分开 truth、工作、authority、所有权、证明、算力与移交。UI 的职责是让用户除非在调试，否则不必支付这份复杂度成本。

## 投影契约

读模型应提供显式压缩层，而不是让每个组件发明标签。

```yaml
mental_model_projection_v0:
  goal:
    title: "Current objective"
    boundary_summary: "What is in and out of scope"
    anchor: "Optional selected proof path"
  next_step:
    primary_action: "One bounded action"
    nearby_candidates: ["Optional small queue"]
    selected_reason: "Why this action is first"
  blocker_permission:
    status: clear | needs_user | forbidden | needs_repair
    concrete_question: "Only when needs_user"
    boundary_reason: "Only when forbidden or needs_repair"
  evidence:
    latest_summary: "Compact validation or artifact pointer"
    confidence: strong | partial | missing
    drilldown_ref: "Run or artifact id"
  continue_state:
    status: can_run | waiting | observe_only | needs_repair | handoff_ready
    reason: "Short operator-readable reason"
    next_safe_transition: "Optional CLI/control-plane transition"
  diagnostics:
    goal_state_ref: "debug only"
    todo_ids: ["debug/search"]
    claims: ["debug/multi-agent"]
    quota_ref: "debug only"
    run_history_refs: ["debug/audit"]
```

同一个 kernel 源仍可驱动搜索、调试与审计视图。默认 surface 应优先读取压缩字段。

## 交互规则

- 默认导航与首屏标题应使用五个用户概念，而不是 kernel 名。
- 搜索仍可接受 todo id、run id、agent id 与 kernel 术语，因为调试需要精确句柄。
- `claim`、`quota`、`scope` 与 `handoff` 应作为详情片、tooltip 或诊断行出现，除非它们需要用户动作。
- User gate 不是泛化的"owner gate"；它必须显示具体决策与批准、拒绝或推迟的后果。
- Evidence 默认紧凑并链接到审计详情。原始日志、私有轨迹、本地路径与敏感资料不得出现在公开夹具中。
- 继续状态不应仅仅因为 quota 允许算力就说"run"。它还必须遵守 gates、scope、写边界与 evidence 要求。
- Review-feed 卡片应产出用户语言反馈，再映射回类型化事件，如 `review_event_v0`、`feedback_signal_v0` 或 `todo_update`。

## Dashboard 布局影响

对 ops surface，一个简单的首屏是：

1. **Goal**：目标、活跃锚点与边界摘要。
2. **下一步**：选中动作、小 todo 队列与选中原因。
3. **需要你的判断**：具体 user gates 与被禁止动作。
4. **Evidence**：最后验证结果、置信度与 artifact 指针。
5. **能继续吗？**：run/wait/observe/repair/handoff 状态。

诊断可以放在可展开面板背后：

- todo explorer；
- agent 泳道详情；
- claims 与 scope；
- quota 与 run 历史；
- handoff packet。

这让 LoopX 对长程工作保持诚实，同时让产品感觉像管理 surface，而不是 schema 浏览器。

## 验收标准

前端映射在以下情况下可接受：

- 新用户能用上述五个概念解释首屏；
- 每个可见 kernel 标签都有可见的理由，如搜索、调试或活跃用户决策；
- 所有诊断展开仍为审计与恢复保留精确 id；
- 同一投影可以表示单个项目、所有项目与多 agent 泳道；
- review-feed 动作使用面向用户标签，但写入类型化 LoopX 事件。
