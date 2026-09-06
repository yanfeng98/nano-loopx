# Host 集成插件计划 v0

`host_integration_plugin_plan_v0` 描述从今天 skill 级 LoopX slash-command 回退到 host 自有命令注册表插件的产品路径。它是规划契约，不是已交付插件清单。

目标是让 Codex App 之类的 host 识别 `/loopx` 命令、安装或刷新瘦 heartbeat 正文、应用 `scheduler_hint` 并保护私有运行时数据，同时让 LoopX CLI 保持事实来源。

本计划组合既有契约：

- [codex_app_host_command_registry_v0](codex-app-host-command-registry-v0.md) 用于 `/loopx`、`/loopx <goal text>` 与 `/loopx-global-*` 解析。
- [host_integration_surface_v0](host-integration-surface-v0.md) 用于生命周期读取、受控写入、CLI 回退与公开/私有边界。
- [session_runtime_loopx_projection_v0](session-runtime-loopx-projection-v0.md) 用于不含原始 transcript 的紧凑运行时投影。

## 非目标

- 不替换 CLI，也不让 host 特定状态机成为权威。
- 不在 LoopX 公开状态中存储原始 transcript、原始工具输出、凭据、计费数据、本地绝对路径或私有项目物料。
- 不把聊天 slash 命令当作破坏性 git、生产动作、私有物料读取、外部发布或 reward 写入的批准。
- 不为可见 TUI 工作流默认做隐藏无头执行。

## 插件能力集

最终 host 插件应小而显式：

| 能力 | Host 职责 | LoopX 事实来源 |
| --- | --- | --- |
| 命令注册表 | 在普通聊天之前解析 `/loopx`、`/loopx <goal text>`、`/loopx-global-*` 与遗留别名。 | `loopx slash-commands`、`bootstrap-command-pack`、global manager 命令。 |
| 项目身份 | 解析工作区根、公开安全根标签、goal id 与已注册 agent id。 | Registry goal 条目与 `quota should-run` agent 身份检查。 |
| 生命周期读取 | 把 status、quota、评审包与 command-pack 输出呈现为紧凑 host 包。 | 来自 `status`、`quota should-run`、`review-packet` 与 `bootstrap-command-pack` 的 CLI JSON。 |
| 受控写入 | 只提供 CLI 等价的 todo/gate/reward/refresh/spend 操作，必要时带 dry-run。 | LoopX CLI 命令与 active-state/event ledger 写入。 |
| 自动化安装 | 使用 `heartbeat-prompt --thin` 与作用域 agent 身份创建或刷新 host heartbeat。 | 生成的 heartbeat prompt 与 registry 协调字段。 |
| Scheduler 适配器 | 仅在 `stateful_backoff.apply_needed=true` 时通过 `automation_update` 应用 `scheduler_hint.codex_app.recommended_rrule`，然后运行 `codex_app.ack_hint.cli_args`；当仅 `ack_needed=true` 时跳过 host 写入，直接运行绑定 ack。 | `quota should-run.scheduler_hint`、`quota scheduler-ack-current`。 |
| 隐私 guard | 脱敏本地路径，拒绝原始 transcript/会话文件/凭据载荷。 | 公开/私有边界加 host 投影边界检查。 |

## 分阶段路径

### 阶段 0：Skill 回退

Agent 通过 `loopx-project` skill 识别 `/loopx` 与 `/loopx <goal text>`，并调用 `loopx bootstrap-command-pack`。这对早期测试足够，但属于 prompt 级行为，可能被会话历史污染。

退出标准：

- `/loopx` 保持读取/状态优先。
- `/loopx <goal text>` 在写入 todos 之前产生有序计划。
- 回退总是显示 host 插件应调用的 CLI 命令。

### 阶段 1：Host 命令别名

Host 解析 slash 命令，并把结构化交接包传给 agent 或直接传给 CLI。包包含命令种类、goal 文本、公开安全项目标签、可选 goal id、已注册 agent id、权限标志与 CLI 回退。它不在公开输出中包含本地绝对路径。

退出标准：

- `/loopx-global-summary`、`/loopx-global-gates`、`/loopx-global-todos` 与 `/loopx-global-risks` 是只读 global manager 命令。
- 未知 `/loopx-*` 命令以 `loopx slash-commands` 帮助失效关闭。
- 解析或命令执行不可用时，host 仍回退到 CLI。

