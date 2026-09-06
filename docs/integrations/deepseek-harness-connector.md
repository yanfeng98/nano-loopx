# DeepSeek Harness 连接器


状态:公开安全 v0 连接器,用于把 DeepSeek Harness(`dsh`)用作 LoopX 之后的
有界 agent 执行宿主。

DeepSeek Harness 是 DeepSeek AI 的开源 agent harness。LoopX 不替代 dsh 的模型
循环、工具、沙箱或会话日志。相反,连接器让 LoopX 通过现有 LoopX Turn 协议一次
治理一段由 dsh 支撑的工作:

```text
LoopX quota should-run
    -> loopx turn run-once
    -> loopx.dsh_goal_mode adapter (python -m loopx.dsh_goal_mode)
    -> DeepSeek Harness Python SDK / dsh runtime
    -> typed loopx_turn_result_v0
    -> independent validator
    -> LoopX writeback + quota spend
```

## 该连接器带来什么

- 一个轻量适配器,现已成为 `loopx/dsh_goal_mode/` 下的一等 goal-mode 子包
  (用 `python -m loopx.dsh_goal_mode` 运行;历史启动器
  `scripts/dsh_turn_host_adapter.py` 仍可用),它把
  `loopx_turn_host_request_v0` 翻译成一个有界的 dsh 会话提示,并把模型的最终
  JSON 结果解析回 `loopx_turn_result_v0`。
- 在 LoopX 接入流程中新增 `deepseek-harness` agent 类型,让用户可以请求确切
  宿主,而不是通用的 `other-agent`。
- 为经过验证的 `deepseek-harness-sdk==0.1.2a3` Python 客户端提供可选依赖
  `loopx[deepseek-harness]`。

## 安装

安装 LoopX 的可选 DeepSeek Harness extras:

```bash
python -m pip install 'loopx[deepseek-harness]'
```

DeepSeek Harness SDK 会启动随附的 `dsh-jsonrpc-agent` runtime。它使用显式配置的
适配器参数以及常规 provider 环境变量:

```text
DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL
DSH_HOME
```

适配器按以下顺序解析其 SDK home:显式 `--dsh-home`,然后是 `DSH_HOME`,再是
`<workspace>/.local/.dsh-sessions`。它把该路径作为 SDK 的 `dsh_home` 字段传入;
SDK 不会隐式选择 `~/.dsh`。

