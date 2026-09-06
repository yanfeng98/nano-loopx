# Heartbeat 自动化提示

> [English](heartbeat-automation-prompt.md)

这是 Codex App heartbeat 自动化的公开复制粘贴模板，它推进一个 LoopX 目标，
而不用把计算策略藏在定时器里。

定时器只唤醒执行者。LoopX 决定该唤醒是否应花费 delivery 计算。

## 两层提示

把 Codex App 可见目标文本与 heartbeat 自动化任务体保持为两独立层：

- **可见目标文本**：短且人类可扫描，例如
  `按 ACTIVE_GOAL_STATE.md，基于 LoopX 体系，推进项目`.
- **Heartbeat 自动化任务体**：由 `loopx heartbeat-prompt` 生成，
  除 `goal_id`、可选的 active-state 覆盖和少量项目特定边界规则外，
  在各项目间几乎相同。
- **紧凑 heartbeat 任务体**：由 `loopx heartbeat-prompt --compact` 生成，
  当上下文压力重要时优先用于活跃 Codex App 自动化。它把 guard、gate、
  blocker-push、推荐、steering-audit、writeback、refresh 与 spend 规则保留在
  已安装提示里，同时把罕见边缘分支指回扩展生命周期契约。
- **精简已安装任务体**：由 `loopx heartbeat-prompt --brief` 生成，
  当已有自动化提示负担过重时优先使用。它是薄调度器：在已安装提示里只保留
  目标身份、预检、quota guard、硬 skip/monitor/spend 规则与紧凑契约接口。
  按需用紧凑契约、top-3 status 队列或 handoff packet 拉取额外细节，
  而不是把一切粘进每次 heartbeat。
- **薄调度器任务体**：由 `loopx heartbeat-prompt --thin` 生成，
  当目标 Codex Agent 被信任在唤醒时自检 LoopX registry/全局 quota 真相、
  active state、status/run history、repo 状态与项目信号时，作为本地机器默认。
  它不把命令分支粘贴进自动化提示。普通 turn 使用 CLI `interaction_contract`；
  生命周期/registry 用 `loopx-project`，运行时/投影漂移用 `loopx-self-repair`。
  CLI payload 保持运行时真相源。这让 Codex 线程成为可替换 worker，
  并把持久任务真相留在 LoopX。

不要把完整生命周期协议粘贴进可见目标文本，也不要用"advance TODO"这样的短目标文本
作为循环自动化任务体。短文本指明目标；生成的 task body 强制 quota、gate、
steering audit、writeback、refresh 与 spend 记账。

Ark Managed Agent 不是自动化 profile。它的集成使用一个传输中立的 goal 提示，
并让目标运行时拥有内部迭代；参见 host 集成协议，而不是改编本循环自动化契约。

对 Codex App，生成的 quota 命令携带紧凑显式运行时 profile
`--runtime-profile codex_app_heartbeat`（生成的命令使用等效紧凑别名
`--codex-app`）。提示不把三个 scheduler 归属字段复述为散文。其他 host 生成
它们真实的 typed 执行上下文，而不是靠省略继承 App cadence。
不要手工编辑每个项目的生命周期分支到一条自动化提示里。项目特定行为属于
LoopX registry、active-state 区块、adapter 输出或窄边界规则。如果一条生命周期
规则通用有用，把它加入 `loopx heartbeat-prompt` 与其 smoke 契约，
让每个项目都继承。可执行与仅 watch 的 Agent 后续应通过 todo CLI 注册
（`--task-class` 与可选 `--action-kind`），再由 `quota should-run` 投影；
不应编码为 benchmark 或项目特定提示文本。
当生成的提示与已安装 skill 不一致时，worker 应首先信任当前 CLI
`interaction_contract`，然后把 skill 当作操作手册，提示只当作引导。
在该契约内，worker 应执行 `agent_channel.primary_action`。可选的
`agent_channel.resolution_trace` 用于调试路线选择与漂移；不应把它当作
另一个要运行的动作，或当作改写 active-state `Next Action` 的权限。

可以从 CLI 生成任务体。对已连接目标，优先 registry 支撑的形式，
使已安装自动化不硬编码可能漂移的状态文件路径：

```bash
loopx heartbeat-prompt --goal-id <GOAL_ID>
```

如果你在测试一个分离状态文件或一个尚未连接进 registry 的目标，传显式覆盖：

```bash
loopx heartbeat-prompt \
  --goal-id <GOAL_ID> \
  --active-state <ACTIVE_GOAL_STATE_PATH>
```

对循环 App heartbeat，默认任务体是薄本地调度器。在完整生命周期已评审后，
当已安装提示应内联更多生命周期细节时，使用紧凑任务体：

```bash
loopx heartbeat-prompt \
  --goal-id <GOAL_ID> \
  --compact
```

扩展提示保持为显式审计源：

```bash
loopx heartbeat-prompt \
  --goal-id <GOAL_ID> \
  --full
```

