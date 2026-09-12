# LoopX 受治理 Turn v0

状态：实验性协议与实现目标。

使用内置 Codex CLI host 的集成方应从 [单 Turn 快速上手](../../product/runtimes/codex-cli/loopx-turn-codex-cli-quickstart.md) 开始。本文档是协议与维护者参考，不是必需 onboarding。

`loopx_turn_v0` 定义 LoopX 如何治理一个由外部 agent-loop host（如 Codex CLI）执行的有界 Turn，而不把该 host 变成第二控制面。LoopX 对 goal 状态、todos、claims、gates、quota、scheduler 提示与紧凑证据保持权威。Host 拥有模型执行、工具与不透明的可恢复会话句柄。

协议是 host 中立的。Codex CLI 适配器是首个目标，但驱动器生命周期不得依赖 Codex 特定会话文件、transcript 格式或 benchmark 任务 schema。

## 心智模型

LoopX Turn 是四阶段控制环，而非另一个 agent 运行时：

```text
LoopX 决策 -> agent CLI 执行 -> 验证器证明 -> LoopX 提交
```

| 阶段 | Owner | 契约 |
| --- | --- | --- |
| 决策 | LoopX CLI | 从实时 goal、todo、gate、capability、quota 与节奏状态中选一个允许动作。 |
| 执行 | Host 适配器加 Codex CLI 等 agent CLI | 消费一个类型化请求、运行一个有界段落、发出一个类型化候选结果。 |
| 验证 | 独立任务特定命令或回调 | 检查真实工件、测试、远程状态或声明的只读后置条件。 |
| 提交 | LoopX CLI | 只在验证通过后写持久化状态并花费一个配额槽。 |

该分离让同一 Turn 契约治理编码、运维、数据、文档、知识维护与其他长程工作流。Agent CLI 仍负责模型与工具执行；它不成为 goal 状态或完成的权威。

## 通用 Agent CLI 快速上手

Agent CLI 不需要原生 LoopX 支持。它需要一个薄 host 适配器与一个独立验证器：

1. 运行 `loopx turn plan` 检查实时类型化决策，而不启动 host 或改变状态。
2. Host 适配器从 stdin 读取一个 `loopx_turn_host_request_v0` JSON 对象，在受治理工作区调用所选 agent CLI，并向 stdout 写恰好一个 `loopx_turn_host_result_v0` JSON 对象。
3. 验证器从 stdin 读取规范化 host 结果，并独立检查声称的后置条件。退出零意为通过；非零意为结果被拒绝。超时或验证器不可用为无定论。
4. `loopx turn run-once --execute` 只在类型化结果与独立验证都通过时执行 writeback 与配额花费。

下面适配器与验证器的可执行名是集成提供的占位符。它们是独立程序，因为执行器不得验证自己的完成主张。

```bash
loopx turn plan \
  --goal-id example-goal \
  --agent-id example-worker \
  --host generic-cli \
  --execution-mode isolated-headless

loopx turn run-once \
  --goal-id example-goal \
  --agent-id example-worker \
  --host generic-cli \
  --execution-mode isolated-headless \
  --project "$PWD" \
  --host-adapter-command-json '["./tools/turn-host-adapter","--agent-cli","trae","chat"]' \
  --validation-command-json '["./tools/verify-turn-postcondition"]' \
  --execute
```

除非它已经实现类型化 stdin/stdout 契约，否则不要直接把自由格式交互命令作为 `--host-adapter-command-json` 传入。对于 Codex CLI 或另一会话式 CLI，适配器在 Turn 请求/结果对象与该 CLI 的 prompt、会话与输出模型之间翻译。原始 transcript 文本、进程退出零与 host 自己的完成主张绝不构成足够验证。


### 任何 Agent CLI 的五个问题

接入 Codex CLI 或另一 host 前，回答这五个问题：

