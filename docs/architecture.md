# 架构


LoopX 有六个持久的控制面层，外加一个可选的探针面——其执行策略要求只读观察；
它不是对等层。

1. **Registry**：列出已知目标、它们的仓库、adapter、权威来源、status 与 guard。
2. **Goal state**：一个目标的活跃状态文件。
3. **Run log**：每个目标保存的 JSON 与 Markdown 报告。
4. **Run history**：被 Agent、heartbeat 与 UI 消费的紧凑索引。
5. **Status / attention queue**：下一个该谁行动的首屏摘要。
6. **Compute quota**：每个目标可消耗多少自动 Agent 计算的本地策略。

**可选探针面（不是第七层）：** 目标可以通过 bootstrap `--next-probe` 注册一个
项目特定的 `next_probe` 命令。注册把命令存为自由文本，且不验证它是只读的；
heartbeat 与 operator 策略要求任何被执行的观察都必须是只读的。
`pre-tick-runnable` adapter 状态单独声明，不从 `next_probe` 推断。
没有随附的 `pre_tick` 模块或 adapter pre-tick 包，所以保持探针注册、
执行策略与 adapter 状态为三个独立契约。

```text
project goal state
  + private registry
  + optional next_probe
        |
        v
shared runtime root
        |
        v
loopx history/check
        |
        v
loopx status
        |
        v
quota-aware agent tick / heartbeat / future UI
```

核心仓库刻意避免领域逻辑。一个数据实验目标、一个笔记维护目标和一个 harness
自改进目标应共享同一运行时与契约，但使用不同 adapter。

## 控制面即 Effect Interpreter

六个层不只是存储面。它们共同在每次 loop 迭代中解释一个 effect request：

```text
model -> effect request -> harness interprets effect -> observation -> model
```

读模型是当前状态（`A`）：registry、goal state 与 run history。投影是观察
（`F[B]`）：status、attention queue 与紧凑 run 摘要。决策是 effect interpreter
（`A => F[QuotaDecision]`）：quota、交互契约、能力门、work-lane 路由与 scheduler
hint 决定下一个 effect 是否可以及如何运行。数据编码的 handler 是 quota packet
中的 `next_effect`：CLI 动作、scheduler ACK/失败提示、writeback 与 spend。

