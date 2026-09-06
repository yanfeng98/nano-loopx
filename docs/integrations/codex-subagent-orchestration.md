# Codex 对等任务编排

> [English](codex-subagent-orchestration.md)

LoopX 支持两个不容混淆的不同概念:

- 持久注册 agent 是同级对等(peer)节点;
- host runtime 可以为一项有界任务启动临时子 worker。

没有任何注册身份拥有 goal。由 claim、租约、任务边界、能力与续接策略决定谁来
行动。当并行工作有价值时,LoopX 可以从参与的对等节点中选出一名临时任务协调者。
该职责随任务包(task bundle)结束而结束。

## 对等 runtime 契约

注册身份使用 `agent_model=peer_v1`。它不承担带等级的角色、隐含评审权威或永久
写回所有权。任务协调者可以:

- 激活或恢复符合资格的 peer lane;
- 向临时子 worker 发出完整简报;
- 汇总返回的证据;
- 写入已接受的任务包状态,并对完成的 Turn 记账。

它不拥有持久的 goal 权威。仓库政策、显式决策范围与 todo 续接仍然支配评审、
合并、发布与生产动作。

## 何时并行

默认策略是自适应编排,而不是用户选择的 `single-agent` 或 `multi-agent` 模式。
LoopX 呈现就绪工作与硬边界;由任务协调者决定并行执行是否缩短关键路径、委托
哪些 todo,以及使用哪个合格的宿主上下文。

在能降低不确定性或延迟时并行化:

- 映射互不相交的代码、文档、测试或 runtime 面;
- 在独立 worktree 中实现相互隔离的切片;
- 运行一次独立的评审或验证;
- 检查各自分开的适配器、证据或边界问题。

把紧密耦合的决策留在同一个 peer lane 中。不要仅仅为了让活动图看起来热闹就启动
worker,绝不要让 worker 数量压过配额、user gate、写入范围或仓库政策。

### 自适应准入

`task_orchestration_contract_v2` 只有在以下条件同时满足时才允许临时子工作:当前
runtime 通过观察到的能力显式报告 `subagent_spawn`,且至少还有两个由协调者持有
或尚未被 claim 的就绪推进 todo。宿主名或 scheduler runtime 档案只是元数据,绝不
提供 `subagent_spawn` 或 `subagent_resume`。每个候选都按以下条件检查:

- 当 goal 声明了非空 `allowed_domains` 过滤器时校验 `task_domain`;
- todo 状态、`resume_ready` 与未解决的 user 依赖;
- `required_capabilities` 与观察到的宿主能力;
- 已声明时的规范 `task_repository` 身份(否则 goal 仓库仍为权威);以及
- 经 goal 授权且互不重叠的 `required_write_scopes`。

被拒绝的候选仍会以类型化原因码出现在 `blocked_lanes` 中。超出 `max_children` 的
就绪 lane 仍显示为 `capacity_deferred`。为了保持在 TurnEnvelope 预算内,签名契约
携带一个共享的 `child_brief_defaults` 块,外加受限的每 lane 增量。类型化宿主
请求把它们组合成完整的 `subagent_control_plane_handoff_v0` 简报。协调者仍可保持
串行执行;准入只是权限与容量,而不是启动指令。

没有 `subagent_spawn` 时,LoopX 保留现有的 `task_orchestration_contract_v1`
注册对等激活路径。这使长寿命的对等身份、租约、worktree 与多轮协作保持显式,
而不是把它们变成默认的子 worker 机制。

## 新建、Fork 或恢复

临时任务协调者根据工作形态选择 worker 上下文:

| 工作类型 | 上下文 | 所需任务简报 |
| --- | --- | --- |
| 广泛映射、先有技术检索、风险发现 | 新 worker | 目标、权威来源、允许的来源、边界、预期输出、非目标(non-goals) |
| 独立评审或对抗性验证 | 新 worker | 被评审的 claim、确切证据、验证命令、接受与合并规则 |
| failed-smoke 修复或 review 评论跟进 | 恢复或 fork | worktree、失败证据、最新补丁、下一次有界修复 |
| 互不相交的实现 | 独立 worktree 中的新 worker | 被 claim 的 todo、允许路径、写入范围、验证、续接策略 |
| 长时运行的已 claim lane | 恢复注册对等任务 | Agent id、todo 或租约、最新已接受证据 |
| 生产动作或紧急回滚 | 不自动启动 worker | 操作员批准、停止条件、可逆命令计划 |

只有当任务协调者能提供完整简报时,新 worker 才有价值。缺少权威、范围、预期
输出或验证属于规划缺口,而不是启动一个规范不足的 worker 的理由。

## 共享控制面交接

每个子 worker 简报都从共享控制面出发。worker 不得从聊天记录、旧数据包或另一个
worker 的摘要中推断当前权威。