1. **如何无人值守运行？** 选择显式非交互命令与工作区。若 CLI 仅交互，它还不是 `isolated-headless` 适配器。
2. **如何返回一个类型化结果？** 优先原生输出 schema 或专用结果文件。不要把任意会话文本当作完成契约抓取。
3. **其恢复句柄是什么？** 把不透明句柄保存在本地适配器状态，按 `(goal_id, agent_id, todo_id)` 键控。绝不放入 LoopX 状态或公开证据。
4. **哪些失败可恢复？** 有界超时或传输丢失可以保留已观察会话。被拒绝的启动契约、不兼容 host 版本或缺会话使其失效，使下一 Turn 干净开始。
5. **什么独立证明工作？** 指名一个检查真实仓库、工件、服务回读、文档修订或其他后置条件、而不信任 agent CLI 自身主张的命令。

这产生一个可复用集成形状：

```text
TurnEnvelope
    -> host adapter -> agent CLI -> typed candidate result
    -> independent validator -> pass | repair | replan
    -> LoopX writeback -> one durable transition and one quota spend
```

薄适配器可以用该 host 中立算法实现：

```text
request = read_one_json(stdin)
todo = request.turn_envelope.action.selected_todo
session = load_local_session(goal_id, agent_id, todo.todo_id)
prompt = render_bounded_prompt(todo, request.result_contract, temporary_result_path)
invoke_agent_cli(prompt, workspace, session, explicit_timeout)
candidate = read_and_shape_temporary_result(temporary_result_path)
write_one_json(stdout, candidate with request.turn_key)
```

`render_bounded_prompt` 应告诉 agent CLI 只处理所选 todo，并把候选结果写到专用临时路径。适配器必须拒绝缺失或畸形结果，而非从散文猜测。提取 host 的不透明会话句柄后，它可以丢弃原始会话输出。LoopX 随后把候选交给独立验证器；适配器不自行宣布工作完成。

对于带原生结构化输出与恢复支持的 CLI，适配器主要是字段映射。对于所选命令只返回会话文本的 Trae 安装之类 CLI，包装器必须先建立专用类型化结果 channel；直接把 `trae chat` 作为适配器不够。检查已安装 CLI 的帮助并钉住合格命令形状，因为标志与无头行为可能随版本变化。

### 可重复 Codex CLI 资格

仓库包含一个可选端到端资格，创建临时 LoopX 项目与工作区。其默认模式使用无模型 Codex fixture，同时演练内置 host 适配器、独立验证器、状态 writeback、一次配额花费与幂等事务重放：

```bash
python3 examples/loopx-turn-codex-cli-e2e-smoke.py
```

只有本地 Codex 登录可用且意图做一次隔离模型调用时才使用真实模式：

```bash
python3 examples/loopx-turn-codex-cli-e2e-smoke.py \
  --real-codex-cli \
  --codex-model <compatible-model>
```

真实模式只发出紧凑 LoopX 资格摘要。LoopX 不把 prompt、transcript、stdout 或 stderr 复制进 fixture 状态，临时工作区与 LoopX 会话绑定被移除，一次性 goal 绝不同步进全局 registry。Codex CLI 可以按本地 Codex 策略保留其不透明 host 会话，使后续适配器 Turn 可以恢复它。紧凑 `codex_cli_model_requires_newer_codex` 失败是 host 兼容结果：事务必须显示零状态写入与零配额花费；重试前选择兼容模型或更新 Codex。

对于编码协作，验证器可以运行聚焦测试并检查预期 git diff。对于运维，它可以回读声明的资源状态。对于数据工作，它可以检查 schema 与有界质量断言。对于文档或知识维护，它可以验证目标修订与必需小节。这些是同一 Turn 编排契约上的不同验证器；它们不需要不同控制环。

## 权限边界

| 关注点 | 权限 |
| --- | --- |
| Goal、todo、claim、gate、quota 与节奏 | LoopX CLI 与 registry 支撑状态 |
| 会话创建、恢复、取消与工具执行 | 外部 host 适配器 |
| 仓库写隔离 | LoopX 工作区 guard 加仓库策略 |
| 验证 | 由 agent 或适配器选择的任务特定验证器 |
| 持久化结局与配额花费 | 验证后的 LoopX writeback |

Host 不得从状态散文推断不同动作。它消费一份新鲜 `loopx_turn_envelope_v0` 决策并保留其动作签名。完整 quota/status 详情仍可通过信封冷路径引用获得。

## Turn 生命周期

一个驱动器 tick 恰好有这些有序相位：

