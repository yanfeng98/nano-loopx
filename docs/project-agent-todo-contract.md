# 项目 Agent Todo 契约


项目 Agent 应把面向 operator 的工作留在那些长长的聊天回复、评审文档和高重载的
`Next Action` 段落之外。LoopX 使用独立字段，让 dashboard 与 quota guard
把合适的工作显示给合适的 actor。

## 字段角色

- `Next Action` 是下一个有界步骤的一个路由句。它不是阅读队列、blocker 堆或清单。
- `User Todo / Owner Review Reading Queue` 是面向人类的清单。用它记录 Agent
  无法独自完成的具体用户、owner 或 controller 输入。
- `Agent Todo` 是项目 Agent 清单。用它记录在健康、operator gate、证据与配额
  允许执行后，Agent 可以做的安全后续工作。
- 生产 blocker、缺失写批准与安全风险是 gate 或停止条件。不要把算作用户 todo，
  除非一个特定的人类行动可以清除它们。

外部看板与管理面，包括 Lark Kanban，是这个契约的投影。它们可以显示关键状态、
声明、gate、证据与 worker handoff 字段，但不应成为 Agent 发明新任务身份的地方。
一个长时 Codex 会话可以声明可见看板工作并继续；当它需要分叉、拆分、替代或创建
successor 工作时，它通过 LoopX todo 生命周期写入新任务，并让看板同步追上。

## 写契约

当只读分析、review packet、gate 清单或 P0/P1 steering 发现具体的用户或 owner
动作时，立即用 todo CLI 写入。只有当条目阻塞一个 Agent 或整个目标时才用
`user_gate`：

```bash
loopx todo add \
  --goal-id <goal-id> \
  --role user \
  --task-class user_gate \
  --blocks-agent <agent-id> \
  --text "<public-safe blocking user or owner decision>"
```

对不应停止无关 Agent 的 owner 可见后续，用 `user_action`：

```bash
loopx todo add \
  --goal-id <goal-id> \
  --role user \
  --task-class user_action \
  --text "<public-safe non-blocking user or owner todo>"
```

项目 Agent 后续工作用 `--role agent`：

```bash
loopx todo add \
  --goal-id <goal-id> \
  --role agent \
  --text "<public-safe agent action>"
```

可执行 Agent 工作应注册其 lane，而不是依赖文本分类。有界的实现、验证、benchmark、
blocker 写回或修复片段用 `advancement_task`：

```bash
loopx todo add \
  --goal-id <goal-id> \
  --role agent \
  --text "<public-safe executable agent action>" \
  --task-class advancement_task \
  --action-kind run_eval
```

只有未变化轮询必须保持安静的表面才用 `continuous_monitor`：

```bash
loopx todo add \
  --goal-id <goal-id> \
  --role agent \
  --text "<public-safe monitor action>" \
  --task-class continuous_monitor \
  --action-kind monitor
```

`--action-kind` 是 public-safe 令牌。`run_eval`、`validate`、`rebuild`、
`writeback`、`monitor` 与 `poll` 等已知通用令牌帮助 CLI 一致地投影 lane，
但两者都存在时显式 `--task-class` 是权威。如果确切 todo 已存在，
`todo add` 更新或插入元数据注释，而不是创建重复复选框。
`--task-class user_gate`、`--task-class user_action` 与 `--task-class blocker`
是非执行控制 lane；quota/executor 代码不得把它们当作推进工作。开放用户 todos
必须声明 `user_gate` 或 `user_action` 之一；裸 `--role user` todo 是编写错误。

对定时 monitor，保持契约最小：`--next-due-at` 是第一个合格时间，
`--cadence` 是重试间隔，`--monitor-target-key` 是稳定幂等键，
可选 `--expires-at` 是之后 monitor 不得追上的硬停止。

术语：`goal_id` 是 LoopX 控制面边界：registry 条目、active-state 文件、quota lane、
status 投影与 run-history 流。`todo_id` 是该目标内的结构化工作条目。
LoopX 目前不把 issue 建为独立运行时对象。

多个 Agent 可以共享同一项目控制面。一个 todo 可以用 `claimed_by` 携带软 owner，
但普通 agent todos 不应复述 Agent 的宽泛提示作用域。作用域属于自动化提示或
sub-agent handoff；Agent 用该作用域决定可以声明哪个开放 todo。
User-gate todos 不同：当用户决策只解锁一个已注册 Agent 或 lane 时，
用 `blocks_agent` 显式记录被阻塞的 Agent，使 quota 不停止无关 Agent。
为方便起见，`todo add/update --role user --task-class user_gate --agent-id <agent>`
在省略 `--blocks-agent` 时默认把 `blocks_agent` 设为该 Agent。在多 Agent 目标中，
开放 `user_gate` todos 必须恰好有一个显式作用域：lane 作用域决策用
`blocks_agent=<registered-agent>`，真实目标级 owner gate 用 `global_gate=true` /
`--global-gate`。未加作用域的多 Agent user gate 是编写错误，
因为否则每个已注册 Agent 都会把另一个 lane 的问题当成自己的停止条件。

