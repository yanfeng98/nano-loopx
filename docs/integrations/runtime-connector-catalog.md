# Runtime 连接器目录


状态:面向 LoopX 宿主/runtime 连接器的公开安全 v0 目录。

LoopX 可以在许多执行界面旁边并行运行,而无需成为执行 runtime 本身。连接器目录
以用户可见的术语命名这些界面,并把每一个映射回相同的内核契约:注册表、活动
状态、todo、配额、scheduler 提示、gate、证据与公开/私有边界。

该目录不是第二事实源。它是覆盖宿主循环的前台索引:这些循环可以唤醒 agent、向
LoopX 询问工作是否被允许、写回已验证状态,并暴露足够的活性信息,让用户与维护者
能够对工作做出判断。

## 连接器字段

| 字段 | 含义 |
| --- | --- |
| `id` | 稳定连接器 id,供文档、状态投影与 smoke 使用。 |
| `surface` | 用户可见的宿主界面或 runtime 系列。 |
| `execution_mode` | 宿主循环如何运行:可见 TUI、app 心跳、本地 scheduler、webhook 或 bridge。 |
| `wake_triggers` | 启动一轮受管 LoopX Turn 的条件是什么。 |
| `state_writeback` | 验证后工作的 LoopX 写回路径。 |
| `liveness_signal` | 在不复制原始日志的前提下表示宿主循环存活的最小信号。 |
| `stop_reset_policy` | scheduler 提示、最终检查或宿主停止规则如何应用。 |
| `budget_meter` | 连接器如何把工作映射到配额或无消耗监视策略。 |
| `human_visibility` | 用户无需读取私有状态即可看到什么。 |
| `boundary` | 连接器不得复制、推断或变更什么。 |
| `smoke_expectation` | 保护连接器契约的聚焦公开检查。 |

## 初始目录

