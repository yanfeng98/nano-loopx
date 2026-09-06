# 接口预算合同

> [English](interface-budget-contract.md)

LoopX 把热路径 worker surface 保持得足够小,让一个简短 heartbeat 就能在无需读取原始 run history 或冗长聊天上下文的情况下路由工作。这是一份约束合同,而不是鼓励增加更多状态 surface。下面的每个 surface 都有一个唯一 owner、一个具名的消费者动作、一个冷路径回退,以及大小/数量预算。

| Surface | Owner | 消费者动作 | 冷路径 | 大小预算 | 嵌套预算 | 数量预算 |
| --- | --- | --- | --- | --- | --- | --- |
| `heartbeat_prompt_json` | heartbeat 自动化 | 唤醒并路由一个有界 Turn | `quota should-run`、`status` 或 `review-packet --handoff-only` | `json_chars <= 3500` 且 `interface_budget.within_budget=true` | `nested_keys <= 40` | `top_level_keys <= 30` |
| `review_packet_handoff_only_json` | 项目 Agent 交接 | 转发最小的充分任务包 | 完整 `review-packet` 或 run history 制品 | `json_chars <= 3000` 且 `handoff_interface_budget.within_budget=true` | `nested_keys <= 40` | `top_level_keys <= 18` |
| `quota_should_run_json` | 配额守卫 | 判定所选 Goal 是否可消耗计算 | `status`、`history` 或活跃状态 | `json_chars <= 13000` | `nested_keys <= 330` | `top_level_keys <= 52` |
| `dashboard_status_json` | 运营者 dashboard | 渲染首屏运营者状态 | `history`、run 制品或项目本地 adapter 输出 | `json_chars <= 18215` | `nested_keys <= 260` | `top_level_keys <= 25` |

这四项预算衡量的是紧凑的内存中机器 payload。它们不衡量实际写入 stdout 的文本:JSON 缩进、兼容投影、重复命令和 Markdown 包装可能让实际输出明显更大。下面的实际输出资格矩阵通过真实 CLI 入口衡量这一独立边界。

配额预算包含 typed 动作组合、一个共享的有界 CLI 路由、待选资格判定,以及 hard-lane 抢占证据。该预算为这些可执行语义保留了适度余量;重复的动作细节和命令前缀仍应放在紧凑引用或冷路径中。

| 实际输出 surface | 默认资格 | 规模/限制合同 | 冷路径 |
| --- | --- | --- | --- |
| `start-goal --guided` | 基线与增长 | 小型、拥挤和多 Agent 的 Goal;目标/命令重复 | `packet_summary.detail_refs` 与 `bootstrap-command-pack` |
| `bootstrap-command-pack` | 基线与增长 | 小型、拥挤和多 Agent 的 Goal;目标/命令重复 | `--message-only` 与 `packet_summary.detail_refs` |
| `quota should-run` | 绝对热路径 | todo 数量增长加语义锚点 | `status`、`history`、活跃状态、可重复的 `--include-detail <section>` |
| `status --goal-id` | 绝对热路径 | todo 数量增长;任务图默认排除 | `--include-task-graph`、`history`、run 制品 |
| `diagnose --goal-id` | 显式限制冷路径 | `--limit 5` fixture 矩阵 | status 加目标特定的配额/todo 读取 |
| `review-packet --handoff-only` | 绝对热路径 | todo 数量增长加交接语义锚点 | 完整 `review-packet`、run 制品 |
| `heartbeat-prompt --thin` | 绝对热路径 | Agent 范围与多 Agent fixture 矩阵 | `--compact`、`--full` |
| `todo list` | 基线与增长 | todo 数量增长与 Agent 过滤语义 | `--thin`、`--limit N`、角色/状态过滤、直接 todo id 生命周期命令 |
| `history --limit 5` | 显式限制冷路径 | 返回 run 界限 | 单项 run JSON/Markdown 制品 |
| `evidence-log --thin --limit 5` | 显式限制冷路径 | 返回证据界限 | 引用的 run history 与 rollout 事件制品 |

`quota should-run` 使用一个可重复的冷路径选择器:`--include-detail scheduler`、`agent-todos`、`user-todos` 或 `goal-boundary`;`--include-detail all` 展开所有 section。公开文档、输出的 `detail_ref` 命令和内部调用者只能使用这个选择器。附加到其他配额命令的未知 section 与选择器会在状态收集之前失败。

标准的实际输出清单与当前刻画上限位于 `loopx.control_plane.testing.cli_output_budget`。这些上限是回归基线,不是目标大小:保留当前较大的值会让未经评审的增长失败,而后续的优化会降低上限。测试还记录 UTF-8 字节数、行数、JSON 可解析性、pretty-print 开销、语义锚点、集合增长斜率以及 bootstrap 重复度。每个声明的面向 Agent 的 surface 都必须指明 owner、消费者动作和冷路径回退。

同一矩阵也刻画显式模式开关,而不是假设默认命令代表它们。覆盖的变体包括 `bootstrap-command-pack --message-only`、配额按 section 与 all-detail 选择器、TurnEnvelope 输出、status 任务图详情、完整 review packet,以及 brief/compact/full heartbeat prompt 模式。这些仍然是显式启用的冷路径,但它们的精确 stdout 大小和语义锚点同样是回归合同。