1. **唤醒**：解析 `goal_id`、已注册 `agent_id`、host 种类、显式执行模式、可用能力与可选不透明会话句柄。
2. **决策**：带观察到的能力运行实时 `quota should-run --turn-envelope`。Fixture 只在测试与影子重放中有效。
3. **路由**：用户 channel 需要动作、工作被限流、monitor 未变化或投递被禁止时，遵循信封而不调用 host。无配额花费地应用并确认仅 scheduler 变更。
4. **准备**：保留所选 todo 身份、契约要求时的 claim 或 lease，并在任何仓库写入前满足工作区 guard。
5. **执行**：只在适配器将声明 host 会话标记为合格时恢复它，或执行模式允许且创建新会话。给 host 薄任务正文加当前信封，并请求一个有界工作段落。
6. **验证**：分类 host 结果，并验证声称的工件或状态迁移。Host 进程退出零不是验证。
7. **写回**：更新或完成当前 todo，需要时创建 repair 或 successor todo，并用紧凑公开安全证据刷新状态。
8. **花费与调度**：只在验证 writeback 后花费一个配额槽，然后应用并确认最新 scheduler 提示。仅节奏工作不花费配额。

驱动器可以在任何相位后停止。停止必须返回类型化结果，且不得静默以不同执行模式继续。

### 只读 Journal 检查

维护者可以在不进入实时 Turn 生命周期的情况下检查一个既有围栏 journal：

```bash
loopx turn inspect-journal \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --turn-key <sha256:64-hex-digest> \
  --format markdown
```

命令解析规范运行时 journal 路径，在既有 journal 锁下读取它，并把 `interpret_turn_journal` 投影为 `loopx_turn_journal_inspection_v1`。它在 status 收集、quota 构建、scheduler 上下文、规划、host 调用、结算、花费或状态 writeback 之前分支。其 `effects` 字段因此始终为空列表。

退出零意为检查完成，包括 `decision` 为 `replay_blocked` 时。非零退出意为命令因选择器、文件、JSON 文档或 schema 无效而无法检查请求的 journal。该界面只作诊断证据：它不授予恢复、重试、结算、调度、花费或写入权限，也绝不是执行关卡。结算重放强制仍归 Turn 执行器所有。

版本 1 分离了版本 0 仅通过重放字段暴露的两个问题：

- `replay_legal` 说明终态 Journal 是否可以在无效果的情况下重新解释；它不是恢复许可。
- `recovery_decision` 是真实执行器对既有 Journal 消费的计划：`action`、`can_continue`、`resume_from`、`reinvoke_host`、类型化 `reason` 与实际参与的检查。

`journal_consistent` 还要求完整规范类型化结算身份。其 goal 与 agent 必须匹配 Journal、信封与请求的 owner；其 Turn 实例必须匹配事务；其绑定与 effect id 必须在结算 schema 下验证。Todo 绑定还必须匹配信封的权威所选 Todo，包括自适应主动作 Todo 覆盖。因此不匹配会在调用 Host 或任何结算 provider 之前产生阻塞恢复决策，即使已完成的相位前缀本来会恢复在持久化 writeback 或后续效果处。当前 Turn 驱动器不产生无 Todo 自主重规划事务 Journal，因此它不会在没有权威 Turn 血统的情况下推断这种绑定。

例如，带保存 Host Result 的 `in_progress` Journal 有 `replay_legal=false`，但可以从 `validation` 继续而无需另一次 Host 调用。`scheduler_action_required` 从 `scheduler_apply` 继续，不重复 Host、writeback 或配额花费。失败 Host Session 只在 `--retry-failed-turn` 显式时被评估，且必须通过当前 Session Binding 检查。可重试 Host 失败还携带无内容的 `loopx_turn_host_failure_v0` 记录。Journal 在 Host 调用前持久化尝试，TypeScript 恢复决策在声明有界预算后拒绝另一次调用。Backoff 是外层 scheduler 提示；`run-once` 从不在进程内睡眠，也不静默更换所选模型。悬挂的 prepare 效果仍归既有 provider 回读协议所有；恢复决策只记录该回读是下一必需检查，不声称通用 exactly-once 执行。

