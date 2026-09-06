# LoopX DeepSeek Harness（dsh）Goal 模式


头等宿主适配器，把 DeepSeek Harness 会话变成受 LoopX 管控的 Goal 循环。LoopX
保持权威（goal/todo 状态、quota、校验）；适配器只把一个受管控 Turn 翻译成一段
有界的 dsh 工作段，并把回复塑造成类型化结果。

## 入口

`deepseek-harness` 宿主表面（别名：`deepseek_harness`、`DeepSeek Harness`、
`dsh`）是一个外部循环驱动：

1. `loopx start-goal --guided --project . --host-surface deepseek-harness`
   在 todo writeback 后返回 host-loop 激活 packet。
2. 每次自动 tick 都从 `loopx quota should-run`（`--runtime-profile generic_cli`）
   开始，并在它说 stop 时停止。
3. 每个被批准的 tick 运行 `loopx turn run-once`，本适配器作为其 generic-cli
   宿主适配器命令。
4. 适配器从 stdin 读取一个 `loopx_turn_host_request_v0` JSON 对象，提取带签名的
   TurnEnvelope 权威，要求 dsh 执行有界的 `primary_action`，并向 stdout 输出
   恰好一个 `loopx_turn_result_v0` JSON 对象。
5. LoopX 在写任何状态或花费 quota 之前独立校验类型化结果。

## 运行适配器

```bash
python -m loopx.dsh_goal_mode \
  --cordis /path/to/cordis.yml \
  --model deepseek-v4-flash \
  --provider deepseek-official
```

历史启动器仍可用，且解析到同一实现：

```bash
python3 scripts/dsh_turn_host_adapter.py --cordis /path/to/cordis.yml
```

Flags：`--provider`、`--model`、`--max-tokens`、`--workspace`、
`--dsh-home`（`--session-root` 仍是兼容别名）、`--cordis`、`--runtime-bin`、
`--request-timeout-seconds` 与 `--dsh-runner`。runner 选项是显式测试 hook；
LoopX 不机器强制其使用范围，调用方本就拥有本地宿主执行权威。

## 进程内宿主（`--host dsh`）

`loopx turn run-once --host dsh` 在 CLI 进程内运行同一适配器，而不是通用
子进程。Provider 失败于是以类型化 `loopx_turn_host_failure_v0` 种类进入 Turn
日志，而不会经裸非零退出塌缩为 `unknown`，因此有界同 Turn 重试保持可用。两种
失败形态都被覆盖：抛出的传输异常，以及 SDK 的正常终态报告
（`RunResult.finish_reason == "error"`，携带结构化 `turn/end` 原因，完全没有
Python 异常）。

分类遵循 `loopx-turn-v0` 优先级：已知 provider `error.code` 优先于 HTTP 状态与
散文，未知非空 code fail closed 到 `unknown` 并封锁所有更低层级，HTTP 状态只在
没有更具体 code 时才决定，有界消息匹配只在没有结构信号时适用。同一层级内
不一致的信号收敛为 `unknown`。SDK 稳定的 `SERVER` code 覆盖 HTTP 5xx 响应，
并映射到可重试的 `provider_overloaded` 桶，即使中间序列化器省略了重复的 HTTP
状态。它的硬配额 `QUOTA` code 仍不可重试，而其显式可重试的 `EMPTY_RESPONSE`
code 映射到最接近的 LoopX 瞬态桶 `transport_lost`。

CLI flags：`--dsh-provider`、`--dsh-model`、`--dsh-max-tokens`、`--dsh-home`、
`--dsh-cordis`、`--dsh-runtime-bin` 与 `--dsh-runner`。针对当前 SDK 配置表面，
home 映射到 `dsh_home`，运行时二进制映射到 `dsh_bin`，cordis 文件作为一条
`patches` 条目挂载。Home 优先级是显式 CLI 值，然后 `DSH_HOME`，然后
`<workspace>/.local/.dsh-sessions`；LoopX 在 SDK 启动前创建选定的本地目录。
会话持久化仍属于选定的 dsh 组合，因此该模式不承诺跨 Turn 的 dsh 会话连续性。
Generic-cli 子进程保留其旧契约：无异常的终端 SDK 错误产生类型化 `wait` 结果，
而进程内宿主把同一结果变成重试感知的宿主失败。密封验证：
`python3 examples/loopx-turn-dsh-builtin-host-e2e-smoke.py`。

SDK 从最后一个 `turn/end.reason.kind` 推导 `finish_reason`；适配器拒绝矛盾或
格式错误（malformed）的 runner 结果为 `contract_rejected`。结果解析与塑形失败
使用同一类型化契约失败，而不是塌缩为 `unknown`。

## 依赖要求

- 可选依赖组 `loopx[deepseek-harness]`，当前锁定在已验证的
  `deepseek-harness-sdk==0.1.2a3` API，或经 `--dsh-runner` 提供兼容 runner。
- 真实运行时需要 dsh `cordis.yml` 以及任何 `DEEPSEEK_API_KEY` /
  `DEEPSEEK_BASE_URL` 设置。
- 设置 `DSH_MODEL` / `DSH_PROVIDER` 时作为默认值。未提供 CLI home 时，
  `DSH_HOME` 可覆盖 workspace 本地 home。

## 边界

显式 dsh 运行时 home（默认 `<workspace>/.local/.dsh-sessions`）保持本地化，
绝不进入公开 LoopX evidence。会话持久化由组合拥有，不是该路径名。适配器绝不
读取 goal/todo 状态、不根据 todo ids 构建 prompt、不写 LoopX 状态、不花费
quota、也不校验自己的工件。无类型化 JSON 候选的有效最终响应变成保守的
`wait`；无效 runner/结果形态是类型化 `contract_rejected` 宿主失败。两条路径都
不得花费 quota。

适配器推导稳定的 owner 本地会话 id，但 LoopX 尚未投影或校验 DSH Host Session
Binding。因此内置表面不声称具备受管 supervisor 恢复、外层唤醒/定时器所有权或跨
进程恢复保证。

完整 connector 走读见 `docs/integrations/deepseek-harness-connector.md`，
密封 smokes 见 `examples/dsh-turn-host-adapter-smoke.py` 与
`examples/loopx-turn-dsh-e2e-smoke.py`。安装可选 SDK 后，
`examples/loopx-turn-dsh-real-e2e-smoke.py` 分别以 `--host generic-cli` 与
`--host dsh` 各运行一次；两条路径都清除环境中的 DSH home 变量，并验证显式
SDK-home 接线。
