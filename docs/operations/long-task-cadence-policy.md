# 长任务 Cadence 提示

> [English](long-task-cadence-policy.md)

LoopX 不应让重复的 heartbeat turn 把长时 Agent 工作拆成微小的仅状态 turn。
cadence hint 是一个小的、派生的信号，告诉 host 或 controller 最近的工作看起来是
blocked、actively runnable、thin、material 还是 unknown。

它刻意不是 scheduler 策略。Quota、gate、goal 边界、权限、公共/私有扫描和
用户/controller 决策仍是真相源。

## 为什么存在

Heartbeat 自动化有用是因为它让目标保持存活，但当每个 turn 都被当作独立小任务时，
频繁唤醒会把工作切碎。提示帮助产品面注意到这些模式：

- 重复的状态或单面写回，没有连贯 artifact；
- 一个加宽不安全的真实 gate；
- 最近的验证进度允许保持当前 cadence；
- 元数据缺失或不完整，产品应避免强声明。

提示应温和地引导下一个 turn。它不得授予权限、跳过 gate、授权破坏性 git、
启动生产动作、复制私有材料，或暴露对话转录、原始本地日志、凭据、benchmark 任务文本、
verifier 输出或本地绝对路径。

## 公共字段

Status 与 quota 可以暴露这个紧凑投影：

```json
{
  "long_task_cadence_hint": {
    "schema_version": "cadence_hint_v0",
    "signal": "thin_progress",
    "recommendation": "widen",
    "reason_codes": ["repeated_surface_only"]
  }
}
```

稳定字段：

| 字段 | 值 | 含义 |
| --- | --- | --- |
| `schema_version` | `cadence_hint_v0` | 公共投影形状。 |
| `signal` | `blocked`、`active_work`、`thin_progress`、`material_progress`、`unknown` | 最近控制面证据的暗示。 |
| `recommendation` | `wait`、`widen`、`keep` | 轻量 host/controller 提示。 |
| `reason_codes` | 紧凑字符串 | 信号的机器可读解释。 |
| `authority` | 紧凑字符串，可选 | 调和了较早兼容性提示的最终权威。 |
| `superseded` | 紧凑提示，可选 | 保留供诊断的较早信号、推荐与 reason codes。 |

典型示例：

```json
{
  "schema_version": "cadence_hint_v0",
  "signal": "blocked",
  "recommendation": "wait",
  "reason_codes": ["quota_state_operator_gate", "open_user_todos_visible"]
}
```

```json
{
  "schema_version": "cadence_hint_v0",
  "signal": "active_work",
  "recommendation": "keep",
  "reason_codes": ["final_agent_scoped_active_work"],
  "authority": "final_agent_scoped_interaction_and_scheduler",
  "superseded": {
    "signal": "blocked",
    "recommendation": "wait",
    "reason_codes": ["quota_state_operator_gate"]
  }
}
```

```json
{
  "schema_version": "cadence_hint_v0",
  "signal": "material_progress",
  "recommendation": "keep",
  "reason_codes": ["implementation_plus_validation_latest_turn"]
}
```

```json
{
  "schema_version": "cadence_hint_v0",
  "signal": "unknown",
  "recommendation": "keep",
  "reason_codes": ["missing_recent_runs"]
}
```

## 如何派生

提示从现有 public-safe 控制面元数据派生：

- 最近 run 的 `delivery_batch_scale`、`delivery_outcome` 和
  `delivery_turn_kind`；
- 配置的执行 profile 的小步阈值；
- quota 状态；
- 开放用户 todo 是否已经可见。

Status 投影可以在最终 Agent 作用域仲裁之前计算。如果那个较早的兼容性提示说
`wait`，但最终 Agent 通道要求一次尝试、禁止 quiet no-op，且最终 scheduler 选择
`run_now` / `active_work`，quota 把提示调和为 `active_work` + `keep`。
最终 interaction contract 与 scheduler 被命名为权威，而较早的信号与 reason codes
留在 `superseded` 下。这种精确调和不适用于真正的阻塞用户 gate。

当前的"薄进展"检测器刻意保守。它基于 Agent 写回元数据，而不是对实际 Agent
loop 运行时的完美度量。经过的实际时间可能成为未来可选输入，但不应是主要裁判：
一个短的已验证修复可以很有价值，一个长 turn 也可能仍卡住。

## Controller 用法

- `blocked` + `wait`：不要加宽；显示具体 gate 或 blocker。
- `active_work` + `keep`：遵循最终 Agent 作用域交互与 scheduler 决策；
  `superseded` 只用于诊断。
- `thin_progress` + `widen`：下一个合格 turn 应尝试连贯 artifact 加验证/写回，
  或写一个说明为何加宽不安全的 blocker。
- `thin_progress` + `keep`：最新 turn 较小，但连续度还不足以引导下一个 turn。
- `material_progress` + `keep`：最近工作产生了更宽的 artifact、验证或里程碑。
- `unknown` + `keep`：元数据缺失或不完整；避免强烈的自动化改动。

该契约当前的 smoke 是
`python3 examples/long-task-cadence-policy-smoke.py`。
