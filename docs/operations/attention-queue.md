# Attention Queue


Attention queue 是 LoopX 的首屏 status 契约。它为 Codex goal tick、heartbeat
作业和未来的 UI 设计，用来快速回答一个问题：

> 哪个目标下一个需要关注，它在等谁？

`loopx status` 从三个 public-safe 面构建队列：

- registry 目标与 adapter 声明，
- 紧凑 run-history 索引，
- 公共/私有契约检查。

它不读取紧凑索引字段之外的私有 run payload，不检查项目特定日志，也不改动文件。

供 dashboard 和脚本使用的完整 JSON 形状见
[status-data-contract.md](../status-data-contract.md)。

## 命令

```bash
loopx status
loopx --format json status
```

该命令刻意保持通用。项目 adapter 决定自己的领域特定分类，但 status 把常见分类
映射到一个小的队列模型。

## 队列条目 Schema

```json
{
  "goal_id": "complex-project-main-control",
  "status": "ready_for_controller_opt_in",
  "lifecycle_phase": "controller_gated",
  "lifecycle_flags": ["controller_gated", "adapter_inspected"],
  "waiting_on": "user_or_controller",
  "severity": "action",
  "recommended_action": "先在 LoopX 完成 operator 判断；同意后项目 Agent 只执行 read-only map dry-run",
  "operator_question": "是否同意 `complex-project-main-control` 先执行 read-only map opt-in？",
  "agent_command": "loopx read-only-map --goal-id complex-project-main-control --dry-run",
  "quota": {
    "compute": 0.5,
    "window_hours": 24,
    "slot_minutes": 1,
    "allowed_slots": 720,
    "spent_slots": 0,
    "state": "operator_gate",
    "reason": "planned goal needs operator opt-in before spending agent turns"
  },
  "source": "latest_run"
}
```

字段：

- `goal_id`：来自 registry 或运行时的稳定 public-safe 目标 id。
- `status`：分类或派生状态。
- `lifecycle_phase`：用于 dashboard 分组的派生 state 交互阶段。
- `lifecycle_flags`：适用于最新目标状态的所有紧凑阶段。
- `waiting_on`：`user_or_controller`、`codex`、`external_evidence`、
  `monitor_signal` 或 `controller` 之一。
- `severity`：`high`、`action` 或 `watch`。
- `recommended_action`：来自 adapter 或 status 层的恰好一个面向用户的下一步行动。
- `operator_question`：可选的、要在 LoopX operator 视图显示的面向人类 gate。
  Dashboard 动作卡片应把它当作存在时的首要首屏问题。
- `agent_command`：可选的、目标 Agent 的命令或指令，仅在 operator gate 获批后生效。
- `quota`：可选的紧凑计算配额状态。它应在自动化再花一个 Agent turn 之前说明目标
  是否合格、受限、等待、暂停或 operator-gated。
- `user_todos`：可选的、给人类/operator 的 active-state 复选框摘要。
  Dashboard 消费方在存在时应在通用 gate 散文之前显示第一个未完成条目。
- `agent_todos`：可选的、给 Codex/项目 Agent 的 active-state 复选框摘要。
  它属于 status/CLI 与 handoff 上下文；不替代用户/controller gate。
- `source`：`contract`、`registry`、`run_history` 或 `latest_run`。

## 摘要计数器

队列摘要保持 controller handoff 可见：

- `needs_user_or_controller`：同时统计 `waiting_on=user_or_controller` 与
  `waiting_on=controller`。
- `needs_controller`：只统计等待目标 controller 或 adapter 连接的 Goal。
- `needs_codex`：统计准备好接受 Codex 行动的目标。
- `watching_external_evidence`：统计等待外部证据或指标的目标。
- `watching_monitor`：统计应保持可见但不要求立即 Codex 工作的 monitor-only 目标。

## 分类映射

Status 把这些视为用户/controller 关注：

- `needs_controller_opt_in`
- `needs_human_reward`
- `needs_user_relay`
- `ready_for_controller_opt_in`
- `ready_for_user_relay`

Status 把这些视为 Codex-ready 行动：

- `controller_opted_in_waiting_for_run`
- `design_next_experiment`
- `inspect_eval_result`
- `inspect_result`
- `needs_more_read_only_evidence`
- `needs_validation`
- `read_only_project_map`
- `run_validation`
- `state_refreshed`

`state_refreshed` 表示 controller 更新了 active state、ledger 或规划文档，
但没有运行项目 adapter。下一个 Codex 行动是检查刷新后的状态并继续一个有界进度片段。

Registry 条目可以用 `waiting_on`、`attention_status`、`recommended_action`、
`operator_question` 和 `next_handoff_condition` 显式覆盖首屏关注。
这让 controller 在最新 run 很新鲜但真实下一步仍是人类或目标 controller 决策时，
把已刷新目标留在 operator lane。该覆盖改变 status 与 quota 资格，
但不授予项目 Agent 执行权。如果 quota 后来报告 `safe_bypass_allowed=true`，
目标 heartbeat 可以处理 active state 中另一个有界的只读 steering 或分析条目，
但仍不得执行被 gate 的命令或任何 adapter/write/生产路径。