薄提示是已安装默认。它让每 tick 上下文保持小，并期望受信任 Agent 在行动前
拉取当前 LoopX 状态。紧凑提示是更重的内联生命周期任务体。

当多个 Agent 共享同一项目控制面时，先在目标上注册 public-safe Agent id，
然后给每个自动化显式身份与自然语言作用域：

```bash
loopx configure-goal \
  --goal-id <GOAL_ID> \
  --registered-agent codex-main-control \
  --registered-agent codex-side-bypass \
  --agent-model peer_v1 \
  --execute
```

```bash
loopx heartbeat-prompt \
  --goal-id <GOAL_ID> \
  --compact \
  --agent-id codex-main-control \
  --agent-scope "benchmark readiness, benchmark execution, and benchmark writeback"
```

对另一个 peer，用不同 id 与不相交作用域：

```bash
loopx heartbeat-prompt \
  --goal-id <GOAL_ID> \
  --compact \
  --agent-id codex-side-bypass \
  --agent-scope "control-plane coordination and todo claim ergonomics" \
  --agent-scope "do not take benchmark execution todos unless reassigned"
```

生成的任务体告诉 Agent 只声明作用域内 todos：
`loopx todo claim --claimed-by <agent-id>`。`--agent-scope` 需要 `--agent-id`，
且 CLI 只在 Agent id 为该目标注册时接受它。作用域留在自动化提示或 handoff 里；
todo 元数据只记录软 `claimed_by` owner。已注册身份是对等 peer。功能性 profile
角色是建议性的，而工作区隔离与延续行为来自所选任务、目标策略与 typed 延续策略。
生成的带作用域 heartbeat 命令把同一 `--agent-id` 传给 `quota should-run` 与
`quota spend-slot`，所以工作区 guard 与 quota 记账评估同一身份。

Host 能力是声明，不是权限授予。当所选 Codex App、CLI 或外部 launcher 已有其
todos 所需的能力时，在生成 heartbeat 时声明它：

```bash
loopx heartbeat-prompt \
  --goal-id <GOAL_ID> \
  --thin \
  --agent-id <AGENT_ID> \
  --available-capability network \
  --available-capability external_evidence_poll
```

生成的 quota guard 与 spend 命令保留相同声明。不要仅为绕过 gate 而声明凭据、
生产访问或另一个能力；launcher 必须真正提供它。

当薄提示在无显式声明时生成，它仍告诉运行时 worker 用 `--available-capability`
投影实际存在的非基础能力。这防止观察到的网络或轮询能力变成虚假用户 gate，
而不猜测 host 没有的能力。显式生成器参数对安装自动化时已知能力的 hosts 仍更受推荐。

- 对小的、AGENTS 合格的验证变更，self-merge 并用
  `--self-merged --evidence "<commit and validation summary>"` 完成 todo；
- 对独立延续，创建 `--next-agent-todo`，可选用 `--next-claimed-by` 选一个
  已注册 peer；
- 需要独立评审时，用 `--next-action-kind review` 加普通 `independent_handoff`；
  仅当作者不得重新声明未声明 successor 时，添加 `--next-excluded-agent <author>`；
- 当一个验证过的 PR 只差人类评审时，用 `--next-user-todo "<review action>"` 与
  `--next-user-task-class user_action` 保持提醒非阻塞，然后在同一完成中创建
  下一个可运行 agent todo。当必须观察 merge/readback 时，为 PR 生命周期添加
  单独 `continuous_monitor`。不要把评审延迟变成 gate；
- `user_gate` 只用于确切权威边界，例如批准把聚合分支 merge 进 `main`、
  发布、启动 benchmark 或执行受保护动作；
- 当工作被阻塞且没有有效 successor 时，把 todo 留在当前 peer 并写具体 blocker，
  而不是发明层级路线。

一旦目标有 `coordination.registered_agents`，不带 `--agent-id` 的提示生成会
fail closed。那是过期 Codex App 自动化的轻量迁移信号：下一次刷新尝试会表露一个
具体身份/作用域升级命令，而不是返回遗留的无作用域提示。`quota should-run`
为执行者安全遵循同一规则：无作用域调用返回
`automation_prompt_upgrade.required=true`、`blocks_should_run=true` 与
`should_run=false`，而不是允许 delivery。对层级时代注册表，`quota should-run`
与 `upgrade-plan` 返回一个稳定迁移 id、每个已注册 peer 一个 heartbeat 命令，
与一个完成命令。host 更新可用该幂等键重试；完成命令原子记录迁移一次，
后续 quota 检查不再投影它。无 `coordination.registered_agents` 的注册表必须先
注册 peer 身份，才能生成作用域提示。

如果紧凑任务体的安装自动化仍太重，生成精简任务体：

```bash
loopx heartbeat-prompt \
  --goal-id <GOAL_ID> \
  --brief
```

只在目标 Agent 有 LoopX CLI 访问时使用精简任务体。它刻意很小，
并把紧凑/完整生命周期契约当作 skill 风格接口，Agent 在 quota 说真实工作可运行
或边缘分支含糊时去取。