继续既有 Journal 时，`run-once` 持久化一条有界 `loopx_turn_recovery_audit_v0` 记录。其 `planned` 值是采纳的共享决策；其 `actual` 值区分 `started` 与 `finished`，只记录最终 Journal 状态、已完成相位 id 与本次恢复是否调用 Host。`inspect-journal` 把该记录暴露为 `last_recovery`。原始 Host 输出、Session 数据、effect 载荷、凭据与本地路径保持排除。

### 用户 Gate 安静等待

当用户拥有下一步且 agent lane 无可执行工作时，决策信封携带执行义务种类 `user_gate_quiet_wait`，`must_attempt_work=false` 与 `delivery_allowed=false`。这发生在至少一个开放用户动作 todo 存在、而 agent lane 不暴露首个可执行项、且没有 agent replan 义务优先时。

安静等待信封不是停住：

- host 不得调用模型、发送 prompt、带退避重试或消耗 heartbeat 花费；
- host 不得为正确等待在此义务上的驱动器报告停住、会话失败或死进程风险；
- 驱动器保持安静，直到投影的用户动作清除前沿或后续决策轮换义务（例如到 replan 或新鲜可运行 todo）。

该义务由控制面机器强制，而非 host 散文：host 从类型化义务读取 `must_attempt_work=false` 并保留安静等待，而不从状态文本重新推导动作。

对于物化结果，schema 有效 host 输出只是候选证据。调用方或适配器必须在 host 执行前选择独立任务/后置条件验证器。通用 CLI 接受可信 JSON argv 数组，把规范化 host 结果经 stdin 传入，绝不调用 shell，并丢弃验证器 stdout 与 stderr。缺失、失败或无定论验证器在 `validation_failed` 停止，记录类型化 `repair_required` 或 `replan_required` 恢复处置，且不能写状态或花费配额。类型化停止结果不需要任务验证，因为它们不产生物化 writeback。

独立回调验证器可以区分终态完成与验证的中间进展。`status=passed` 意为声明的终态后置条件成立，使用退出码 `0`。`status=progress` 意为有界、任务面向的后置条件被独立证明，但终态后置条件仍开放；它使用显式非零标记。两种状态都可以恰好提交一个 Turn 与一次配额花费。只有 `progress` 允许 host 适配器启动另一个 Turn，且只在预先声明的最大次数、共享总时间预算与无反馈继续策略下。每个其他验证器状态在 writeback 前失效关闭。

缺乏独立终态信号的适配器可以声明有界 `fixed-n` 终态策略。在该策略下，每次成功独立验证器调用证明进展，而只有最终配置成功的 Turn 满足序列终态后置条件。默认 `validator` 策略继续把退出码 `0` 解释为每 Turn 终态完成。在有界多 Turn 序列内，一个成功且同时证明持久化内容变更的 Turn 会先收到一次盲审 Turn，然后才序列终止；下一个成功的无变更 Turn 可以提前终止。该策略在公开安全 runner 前置条件中显式，绝不改变 benchmark 评分。

## Turn 输入

驱动器输入是既有契约的小型组合：

```json
{
  "schema_version": "loopx_turn_request_v0",
  "goal_id": "example-goal",
  "agent_id": "codex-worker",
  "host": {
    "kind": "codex_cli",
    "execution_mode": "interactive_visible",
    "session_handle": "opaque-local-handle"
  },
  "wake": {
    "reason": "scheduler_due",
    "turn_key": "stable-idempotency-key",
    "available_capabilities": ["shell", "filesystem_write"]
  },
  "decision": {
    "schema_version": "loopx_turn_envelope_v0",
    "action_signature": {
      "matches": true
    }
  }
}
```

`session_handle` 是本地适配器状态。它不得被提交、复制进 LoopX 公开状态或当作身份权限。稳定控制面身份是 `(goal_id, agent_id, selected_todo.todo_id)`。

适配器可以支持两种显式执行模式：

- `interactive_visible`：用户可见且可中断；绝不回退到隐藏执行。
- `isolated_headless`：隔离工作区中的显式选择的实验或 worker 模式；绝不声称保留交互 TUI。

模式选择是输入策略，不是重试启发式。

## 类型化结果

每次尝试的 tick 返回一个结果种类：