为兼容性起见,现有宿主-子数据包名称保持为
`subagent_control_plane_handoff_v0`。其谱系字段不产生持久等级:

- `parent_goal_id`:共享 goal 谱系,而非 owner 身份;
- `authority_artifact`:当前 goal、政策或评审权威;
- `latest_state_ref`:应最先读取的状态哈希、run id 或生成时间值;
- `quota_gate_snapshot`:当前资格、等待或 gate 状态;
- `evidence_boundary`:允许的来源、路径以及公开/私有规则;
- `writeback_spend_contract`:谁可以接受证据并对 Turn 记账;
- `child_decision`:`continue`、`wait` 或 `reuse_existing_evidence`。

只有在这之后,简报才应包含 todo id、工作范围、预期 artifact、验证与续接策略。
紧凑规则是:子 worker 只报告证据;临时任务协调者写入已接受状态并进行消耗。

```yaml
subagent_control_plane_handoff_v0:
  parent_goal_id: example-peer-task-goal
  authority_artifact: .codex/goals/example-peer-task-goal/ACTIVE_GOAL_STATE.md
  latest_state_ref: state_hash_or_run_id
  quota_gate_snapshot: eligible
  evidence_boundary: public-safe read-only repository map
  writeback_spend_contract: child worker reports evidence only; task coordinator writes accepted state and spends
  child_decision: continue
goal_id: example-peer-task-goal
todo_id: todo_docs_map
work_scope: inspect docs and return evidence paths
validation: cite files and residual risk; do not edit
continuation_policy: independent_handoff
```

经过显式能力准入后,签名的 Turn 宿主请求只使用合法宿主元数据来映射受支持的
原生上下文操作。宿主名不构成子工作的准入。任务协调者从该目录中选择:

- Codex 暴露 `fresh` 与 `resume`;
- Claude Code 通过其原生 Task 界面暴露 `fresh`;
- 通用适配器不暴露子能力,除非适配器自行声明。

`fork` 将继续留在公开执行目录之外,直到某个真实宿主适配器证明其具备版本化
执行状态、写时复制工作区隔离、容量预留、分支租约、持有结果结算、取消与恢复
能力。上下文选择是建议性的执行策略,不能扩大 LoopX 权威。

## 回执与执行边界

每个被观察的子 worker 返回一条有界宿主回执。`runtime_id` 标识稳定的宿主种类,
而不是进程、可执行文件、工作区、Session 文件或其他本地路径。内置 Codex 适配器
把它固定为 `codex-cli`;`worker_ref` 保持为不透明的宿主子引用。LoopX 拒绝复制
本地路径或无法绑定到计划任务包、lane、任务包摘要、上下文、工作区或效果类别的
回执。证据引用是诸如 `artifact:child-result` 之类的一个或多个不透明令牌,绝不会
是散文、URL、转录或本地路径。

预防优先的数据包检查在启动前强制执行。结果对账目前仅用于观察:它可以标注缺失、
被拒绝、已取消、漂移或一致的子证据并要求父级接受,但不能拦截运行中的宿主工具,
也不会自动终止运行中的子 worker。因此,回执使证据具备被父级评审的资格;它本身
不授权结算、发布、外部写入或生产动作。

## Claim、租约与 Worktree

注册对等节点通过 LoopX todo 与租约 claim 工作。控制面允许一个 `(goal_id,
todo_id)` 只有一个待处理租约。`goal_id` 是共享控制面 lane;`todo_id` 是被
claim 的工作项。宿主子 worker 可以在简报中携带 claim 上下文,但它不会成为带
等级的 agent。

写仓库的对等节点与子 worker 使用独立 worktree。重叠通过任务边界与仓库政策
解决,而不是通过一个永久控制器。完成使用类型化续接:

- `independent_handoff`:把后继者留给对等节点使用;
- `same_agent_non_delivery`:把非交付跟进保留给同一对等节点。

评审仍然是在 `independent_handoff` 之上的 `action_kind=review`。只有当后继者
必须对合格对等节点保持开放、但又不能被作者本人回取时,才把作者加入
`excluded_agents`。

## 启用有界编排

配置界面与 runtime 政策是彼此独立的 opt-in。要暴露本地预览锁定 API、状态字段
与 Dashboard 控件,请显式启动 loopback Dashboard:

```bash
loopx dashboard --enable-goal-subagent-configuration
```

没有该启动标志时,Chat 能力省略该功能,`/api/chat/goal-subagents/*` 两条路由都
返回 404,状态省略 `spawn_policy`,Dashboard 也不渲染该控件。启用界面后,让一个
Goal 接入有界编排:

