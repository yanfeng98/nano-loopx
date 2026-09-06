# 对等 Supervisor v0
> [English](peer-supervisor-v0.md)

## 状态

实验性且默认关闭。本协议在已注册 `peer_v1` agent 之上增加一个观察与建议层。它不新增 scheduler、不创建 agent 会话，也不授予某个身份对另一个的持久化权限。

设计受 Shepherd 的运行时 supervisor 实验启发：更强的观察者可以比较并发效果流，并选择注入、交接或丢弃一个分支。LoopX 将这些动作保持为类型化建议，直到 host 运行时暴露所需的执行能力并返回证据。

## 为何要 Supervisor

几个对等方对独立进展有用，但它们给用户多处检查点。可选 supervisor 提供一个可对比的综合 channel：

- goal 状态与用户 gates；
- 每个对等方的 quota 与交互契约；
- todo claims、leases 与继续状态；
- 近期 agent 作用域证据；
- 紧凑运行时效果或状态引用。

用户可以在多个对等方运行时把 supervisor 任务用作首选控制室对话。用户仍可直接与任何对等方交谈。改变 goal 权限的决策仍是 LoopX 用户 todos 或 gates，因此它们不只存在于 supervisor transcript 中。

## 配置

Supervisor 必须已是已注册对等方。启用它是显式的：

```bash
loopx configure-goal \
  --goal-id <goal-id> \
  --supervisor-agent <registered-agent-id> \
  --supervised-agent <peer-a> \
  --supervised-agent <peer-b> \
  --execute
```

省略 `--supervised-agent` 以观察除 supervisor 外的每个已注册对等方。禁用该功能：

```bash
loopx configure-goal --goal-id <goal-id> --clear-supervisor --execute
```

配置以 schema `peer_supervisor_v0` 存储为 `coordination.supervisor`。缺失即禁用。规范配置具有 `execution_mode=proposal_only`。

配置后生成专用任务正文：

```bash
loopx supervisor-prompt \
  --goal-id <goal-id> \
  --agent-id <supervisor-agent-id>
```

该 prompt 先运行 supervisor 自己的 quota guard，然后消费一个只读观察包：

```bash
loopx supervisor-observe \
  --goal-id <goal-id> \
  --agent-id <supervisor-agent-id>
```

`supervisor_observation_v0` 从既有公开安全投影中选择。对每个受监督对等方，它包括当前 claim、状态、下一动作、最后活动、工作区/交接引用、近期薄证据行与紧凑效果引用。它不运行另一个对等方的 quota guard、不包含原始历史或 transcript、不引入写权限。缺失的对等方状态或证据投影为警告并使 `decision_input_complete=false`。降级状态契约行为相同：包保留可用的只读投影、报告紧凑健康计数，且不声称决策输入完整。

## 持久化建议与 Host 回执

Supervisor 在报告前记录其精确规范化决策：

```bash
loopx supervisor-event propose \
  --goal-id <goal-id> \
  --agent-id <supervisor-agent-id> \
  --decision-json <decision.json> \
  --execute
```

这追加一条 goal 局部 `supervisor_proposed` 事件。它保持 `proposal_only`；该建议绝不证明 host 变更了会话。

CLI 可以验证或追加 `rejected` 或 `failed` 尝试回执：

```bash
loopx supervisor-event receipt \
  --goal-id <goal-id> \
  --agent-id <supervisor-agent-id> \
  --receipt-json <receipt.json> \
  --execute
```

`executed` 回执更严格：它只能通过 host 适配器 API 追加，该 API 提供可编辑回执 JSON 之外的已验证能力。它还需要不透明权限引用、紧凑证据引用与显式回滚边界。回滚模式限于 `compensating_action` 或 `not_reversible`；两种模式都不授权自动回滚。缺失能力、权限、证据或回滚边界失效关闭。因此普通 CLI 调用方不能仅凭命名能力把建议提升为已执行。`rejected` 与 `failed` 回执保持为持久化尝试证据而不投影成功。载荷匹配时复用同一记录 id 是幂等的，不同则为冲突。