| 结果种类 | 含义 | 所需下一状态 |
| --- | --- | --- |
| `validated_progress` | 一个有界段落产出了验证证据。 | 更新当前 todo、刷新、花费一次。 |
| `validated_completion` | 当前 todo 的验收已满足。 | 恰好带一个类型化继续（`successor`、`active_goal` 或 `no_followup`）完成 todo、刷新、花费一次。 |
| `repair_required` | Todo 仍健全，但可恢复执行缺陷阻塞它。 | 保留或创建具体 repair todo；不标记成功。 |
| `replan_required` | 当前路由耗尽或不兼容，而 goal 验收缺口仍存在。 | 写有界 todo 增量或 vision replan 触发。 |
| `user_action_required` | 投影出具体用户决策、载荷或凭据动作。 | 用配置的操作员语言通知投影动作；不运行 host、不花费。 |
| `wait` | Quota、monitor、scheduler 或另一类型化等待契约适用。 | 保留状态、需要时应用节奏、不花费。 |
| `host_failure` | Host 无法启动、恢复或完成一个 Turn。 | 记录失败类别与重试或修复策略。 |
| `validation_failed` | Host 输出存在，但任务验证失败或无定论。 | 保留失败证据并路由到修复/replan。 |
| `writeback_failed` | 已验证工作无法持久化记录。 | 不花费；更多投递前先重试幂等 writeback。 |

`validated_completion` 只在 Turn 调用方提供显式 Todo 生命周期适配器时被准入。独立验证后，适配器必须通过既有 Todo 生命周期授权并完成所选 Todo，然后为该同一 Todo 返回紧凑结局：链接 successors、授权 `no_followup` 记录或 `active_goal` 继续。持久化 Turn journal 在配额花费前记录该结局。仅 Todo 完成绝不终止 goal；新鲜决策拥有 successor 选择与 goal 终止。

每个新完成的 Todo 显式持久化 `completion_continuation` 与不透明完成身份。该值必须与其持久化关系一致：`successor` 要求至少一个 `successor_todo_id`，`no_followup` 要求 `no_followup=true`，`active_goal` 两者都不要求。省略该字段的已完成记录不被解释为 `active_goal`；它失效关闭，直到 agent 通过重放 `loopx todo complete` 显式修复。唯一的后完成转换是窄 #3261 恢复接缝：在原 quota 绑定 `completion_turn_key` 内，匹配的 writeback 与花费回执存在后，显式 `active_goal` 可以升级为 `no_followup`。恢复记录 `completion_recovery=same_turn_terminal_closeout`；它不能跨 Turn，也不能替换 successor。配额 Turn 之外做出的完成则持久化 TS 派生的 `local_completion_*` 身份。当严格 `refresh-state` 拒绝后来证明只缺 Todo 生命周期结算时，它可以通过 `--completion-identity-key` 投影该精确键。完成围栏只为带 `active_goal`、无 successor、且授权生命周期 actor 的匹配已完成 Todo 接受这个不同 `lifecycle_reentry_terminal_closeout`。它不把本地键重新解释为配额回执，也不允许任意跨 Turn 终态重放。

`repair_required` 与 `replan_required` 有别。Repair 保留当前任务意图。Replan 改变可运行 todo 集或路由，因为既有任务不再推进 goal。以下任一为真时要求 replan：

- 无可运行 todo，而活动 vision 仍有验收缺口；
- 所选 todo 终态、过期或与观察到的 host 能力不兼容；
- 已验证负面证据使当前路由无效；或
- 两次合格 Turn 经同一路由无物化进展。

驱动器不得仅因一个 todo 结束而终止。Goal 终止要求 goal 验收证据、显式用户停止、或带具体投影动作的类型化阻塞状态。

## 可恢复失败类别