当一个用户 gate 只阻塞一个具体动作时，用 `unblocks_todo_id=<todo_id>` 添加
被阻塞的 todo id。当多个 todos 共享同一宽泛 `action_kind` 时，
使用 schema 支撑的 decision-scope 字段，而不是依赖标题/正文令牌重叠：

```bash
loopx todo add \
  --goal-id <goal-id> \
  --role user \
  --task-class user_gate \
  --agent-id codex-main-control \
  --decision-scope direction:action:benchmark_target_choice \
  --text "Choose the benchmark target before running that case."

loopx todo update \
  --goal-id <goal-id> \
  --todo-id <agent-todo-id> \
  --required-decision-scope direction:action:benchmark_target_choice
```

当 `decision_scope` 匹配或支配该 todo 的某个 `required_decision_scopes` 时，
quota 把 gate 视为覆盖该 agent todo；否则该 todo 独立，边界允许时可以被选作安全
fallback。

每个共享目标声明 `coordination.agent_model=peer_v1` 与一个
`coordination.registered_agents` 集。注册授予身份，不是等级。工作权威来自
`claimed_by`、任务租约、目标/写边界与 typed 延续策略。功能 profile 角色与
作用域摘要是建议性的；它们不使一个身份成为默认评审者或 leader。

普通生命周期变更遵循 todo 归属。一个目标可以单独把窄的跨 owner 动作委托给
编排 Agent：

```yaml
coordination:
  todo_lifecycle_authority:
    - agent_id: codex-main-control
      actions: [complete, reassign, supersede]
      requires_reason: true
```

不用手工编辑状态即可配置等效 registry 值：

```bash
loopx configure-goal \
  --goal-id <goal-id> \
  --todo-lifecycle-authority-json \
  '{"agent_id":"codex-main-control","actions":["complete","reassign","supersede"],"requires_reason":true}' \
  --execute
```

被委托的 Agent 必须已注册。每个 override 是按动作作用域化的，并发出包含
actor、原始 owner、权威来源与 public-safe `--authority-reason` 的 typed 收据。
委托绝不绕过显式 `excluded_agents` 边界。`coordination.supervisor` 仍是
仅提议的观察角色，不暗示生命周期权威。

```bash
loopx todo complete \
  --goal-id <goal-id> \
  --todo-id <todo-id> \
  --agent-id codex-main-control \
  --authority-reason "Verified the result and closed the stalled lane." \
  --evidence "<public-safe evidence>"
```

Agent todo 可以指名不同的任务仓库，而不把 Agent 作用域拷进 todo 元数据：

```bash
loopx todo update \
  --goal-id <goal-id> \
  --role agent \
  --todo-id <todo-id> \
  --task-repository git:github.com/owner/repo
```

`task_repository` 是一等、无凭据的 Git 身份。它路由工作区隔离，不是写权威；
claim/lease、能力、目标边界与仓库策略继续适用。

`quota should-run --agent-id <agent-id>` 是每个 peer 的预检。当所选任务写仓库状态，
且 peer 处于非 git、无关或非隔离工作区时，它返回 `workspace_guard`，
并在该 peer 移到独立 worktree 并重跑 guard 前阻塞普通 delivery。
只读和 monitor-only 工作不因 Agent 身份而要求隔离。当 `task_repository` 缺失时，
注册的目标 repo 仍是预期仓库，因此无关的 worktree 不能绕过目标仓库规则。

面向贡献者的示例：

```bash
loopx --format json quota should-run \
  --goal-id <goal-id> \
  --agent-id codex-peer-b
```

如果响应包含 `effective_action=agent_workspace_repair`，peer 不应立即编辑文件。
创建或切换到独立 worktree 并重跑同一 guard：

```bash
git worktree add /tmp/<goal-id>-peer-b -b codex/<peer-branch>
cd /tmp/<goal-id>-peer-b
loopx --format json quota should-run \
  --goal-id <goal-id> \
  --agent-id codex-peer-b
```

