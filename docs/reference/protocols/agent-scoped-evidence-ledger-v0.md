# agent_scoped_evidence_ledger_v0

`agent_scoped_evidence_ledger_v0` 为需要重规划、交接或解释进展、又不读取原始 rollout 日志、私有 active state 或另一个 agent 详细工作轨迹的 agent 定义了一个薄的时间顺序读模型。

本契约是读模型。它不取代 `ACTIVE_GOAL_STATE.md`、todo 状态、紧凑 run 历史、状态投影、评审包、quota 路由或追加式 rollout 事件日志。

## 当前来源

LoopX 已有有用的历史与证据界面，但它们服务于不同工作：

| 界面 | 当前工作 | 对 agent 重规划的缺口 |
| --- | --- | --- |
| `rollout-event-log.jsonl` | 追加式结构化事件，如 todo、quota、refresh、validation 与紧凑证据事件。 | 它是底层事件来源，不是面向 agent 的过滤时间线。 |
| `loopx status` | 投影当前状态、todo index、关注队列、agent lane、run 历史与事件摘要。 | 它回答「现在什么是真的」，而非「该 agent 重规划前应复习什么序列」。 |
| `loopx review-packet` | 为评审或交接打包状态与关注项。 | 它是包形状，不是通用作用域事件 ledger。 |
| `loopx history` | 读取紧凑 run 历史与 run index。 | 它以 run 为中心，不等于 rollout 事件。 |
| `loopx quota should-run --agent-id ...` | 决定特定 agent lane 是否应行动，并从证据来源投影紧凑覆盖 ledger 加未覆盖前沿。 | 它不要求模型重建历史，也不把读取回执当作进展。 |

得到的界面是公开安全、有界、agent 作用域的 ledger，host 可投影进重规划动作包，操作员可完整检查。

## 所有权边界

| 层 | 拥有 | 不得拥有 |
| --- | --- | --- |
| 事件来源 | 持久化追加式事件、紧凑 run 记录、id、时间戳与公开安全引用。 | 面向 prompt 的规划摘要或跨 agent 隐私策略。 |
| Status 与评审包 | 当前投影、关注队列、前沿摘要与操作员包。 | 原始时间顺序重放或写权限。 |
| Quota | Lane 路由、花费策略、scheduler 提示、host 上下文投递与最小重规划动作包。 | 存储重规划理由或接受 writeback。 |
| Agent 作用域证据 ledger | 当前 agent 的薄时间顺序行，加其他 agent 压缩前沿。 | 重规划选择策略、语义增量验证、规范写入、原始日志、原始轨迹、私有文档或完整其他 agent 轨迹。 |
| 重规划上下文策略 | 构建覆盖 ledger、投递回执与未覆盖前沿。 | 重新实现类型化进展比较或终态关闭真相。 |
| 语义写 gate | 依据当前义务验证类型化进展、状态接地的 successors、新鲜 vision 结局、blockers 与覆盖背书的终态结果。 | 重建证据 ledger 或解释分类措辞。 |
| 行动 agent | 从投递的上下文选择一个未覆盖方向，提交类型化观察或 vision 结局。 | 单独把上下文投递、手动读取或遗留 ACK 当作进展。 |

## 读模型形状

CLI 载荷使用交付的 `agent_scoped_evidence_log_v0` schema（协议名描述的是 ledger 概念，而非第二个线格式 schema）：

```json
{
  "schema_version": "agent_scoped_evidence_log_v0",
  "goal_id": "example-goal",
  "agent_id": "codex-evidence-peer",
  "mode": "thin",
  "todo_id": null,
  "since": null,
  "event_kinds": [],
  "limit": 30,
  "matched_count": 1,
  "ledger_count": 1,
  "truncated": false,
  "source_refs": [
    "rollout_event_log.public_safe_view",
    "compact_run_history.public_refs"
  ],
  "ledger": [
    {
      "event_id": "evt_123",
      "recorded_at": "2026-07-05T00:00:00Z",
      "source": "rollout_event_log",
      "event_kind": "todo_update",
      "agent_id": "codex-evidence-peer",
      "todo_id": "todo_123",
      "classification": "implementation_batch",
      "status": "open",
      "summary": "P0 implementation frontier was split into a design contract and a CLI read model."
    }
  ],
  "other_agent_frontier": {
    "schema_version": "other_agent_frontier_v0",
    "policy": "goal_frontier_only",
    "item_count": 1,
    "items": [
      {
        "agent_id": "codex-main-control",
        "source": "run_history",
        "classification": "validated_progress"
      }
    ]
  },
  "boundary": {
    "raw_logs_recorded": false,
    "raw_trajectory_recorded": false,
    "credential_values_recorded": false,
    "absolute_paths_recorded": false,
    "other_agent_event_stream_expanded": false
  }
}
```