用以下命令读取紧凑投影：

```bash
loopx supervisor-event list \
  --goal-id <goal-id> \
  --agent-id <supervisor-agent-id>
```

该 ledger 是 local-private goal 运行时状态。JSON 输入路径从不记录，内联凭据形状的值被拒绝。

## 决策契约

`supervisor_decision_v0` 使用枚举式封闭集合：

| 种类 | 含义 | 所需 host 能力 |
| --- | --- | --- |
| `observe` | 继续观察；没有正当干预。 | 无 |
| `inject` | 建议向既有会话发送有界消息。 | `session_message_injection` |
| `handoff` | 建议从命名源状态继续目标。 | `session_state_fork`、`workspace_state_transfer` |
| `discard` | 建议终止失败分支，同时保留紧凑证据。 | `session_termination` |

每个建议指名原因码与紧凑证据引用。`inject` 指名目标与消息。`handoff` 指名源、目标与状态引用。`discard` 指名目标与状态引用。

v0 CLI 不执行这些动作。缺失 host 能力使建议保持未执行；模型响应绝不作为会话被注入、分叉或终止的证明。破坏性动作即使有执行器也需显式 host 权限。

## 未来 Fork 扩展关卡

Shepherd 式 `fork` 有用，但它不是 `handoff` 的另一种拼写：

| 操作 | 源继续 | 目标 | 调度效果 |
| --- | --- | --- | --- |
| `handoff` | 通常已结束或让位 | 另一个已注册对等方从 `state_ref` 继续 | 转移继续；默认不应增加活动分支计数 |
| 未来 `fork` | 是 | Scheduler 把临时执行分支租给空闲且能力匹配的已注册对等方 | 增加活动工作，必须预留有界容量 |

LoopX 只有在真实 host 调用点能兑现完整执行契约时才应把 `fork` 加入封闭 supervisor 决策集。在此之前它保持为文档化扩展关卡，而非投机性生产 schema 或纯 prompt 动作。

### 身份与状态模型

Raft 的持久化 agent 模型是 LoopX 的正确约束：一个已注册对等方保持一个持久身份与累积上下文。Fork 复制执行状态，而非身份。它创建 `execution_branch_id`，然后 scheduler 把 `branch_lease_id` 赋给一个既有空闲、能力匹配的 `executor_agent_id`。源与执行者可以是同一对等方，但正常多 agent 路径使用另一个可用对等方，使源可以继续。Scheduler 不得注册克隆对等方、不得把持久化记忆复制进新身份、不得创建隐藏 leader/follower 关系。

因此分支显式分离四个身份：

- `source_agent_id`：其版本化执行状态被 fork 的对等方；
- `source_state_ref`：不可变执行与工作区检查点；
- `execution_branch_id`：临时分支身份；
- `executor_agent_id` 加 `branch_lease_id`：被临时调度运行它的已注册对等方。

分支 lease 比普通 todo 所有权更窄。它授权一个分支的有界执行，而非认领源对等方的 todo、继承其配额或合并其持久化记忆。若结果被选中，由普通 LoopX 继续或交接策略决定哪个对等方拥有下一个持久化 todo。

源必须是版本化不可变 `source_state_ref`，而非重建的聊天 transcript。分支获得隔离的会话/进程视图与写时复制工作区视图。其效果与证据流保持可单独寻址，并通过稳定引用接回源。

### 准入与 Settlement

Fork 消耗更多计算并产生竞争输出，因此 supervisor 建议不足以启动一个。未来 host 准入回执必须证明：