只有在该重跑返回普通 delivery 后，peer 才应声明作用域内 todo 并编辑仓库文件。
另一个 peer 声明的 todo 在该 peer 显式转移前仍属其所有。对 Agent 特定 quota
payload，当前 Agent 声明优先，未声明 todos 保持可选，其他 peer 声明是诊断上下文
而不是可执行工作。这减少冲突，而不把宽泛提示作用域写进 todo 元数据，
也不假装软声明已经是硬租约。当可运行的当前 Agent 或未声明推进 todo 存在时，
quota 还可以暴露 `agent_lane_next_action.schema_version=agent_lane_next_action_v0`。
该字段是该 peer 本 turn 的当前切片；它不覆盖持久的目标级 `Next Action`。
`loopx status --agent-id <agent-id>` 可以把同一派生字段附加到匹配的 status
队列条目供观察，而保持项目级路线不变。
当候选有 `target_capabilities` 且目标 bridge 能力缺失时，quota 可标记它
`capability_repair_mode=true`；作用域 next-action 选择应优先该修复模式候选，
而不是同一 claim/优先级桶中的普通可运行工作，使能力构建 todos 不需要脆弱的
active-state 重排。

### 机器可读恢复条件 {#machine-readable-resume-conditions}

延迟 todos 可以用 `resume_when=<token>` 携带机器可读恢复条件。支持的条件是：

- `resume_when=todo_done:<todo_id>`：被引用 todo 达到 `status=done` 后，
  延迟 todo 成为 successor replan 候选。
- `resume_when=pr_merged:#532` 或
  `resume_when=pr_merged:owner/repo#532`：结构化上线事件记录该 PR merge 后，
  延迟 todo 成为 successor 候选。无资格 `#532` 只绑定到该 todo 的 GitHub
  `task_repository`；跨仓库依赖用限定形式。如果 LoopX 无法推导该绑定，
  它保持 todo 延迟并暴露机器可读的仓库歧义，而不是匹配另一个仓库里的相同 PR 编号。
- `resume_when=capacity_available:<capability>`：只有当前 quota 读取提供该运行时
  能力时，todo 才就绪。
- `resume_when=monitor_changed:<monitor_todo_id>`：被引用的 `continuous_monitor`
  记录新的 typed 材料变化世代后，开放的推进 todo 才恢复。转移把 monitor 当前世代
  绑定为基线，因此未变化轮询、笔记编辑与相同材料结果重放不会唤醒该 todo。

Monitor 与其发现的 delivery 是分开的工作条目。`continuous_monitor` 仅观察；
它从不成为可运行 delivery。在材料观察时，用
`quota monitor-poll --material-change --next-agent-todo ... --next-action-kind ...`
发出独立的开放 `advancement_task`。等待的推进 Todo 保持 `status=open`，
并通过 `--successor-todo-id` 把 `resume_when=monitor_changed:<monitor_todo_id>`
与那个独立 Todo 配对。是恢复条件——而不是 `status=blocked`——
使等待 Todo 在 monitor 世代推进前不进可运行选择。相关命令结果暴露紧凑的
`monitor_advancement_authoring_v0` 契约，让 Agent 无需解析文档散文即可恢复此序列。

开放 todos 在可见但尚不可执行时也可以携带 `resume_when`。在解析的
`resume_condition.satisfied` 值为 true 之前，status 与 quota 把该 todo 排除在
`first_executable_items`、`executable_backlog_items`、
`capability_gate.runnable_candidates` 与 `agent_lane_next_action` 之外。
当 `resume_ready=true` 时，开放 todo 可以进入其声明 Agent 的正常可执行 lane。

Status 与 quota 在排序后的开放 todo lane 之后把延迟 todos 暴露为可见性 lane。
这是延迟 gate-resume lane：它不是可运行工作，也不是当前 Agent 没有 todo 的证据，
直到 Agent 重新打开、替代或为该延迟条目记录无后续理由。

```bash
loopx register-agent \
  --goal-id <goal-id> \
  --agent-id codex-main-control \
  --agent-id codex-side-bypass \
  --execute
```

然后通过专用命令声明。`--claimed-by` 记录持久 owner，而 `--agent-id`
归因执行该变更的 peer。自声明时两者都必需，且必须点名同一注册 Agent：

```bash
loopx todo claim \
  --goal-id <goal-id> \
  --todo-id <todo_id> \
  --claimed-by codex-main-control \
  --agent-id codex-main-control
```

还没有 `coordination.registered_agents` 的旧项目在 Agent 尝试声明工作时会被
刻意阻塞。CLI 错误包含 `register-agent --agent-id <agent-id> --execute` 命令，
让 Agent 或 controller 在写归属元数据前注册其身份。Agent 注册写入全局投影点名的
来源注册表；如果共享全局注册表不可写，它在改变该来源前失败，
使控制面不会漂移到半注册状态。

