# LoopX Worker Bridge 安装契约

> [English](worker-bridge-install-contract.md)

worker bridge 是一种 runner 中立的方式,让 LoopX CLI 在隔离执行器中可用。它声明
来源/runtime 挂载、Python 预检、紧凑计数器 trace 与可选的活跃用户更新通道。它
不拥有 benchmark 结果 schema、评分、上传或提交。

在本地预览该契约:

```bash
loopx worker-bridge contract --format json
```

默认载荷使用公开占位符,不授予任何执行权威:

```text
schema_version=loopx_worker_bridge_install_contract_v0
install_mode=source_mount_read_only_pythonpath
loopx_command_prefix=PYTHONPATH='<loopx-project-root>' python3 -m loopx.cli
loopx_counter_trace_json=/logs/agent/loopx-counter-trace.jsonl
```

执行器可以把返回的 `mounts` 与 `agent_kwargs` 翻译成自己的容器、虚拟环境或
sidecar 配置。私有启动器可以替换为真实宿主路径,但这些路径、凭证、转录与原始
工具输出绝不能进入公开状态或证据 artifact。

对活跃用户协作 lane,请请求一个可写 feed 挂载,并使用返回的
`active_user_intervention_channel_contract` 所记录的拉取式命令。该通道不暴露隐藏
测试、预期解答、评测器答案、凭证或私有项目材料,也不授权评分或排行榜声明。

同一个 `worker-bridge` 界面还承载 provider 中立的
[`attached Agent 会话中介`](attached-agent-session-broker.md)。该中介绑定一个
已在运行的宿主会话,让该确切宿主 claim 并完成排队的 Web 或 Connector 消息。它
从不启动替代 runtime。宿主会话 id、消息体与响应文件都保持在 owner 本地。

已退役的 benchmark 结果/写回层保留在
[`deprecate/benchmark-legacy/`](https://github.com/huangruiteng/loopx/blob/main/deprecate/benchmark-legacy/README.md)
下,供源码考古之用。新的 benchmark 工作应从
[`benchmark/`](https://github.com/huangruiteng/loopx/blob/main/benchmark/README.md)
研究工作区开始,并让 runner 与 verifier 语义保持 benchmark 原生。

## 验证

```bash
python3 examples/cli-worker-bridge-command-modularization-smoke.py
python3 examples/worker-bridge-active-user-feed-smoke.py
```
