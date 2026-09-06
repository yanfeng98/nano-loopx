# 实验性 Planner-Worker 模式


状态：**实验性**，opt-in，provider-neutral。它不是常驻调度器，也不是 LoopX 的
默认多 Agent runtime。一次调用运行一个有界的 Planner → Worker → 验证切片，并
返回 typed receipt。

使用
`examples/experiments/planner_worker/runtime-smoke.py` 中交付的 fake adapters，
无需在线模型 provider 即可学习契约。TraeX 只是可选的扩展 provider 之一。

## 操作者契约

| 规则 | 要求 |
| --- | --- |
| 干净工作区 | Planner 运行前，工作区必须是没有任何脏改或未跟踪变更的 git worktree。 |
| 显式模型路由 | 调用方为 `planner`、`cheap_worker` 与 `strong_worker` 传入 `model_routes`。缺少路由时 fail closed。 |
| 调用方批准的验证 | 每个 `validation_commands` 条目必须出现在调用方 allowlist 中。未批准的命令在 Worker 写入前停止。 |
| 单步 receipt | 每次 `run_planner_worker_once` 最多选择一个可执行步骤，执行一次，并返回 `planner_worker_receipt_v0`。 |
| 不完整成本 | Receipt 在收到定价之前始终设置 `cost.complete=false`；token `usage` 仍可能是完整的。 |
| Provider opt-in | Core 拥有契约与 fake runtime。在线 provider（例如 TraeX）保持可选，且必须显式调用。 |
| 停止 | 不自动重启或调度另一个切片。读取 receipt 的 `status`/`reason` 并退出；任何后续调用前清理或重置工作区。 |

## Fake Runtime 走查

```bash
python3 examples/experiments/planner_worker/contract-smoke.py
python3 examples/experiments/planner_worker/runtime-smoke.py
```

runtime smoke 构建一个临时干净 git fixture，注入 fake Planner 与 Worker adapters，
把 `python3 verify.py` 加入 allowlist，并断言一个验证通过的完成 receipt。它证明：

- 脏工作区在 observer 边界被拒绝；
- Worker 看到显式的 cheap-worker 模型路由；
- 验证只运行已批准的命令；
- `usage.complete` 可以为 true，而 `cost.complete` 保持 false。

## 可选 TraeX Provider

仅当你有意 opt-in 一个真实 TraeX 二进制时：

```bash
python3 scripts/experiments/traex_planner_worker_probe.py \
  --cwd /path/to/clean/worktree \
  --validation-command 'python3 -m pytest -q tests/test_target.py'
```

显式传入每个已批准的验证命令。探测前保持工作区干净。把 TraeX 输出当作一个
包装着同一 typed receipt 的 provider 探测载荷——而不是 LoopX 内核写回权威。

## 该模式不是什么

- 不是 heartbeat、cron 或常驻多 Agent 调度器。
- 不是 [runtime connector catalog](../integrations/runtime-connector-catalog.md) 中
  `loopx turn run-once` 或 host-mode connector 的替代品。
- 不是自动 quota 花费、todo 写回或默认产品编排。

一个 receipt 之后就停止。任何后续切片都是新的调用方决策：新的干净工作区、
显式路由与新的已批准验证集。

## 相关界面

- 契约与 runtime：`loopx/experiments/planner_worker/`
- 公开 smokes：`examples/experiments/planner_worker/`
- 目录索引：[Runtime connector catalog](../integrations/runtime-connector-catalog.md)
