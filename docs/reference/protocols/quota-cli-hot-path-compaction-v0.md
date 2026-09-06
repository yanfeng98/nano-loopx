# 配额 CLI 热路径压缩 v0
> [English](quota-cli-hot-path-compaction-v0.md)

`quota_cli_hot_path_compaction_v0` 在不改变配额控制面所计算决策的前提下，界定默认面向 agent 的 `quota should-run` 投影。完整决策先构建。仅 CLI 的投影随后在热路径保留动作权限，并把重复的诊断细节移到显式 `--include-detail` 选择器之后。

## 所有权边界

配额控制面拥有决策、优先级、scheduler、交互、所选 todo 与用户动作语义。`cli_projection.py` 只拥有供 agent 消费的序列化视图。压缩器不得成为第二个决策所有者，也不得重算任何路由。

默认投影保留：

- `decision`、`should_run`、`effective_action` 与 `recommended_action`；
- 所选 todo、有界 `action_portfolio`、只读 `planning_horizon` 与执行义务；
- 交互模式、用户 channel 与可执行 agent/CLI 动作；
- scheduler 动作与自主重规划权限；
- 紧凑 vision 决策、触发种类、必需读取与 judge 结果；
- 警告种类、计数、稳定身份与冷路径引用。

`action_portfolio` 不是诊断性候选噪声。它保留在默认包中，因为当所选主动作在其真实调用点不可用时，它携带可执行回退规则。压缩只有在原样保留这一有界组合之后，才可以移除更大的 todo/capability 候选列表。

`turn_envelope_action_dimensions_v2` base/head 迁移对此增量组合有一个仅限 JSON 的有界增长配额。该配额只在 v0/v1 基线迁移到 v2 期间适用，始终作为评审信号，并且在超过 1,280 字符/字节、36 行或 896 个紧凑字符时仍然失败。一旦 v2 成为基线，普通热路径增长限制重新生效。

`quota_planning_horizon_v0` 同样是承载动作的上下文而非诊断噪声。紧凑路径原样保留其有界 Todo 链、类型化关系、attention id、完整性计数器与冷路径引用。其 `turn_envelope_action_dimensions_v3` 迁移获得一次仅限 JSON 的配额：3,200 字符/字节、84 行或 2,800 个紧凑字符。该配额只适用于 `none -> quota_planning_horizon_v0`，连同 v0/v1/v2 动作覆盖移入 v3。一旦 v3 成为基线，普通增长限制恢复。该 horizon 保持只读，从不取代 `selected_todo` 或显式 action-portfolio 选择。

热路径 horizon 与 `--include-detail agent-todos` 共享同一个 TypeScript 拥有的 `todo_planning_inventory_v0`；它们不是别名。前者最多主动披露五个策略项。后者增加更大的 `todo_planning_inventory_detail_v0` lens，包括规划状态、claim 状态、类型化关系与完整性，同时在重复 item 细节上引用现有 Todo 摘要。具体命令 `todo list --goal-id ... --role agent --status open --agent-id ...` 仍是完整来源读取。库存溢出必须变成显式的不完整，而不是配额失败或无界默认包。

增量式 `none -> todo_planning_inventory_detail_v0` 迁移有一个仅限 JSON 的配额：1,280 字符/字节、36 行与 1,024 个紧凑字符。它只在该 probe 在显式 detail 变体上观察到这一精确 schema 变更时适用。未知 schema 与更大增长失效关闭；一旦 v0 进入 base，普通冷路径限制恢复。

重复 vision 审计使用 `$.vision_continuation_audit` 作为权威投影。候选清单与对等动作清单保留计数，并指向 `--include-detail agent-todos`。完整 vision 审计可通过 `--include-detail vision` 获得；`--include-detail all` 恢复每个受支持的 detail 小节。

## 资格契约

确定性测试拥有完整与紧凑的精确一致性、冷路径恢复、schema 形状与字符预算。真实规模回归必须在压缩前超过默认预算，并在其后保持在预算之内。

模型资格是单臂且实际默认的。交付的 `actual_default_model_behavior_portfolio_v0` 把 CLI 热路径投影——而非未投影的内存中决策——发送给 Doubao actor。其独立来源 oracle 仍须在每次重复中观察到预期所选 todo、用户关卡、执行义务、scheduler 路由与 vision/重规划行为。planning-horizon 场景另外从固定类型化事实出发，独立于生产者验证完整策略关系链，并要求模型在所选工作之前对 horizon 进行有界回读。移除 horizon、破坏中间关系或同时偏移生产者和紧凑包都会在 provider 花费之前失败。一个专门的压缩回归场景必须在投影前超过 JSON 热路径预算、之后保持在预算内、保留精确的源生语义契约并保留模型路由。两个额外的超预算场景在省略诊断噪声的情况下重复干净所选工作与阻塞关卡契约。有界对比结果要求这些配对保持不变，而阻塞与非阻塞用户动作、所选工作与必需 vision 重规划仍可区分。精确 helper 遍历、省略计数、警告引用、去重与对等路由形状仍是确定性投影测试的职责。旧完整包不作为永久第二产品契约保留；配对模式保留给显式差异诊断。

该组合还包含一个未来主动作场景：一个窗口未到的类型化 P0 monitor 仍以不可用的更高优先级工作可见，而实际默认模型必须执行所选的就绪回退。这界定了模型对投影的服从性；确定性测试分别覆盖遗留情况：粘性主动作存活时，包仍必须暴露回退动作。

实时回执只可保留有界场景结果与摘要。包、prompt、原始模型响应、凭据与对话保持在仓库之外。