对复杂目标，避免把整个阅读队列编码进一个很长的 `recommended_action`。
把 `recommended_action` 保持为一个路由句，然后在 active state 里写显式复选框区块。
项目 Agent 应优先使用 CLI helper 而不是手编区块名：

```bash
loopx todo add \
  --goal-id <goal-id> \
  --role user \
  --task-class user_gate \
  --blocks-agent <agent-id> \
  --text "Read the short review packet before approving delivery."

loopx todo add \
  --goal-id <goal-id> \
  --role agent \
  --text "Build the next read-only worksheet after the user decision is recorded."
```

Helper 从 registry 解析目标的 active state，在需要时创建规范区块，
并避免重复的确切 todo 文本。生成的 Markdown 形状是：

```md
## User Todo / Owner Review Reading Queue

- [ ] Read the short review packet.
- [ ] Record the owner decision in the worksheet.

## Agent Todo

- [ ] Build the next read-only worksheet after the user decision is recorded.
```

Status 把这些复选框提升到 `user_todos` 和 `agent_todos`，因此 dashboard 关注
保持人类可读，Agent 面向的 status 保持可执行。

`read_only_project_map` 表示一个已连接的只读项目现在有了来自
`loopx read-only-map` 的标准 map run。下一个 Codex 行动应使用 map 的推荐行动，
或按需升级到项目特定 adapter。

Status 把 `blocked_by_safety` 视为高严重度的用户/controller 关注。

Status 把带 `await_` 或 `monitor_` 前缀的分类视为外部证据关注。

如果一个已连接目标还没有保存的 run，status 发出 `connected_without_run`，
这样下一个 Codex 行动就清楚了：运行第一个只读 adapter tick 并保存紧凑 run 记录。

如果一个计划中的高复杂度 read-only-map adapter 还没有保存 run，status 把它
保持在用户/controller 关注里，在 LoopX 中询问 operator gate，并把
`loopx read-only-map --goal-id <goal> --dry-run` 暴露为 `agent_command`。
该命令是执行上下文，不是批准。预览不追加任何内容；真正的 map run 仍等待
目标 controller 把 adapter 移到 `read-only-map-ready` 或 `connected-read-only`。
Agent 执行者应使用
`loopx --registry "$HOME/.codex/loopx/registry.global.json" quota should-run --goal-id <goal>`
作为硬计算 gate。当条目仍是 planned 时，该 guard 保持 `should_run=false`
并省略 `agent_command`，即使 status 为人类 operator 显示预览命令。
如果 guard 也报告 `safe_bypass_allowed=true`，Agent 可以做一个不依赖该
operator gate 的独立只读 steering 或分析步骤；在 gate 获批前不能运行预览命令。
在采取该 safe-bypass 步骤前，如果同一未决问题没有在最近可见线程中问过，
Agent 应向用户/controller 表露当前 gate。`quota should-run` 暴露
`gate_prompt`、`operator_question`、`user_todo_summary` 和 `agent_todo_summary`，
因此 Agent 可以问一个具体的中文问题并看到自己的安全后续清单，
而不是静默跳过或强迫用户手动检查 dashboard。
Markdown status 输出还在 `agent_command` 前打印 `operator_gate_dry_run` helper，
让 CLI 面向的 Agent 看到 operator gate 是任何项目 Agent handoff 之前的
用户拥有 dry-run 预览。

operator 回答那个 gate 后，用
`loopx operator-gate` 记录。已批准的 gate 产生 `operator_gate_approved`
并把下一个行动连同已批准的 `agent_command` 移交给 Codex；被拒绝或延迟的 gate
产生 `operator_gate_rejected` 或 `operator_gate_deferred`，并把目标留在
用户/controller lane，带记录的理由。

如果运行时包含一个不在 registry 中的可执行目标，status 发出
`unregistered_runtime_goal`。这是 controller 行动：要么把目标加入 registry
使它成为多项目面的一部分，要么归档运行时记录，使旧实验不像活跃工作。
只读的遗留记录，如 `await_*` 和 `monitor_*`，留在 run history 而不成为队列条目。

用 `loopx archive-runtime --goal-id <goal-id>` 预览清理一个过期的纯运行时目标。
该命令只在重跑 `--execute` 时移动文件。

如果契约检查失败，status 在项目目标前插入一个高严重度 `loopx-contract` 条目。

## 边界

每当目标 id 与推荐行动已脱敏时，队列才安全出现在公共文档或本地 UI。它不应包含：

- 本地绝对路径，
- 内部任务 id，
- 来自私有系统的原始指标值，
- 文档链接，
- 凭据，
- 原始提示或日志。

项目特定 adapter 可以在自己的仓库或运行时 payload 里保留更丰富的私有证据，
但 status 队列应保持紧凑且 public-safe。

生命周期阶段由 status 层派生，且应保持独立于 adapter 分类。一个队列条目可以保留
其领域特定 status，同时说明目标只是 connected、mapped、refreshed、
adapter-inspected、reward-judged，还是 controller-ready。