对最薄的本地默认，生成调度器任务体：

```bash
loopx heartbeat-prompt \
  --goal-id <GOAL_ID> \
  --thin
```

只在期望 controller 每次唤醒都做新鲜 registry/quota/state/status/repo 检查时使用
薄任务体。它应保持项目无关；如果一个行为需要在 worker 间被记住，
把它写进 active state、run history、registry 或生成的提示契约，
而不是手工编辑自动化任务体。

`loopx heartbeat-prompt --format json` 为所选模式发出一个 `interface_budget`
对象。它报告渲染提示的 `char_count`、`line_count`、归一化 `budget_char_count`、
`max_chars` 与 `within_budget`。`upgrade-plan --format json` 在每个生成提示内
携带同一预算摘要，所以本地默认晋升检查能标记提示膨胀，而无需解析散文
或依赖聊天线程。

`upgrade-plan --format json` 在已安装提示的正文通过本地 Codex App 自动化记录
或显式清单可用时，还为其携带紧凑 `prompt_policy_audit`。审计不回显提示正文。
它只报告警告种类，如 generic `should_run=false` 硬停止出现在 safe-bypass
处理前、嵌入的项目策略块或 pinned 的 `--active-state` 参数。任何警告都应视为
升级工作：从当前 CLI 契约重新生成已安装 heartbeat，并把项目特定策略留在
registry/state/status/review-packet payload 里。

对灰度上线，通过 `loopx-canary` 生成精简任务体并传 `--cli-bin loopx-canary`，
使只有所选 goal controller 使用活 checkout：

```bash
loopx-canary heartbeat-prompt \
  --brief \
  --cli-bin loopx-canary \
  --goal-id <GOAL_ID>
```

## 模板

安装自动化前替换占位符：

- `<ACTIVE_GOAL_STATE_PATH>`：分离状态文件的可选覆盖。对已连接目标省略它，
  让 CLI 解析 registry goal `state_file`。
- `<GOAL_ID>`：稳定 LoopX 目标 id。
- `<MATERIAL_QUEUE_RULE>`：可选项目特定规则，如"除非用户明确要求，否则不要
  消费学习材料队列"。