| id | surface | execution_mode | wake_triggers | state_writeback | liveness_signal | stop_reset_policy | budget_meter | human_visibility | boundary | smoke_expectation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `codex_app_heartbeat` | Codex App 自动化 | 调度的 headless app 线程 | Codex App 心跳 RRULE;`scheduler_hint.reset_policy.reset_token` | `todo` 生命周期、`refresh-state`,然后验证后 `quota spend-slot` | 心跳运行加配额事件 | 应用 `scheduler_hint.codex_app` 重置/退避;仅节奏变化不消耗 | 验证后的写回之后,按 goal/按 agent 的配额槽 | 可见线程、心跳 XML,以及需要时的具体 user todo | 生成的心跳提示;作用域限定的 `--agent-id`;没有项目特定提示分支 | 提示 smoke 覆盖 scheduler 提示、重置令牌、身份与无消耗节奏变化。 |
| `codex_app_ssh_goal` | 通过 SSH 连接远程工作区的 Codex App | 可见交互式 Goal 循环 | 宿主 `/goal` 续接;无自动化工具依赖 | 相同的 CLI todo/refresh/spend 路径,验证后带 `--source visible-goal` | 可见 Goal 状态加紧凑 LoopX 状态 | 仅在终态且无跟进时完成;三次未变化的被阻止 Turn 之后,原生 `update_goal(status=blocked)` 停止宿主续接,而 LoopX 保持活动;用户 `/goal resume` 重新激活它 | 验证后的写回之后配额槽;gate、等待、最终检查或宿主阻止不消耗 | 用户看到活动 Codex 任务及其具体 gate 或下一动作 | 生成的消息体保持在 `/goal` 4000 字符限制内,绝不虚构 `LOOPX_TURN`,也绝不调用 `automation_update` | Agent-onboard smoke 验证确切宿主选择、类型化 scheduler 上下文、消息体预算、有界静默停止,以及不存在仅心跳指令。 |
| `codex_cli_tui` | Codex CLI TUI | 可见交互式终端循环 | 用户 bootstrap、`/goal` 或可见续接 | 相同的 CLI todo/refresh/spend 路径 | TUI 转录加紧凑 LoopX 状态 | 在类型化未变化限制之后,使用相同的原生 `update_goal(status=blocked)` 与 `/goal resume` 契约 | 验证后的写回之后配额槽;被阻止/最终检查转移不消耗 | 用户看到活动 TUI Turn | 不要静默切换到隐性 headless 执行,也不要复制原始转录 | TUI 提示/bootstrap smoke 覆盖作用域身份与原生 blocked/resume 语义。 |
| `claude_code_loop` | Claude Code 循环 | 可见本地 agent 循环 | slash 命令、本地循环 tick 或宿主循环续接 | 相同的 CLI todo/refresh/spend 路径 | 循环状态加紧凑转录指针 | 当配置了未变化限制时,停止前做最终配额/replan 检查 | 验证后的写回之后配额槽;停止/最终检查不消耗 | 用户看到本地循环状态与响应 | 不含私有材料、凭证、生产动作或隐性批准旁路 | Loop smoke 覆盖作用域身份、未变化最终检查与不消耗的停止。 |
| `opencode_goal_loop` | OpenCode goal 模式 | 由 LoopX gate 的可见 OpenCode goal 插件循环 | 已安装 opt-in OpenCode goal bridge 时的 `/loopx <task>` | 经由 bridge 的相同 CLI todo/refresh/spend 路径 | bridge 状态加紧凑 LoopX 状态 | 当配置了未变化限制时,循环停止前做最终配额/replan 检查 | 验证后的写回之后配额槽;停止/最终检查不消耗 | 用户看到 OpenCode goal Turn 与 bridge 状态 | bridge 安装保持 opt-in;不复制原始转录、凭证或本地会话路径 | OpenCode bridge 测试与 host-mode 选择器 smoke 覆盖作用域身份与目录一致性。 |
| `opencode2_goal_worker` | OpenCode 2 goal 模式 | 持久的进程外 worker,通过其 HTTP API 驱动可见 OpenCode 2 会话 | `loopx opencode2-goal-worker --goal-id <id> --directory <dir>` | 经由 worker 的相同 CLI todo/refresh/spend 路径 | worker 状态文件、宿主轮询回执与紧凑 LoopX 状态 | 未变化轮询限制以可见合成通知停止循环;探测失败以有界退避重试 | 验证后的写回之后配额槽;等待、通知或最终检查不消耗 | 用户看到 OpenCode 2 会话 Turn、续接提示与停止/暂停通知 | worker 状态保持在 `$XDG_STATE_HOME/loopx/opencode2` 下;不复制原始转录、凭证或本地会话路径 | worker 契约测试覆盖 Turn 循环、可见停止、租约防护(lease fencing)与用户消息续接。 |
| `pi_goal_loop` | Pi goal 模式 | 由 LoopX gate 的可见 Pi goal 扩展循环 | 已安装 opt-in Pi goal 扩展时的 `/loopx <task>` | 经由扩展的相同 CLI todo/refresh/spend 路径 | 扩展状态加紧凑 LoopX 状态 | 当配置了未变化限制时,循环停止前做最终配额/replan 检查 | 验证后的写回之后配额槽;停止/最终检查不消耗 | 用户看到 Pi goal Turn 与扩展状态 | 扩展安装保持 opt-in;绑定保持在项目 `.loopx/` 树中;不复制原始转录、凭证或本地会话路径 | Pi 扩展源代码契约测试与 host-mode 选择器 smoke 覆盖作用域身份与目录一致性。 |
| `shell_worker` | shell、cron、launchd 或服务定时器 | headless 本地命令 | cron/服务/手动 shell 唤醒 | 来自项目 checkout 的 CLI 写回命令 | 退出码、run id 与紧凑状态 | 遵循本地 `scheduler_hint` 退避/重置;缺少 goal 或 agent id 时失败即关闭 | 投递的配额槽;仅监视轮询保持无消耗 | 日志或状态命令,而非原始状态文件 | 不要把本地路径、密钥或项目政策写死到可复用脚本 | 命令示例使用全局注册表、`--agent-id` 与无消耗监视行为。 |
| `http_webhook` | HTTP webhook 或本地 daemon | 请求驱动的 bridge | loopback 回调、webhook 或宿主事件 | 适配器验证后发出 LoopX todo/gate/证据事件 | 请求日志加紧凑状态导出 | webhook 不自轮询;除非某个 scheduler 拥有重试,否则 scheduler 提示仅为建议 | 仅在接受的写回之后消耗配额 | Dashboard/状态流 | 默认 loopback;写入端点要求显式 dry-run/预览与 CLI 等价兜底 | loopback smoke 拒绝远程状态/写入权威,并验证预览门控写入。 |
| `worker_bridge` | Worker Bridge | 外部执行器、任务容器或远程 worker bridge | worker 事件、bridge 消息或 runner sidecar | bridge 发出紧凑的公开安全状态、todo 或证据 | worker 心跳/状态与紧凑计数器 trace | 宿主特定的停止/重置映射回 scheduler 提示与结果政策 | 已接受工作的配额事件;bridge 证据不授予任务评分权威 | Dashboard/前台投影与紧凑证据时间线 | 剥离原始日志、本地路径、私有 trace、任务文本与凭证 | Worker Bridge 安装/状态 smoke 验证来源挂载、计数器 trace 与私有边界剥离。 |
| `computer_use_runtime` | 浏览器、桌面或应用自动化 runtime(是 provider/runtime 执行界面,不是 LoopX 产品能力,也不是 `value-connectors` 连接器) | 可见或可回放的 UI 执行界面 | 来自拥有方能力的受限动作请求、宿主回放事件或用户接管交接 | 交给拥有方能力域本地 reducer 的紧凑类型化回执(仅事实),由该 reducer 向 Kernel 验证提出 LoopX gate/证据写回 | 宿主拥有的回放/截图指针加紧凑回执字段 | 在未知弹窗、隐私不明或最终外部写入动作处停止;scheduler 提示仍然来自 LoopX 配额 | 仅在拥有方能力的 reducer 提案被 Kernel 接受后消耗配额;就绪/档案检查保持无消耗 | 带意图动作、禁止效果类别、证据句柄与接管路径的评审卡片 | 不复制凭证、cookies、原始截图、私有 UI 消息体,不执行无确切 gate 的发送/购买/生产变更;provider 绝不能自己编写 Kernel 写回 | 合成 runtime-profile/动作请求/回执 smoke 验证先 gate 后写、原始证据剥离,以及拒绝 provider 编写的写回字段。 |
| `deepseek_harness_loop` | DeepSeek Harness | 经 LoopX Turn 的隔离 headless 有界执行 | 带 `loopx.dsh_goal_mode` 的 `loopx turn run-once`(兼容:`scripts/dsh_turn_host_adapter.py`) | 验证 dsh 结果后的相同 CLI todo/refresh/spend 路径 | 紧凑 Turn 回执加本地 dsh 会话指针 | 外部控制器遵循 scheduler 提示;预览/失败验证保持无消耗 | 仅在验证后的写回之后配额槽 | 操作员看到类型化结果、验证器回执与下一预览命令 | 不复制 dsh JSONL 会话、原始转录、凭证、本地路径或模型工具日志 | 适配器 smoke、fake-dsh e2e 与 real-dsh e2e 验证类型化结果成形、真实 dsh runtime 启动、写回与回放幂等。 |
| `loopx_turn` | LoopX Turn 宿主适配器 | 隔离 headless 有界执行 | `loopx host-mode-plan` 选择模式,然后 `loopx turn plan` 预览一个类型化决策 | `loopx turn run-once --execute` 仅在独立验证后写回 | 紧凑 Turn 回执与 scheduler 执行上下文 | 外部控制器遵循 scheduler 提示;仅节奏/预览工作保持无消耗 | 仅在验证后的写回之后配额槽 | 操作员看到所选宿主、执行模式、验证器要求与下一预览命令 | 不发布不透明会话句柄、原始转录、本地路径、凭证或宿主本地日志 | host-mode-plan smoke 验证宿主模式选择、作用域身份、Turn 映射与可见/headless/混合交接就绪。 |

