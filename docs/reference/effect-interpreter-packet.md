# Effect 解释器 Packet

> [English](effect-interpreter-packet.md)

本页记录 `quota should-run` 的标准读取视角:

```text
effect_request -> interpretation -> observation -> next_effect
```

它不增加新的 runtime 合同。它只是命名已经扮演各角色的现有 packet 字段。

## 代码透镜

`loopx.control_plane.effect_program.interpret_quota_should_run_packet` 把现有的 `quota should-run` packet 映射到标准槽位,`interpret_turn_result_packet` 把现有的 `loopx_turn_result_v0` packet 映射到标准槽位:

- `EffectRequest`
- `EffectInterpretation`
- `EffectObservation`
- `EffectNext`
- `EffectTurn`

两个函数都刻意保持只读。它们不替代配额决策或 Turn 结算逻辑;它们给重构与测试代码提供一个稳定的抽象,用于跨 packet 族读取 effect program 形状。

## Turn Journal 透镜

`interpret_turn_journal` 读取现有的 fenced Turn journal,并返回一个 `EffectTurn`。它跨 journal、已存储 plan、typed 结算标识、host 结果与 receipt,比较 Goal、Agent owner 与 Turn-key 身份。它还验证已完成的 phase 是有序事务前缀,并暴露保留的 `committed`、`stopped` 与 `failed` journal tombstone。

`request.context.replay_legal` 只是无 effect 的终态重放信号。身份、phase 顺序与终态失败会作为稳定的 typed 违规值一起出现在 `request.context.violations` 中;语义不匹配返回被阻断的 observation,而不是抛出异常。

`EffectObservation.should_run` 保持为 false,`EffectNext` 保持为空,因此检查本身永远不会授予 effect 权限。同一解释器还投影 `recovery_decision`,即 executor 的恢复计划:其动作、是否允许继续、要恢复的 phase、Host 是否必须再次被调用、typed 原因,以及只包含参与过的检查。真正的 Turn executor 在继续之前消费该决策。因此 `replay_legal=false` 并不意味着 `in_progress` 或 `scheduler_action_required` journal 不可恢复。

公开的只读消费入口是:

```bash
loopx turn inspect-journal \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --turn-key <sha256:64-hex-digest> \
  --format json
```

添加 `--retry-failed-turn` 以评估 `turn run-once` 使用的同一显式失败 Turn 重试。当失败的 Host 记录了 `resume_session` 时,检查会执行当前的只读 Session 绑定检查;没有显式重试请求时,决策报告 `failed_retry_not_requested`。

它只解析标准的 journal 位置。不存在任意的 `--journal-path` 输入。该命令验证选择器、获取现有 journal 锁、对存储的 JSON 做 schema 检查,并返回带版本号的 `loopx_turn_journal_inspection_v1` 投影。版本 1 保留所有 v0 重放与完整性字段,并新增 `journal_consistent`、`recovery_decision` 与可选的 `last_recovery` 审计。审计只包含采用的公开安全 plan、它的有界实际状态、已完成的 phase id 与 Host 调用布尔值。它永远不包含 Host 日志、Session 内容、provider payload 或路径。

Journal 一致性对标准 typed 结算身份以及 Journal/envelope 谱系与 phase 排序都是 fail-closed 的。在共享恢复决策可以授权任何 provider 调用之前,结算 Goal、Agent、Turn 实例、绑定与 effect id 都必须验证并绑定到被检查的 Turn。在当前 Turn driver 中,绑定是 envelope 的所选 Todo(或自适应主 Todo 覆盖);不同的标准 Todo 身份仍然不一致并 fail closed。

JSON 与 Markdown 渲染同一投影。它们不暴露原始 journal、plan、host 结果或 receipt 主体;请求上下文;capability;推荐动作;凭据;证据;或解析后的本地路径。成功解释的 `replay_blocked` journal 以 0 退出,因为重放合法性与可恢复性是独立的诊断数据。无效选择器、缺失 journal、格式错误的 JSON 与不支持的 schema 以非零退出。

## 标准示例

### 1. Effect 请求

Agent 或 host 提出下一个有界 Turn。输入包括:

- `goal_id`
- `agent_id`
- `available_capabilities`
- host surface 与 scheduler 执行上下文
- 适用时的当前 host RRULE

### 2. 解释

harness 通过以下方式解释请求:

| Packet 字段 | 角色 |
|---|---|
| `work_lane_contract.lane` | 路由:advancement、monitor、gate 或 wait |
| `work_lane_contract.obligation` | 所选路由必须做什么 |
| `interaction_contract.mode` | 面向 host 的交互模式 |
| `capability_gate.action` | 存在 gate 时的 capability 决策 |
| `scheduler_hint.cadence_class` | 下一次 host 唤醒的时序决策 |

### 3. Observation

决策以如下形式返回:

