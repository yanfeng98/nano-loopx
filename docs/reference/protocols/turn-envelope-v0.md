# TurnEnvelope v0

`loopx_turn_envelope_v0` 是已计算的 `quota should-run` 决策之上附加的、有界的读模型。它不给 agent 重放完整配额载荷中的每个诊断 lane，而是给出下一动作及其安全契约。

显式预览它：

```bash
loopx quota should-run --goal-id <goal-id> --agent-id <agent-id> --turn-envelope
```

默认 `quota should-run` 输出保持不变。v0 信封保留：

- 所选 todo、claim 与有效动作；
- 当 agent 必须在投递前从多个已准入动作中选择时的有界动作组合；
- 当所选工作有战略 Todo、关系或 goal 验收上下文时的有界只读规划 horizon；
- 具体用户动作与 gate 原因；
- 必需读取；
- 写 scope、批准、guard、workspace/capability 关卡与停止规则；
- 投递、修复、安全绕行与阻塞动作策略；
- 验证/writeback 与配额花费策略；
- 当前 scheduler 动作与节奏确认命令。

信封还携带一个有界 `contract_capsule`，用于交互模式、工作 lane 与执行义务、successor/replan 职责、自动化活性、vision/handoff 状态与可行动警告引用。规范 `action_signature` 独立地从完整决策与从信封构建；哈希匹配证明该投影下覆盖的动作维度一致。它们不证明每个可能的配额状态都有测试覆盖。

动作签名覆盖独立于信封 schema 版本化。`turn_envelope_action_dimensions_v0` 覆盖原始动作投影；`turn_envelope_action_dimensions_v1` 额外覆盖阻塞用户 gate 的 `response_plan`；`turn_envelope_action_dimensions_v2` 额外签署 `action.action_portfolio`；`turn_envelope_action_dimensions_v3` 额外签署 `action.planning_horizon`。Base/head 资格接受声明的覆盖迁移作为评审信号。有界的、仅限 JSON 的 v2 与 v3 迁移预算只适用于其命名的 schema 迁移；新版本成为基线后，普通增长限制恢复。无受支持覆盖迁移的摘要变化，或超过其单版本预算的投影，仍然失效关闭。

`quota_planning_horizon_v0` 即使在信封中携带时仍保持咨询性。其 `selection_contract` 指回 `selected_todo` 与 `action_portfolio`，且 `horizon_changes_selection=false`。Effect Program 传输该观察；TypeScript work-item reducer 拥有其排序与界限。配额投影保留 horizon 的类型化 `detail_refs`。TurnEnvelope 不第二次复制那些命令：它发出 `action.planning_horizon.detail_refs_ref="$.detail_ref"`，而既有顶层冷路径拥有完整决策、Todo 与状态读取。此传输压缩由同一动作签名覆盖，不改变 horizon 完整性或选择权限。参见 [quota_planning_horizon_v0](quota-planning-horizon-v0.md)。

对于 `quota_action_portfolio_v2`，信封携带推荐与有界、非穷尽的 `suggested_actions`，但两者都不是 settlement 身份或权限清单。当完整交互契约指明 `selection_required=true` 时，agent 必须在同一 Turn 中，带上任何当前权威、同 agent、能力就绪的 Todo 重跑 quota。完整决策的 `selection_command.command_args_template` 是渲染模板，不是权限清单。它与 `candidate_discovery_args` 共享一个有界 `route_prefix`；当有界建议不足时，发现路由暴露当前开放 agent 队列。请求的 Todo 保持 pending，直到第二个 guard 重跑当前 lane 仲裁与资格；只有资格通过的请求才会把无身份回执升级。新到期的硬 lane 使回执保持未绑定，而只有最终绑定回执的信封才是投递契约。

Portfolio v2 保留 v1 的选择策略、候选排序与 settlement 规则，并为每个建议动作增加可选 `continuation_hint`。默认配额生产者与 Turn controller 现在要求 v2。紧凑配额 CLI 视图使用独立版本化的 `quota_cli_action_portfolio_compaction_v1` 详情标记，并把候选 `text`、`priority`、`action_kind` 与 `continuation_hint` 与 v1 身份字段一同内联。TurnEnvelope 保持相同的 `loopx_turn_envelope_v0` 外壳 schema 与 v2 动作签名覆盖；只有其嵌套动作组合版本改变。严格接受 v1 的 host 必须在消费新默认前更新。LoopX 不双发或协商 v1 降级，因此未知嵌套组合版本必须失效关闭。读取已存 v1 证据时忽略缺失的 `continuation_hint` 仍然有效，但它不会让仅 v1 的实时解码器与 v2 生产者兼容。

`loopx turn plan` 与 `loopx turn run-once` 在构建 host 事务前没有 agent 选择阶段。当这样的 Turn 看到 v2 组合时，其外层 controller 通过重跑同一当前资格条件绑定咨询性主动作，在信封中保留组合以供审计，并把所选 Todo 标记为 `selected_by=turn_controller_advisory_primary`。这一确定性兼容路径不适用于 heartbeat/model Turn：它们的首个响应保持无身份且投递阻塞，直到 agent 显式选择。

紧凑信封不把那些可执行命令截断成不可用字符串。它携带非穷尽的 `writeback.suggested_todo_ids` 加 `selection_command_ref`；完整决策仍是精确 argv 的权威。

`protocol_action_packet` 保留在完整决策/冷路径中。信封从 `action`、`user`、工作 lane、automation 与 scheduler 契约重建其有序语义字段，同时携带显式 `llm_policy=no_api` 恒等式。当重建完全匹配时，capsule 只保留来源摘要哈希与推导状态。如果紧凑动作不同，它只保留该字段级 `residue`；如果较旧或不透明包无法重建，它保留原始摘要。这仅在一性之后移除重复，不改变源包持久化或默认配额输出。

大型 todo 摘要、前沿诊断、就绪历史、兼容字段与警告集合保留在被引用的完整决策/状态冷路径上。信封有 8 KiB JSON 预算，并报告其测量的源/信封字节数。

当内联值只会重复另一个权威字段时，热路径字段可以使用显式引用。特别是 `action.selected_todo.text_ref = action.recommended_action` 表示所选 todo 文本已经存在于推荐动作中。Scheduler 重置计划在满足可执行 argv 限制时内联保留精确确认 argv；失败 argv 保持在 `failure_cli_args_detail_ref` 之后，直到 host 更新实际失败。消费者必须跟随这些引用，而不是把省略的重复当作缺失状态。

本契约只是投影。它不改变配额选择、todo 路由、scheduler 状态、历史写入或状态迁移。把它提升为默认 agent 视图需要跨投递、monitor、用户 gate、capability gate、workspace-guard 与阻塞状态的单独一致性证据。

## 多状态一致性证据

`tests/fixtures/turn_envelope_state_matrix.json` 是持久的合成提升 fixture。它覆盖投递、monitor 静默跳过、用户 gate、capability gate、workspace guard、自主重规划、successor 重规划、阻塞与限流决策。每个用例都必须保留规范动作签名、重建 `protocol_action_packet`，并保持在 8 KiB 预算内。

当前矩阵产生 4,866 到 5,602 字节的信封，相对完整合成决策缩减 66.44% 到 69.36%。这足以让投影保持为可选的 host 视图。它不足以改变默认 CLI 响应：默认提升仍需要来自真实 host 集成的影子一致性、完整决策作为冷路径可用时无消费者回归，以及对默认视图变更的显式兼容验收。
