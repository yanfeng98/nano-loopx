# 会话运行时受控 writeback v0

状态：外部 agent 运行时元数据写入的公开安全协议草稿。

本契约定义了 `session_runtime_loopx_projection_v0` 证明只读价值之后的第一个 writeback 边界。目标不是让 LoopX 直接驱动运行时。目标是让外部运行时以元数据或事件指针的形式携带紧凑的 LoopX 决策，使一个可见会话能够恢复、交接，并解释它为何被允许继续。

## 进入条件

只有在以下条件全部成立时，受控 writeback 才可用：

1. 只读投影已存在，并标识 `goal_id`、`agent_id`、`runtime_id`、`session_id` 以及至少一个 LoopX `run_id` 或 `todo_id`。
2. LoopX 源事件已经通过 CLI 或 CLI 等价适配器记录。
3. 运行时目标支持 dry-run 或 preview 路径。
4. 载荷是紧凑元数据，而不是原始 transcript、原始工具输出、本地路径、凭据或私有文档正文。
5. 适配器能够不靠猜测地把已应用、已跳过、已拒绝或失败的结果报告回 LoopX。

任一进入条件缺失时，适配器必须保持只读模式，并通过 LoopX 写入一个 blocker 或用户 todo，而不是尝试 host 写入。

## 写入类别

| LoopX 源 | 运行时目标 | 允许载荷 | 不得意指 |
| --- | --- | --- | --- |
| `operator_gate` 决策 | 类批准运行时事件或元数据 | decision id、decision label、actor class、原因摘要、源 run id | 运行时权限覆盖、隐藏批准、生产授权 |
| `human_reward` overlay | 绑定 run 的判定元数据 | reward id、被判定 run id、decision label、公开安全原因 | 模型分数、benchmark 分数或任务 pass/fail 冒充 |
| `quota_decision` | scheduler 提示元数据 | eligible/throttled/monitor 提示、window id、原因码 | 计费决策、启动权限或隐藏会话开始 |
| `handoff_packet` | 会话元数据指针或消息草稿 | handoff id、下一动作、停止条件、evidence 指针 | 原始 transcript 复制、无界 prompt 注入或强制同会话控制 |
| 紧凑工件/run 指针 | 运行时工件注解 | artifact id、验证标签、结局类别 | 原始证据上传、本地路径暴露或私有日志镜像 |

Writeback 刻意比 host 集成界面更窄。Todo 创建、gate 记录、reward 记录、refresh-state 与配额花费仍源自 LoopX。运行时只在 LoopX 记录权威事件之后接收紧凑反映。

## 最小形状

```json
{
  "schema_version": "session_runtime_controlled_writeback_v0",
  "goal_id": "loopx-meta",
  "agent_id": "codex-side-bypass",
  "runtime": {
    "runtime_id": "codex_cli_tui",
    "session_id": "public-safe-session-handle"
  },
  "loopx_source": {
    "source_run_id": "run_123",
    "source_todo_id": "todo_123",
    "source_event_class": "handoff_packet"
  },
  "writeback": {
    "write_class": "handoff_packet_pointer",
    "mode": "dry_run",
    "idempotency_key": "loopx-meta:run_123:handoff_packet_pointer",
    "payload": {
      "decision_label": "approved_next_action",
      "summary": "continue the validated next action until the stop condition fires",
      "evidence_pointer_count": 2
    }
  },
  "boundary": {
    "raw_transcripts_copied": false,
    "raw_tool_outputs_copied": false,
    "credentials_copied": false,
    "private_paths_copied": false,
    "launch_authority_granted": false
  },
  "result": {
    "status": "previewed",
    "runtime_event_id": "evt_123",
    "loopx_writeback_run_id": null
  }
}
```

dry-run 结果可以在本地控制面 UI 中显示。它不是继续运行的运行时命令。真正的 apply 仍须绑定到已记录的 LoopX 事件，并报告紧凑结果。

## 流程

1. 读取当前 LoopX 投影与 host 会话事实。
2. 验证进入条件与公开/私有边界。
3. 用 `idempotency_key` 构建 dry-run 载荷。
4. 显示或记录 dry-run 预览。
5. 只在相关 LoopX 事件已经存在且运行时适配器暴露匹配写入类别时应用。
6. 追加一条紧凑 LoopX 结果 run，`status=applied`、`skipped`、`rejected` 或 `failed`。

当运行时已经持有同一 `idempotency_key` 时，适配器可以跳过 apply。它仍必须把跳过报告为紧凑结果，使 LoopX 能区分「已反映」与「从未尝试」。

## 失败语义

受控 writeback 失效关闭：

- 只读投影缺失：保持只读并先请求投影。
- LoopX 源事件缺失：先记录 LoopX 事件。
- 运行时 dry-run 支持缺失：阻止 writeback，并把 CLI 保持为事实来源。
- 运行时目标不可用：记录 `failed` 或 `skipped`，而不是用户批准。
- 载荷不安全：拒绝载荷并创建公开安全 blocker。

运行时 writeback 失败不会使 LoopX 决策失效。它只表示 host 尚未收到紧凑反映。

## 验收检查

一个受控 writeback 适配器在以下条件下可接受：

1. 每个受支持写入类别都有 CLI 等价的 LoopX 源事件；
2. dry-run 在 apply 之前可用；
3. `idempotency_key` 防止重复运行时元数据；
4. 载荷排除原始 transcript、原始工具输出、凭据、本地路径、私有文档正文与生产日志；
5. 配额 writeback 被当作 scheduler 提示，绝不作为启动或计费权限；
6. 人类奖励 writeback 与 benchmark/任务评分明显区分；并且
7. 失败返回紧凑 blocker 或结果事件，而不是绕过关卡猜测。