`todo list --thin` 是显式的有界投影,不是新的过滤或排序模式。在常规角色、状态、Todo id 和 Agent 过滤之后,它在单个顶层 `todos` 容器中为每个角色最多保留两个匹配项。热路径条目形状保留 `text`,省略冗余的派生 `title` 字段,使最大保留字段形状保持在已注册的固定预算之内。payload 保留现有 `todo_count` 语义,新增完全匹配的 `matched_todo_count` 以及 `returned_todo_count` 和 `omitted_todo_count`,并在 `payload_compaction` 中重复每角色溢出回读。保留的字符串与嵌套 scope 集合按 `todo_list_thin_projection_v0` 声明的范围进行限制,而可操作的标识与 gate/监控关系字段保持在允许清单中。本地路径、note/证据详情与重复摘要通道仍被省略。

`--limit N` 通过把每角色固有上限降低到 `min(N, 2)` 进行组合;它永远不会扩展 thin 投影。当需要被省略的条目或完整字段时,使用不带 `--thin` 的 `todo list`、直接的 Todo id 冷路径,或活跃状态。省略 `--thin` 会恢复现有的完整列表形状,而不改变 Todo 选择、排序、配额、生命周期或写入行为。

公开 help 表面中的 start 与 daily 命令组,以及 `heartbeat-prompt`,是 fail-closed 的清单输入。每个命令必须映射到一个默认合格 surface,或携带一个带理由的显式冷路径例外。canary 规划器会为 CLI 命令、help、实现、fixture、工作流或预算合同变更选择输出预算 profile,PR CI 将矩阵作为命名步骤运行。

资格判定还会对 `origin/main` 和候选 checkout 运行同一个公开 fixture。它只允许每个 surface 和格式获得策略级大小的增长,而不是把一个全局百分比视为安全。更小的候选在移除已声明的语义 key 或改变现有 `action_signature` 语义合同时仍然失败。被移除的可观测嵌套 JSON 路径或 Markdown 标题会作为评审信号上报:敏感的输出缩减必须在人工评审中说明这些内容,而有意的呈现或结构重构不应成为永久性的 CI 红灯。receipt 只包含计数、形状路径、标题与摘要;它们不持久化原始 CLI 输出。仅候选的 surface 在其绝对刻画通过后允许存在,而移除已合格的基础行则 fail closed。

两个预算层都刻意针对投影,而不是完整的归档事实。当某个 surface 需要更多详情时,把详情放到可查询的冷路径命令或链接的 run history 制品之后,而不是让周期性 heartbeat prompt 承载它。`nested_keys` 在三个 payload 层深度内统计字典 key,并每层最多采样 20 个列表项;它是热路径结构预算,不是归档记录大小预算。

新字段的约束规则:

1. 优先把证据加到 run history,然后只把最小的决策摘要投影到热路径 surface。
2. 热路径字段必须回答某个当前的消费者动作。如果消费者只说"便于查看",就把字段留在冷路径。
3. 新的嵌套对象必须保持在上述嵌套预算之内,或退役/压缩同一 surface 中的较旧字段。
4. 不要为了弥补不清晰的 payload 而增加 prompt 分支。改为澄清 status/配额/review-packet 合同。
5. 如果简短 worker 在选择下一个动作之前需要读取多个热路径 payload,就应把额外详情降级为冷路径命令。

配额守卫保留顶层 `action_required` 和 `open_count` 作为较旧 heartbeat/host prompt 的紧凑兼容别名;权威结构化字段仍然是 `interaction_contract.user_channel` 和 `user_todo_summary`。

回归入口:

```bash
pytest -q tests/control_plane/test_cli_output_budget.py
pytest -q tests/control_plane/test_cli_output_differential.py
python3 examples/control_plane/cli-output-base-head-differential-smoke.py
python3 examples/control_plane/cli-output-budget-regression-smoke.py
python3 examples/control_plane/hot-path-interface-budget-smoke.py
python3 examples/control_plane/status-quota-perf-budget-smoke.py
```

节奏合同:

同一个 smoke 还会输出并验证一个 `interface_budget_cadence` 摘要,用于干净的漂移检查。漂移检查 run 可以把该摘要记录到 run history;`loopx status` 会把它投影到 `attention_queue.items[].project_asset.interface_budget_cadence` 下,而 `quota should-run` 在顶层镜像所选 Goal 的摘要。这让简短 heartbeat 可以静默跳过仍然新鲜的干净检查,而不会丢失进行中的守卫 todo。

稳定的节奏字段:

- `checked_at`:热路径预算检查的运行时间。
- `freshness_hours`:干净检查保持新鲜的时间长度。
- `next_check_due_at`:下一次检查的到期时间。
- `overdue`:当前摘要是否已超过 `next_check_due_at`。
- `within_budget`:所有被测量的热路径 surface 是否在各自预算内。
- `minimum_headroom_ratio`、`tightest_surface`、`tightest_metric` 和 `headroom_remaining`:最紧张观测 surface 的紧凑余量证据。
- `recommendation`:取 `quiet_skip_until_next_check_due` 或 `rerun_hot_path_interface_budget_smoke` 之一。只有当每个 surface 都在预算内且最紧张指标仍有正余量时,新鲜检查才会静默跳过;余量为零的 surface 已经处在兼容性边缘,在更多热路径增长被接受之前应重新运行 smoke。

不要为这个节奏添加 heartbeat prompt 分支。把精确测量存入 run history,只投影这个紧凑决策摘要,并在 `overdue=true`、`headroom_remaining <= 0` 或 prompt/status/配额/review-packet/dashboard 合同变化时重新运行 smoke。

Scheduler 重置策略预算:

`quota should-run.scheduler_hint.reset_policy` 是 host 动作摘要,不是调试快照。它携带重置 token、host 状态 key、初始 Codex App RRULE、未变状态清除标志,以及检测重置转换所需的短标识/profile 签名。完整的标识/profile 快照不进入热路径;调试重置 token 为何改变时,使用 status、history、活跃状态或聚焦的回归 fixture。
