# host_mode_plan_v0

`host_mode_plan_v0` 是 LoopX 工作流的公开安全 host 模式选择器。它位于交付的 [LoopX Turn](loopx-turn-v0.md) 与 [runtime connector catalog](../../integrations/runtime-connector-catalog.md) 之上：从意图与广告的 host 能力选择面向用户的 host 模式，然后打印匹配的预览命令。它不是启动器、scheduler、权限授予、验证器或第二事实来源。

它解决的问题是运维歧义。用户可能说「我关闭可见 UI 后继续工作」「让聊天创建工作」或「从定时器唤醒」。这些是不同的 host 模式，但都必须保留相同的 LoopX 恒等式：作用域 agent 身份、工作前的配额 guard、零花费安静检查、独立验证、持久化 writeback，以及仅在已验证 writeback 之后的配额花费。

## 边界

选择器返回 `mode=dry_run_host_mode_selector`。它不得启动进程、打开会话、布设定时器、调用聊天网关、验证结果、写入 LoopX 状态或花费配额。对于任何执行路径，`loopx_turn_v0`、TurnEnvelope、registry、quota、todo 投影与 run 历史保持权威。

对于无头执行，选择器映射到 `loopx turn plan`，然后是既有 Turn 生命周期：

```text
LoopX 决策 -> host 适配器执行 -> 独立验证器证明 -> LoopX 提交
```

该映射是关键产品价值：选择器使模式选择可见，而不发明并行 runner 或第二工作流权威。

## 模式

| 模式 | connector / 契约 | 合适场景 | 所需能力 |
| --- | --- | --- | --- |
| `visible_tui` | `codex_cli_tui` connector | 用户想观察或引导每一 Turn | `visible_session` |
| `isolated_headless_turn` | 带 `generic-cli` 与 `isolated-headless` 的 `loopx_turn_v0` | 通过类型化 host 结果做有界无人值守工作 | `loopx_turn`、`typed_host_adapter`、`independent_validator` |
| `im_gateway` | gateway/webhook connector | 聊天或其他界面应创建持久化工作 | `chat_gateway` |
| `shell_service` | shell worker 加 LoopX Turn | cron、launchd、服务定时器或手动 shell 唤醒 | `service_timer`、`shell`、`loopx_turn`、`typed_host_adapter`、`independent_validator` |
| `hybrid_handoff` | 显式转换契约 | 一种模式应在另一种模式中升级或继续 | 至少两种具体模式就绪 |

## 意图与能力信号

公开安全 `user_intent` 信号在未知时失效关闭：

- `watch_each_turn` -> `visible_tui`；
- `continue_without_ui` -> `isolated_headless_turn`；
- `intake_from_chat` -> `im_gateway`；
- `timer_keepalive` -> `shell_service`；
- `escalate_between_modes` -> `hybrid_handoff`。

公开安全 `host_capabilities` 信号有：

- `visible_session`；
- `loopx_turn`；
- `typed_host_adapter`；
- `independent_validator`；
- `chat_gateway`；
- `service_timer`；
- `shell`。

首个意图选择 `selected_mode`。每个模式选项仍报告 `capability_ready`，使操作员能看到所选 host 实际能否运行期望模式。

## 可见 Host 身份

粗略的 `visible_session` 能力无法区分 Codex CLI、Claude Code 或 Pi 等另一个通用可见 host。因此规划器在未提供显式目录注册 `host_identity` 时对 `visible_tui` 失效关闭（`--host-identity`：`codex-cli`、`claude-code`、`generic-cli`，或 `pi` 别名）。没有身份时，可见选项报告 `connector_id=null`、`host_resolution=identity_required`、`turn_mapping.host=null`、`capability_ready=false`、一条指名缺失身份的阻塞原因，以及一个停首的下一步；不编造 Codex CLI 默认。未注册身份同样得到 `connector_id=null` 且 `host_resolution=unregistered_host_identity`。解析状态存放在单独类型化的 `host_resolution` 字段中，使 `connector_id` 字段只携带真实运行时 connector 目录 id。有身份时使用类型化映射：`codex-cli` -> `codex_cli_tui`、`claude-code` -> `claude_code_loop`、`generic-cli` -> `generic_cli_visible_loop`（经 generic-cli Turn host 运行的可见 host loop）、`pi` -> `pi_goal_loop`（Pi 也经 generic-cli Turn host 运行，同时保留自己的 connector 身份）。每个发出的 connector id 都必须存在于运行时 connector 目录；无注册目录 connector 的身份失效关闭，而不是发出动态字符串。