当拥有 peer 重新分配 todo 或释放工作时，用 `--clear-claim`。`claimed_by`
是可见性，不是运行时租约：它不绕过 quota、用户 gate、写作用域检查、验证或 actor
授权。在已注册多 Agent 目标上，`todo claim/update/complete/supersede` 需要
`--agent-id`；actor 不得被排除，且存在 `claimed_by` owner 时必须匹配。
一个精确链接的 `user_gate` 决策作用域是窄例外：它的 typed approve/reject/cancel
完成归因于 owner/controller 决策，而不是 Agent actor。没有
`coordination.registered_agents` 的旧项目在归属元数据写出前仍 fail closed。
`todo claim` 是非破坏性的：如果另一个注册 Agent 已拥有该 todo，
它 fail closed，而不是静默替换 `claimed_by`。用显式
`todo update --clear-claim` 或 `todo update --claimed-by <agent-id>` 决策转移归属。
CLI 在写 claim 变更与完成 handoff 时使用与 todo add/update/complete 相同的
active-state 文件锁，因此并发 CLI 写者会先重读最新状态再编辑，
而不是覆盖过期快照。

命令从项目 registry 解析 active state，在需要时创建规范区块，更新 `updated_at`，
并避免重复的确切 todo 文本。如果 dashboard 或 controller 需要立即看到新清单，
在写之后刷新 status 投影：

```bash
loopx refresh-state --goal-id <goal-id> --agent-id <registered-agent>
```

对多 Agent 目标，`refresh-state` 需要显式 `--agent-id`。默认的作用域刷新是
Agent lane run：它用于保持同一 turn 的写回/记账身份完整，
但不替代目标级 status 路线。

## 生命周期契约

Agent 不应直接修补 active-state 复选框来推进工作。使用生命周期命令，让 LoopX
在一次写中保留 `todo_id`、status、分类元数据、时间戳与幂等。

Todo 生命周期应保持简单。不要添加独立功能状态机，如 `slice_done`、`rolled_out`
或 `proven_in_product_path`，除非产品对它有没有具体的 UI/运行时需求。对普通项目
工作，用 **todo succession**：完成实现切片，然后为上线、产品路径审计、benchmark
证明、文档、遥测或 operator 决策创建下一个具体 todo。

一个非平凡功能 todo 只作为切片完成。在完成前或完成时，Agent 应做以下之一：

- 用 `--next-agent-todo`、`--next-user-todo` 或后续 `todo add` 创建下一个
  public-safe Agent 或用户 todo；
- 用 `--no-follow-up` 加 `--note` / `--reason` / `--evidence` 记录紧凑无后续理由，
  说明该功能为何真的完成，不需要上线、审计、文档或产品路径证明。

这个 succession 决策是持久 Todo 状态。后来的进度观察、vision ACK、
覆盖耗尽结果或重写的理由都不能替代它。因此每个新完成都保留不透明完成身份。
受配额约束的完成对 Agent 推进工作只允许收据支撑的同一 turn `todo complete` 转移。
先完成匹配的问责 `refresh-state` 与 `quota spend-slot`；显式 `same_agent_non_delivery`
工作、monitor、用户行动与用户 gate 保持其现有生命周期路径。普通未加作用域的完成
获得稳定的 `local_completion_*` 身份；如果后来的 `refresh-state` 发现完成的 Goal
没有真实 successor，其 typed 拒绝可以投影 `--completion-identity-key`，
用于一次直接生命周期重入。该命令只对确切的已完成 Todo、其匹配的本地身份、
`active_goal` 延续、无 successor 与经授权的生命周期 actor 有效。
它不能用于开放 Todo，也不能用作 quota turn 身份。否则添加/链接真实 successor。
不要仅仅为了压制 succession 警告而创建用户 gate。

已完成事务在写同一 turn 的 refresh 与 quota 收据前完成 Todo 的兼容 host adapter，
必须显式把其非仓库工作标记为 `same_agent_non_delivery`。通过这些 adapter 的仓库
推进 fail closed，得到 typed 结算 blocker，直到 adapter 采用 writeback-and-spend-
before-completion 事务。

这让活跃清单保持诚实，而不使 LoopX 成为沉重项目管理系统。

完成当前 todo 并原子注册下一个可执行 todo：

```bash
loopx todo complete \
  --goal-id <goal-id> \
  --todo-id <todo_id> \
  --agent-id <registered-agent> \
  --evidence "<public-safe artifact or result>" \
  --next-agent-todo "<public-safe next executable action>" \
  --next-task-class advancement_task \
  --next-action-kind run_eval
```

人类评审不自动是执行 gate。当一个已验证功能 PR 可以在独立工作继续时等待评审，
原子派生一个有界提醒与可运行 successor：