### 可复用的 shell_worker 参考

`scripts/external_scheduler_worker.py` 是一个感知 scheduler 提示的
`shell_worker`,用于通用可见 CLI 循环。每个 tick 运行
`quota should-run --include-detail scheduler`,投影一行公开安全状态
(`waiting`/`should_run`/`terminal`、节奏类别、下次检查分钟数、未变化次数),并按
`local_scheduler` 进阶阶梯休眠。它在一个小的状态文件中跟踪连续未变化索引,并在
`scheduler_hint.reset_policy.reset_token` 变化时将其重置。它默认仅观察;只有要
触发有界 headless Turn 时才传 `--wake-cmd`(例如
`loopx turn run-once ... --execute`)。它不能在可见 TUI 中输入,因此不替代交互式
宿主循环。一个 launchd 模板随附在
`examples/external-scheduler-worker.launchd.plist`,契约由
`examples/external-scheduler-worker-smoke.py` 守护。生产者生成的有界等待
scheduler 提示与 Pi 之间存在一个薄的消费者一致性(parity)契约,包括由第三次
未变化轮询触发的最终配额/replan 复查;它由
`tests/test_host_loop_runtime_parity.py` 与 `tests/pi_goal_loop_runtime.test.mjs`
中的 Pi runtime 测试守护。

## 外部工具扩展候选

MCP 服务器在 LoopX 周围可以扮演两种不同角色:

- 一个 **LoopX 宿主适配器**:向具备 MCP 能力的宿主暴露 LoopX 生命周期读取与
  受控写入;
- 一个 **外部工具扩展**:把另一个产品的工具暴露给宿主,并作为 LoopX 结果能力
  之后的可替换 provider。

以下条目是探索记录,不是可用性声明。目录化一个扩展并不增加 LoopX 能力、宣传
已可用能力,也不授予凭证、网络访问、私有读取或外部写入权威。

