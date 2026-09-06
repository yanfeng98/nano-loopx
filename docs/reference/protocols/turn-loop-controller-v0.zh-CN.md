# loop_turn_loop_disposition_v0
> [English](turn-loop-controller-v0.md)

`loop_turn_loop_disposition_v0` 是纯 Turn Loop Controller 转换契约。它仅凭一张已验证的 Turn 回执加一份全新 quota/scheduler 决策，决定受治理 loop 的下一步，别无其他。

`loopx turn run-once` 仍是原子受治理执行器：决策、执行一个有界 host 段落、独立验证、writeback、一次性花费。controller 不取代它、不调度进程、不调用 host 唤醒 API、不调用模型、不睡眠、不写状态、不花费配额。Scheduler 进程管理、host 特定唤醒适配器与操作员呈现是 Turn Loop Controller 计划中的后续切片。

## 输入

| 输入 | 形状 | 备注 |
| --- | --- | --- |
| `turn_receipt` | 从 `loopx_turn_execution_v0` 合格化的一张 `ValidatedTurnReceipt` | 当尚无 Turn 运行时可以缺席；物化结果需要下述完整 M7 settlement 证据 |
| `quota_decision` | 一份全新 `loopx_turn_envelope_v0` | 必须满足共享类型化信封契约 |
| `predecessor_turn_key` | 由外部继续适配器提供的因果绑定 | 有回执时必需，且必须等于其 `turn_key`；它刻意不是配额信封内的未签名字段 |
| `bounded_turn_budget` | 一个 `BoundedTurnBudget` | 当回执为 `validated_progress` 时必需 |

输入在边界处类型化并验证。controller 不接受调用方编写的 `result_kind + lineage` 或仅相位映射。回执从一份公开 `loopx_turn_execution_v0` 合格化，其交易回执须 `ok=true`、受支持的结果种类、完整 `(goal_id, agent_id, todo_id)` 血统与一个 `turn_key`。物化结果（`validated_completion` / `validated_progress`）还要求以下全部事实：

- 执行与交易回执均为 `committed`；
- Core M7 settlement 成功，并恰好发出有序的 `validation -> durable_writeback -> quota_spend` 回执链；
- 每个 settlement 回执都在同一 `effect_id` 下提交，且该 id 与交易的类型化 settlement 身份匹配；
- 公开执行效果证明持久化状态写入与一次配额花费；
- scheduler 交接已完成；
- `validated_completion` 从必需的显式 `completion_continuation` 字段携带持久化 Todo 生命周期结局（`successor`、`active_goal` 或 `no_followup`）。缺失或矛盾的完成状态被拒绝而非推断。

这使 settlement 真相保留在 Core Effect Program 中，而不是作为 Turn-controller 相位逻辑重复。预算必须携带严格整数域（`type(...) is int`、`max_turns > 0`、`0 <= completed_turns <= max_turns`）以及与新鲜决策相同的血统。提供回执时，外层适配器必须用等于回执 `turn_key` 的独立 `predecessor_turn_key` 绑定新鲜决策；旧回执不能对后续信封重放。无效或过期输入抛出 `ValueError`；它绝不编码为一种 disposition。

## 输出

恰好一个类型化 disposition：

| disposition | 含义 | quota |
| --- | --- | --- |
| `run_now` | 新鲜决策允许下一个投递 Turn | controller 不花费 |
| `wait` | 安静节奏或投递被阻塞 | 不花费 |
| `user_action_required` | 回执或决策投影出具体用户动作 | 不花费 |
| `repair` | 任何 successor Turn 之前需要 repair 级恢复 | 不花费 |
| `replan` | replan 级恢复；见下方继续边界 | 不花费 |
| `terminal` | 新鲜 Goal 前沿加持久化 no-follow-up 证明 Goal 关闭 | 不花费 |

输出空间恰好是这六种 disposition。没有 `contract_error` disposition：契约失败在类型化输入边界处被拒绝。每个载荷都携带 `spends_quota=false`、`launches_host=false` 与 `writes_state=false`。

## 决策表