```bash
loopx todo complete \
  --goal-id <goal-id> \
  --todo-id <todo_id> \
  --claimed-by <registered-agent> \
  --agent-id <registered-agent> \
  --evidence "<validated PR URL and checks>" \
  --next-user-todo "Review the validated feature PR." \
  --next-user-task-class user_action \
  --next-agent-todo "Continue the next independent feature slice." \
  --next-claimed-by <registered-agent>
```

`--next-user-todo` 需要显式 `--next-user-task-class user_gate|user_action`。
保持可见但不设置 `blocks_agent` 的提醒用 `user_action`；把 `user_gate` 保留给
确切 owner/controller 权威边界，如把聚合分支 merge 进 `main`、发布、benchmark
启动、凭据或受保护生产动作。省略 task class 会在 writeback 前失败，
使 LoopX 永不猜测授权边界。当 PR 生命周期需要周期读回时，额外添加
`continuous_monitor` todo。

对实验功能栈，稳定集成分支可以收集小功能 PR，而评审提醒保持开放。
每个功能仍使用专用 worktree 与分支；其 PR 指向集成分支。指向 `main` 的聚合
集成分支 PR 是评审/merge 边界。这让评审延迟不用挂起无关工作，
也不削弱最终交付 gate。

终态 PR 状态不会静默完成评审提醒：已 merge 的 PR 可能仍需要 merge 后评审。
当 owner 显式确认确切的评审动作已完成时，用确切的绑定 `user_action` 与 GitHub PR
持久一个 typed 确认收据：

```bash
loopx issue-fix pr-review-ack \
  --url https://github.com/owner/repo/pull/123 \
  --goal-id <goal-id> \
  --todo-id <review-todo-id> \
  --agent-id <bound-agent> \
  --owner-acknowledged
```

收据是 fail-closed、按 todo revision 幂等的，并在追加后读回。它绑定 goal、
todo revision、agent、provider、仓库、PR 编号与 canonical 永久链接，
而不解析提醒散文。重新打开或实质性编辑该 todo 会使先前确认失效。

用 `pr-review-reconcile` 作为单一调和路径。它可以显式调用，
或由到期的 `continuous_monitor` 通过任何 scheduler 或 host adapter 调用。
先提供 `--owner-acknowledged` 记录同一 typed 收据。调和在 provider 访问前与完成前
验证当前 todo revision，然后只为确切终态 PR 关闭提醒。缺失收据、过期 revision、
provider 不可用或不支持的 forge 会保持提醒开放。Quota 投影没有 provider 副作用。

带 `external_evidence_poll` 的 heartbeat host 可以在 quota 前运行有界批量形式：

```bash
loopx heartbeat-prequota -g <goal-id> -a <bound-agent>
```

批量只读取持久的确切确认绑定，在 provider 访问前跳过过期或已调和 todos，
且不花 quota。Provider 失败报告为降级结果，不阻塞后续 quota guard。
绑定、确认与调和是内核契约；`loopx-project` 可以记录该工作流，
但不是运行时依赖。

如果 Agent 在完成时接管归属，在同一锁定的生命周期写中包含声明：

```bash
loopx todo complete \
  --goal-id <goal-id> \
  --todo-id <todo_id> \
  --claimed-by codex-peer-a \
  --agent-id codex-peer-a \
  --evidence "<public-safe artifact or result>" \
  --next-agent-todo "Continue the next bounded task." \
  --next-claimed-by codex-peer-b \
  --next-continuation-policy independent_handoff
```

LoopX 不从 Agent 身份推断延续权威。`action_kind` 仍是描述工作的开放领域令牌。
闭合的 `continuation_policy` 枚举只描述完成任务与其 successor 的关系：

- `independent_handoff` 是默认。除非 `--next-claimed-by` 选择了一个已注册 peer，
  successor 保持未声明；
- `same_agent_non_delivery` 与完成的 peer 保持一个证据支撑的非 delivery 延续。

评审、验证、merge 与发布仍是普通 `action_kind` 值。它们不改变 scheduler 排序。
另一个 peer 可能声明的 successor 用 `independent_handoff`，并在需要执行者分离时
添加一个或多个 `excluded_agents`。`claimed_by` 不得点名被排除的 peer。

`same_agent_non_delivery` 刻意是结构性的，而不是特定于评审。它在显式选择时涵盖
就绪检查、审计、分类与其他非 delivery 延续。LoopX 不从 `action_kind` 推断它，
也不授权仓库 delivery 或绕过 successor quota/能力检查。