```text
推进由 <ACTIVE_GOAL_STATE_PATH> 描述的目标。

通用 LoopX 生命周期。把项目特定分支留在自动化提示之外。把本地策略放入
registry、active-state 区块、adapter 输出、quota should-run.goal_boundary
或边界规则；如果确实需要一条生命周期规则，更新 loopx heartbeat-prompt，
让所有项目继承它。

在花 delivery 计算之前，先让 LoopX CLI 在本自动化 shell 中可用，然后运行
quota guard：

export PATH="$HOME/.local/bin:$PATH"
install_script="$HOME/loopx/scripts/install-local.sh"
if ! command -v loopx >/dev/null 2>&1; then
  if [ -x "$install_script" ]; then
    "$install_script"
    export PATH="$HOME/.local/bin:$PATH"
  else
    echo "loopx is not on PATH; clone the LoopX repo and run scripts/install-local.sh" >&2
    exit 1
  fi
fi
loopx doctor >/dev/null
loopx --format json --registry "$HOME/.codex/loopx/registry.global.json" quota should-run --goal-id <GOAL_ID> --runtime-profile codex_app_heartbeat --turn-instance-id "${LOOPX_TURN:?}"

如果该预检仍失败，本轮不要做实现工作、adapter 工作、文件编辑、研究、
项目探索或 quota spend。用一个安静 heartbeat DONT_NOTIFY 回复并带上确切的
预检失败原因。

如果结果显示 should_run=false：

- 如果 payload 说 state=operator_gate，把该 gate 当作用户/controller 交互，
  而不是静默 skip。从 payload 读取 gate_prompt、operator_question、
  recommended_action、next_handoff_condition、missing_gates、user_todo_summary
  与 agent_todo_summary。如果同一未决 gate 最近没有在可见线程中问过，
  返回 heartbeat NOTIFY，带一句简洁的中文问题，列出该 gate 与期望的回复格式。
  把 `interaction_contract.user_channel.notify` 当作最终通知信号。当它是
  `NOTIFY` 时，即使 `action_required=false`、`user_todo_summary.open_count=0`
  且 `non_blocking=true`，也要点名已投影的具体 `actions`、todos 或问题；
  non-blocking 表示 Agent 可以继续独立工作，而不是用户动作被静默。
  永远不要说"只是 owner gate"。如果用户面向的必需条目没有被投影，
  说"具体 user todo 未投影，需修复 LoopX 状态投影"；这种情况永远不要说
  "no new user action"。只有当 `notify=DONT_NOTIFY`、`action_required=false`
  且 `open_count=0` 时，heartbeat 才可说"无用户待办/无需通知"或保持安静。
  询问期间不要执行 agent_command、adapter 工作、write-control、生产动作或
  被 gate 的路径。
- 如果 payload 说 notify_user_on_open_todo=true，把现有开放 user_todo_summary
  当作 blocker-push 机会，而不是静默 skip。这对 state=focus_wait、state=waiting
  与 waiting_on=external_evidence 尤其重要，一个简短的 user/owner 回答
  就能解锁安静项目或停止无意义的重复轮询。如果 payload 显式包含
  open_todo_notification_policy=repeat_until_resolved，返回 heartbeat NOTIFY
  直到用户 todo 完成、延迟或被替换。当
  user_gate_notification_cooldown.notification_suppressed=true 时，
  保留待决 gate，但在其有界提醒窗口或实质 gate/host 变化前返回安静
  DONT_NOTIFY。否则，如果同一 blocker 诉求最近没有在可见线程中出现过，
  返回 heartbeat NOTIFY，带一句简洁中文诉求，最多列三个 first_open_items、
  open_todo_notify_reason 与期望回复格式：done、defer/not now，
  或新的证据链接/日期/结论。该 blocker-push turn 不要做实现工作、adapter 工作、
  文件编辑、研究、项目探索或 quota spend。如果同一非 monitor blocker 最近
  已被表露，返回安静 DONT_NOTIFY 跳过理由且不追加 quota spend。
- 如果 payload 也说 safe_bypass_allowed=true 且同一 gate 已表露过，该 gate
  只阻塞被 gate 的 delivery 路径。你仍可读取 active state 并做恰好一个
  Priority Stack 里的有界 safe-bypass 步骤，例如只读 steering 分析、文档，
  或另一个不依赖该 gate 的 P0/P1 条目。如果你做了 safe-bypass 步骤，
  验证它、写回 progress/critic/next action、刷新可问责进度、追加恰好一个
  spend 事件并紧凑报告。如果 `interaction_contract.user_channel.notify=NOTIFY`
  或 `user_todo_summary.open_count > 0`，具体包含投影的用户动作或 todos，
  并不要说没有"no new user action"。如果 agent_todo_summary.open_count > 0，
  报告还应点名它下一个可执行的安全 agent todo。如果没有有用的 safe-bypass
  步骤，紧凑报告待决 gate，而不是做工作。
- 给每个 heartbeat 一个稳定 turn id：把它的 `<current_time_iso>` 拷进
  `LOOPX_TURN`；同一 heartbeat 的 guard 重试复用该 id。`quota should-run`
  为每个 turn 提交一个幂等收据。如果 effective_action=monitor_quiet_skip，
  同一 guard 幂等追加无 spend 停滞观察并返回后续决策。不要追加第二个手动
  monitor 轮询。如果仍是 monitor-only，返回安静 DONT_NOTIFY：不做 delivery
  编辑、不 spend。保持自动化激活：未变化的 monitor-only 收据不是自停信号。
  如果 guard 报告 autonomous_replan_required 或其他硬 replan 契约，遵循该契约。
- 如果 waiting_on=external_evidence 或 state=waiting，且本自动化显式是 monitor，
  运行最多一次有界只读观察轮询，使用 active state、recommended_action 或
  goal_boundary.next_probe 点名的项目批准 status/log/metric/marker 面。
  未变化证据：安静 DONT_NOTIFY，不编辑、不 spend。新的 eval/fail/complete/
  blocker/approval/CI/deploy/data 证据：报告，只写回允许的 canonical
  state/board/ledger，需要时添加 todos，然后验证后 spend 一次。仍不要
  启动/停止/重启/同步/设计代码或变更生产，除非 should_run=true 或用户显式授权。
- 否则，本轮不要做实现工作、adapter 工作、文件编辑、研究或项目探索。
  返回安静 heartbeat DONT_NOTIFY 回复并带跳过理由。

如果结果显示 should_run=true：

1. 读取 active state、Priority Stack、最近进度与 critic。
   当你检查当前 LoopX 路由时，使用当前 status 队列：attention_queue.items
   与每个条目的 project_asset 是 owner、gate、等待方与下一行动的权威。
   如果 project_asset 缺失或为 legacy/raw fallback，原始队列字段不具
   owner/gate/stop 权威。把 run_history.latest_runs 当作证据与下钻即可；
   它可能受 status 命令上限或过滤器限制，所以不要只从 latest runs 判断
   gate 是否待决或已批准。还要检查 goal_boundary 并守卫 user_todo_summary。
   只有当开放 user/owner todo 属于本目标的 guard payload 或当前 project asset
   且阻塞所选路径时才停下来；然后用上面的 blocker-push 模式。在
   `attention_queue.items` 中找到的依赖或兄弟目标 todos 应记录为依赖 blocker；
   它们不得消耗整个合格 turn；当存在时为本目标选一个独立于 gate 的
   P0/P1/P2 候选。
   如果 `effective_action=outcome_floor_recovery` 或
   `recovery_delivery_allowed=true` 或 `safe_bypass_kind=outcome_floor_recovery`，
   产出 `must_advance` 点名的必需 ranker/cross-domain 证据产物，
   或写回具体 blocker。不要落入普通 delivery、表面传播或仅合成链。
   在发明本地自动化行为之前，还要从 quota payload 读取 execution_obligation
   与 heartbeat_recommendation。heartbeat_recommendation.notify 只是用户通知
   策略，不是执行 gate。如果 execution_obligation.must_attempt_work=true，
   即使 notify=DONT_NOTIFY 也尝试一个有界片段；quiet no-op 需要
   execution_obligation.must_attempt_work=false 且没有
   notify_user_on_open_todo=true 的 blocker-push 通知，例如经核实的
   mapped_noop_if_unchanged turn。如果 heartbeat_recommendation 说
   recommended_mode=run_first_read_only_map，就把它给的命令当作真实只读映射
   运行一次，而不是另一次 dry-run，然后验证/保存 read_only_project_map 结果、
   刷新可问责进度、追加恰好一个 heartbeat spend、按需同步 state 并 NOTIFY。
   如果它说 recommended_mode=mapped_noop_if_unchanged 且
   stop_if_unchanged=true，且你没有发现新用户指令、owner 证据、agent todo、
   过期来源或安全 handoff，返回安静 `DONT_NOTIFY`：不运行、不编辑、不 spend。
   检查 `delivery_batch_scale`、`delivery_outcome`、
   `post_handoff_outcome_gap_streak` 与 `handoff_delivery_contract`；
   对 repeated-small 或 surface-only 循环，遵循该契约。
2. 在选工作前跑一个简短 steering audit：有用时列出至少三个、跨越不同
   P0/P1/P2 lane 的合理 next-action 候选；如果同一主题已消耗多个最近 delivery
   切片，应用延续检查并说明为何继续仍赢；保持 compute quota 与 focus quota
   分离；记录任何不应被遗忘的落选高价值候选。包含产品瓶颈视角：询问核心目标
   当前是否被用户体验、Agent 能力、证据质量、adapter 就绪或优先级规则缺口
   卡住，并在应胜过最近本地 TODO 时提升一个具体瓶颈候选。
   计划/top todo/路线变更需要 todo/Next Action 写回或无写回理由。
3. 在选 delivery 工作前运行 no-progress 自修复检查。先遵循 `quota should-run`
   返回的任何机器可读 `autonomous_replan_obligation` 或
   `execution_obligation.must_attempt_work=true`；即使 heartbeat 提示很短，
   该硬契约也覆盖 quiet no-op。检查最近 active-state 进度与公共 run history
   是否有连续合格 heartbeat turns。只有当一个 turn 没有产出实质产物、没有
   adapter 或实现进度、没有新 gate 或用户决策、没有新验证信号，
   且只有重复 status/brief-check/compact-checkpoint 状态编辑时，才把它计为
   no-progress。把 `quota_monitor_poll` 事件当作该 guard 的无 spend 停滞证据。
   如果 2 个连续合格 heartbeat 是 no-progress 循环，在另一次 quiet no-op 前
   跑一个（一次）有界自修复/replan 片段。只有该修复路径自己再卡 2 个合格 turn
   时才删除或暂停自动化，不要为自取消 turn 追加 quota spend，
   并返回 NOTIFY 说明该自动化因空转无进展被取消。
4. 从该 audit 选一个有界、可验证的进度片段。当写作用域清楚且验证显式时，
   它可以是跨相关实现、测试、文档与状态写回文件的连贯批量；
   不应被硬塞成微小的单文件步骤。
5. 只做该片段。存在 goal_boundary 时留在其内，并保持公共/私有边界完整。
   public-safe 仓库发布本身不是 operator gate：对常规公共项目工作，commit、push
   与 PR 创建可以在验证与干净的公共/私有边界扫描后自主进行。
   只为私有或公司内部材料、凭据、破坏性 git 操作、生产动作，
   或明确要求评审的仓库规则停下来并表露用户/controller gate。
6. 运行最小的有用验证。
7. 把变更文件、验证、critic 与下一动作写回 active state。如果出现 user/owner
   todo，不要把它藏进散文：
   `loopx todo add --goal-id <GOAL_ID> --role user --task-class user_gate --blocks-agent <agent-id>`
   或 `loopx todo add --goal-id <GOAL_ID> --role user --task-class user_action`。

   项目 Agent 后续工作用 `--role agent`。
   对非平凡功能切片，只在添加 successor todo 后完成当前 todo，
   或包含紧凑无后续理由。
   完整字段契约见 LoopX checkout 里的 `docs/project-agent-todo-contract.md`。
8. 验证与其他 writeback 完成后，在 spend 前记录本 turn 的可问责 delivery：

   loopx refresh-state --goal-id <GOAL_ID> \
     --classification <PUBLIC_SAFE_PROGRESS_CLASSIFICATION> \
     --delivery-batch-scale <ACTUAL_DELIVERY_BATCH_SCALE> \
     --delivery-outcome <ACTUAL_DELIVERY_OUTCOME>

   三个占位符都必须替换为本验证 turn 证明的值。绝不把更小或准备性工作默认、
   拔高为 `multi_surface` / `outcome_progress`。
   该 refresh 是 `quota spend-slot` 消费的因果 delivery 记录。
   纯 state-only refresh 是 quota 中性且不能替代它。然后，
   对分钟级 heartbeat，花一个槽位：

   loopx --format json --registry "$HOME/.codex/loopx/registry.global.json" quota spend-slot --goal-id <GOAL_ID> --todo-id <SELECTED_TODO_ID> --slots 1 --source heartbeat --execute

   按渲染原样运行一次；不要管道/过滤/重试。如果 spend 输出含糊，
   用只读 quota status 核对；绝不重跑。

   如果自动化保留更粗的固定间隔，把 `--slots` 设为该完成 turn 消耗的
   scheduler 分钟数。

   不要为安静 should_run=false 跳过、预检失败、纯 dry-run 预览或重复记账尝试
   追加 spend。如果 should_run=false 但 safe_bypass_allowed=true 且你实际完成了
   一个有界 safe-bypass 步骤，在验证/writeback 后也追加一次该 spend 事件。

9. 如果 dashboard 或 controller 在 spend 后需要仅状态更新，运行：

   loopx refresh-state --goal-id <GOAL_ID>

   spend 后不要再发出另一个可问责进度刷新；那会创建一条新的未 spend delivery 记录。

10. 返回紧凑最终报告。只对有意义用户可见性用 heartbeat NOTIFY，例如已提交
    artifact、用户 gate、真实 blocker 或自动化自停。其他情况用 DONT_NOTIFY。

<MATERIAL_QUEUE_RULE>
当前 Codex 会话已被信任时，不要请求权限。
```

