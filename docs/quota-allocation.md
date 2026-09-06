# 计算配额


LoopX 应在项目之间拥有计算分配。第一版应刻意简单：每个目标获得一个计算配额数字，
自动化或 controller tick 用该数字决定目标可多频繁消耗 Agent 时间。

这取代了当前仅靠变更自动化周期表达优先级的临时模式。定时器可以唤醒执行者，
但产品策略应住在 LoopX。

## 产品范围

在 v0.1 中，quota 意思是**仅计算配额**。

它不决定人类奖励、写批准、生产权限或 operator gate 结果。那些仍是独立的
LoopX 状态。

计算配额回答一个问题：

> 在可用自动 Agent 时间中，该目标应被允许消耗多少？

示例：

- `1.0`：完整占空比。如果 controller 每小时检查，该目标在 24 小时窗口内
  每次健康检查都合格。用默认分钟粒度记账，`1.0` 表示 `24 * 60 = 1440`
  个自动计算分钟槽位。
- `0.5`：一半占空比，约每天 12 小时或调度分钟槽位的一半。
- `0.3`：30% 占空比，约每天 7.2 小时或调度分钟槽位的 30%。
- `0`：compute-paused。这是**目标级硬暂停**：目标保持可见但收不到自动
  Codex turns，`quota should-run` 返回单一权威暂停契约。因为暂停是在任何
  selector lane 构建前评估的 typed 终态决策，capability-bridge、workspace、
  replan、monitor 或 inbox lane 都不能在其下面留下冲突执行信号
  （`should_run=false`、所有自动权限 false、`DONT_NOTIFY`、scheduler 从不
  `run_now`、没有 quota spend）。用 `loopx configure-goal --quota-compute 0` 设置；
  负值被拒绝。

  这不同于单个 Agent 的 `monitor_only` 工作模式。`quota.compute=0` 为每个
  Agent 与每一条 lane 暂停**整个 Goal**；`monitor_only` 是每 Agent lane 状态，
  一个 Agent 仍运行有界只读 monitor 轮询，而 Goal 本身对其他工作保持活跃。

该数字既可按占空比解释，也可按相对权重解释，取决于执行者：

- 每目标自动化可以把 `0.5` 变成"大约一半的 ticks 上运行"；
- 共享 controller loop 可以把同一数字当作合格目标之间的加权选择比。

## 最小契约

紧凑 status 形状可以从一个小对象开始：

```json
{
  "quota": {
    "compute": 0.5,
    "window_hours": 24,
    "slot_minutes": 1,
    "allowed_slots": 720,
    "spent_slots": 240,
    "state": "eligible",
    "next_eligible_at": "2026-06-02T12:00:00+08:00",
    "reason": "0.5 compute quota, 240/720 minute-slots spent in the current window"
  }
}
```

Registry 条目可以直接声明同一策略：

```json
{
  "quota": {
    "compute": 0.5,
    "window_hours": 24
  },
  "control_plane": {
    "self_repair": {
      "enabled": false,
      "allow_health_blocker_repair": false,
      "allow_waiting_projection_repair": false
    }
  }
}
```

如果 `quota.compute` 缺失，status 默认把它当作 `1.0`，使新连接的项目保持合格，
除非更硬的 gate 阻塞它。

`slot_minutes` 可选，默认为 `1`。默认 `allowed_slots` 计为
`window_hours * 60 / slot_minutes * compute`，所以 `compute=1.0` 已经是完整
24 小时占空比。Operator 应只为异常覆盖而显式设置 `allowed_slots`，
例如临时突发、刻意更严格的实验上限或非分钟 scheduler。它不应被要求来表达正常
完整配额。

对首个实现，`spent_slots` 计紧凑自动计算预算单位。在默认分钟粒度下，
一个 slot 表示一分钟自动计算预算。分钟级 heartbeat 延续可以花 `--slots 1`；
更粗的 controller 应花它们实际保留的 scheduler 分钟数。它不需要精确计 token。

Status 从当前 `window_hours` 窗口内的紧凑 `quota_slot_spent` 运行时事件派生
当前 `spent_slots`。Registry 保持为 `compute`、`window_hours` 与可选
`allowed_slots` 的策略源；它不是 spend ledger。

后续版本可以用真实运行时、token 消耗或成本替换 slots，
但 operator 面向的模型应保持相同：一个项目有一个简单计算份额。

## 状态顺序

Quota 在硬 gate 后应用：

1. 健康与安全 gate：损坏的 registry、契约失败或不安全边界问题阻塞目标。
2. Operator gate：只读 opt-in、write-control、奖励判断与生产动作仍需显式人类决策。
3. 证据等待：等待外部指标或目标 controller 响应的目标不应只因 quota 剩余就消耗
   delivery 计算。
4. Focus 等待：当前 delivery lane 饱和或等待新意、owner 证据、外部 eval 或干净
   基线时，目标仍可归 Codex 所有。它应保持可见，但不应只因 compute quota 剩余就
   花 delivery 计算。
5. 计算配额：在其他方面合格的目标之间，quota 决定这一个是否应收到下一个自动 turn。

这保持模型小。Quota 不会变成第二权限系统。

## 控制面设置

Registry 条目可以随 quota 携带每目标 `control_plane` 策略。这些设置是
那些否则会诱人地编码进 heartbeat 提示的行为的控制面。

当前自修复设置：

- `control_plane.self_repair.enabled`：默认 `false`。
- `control_plane.self_repair.allow_health_blocker_repair`：启用时，目标可以花
  一个有界 turn 修复阻止正常 delivery 的 LoopX 健康或契约 blocker。
- `control_plane.self_repair.allow_waiting_projection_repair`：启用时，
  处于 `state=waiting`、无具体等待 owner 但有当前动作或 Agent 积压的目标，
  可以花一个有界 turn 修复投影或写回具体 blocker。

自修复按目标刻意 opt-in。简短 heartbeat 可以从 `quota should-run` 读机器契约，
但没有该 registry 策略的普通目标保持其现有 skip、waiting 或 health-blocked lane。
独立于 opt-in 健康/投影修复，当 active state 或公共 run history 显示 2 个连续
停滞 monitor/no-progress turn 时，status 可以投影一个 `autonomous_replan_obligation`。
那时 `execution_obligation.kind=autonomous_replan_required` 且
`must_attempt_work=true`；launcher 应在另一次 quiet no-op 前运行一个有界 replan
切片，然后只在验证写回后 spend。

## 分配契约

`quota plan` 报告建议性的下一个自动 turn。它不授予许可、不清理 operator gate、
不记录人类奖励，也不授权项目 Agent 运行否则会被阻塞的工作。

分配规则刻意小：

1. 从 `loopx status` 使用的同一 status payload 派生 quota 组；
2. 把 `blocked_health`、`operator_gate`、`focus_wait`、`waiting`、`throttled`
   与 `paused` 目标保留在各自 lane，即使它们有高 `quota.compute`；
3. 只有 `state=eligible` 的目标进入合格 lane；
4. 按有效 `quota.compute` 排序合格目标，最高优先；
5. 把 `summary.next_automatic_turn` 设为第一个合格目标，合格 lane 为空时为 `none`。

自动化与 controller 应把 `next_automatic_turn` 当作调度提示，
然后在花计算前立即问 `quota should-run --goal-id <goal-id>`。如果 guard 返回
`should_run=false`，执行者应跳过被阻塞的 delivery 工作并遵循报告的健康、
operator、证据、focus-wait、pause 或 throttle 原因。当 `state=operator_gate`
同时返回 `safe_bypass_allowed=true` 时，目标 heartbeat 可以做不依赖该 gate 的
一个有界只读 steering 或分析步骤，但不得执行 `agent_command`、adapter work、
write-control、生产动作或被 gate 的路径。
当 `state=focus_wait` 由 connected-delivery outcome floor 造成且 payload 返回
`safe_bypass_kind=outcome_floor_recovery` 时，目标不能自由恢复普通 delivery。
它只能花一个有界恢复 turn 来产出 `quota.must_advance` 点名的必需
ranker/cross-domain 证据产物，或写回阻止该产物的具体 blocker。
Surface-only 摘要/队列/契约传播与仅合成测试链保持阻塞。
当 `control_plane.self_repair.enabled=true` 且所选目标被可修复控制面条件卡住时，
`quota should-run` 可以改返回 `decision=self_repair`、`self_repair_allowed=true`、
`stall_self_repair` 与 `effective_action`，如 `control_plane_health_repair` 或
`control_plane_projection_repair`。这把"修复控制面"变成所选目标的机器可读有界动作，
而不是提示特定分支。Spend 只在验证与持久 writeback 后被允许。

