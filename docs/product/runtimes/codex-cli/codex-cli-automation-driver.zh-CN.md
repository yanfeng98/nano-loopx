# 面向 LoopX Turn 的 Codex CLI Adapter

> [English](codex-cli-automation-driver.md)

状态：实验性产品路径，已发布隔离无头驱动（isolated-headless driver）。

面向伙伴的路径请从
[用 Codex CLI 运行一次 LoopX Turn](loopx-turn-codex-cli-quickstart.md) 开始。它把这份维护参考缩小为内置 adapter、一个独立校验器与一条命令。

产品目标是一个可复用机制：LoopX CLI 决定什么可以运行，Codex CLI 执行一个有边界的 agent Turn，LoopX 校验并记录结果。它应当接近 Codex App 中可用的控制面行为，但不复制 App 特定的 heartbeat 逻辑，也不把 Codex session 文件变成项目状态。

主机无关（host-neutral）生命周期由
[`loopx_turn_v0`](../../../reference/protocols/loopx-turn-v0.md) 定义。本页记录 Codex CLI adapter 策略与当前 parity 缺口。

## 当前结论

`loopx turn plan` 与 `loopx turn run-once` 现在为显式 `isolated-headless` 工作提供主机无关驱动。内置 `codex-cli` host 与类型化 `generic-cli` adapter 路由都消费同一个实时 TurnEnvelope。实质性结果只在独立任务校验、持久状态写回、一次 quota spend 与最后 scheduler 检查之后才提交。

Codex host 把 resume id 保留在按 goal、agent、todo 键控的私有本地 runtime 状态中。有界的中断可以保留观察到的 session；不兼容的 host 版本、被拒绝的输出契约、缺失 session 与遗留资格记录则会干净地重新开始。Session 恢复从不计作任务 evidence。

其余 parity 缺口更窄：

- `interactive-visible` 在集齐 attach、idle、interruption 与 takeover 证据之前还不能成为受支持的 Turn 执行模式；
- Trae 等非 Codex 对话式 CLI 还需要一个提供确定性类型化结果通道的薄 adapter；
- 周期性外部调度必须组合既有 `run-once` receipt 与 scheduler hint，且不与活跃 host Turn 重叠；以及
- benchmark 晋升仍需要匹配、可计数的对照 evidence。

较旧的 `codex-cli-local-scheduler-*` 命令保持为诊断与兼容性探针。它们不是默认编排叙事，也不得被手工组合成第二套控制面。

## Codex App Parity 矩阵

| 能力 | Codex App 基线 | 当前 Codex CLI 路由 | v0 驱动要求 |
| --- | --- | --- | --- |
| 持久身份 | 自动化线程加注册的 LoopX agent | Goal、agent 与 todo 是权威；resume id 留在私有 runtime 状态 | 保持 session 句柄不透明、本地、非权威 |
| 唤醒与恢复 | Heartbeat 唤醒既有线程 | `run-once` 只启动或恢复合格的本地位 session | 添加不重叠的周期性唤醒 host 与交互式 attach 证据 |
| 新鲜控制决策 | Agent 运行实时 `quota should-run` 并遵循 `interaction_contract` | `turn plan` 与 `run-once` 使用实时 TurnEnvelope | 保持夹具仅测试用，并在每次 host 尝试前重新决策 |
| User gate | 显示具体投影动作；host 工作停止 | 在 host 调用之前路由 | 保留精确投影动作与 no-spend 行为 |
| Todo 延续 | 选中的 todo、claim、延续与后继策略跨 Turn 幸存 | Todo 身份经 plan、host 请求、写回与 receipt 保持 | 增加更广的调度式与交互式延续资格 |
| 工具 capability | 观察到的 capability 传入 quota 路由 | `--available-capability` 供实时决策 | 添加 host 特定发现辅助，而不创建 user gates |
| Workspace 隔离 | Agent 遵守 workspace guard 与仓库策略 | 调用方提供显式项目；仓库 worktree 策略保持外部 | 在可写 host 之前集成一级 workspace guard |
| 有界执行 | Heartbeat prompt 要求一个有验证的片段 | 内置与通用 host 要求类型化结果与显式超时 | 合格化更长的仓库 Turn 与交互式中断 |
| 校验与写回 | 校验、刷新，然后 spend 一个槽位 | 独立命令校验门控持久写回与一次 spend | 保持校验器任务特定并在 host 之外 |
| Scheduler/backoff | App RRULE 被应用并确认而不 spend | 最终实时 scheduler 检查是 Turn receipt 的一部分 | 外部周期性 host 必须无重叠地应用所需 host 动作 |
| 修复/replan | 类型化控制状态可以保留、修复或替换当前路线 | Host 与校验失败路由到类型化修复/replan；两次停滞需要 todo 或 vision 增量 | 扩展真实 host 负向路径资格 |
| 隐私 | 原始 host 资料留在 LoopX 状态之外 | 现有边界强健 | 保持当前边界并添加类型化结果通道 |