## 最小用户面向形式

在 Codex App 中创建 heartbeat 时，保持可见指令简短，并把生命周期放进自动化
任务体。默认上手 cadence 从 3 分钟开始；在第一次 guard 后，遵循
`quota should-run.scheduler_hint` 退避长等待，并在最终 quota/replan 检查确认
重复未变化轮询后停止外部循环。Codex App heartbeat 在可用时应 search/use
`automation_update`。如果 `scheduler_hint.action=stop_until_explicit_resume`
且 `scheduler_hint.codex_app.host_action=pause_or_delete_current_heartbeat`：
在该终态情况下，调用 `automation_update` 一次以暂停当前 heartbeat
（仅当暂停不可用时删除），验证 host 结果，不花 quota，并不带 scheduler ACK
结束 turn。否则只在
`scheduler_hint.codex_app.stateful_backoff.apply_needed=true` 且
`scheduler_hint.codex_app.recommended_rrule` 存在时调用它。
成功 RRULE 更新后，用 `scheduler_hint.codex_app.ack_hint.cli_args` 运行
`loopx`；当前 payload 用 `quota scheduler-ack-current`，让 LoopX 重读最新
hint 并拥有推进/重置状态。ACK 结算该 RRULE；即时最终 guard 可以验证同一目标，
但不得当作又一次已过轮询。每个 hint 与 turn 最多尝试一次 host 更新。
如果失败或超时，不要重试或 ACK；运行 `scheduler_hint.codex_app.failure_hint.cli_args`
一次以持久化失败目标与观察到的 host RRULE，且不花 quota。精确重复此后抑制，
直到任一值变化。在观察到的 host cadence 下继续任何允许的 delivery。
当期望 RRULE 已应用时，跳过 `automation_update`；
如果 `stateful_backoff.ack_needed=true`，直接运行绑定的 ack hint，否则不动。
对唯一匹配的当前 heartbeat，`quota should-run` 调和已安装 RRULE 与 ACK ledger；
`host_observation.status=drift_detected` 结果会重新打开 `apply_needed`：