Delivery outcome 是 quota 消费的结构化枚举，不是从 `classification` 推断的后缀。
新写应使用其中之一：

| 值 | Quota 含义 |
| --- | --- |
| `surface_only` | 有用的面工作，但不是主结果证据；推进 todo 仍开放时可能触发 follow-through。 |
| `outcome_gap` | Run 暴露了具体 blocker 或缺失结果；后续应推进结果或写精确 blocker。 |
| `outcome_progress` | 可问责 delivery 进度，可能在验证/writeback 后有资格 spend。 |
| `primary_goal_outcome` | 所选阶段的主结果完成；它满足 outcome-floor recovery。 |

`classification` 保持为人类/历史标签。Quota 只能把旧执行 profile 提示当作
历史 run 的兼容 fallback；新控制面决策应由上面的枚举驱动。

一个 `outcome_gap` 不会变成 delivery 进度。只有当同一 writeback 包含
`typed_progress_observation_v0` 且 `result_class=blocked`、匹配的 `work_item_id`、
稳定 `blocker_id` 与非空稳定 `evidence_ids` 数组时，它才能结算并花一个确切
Todo 绑定 Turn。缺失 schema、仅散文 blocker、畸形证据与 Todo 身份不匹配保持
fail-closed。

`quota should-run` 还把长时观察与应推进所选目标的工作分开。当所选目标的当前投影
是仅依赖观察时，payload 包含 `work_lane_contract` 且 `lane=continuous_monitor`。
如果开放 agent todos 存在，schema `work_lane_contract_v1` 现在把 todo 条目分类为
`task_class=advancement_task` 或 `task_class=continuous_monitor`。Agent 应用
`loopx todo add --task-class advancement_task --action-kind <token>` 注册可执行工作，
而不是依赖自动化提示里的项目特定短语。guard 把显式 `task_class` 当作权威，
用识别的通用 `action_kind` 令牌作为其次信号，并只对更旧复选框回退到保守文本分类。
它只在至少一个开放 todo 是推进类工作时设置 `next_lane=advancement_task`、
`obligation=advance_unless_material_monitor_transition`、`must_attempt_work=true`
与原因代码，如 `dependency_observation` 和 `open_agent_todo`。
如果所有可见开放 todos 都是 monitor 类且没有隐藏开放 todo，同一契约使用
`obligation=quiet_until_material_monitor_transition` 与 `must_attempt_work=false`。
隐藏开放 todos 当作推进工作处理，避免截断的 top-N todo 投影造成虚假 quiet no-op。
显式说在 owner 证据、凭据、基底证明或另一个前置条件存在前不要运行/启动的开放
agent todos 是 monitor 类 blocker，而非可执行推进工作；有开放用户 todo 时，
应把该 todo 保持 `user_todo_summary` 可见，而不把未变化的合格 monitor 轮询变成
blocker-push 通知。
如果所选目标的 `next_action`/`recommended_action` 显式指向可执行链，
如收集或聚合重复然后重建标签、重跑 scorer 或验证 eval gate，
monitor-only todos 不得让目标安静。契约改用
`obligation=materialize_advancement_todo_or_blocker` 与 `must_attempt_work=true`，
让 worker 要么物化具体推进 todo，要么写阻止它的 blocker。
`heartbeat_recommendation` 随后应说 `follow_work_lane_contract` 或
`monitor_quiet_until_material_transition`，而不是编码另一个项目特定分支。
当它改变所选目标决策时，执行者仍可记录一次材料依赖状态转移，
但未变化 monitor 轮询是 `should_run=false` 与
`effective_action=monitor_quiet_skip` 的安静无 spend 检查。这让监控有用，
而不让它消耗每个合格 turn，并把硬路由规则保持在一个小机器契约里。
当当前 Agent lane 只有 monitor 工作且没有当前、未声明或其他 Agent 推进边界时，
有效的未来 `next_due_at` 是显式等待状态：quota 用 typed `future_monitor_wait` 规则，
返回 `monitor_quiet_skip`，并调度下一次有界唤醒，而不要求合成 replan。
到期的 monitor 通过 `due_monitor_execution` 保持可执行。缺失或无效调度、
无变化连续段、vision/succession 缺口、用户 gate 与真实 blocker 仍进入其
更高优先级修复或 replan 规则。来自另一 Agent lane 的投影 ACK 保持诊断，
不能清除当前 lane 义务。

可执行 todos 也可以通过 todo 元数据声明显式写作用域需求，例如
`required_write_scopes=runner%2F%2A%2A` 或 CLI 标志
`loopx todo add --required-write-scope runner/**`。在普通 delivery 前，
`quota should-run` 把第一个可执行推进 todo 的 `required_write_scopes` 与
`goal_boundary.write_scope` 比较。如果当前边界不覆盖所选作用域，
guard 为有界修复 turn 保持 `should_run=true`，但设置
`normal_delivery_allowed=false`、`effective_action=boundary_projection_repair` 与
`blocked_action_scope=boundary_projection`。worker 在尝试写之前必须修复
checkpointed 边界投影、在现有边界内重写 todo，或写具体用户/controller gate。

可执行 todos 也可以声明环境能力需求，例如
`required_capabilities=shell%2Cbenchmark_runner` 或 CLI 标志
`loopx todo add --required-capability benchmark_runner`。
这不是全局 Agent profile，也不是权限系统。它是逐 todo 执行预检，
让 guard 区分"quota 可用"与"这个步骤在当前环境里真的能跑"。
用 `required_capabilities` 表示前置条件，而不是表示 todo 要创建的能力。
修复、开发、物化或 parity 检查 bridge 能力的 todo 应用 `target_capabilities`
声明那一输出侧。目标能力为可见性与修复模式路由而投影，但它们不是硬执行 gate。

`quota should-run` 把可见可执行推进队列与当前 launcher 能力比较。
`shell`、`filesystem_read` 与 `filesystem_write` 等基础本地能力默认假设；
launcher 可以用 `--available-capability` 增加临时能力，例如：

```bash
loopx --format json quota should-run \
  --goal-id <goal-id> \
  --available-capability benchmark_runner
```

验证 turn 后在 `quota spend-slot` 使用相同 `--available-capability` 标志，
因为 spend 预览在写 quota 记账前重算同一 should-run guard。

结果 `capability_gate` 是只读投影：

```json
{
  "schema_version": "capability_gate_v0",
  "action": "run",
  "required": ["shell", "filesystem_write"],
  "missing": [],
  "decision_owner": "agent",
  "selection_policy": "agent_steering_audit_over_runnable_candidates",
  "runnable_candidates": [
    {"todo_id": "todo_docs"}
  ],
  "blocked_candidates": [
    {
      "todo_id": "todo_eval",
      "required_capabilities": ["shell", "benchmark_runner"],
      "missing_capabilities": ["benchmark_runner"]
    }
  ]
}
```

多个 P0/P1 条目按有序队列处理，而不是单一所选 todo。guard 按投影顺序扫描
可见可执行候选，并在 `runnable_candidates` 投影哪些候选真实可运行；
Agent 随后在 steering audit 中选择推进哪个可运行条目。可运行 P0 在任何 P1
fallback 前保持可见，但 LoopX 不把该顺序变成自动最终选择。被阻塞的高优先级
候选保持 `blocked_candidates` 可见。如果每个可见可执行候选都缺能力，
gate 对可修复本地 bridge（如 `benchmark_runner`/`external_evidence_poll`）
与运行时供给（如 `network`）返回 `action=repair_bridge`，
对 owner 持有能力（如 `credentials`/`production_access`）返回
`action=ask_owner`，或对不支持的能力类别返回 `action=skip`。