只有同时携带 `unblocks_todo_id` 与执行者排除时，handoff 才成为阻塞依赖。
普通独立 successor 不会隐式继承 owner。下一个 owner 已知时用 `--next-claimed-by`；
后续声明应选择它时，让 successor 保持未声明。

对满足仓库 self-merge 规则的小变更，peer 可以显式说明例外，self-merge 并无 successor
评审 todo 完成：

```bash
loopx todo complete \
  --goal-id <goal-id> \
  --todo-id <todo_id> \
  --claimed-by codex-peer-a \
  --agent-id codex-peer-a \
  --self-merged \
  --evidence "<public-safe commit, validation, and self-merge summary>"
```

`--self-merged` 需要 `--evidence`。不要把它用于需要独立 handoff 的运行时、
benchmark、权限、生产、破坏性 git、发布、公共证据策略或宽泛协调变更。
在验证后的 self-merge 之后，当切片推进了公共产品或用例路径时，
在项目级写回真实 delivery outcome。带 `--agent-id` 的 Agent lane refresh
记录 peer 本地笔记；goal 作用域 refresh 记录持久目标路线。两者都要求已注册 peer。
不要在已验证的 `outcome_progress` 切片后再追加一个目标级 `surface_only` 同步；
要么跳过重复同步，要么用以下方式镜像产品进度：

```bash
loopx refresh-state \
  --goal-id <goal-id> \
  --classification <public-safe-progress-classification> \
  --delivery-batch-scale multi_surface \
  --delivery-outcome outcome_progress \
  --agent-id <registered-agent> \
  --progress-scope goal
```

这让已验证的 peer 产品工作不被误读为又一个 surface-only heartbeat turn。
当 self-merged 切片有明显同作用域延续时，它还可以原子添加该 successor todo
并把它收回给同一 peer：

```bash
loopx todo complete \
  --goal-id <goal-id> \
  --todo-id <todo_id> \
  --claimed-by codex-peer-a \
  --agent-id codex-peer-a \
  --self-merged \
  --evidence "<public-safe commit, validation, and self-merge summary>" \
  --next-agent-todo "Continue the next small docs/productization slice." \
  --next-claimed-by codex-peer-a
```

没有 `--self-merged`，不会创建隐式评审路线。需要独立评审时，用
`--next-action-kind review --next-continuation-policy independent_handoff`；
只有评审必须对多个 peer 开放同时排除作者时，才加
`--next-excluded-agent <author>`。当 successor 属于特定仓库或需要执行能力时，
在同一完成命令中设置 `--next-task-repository <git:host/path>` 并重复
`--next-required-capability <capability>`。successor 在执行者排除生效前就完全可路由。

较低级别、非终态的状态变化用 `todo update`：

```bash
loopx todo update \
  --goal-id <goal-id> \
  --todo-id <todo_id> \
  --agent-id <registered-agent> \
  --status blocked \
  --reason "<public-safe blocker>" \
  --task-class blocker
```

Agent Todo 完成始终走 `todo complete`；`todo update --status done` 被拒绝，
所以评审、successor 与无后续策略不能被绕过。一个有证据支撑的 peer
`continuous_monitor` 没有必需写作用域时，可以在其有界 watch 无材料转移地结束时
用 `todo complete --no-follow-up` 关闭。该收尾记录 `self_merged=false`，
且不为观察-only 工作创建 successor 评审 todo。

User-role todos 仍可通过 `todo update --status done` 写 `done`；
当 todo 声明 `validation_command`（或通过 `--validation-command-json` 声明的
`validation_command_argv`）时，该更新与 `todo complete` 运行相同完成验证 gate，
并以 typed `validation_blocked_completion` 收据 fail closed，
而不是提交 `done`。没有声明命令的 todos 保持未变更的快路径。

当延迟 successor 应在一个机器可读条件后唤醒，而不是只存在于散文时，用
`--resume-when`：

```bash
loopx todo update \
  --goal-id <goal-id> \
  --todo-id <todo_id> \
  --agent-id <registered-agent> \
  --status deferred \
  --resume-when todo_done:<blocking_todo_id> \
  --reason "<public-safe deferred rationale>"
```

当一个开放推进切片等待 monitor 观察时，保持它可见，并原子绑定等待与一个独立
可运行 successor：

```bash
loopx todo update \
  --goal-id <goal-id> \
  --todo-id <waiting_todo_id> \
  --agent-id <registered-agent> \
  --resume-when monitor_changed:<monitor_todo_id> \
  --successor-todo-id <runnable_successor_todo_id> \
  --reason "<public-safe external-wait rationale>"
```