```bash
loopx configure-goal \
  --goal-id example-peer-task-goal \
  --multi-subagent-feature enabled \
  --max-children 2 \
  --execute
```

任务域过滤是可选的。不传 `--allowed-domain` 时,带标签与不带标签的就绪 Todo
都保持合格,但需满足其他所有准入边界。只有当要把执行范围缩小到匹配的类型化
Todo 时,才添加一个或多个 `--allowed-domain <token>` 参数;不带标签或匹配不上
的 Todo 随后会被 `task_domain_not_allowed` 阻止。

`multi_subagent` 仍是宿主子 worker 能力与权限政策的兼容名称。它不要求用户选择
运行模式或 agent 层级。在观察到宿主子能力时,`quota should-run` 可以投射自适应的
`task_orchestration_contract_v2`。没有该能力时,它不会退回到协调注册对等节点:
注册授予 Todo 所有权,而不是跨 agent 的调度权威。

使用 `--multi-subagent-feature off` 关闭 worker 启动。底层 `--orchestration-mode`
与 `--spawn-allowed` 标志仍可供宿主集成使用。

要移除配置界面本身,请停止 Dashboard 并以不带
`--enable-goal-subagent-configuration` 的方式重启。该标志只暴露一个本地的、预览
锁定的配置契约。它不授予任何 Goal 所有权、仓库写入、凭证、发布、生产或结算
权威;Goal 政策与观察到的宿主能力仍然独立地保持权威。

## 显式注册对等协调

注册对等节点默认独立。LoopX 从不通过哈希对等集合或开放 Todo 包来自动选举
协调者。真正能够激活或恢复持久对等 runtime 的宿主可以显式选择一名协调者:

```bash
loopx configure-goal \
  --goal-id example-peer-task-goal \
  --peer-task-coordinator codex-alpha \
  --execute
```

然后,选定的协调者必须在每个合格 Turn 上报告观察到的宿主能力:

```bash
loopx quota should-run \
  --goal-id example-peer-task-goal \
  --agent-id codex-alpha \
  --available-capability peer_agent_activation
```

该契约只包含当前可执行的 peer lane。休眠的注册 agent 以及已关闭、被阻止或
延期的 todo 都不是协调者候选。休眠或不可恢复的 lane 会投射在
`blocked_peer_lanes` 下;如果没有 peer lane 能运行,任务包就具有
`execution_state=blocked`、`terminal_outcome=blocked` 与
`retry_policy=material_peer_state_change_only`。这一被阻止诊断不替代协调者自己的
可运行 lane,也不会在每次心跳上重新武装激活义务。如果协调者范围内也没有可运行
兜底,最终交互模式就是 `peer_coordination_blocked`:scheduler 把任务包退回其
owner,并停止周期性心跳,直到 peer 能力/就绪状态、协调者配置或协调者自己的
工作前沿发生实质性变化。

在不改变 peer 注册或子 worker 政策的前提下关闭注册对等协调:

```bash
loopx configure-goal \
  --goal-id example-peer-task-goal \
  --clear-peer-task-coordinator \
  --execute
```

该 opt-in 既不授予跨 owner 的 Todo 变更,也不授予更广泛的仓库、发布、凭证或
生产权威。依赖它之前,请用
`loopx configure-goal --goal-id example-peer-task-goal` 读回验证。

## 运行历史与观察

运行历史应归因任务协调,而不持久化等级:

```json
{
  "agent_model": "peer_v1",
  "task_coordinator": "codex-alpha",
  "control_plane_handoff_version": "subagent_control_plane_handoff_v0",
  "peer_lanes": [
    {"agent_id": "codex-beta", "todo_id": "todo_docs_map", "state": "completed"},
    {"agent_id": "codex-gamma", "todo_id": "todo_validation", "state": "running"}
  ],
  "accepted_evidence_count": 1,
  "next_action": "review the remaining validation evidence"
}
```

有用的观察面包括任务包、参与的对等节点、worker 上下文(`fresh`、`fork` 或
`resume`)、被接受或被拒绝的证据、租约、worktree、配额状态与类型化续接。它们
不得从一次临时协调事件重建出持久领导。

## 安全规则

- 当配额或所选 user gate 阻止任务时不要启动。
- 不要从 agent 名称、档案标签或旧提示词推断权限。
- 没有完整任务简报时不要启动新 worker。
- 不要把凭证、私有链接、原始日志或生产材料放进公开交接包。
- 保持实现范围互不相交并使用独立 worktree。
- 让仓库政策决定评审与合并;对等身份不授予两者中的任何一个。
- 让一名临时协调者接受任务包证据,并在验证通过进度后写入一个消耗事件。

结果是无永久领导的并行执行:持久 agent 保持对等,而任务协调与宿主-子关系仅
限定在需要它们的工作上。