当多个同 Agent 动作被准入时，`quota should-run` 通过
`action_portfolio.suggested_actions` 让该选择可读：一个有序推荐加至多两个
替代。这些建议为可读性而有界，且显式非穷举；推荐是默认，不是绑定或权限列表。
第一次响应设置 `interaction_contract.cli_channel.selection_required=true`，
返回一个 typed `selection_command.command_args_template`、共享绑定 `route_prefix`、
紧凑 `candidate_discovery_args`，并创建无身份 heartbeat 收据。在 steering audit
后，Agent 可以用发现命令检查权威开放 Agent 队列，然后用任何当前权威、
同 Agent、能力就绪的 Todo 渲染模板，包括未在有界建议中显示的一个。
该请求只是待决选择：第二个 guard 在升级收据前重跑当前 lane 仲裁与资格检查。
新到期的高优先级 monitor、阻塞用户 gate 或其他当前抢占会推迟请求并让收据保持
无身份。Delivery 与 quota spend 在绑定成功前保持禁用。单候选响应保持直接执行
路径，不增加额外选择往返。

当所选 Todo 有意义的策略上下文时，同一默认响应可以包含
`planning_horizon.schema_version=quota_planning_horizon_v0`。它携带至多
五个选中/相关/可运行或更高优先级等待 Todos、八个 typed
lineage/resume/route 关系、两个目标接受缺口与显式完整性计数器。
Horizon 是只读 steering 输入：`selection_contract.horizon_changes_selection=false`
且动作权威保持 `selected_todo` 加 `action_portfolio`。如果 horizon 暴露了
更好的可运行条目，Agent 仍使用现有候选发现与显式选择重入。如果它被截断，
Agent 在把可见切片当作穷举前遵循其 Todo-detail 或 task-graph 冷路径引用。见
[`quota_planning_horizon_v0`](reference/protocols/quota-planning-horizon-v0.md)。

Portfolio 与 horizon 不独立重建 Todo 队列。Python 选择 canonical Todo 领域状态行，
TypeScript 将其归一化为一次 `todo_planning_inventory_v0`。Inventory 保持
`planning_state` 独立于 `claim_state`，因此未声明的可运行条目明确要求先声明再
工作。`--include-detail agent-todos` 暴露更大的有界规划视图，
并把其条目细节指回 `agent_todo_summary`；horizon 的 `full_todo_list` 命令读取
完整开放 Agent 队列。溢出通过完整性计数器报告，而不是让只读 quota guard 失败。
Task graph 使用相同 canonical Todo 行，同时扩展终态前置/证据行，
并保持带独立 gate/证据上下文的 Agent 中性读模型。

被阻塞候选即使另一个 todo 可运行也保留 typed `resolution_bindings`。
每个绑定点名能力、其解决 owner 与确切 `blocked_todo_ids`。交互契约把 owner 持有
绑定变成由 `unblocks_todo_id` 链接的幂等范围化 `user_gate` 写，
而 Agent 可修复绑定变成 `target_capabilities` 含有该能力的幂等推进 todo。
用户 gate 不阻塞无关可运行 todos。`quota should-run` 保持只读；Agent 或 host
在普通 writeback 前执行投影的 todo 写。

完成修复或 owner todo 不是运行时能力可用的证明。当前 host 仍必须验证真实
callsite，并在预检与 spend 都传 `--available-capability`。这保持能力真相
会话作用域化，并防止过期的持久授予。

运行时能力缺失不是权限权威。因此缺失 `network` 声明保持在 Agent 修复 lane：
Agent 应观察或修复 launcher/runtime bridge，验证后如实传
`--available-capability network`，或写具体运行时 blocker。
LoopX 不得把该条件变成用户批准请求。

当缺失的可修复 bridge 本身就是 todo 目标时，例如
`required_capabilities=shell` 加 `target_capabilities=benchmark_runner`，
候选保持 `runnable_candidates` 中，带 `capability_repair_mode=true`、
`capability_action=repair_bridge` 与候选本地 `missing_target_capabilities`。
这避免循环 gate：一个 todo 不能因为没有 `benchmark_runner` 而开发
`benchmark_runner`。

多 Agent handoff 使用与所有其他 agent todos 相同的排序。评审是 `action_kind`，
不是调度等级。`excluded_agents` 可以防止点名 peer 声明或执行否则普通的 handoff，
而 `unblocks_todo_id` 记录依赖谱系。Active-next 对齐、声明、优先级、能力 gate、
写作用域、用户 gate 与验证继续决定可执行动作。

延迟 todo 可见性是独立 gate-resume lane，不是可执行积压，也不属于无候选
quiet-wait 语义。Status/quota 可以在排序开放 todo lane 后暴露至多八个排序
`deferred_items` 与至多八个就绪 `deferred_resume_candidates`。在 Agent 作用域
`quota should-run --agent-id <peer>` 中，所有延迟条目可以保持诊断可见，
但只有当前 Agent 声明或保持未声明的就绪候选能唤醒该 peer。如果这样的候选存在
且没有开放当前 Agent/未声明推进 todo，quota 返回
`effective_action=successor_replan_required`、`normal_delivery_allowed=false`
与 `execution_obligation.contract = deferred_resume_projection`。worker 必须
重新打开、替代或记录 public-safe 无后续理由，然后才能普通 delivery 工作。
只在没有就绪当前 Agent/未声明延迟恢复存在时，Agent 作用域 quota 才落入
`agent_scope_wait`、`reassignment_required` 或 `scope_exhausted`。

优先级在恢复边界间保持权威。当就绪当前 Agent 或未声明延迟 successor 严格高于
所选开放推进 todo 时，quota 也在较低优先级 delivery 前返回
`successor_replan_required`。延迟条目不能就地变为可执行：`selected_todo`
指向延迟 successor，让 worker 显式重新打开、替代或关闭它，而
`goal_frontier_projection.deferred_successors.top_ready_todo_id` 报告同一
生命周期目标。同优先级开放 todo 保持可执行，避免优先级桶内不必要的生命周期折腾。

无关 `user_action` 可以为本 turn 增加可见 `NOTIFY` 通知，但它不能替代所选
生命周期义务或把它变成用户等待。此处 `delivery_allowed=false` 禁止普通材料
delivery；它不取消 `execution_obligation.must_attempt_work=true`。最终交互契约
因此保持 `mode=successor_replan_required`，把通知投影为 `non_blocking=true`，
保留 Todo 生命周期 CLI 动作，并让 scheduler 停留在 active-work cadence。
当显式 `user_gate` 的决策作用域覆盖所选生命周期动作时，它仍优先。

开放 todos 带 `resume_when` 时使用同一就绪信号，再进入普通执行 lane。
在 `resume_ready=true` 前，quota 不得把该 todo 包含进
`capability_gate.runnable_candidates` 或 `agent_lane_next_action`；
当交互契约允许安全作用域 fallback 工作时，它可以继续较低优先级可执行 fallback。
动作 portfolio 把更高优先级 typed 等待保持为 `availability_reason=resume_condition_pending`
可见，同时让可运行 fallback 及其有界延续上下文成为默认模型面向动作。

如果活跃的每 Agent vision 没有其他可选推进，且其现有当前 Agent 或未声明
successor 被一个确切支持的 `resume_when` 阻塞，quota 投影
`vision_wait_state.state=waiting` 与 `agent_scope_wait`，
而不是派生另一个自主 vision replan。等待 payload 保留 todo id、条件与自动恢复
契约。一旦 `resume_ready=true`，等待消失，普通开放 todo 或延迟 successor
选择再次运行。缺失 vision checkpoint、关闭阶段 succession、不支持条件与
continuous-monitor-as-gate 修复保持 fail-closed，不被该等待路径隐藏。

对已完成的 handoff gate，结构化记录该理由为 `no_followup=true`；
status 把 gate 投影为 `cleared_no_followup`，而不是用
`successor_replan_required` 唤醒被阻塞 Agent。