| id | 上游界面 | 状态 | 可能的 LoopX 绑定 | 集成前的边界 | 晋升证据 |
| --- | --- | --- | --- | --- | --- |
| `official_xmcp` | X Developer Platform [XMCP](https://github.com/xdevplatform/xmcp) 与[官方 MCP 文档](https://docs.x.com/tools/mcp) | `catalogued_not_integrated`;无 LoopX 安装检查或线上资格认定 | 现有 `content-ops` / `social_browser_x` 结果路径的可选 MCP provider;不是新能力,也不是替代控制面 | 宿主拥有 OAuth 材料与 X API 成本/速率限制。从显式只读工具 allowlist 开始。发帖、回复、点赞、关注、DM、账户变更、付费查询与私有扩展都要求确切 LoopX gate。不要把原始帖子、时间线、DM、令牌或 MCP 载荷投影进公开状态。 | provider 中立的操作地图;无凭证的安装/就绪检查;仅元数据的公开读取包;确切的写入/私有/成本 gate 计划;紧凑回执;聚焦契约 smoke。真实的 X 线上 E2E 属于后续 owner 授权的资格认定,目录状态不要求它。 |

XMCP 是官方本地 MCP 服务器,在启动时从 X API OpenAPI 规范派生 200 多个工具。
因此,其上游 allowlist 是安全与成本边界,而不仅仅是输出预算优化。LoopX 适配器
应暴露一个小型操作档案,例如公开账户查询与有界的近期搜索,而不是转发完整生成
的工具界面。流式与 webhook 端点不在 XMCP 的请求/响应界面内;持久监视仍需单独的
宿主 scheduler 或事件连接器,由常规 LoopX 监视契约治理。

X 还在 `https://docs.x.com/mcp` 托管一个仅文档的 MCP。该服务器可能帮助实现 agent
查看当前 X API 文档,但它不提供社交来源证据,且绝不能报告为 `social_browser_x`
runtime 就绪。

只有当用户结果、provider 中立数据包、CLI 入口点、gate 模型与聚焦 smoke 全部稳定
时,才把扩展候选晋升到能力路径。在此之前,该扩展仍是现有能力之后的可互换基础
设施。

## 投影规则

- LoopX 内核对象保持权威:注册表、活动 goal 状态、todo、运行历史、配额账本、
  gate 与证据指针。
- 连接器可以把宿主事实投影到状态或 Dashboard 卡片,但绝不能把原始转录、原始
  日志、凭证、本地绝对路径或私有 artifact 存储进公开状态。
- 每个投递 Turn 都以按 `goal_id` 与注册 `agent_id` 限定的 `quota should-run`
  开始。
- 节奏更新、重置令牌处理、最终配额检查、循环退出与仅监视轮询不消耗投递配额。
- user gate 必须呈现具体的 user todo 或问题。如果缺少载荷,连接器应报告投影
  错误,而不是静默等待。
- 验证后的投递在配额消耗之前以持久写回结束:todo/状态/证据更新、
  `refresh-state` 与一次配额消耗事件。

## Smoke 预期

连接器 smoke 应保持狭窄。它们保护可复用契约,而不是某位维护者的本地自动化:

- 提示与 bootstrap smoke 覆盖作用域身份、`scheduler_hint`、重置政策与无消耗
  节奏或最终检查行为;
- 本地状态/服务器 smoke 覆盖仅 loopback 默认值、只读浏览器投影与写入前的显式
  dry-run/预览;
- bridge smoke 覆盖紧凑写回载荷、活性计数器与私有边界剥离;
- todo/写回 smoke 覆盖验证工作序列,并验证仅监视或仅停止路径不消耗配额。

## 实验性 planner-worker 模式

planner-worker 是一个 **opt-in 实验性**切片,不是目录连接器,也不是常驻
scheduler。一次调用完成规划、最多执行一个 worker 步骤、运行调用者批准的验证,
并返回类型化回执。模型路由保持显式;在提供定价之前成本保持不完整;线上 provider
由调用方显式提供。

操作员指南(provider 中立的 fake runtime):
[实验性 planner-worker 模式](../guides/planner-worker-experimental.md)。

公开检查:

```bash
python3 examples/experiments/planner_worker/contract-smoke.py
python3 examples/experiments/planner_worker/runtime-smoke.py
```

## 相关契约

- [宿主模式计划 v0](../reference/protocols/host-mode-plan-v0.md)
- [LoopX Turn v0](../reference/protocols/loopx-turn-v0.md)
- [心跳自动化提示](../heartbeat-automation-prompt.md)
- [宿主集成面 v0](../reference/protocols/host-integration-surface-v0.md)
- [Computer-use runtime v0](../reference/protocols/computer-use-runtime-v0.md)
- [Value connectors](../../loopx/capabilities/value_connectors/README.md)
- [Session runtime 到 LoopX 的投影 v0](../reference/protocols/session-runtime-loopx-projection-v0.md)
- [Worker Bridge 安装契约](worker-bridge-install-contract.md)
- [配额分配](../quota-allocation.md)
- [实验性 planner-worker 模式](../guides/planner-worker-experimental.md)