LoopX 把等待 todo 保持为 `status=open`，在 `resume_ready=false` 期间把它排除在
可运行候选之外，并在 monitor 世代推进后自动恢复它到可运行 lane。
在刻意重新武装同一 monitor 等待前，用 `todo update --clear-resume-when` 清除
已满足的条件。

当前开放 todo 应退役并由替代时，用 `todo supersede`：

```bash
loopx todo supersede \
  --goal-id <goal-id> \
  --todo-id <todo_id> \
  --agent-id <registered-agent> \
  --reason "<public-safe reason>" \
  --next-agent-todo "<replacement executable action>"
```

如果被替代的 todo 被声明，替代继承该 `claimed_by`。如果它携带
`blocks_agent` / `unblocks_todo_id`，替代也继承那些解除阻塞字段。
用 `--next-claimed-by <agent-id>` 显式指明 handoff。

`todo complete` 对重复 heartbeat 是终态幂等的：来源 todo 完成后，
后续完成返回 `changed=false`，不能追加或重新链接不同 successor。
用显式后续 todo 或生命周期命令纠正已完成路线，而不是用新参数重放 `complete`。
`todo supersede` 保持自己的幂等 successor 插入。
`todo archive-completed` 只是卫生命令：它把已完成的活跃 todos 移入
`Completed Work Archive`；它不把开放 todos 标记为 done。

当一个开放 todo 有生效的硬任务租约时，完成必须证明执行实例，
而不只是共享 Agent 身份：

```bash
loopx todo complete \
  --goal-id <goal-id> \
  --todo-id <todo_id> \
  --claimed-by <agent-id> \
  --task-lease-idempotency-key <acquire-key> \
  --task-lease-expected-version <lease-version> \
  --evidence "<public-safe evidence>"
```

租约活跃时 key 与 version 都必需。缺失或不匹配的对在 Todo 或 successor 状态
写出前失败，包括两个 host 进程刻意共享一个 `agent_id` 时。
`todo supersede` 把同一 todo 移为 done，并以同样两个选项跨同一围栏；
被租约的 todo 不能通过任一动词以部分围栏退役。释放保留非活跃终态记录，
下次获取必须使用新执行 key，并收到更大的版本与权威拥有的 `lease_epoch`。

## 解析 Schema

项目可以继续写普通 Markdown 复选框，但读者应在可用时使用 status/quota 发出的
结构化投影。Todo 摘要携带 `schema_version=todo_summary_v0`；单个条目携带
`schema_version=todo_item_v0`、`todo_id`、`role`、`status`、`priority`、
`title`、`archive_state`、`source_section`、`index`、`text`、`task_class`，
以及可选的 `action_kind`、`claimed_by`、`required_capabilities` 和
`target_capabilities`。一个被能力许可的 Agent Todo 还可以携带不透明
`capability_binding_ref`；它标识能力拥有的权威行，并跨生成的 Agent successor 保留。
一旦设置，该绑定不可变，且不同于执行者 `required_capabilities`。
`action_kind` 可扩展；可选 `continuation_policy` 限于 `independent_handoff`
或 `same_agent_non_delivery`。Agent todos 还可以携带 `excluded_agents`、
`unblocks_todo_id` 与 `no_followup=true` 来表达执行者分离、依赖谱系与刻意收尾。
`blocks_agent` 保留用于给 user gates 加作用域。

硬切升级后，`loopx check` 报告仍携带已移除 gate 路由字段的 agent todos。
新读者还保留一个只读 `removed_continuation_policy` 诊断，用于遗留 `review_handoff`
与 `primary_review` 记录，并把那些记录排除在声明/quota 执行之外。
这个 fail-closed 兼容标记不是受支持的延续类型，且从不写回。显式修复遗留评审记录：

```bash
loopx todo update \
  --goal-id <goal-id> \
  --todo-id <todo-id> \
  --agent-id <registered-agent> \
  --role agent \
  --continuation-policy independent_handoff \
  --excluded-agent <author>
```

对已移除的 `blocks_agent` 路由，用 `loopx todo update --todo-id <todo_id>
--role agent --clear-blocks-agent`。LoopX 不推断被排除作者，
也不自动重写任一形式。

延迟 successors 可以携带 `resume_when`、`resume_condition` 与 `resume_ready`；
`resume_ready=true` 表示延迟条目应在任何 Agent 作用域无候选等待之前被考虑为
successor replan，而不是普通 delivery 可跳过 todo 生命周期。
就绪的延迟 successor 还为这次生命周期 replan 抢占严格更低优先级的开放推进 todo。
它不抢占同优先级开放 todo，且在生命周期命令重新打开前绝不进入普通可执行积压。
由 CLI 写入时 `todo_id` 是一等。
`claimed_by` 值是归一化的 public-safe Agent id，应对应
`coordination.registered_agents`。没有元数据的遗留 Markdown 仍从本地
section/index/text 获得解析器派生的兼容 id，第一个生命周期命令会把该 id
物化回元数据。未来的租约时间戳、依赖、能力细节与证据链接字段应扩展该条目形状，
而不是添加另一个 todo 格式。
在 Markdown 中，lane 元数据存储为复选框正下方的缩进 HTML 注释，例如：