如果会话中没有 `automation_update` 且
`scheduler_hint.codex_app.fallback_hint.available=true`，运行绑定的
`fallback_hint.cli_args`（`loopx-apply-rrule`）一次代替。它备份
`codex-dev.db`、同步自动化 TOML 与 SQLite 行，并运行绑定 ACK；
直接 SQLite 编辑绕过 App API，所以这是有界 fallback，永不作为常规路径。
该 bridge 为其内部 `quota should-run` 查询复用提供的父 Turn。同一 Turn 重放
保留已提交收据的绑定 Todo、观察到的能力与结算身份；显式冲突身份仍 fail closed。
当自动化 id 无法解析时，`fallback_hint.available=false` 且可粘贴 heartbeat
gate 是正确停止——绝不猜测自动化 id。

```text
为当前线程创建一个从 3 分钟开始的 heartbeat 自动化；
然后应用 `quota should-run.scheduler_hint`：仅在 `apply_needed=true` 时更新
RRULE，每个 hint 与 turn 尝试一次；只在 host 更新成功后用提供的
`ack_hint.cli_args` ACK，若更新失败或超时则运行提供的 `failure_hint.cli_args`
一次。如果 `automation_update` 不可用且 `fallback_hint.available=true`，
运行提供的 `fallback_hint.cli_args` 一次代替；若不可用，表露可粘贴 heartbeat gate。

任务：
用 <ACTIVE_GOAL_STATE_PATH> 推进 <GOAL_ID>。在任何 delivery 工作前，
把 `$HOME/.local/bin` 导出到 PATH 并运行 `loopx doctor`；若 CLI 仍不可用，
安静报告该预检失败且不做任何工作。然后把本触发器的 `<current_time_iso>` 拷入
`LOOPX_TURN` 并运行 `loopx --format json --registry "$HOME/.codex/loopx/registry.global.json" quota should-run --goal-id <GOAL_ID> --runtime-profile codex_app_heartbeat --turn-instance-id "${LOOPX_TURN:?}"`。若返回 `should_run=false`，用 NOTIFY 就 operator gate 用 `gate_prompt` 提问，
除非同一未决 gate 最近已被表露。若 payload 说 `notify_user_on_open_todo=true`，
把最多三个开放 `user_todo_summary` 条目作为 blocker-push NOTIFY 询问，
且该 blocker-push turn 不花 quota。若 `open_todo_notification_policy=repeat_until_resolved`，
重复该 NOTIFY 直到 todo 完成、延迟或被替换。若返回 `should_run=true` 且
`effective_action=outcome_floor_recovery` 或 `recovery_delivery_allowed=true`，
只运行有界证据/blocker 恢复再进入任何普通 delivery。若它返回 `state=operator_gate`
加 `safe_bypass_allowed=true`，避免被 gate 的命令，并在 gate 已表露后做至多
一个独立只读 steering/分析步骤。
若返回 `should_run=true`，先检查 `effective_action`，然后对照优先级栈比较候选
下一动作，用 `attention_queue.items` / `project_asset` 作为当前路由权威；
若 project_asset 缺失或为 legacy/raw fallback，原始队列字段不具 owner/gate/stop
权威。把 `run_history.latest_runs` 只当作证据，读取 `goal_boundary`，
检查本目标自己的开放 `user_todo_summary` 是否是 gate / focus_wait /
外部证据等待的 blocker-push 机会，记录依赖或兄弟目标 todos 而不让它们消耗
整个合格 turn，对重复主题应用延续检查，然后读取 `execution_obligation` 与
`heartbeat_recommendation`：
当 `execution_obligation.must_attempt_work=true` 时，
即使 `heartbeat_recommendation.notify=DONT_NOTIFY` 也做一个有界进度片段；
quiet no-op 需要 `execution_obligation.must_attempt_work=false` 且无
`notify_user_on_open_todo=true` blocker-push 通知。把
`recommended_mode=run_first_read_only_map` 当作一次真实只读映射并在验证后 spend
一次；对 `recommended_mode=mapped_noop_if_unchanged`，当没有新
指令/证据/todo/过期来源/安全 handoff 时，返回安静 no-op 且不再 dry-run、
文件编辑或 quota spend。检查 `delivery_batch_scale`、`delivery_outcome`、
`post_handoff_outcome_gap_streak` 与 `handoff_delivery_contract`；
对 repeated-small 或 surface-only 循环遵循契约。然后遵循任何机器可读
`autonomous_replan_obligation` 或 `execution_obligation.must_attempt_work=true`；
若 2 个连续合格 heartbeat 是 no-progress 循环，在另一次 quiet no-op 前运行
有界自修复/replan。当真实边界存在时做一个有界可验证进度批量：实现、验证、
文档与状态写回可以属于同一批量。当验证/writeback 边界已清楚时不要停在
第一个微小子步骤。验证它，写回变更文件 / 验证 / critic / 下一动作；
对非平凡功能切片创建 successor todo 或写紧凑无后续理由；追加一次可问责
`refresh-state --delivery-outcome outcome_progress`，然后恰好一次
`loopx --format json --registry "$HOME/.codex/loopx/registry.global.json" quota spend-slot --goal-id <GOAL_ID> --todo-id <SELECTED_TODO_ID> --slots 1 --source heartbeat --execute`
事件用于完成的 turn；按渲染运行，不加管道或过滤器，绝不重跑。spend 后只允许
可选的 state-only refresh。分钟级 heartbeat 用 `--slots 1`；更粗间隔则花该 turn
消耗的 scheduler 分钟数。
```