这与
[Agent Loop Effect Interpreter RFC](architecture/rfcs/agent-loop-effect-interpreter-v0.md)
和
[Harness Is the Effectful Program](development/control-plane-course/01-agent-loop-effectful-program.md)
是同一透镜。公开表述来自齐梦星空，
[主线一：Agent Loop 是 effectful program(1)](https://www.xiaohongshu.com/discovery/item/6a01d501000000003700c5de?source=webshare&xhsshare=pc_web&xsec_token=ABqpNuladcxhev099wLKw8M3ilhKBua0BQXNpxnBZEGkc=&xsec_source=pc_share)。

## 引导式自主，而非推荐锁定

LoopX 区分**硬边界**与**引导建议**。声明、范围、能力就绪、gate、quota、
公共/私有策略，以及破坏性或生产效果规则定义 Agent 可以做什么。优先级、
推荐、有界建议与 `next_cli_actions` 帮助 Agent 在该合法集内高效选择；
它们不会偷偷缩小它。

因此投影针对可读性优化，而不假装穷举。Agent 可以选择一个当前权威的合格动作，
即使它不在第一组建议里；当有界视图不足时，typed 发现路径应暴露权威队列。
Agent 必须把该选择带回同一条 typed 预检、收据绑定、验证、写回与 spend 路径。
这保留了流程引导与可审计性，同时在没有真实边界要求单一路线时保持 Agent 自主。

一个字段如果是建议性的，就必须在 schema 里说明。如果 controller 想要白名单、
排他租约、owner gate 或其他机器强制限制，该限制属于 typed 权威或转移契约，
而不是从列表位置或提示措辞推断。

## Turn 决策词汇表 {#turn-decision-vocabulary}

面向 operator 的文档与 heartbeat 提示常把 turn 概括为 deliver、wait、ask、
replan、repair 或 stay quiet。这个简写描述交互意图；它不是 Turn 契约携带的
typed packet 词汇。

可执行词汇与其拥有契约共存：

| 契约 | 时机 | 权威定义 |
| --- | --- | --- |
| `LoopXTurnRoute` | Host 执行前 | [`driver.py`](../loopx/control_plane/turn_driver/driver.py)，枚举 `LoopXTurnRoute` |
| `TurnResultKind` | Host 执行后 | [`settlement.ts`](../loopx/control_plane/turn_driver/settlement.ts)，`TURN_RESULT_KINDS`；Python adapter: [`transaction.py`](../loopx/control_plane/turn_driver/transaction.py)，枚举 `LoopXTurnResultKind` |

阅读这些定义里的完整成员列表；本页解释它们的含义，而不维护另一份穷举枚举。

- 散文 "deliver" 拆成 `validated_progress` 与 `validated_completion`。
- 执行失败是一等 typed 结果。特别是 `terminal_closeout_failed` 表示终态收尾在持久的
  writeback 与 quota spend 之后失败。恢复重试同一 Turn 的收尾而不重复那些已提交的
  effect；它绝不能把失败当作未 spend。
  [Turn executor 恢复测试](../tests/test_loopx_turn_executor.py)覆盖这一边界。
- "Stay quiet" 是通知/monitor 行为（例如 `monitor_quiet_skip` 或 heartbeat
  `DONT_NOTIFY`），不是两个枚举的成员。

Quota `interaction_contract` 与 heartbeat 引导仍可使用 operator 简写。
Turn adapter 使用上面链接的可执行定义。

## 运行时责任模型 {#runtime-responsibility-model}

上面六个持久层描述控制面表面。它们不描述谁执行一个 turn 的每一步。
运行时归属用四个责任：

| 责任 | 拥有 | 不得拥有 |
| --- | --- | --- |
| **Agent** | 规划、分析、工具使用，以及通过 host/runtime 的一次有界执行 | 持久目标生命周期或未加作用域的 effect 权威 |
| **Provider** | 外部调用与有界观察、effect 结果与读回 | 领域转移策略或 LoopX todo 状态 |
| **Capability** | 面向调用方的结果契约、领域策略、观察归一化、验证与 typed 转移提议 | 持久调度、声明、gate 或直接生命周期写 |
| **LoopX 内核** | Goal、todo、claim、gate、monitor、quota、被接受的 writeback、恢复与调度 | 领域特定推理或 provider 实现细节 |

因此请求与结果路径反向运行：

```text
Agent -> Capability -> Provider -> external system
external observation / effect readback -> Provider -> Capability
typed transition proposal -> LoopX Kernel -> next todo / gate / monitor / turn
```

观察不是转移，provider 收据在 capability 验证它且内核提交结果状态变化前，
也不是被接受的进度。领域状态、证据与收据是这些责任之间交换的产物，
不是额外运行时 owner。

host/runtime 携带 Agent 的会话、工具与调用。它是可替换的执行边界，
不是第五个领域决策 owner。

一个**extension** 是独立的分发与生命周期轴。它可以安装可选 provider，
而内置 capability 可以使用核心 provider。extension 不会成为第五个运行时责任，
也不会获得内核权威。这个边界直接由 `CapabilityRegistry` 表示，
它分别注册 providers、capability 契约与其实现。

### Agent 原生 Kanban 是一种投影

LoopX 状态可以渲染为 Agent 原生 Kanban：todos 是卡片，逻辑 lane 是派生视图，
卡片移动是经过验证的转移。这个隐喻不引入另一个状态 owner。Canonical
todo/event/state 契约保持权威；dashboard 与协作看板消费 public-safe 投影。

Capabilities 可以投影领域 lane，如 Issue Fix
`feasibility -> patch -> checks -> review -> merge`，而不把这些标签加入
内核生命周期。Provider 提供 lane 背后的事实，capability 验证它们并提议 typed
转移，内核拥有 claim、gate、monitor、quota、writeback、恢复与终态关闭。见
[概念入门](development/control-plane-course/00-concept-primer.md)与
[state 基底讲义](development/control-plane-course/04-state-substrate.md)。

## 当前依赖预算 {#current-dependency-budget}

可执行边界策略位于
[`test_control_plane_import_boundaries.py`](../tests/architecture/test_control_plane_import_boundaries.py)：

- `test_control_plane_does_not_gain_outward_dependencies` 拒绝控制面导入
  展示、CLI、capability 或 benchmark-adapter 层。
- `test_status_has_no_forbidden_outward_dependencies` 拒绝 status 导入
  benchmark-adapter 或展示层。
- `test_quota_markdown_is_owned_by_the_presentation_layer` 保护渲染器归属与
  CLI 组合边界。

这些是零例外检查。先前 quota-Markdown 与 status verifier-bootstrap 边已被移除；
这些检查没有剩余债务白名单。运行链接的架构测试文件检查当前违规，
而不是在散文里维护一份边清单。

Adapter 特定增强属于应用/插件组合，而不是 status 核心。只有在存在
characterization 对等后才移动一条边。在函数或动态导入里藏 adapter 依赖
不算架构分离；当前 AST 检查审查静态导入，包括函数局部导入，
但不证明动态导入不存在。

### Status 与 Quota 门面

`loopx.status` 与 `loopx.quota` 保持为其门面拥有行为的兼容入口。
被导入的实现属于其 canonical 有界模块；唯一纯兼容再导出是每个门面
`_PUBLIC_COMPAT_REEXPORTS` 映射中的键，其值指明 canonical owner。

新仓库代码必须导入 canonical owner。当公共示例、回归或文档导入契约消费它时，
纯兼容条目可以保留。零消费者、无文档的条目被移除，而不是变成永久意外 API。
移除保留条目需要显式迁移或弃用步骤，且 status/quota CLI JSON 对等性必须独立于
兼容绑定保持特征化。

Capabilities 与 extensions 也是正交的：capability 是产品契约，
而 extension 是独立管理的分发单元，可以为多个 capability 安装 providers。
provider 感知的注册与清单边界在 [extensions.md](reference/extensions.md) 中说明。

Operator 收件箱紧迫度就是这样一个内向契约。Quota 消费控制面的无内容
`operator_inbox_urgency_v0` 读模型；它不导入 Lark provider。现有 Lark 配置、
事件文件、capability key、lane 名称与 CLI 在 provider 把紧迫度投影委托给该契约
时保持兼容面。只有在该读模型与 work-lane 对等性保持特征化后，provider 文件才应移动。

LoopX 还应吸收经过现场检验的项目控制机制，如权威注册表、当前信念 TODO、
托管外部来源清单、实验看板、验证面映射与带 gate 的 handoff packet。
见 [field-derived-patterns.md](concepts/field-derived-patterns.md)。

LoopX 还应暴露一个人类友好的 frontstage，而不把真相源搬进聊天。
一个目标可以投影为通道，Agent 可以投影为工作区成员，任务归属可以投影为
显式租约；registry、active state、run history、quota、gate 与租约事件仍是
backstage ledger。见
[frontstage-channel-lease-roadmap.md](product/roadmaps/frontstage-channel-lease-roadmap.md)。

LoopX 还应成长出一个窄的 host 集成面。CLI 命令保持兼容基线，
但长时 Agent host 在同状态可用作 hook/MCP/server adapter 时受益：

- hook 激活应只把 host 导向当前 LoopX 契约；它不得嵌入第二个 scheduler
  或过期的项目策略；
- MCP/server 工具应暴露生命周期读、todo/gate/lease 写与紧凑 status 投影，
  而无需 host 解析 Markdown；
- host adapter 应隔离平台细节，同时保留相同的 registry、事件 ledger、
  quota、公共/私有边界与租约语义；
- 任务图应是 LoopX 状态上的可选投影，而不是事件 ledger 或活跃目标真相的替代品。

这使 LoopX 在 Codex、本地 CLI loop、dashboard 与未来 Agent host 之间保持可移植，
同时避免为每个 host 派生一个控制面。v0 协议契约是
[`host-integration-surface-v0`](reference/protocols/host-integration-surface-v0.md)：
hook 激活保持薄，生命周期读与 todo/gate/lease 写映射到 CLI 等效操作，
紧凑 status 投影排除原始/私有材料，可选派生投影保持只读，
且 adapter 缺失时 CLI fallback 依然可用。

## 终身目标不变量

LoopX 应优化**终身目标**：可能活过一个线程、执行器、项目阶段或计划的持久意图。
这是产品不变量，不是额外存储层。

一个终身目标必须稳定到足以让未来的人或 Agent 恢复：目标是什么、
当前什么定义它、谁可以改变它、下一个安全转移是什么。它也必须保持窄，
让自动化能做一个有界、可验证的动作，而不是声称开放式的权威。

架构把该不变量映射到现有层：

- registry 给终身目标稳定身份、仓库边界、adapter 状态、guard 与权威来源列表；
- active goal state 记录当前信念、优先级栈、非目标与下一个动作，
  而不变成完整日记；
- 权威来源用可评审上下文与冲突规则取代隐式模型记忆；
- run history 在会话与 Agent 之间保留紧凑证据轨迹；
- todos 把终身目标变成有界的用户与 Agent 义务；
- gates、reward 与 quota 让人类判断、路线修正与计算 spend 附着在具体转移上。

结果应在不声称开放式自主性的情况下保留连续性：目标可以活好几年，
但每个 Agent turn 仍必须经过当前权威、边界、quota、验证与 writeback，
才能算作进度。

对已经拥有 Agent 定义、会话事件、工具执行、权限、计费与产品 frontstage 的
会话运行时平台，Goal Harness 应集成为目标级控制投影，而不是第二个运行时。
只读 adapter 路径是：摄入紧凑会话、事件、批准、结果与产物摘要；产出
`goal_state`、`run_projection`、`operator_gate`、`human_reward`、
`work_lane_contract`、`quota_decision`、`handoff_packet` 与
`dreaming_proposal` 投影；然后让产品面显示这些投影。见
[session-runtime-control-plane-adapter.md](integrations/session-runtime-control-plane-adapter.md)。

## 本地服务器 / Daemon 路线图

CLI 保持兼容基线。未来的本地服务器应是同一 registry、active state、run history、
quota、todo 与边界契约上的可选控制面协调器，而不是替代状态机。

在当前控制面中，一个 **goal** 是稳定的 `goal_id` 边界：一个 registry 条目、
active-state 文件、quota lane、run-history 流与 status 投影。一个 **todo**
是该目标内的结构化 active-state 复选框，用 `todo_id` 编址，
并投影为 Agent 或用户工作条目。LoopX 运行时模型中没有独立的 issue 对象。

服务器路径应分层落地：

1. **服务器之前的写入正确性**：用每目标锁、幂等键与乐观 revision 检查，
   让现有 CLI 写者在并发下安全。`todo`、`refresh-state`、reward writeback、
   quota spend 与 history append 路径应在过期 revision 或重叠写作用域上 fail closed。
2. **租约采用**：可选本地 `task_lease_v0` CLI 已提供 owner、TTL、写作用域、
   幂等、冲突、转移与释放语义。已释放的世代保持为非活跃的逐 todo tombstone，
   因此后续 acquire 同时推进 CAS 版本与权威拥有的 `lease_epoch`；
   终态 writeback 使用返回的 key/version 对。把 `claimed_by` 保持为默认软路径，
   只为有确证并发写问题的 host 采用硬租约。
   Pending/lease 键应为每 todo：`(goal_id, todo_id)` 是争用单元，
   不是整个目标或项目。同一目标下不同 todos 在写作用域与 gate 允许时可以并行；
   同一 todo 上的竞争 claim 会 fail closed 或续约。
   Status 目前暴露 capability 可用性；quota 不强制也不消费硬租约。
   后续 host 集成可在其采用契约与回退行为验证后投影活跃租约行。
3. **Loopback 协调器**：把现有本地 status server 扩展为纯 loopback 协调器，
   可以集中每目标锁、租约、quota 决策、紧凑 status 投影与 heartbeat 调度。
   它必须绑定本地，让原始/私有证据远离紧凑响应，并为每次写保留 CLI fallback。
4. **Heartbeat scheduler**：只在 quota/spend 幂等被证明后，把循环 heartbeat
   簿记移到协调器后面。Scheduler 输出应为当前自动化提示已使用的同一
   `quota should-run` / `interaction_contract` / `protocol_action_packet` 形状。
5. **规划与 dreaming 队列**：让后台规划把排名 todo 提议、证据探针与重构警告
   产出为建议性记录。这些队列不得执行受保护工作、读取私有材料，
   或在经过后续正常 `quota should-run` 决策与目标边界批准前花费 delivery 配额。
   紧凑契约是 `server_managed_planning_contract_v0`；见
   [dreaming-exploration-lane.md](product/roadmaps/dreaming-exploration-lane.md)。
6. **Host adapters**：通过 MCP、hooks 或小型本地 HTTP API 为 Codex 类 host
   暴露相同契约。Host adapter 应把 Agent 路由到当前状态与合法写；
   不应嵌入过期项目策略或创建第二个 scheduler。

首个服务器支撑里程碑的验收标准：

- 守护进程停止后，同一动作仍可通过纯 CLI 模式完成；
- 重复 heartbeat、重复 quota spend 或过期 todo 更新变成显式 no-op 或冲突，
  而不是第二个 delivery 事件；
- status 显示活跃租约与当前 owner，而不让租约成为项目真相源；
- 所有紧凑服务器响应通过公共/私有边界扫描；
- 测试覆盖一个并发写者冲突与一个守护进程宕机回退。

在服务器支撑的租约存在之前，LoopX 保留一个更轻的共享控制面契约：
todo 元数据可以包含 `claimed_by`，由 todo CLI 在 active-state 文件锁下写入。
该字段是仅供可见的软 owner，CLI 只在 id 注册于
`coordination.registered_agents` 时接受它。已注册身份是对等 peer。
工作权威来自显式 claim、任务租约、目标/写边界与 typed 延续策略，
而不是持久 leader 角色。做仓库工作时任何 peer 都遵循同一工作区隔离规则；
仓库维护者策略决定它可否 self-merge。未来服务器租约应保持每 todo，
并增加 TTL、幂等键、过期 claim 检测、重叠警告与 compare-and-swap 冲突响应。

## State 交互模型

LoopX 有四个产品 actor：

- **goal**，拥有持久 objective、状态、guard、run history 与 reward overlay；
- **Codex App executor**，执行有界转移，但不应是长期真相源；
- **user**，提供 operator 意图、批准与高质量奖励信号；
- **dashboard**，可视化派生 status，且在启用显式本地写边界前应保持只读为主。

这个 actor 模型是未来命令与 dashboard 工作的设计关卡。一个新 capability
应指明它读的状态、写的状态、该写的 owner，以及 dashboard 如何证明转移发生。

见 [state-interaction-model.md](state-interaction-model.md)。

## Peer 任务协调

对并行工作，每个已注册 LoopX Agent 有平等身份权威。每个 peer 只在当前目标边界内
拥有其声明或租约的工作。一个 peer 可以：

- 检查或声明一个合格 todo；
- 推进一个有界的实现、验证、监控或修复切片；
- 创建一个普通独立 successor，可选带执行者排除；
- 为其自身被接受的任务结果写回证据。

当有界编排启用时，LoopX 确定性为一批任务选择一个临时协调者。
该协调者可以激活或恢复合格 peer lane 并汇总被接受的 bundle 证据。
它不会成为持久 leader，也不会对其他身份获得隐式评审、merge、发布或 replan 权威。

LoopX 不取代操作系统 scheduler 或 Codex App executor。但是，它应拥有
那些执行者在运行更多工作前读取的简单计算配额。定时器 cadence 是执行机制，
不是项目优先级的真相源。

见 [quota-allocation.md](quota-allocation.md)。

见 [peer-agent-runtime-v1.md](reference/protocols/peer-agent-runtime-v1.md)。

## Status / Attention Queue

status 层从 registry、run history 与契约健康派生紧凑队列。它应是 controller
或未来 UI 首先读取的内容：

- 契约失败阻塞 adapter 工作，
- 等待用户/controller opt-in 的目标被显式表露，
- 准备好接受 Codex 工作的目标与外部证据关注分离，
- 已连接且带有效 run 的只读目标不需要索要冗余评审。

见 [attention-queue.md](operations/attention-queue.md)。

JSON 导出是 dashboard、heartbeat 摘要与未来 UI 工作的边界。
见 [status-data-contract.md](status-data-contract.md)。产品 dashboard
前端应遵循
[dashboard-frontend-selection.md](product/roadmaps/dashboard-frontend-selection.md)；
单文件 HTML 渲染器保持为冒烟测试与离线检查的回退。