### 阶段 2：Heartbeat 安装器

项目连接后，host 可以提议安装或刷新循环 LoopX heartbeat。它应生成瘦身作用域任务正文：

```bash
loopx heartbeat-prompt --thin --goal-id <goal-id> \
  --agent-id <registered-agent-id> \
  --agent-scope "<public-safe agent scope>"
```

插件不应把项目特定策略手抄进自动化。它只应存储 host 自有的调度元数据，如当前 `reset_token`、最后应用的 RRULE 与未变化轮询状态。

退出标准：

- goal 有已注册 agent 时，缺失 agent 身份失效关闭。
- 更新 heartbeat 正文不花费配额。
- host 在写入自动化设置前可以显示生成的正文或紧凑安装包。

### 阶段 3：Scheduler 提示适配器

Host 在每次 heartbeat 结果后应用 `quota should-run.scheduler_hint`：

- `run_now` 恢复或保留活动节奏。
- wait/backoff 状态只在需要 host 更新工作时暴露 `codex_app.recommended_rrule`。
- `codex_app.stateful_backoff.apply_needed=true` 意为针对该 RRULE 调用 `automation_update`；成功后运行 `codex_app.ack_hint.cli_args`，使 LoopX 持久化 reset token、身份签名、进度索引与最后应用的 RRULE。
- `apply_needed=false` 意为所需 RRULE 已应用；跳过 host 更新。若 `ack_needed=true`，直接运行绑定的 `ack_hint.cli_args`，使 LoopX 持久化匹配的 host 回读；否则无需任何 scheduler 动作。
- Codex CLI TUI 与 Claude Code loop 在自停前运行最终 quota/replan 检查。

仅节奏更新、重置为初始变更、最终检查与自停决策不花费配额。投递 Turn 只在验证与持久化 writeback 之后花费。

### 阶段 4：受控写入工具

插件只能在 CLI 等价命令与预览路径已文档化后暴露受控写入。Todo 生命周期与状态刷新可更早可用；gate 决策、human reward、lease 写入、生产动作以及浏览器/frontstage 触发的写入需要更严格的预览与批准语义。

退出标准：

- 每个写入都广告其 CLI 回退。
- 缺失权限返回结构化 blocker。
- Host 批准不得冒充用户 reward 或 controller 批准。

## 验收矩阵

| 场景 | 所需结果 |
| --- | --- |
| 已连接项目中的 `/loopx` | Host 返回读取/状态优先命令包且不写状态。 |
| `/loopx fix issue triage` | Host 保留 goal 文本、运行 bootstrap command pack、仅通过显式 goal-start 流程写入有序 todos。 |
| `/loopx-global-summary` | Host 返回只读全局摘要，且不能修改项目状态。 |
| 未知 `/loopx-debug-me` | Host 以 `loopx slash-commands` 帮助失效关闭。 |
| 缺失已注册 agent id | 协调 goal 的 heartbeat 安装/刷新失效关闭。 |
| Scheduler reset token 变更 | Host 恢复初始 RRULE 并清除未变化轮询状态，不花费配额。 |
| 原始 transcript 提交给插件 | 插件拒绝或脱敏载荷，且不在公开状态中记录原始 transcript。 |
| CLI 不可用 | 插件报告安装/doctor blocker，而不是发明仅 host 的状态迁移。 |

## 最小公开 Fixture 形状

```json
{
  "schema_version": "host_integration_plugin_plan_v0",
  "host_kind": "codex_app",
  "command_registry": "codex_app_host_command_registry_v0",
  "automation": {
    "heartbeat_prompt_mode": "thin",
    "requires_agent_identity": true,
    "scheduler_hint_source": "quota_should_run"
  },
  "privacy": {
    "raw_transcripts_accepted": false,
    "credentials_accepted": false,
    "public_local_paths_allowed": false
  },
  "fallbacks": ["loopx slash-commands", "loopx doctor", "loopx bootstrap-command-pack"]
}
```

## 开放实现问题

- 哪个 host API 拥有命令注册表安装与命令面板标签？
- 自动化安装应该是显式 host 动作、LoopX CLI helper，还是两者皆是？
- Host 应如何暴露 `scheduler_hint` 状态，使用户无需阅读 JSON 就能理解退避与重置？
- 在不制造第二个 LoopX 运行时的情况下，受控写入的最小工具界面是什么？