## Agent 清单

每个自动 heartbeat turn 的 Agent 面向清单是：

1. 先 guard：`quota should-run --turn-instance-id <HEARTBEAT_TURN_ID>`，
   使用本触发器的 `<current_time_iso>` 并在同 heartbeat 重试中复用。
   若 `loopx` 初始不在 PATH，导出 `$HOME/.local/bin:$PATH` 并在声明预检失败前
   运行本地安装器 fallback。
2. 若 `should_run=false` 且 `state=operator_gate`，询问用户/controller 当前 gate，
   除非同一未决 gate 最近已被表露。每个 heartbeat guard 提交一个幂等收据。
   若 `effective_action=monitor_quiet_skip`，它还提交无 spend 停滞观察并返回
   后续决策；不要追加另一个手动轮询。若仍为 monitor-only，返回安静 `DONT_NOTIFY`。
   保持 monitor todos 可见，但在实质证据变化或 guard 暴露
   `autonomous_replan_required` / `execution_obligation.must_attempt_work=true`
   前不做 delivery 编辑也不 spend。
3. 若 `notify_user_on_open_todo=true`，把最多三个开放用户 todos 作为
   blocker-push 通知询问，且该 blocker-push turn 不花 quota。
   若 `open_todo_notification_policy=repeat_until_resolved`，重复通知直到 todo
   完成、延迟或被替换。若
   `user_gate_notification_cooldown.notification_suppressed=true`，
   保持 gate 待决但返回安静 `DONT_NOTIFY`，直到其有界提醒窗口或实质 gate/host
   变化。否则，同一 blocker 最近被表露时，普通 blocker-push 诉求可以去重。