外部证据等待有额外的 CLI 级观察契约。当所选目标是 `state=waiting`、
`waiting_on=external_evidence` 且其当前 lane 是持续 monitor，或 active state 说
已启动长时外部 worker 且当前动作是轮询紧凑结果/标记时，
`quota should-run` 返回
`external_evidence_observation.schema_version = external_evidence_observation_obligation_v0`。
guard 保持 `should_run=false` 使普通 delivery 保持阻塞，但设置
`effective_action=external_evidence_observe` 与
`execution_obligation.kind=external_evidence_observation_required`，
`must_attempt_work=true`。执行者必须在把轮询当作未变化证据前验证只读可观察
handle，如线程 id、自动化 id、作业 id、锁/结果标记或紧凑 writeback 路径。
如果该 handle 缺失、过期或从未启动，写回紧凑 blocker 或启动就绪故障，
而不是返回 quiet no-op。

对自主 heartbeat，未变化 monitor 轮询可以记录为无 spend 停滞证据：

```bash
loopx --registry "$HOME/.codex/loopx/registry.global.json" quota monitor-poll --goal-id <GOAL_ID> --source heartbeat --execute
```

`quota monitor-poll` 在当前 guard 是 quiet monitor skip、外部证据观察、
或由 `work_lane_contract.obligation=attempt_due_monitor` 选择的到期
`continuous_monitor` todo 时有效。对到期 monitor todos，传 `--todo-id` 或
`--target-key` 加公共 `--result-hash`；未变化轮询更新 `last_checked_at`、
`next_due_at` 与 `consecutive_no_change`，而不追加 `quota_slot_spent`：

```bash
loopx quota monitor-poll --goal-id <GOAL_ID> \
  --todo-id <TODO_ID> --result-hash <HASH> --execute
```