该 schema 刻意窄。它应廉价生成、prompt 中廉价读取，并稳定到足以支撑配额/重规划测试。

## CLI 契约

公开 CLI 只读：

```bash
loopx --format json evidence-log --goal-id <goal-id> --agent-id <agent-id> --thin --limit 30
```

受支持过滤器：

| 选项 | 含义 |
| --- | --- |
| `--todo-id <todo-id>` | 按精确 todo id 过滤 rollout 事件，并按有界 todo 提及过滤紧凑 runs。 |
| `--since <iso8601>` | 返回时间戳之后记录的行。 |
| `--event-kind <kind>` | 过滤 rollout 事件种类，如 `todo_update`、`quota_should_run` 或 `validation`。 |
| `--limit <n>` | 过滤后界定行数。默认应小到足以进入 agent prompt。 |
| `--history-limit <n>` | 过滤前扫描的紧凑 run 历史行数上限。 |
| `--rollout-limit <n>` | 过滤前从尾部扫描的 rollout 事件行数上限。 |
| `--thin` | 选择当前唯一的公开安全模式；显式接受它以便生成可读命令。 |
| 全局 `--format json\|markdown` | 选择 JSON 或紧凑 Markdown 渲染。 |

命令在缺 `goal_id` 或 `agent_id` 时必须失效关闭。`codex` 这类模糊界面值不应静默落入 other-agent 语义；调用方应传已注册 agent id，并在需要时传独立 host 界面，如 `codex-cli` 或 `claude-code`。

## 作用域规则

当前实现按以下确定性规则返回详情行：

- 事件的 `agent_id` 等于请求的 agent id；
- 存在 `--todo-id` 时，事件具有该精确 todo id；
- 紧凑 run 历史行具有请求的 agent id，且按 todo 过滤时在有界 run 字段之一提及该 todo；
- `--since` 与规范化 `--event-kind` 过滤器在最终最新优先限制之前应用。

其他 agent 默认不应逐行显示。它们应从每个 agent 的最新紧凑 run 历史行压缩进 `other_agent_frontier`，至多三行。这使 agent 了解共享方向，而不会继承另一个 lane 的私有草稿。

## 重规划集成

当 quota 或 status 为 agent 投影重规划义务时，host 把有界 agent 作用域时间线折叠进紧凑覆盖 ledger，并与当前义务一同投递：

```json
{
  "replan_action_packet": {
    "decision": "replan_required",
    "obligation_id": "replan-opaque-id",
    "uncovered_frontier": {
      "baseline": {"surface_id": "surface-auth", "result_class": "unchanged"},
      "required_any_of": ["new_surface", "new_hypothesis", "new_probe_family"]
    },
    "required_outcome": "semantic_delta",
    "writeback_contract": {
      "schema_version": "typed_progress_observation_v0",
      "transport": "loopx_refresh_state",
      "command_template": "loopx ... refresh-state ... --progress-result-class <typed-class> --progress-evidence-id <evidence-id> <typed-dimension-options>"
    },
    "allowed_terminal": ["exploration_exhausted", "blocked", "no_followup"]
  }
}
```

完整义务还携带 `replan_context_v0`：一个有界 `coverage_ledger`、同一未覆盖前沿与 `replan_context_delivery_receipt_v0`。控制面责任刻意拆分并因果绑定：

- 证据 ledger 保持持久化公开安全时间线；
- quota 拥有上下文投递，不需要弱协议遵循模型去发现或执行读仪式；
- `typed_progress_observation_v0` 拥有工作切片身份与结果语义；
- quota 与 `refresh-state` 使用同一 goal-frontier reducer，写 gate 只以接受的语义增量关闭当前义务。

