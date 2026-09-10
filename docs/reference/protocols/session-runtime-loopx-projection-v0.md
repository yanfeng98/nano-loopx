# 会话运行时到 LoopX 契约

状态：面向只读首屏投影的公开安全契约 v0。

本契约定义外部 agent 运行时如何把可见会话映射进 LoopX，而无需让 LoopX 成为运行时、复制私有 trace 或隐藏用户的主控制界面。它刻意保持运行时中立：Codex CLI、Claude Code、自定义 worker 与未来 host 集成都应能投影同一份小而稳定的形状。

## 边界

会话运行时拥有：

- 会话生命周期、模型/工具执行、沙箱、host 认证与计费；
- 原始 transcript、原始日志、原始工具输出与 host 审计轨迹；
- host 原生会话、事件、工具调用、工件与批准 id。

LoopX 拥有：

- goal id、goal 边界与权威源；
- todo、gate、quota、run 历史、reward 与 handoff 状态；
- 会话事实之上的紧凑公开安全投影；
- 通过 LoopX 命令或等价适配器进行的受控 writeback 决策。

首个集成模式是只读的。运行时可以把紧凑会话事实喂给 LoopX，但直到单独的受控写入契约被接受之前，LoopX 不得写入运行时、不得启动新会话、也不得声称同会话自动化。

## 身份映射

每个投影都应保留排查一次交接所需的关联键，同时把私有数据排除在 LoopX 状态之外。

| 字段 | Owner | 含义 |
| --- | --- | --- |
| `goal_id` | LoopX | 正在控制的稳定 goal。 |
| `agent_id` | LoopX | 已注册自动化或面向用户的 agent lane。 |
| `runtime_id` | 运行时适配器 | 公开安全运行时家族，如 `codex_cli_tui` 或 `custom_worker`。 |
| `session_id` | 运行时适配器 | 可见会话或 worker 的公开安全句柄。不安全时进行脱敏。 |
| `run_id` | LoopX | 记录该投影的紧凑 LoopX run 历史事件。 |
| `event_id` | 运行时适配器 | 可选紧凑来源事件指针。 |
| `todo_id` | LoopX | 当投影选择或阻塞具体任务时的关联 todo。 |
| `outcome_id` | 运行时适配器 | 可选紧凑结局/结果指针。 |

`session_id`、`event_id` 与 `outcome_id` 是引用，不是证据载荷。它们不得内嵌原始 prompt、本地路径、凭据、私有文档 id 或完整 host URL。

## 首屏投影

首屏是判断一个 loop 是否可以继续所需的最小操作员视图：

| 字段 | 必需 | 描述 |
| --- | --- | --- |
| `waiting_on` | 是 | `none`、`user`、`controller`、`agent`、`runtime` 或 `external_evidence`。 |
| `next_action` | 是 | 一个紧凑安全动作，写给当前执行者。 |
| `open_user_todo` | 是 | 首个具体用户 todo，或 `null`。 |
| `first_executable_agent_todo` | 是 | 通过 quota、scope 与 capability 关卡后的首个可运行 agent todo，或 `null`。 |
| `latest_validation` | 是 | 最新紧凑验证、blocker 或缺失证据摘要。 |
| `gate_state` | 是 | `clear`、`user_todo`、`operator_gate`、`blocked`、`deferred` 或 `approved`。 |
| `quota_state` | 是 | `eligible`、`throttled`、`monitor_quiet_skip`、`operator_gate` 或 `blocked`。 |
| `boundary` | 是 | 读/写 scope、私有数据规则与停止条件。 |

### 边界键状态

`boundary` 块使用类型化词级规则报告输入键如何被分类（精确键、完整词，或在 `_`、`-` 与驼峰命名拆分后的精确词序列；绝不使用子串）。来自 raw-material 与未分类键的值从不复制；显式紧凑字段契约中的值可用于构建有界投影。

- **compact**：投影读取的键、时间戳、用量指标（`*_tokens`）与指针/计数（`*_id`、`*_ref`、`*_count`、`*_at`），仅在没有 raw-material 词或短语存在时。已确认的冲突，如 `trace_id`、`message_id`、`conversation_id`、`log_count`、`prompt_tokens` 与 `prompt_token_count`，是显式安全例外。
- **raw material**：凭据、消息/transcript、日志、本地路径与原始工具输出。设置 `raw_material_detected`，列出 `raw_material_key_names` 与 `raw_material_categories`，并关闭 `agent_can_continue`。
- **unclassified**：任何其他键。列在 `unclassified_key_names`（有界）中，使生产者能发现契约漂移；它从不阻塞继续。

Raw-material 证据优先于通用指针后缀。例如 `secret_id`、`transcript_id`、`raw_id` 与 `api_key_id` 是 raw material，而非紧凑指针。

即使当前没有附着会话，投影也应有意义。此时 `runtime_id` 可为 `none`，`session_id` 可为 `null`，并且 `latest_validation` 应解释缺失的是哪个运行时事实。

## 最小 JSON 形状

```json
{
  "schema_version": "session_runtime_loopx_projection_v0",
  "goal_id": "loopx-meta",
  "agent_id": "codex-side-bypass",
  "runtime": {
    "runtime_id": "codex_cli_tui",
    "session_id": "public-safe-session-handle",
    "source_ids_redacted": false
  },
  "loopx_refs": {
    "run_id": "run_123",
    "todo_id": "todo_123",
    "event_id": "evt_123",
    "outcome_id": null
  },
  "first_screen": {
    "waiting_on": "agent",
    "next_action": "advance the first executable agent todo",
    "open_user_todo": null,
    "first_executable_agent_todo": "todo_123",
    "latest_validation": "last run validated install smoke",
    "gate_state": "clear",
    "quota_state": "eligible",
    "boundary": {
      "mode": "read_only_projection",
      "raw_transcripts_copied": false,
      "credentials_copied": false,
      "private_paths_copied": false,
      "stop_condition": "stop for user gate, missing authority, or unsafe write"
    }
  }
}
```

## 产品界面

同一契约应供给两个不同界面：

- **Showcase frontstage：** 仅公开 fixture，渲染为叙事案例卡片或动效状态。它可以渲染进度、关卡与交接，但不得发布实时 registry 状态。
- **本地控制面：** 面向操作员的实时私有/本地投影。当它们在本地环境安全时可以显示会话句柄与当前关卡，但这些细节不得进入 GitHub Pages 与公开文档。

## 验收检查

一个会话运行时投影在以下条件下可接受：

1. `goal_id`、`agent_id`、`runtime_id` 与 LoopX 引用足以在无需复制原始证据的情况下对账一次交接。
2. `waiting_on`、`next_action`、用户 todo、agent todo、验证、关卡与配额状态可在首屏渲染。
3. 缺失运行时事实变成显式 blocker 或 `null` 字段，而不是猜测动作。
4. 在单独的 writeback 契约启用之前，投影始终只读。
5. 公开 fixture 不包含原始 transcript、凭据、私有链接、本地路径或内部项目名。