| 回执 | 新鲜决策 | disposition |
| --- | --- | --- |
| 无 | 允许投递 | `run_now` |
| 无 | 安静 / 仅节奏 | `wait` |
| 无 | 新鲜 `terminal_no_followup` Goal 前沿 | `terminal` |
| `validated_completion` + 持久化 `successor` | 所选 Todo 是声明的 successor | 路由新鲜决策（`run_now`、`wait`、`repair`、`replan` 或用户动作） |
| `validated_completion` + 持久化 `active_goal` | 新鲜 Goal 前沿选择不同 Todo | 路由新鲜决策 |
| `validated_completion` + 持久化 `no_followup` | 新鲜 Goal 前沿也是终态 no-follow-up | `terminal` |
| `validated_completion` | 过期、缺失或未声明的继续 | `ValueError` |
| `validated_progress`，预算剩余 | 允许投递 | `run_now` |
| `validated_progress`，预算耗尽 | 任意 | `replan` 并带有限增量要求 |
| `validated_progress` | 无投递 | `wait` |
| `repair_required` | 任意 | `repair` |
| `replan_required` | 任意 | `replan` |
| `user_action_required` | 任意 | `user_action_required` |
| 持久化 `no_followup` + 新鲜终态前沿 + 决策用户动作 | — | `terminal`（已证明的 Goal 关闭胜出） |
| 继续中完成 + 决策用户动作 | — | `user_action_required` |
| `wait` | 任意 | `wait` |
| 可重试 `host_failure`，尝试预算剩余 | 投递或 wait | `wait` 并带同 Turn 受限退避继续 |
| 可重试 `host_failure`，尝试预算耗尽 | 任意 | `repair` |
| 不可重试或遗留 `host_failure` / `validation_failed` / `writeback_failed` / `quota_spend_failed` | 任意 | `repair`（在任何 successor Turn 之前路由） |
| replan 类决策动作（`autonomous_replan*`） | — | `replan` |
| repair 类决策动作（`*_repair*`） | — | `repair` |
| 决策投影出用户动作 | — | `user_action_required` |

## 优先级与失效关闭规则

- `validated_completion` 证明的是 Todo 转换，不是 Goal 关闭。声明的 successor 或活动 Goal 前沿继续穿过新鲜决策。只有持久化 `no_followup` 加新鲜终态 Goal 前沿才能产生 `terminal`。未声明 successor、重新选中的已完成 Todo 或缺失生命周期结局都会抛出 `ValueError`。
- 生命周期只能在同一 `completion_turn_key` 内把显式 `active_goal` 完成恢复为 `no_followup`。该受审计恢复不是第四种继续方式，且从不削弱 controller 的新鲜前沿要求。
- 仅验证的中间态、仅相位提交映射、不完整 settlement 回执链、不匹配的 effect 身份、缺失持久化效果或不完整 scheduler 交接，都不能驱动 `terminal`、`run_now` 或任何其他物化继续。
- 提供回执时，外层适配器必须提供等于回执 `turn_key` 的独立 `predecessor_turn_key`。缺失或不匹配的键抛出 `ValueError`（`stale_receipt`）；这在不给 `loopx_turn_envelope_v0` 增加未签名字段的情况下关闭了过期重放缺口。
- 每个其他用户动作信号（来自回执或决策）都在投递 disposition 之前路由到 `user_action_required`。
- 类型化可重试 Host 失败从不授权不同模型或新 Todo。controller 返回 `wait`，并带精确尝试次数、最大尝试数、重试延迟、`same_turn=true` 与 `model_fallback_allowed=false`。外层 scheduler 可以在延迟后以显式重试权限唤醒同一失败 Turn。一旦尝试预算耗尽，controller 返回 `repair`；遗留或畸形失败元数据不能选择重试。
- 新鲜决策必须通过 Turn 计划驱动者使用的同一类型化路由满足共享 Turn 信封契约（`loopx_turn_envelope_v0` schema、非空相等签名哈希与预算内压缩）；伪造或截断信封抛出 `ValueError`，绝不 `run_now`。
- `validated_progress` 只有在血统与新鲜决策匹配的已证明 `BoundedTurnBudget` 下才能继续；没有它，controller 抛出 `ValueError`，而不是猜测无界继续。预算耗尽路由到 `replan`，而不是 `terminal`，因为有界 Turn 链结束并不是 Goal 结束的证据。
- 输入有效性在类型化输入边界处强制，而不是编码为第七种 disposition。转换输出空间始终是上述六种 disposition 之一。

## Replan 继续边界

`replan` 绝不因 host 会话可恢复而允许重跑同一过期 todo。disposition 载荷携带 `replan_continuation`：

- `requires_bounded_delta=true`：任何 successor Turn 之前必须写入有界 `todo_delta` 或 `vision_delta`；
- `fresh_envelope_required=true`：下一个 Turn 必须来自新鲜 TurnEnvelope，而非重放的；
- `stale_todo_rerun_allowed=false`。

这镜像自主重规划与两次停滞契约：带开放验收缺口的无可运行 todo、终态/过期/不兼容的所选 todo、已验证的负面证据，或两次合格 Turn 无物化进展，都要求 replan 而非另一次投递尝试。

## 边界

controller 是纯函数。它不得调用模型、睡眠、修改 host scheduler、写状态或花费配额。无效或过期输入在类型化输入边界处以 `ValueError` 拒绝；它从不猜测恢复方式，也不捏造 host、gate 或用户动作。