## 就绪与证明

就绪失效关闭：一种模式只有在 `required_host_capabilities` 中列出的每个能力都被广告时才报告 `capability_ready=true`。由于 `shell_service` 证明类型化 host 结果与独立验证，这些能力是其要求的一部分；仅有 `service_timer`、`shell` 与 `loopx_turn` 的 host 不算就绪。每个模式选项还报告 `missing_host_capabilities`、人类可读的 `blocking_reasons` 与 `recommended_next_steps`，使操作员在该模式尝试前知道要补什么。模式未就绪时，首个推荐步骤是 `stop`：操作员补齐差距并重跑选择器，然后才把任何预览命令视为可运行。`im_gateway` 就绪时，其步骤是摄取优先：从聊天/webhook 界面创建持久化工作，确认 LoopX 状态可安全继续，然后选择执行模式（无人值守运行用 `isolated_headless_turn`，用户关卡用 `visible_tui`），而不把网关当作执行器。

## 形状

```json
{
  "schema_version": "host_mode_plan_v0",
  "mode": "dry_run_host_mode_selector",
  "agent_model": "peer_v1",
  "goal_id": "loopx-meta",
  "agent_id": "codex-main-control",
  "selected_mode": "isolated_headless_turn",
  "selected_connector_id": "loopx_turn",
  "selected_turn_mapping": {
    "host": "generic-cli",
    "execution_mode": "isolated-headless",
    "scheduler_owner": "outer_controller",
    "plan_command": "loopx turn plan --goal-id loopx-meta --agent-id codex-main-control --host generic-cli --execution-mode isolated-headless --scheduler-owner outer_controller"
  },
  "next_preview_command": "loopx turn plan ...",
  "mode_options": [],
  "identity_contract": {},
  "no_spend_policy": {},
  "turn_contract": {},
  "transitions": [],
  "boundary": {},
  "truth_contract": {}
}
```

每个 `mode_options[]` 条目包括 connector id、就绪状态、必需 host 能力、存在的 Turn 映射、scheduler 执行上下文、配额 guard 命令与所需证明。

## 功能点

选择器提供四个具体功能：

1. **模式选择：** 把用户意图变成命名 host 模式，而不是迫使人与 agent 手动推断可见/无头/网关/定时器行为。
2. **Turn 映射：** 对于无人值守执行，打印保留 host、执行模式、scheduler owner、agent id 与可用能力的精确 `loopx turn plan` 预览。
3. **就绪界面：** 在模式可被信任之前报告哪些广告能力缺失。
4. **安全交接计划：** 命名转换，如可见引导到隔离无头 Turn、无头用户关卡升级回可见 TUI、网关摄取到 Turn、shell 定时器到可见升级。

## 验收检查

一个 fixture 或实现在以下条件下可接受：

1. `schema_version=host_mode_plan_v0` 且 `mode=dry_run_host_mode_selector`；
2. 五个规范模式都存在且意图选择预期模式；
3. `isolated_headless_turn` 映射到 `loopx turn plan --host generic-cli --execution-mode isolated-headless --scheduler-owner outer_controller`；
4. 作用域身份以 `--agent-id` 流入 Turn 与配额预览命令；
5. 零花费策略覆盖选择器预览、Turn 计划预览、安静 monitor、仅节奏变更与最终/就绪检查；
6. 边界声明选择器不执行、不写入、不花费、不推断生产权限、不推断凭据访问、不推断破坏性权限；
7. 没有模式在能力支撑的必需证明不可用时报告 `capability_ready=true`（包括 `shell_service` 要求同时具备 `typed_host_adapter` 与 `independent_validator`）；
8. 选择 `visible_tui` 时必需可见 `host_identity`，对 Codex CLI 与 Claude Code 等不同 host 在 connector id、Turn 映射与预览命令中保持区分，且每个发出的 connector id 都存在于运行时 connector 目录（未解析映射发出 `connector_id=null` 加类型化 `host_resolution`，而非非目录值）；
9. 交接保留所选 agent id 并暴露目标就绪状态；并且
10. 未知意图或 host 能力值带建议失效关闭。