4. 若 `effective_action=outcome_floor_recovery` 或
   `recovery_delivery_allowed=true`，把 `should_run=true` 当作恢复 turn：
   只运行有界证据/blocker 恢复，并在验证写回后才 spend。
5. 若 gate 已被表露且 `safe_bypass_allowed=true`，要么做一个独立 safe-bypass
   步骤，要么紧凑报告待决 gate。
6. 若当前目标合格，依赖或兄弟目标的开放用户 todos 不得停止整个 turn；
   记录或表露它们，然后继续为当前目标寻找独立于 gate 的 P0/P1/P2 候选。
7. 选工作前运行 steering audit。
8. 用 `attention_queue.items` / `project_asset` 作为当前路由权威；
   若 project_asset 缺失或为 legacy/raw fallback，原始队列字段不具
   owner/gate/stop 权威。把 `run_history.latest_runs` 只当作证据或下钻。
9. 在决定 quiet no-op 前遵循 `execution_obligation`：
   `heartbeat_recommendation.notify` 不是执行 gate。若 `must_attempt_work=true`，
   即使 `notify=DONT_NOTIFY` 也做一个有界进度批量或片段；只有
   `must_attempt_work=false` 且没有待决的 `notify_user_on_open_todo=true`
   blocker-push 通知时才 quiet no-op。
   然后遵循 `heartbeat_recommendation`：首先已连接的只读目标应运行一次真实
   `read-only-map`，而已映射的未变化目标应返回安静 no-op，不再 dry-run 或花 quota。
10. 检查 `delivery_batch_scale`、`delivery_outcome`、
    `post_handoff_outcome_gap_streak` 与 `handoff_delivery_contract`；
    对 repeated-small 或 surface-only 循环遵循契约。
11. 若 2 个连续合格 turn 只是重复的 no-progress 状态循环，启动有界自修复/replan。
    只有该修复路径自身再卡 2 个合格 turn 时才取消或暂停而不是 spend。
12. 普通完成在结算前链接 successor。最终无后续完成只在可问责刷新与匹配 spend
    收据之后发生。
13. 计划/top todos/路线变更需要 LoopX todo / Next Action 写回或无写回理由。
14. 在干净验证与公共/私有边界扫描后，把常规公共 commit、push 与 PR 创建当作
    自主的；为私有/公司材料、凭据、破坏性 git、生产动作或明确要求评审的仓库规则
    停下来。
15. `should_run=true` 时有界工作；当作用域与验证清楚时，连贯的实现/测试/文档/状态
    批量优于微小子步骤。
16. 报告前验证。
17. 验证/writeback 后，用显式 delivery scale/outcome 提示刷新可问责进度，
    然后针对该记录恰好 spend 一次。
18. 记账后只在需要时刷新仅状态元数据；记账后绝不发出另一个可问责进度刷新。
19. 紧凑报告。

该提示刻意是生命周期模板。调度策略在 `quota should-run.scheduler_hint` 中，
因此每项目 heartbeat、共享 controller loop、Codex CLI TUI、Claude Code loop
或未来 Codex goal-mode 自动化都可以共享同一 LoopX quota guard，
而无需硬编码不同等待循环。Host 实现应先执行终态
`codex_app.host_action=pause_or_delete_current_heartbeat`：停止当前 heartbeat
一次、验证结果，并在不 ACK scheduler 或花 quota 的情况下结束。
否则应读取紧凑 `codex_app.stateful_backoff` packet，只在 `apply_needed=true`
时调用 `automation_update`，然后让 `quota scheduler-ack-current` 从最新
scheduler hint 持久化已应用的 RRULE 状态且不花 quota。匹配的重置读回
可以改为设置 `ack_needed=true`；那时跳过 host 写并直接执行绑定 ACK。