该矩阵是实现检查清单，不是这些能力已匹配的 evidence。

## 产品形态

已发布的实验命令组是：

```bash
loopx turn plan \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --host codex-cli \
  --execution-mode isolated-headless

loopx turn run-once \
  --project . \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --host codex-cli \
  --execution-mode isolated-headless \
  --validation-command-json '["./verify-postcondition"]' \
  --execute
```

`plan` 只读。`run-once` 组合实时决策、一次 host 尝试、类型化收尾、独立校验、写回、spend 与 scheduler 最终检查。对于 Trae 或其他 CLI，在其 wrapper 按主机无关协议实现类型化 stdin/stdout 契约之后，使用 `--host generic-cli --host-adapter-command-json ...`。

该 wrapper 刻意很薄：把一个 Turn 请求翻译成一次有边界的 Agent CLI 调用，只保留不透明的本地恢复句柄，返回一个类型化候选结果。LoopX 仍负责控制决策、todo 延续、独立校验、持久写回、quota 与 scheduler 状态。

Codex CLI 策略支持两个显式模式：

- `isolated-headless` 是当前受支持的实验 worker 与 benchmark 路由。它使用隔离 workspace，从不断言保留可见 TUI。
- `interactive-visible` 仍是面向用户可见的预期路由。在 attach、idle、interruption 与 takeover 证据集齐之前，它不是受支持的 `run-once` 模式。

驱动绝不能把 `interactive-visible` 回退切换到 `isolated-headless`。这既保留现有 `/goal` visible-first 承诺，又允许受控的非交互 dogfood 测试主机无关机制。

## Run-once 算法

```text
1. 解析项目、goal、注册 agent、执行模式与 Codex capability。
2. 带观察到的 capability 运行实时 quota should-run --turn-envelope。
3. 完全按决策路由用户通知、quiet wait、修复或交付。
4. 认领/保留选中的 todo 并满足 workspace guard。
5. 用薄任务正文与 TurnEnvelope 开始或恢复一次 Codex Turn。
6. 要求类型化结果；校验实质性 artifact 或状态变更。
7. 更新/完成 todo 或写修复/replan 增量；刷新状态。
8. 只为经过验证的交付 spend 一次；应用并确认 scheduler 状态。
```

Host adapter 可以使用既有 session 证据、runtime idle、超时与 command-prefix 辅助。它不应让调用方手工组装旧的探针链。

## 类型化修复与 Replan

当当前 todo 仍然正确但 host、workspace、capability、校验或写回路径可恢复时，LoopX Turn 使用类型化修复。当路线本身不再是关闭 goal 验收差距的有效方式时，它使用类型化 replan。

Replan 由以下任一条件触发：

- 活跃 vision 仍未关闭，但没有可运行的 todo；
- 负向 evidence 使选中的路线失效；
- host capabilities 使 todo 不可执行，且修复会改变其意图；或
- 两个合格 Turn 重复相同的无进展结果。

Replan Turn 必须写一个边界 todo 增量或 vision replan 触发。如果它不能产生实质性增量，就返回具体 blocker，而不是无限轮询。

## 实验阶段

1. **契约 - 完成**：主机无关生命周期、类型化结果与独立校验器 gate 已发布。
2. **Shadow - 当前矩阵完成**：状态夹具在不执行 host 的情况下保留动作签名与类型化路由。
3. **一次 Turn - 隔离 Codex CLI 完成**：一个真实恢复的 host session 返回类型化结果、通过独立测试、写入状态、spend 一次并完成 scheduler 最终检查。
4. **调度式延续 - 部分**：恢复/新 session 资格与超时恢复已证明；通用非重叠周期性 host loop 与 `interactive-visible` 模式仍开放。
5. **Benchmark dogfood - 进行中**：在匹配的 source、budget、并发、无反馈、无同步、无上传、无提交边界下，把驱动与 Codex App 及规范可计数 `/goal` 基线对比。
6. **晋升评审 - 待定**：决定保持 adapter 实验状态、退役更旧探针，还是晋升另一 CLI host。

Benchmark dogfood 记录紧凑 parity、轨迹与收尾 evidence。它不得提交原始任务文本、原始轨迹、verifier 输出、凭据或本地 artifact 路径。

## 回滚与非目标

Adapter 必须可以在不改变 LoopX goal 状态、普通 CLI 命令或 Codex App heartbeat 运行的情况下禁用。旧探针命令可以保留为诊断，直到整合驱动覆盖它们的持久边界；它们不得成为默认产品叙事。

该路径不会：

- 在测出匹配 parity evidence 之前替换 Codex App；
- 让 Codex CLI session 数据成为权威；
- 悄悄回答 user gates 或处理凭据；
- 启动 benchmark 作业、上传 artifacts 或提交 leaderboard 结果；或
- 把进程退出码零、生成的散文或 session 恢复当作已验证的任务进展。
