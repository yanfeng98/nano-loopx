# LoopX Pi Goal 模式

> [English](README.md)

Pi 的 LoopX 宿主适配器。Pi 是一个终端编码 agent，其 extensions 注册命令、工具与
事件处理器；本适配器把 Pi 会话变成受 LoopX 管控的可见 Goal 循环。

## 入口

- **`/loopx`** —— 无参数时运行 `loopx bootstrap-command-pack --project .`，并把
  packet 作为 widget 加一条 transcript 条目展示。带 goal 文本参数时，运行
  `loopx start-goal --guided --project . --goal-text "<text>" --host-surface pi`，
  并把返回的 packet 作为后续用户消息（`sendUserMessage`，带 `triggerTurn`）直接
  交给 agent，因此引导事务无需弹出框或手工 Enter 步骤。
  `/loopx resume` 在用户暂停或运行中止后重新武装自动延续。
- **`loopx_goal_activate`** —— agent 可调用工具。用其一次性 `activationToken` 加
  心跳 `objective`/task_body 把当前会话绑定到宿主校验的 Pi 启动/会话 packet，
  然后启动 quota gated 循环。Goal、agent、registry 与变更能力都从该 packet 推导；
  与锁定权威不匹配的兼容性 echo 被拒绝。
- **`loopx_task_lease`** —— agent 可调用，显式封装现有 `task_lease_v0` CLI。它
  支持 `acquire`、`renew`、`transfer`、`release` 与只读 `inspect`。活跃 Pi 绑定向
  其提供 `goalId` 与当前 owner；模型不能替代任一经授权限。变更调用要求非空
  宿主校验的绑定 `agentId` 与宿主签发的 `task_lease_v0` 能力。类型化冲突与 CAS
  载荷（例如 `write_scope_conflict` 与 `lease_cas_mismatch`）作为工具结果保留。
- **Goal 循环** —— 每次 `agent_settled`，extension 为绑定 goal 探测
  `loopx quota should-run --runtime-profile generic_cli`。LoopX 决定是继续（心跳
  task_body 作为后续注入）、带调度器提示退避地等待（unchanged-poll 限制适用），
  还是在校验的终态 no-follow-up 处停止。探测失败带有限重试地 fail closed；
  extension 绝不自我声明关闭。
- **中止边界** —— Pi 运行期间按 Escape 会在 `agent_settled` 前持久化
  `autoResume: false`，取消任何挂起的退避定时器，并为进行中的 quota 探测设围栏。
  对持久会话，循环在 Pi 重启间保持暂停，直到 `/loopx resume` 或一次新的 goal
  激活显式重新武装它。

## 安装 / 卸载

```bash
loopx slash-commands --install --surface pi --pi-project .
loopx slash-commands --uninstall --surface pi --pi-project .
```

向项目安装两个 LoopX 管理的文件（项目信任后加载）：

- `.pi/extensions/loopx-goal.ts` —— 注册 `/loopx`、`loopx_goal_activate`、
  `loopx_task_lease` 与 `agent_settled` 循环接线的 extension 适配器。
- `.pi/extensions/pi-goal-loop-runtime.mjs` —— quota/wait/store 循环核心
  （不会被自动发现为 extension；适配器直接导入它）。

Pi 的 extension 加载器为 `typebox` 与 `@earendil-works/*` 包做别名，因此无需本地
`node_modules`。`--pi-project` 标志把安装器指向目标项目，使命令即使从另一目录
运行也正确；`agent-onboard --agent-type pi --project <path>` 自动输出解析后的
项目。

## 状态

绑定持久化在 `<project>/.loopx/pi/` 下（gitignored），按会话为键。用
`LOOPX_PI_STATE_DIR` 覆盖。用 `LOOPX_BIN` 调用 CLI 二进制。

没有会话文件（`pi --no-session`）的会话是瞬态的：适配器为每个 extension 实例使用
唯一的内存身份，绝不持久化其绑定，因此之后的 `--no-session` 运行不能继承上一次
运行的 goal，必须经 `loopx_goal_activate` 再次激活。

## 显式任务租约

租赁支持在工具调用处显式，而其变更能力为宿主绑定。用 `/loopx <goal text>` 启动
Pi 流程，并在激活时使用该启动 packet 的 `pi_session_authority.token`：

```text
loopx_goal_activate({
  activationToken: "<pi_session_authority.token>",
  objective: "<heartbeat_prompt.task_body>"
})
```

该权威锁定到此 Pi 会话。之后改变 goal、agent、registry 或能力集的激活返回类型化
权威失败，不会到达租赁 CLI。需要不同权威时，在新主机会话中重跑
`/loopx <goal text>`。

激活后，只带生命周期字段调用租赁工具：

```text
loopx_task_lease({
  action: "acquire",
  todoId: "todo_ab12cd34ef56",
  idempotencyKey: "pi-turn-42",
  writeScopes: ["loopx/**"],
  ttlSeconds: 2700
})
```

`renew`、`transfer` 与 `release` 要求租约的 `expectedVersion`；`transfer` 额外
接收 `newOwner` 与 `newIdempotencyKey`。`inspect` 只读，只需要活跃 goal 绑定。
Pi 不会自动 acquire、renew、transfer 或 release 租约。等价 CLI 回退是：

```bash
loopx --registry <registry> --format json task-lease acquire \
  --goal-id <goal> --todo-id <todo> --owner <agent> \
  --idempotency-key <turn-key> --write-scope 'loopx/**'
```

同一回退把 `acquire` 换成 `renew`、`transfer`、`release` 或 `inspect`；
`renew`/`transfer`/`release` 传 `--expected-version`，`transfer` 还传
`--new-owner` 与 `--new-idempotency-key`：

```bash
loopx --registry <registry> --format json task-lease renew \
  --goal-id <goal> --todo-id <todo> --owner <agent> \
  --idempotency-key <turn-key> --expected-version <version>
loopx --registry <registry> --format json task-lease inspect \
  --goal-id <goal> --todo-id <todo>
```

该工具只暴露公开安全类型化回执与冲突。它不授予活跃 LoopX goal 绑定之外的权威、
不绕过注册、不改变 quota/scheduler/todo 默认值，也不把 Pi transcript、凭据或会话
路径复制进 LoopX 状态。

## 边界

Extension 只读取 LoopX 公开安全状态，绝不复制原始 transcripts、凭据或本地会话
路径。延续由 LoopX quota 管辖；用户 prompt 与中止运行暂停自动恢复；`/loopx
resume` 或重新激活重新武装它。没有活跃 LoopX 状态或 owner 授权，不发生外部写入。

在 `session_shutdown`（会话切换、fork 或 reload）时，extension 实例被原子释放：
每个定时器被取消，之后返回的进行中 quota 探测在释放守卫处停止，因此旧会话绝不
能在 reload/会话替换边界之后注入后续或重新调度。
