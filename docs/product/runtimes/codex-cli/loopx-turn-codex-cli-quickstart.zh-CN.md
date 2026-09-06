# 用 Codex CLI 运行一次 LoopX Turn

> [English](loopx-turn-codex-cli-quickstart.md)

状态：实验性 `isolated-headless` 产品路径。

LoopX Turn 只需要三块：

1. **Agent CLI adapter**：内置 `codex-cli` adapter 把一个类型化 LoopX 请求翻译成一次有边界的 Codex CLI 运行，并返回一个类型化结果。
2. **独立校验器**：你的命令检查真实后置条件。它不信任 agent 的完成声明。
3. **一条 Turn 命令**：LoopX 决策，Codex 执行，校验器证明，LoopX 提交。

```text
LoopX decides -> Codex CLI executes -> validator proves -> LoopX commits
```

## 运行之前

你需要一个已连接的 LoopX goal、一个带可运行 todo 的注册 agent、一个隔离项目 workspace，以及一个可执行校验器。校验器从 stdin 接收规范化 host 结果，并且只在实际 artifact 或状态正确时退出零。

用 `codex doctor` 检查一次本地 host。如果默认模型比已安装的 Codex CLI 新，更新 Codex 或传 `--codex-model`。

## 运行一次 Turn

对于可写的编码类 todo：

```bash
loopx turn run-once \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --host codex-cli \
  --project "$PWD" \
  --codex-sandbox workspace-write \
  --codex-model <qualified-model> \
  --validation-command-json '["./verify-postcondition"]' \
  --execute
```

内置 Codex adapter 意味着该路径无需编写 adapter 程序。另一 Agent CLI 通过薄的 `generic-cli` adapter 使用同一 Turn 契约：从 stdin 读取一个 JSON 请求，向 stdout 写入一个 JSON 结果。

## 读取结果

紧凑 JSON 结果告诉调用方接下来会发生什么：

| 信号 | 含义 |
| --- | --- |
| `status=committed` | 独立校验通过；LoopX 写入持久结果并 spend 一次。 |
| `result_kind=repair_required` | 保留 todo，修复执行或 artifact，然后重试。 |
| `result_kind=replan_required` | 当前路线不再有效；写后继或 vision 增量。 |
| `result_kind=wait` | 现在不应运行任何 host 工作。 |
| `result_kind=user_action_required` | 显示具体用户动作，不要发明替代品。 |

失败的校验器不能提交或 spend；重放不调用任何东西。新逻辑 Turn 使用新的稳定 `--turn-instance-id`，而重试复用该 id。

## 适配另一 Runtime

当 Agent CLI 由受管理 runtime 支撑时，保持相同边界：

| Runtime 拥有 | LoopX 拥有 |
| --- | --- |
| Session、turn、sandbox、原始事件流、平台结果 | Goal、todo、gate、控制决策、紧凑 evidence、持久结果 |

Adapter 携带既有 `turn_key` 作为相关 id，创建或恢复 host run，消费其 Event/Outcome API，并发出一个既有结果种类。校验器独立读取测试、评分器或平台状态。Host 观察如 requested、accepted、running、outcome-ready、failed 与 resumed 映射到 committed、repair、replan 或 wait；它们不会变成新的 Turn 状态。

用真实任务、场景 owner、adapter owner、校验器与可度量结果验证新 adapter。只有在调用点证明紧凑结果无法携带该 evidence 时，才添加事件引用。

## 验证集成

仓库附带一个一次性资格验证，把原始 prompt、transcripts、凭据与临时 workspace 排除在 LoopX 状态之外：

```bash
python3 examples/loopx-turn-codex-cli-e2e-smoke.py
python3 examples/loopx-turn-codex-cli-e2e-smoke.py \
  --real-codex-cli \
  --codex-model <qualified-model>
python3 examples/loopx-turn-codex-cli-e2e-smoke.py \
  --real-codex-cli --turn-count 3 --codex-model <qualified-model>
```

第一条命令确定且与模型无关。第二条命令做一次真实 Codex CLI 调用，必须报告 `status=committed`、`validation_status=passed`、一次 quota spend，以及一个无副作用的重放。紧凑的 `codex_cli_model_requires_newer_codex` 结果是 host 兼容性失败，不是任务进展；它必须显示零状态写入与零 quota spend。

第三条命令对同一个临时 goal 与 todo 做 N 次真实调用。它开始一个不透明 session，为 Turn 2 到 N 恢复它，并独立校验每个标记。用 `--turn-count 3`，成功报告 `committed_turn_count=3`、`session_resumed=true` 与三次 quota spend。Session id 保持私有，从不打印或同步。

这就是完整的伙伴面向路径。实现细节见 [adapter 说明](codex-cli-automation-driver.md) 或 [Turn 协议](../../../reference/protocols/loopx-turn-v0.md)。