当默认的随附组合(composition)不合适时,请准备一个 dsh `cordis.yml`。关于
runtime 选择与配置,请参阅
[DeepSeek Harness Python SDK 参考](https://github.com/deepseek-ai/deepseek-harness/blob/master/python/sdk/README.md)。

## 接入

```bash
loopx doctor --agent-type deepseek-harness

loopx agent-onboard \
  --agent-type deepseek-harness \
  --project . \
  --goal-id <goal-id> \
  --agent-id deepseek-worker \
  --available-capability shell
```

`deepseek-harness` 映射到通用 CLI agent 循环,并在配额/心跳命令中使用
`--runtime-profile generic_cli`。

## 运行一轮受管 Turn

```bash
loopx turn run-once \
  --goal-id <goal-id> \
  --agent-id deepseek-worker \
  --host generic-cli \
  --execution-mode isolated-headless \
  --project "$PWD" \
  --host-adapter-command-json '["python3", "-m", "loopx.dsh_goal_mode", "--dsh-home", "/path/to/dsh-home", "--cordis", "/path/to/cordis.yml", "--model", "deepseek-v4-flash"]' \
  --validation-command-json '["python3", "/path/to/verify-postcondition.py"]' \
  --execute
```

适配器默认使用 `<workspace>/.local/.dsh-sessions/` 作为其工作区本地 SDK home。
可用 `--dsh-home <path>` 覆盖;历史拼写 `--session-root` 仍是适配器命令的兼容
别名。会话持久化本身由所选 dsh 组合拥有,并不因 home 目录名而隐含。

## 在进程内运行一轮受管 Turn(`--host dsh`)

内置宿主在 CLI 进程内运行同一个适配器:

```bash
loopx turn run-once \
  --goal-id <goal-id> \
  --agent-id deepseek-worker \
  --host dsh \
  --execution-mode isolated-headless \
  --project "$PWD" \
  --dsh-home /path/to/dsh-home \
  --dsh-cordis /path/to/cordis.yml \
  --dsh-model deepseek-v4-flash \
  --validation-command-json '["python3", "/path/to/verify-postcondition.py"]' \
  --execute
```

与子进程模式不同,provider 失败会以类型化 `loopx_turn_host_failure_v0` 种类进入
Turn 日志(包括 SDK 无异常的 `RunResult.finish_reason == "error"` 终止报告),
因此同 Turn 有界重试仍然可用。该模式不承诺跨 Turn 的 dsh 会话连续性,也不承诺
外部 wake/定时器。关于 home 与分类优先级,以及密闭(hermetic)验证 smoke
(`examples/loopx-turn-dsh-builtin-host-e2e-smoke.py`),请参阅适配器 README。

## 边界

- LoopX 保留持久 goal、todo、claim、gate、配额、证据与 scheduler 权威。
- dsh 拥有模型调用、工具、沙箱化与原始会话日志。
- 适配器不得把原始转录、dsh JSONL 会话、凭证、本地绝对路径或无界工具输出发布
  进 LoopX 状态。
- `DeepSeekHarness.run()` 返回的是候选结果;它不是完成的证明。LoopX 写回之前
  需要独立验证器。
- dsh Python SDK 是可选依赖。核心 LoopX 保持无 runtime 依赖。
- 适配器派生一个 owner 本地会话 id,但 LoopX 不投影或验证 DSH Host Session
  Binding。因此该界面不声称受管监督器或跨进程恢复保证。

## 密闭验证

仓库包含四条验证路径。前三条不需要 DeepSeek Harness SDK 或真实 dsh runtime:

```bash
python3 examples/dsh-turn-host-adapter-smoke.py
python3 examples/loopx-turn-dsh-e2e-smoke.py
python3 examples/loopx-turn-dsh-builtin-host-e2e-smoke.py
```

第一条守护适配器翻译与结果成形。第二条驱动完整的
`loopx turn run-once -> adapter -> fake dsh -> validator -> writeback ->
quota spend -> idempotent replay` 链路。第三条验证内置宿主的成功路径,外加三次
有界 provider 容量尝试、在不产生第四次 Host 调用的情况下耗尽重试预算、零失败
消耗/写回,以及 provider 散文不持久化。

第四条使用真实 `deepseek-harness-sdk` 与随附的 dsh JSON-RPC runtime。它通过
提供本地 mock 的 OpenAI 兼容 SSE 端点,仍然避免真实模型调用,因此是密闭的,
也不需要 `DEEPSEEK_API_KEY`:

```bash
python3 examples/loopx-turn-dsh-real-e2e-smoke.py --host generic-cli
python3 examples/loopx-turn-dsh-real-e2e-smoke.py --host dsh
```

real-dsh smoke 会清除环境中的 DSH home 变量,并验证:两条宿主路径都能提供显式
SDK home、启动实际 dsh runtime、通过真实 JSON-RPC agent 循环运行一轮有界 Turn、
解析类型化 JSON 最终消息,并完成 LoopX 验证/写回/配额消耗。

## 相关契约

- [DeepSeek Harness 控制面适配器](deepseek-harness-control-plane-adapter.md)
- [Runtime 连接器目录](runtime-connector-catalog.md)
- [LoopX Turn v0](../reference/protocols/loopx-turn-v0.md)
- [宿主集成面 v0](../reference/protocols/host-integration-surface-v0.md)
- [在 Agent Runner 中嵌入 LoopX](../guides/custom-agent-runner-integration.md)
