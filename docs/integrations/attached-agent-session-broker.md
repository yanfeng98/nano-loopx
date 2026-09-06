# Attached Agent 会话中介


Attached Agent 会话中介把已在运行的宿主会话表示到 owner 本地的 LoopX Chat
存储中。它不会启动、恢复或替换 Agent runtime。

第一个桥接阶段支持:

- 精确的 `(Goal、注册 Agent、宿主界面、宿主会话)` 准入;
- 区分 LoopX `agent_id` 与执行器 `executor_endpoint_id` 两套身份;
- 为 Web 与 Connector 消息提供一份带 `origin` 的共享有序队列;
- 防重复的宿主 claim 与完成回执;
- 通过现有 Chat 的 Turn 与 Lark 回复路径回读响应;以及
- 不含内容的 Session 列表投影。

宿主会话必须已经具备一项精确的 `bind-agent-thread` 注册。使用 owner 本地的
不透明(opaque)值把它绑定到 Chat:

```bash
loopx worker-bridge attached-session-bind \
  --goal-id <goal-id> \
  --agent-id <registered-agent-id> \
  --host-surface <host-surface> \
  --host-session-id <opaque-host-session-id> \
  --executor-endpoint-id <executor-endpoint-id> \
  --execute
```

Web 或 Lark 的 `session_queue` 输入随后由现有宿主 claim:

```bash
loopx worker-bridge attached-session-claim \
  --session-id <loopx-chat-session-id> \
  --host-surface <host-surface> \
  --host-session-id <opaque-host-session-id> \
  --claim-id <stable-claim-id> \
  --wait-seconds 30 \
  --format json
```

`--wait-seconds` 把 claim 变成有界的宿主订阅。现有宿主 bridge 可以保持一个
claim 请求处于打开状态,一旦最早的排队消息可用就立即唤醒,而不是在紧循环中
轮询该命令。等待以 30 分钟为上限,并且从不启动或恢复 Agent runtime。超时返回
`claimed=false`;是否再次订阅由宿主决定。

把 Agent 响应写入一个至少包含 `message` 字段的 owner 本地 JSON 文件,然后完成
该精确 claim:

```bash
loopx worker-bridge attached-session-complete \
  --session-id <loopx-chat-session-id> \
  --turn-id <loopx-chat-turn-id> \
  --host-surface <host-surface> \
  --host-session-id <opaque-host-session-id> \
  --claim-id <stable-claim-id> \
  --completion-id <stable-completion-id> \
  --response-json <owner-local-response.json>
```

本阶段启用 `session_queue`、有界 claim 等待与回复回读。在宿主为已经运行的
Turn 暴露推送传输通道之前,`live_steering` 明确报告为不可用。LoopX 采用失败
即关闭(fail closed)的处理,而不是启动受管 runtime,或者把某个事件静默降级到
另一种入口模式。

带有活动宿主 claim 的 attached Session 不能关闭。先完成已 claim 的 Turn,再关闭
该 Session。这保留了宿主的写回权威,并防止已关闭的 Session 遗留一个正在运行的
Turn。

不透明宿主标识符、消息体与响应文件都保留在本地 runtime 存储中。公开 Session
投影只包含 LoopX Session id、Goal/Agent 绑定、执行器端点标签、宿主界面、能力
布尔值与生命周期状态。