- `versioned_execution_state` 与 `session_state_fork`；
- `workspace_copy_on_write` 或等价隔离工作区状态；
- `scheduler_capacity_reservation` 与 `idle_peer_selection`，包括能力匹配、扇出、成本、公平性、过期与取消边界；
- `branch_execution_lease`，防止一个空闲对等方接受竞争分支，并使失去 lease 失效关闭；
- 一个不透明权限引用与幂等分支 id；
- 无原始 transcript 注入的紧凑效果/证据引用；以及
- `held_result_settlement`，使分支输出不能仅仅因为分支结束就落入规范工作区或 LoopX 状态。

最小生命周期是：

```text
proposal_only -> admitted -> leased -> running -> held_result
                                                -> failed
                                                -> expired
held_result -> selected | discarded
```

`selected` 仍经过普通 LoopX todo 所有权、验证、评审、合并与用户 gate 策略。它不是自动合并。`discarded` 保留紧凑证据并释放执行者对等方加预留容量；它不授权破坏性 git 清理。过期或失去 lease 的分支必须失效关闭，而不是静默继续。

### Supervisor 与工作区交互

Supervisor 仍保持首选综合 channel，而非集中式公司大脑。分支进展应作为可查询的收件箱式投影行出现，使 supervisor 可以拉取相关变更，而不把每个分支事件推入其上下文。已完成分支输出保持 held，直到显式 settlement，这与 agent 原生工作区一致：持久化对等方保持各自上下文并交换有界消息或工件。

该扩展应首先作为默认关闭的 dry-run canary 落在具体多 agent scheduler/host 适配器之上。所需验证包括容量耗尽、重复 fork 幂等、源状态不可变、工作区隔离、基于能力的空闲对等方选择、竞争分支 lease、分支过期/取消、held-result settlement，以及 host 报告部分失败时的恢复。只有该证据才正当化扩展 `SupervisorDecisionKind` 与公开事件 schema。

## 可选注入适配器 Canary

`loopx.control_plane.agents.supervisor_inject` 为 `inject` 暴露一个窄 Python host 接缝。LoopX 不提供默认适配器，也没有启用它的 CLI 开关。Host 必须显式提供带 `session_message_injection`、回滚模式与不透明回滚策略引用、外加单次执行权限引用的适配器。Dry-run 不调用 host 即验证整个请求。

执行时，适配器接收稳定 `SupervisorInjectRequest` 并必须返回类型化 `SupervisorInjectResult`。LoopX 随后追加能力匹配的回执。先前已执行回执抑制第二次 host 调用，使重复控制面请求幂等。回滚字段记录边界；它不撤回消息，也不授予发送补偿消息的权限。`handoff` 与 `discard` 保持 proposal-only，直到其自身 host 契约与安全证据存在。

## 权限边界

- Supervisor 是带额外观察职责的对等对等方。
- 它不能认领另一个对等方的 todo、花费另一个对等方的配额，或仅为解决建议而改写用户 gate。
- 评审与交接保持普通任务策略；supervisor 不成为隐藏评审 owner。
- Pre-peer 层级字段仍限于既有 exactly-once 迁移读取器。它们不是活动配置模型，本协议也不使用它们。

该分离使 LoopX 可在不把 State Kernel 耦合到特定会话运行时、也不把持久化层级带回 `peer_v1` 的情况下，测试更丰富的综合是否改善投递。

## 参考

- [Shepherd: A Meta-Agent for Versioned Execution](https://arxiv.org/abs/2605.10913)
- [CooperBench](https://arxiv.org/abs/2601.13295)
- [Shepherd repository](https://github.com/shepherd-agents/shepherd)
- [Raft: Where Humans and Agents Build Together](https://raft.build/resources/blog/introducing-raft-where-humans-and-agents-build-together/)
- [Raft: Is Having Agents in the Room Meant to Be Chaotic?](https://raft.build/resources/blog/is-having-agents-in-the-room-meant-to-be-chaotic/)
- [Raft: You Don't Need a Company Brain](https://raft.build/zh-cn/resources/blog/you-dont-need-a-company-brain/)