当轮询看到实质转移时，加 `--material-change`，可选用 `--next-agent-todo` 或
`--next-user-todo`，让 monitor 产生具体后续，而不是保持不透明 watch。
用户后续必须显式声明
`--next-user-task-class user_gate|user_action`：阻塞 owner 决策用 `user_gate`，
必须不阻塞绑定 Agent lane 的可见提醒用 `user_action`。省略 task class 会在
writeback 前失败。Monitor 保持观察-only `continuous_monitor`；
`--next-agent-todo` 创建独立可运行 `advancement_task`。对应 generation-fenced
等待 Todo 配方见
[项目 Agent Todo 契约](project-agent-todo-contract.md#machine-readable-resume-conditions)：

```bash
loopx quota monitor-poll --goal-id <GOAL_ID> \
  --target-key <TARGET_KEY> --result-hash <HASH> --material-change \
  --next-user-todo "<PUBLIC_SAFE_REVIEW_REMINDER>" \
  --next-user-task-class user_action \
  --next-agent-todo "<PUBLIC_SAFE_FOLLOW_UP>" --execute
```

命令追加 `quota_monitor_poll` run 记录，不改 registry，不追加
`quota_slot_spent`。Run 包含 `quota_monitor_target_v0`，即公共 monitor 身份的
紧凑哈希。版本化 `quota.monitor_poll.commit` TypeScript 事务拥有准入重验证、
该目标/事件构造、同效应重放、index CAS 与可修复 JSON/Markdown/index 写集。
无 Todo 目标的轮询跨受管运行时一次。Todo 目标使用 fail-closed provider 预检，
随后一次最终提交；保留的 Todo writer 持久化 monitor 效应身份，
使崩溃重试不能推进计数器两次，也不能让较旧观察覆盖较新的。

同一具体到期/外部 monitor Todo 或目标连续六次未变化执行，把
`autonomous_replan_obligation` 喂给 `dead_monitor_repeat`，
所以下一次独立 `quota should-run` 可以翻到 `autonomous_replan_required` /
`execution_obligation.must_attempt_work=true`；执行者随后应记录 watch-lane 过期、
具体 blocker、todo supersede 或可运行 successor todo，而不是又一次 quiet skip。
自动 `quota should-run` heartbeat 存活收据没有具体的已执行 monitor 身份，
不计入该阈值；不同 heartbeat turn id 是幂等证据，不是 monitor 执行证据。

在该有界 replan 切片被携带 `autonomous_replan_ack_v0`与
`repair_delta_contract_v0`（`delta_present=true`）的紧凑状态 run 确认后，
同一已确认等待的后续空 monitor 轮询不会反复重新触发 replan。
诸如 `monitor_poll_autonomous_replan_recorded_v0` 的纯分类不足够。
`delivery_completion_spend_accounted_v0` 等仅记账 run 保持中性存活记录；
它们本身不关闭 replan 义务。空轮询保持无 spend 存活检查，直到出现实质 monitor
转移、回归或具体 blocker。

同一 guard 暴露 `automation_liveness`。对 `monitor_quiet_skip`，
它必须说 `automation_action=keep_active_quiet`、`keep_active=true` 与
`pause_allowed=false`：未变化的 monitor-only 轮询不是取消循环自动化的理由。
暂停/删除保留给两种情形之一：由 LoopX 从完整、有效 todo 来源、无后续关闭证据
与空归一化边界派生的只读终态；或自身再卡两个合格 turn 的有界自修复/replan 路径。
终态情形投影 `automation_action=stop_terminal_no_followup`、
`keep_active=false` 与 `pause_allowed=true`；原始 status/attention 字段不是
终态权威。缺失或畸形来源与任何开放 todo、monitor、successor、接受缺口、
自主 blocker 或 replan 义务都 fail closed。这让循环 controller 在普通等待中存活，
同时在不额外花配额 turn 的情况下尊重显式完成的目标关闭。

单个已注册 peer 可以改为置入 `monitor_only` 工作模式：

```bash
loopx configure-goal --goal-id <goal-id> \
  --agent-work-mode <agent-id>=monitor_only --execute
```

这抑制该 peer 的推进、自主 replan、修复、fallback 与新主题 lane，
而保留到期 `continuous_monitor` todos 与验证的直接 operator 回复。
未来或未变化的 monitor 保持安静且无 spend；到期 monitor 只能在验证实质转移后
spend。其他 peers 保持活跃。用 `--clear-agent-work-mode <agent-id>`
（或设为 `=active`）恢复普通推进。

读模型把该派生暴露为
`goal_frontier_projection.terminal_state={kind:no_followup, derived:true,
source:validated_goal_closure}` 加
`source_completeness.user_todos=valid` 与
`source_completeness.agent_todos=valid`。生产者从结构化 todo 条目派生来源
证明与关闭意图；调用方不能通过写 `attention_queue.status` 或 registry
attention 文本来授权关闭。

`automation_liveness` 刻意不设置轮询 cadence。guard 还暴露 `scheduler_hint`，
它是 host 运行时调度契约：Codex App 自动化在长等待期间应渐进后退到推荐
间隔/最大值，而 Codex CLI TUI 与 Claude Code loop 应在其未变化轮询上限后运行
一次最终 `quota should-run` replan 检查，并在 guard 仍未变化时退出或停止。
Cadence 变更、最终检查与自停 turn 永不 spend 配额；只有验证 delivery 或允许的
writeback 会。

Scheduler 归属是显式的。裸 `quota should-run` 仍可暴露 quota 决策，
但其 `scheduler_hint` 以 `repair_scheduler_execution_context` fail closed；
它永不假设 Codex App。生成的 Codex App heartbeat 传显式
`codex_app_heartbeat` profile；生成的命令用其紧凑别名 `--codex-app`。
其他 host 传 typed `--host-surface`、`--scheduler-owner` 与 `--execution-mode`
三元组描述消费该 hint 的运行时。

## 计算状态

推荐的紧凑状态：

- `eligible`：目标可以消耗下一个自动 Agent turn。
- `focus_wait`：目标原则上可被 Codex 编址，但当前 delivery 焦点被延续边界
  或缺少新意、owner 证据、外部 eval 或干净基线而刻意暂停。
- `throttled`：目标健康但已花完当前计算配额。
- `waiting`：目标等待外部证据或目标 controller，因此暂不应花计算。
- `operator_gate`：目标在更多计算有用前需要人类决策。
- `paused`：计算配额为 `0` 或 operator 暂停了目标。
- `blocked_health`：目标在更多工作运行前必须修复 registry、契约或边界问题。

这些是 dashboard 的产品状态。Adapter 分类保持下钻细节。

## Dashboard 含义

Dashboard 应把计算配额显示为紧凑控制面：

- quota 芯片：`1.0`、`0.5`、`0.3`、`0`；
- 当前窗口的已花/允许分钟槽位；
- 只有 `allowed_slots` 被手动设离窗口派生默认时才显示显式覆盖标记；
- throttled 时的下一个合格时间；
- 简单 operator 动作：设置 quota、暂停、恢复或授予临时突发；
- 按"应收到下一个自动 turn"排序的 next-turn 视图。

首屏应让一个项目为何安静显而易见：

- 等待证据；
- 被 operator 关卡；
- 因当前 lane 在另一个 delivery turn 前需要新意、证据或干净基线而处于 focus wait；
- 被计算配额节流；
- 被暂停；
- 或者合格且下一个应运行。

## CLI 面

首批只读或预览命令是：

```bash
loopx quota status
loopx quota plan
loopx --format json --registry "$HOME/.codex/loopx/registry.global.json" quota should-run --goal-id <goal-id> --runtime-profile codex_app_heartbeat
loopx --registry "$HOME/.codex/loopx/registry.global.json" quota spend-slot --goal-id <goal-id> --slots 1
loopx --registry "$HOME/.codex/loopx/registry.global.json" quota spend-slot --goal-id <goal-id> --slots 1 --execute
```

这些命令复用 status 契约，包括契约健康、全局 registry 健康、attention queue、
run history 与派生 quota 状态。它们不改 registry、运行时历史、reward overlay
或 operator gate。项目 heartbeat 提示应对 `should-run` 与 `spend-slot`
使用共享全局 registry，使它们看到与 dashboard 相同的 operator gate、用户 todos
与 quota 状态。`refresh-state` 与 `todo add` 等项目本地状态写仍在来源项目发生，
并把其 public-safe 投影同步回全局 registry。

`quota status` 是面向 Agent 的宽泛清单：它显示每个注册目标处于
`blocked_health`、`operator_gate`、`focus_wait`、`eligible`、`waiting`、
`throttled` 或 `paused`。

`quota plan` 是自动化的 next-turn 视图：它在 Markdown 输出隐藏空组，
并在目标合格时高亮 `next_automatic_turn`。如果该值是 `none`，
自动化应跳过 delivery 计算并遵循显示的 gate、证据或健康原因。

`quota should-run` 是 heartbeat 作业的每目标 guard。它返回一个小 JSON 或
Markdown 决策：

其健康 gate 也是每目标的：全局契约错误与归所选目标所有的错误 fail closed，
而其他目标拥有的错误保持在宽泛 status 清单可见而不阻塞本决策。错误归属来自
结构化契约诊断，绝不来自从错误字符串解析 goal-id 前缀。

```json
{
  "goal_id": "project-main-control",
  "decision": "skip",
  "should_run": false,
  "state": "operator_gate",
  "reason": "operator gate blocks gated delivery; safe non-gated steering may continue",
  "blocked_action_scope": "gated_delivery",
  "safe_bypass_allowed": true,
  "heartbeat_recommendation": {
    "source": "quota.should-run",
    "recommended_mode": "ask_operator_gate",
    "notify": "NOTIFY",
    "spend_policy": "do not append quota spend while asking the operator gate"
  },
  "scheduler_hint": {
    "schema_version": "scheduler_hint_v0",
    "action": "backoff_waiting_for_user",
    "codex_app": {
      "recommended_interval_minutes": 30,
      "example_progression_minutes": [30, 60]
    },
    "unchanged_poll": {
      "limits": {
        "local_scheduler": 3,
        "codex_cli_tui": 3,
        "codex_app_ssh_goal": 3,
        "claude_code_loop": 3
      },
      "after_limits": {
        "local_scheduler": "stop_tick_loop",
        "codex_cli_tui": "update_goal_blocked_keep_loopx_active",
        "codex_app_ssh_goal": "update_goal_blocked_keep_loopx_active",
        "claude_code_loop": "stop_loop"
      },
      "final_quota_replan_check_enabled": true,
      "final_quota_replan_check_action": "rerun_quota_should_run_once",
      "spend_policy": "no quota spend for final replan check or loop stop"
    },
    "detail_ref": {
      "schema_version": "scheduler_hint_detail_v0",
      "omitted_by_default": true,
      "execution_required": false,
      "request": "loopx quota should-run --include-detail scheduler",
      "hot_path_runtime_fields": [
        "codex_app",
        "unchanged_poll",
        "reset_policy"
      ],
      "contains": [
        "local_scheduler",
        "codex_cli_tui",
        "codex_app_ssh_goal",
        "claude_code_loop",
        "final_quota_replan_check",
        "reset_policy_detail",
        "stateful_backoff_detail"
      ]
    },
    "reset_policy": {
      "reset_token": "0123456789abcdef",
      "host_state_key": "scheduler_hint.reset_policy.reset_token",
      "codex_app_initial_interval_minutes": 30,
      "codex_app_initial_rrule": "FREQ=MINUTELY;INTERVAL=30",
      "identity_signature": "123456789abc"
    }
  },
  "operator_question": "是否同意 project-main-control 先做 read-only map dry-run？",
  "gate_prompt": "请用户/控制器确认当前 gate：..."
}
```

只有 `state=eligible`、outcome-floor recovery safe-bypass 或 registry 启用的
控制面自修复返回 `should_run=true`。被 gate、focus wait、waiting、throttled、
paused 或 health-blocked 的已知目标只在 status 导出本身健康时返回 `ok=true`，
但其他情况返回 `should_run=false`。
`safe_bypass_allowed=true` 不是清理 gate 的权限；它只说 Agent 可以在独立只读
steering/分析上花一个有界 turn。
对 `state=operator_gate`，`quota should-run` 在字段可用时还应表露
`gate_prompt`、`operator_question`、`next_handoff_condition`、`missing_gates`、
`user_todo_summary` 或 `agent_todo_summary`。Heartbeat 应使用该提示向用户或
目标 controller 问具体 gate，而不是静默跳过，除非同一未决 gate 最近已在可见
线程中问过。如果 `user_todo_summary.open_count > 0`，现有开放用户 todos 本身
就是用户可见动作；这些 todos 保持开放时不要报告 "no new user action"。
这也适用于有界 safe-bypass 步骤之后：紧凑报告仍必须列出现有开放用户 todos，
而不是说没有用户动作。如果 `agent_todo_summary.open_count > 0`，
Agent 应使用该摘要作为其下一个安全后续清单，而不是挖掘聊天历史或超长
`Next Action`。

对 Agent 作用域 quota 请求，`user_todo_summary.open_count` 只计绑定到该
Agent 的用户 todos 加显式 `goal_bound=true` 条目。绑定到另一 Agent 的 todos
保持 `other_agent_bound_user_action_items` 供诊断，但不得保留继承的
`operator_gate`、进入 `interaction_contract.user_channel` 或触发 heartbeat
通知。在多 Agent 目标中，todo 编写必须使用 `--bound-agent <registered-agent>`
（作者与绑定 lane 相同时用 `--agent-id`）或 `--goal-bound`；
`claimed_by` 不是用户 todo 路由字段。

对 `state=focus_wait`、`state=waiting` 或 `waiting_on=external_evidence`，
开放用户 todo 可以是安静项目的最小解锁。那时 `quota should-run` 应设置
`notify_user_on_open_todo=true` 并包含 `open_todo_notify_reason`。目标 heartbeat
应返回紧凑 `NOTIFY`，列出至多三个开放用户 todos 与期望回复（`done`、
`defer/not now` 或新证据链接/日期/结论），同时为该 blocker-push turn 跳过
delivery 工作与 quota spend。如果 quota 还设置
`open_todo_notification_policy=repeat_until_resolved`，重复该通知直到 todo
完成、延迟或被替换。如果失败的 host cadence 更新留下更紧的轮询，
`user_gate_notification_cooldown_v0` 保持 gate 打开但在有界提醒窗口外抑制
重复通知。否则，同一 blocker 最近已被表露时 blocker-push 情形仍可去重。
合格 monitor-only 无转移轮询把开放用户 todo 保持 `user_todo_summary` 可见，
但不得强制重复通知、使 turn 变成用户动作 gate，或为否则安静 no-op 保留顶层
`should_run`。

Cooldown 抑制对阻塞诉求与非阻塞 `user_action` 通知都优先：最终
`interaction_contract.user_channel` 必须是
`action_required=false, notify=DONT_NOTIFY`，且不得保留动作列表。
Goal Channel delivery 添加按 gate 身份、其材料状态世代与（仅到期时）显式提醒
窗口世代键控的 sink 本地重放围栏。复制变更、推荐更替与 provider 读回缺失不会
创建新的发送世代；实质 Todo 转移或新显式提醒窗口会。

Monitor 追赶在可运行 lane 间也有界。两次连续未变化 monitor-only 工作 turn 后，
`monitor_debt_arbitration_v0` 优先同或更高优先级的推进 todo，而非另一个逾期
monitor，包括范围化用户 gate fallback 选择内。Scheduler/记账与 state-refresh
行不打断连续段；真实推进或实质 monitor 转移会。直接 Lark 收件箱 `reply_due`
工作保持更强抢占，绝不被此公平性退避延迟。

对每个注册目标，`quota should-run` 还包含一个 `todo_write_hint`，
让 Agent 执行者知道用 `loopx todo add --role user --task-class user_gate|user_action`
写新发现的用户/owner 工作，而不是藏在 `Next Action`、评审文档或聊天里。
多 Agent 写还必须点名 `--bound-agent <registered-agent>` 或 `--goal-bound`；
Agent 作用域 `user_gate` 写绑定到 `--blocks-agent` 点名的同一 Agent。
可用时，`quota should-run` 还保持 next-action 信号分离：
`active_state_next_action` 是持久 `## Next Action`，`latest_run_recommended_action`
是最新非 Agent lane run 的推荐，而 `agent_lane_next_action` 是当前 `--agent-id`
切片。Agent 作用域 payload 还可以包含
`goal_route_hint.schema_version=goal_route_hint_v0`，一个紧凑只读综合，
说明当前 lane 应 run、claim、wait 还是 reassign，同时把 `## Next Action` 保留为
持久目标级指导。它是建议性路由提示，不是写回指令，也不是
`agent_todo_summary` 的替代品。
投影时，`goal_frontier_projection.schema_version = goal_frontier_projection_v0`
是在 lane 本地 quiet 或 wait 决策前使用的每目标进度/边界视图。其
`autonomous_replan_decision` 说明必需 replan 必须独立于 `monitor_quiet_skip` 或
`agent_scope_wait` 选择；策略住在
`loopx.control_plane.goals.goal_frontier`，而 quota 只把所选模式接入
`interaction_contract`。
如果 active-state 与 latest-run 动作不同，`next_action_projection_warning` 要求
执行者用主目标作用域 `refresh-state --next-action` 显式写回预期的持久路线，
或把信号保持为不同信号。
`refresh-state` 记录 `recommended_action_source`，使 host 能说出 run 推荐来自
显式参数、持久 `## Next Action`、Agent Todo 兼容 fallback 还是通用默认。
分发仍来自 `agent_lane_next_action` / todo 投影，而不只是共享 `## Next Action`。
当 `agent_lane_next_action.selected_by=unclaimed_todo` 时，payload 标记
`claim_required_before_work=true`；执行者必须在编辑或启动 delivery 工作前声明
该 todo。
对带 `coordination.registered_agents` 的目标，`quota should-run` 接受可选
`--agent-id <registered-agent>`。身份感知 heartbeat 提示通过其 quota guard
传该标志。如果注册目标不带 Agent id 检查，payload 包含
`automation_prompt_upgrade.required=true` 与推荐 `heartbeat-prompt --agent-id ...
--agent-scope ...` 命令。这不翻转 `should_run`；它是过期已安装自动化的轻量迁移
信号。
当 status payload 有同目标过期 checkpoint 决策或更新的采样事件时，
`quota should-run` 包含 `decision_freshness_warning`。该警告不让合格目标跳过；
它防止 worker 把旧 reward、steering note 或 operator gate 当作当前权威。
复用该决策前，worker 必须对照最新 registry、ACTIVE_GOAL_STATE、quota、策略与
run status 重新基准决策点。这不是仓库回滚，也不带整个旧聊天状态向前。
当 status payload 有缺失、过期或未知 canary 晋升就绪证据时，`quota should-run`
还包含 `promotion_readiness_warning`。该警告是附加的：它不改变 `should_run`，
但让 heartbeat worker 与 dashboard 从共享运行时发布 ledger 报告发布就绪
blocker，而不解析 `doctor`、dashboard 文案或聊天报告。新证据存储在那里，
而不是项目 Goal 里。晋升本地发布快照前，运行
`python3 examples/canary/canary-promotion-readiness-smoke.py` 并确认 status
或 doctor 输出中的新鲜证据。`--no-write-evidence` 形式保持非变更验证路径，
因此不会清除该警告。
已连接 delivery 目标在 registry 有边界数据时还包含 `goal_boundary`。该字段携带
adapter 状态、允许写作用域、父批准作用域、registry guard、next probe 与停止
条件。它是项目特定 delivery 边界的优先位置；automation 提示应说遵循
`goal_boundary`，而不是重复很长的受保护文件或动作列表。
它还包含 `heartbeat_recommendation`，把通用 heartbeat 生命周期决策留在 LoopX，
而非一次性 automation 提示。常见模式是：

- `run_first_read_only_map`：已连接只读目标还没有保存的紧凑 run；
  运行一次真实 `loopx read-only-map --goal-id <goal-id>`，验证并保存
  `read_only_project_map`，然后追加恰好一次 heartbeat spend。
- `mapped_noop_if_unchanged`：最新紧凑只读映射已存在；如果没有新用户指令、
  owner 证据、agent todo、过期来源或安全 handoff，返回 quiet no-op，
  不再 dry-run 或 quota spend。
- `steering_audit_then_one_step`：目标合格但需要正常 steering audit 再选择
  一个有界进度片段。当作用域与验证清楚时，连贯实现/测试/状态批量有效；
  契约是有界的，不是微小的。

同一响应包含 `interaction_contract.schema_version = loopx_interaction_contract_v0`，
即所选 turn 的顶层用户/Agent/CLI 协议。它告诉 worker 这是用户 gate、
blocker push、有界 delivery、外部证据观察、monitor quiet skip、自主 replan、
outcome-floor recovery、mapped no-op 还是 quota throttle。它还点明用户是否必须被打断、
Codex 是否必须尝试工作、delivery 是否允许、quiet no-op 是否允许，
以及 quota spend 是否只在验证后允许。执行者应先读该对象。
响应还包含 `scheduler_hint.schema_version=scheduler_hint_v0`。该 hint 不是
delivery 权限。它是跨运行时等待策略：`run_now` 对必需工作保持活跃 cadence；
`backoff_waiting_for_user` 减缓 Codex App 并在重复未变化轮询后停止 CLI/Claude
loop；`backoff_until_reassigned` 处理 peer 重分配等待而不过快丢 Agent 间
handoff cadence；`backoff_until_material_transition` 处理 monitor-only quiet
轮询；`backoff_until_fresh_evidence` 处理映射或 post-handoff no-op 等待。
对 Codex App 与本地 scheduler，`recommended_interval_minutes` 是下一个目标间隔。
对 Codex App heartbeat，`recommended_rrule` 只在
`codex_app.stateful_backoff.apply_needed=true` 时发出；如果期望 RRULE 已应用，
它被省略，使 Agent 不再调用 host 工具。
如果该匹配仍需要 reset-token/identity 绑定，`stateful_backoff.ack_needed=true`
且绑定 ack 不经 host 更新运行。
当需要 apply 但会话中没有 `automation_update` 时，`codex_app.fallback_hint`
携带已解析自动化的有界 `loopx-apply-rrule` 命令（备份 `codex-dev.db`、
同步 TOML+SQLite、运行绑定 ACK）。直接 SQLite 编辑绕过 App API，
所以 fallback 只为此缺口投影，绝不作为常规路径；未解析自动化 id 投影
`available=false` 并需要可粘贴 heartbeat gate，而不是猜测。
成功的 host RRULE 更新后，Agent 用 `loopx` 加 `codex_app.ack_hint.cli_args`
记录该事实；当前 payload 用 `quota scheduler-ack-current` 在 LoopX 无 spend 地
推进每 goal/agent scheduler 状态前重读最新 scheduler hint。人类 gate 可以在具体
用户 todo 表露后让 Codex App heartbeat 通过 `[30, 60]`。LoopX 把 Codex App
集成上限设为 60 分钟；更粗等待保持本地 scheduler 可用，而不作为 App heartbeat
RRULE 发出。
CLI 产生的 ACK hint 把该参数向量绑定到产生 `quota should-run` 的确切 registry
与有效运行时根。Host 必须执行完整向量；剥掉其前置全局选项可以把项目启动的
ACK 路由到项目本地 scheduler 状态，而不是共享控制面。当决策被 heartbeat 收据化时，
ACK 与失败 hint 还绑定源 `turn_instance_id`。后续重建同一收据绑定的活跃决策，
再验证其 reset token 与身份；后来的 Todos 或不同无作用域等待 lane 不能替换
请求 host 动作的决策。
Monitor-only quiet 等待走 `[15, 30, 60]`，同时保持同一无 spend monitor-poll
契约，除非 monitor cadence 或到期时间更早封顶推进。15 分钟只是默认 quiet-monitor
下限：低于 15 分钟的显式 cadence 或到期horizon 成为 host 初始间隔，
使下一次唤醒不能发生在 monitor 到期之后。
同一截止时间上限在人类 gate 拥有通知语义时适用：用户动作保持人类 gate，
普通 gate 仍用 `[30, 60]`，但更紧的持续 monitor 唤醒对 host cadence 保持权威。
仅通知 cooldown 继续使用人类 gate 间隔，而不是把 monitor 截止时间变成三分钟
提醒策略。
Agent 作用域等待使用更保守的调整曲线，如 `[10, 20, 30, 60]`，
使 600 秒本地 tick 在进一步冷却前接近现有 Agent 间交互 cadence。
紧凑热路径只携带 host 需要行动的 reset 字段：`reset_policy.reset_token`、
`host_state_key`、`codex_app_initial_interval_minutes`、
`codex_app_initial_rrule` 与短 `identity_signature`。Host 应在未变化轮询间缓存
并比较 `reset_token`，并在 token 变化时重置未变化连续段。token 由 scheduler
动作加当前身份/profile 输入派生；解释性 reset profile、profile 签名、reset
条件摘要与 stateful-backoff 策略在调用方请求
`loopx quota should-run --include-detail scheduler` 时住在
`scheduler_hint.cold_path_detail`。Host 还应在外部事件使目标再次可执行时重置，
例如线程中的用户反馈、新或重分配 todo、已解决 gate 或实质证据转移。
重置在再次开始未变化退避前应用 `codex_app_initial_interval_minutes`
（与匹配的本地 scheduler 初始间隔）；它永不 spend quota。
对 Codex App heartbeat，host 与 Agent 只在
`codex_app.stateful_backoff.apply_needed=true` 且 `codex_app.recommended_rrule`
存在时使用 `automation_update`。`automation_update` 成功后，Agent 必须运行
`codex_app.ack_hint.cli_args`。当前 payload 用 `quota scheduler-ack-current`，
LoopX 随后在运行时根下持久化 `reset_token`、`identity_signature`、
`progression_index` 与 `last_applied_rrule`。重复未变化身份只在已应用 RRULE
完成一个真实间隔后推进 `progression_minutes`。因此即时 post-ACK 调和验证已结算
目标，而不是在同 turn 制造下一个退避目标。变化的
`reset_policy.reset_token` 回到当前 profile 的初始间隔。这给 host 一个紧凑
post-update ack 协议，而无需他们拥有或 diff 整个 quota 状态。如果
`apply_needed=false` 且 `ack_needed=true`，同一命令记录确切匹配的 host 读回，
而不调用 `automation_update`。
如果 `automation_update` 失败或超时，Agent 不得 ACK。LoopX 保持观察到的 host
RRULE 权威。Agent 运行 `codex_app.failure_hint.cli_args` 一次持久化失败
target/observed-host 对，且不花 quota。LoopX 保留至多四个不同对 24 小时，
因此活跃工作与 monitor 等待目标在 host RRULE 未变时不能互相覆盖。后续 heartbeat
对每个保留的确切对暴露 `apply_needed=false` 与
`state_status=host_update_failure_suppressed`。
变化的主机观察使对旧主机记录失败失效，成功 scheduler ACK 只清除目标为被确认
RRULE 的失败。因此 fallback ACK 为另一观察于同一未变化主机的目标保留失败，
阻止下一 turn 重试已知坏 target/host 对。遗留 `host_update_failure` 标量
保持最新兼容投影；新 host 应消费 `host_update_failures`。LoopX 绝不把预期
cadence 当作已应用 cadence。
对观察到的 host 间隔比失败目标更紧的人类 gate，同一 packet 还投影
`user_gate_notification_cooldown_v0`。第一条通知保留；短 host 轮询安静，
每个目标 cadence 打开一个 host 大小的窗口，变化的 gate 身份或 host RRULE
绕过旧 cooldown。这只改变通知方式，不改变底层用户 todo。
`scheduler-ack` 不是第二个 `should-run`：它确认 host 更新或匹配读回，
且不在同一 turn 发出或立即到期一个 successor RRULE。用户反馈、新可运行工作、
重分配或实质证据因此把自动化恢复到当前 profile 初始间隔，再恢复退避。

`quota should-run` 还观察唯一匹配的活跃 Codex App heartbeat（goal + agent +
当前线程）的 RRULE。观察到的 host RRULE 计算 `apply_needed` 时优先于
`last_applied_rrule`，紧凑结果暴露为 `stateful_backoff.host_observation`。
不匹配是 `drift_detected`，所以 host 更新前写入的 ACK——或后来的 host 侧
cadence 回归——不能永久压制修复。该观察只包含 cadence 元数据。如果
reset RRULE 已匹配但其新 reset token/identity 未持久化，`apply_needed=false`、
`ack_needed=true`，绑定 `ack_hint.cli_args` 记录确切读回，而不做 no-op host 写。
缺失或不匹配读回仍需要 `automation_update`；LoopX 从不直接编辑 App manifest。
对 Codex App SSH Goal、Codex CLI TUI 与 Claude Code loop，默认热路径读取
`scheduler_hint.unchanged_poll.limits.<runtime>`。值 `3` 表示第三次未变化轮询
触发 `scheduler_hint.unchanged_poll.final_quota_replan_check_action` 点名的紧凑
最终 quota/replan 检查；如果重跑仍未变化，loop 应用
`scheduler_hint.unchanged_poll.after_limits.<runtime>`。需要更旧每运行时细节对象
的 host 必须用 `quota should-run --include-detail scheduler` opt in，
并读取 `scheduler_hint.cold_path_detail.local_scheduler`、
`scheduler_hint.cold_path_detail.codex_cli_tui`、
`scheduler_hint.cold_path_detail.codex_app_ssh_goal` 或
`scheduler_hint.cold_path_detail.claude_code_loop`。该 opt-in 只是诊断与迁移支持：
忘记 `--include-detail scheduler` 的 host 或 Agent 仍须通过读取
`scheduler_hint.detail_ref.hot_path_runtime_fields` 点名的默认热路径字段
保留核心调度能力。
对原生 Codex `/goal` 运行时（`codex_cli_tui` 与 `codex_app_ssh_goal`），
after-limit 动作只在同一阻塞条件连续重复三个 Goal turn 后调用
`status=blocked` 的 `update_goal`。注册的 LoopX 目标保持活跃，用户用
`/goal resume` 恢复原生 Goal，最终检查与阻塞转移都不花 LoopX quota。
响应还包含 `execution_obligation`，它是把 worker 执行与用户面向通知分开的兼容
字段。`heartbeat_recommendation.notify` 回答"这个 heartbeat 应打扰用户吗？"，
不是"worker 可以跳过工作吗？"当 `execution_obligation.kind=work_lane_contract`
时，硬路由规则是 `work_lane_contract.obligation`；`execution_obligation`
应只把 worker 指向该对象。当
`execution_obligation.kind=external_evidence_observation_required` 时，
普通 delivery 仍阻塞，但在 quiet no-op 前必须做一次只读观察或写紧凑
缺失 handle blocker。当 `execution_obligation.must_attempt_work=true` 时，
短 heartbeat 必须尝试一个有界片段、验证它、写持久状态/事件，并在成功 delivery
后花一次。Quiet no-op 只在机器契约显式说 `must_attempt_work=false` 且不需要
blocker-push 通知时允许。如果 `notify_user_on_open_todo=true`，
turn 应通知用户并跳过 spend，而不是无声消失；确认映射来源未变化后的验证
`mapped_noop_if_unchanged` 保持 quiet no-op 情形。

未知目标或状态收集失败返回非零，使自动化 fail closed。

`quota spend-slot` 是记账 helper。默认仅 dry-run：它显示消耗槽位前后的
should-run 决策且不写任何东西。用 `--execute`，它追加一个紧凑
`quota_slot_spent` 运行时事件。它从不改 registry、reward overlay、operator gate、
write control、私有证据或生产状态。事件是 status 中性的：它保持在 run history
供审计与 quota 计数，但不应成为 status、quota `should-run` 或 dashboard
attention queue 中的当前工作分类。

显示的 before -> after 转移是为被写槽位的同 status payload 投影。后续
`quota status` 与 `quota should-run` 命令从仍在滚动 `window_hours` 内的
`quota_slot_spent` 事件重算 `spent_slots`；如果较旧的 spend 在预览与下次检查
之间过期，即使新事件被追加，可见总数也可以持平或下降。把追加事件路径当作写收据，
把 `spent_slots` 当作当前滚动窗口总数，而不是单调计数器。

Turn 后记账协议：

- 花 delivery 计算前调用 `quota should-run`；
- 做有界自动 turn、验证与状态写回；
- 在 spend 前追加一次可问责 `refresh-state`，带
  `delivery_outcome=outcome_progress` 或 `primary_goal_outcome`。该 run 是
  `spend-slot` 消费的因果 delivery 记录；不带 delivery outcome 的纯
  `state_refreshed` run 是 quota 中性且不能替代它；
- 验证写回后为完成的 turn 追加恰好一个 `quota spend-slot --execute` 事件。
  当 writeback 是把 guard 从 eligible/replan 移到 waiting 的状态刷新时，
  `spend-slot` 仍可一次记账最新未 spending `outcome_progress` delivery run；
  后续重复 spend 被拒绝，因为那时最新 run 是 spend 事件，不是 delivery run。
- quota 中性的 `refresh-state` 记录可以使用自定义 classification。其 refresh
  出处（而不是字面 `state_refreshed` classification）使它不隐藏先前 delivery。
  显式不可问责 delivery 结局与无关事件保持 fail-closed。
- spend 后，可选的纯 state-only refresh 可以更新 dashboard 或 controller 状态。
  spend 后不要再追加可问责进度刷新，因为它会成为新的未 spend delivery 记录；
- 把可问责 delivery 归因保留在产生它的 worktree 上。如果 `refresh-state` 必须从
  独立 registry checkout 运行，传 `--delivery-workspace-path <delivery-worktree>`；
  路径在本地验证，且从持久历史省略。不要把该选项指向用于 peer 工作的 canonical
  checkout。
- delivery 归因不等于 Git。项目没有 Git origin 的已注册单 Agent 目标在 refresh
  运行于注册项目根内时记录无路径 `local_goal` 工作区身份（`loopx:<goal-id>`）。
  这让验证的非仓库工作无中生有仓库地结算。它不削弱 peer 隔离：peer 仓库写仍
  需要 `independent_git_worktree`，且该要求激活时本地目标工作区被拒绝。
- 自主 replan 遵循同一可问责结局规则：在具体 successor、blocker 或
  `outcome_progress`/`primary_goal_outcome` writeback 后 spend，
  但不为 `surface_only` watch-lane 延续或关闭进 `monitor_quiet_skip` 的
  无后续理由 spend。只改变用户 gate、monitor 目标、watch 延续或持久 Next Action
  的 replan 被归一化为 `outcome_gap`，即使调用方请求可问责结局；它必须也改变
  可执行、被阻塞或终态边界，才能算作 delivery 进度。
- 给每个 heartbeat 一个稳定 turn id 并传给 `quota should-run`；guard 提交
  一个幂等收据，对未变化 `monitor_quiet_skip` 幂等追加无 spend 停滞观察，
  再返回 quiet no-op 与自主 replan；
- 不要为安静 `should_run=false` 跳过、预检失败、纯 dry-run 预览或重复记账尝试
  追加 spend；
- 如果 `should_run=false` 但 `safe_bypass_allowed=true` 且 Agent 实际完成有界
  safe-bypass 工作，为那工作追加一个 spend 事件。对
  `safe_bypass_kind=outcome_floor_recovery`，只在验证 ranker/cross-domain 证据
  或具体 blocker 写回后 spend，而不是另一次 surface-only 报告。每个 safe-bypass
  spend 必须有一个最新未 spending 可问责 delivery writeback；单独绕过决策
  从不授权记账。
- 如果 `should_run=true` 且 `effective_action=control_plane_health_repair` 或
  `control_plane_projection_repair`，只在该控制面投影或 blocker 写回验证后
  追加一个 spend 事件。

## Slotted Spend 事件契约

真实 spend 写路径在一个自动 Codex turn 实际消耗配额后追加一个紧凑运行时事件。
最小 public-safe 事件是 `classification=quota_slot_spent` 带嵌套 `quota_event`
对象：

```json
{
  "goal_id": "project-main-control",
  "classification": "quota_slot_spent",
  "quota_event": {
    "event_type": "quota_slot_spent",
    "source": "heartbeat",
    "slots": 1,
    "reason_summary": "one automatic Codex turn completed under an eligible quota guard",
    "delivery_run_generated_at": null,
    "delivery_run_classification": null,
    "before": {
      "should_run": true,
      "state": "eligible",
      "compute": 0.5,
      "window_hours": 24,
      "slot_minutes": 1,
      "spent_slots": 719,
      "allowed_slots": 720
    },
    "after": {
      "should_run": false,
      "state": "throttled",
      "compute": 0.5,
      "window_hours": 24,
      "slot_minutes": 1,
      "spent_slots": 720,
      "allowed_slots": 720
    }
  }
}
```

公共 fixture 是
[`examples/quota-slot-spend-event.example.json`](https://github.com/huangruiteng/loopx/blob/main/examples/quota-slot-spend-event.example.json)。

验证规则：

- 只在新鲜 `quota should-run` 返回 `should_run=true` 后写，或它返回
  `safe_bypass_allowed=true` 且 Agent 完成一个有界 safe-bypass 步骤后写；
- 对 `effective_action=control_plane_health_repair` 或
  `control_plane_projection_repair`，把 spend 当作控制面自修复记账，
  而不是普通 delivery；
- `slots` 必须为正，`after.spent_slots` 必须等于 `before.spent_slots + slots`；
- 如果 `after.spent_slots >= after.allowed_slots`，`after.state` 应为
  `throttled` 且 `after.should_run` 应为 `false`；
- 不要在 quota 事件中包含人类奖励、operator-gate 批准、write-control、私有证据、
  内部链接、原始日志或生产标识符。

该事件是记账，不是权限。它记录在正常健康/证据/quota 检查允许该 turn 后，
或在 operator gate 显式把其阻塞限定到被 gate 的 delivery 路径并允许一个独立
safe-bypass 步骤后，计算被花费。

其他写命令可以留在显式 operator 批准后：

```bash
loopx quota set --goal-id <goal-id> --compute 0.5
loopx quota pause --goal-id <goal-id>
loopx quota burst --goal-id <goal-id> --slots 2 --dry-run
```

重要行为是：自动化在花计算前问 LoopX 目标是否合格。它们不应只依赖自己的 cron
周期作为优先级模型。

## 验收标准

- 每个活跃目标可以暴露 `1.0`、`0.5`、`0.3` 或 `0` 这样的计算配额。
- `loopx status` 可以在自动化再花一个 turn 前说明目标合格、节流、等待、
  暂停还是受阻。
- 共享 controller 可以按计算配额对合格目标排序，而无需打开每个项目 Agent 线程。
- 每目标自动化可以用同一配额跳过一些 ticks，并带紧凑理由。
- 改变自动化 cadence 不再是表达项目优先级的主要方式。