当 Turn 身份使 settlement 链可执行时，`interaction_contract.cli_channel.replan_settlement_contract` 指名其唯一因果绑定。当所选 Todo 拥有回执时，其 `semantic_obligation.settlement_bound` 字段为 `false`：此时类型化 replan 增量只用 `--todo-id` 写入并花费，而义务 id 保留用于语义验证。组合 `--todo-id` 与 `--replan-obligation-id` 绝不成为有效 settlement 身份。没有所选 Todo 时，同一契约把 replan 义务标记为直接绑定并投影 `--replan-obligation-id`。无作用域诊断读取只保留紧凑 replan 指引；它不在缺失 Turn 身份时广告可执行 settlement 契约或配额花费。

agent 随后应写回以下之一：

- 带新界面、假设或 probe 家族的 `advanced` 观察；
- 指名当前状态中实际可运行的 successor Todo 的 `advanced` 观察；
- 带证据的新具体 blocker；
- 覆盖背书的 `exploration_exhausted` 或 `no_followup`；或
- 对 vision 派生职责，一个新鲜、证据链接的 vision 路径结局。

被接受的类型化语义 ACK 结清相应投影义务，即使来源验收缺口仍可见。终态覆盖输入在其所需覆盖作用域缺失时于 CLI 边界失败；`exploration_exhausted` 另外要求显式覆盖完成。

每次成功的诊断性 `loopx evidence-log` 执行都追加一个 `evidence_log_read` rollout 事件并返回 `evidence_log_read_receipt_v0`。回执携带 goal id、agent id、有界读取窗口、规范公开安全命令与记录时间戳。回执事件从无过滤 ledger 视图中排除，使重复读取不会递归膨胀时间线。它们只是可观测性事实：一次读取、一次失败读取、一个散文 ACK 或一个历史修复增量 ACK 都不关闭当前义务。这防止先前周期评审的回执掩盖后续 vision/frontier 职责。

### Effect 程序边界

本流程使用 effect-program 分离，而不添加第二个 settlement 执行器。Host 上下文投影是可重复读取效果；类型化进展 writeback 是单独验证的状态迁移。投递回执证明上下文投递，语义增量证明该上下文的使用。任一回执都不得冒充另一个。

实时行为资格测试通过实际函数工具对话而非仅测试输出字段验证该因果交接。一个 Doubao actor 接收交付的宿主 heartbeat 正文，并针对一个封闭公开安全 Goal 选择 quota 命令。Harness 通过真实 LoopX CLI 运行该命令，返回其实际上下文/动作包，并要求 actor 选择下一个真实工具动作。actor 独立资格选定的类型化观察，然后执行真实 `refresh-state` 命令。仅证据日志、仅散文、quota 前、等价指纹与无 grounding 的 successor 动作都不能通过。只允许临时 fixture 状态变化，回执存储有界命令摘要与类型化结局，而非 prompt、包或输出。

## 隐私边界

Ledger 必须保留 rollout 事件边界：

- 无原始任务文本；
- 无原始日志、stdout、stderr、轨迹或 verifier 尾部；
- 无凭据、token、header 或 secret；
- 无本地绝对路径；
- 无私有文档正文或聊天 transcript；
- 无复制进公开安全行的私有源载荷。

行可以包含紧凑 id、相对公开工件引用、脱敏摘要、省略说明与私有源计数。若来源私有，行应说明只记录了紧凑指针或计数。

## 当前实现状态

CLI、rollout 事件/run 历史合并、有界其他 agent 前沿、host 投影覆盖上下文、最小动作包、类型化重复检测器与共享 quota/写时语义 gate 均已实现。Todo 与物料投影仍是独立当前状态界面；它们不复制进本时间顺序 ledger。历史修复 ACK 对旧 run 行有有界读取适配器，但新重规划关闭只有一条真相：类型化语义增量。

## 验收

一项变更只有满足以下条件才符合本契约：

- `loopx evidence-log` 针对具体 `goal_id` 与 `agent_id` 返回有界 JSON 包；
- 当前 agent 行详细，而其他 agent 行默认压缩；
- 过滤器表现确定，无需 agent prompt 解析原始 JSONL；
- 可重规划 quota/status 载荷投递紧凑覆盖 ledger 与未覆盖前沿，而不要求模型读仪式；
- 实时函数工具资格证明默认模型从生产 heartbeat/quota 交换中选择并执行语义下一动作，而非仅仅复述测试字段；
- 既有 status、history、review-packet 与 rollout-event-log 界面保持当前职责；并且
- 公开测试在不提交私有状态、本地路径、原始日志或原始轨迹的情况下证明隐私边界。