```markdown
- [ ] Run one validated benchmark case and write back result or blocker.
  <!-- loopx:todo todo_id=todo_8e280be49441 status=open task_class=advancement_task action_kind=run_eval required_capabilities=shell%2Cbenchmark_runner claimed_by=codex-main-control -->
```

纯复选框文本保持兼容 fallback。新自动化面向的工作应优先 CLI 元数据路径，
使 quota 与 dashboard 消费方不需要项目特定词表。

可执行 agent todos 可以用 `--required-capability` 声明逐 todo 环境需求。
把该字段放在 todo 附近，而不是全局 Agent profile：同一 Agent 可能对文档工作有
shell/filesystem 能力，但对某个步骤缺少 `benchmark_runner`、`external_evidence_poll`、
`network` 或其他 bridge。

```bash
loopx todo add \
  --goal-id <goal-id> \
  --role agent \
  --text "<public-safe executable agent action>" \
  --task-class advancement_task \
  --action-kind run_eval \
  --required-capability shell \
  --required-capability benchmark_runner
```

当 todo 是为了构建、修复、物化或 parity 检查一个能力，而不是把该能力用作前置条件时，
用 `--target-capability`。例如，一个 benchmark 产品路径 parity todo 可以只硬性
要求 shell，同时把 benchmark runner bridge 作为目标：

```bash
loopx todo add \
  --goal-id <goal-id> \
  --role agent \
  --text "<public-safe benchmark parity repair action>" \
  --task-class advancement_task \
  --action-kind benchmark_treatment_product_path_parity \
  --required-capability shell \
  --target-capability benchmark_runner
```

`status` 在每个可见 todo 上投影 `required_capabilities`。`quota should-run`
随后从可见可执行队列而不是单个预选 todo 派生只读 `capability_gate`。
有多个 P0 或 P1 条目时，它按顺序扫描投影队列并暴露候选集：能力满足的 todos
出现在 `capability_gate.runnable_candidates`，而被阻塞的高优先级候选保持
`capability_gate.blocked_candidates` 可见。gate 不选最终 todo；
Agent 保持决策权威，并必须在 steering audit 期间从可运行集选择。
如果没有可见可执行候选可以运行，gate 按缺失能力类别返回 `repair_bridge`、
`ask_owner` 或 `skip`。
`target_capabilities` 保持可运行候选 payload 可见。如果目标 bridge 缺失，
候选被标注 `capability_repair_mode=true` 与 `missing_target_capabilities`，
但该目标不当作硬执行 blocker。

## 执行顺序

1. 在花自动 delivery 计算之前，对照共享全局 registry 运行 quota guard。
2. 如果 guard 或 review packet 暴露开放用户 todos，向用户表露它们，
   而不是报告 "no new user action"。
3. 如果 guard 设置 `notify_user_on_open_todo=true`，把开放 todos 当作
   blocker-push 通知：最多问三个条目，跳过 delivery 工作，且除非同一 blocker
   最近已被表露，否则跳过 quota spend。
4. 相关 gate 仍未解决时，不执行 `agent_command`、adapter work、write-control
   或生产动作。
5. 用户 todo 完成或显式延迟后，项目 Agent 只能通过当前 guard 或 review packet
   允许的安全路径继续。

## 公共 Smokes

两个无依赖公共 fixture 覆盖该契约：

```bash
python3 examples/control_plane/todo-cli-smoke.py
python3 examples/control_plane/todo-lifecycle-cli-smoke.py
python3 examples/project/project-agent-adoption-smoke.py
python3 examples/control_plane/todo-concurrent-write-lock-smoke.py
python3 examples/capability-gate-smoke.py
```

第一个验证 todo CLI 写入规范 active-state 区块。第二个验证按 `todo_id` 的生命周期
转移，包括声明完成、supersede、幂等 next-todo 插入与非可执行 blocker lane。
第三个验证从 quota guard 提示到用户 todo 写、到 status 投影、到已批准项目 Agent
handoff 的执行者面向路径。
第四个验证并发 todo 写者等待 active-state 锁，并保留 claim 元数据与无关更新。
第五个验证逐 todo `required_capabilities`，包括多 P0/P1 候选选择、bridge 修复
与 owner 门控能力缺失。