| 失败类别 | 驱动器行为 |
| --- | --- |
| `auth_required` | 为具体凭据动作停止；绝不读取或上传凭据。 |
| `session_unavailable` | 返回 `host_failure`；只有所选模式允许时才重试恢复或启动新会话。 |
| `capability_missing` | 用观察到的能力重跑决策，使用能力修复路由，而非捏造用户 gate。 |
| `workspace_guard_denied` | 写入前修复或迁移工作区。 |
| `executor_timeout` 或 `transport_lost` | 返回带重试元数据的 `host_failure`；不推断完成。 |
| `provider_capacity`、`provider_overloaded` 或 `rate_limited` | 优先精确结构化 provider 码，否则使用有界适配器局部诊断回退。只保留类型化类别、精确尝试、同配置策略、有界指数退避与最大尝试数。绝不持久化 provider 散文或静默选择另一模型。 |
| `quota_exhausted` | 把硬计划、计费或包含用量耗尽视为不可重试修复。不要把它坍缩成限时速率限制。 |
| `result_missing` | 返回 `validation_failed`；无类型化结果的进程退出是无定论。 |
| `validation_failed` | 保留紧凑负面证据并选择修复或 replan。 |
| `writeback_failed` | 重试幂等 writeback；绝不先花费。 |
| `scheduler_apply_failed` | 保留已完成 writeback、记录节奏失败、无需投递花费地重试 scheduler 控制。 |

结构化失败判别是失效关闭的。已知 `error.code` 胜过 HTTP 状态与散文。未知非空码变成 `unknown` 并路由到修复；它不得从其消息重新解释。HTTP 429 只在无更具体 provider 码时是有界 `rate_limited` 信号，因此 `insufficient_quota` 响应即使以 HTTP 429 传输也保持不可重试。当前 `codex exec --json` 版本暴露仅消息错误事件，因此诊断匹配仍是该适配器的实时兼容路径；结构化 Responses、app-server 与 JSON-RPC 信封被接受为前向兼容输入，但不声称是当前 exec JSONL 契约发出的字段。

会话恢复是失效关闭的：

| Host 观察 | 会话处置 | 下一 Turn |
| --- | --- | --- |
| 返回类型化结果 | 保持不透明会话合格。 | 同一 todo 仍被选中时恢复。 |
| 观察会话后超时或传输丢失 | 保持合格，但不推断进展。 | 重试副效应安全 host 相位。 |
| 不兼容 host 版本或被拒绝的启动/输出契约 | 使其失效。 | 修复后启动新会话。 |
| Host 报告会话缺失 | 使其失效。 | 策略仍允许执行时启动新会话。 |
| 观察任何会话前失败 | 不存储。 | 重新决策，然后只在允许时全新开始。 |

会话资格是恢复元数据，不是工作发生的证据。它绝不绕过新鲜 Turn 决策、任务 lease、独立验证或 writeback 顺序。

## 适配器要求

外部 host 适配器必须提供：

- 可以传给 `--available-capability` 的能力发现；
- 启动、恢复、取消与有界超时操作；
- 与原始 transcript 输出分离的公开安全类型化结果 channel；
- 显式执行模式与无静默模式回退；
- 除 host 恢复外无权限的不透明本地会话句柄；
- 注入交互会话前的可见性与空闲证明；以及
- 到上述结果与失败类别的确定性失败映射。

最小有用适配器只有三个职责：把类型化请求翻译为一次有界 agent-CLI 调用、host 支持时保留不透明本地恢复句柄、把最终结局翻译为一种类型化候选结果。它不得解析 LoopX 状态散文、写 LoopX 状态、花费配额或验证自己的工作。

驱动器可以丢弃原始 stdout 与 stderr，但不得把它们的缺失当作类型化结果。原始 prompt、transcript、benchmark 任务文本、verifier 尾部、凭据与本地会话路径保持在已提交 fixtures 与 LoopX 状态之外。

## 提升关卡

本协议只有在以下全部成立时保持实验性：

1. 影子重放在投递、用户 gate、monitor 等待、能力修复、工作区修复、replan、阻塞与限流状态中保留实时 TurnEnvelope 动作签名；
2. 一个真实 host 适配器证明启动/恢复、类型化结果、验证、幂等 writeback、花费顺序与 scheduler 确认；
3. 交互与隔离无头模式失效关闭而不互切；
4. 受控 benchmark dogfood 运行显示来源、预算、并发与无反馈边界保持可比；并且
5. 回滚可以禁用适配器，同时保持普通 LoopX CLI 状态与宿主 heartbeat 运行完好。

本协议不授权 benchmark 启动、leaderboard 提交、生产写入、凭据处理或默认替换宿主。