| Packet 字段 | 角色 |
|---|---|
| `decision` | Run、skip、observe 或 repair |
| `should_run` | 是否允许计算 |
| `effective_action` | 机器可见的有效动作 |
| `recommended_action` | 下一个具体动作文本 |
| `action_portfolio` | 主动作加有界 typed 回退(存在时) |
| `protocol_action_packet.summary` | 紧凑的面向 actor 的摘要 |

`EffectTurn.observation.action_portfolio` 是该字段的标准 TypeScript 归属 observation。Python 只提供作用域/capability 允许的 todo 行;TypeScript reducer 在 Turn envelope 签名之前验证身份、移除重复、限制列表大小并修正执行失败触发器。

### 4. 下一个 Effect

observation 指回 Loop:

| Packet 字段 | 角色 |
|---|---|
| `interaction_contract.cli_channel.next_cli_actions` | 下一个 CLI effect |
| `execution_mode` | 有序 effect program 的执行策略(`serial` / `parallel` / `interleaved`) |
| `scheduler_hint.action` | 调度器周边决策 |
| `scheduler_hint.cadence_class` | 下一次 host 唤醒的节奏 |
| `scheduler_hint.codex_app.ack_hint.cli_args` | Host ACK effect |
| `scheduler_hint.codex_app.failure_hint.cli_args` | Host 失败 effect |

`EffectTurn.next_effect` 是该槽位的代码透镜。它保持数据编码的 handler 可见:host 调用 CLI 动作,并通过 ACK/失败 hint 结算成功或失败,而不是让 LoopX 跨 Turn 持有一个 callable。当下一个 effect 是有序 effect program 时,`execution_mode` 是数据编码的策略;当 packet 未声明时默认为 `None`。

## Around 语义

`capability_gate`、`interaction_contract`、`work_lane_contract` 与 `scheduler_hint` 是对标准 effect 步骤的 around 决策,而不是独立的特性模块:

| Around 层 | 可短路 | 可重写 |
|---|---|---|
| `capability_gate` | `ask_owner`、`repair_bridge`、`unsupported` | 修复 todo 与下一个 CLI 动作 |
| `interaction_contract` | `action_required`、`mode` | 主/协议动作与通知 |
| `work_lane_contract` | Monitor/inbox 抢占、`must_attempt_work=false` | Lane、obligation、`next_lane` |
| `scheduler_hint` | 暂停/删除 heartbeat、无消耗静默 | RRULE、节奏、有状态退避 |

顺序与 effect 语义是合同。capability gate 不能被折叠为通用异常处理器:`owner_missing`、`repair_missing` 与 `decision_owner` 必须保持可见,因为 `ask_owner` 与 `repair_bridge` 会导向不同的下一个 effect。

CLI packet 是比单个工具调用密度更高的 effect:一条命令可以携带权限、预算、验证、执行、失败语义、ACK 与写回。vendor 的串行或交错工具 API 是解释器内部的执行模式,而不是新的状态机。

## 有序 Effect Program

`loopx.control_plane.effect_program.effect_program_from_ordered_steps` 把现有的 `guided_transaction.ordered_steps` 值映射到 `EffectProgram`:

- `EffectStep` 保留 `step_id`、`kind`、`command` 与 `purpose`;
- `EffectProgram` 保留有序步骤与可选的 `execution_mode`。

这仍然是只读透镜。在 LoopX runtime 调用方拥有多步执行之前,executor 保持 host 驱动。

## 终态收尾顺序

结算 plan 把最终 Goal 收尾与普通 Todo 延续区分开来。其有序合同是:

```text
validation -> durable_writeback -> quota_spend -> terminal_closeout?
```

`terminal_closeout` 是有条件的:仅当已验证的完成声明 `no_followup` 时才存在。普通后继完成仍然是 Todo 生命周期动作,不会假装是终态结算步骤。最终收尾必须证明相同的 effect 身份以及匹配的写回与消耗 receipt,之后才能使 Goal 进入终态。

这一顺序是刻意为之。先完成最终 Todo 会使严格的终态守卫拒绝为同一实质 effect 记账的消耗。修补不是终态之后的消耗例外:终态仍然严格,收尾移动到消耗之后。如果收尾失败,其已记录到 journal 的 receipt 可以重试,而不必重复写回或消耗。Scheduler apply 与 ACK 仍是本结算链之外的 host 交接。

## 与状态机的关系

每个状态族都是该透镜上的一个解释表:

```text
input effect -> interpreter -> decision -> observation -> next effect
```

参见
[Agent Loop Effect Interpreter RFC](../architecture/rfcs/agent-loop-effect-interpreter-v0.md)
与
[Harness 是 effectful Program](../development/control-plane-course/01-agent-loop-effectful-program.md)。
公开框架来自齐梦星空,
[主线一:Agent Loop 是 effectful program(1)](https://www.xiaohongshu.com/discovery/item/6a01d501000000003700c5de?source=webshare&xhsshare=pc_web&xsec_token=ABqpNuladcxhev099wLKw8M3ilhKBua0BQXNpxnBZEGkc=&xsec_source=pc_share)。
