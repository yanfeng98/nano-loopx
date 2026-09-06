# Agent Turn Recall

`agent-turn-recall` 在可能没有新用户 prompt 时，为一次自主 agent turn 准备 memory
指引。它组合现有 LoopX surface，而不是引入另一个 memory store：

- quota 与 Todo 投影选出当前工作；
- Agent Turn Recall 构建有界的情境与 query；
- Reward Memory 强制 corpus、identity、authority、freshness 与 lifecycle；
- 配置的 context provider 执行只读 retrieval。

该 capability 默认关闭。Goal 必须显式地为 agent 开启一个 Reward Memory 实验，
并配置 `agent_workflow.turn_admission` surface。

## Turn 契约

`agent_turn_situation_v0` 包含 agent、goal、project、选中的 Todo、阶段、近期
outcome 与下一步意图。它记录 `user_prompt_included=false`；聊天文本不是后备输入。
这些 material 字段产生一个 `situation_fingerprint`。把该 fingerprint 与 host 提供
的 `turn_instance_id` 组合，得到 `turn_recall_id`。

这给出两种有用身份：

Turn id 是不透明 host 身份，不是时间戳。执行时用当前 UTC 观察时间计算 memory
freshness，同时保留原始 turn 身份用于验证与去重。

- Todo、target、阶段或意图变化会改变 situation fingerprint；
- 新 turn 会改变 recall id 并重新召回，即使情境本身没有变化。

同一 recall id 的重复执行可以复用一条被忽略的本地回执。回执只存储复现该 turn 指引
所需的紧凑私有上下文；它从不存储 provider payload、凭据或 query 文本。

## 使用

无 provider 访问的预览：

```bash
# 把已用于 turn 路由的精确 packet 持久化到被忽略的本地状态。
loopx quota should-run ... --format json > .local/turn-quota.json

loopx agent-turn-recall \

  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --turn-instance-id <iso-turn-id> \
  --quota-decision-json .local/turn-quota.json \
  --format json
```

在 quota/Todo 选择之后召回：

```bash
loopx agent-turn-recall \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --turn-instance-id <iso-turn-id> \
  --quota-decision-json .local/turn-quota.json \
  --execute \
  --format json
```

命令消费精确的 quota packet，而不是重建 status。这让 turn admission 保持有界，
并确保召回 query 使用 host 正在跟随的同一个选中 Todo 与交互状态。当 host 拥有安全
管道时，可用 `-` 从 stdin 读取 packet。

结果携带一个用于 agent 推理的私有 `context.guidance` 列表。它不是动作权威。
agent 仍必须遵守当前 interaction 契约、capability gates、写范围与 user gates。

召回相关性与应用适用性保持分开。召回指引是有条件的私有上下文；agent 在行动前必须
把它与精确 turn 情境和当前权威比较。

## Freshness 与失败

活跃的 Reward Memory 记录可携带 `lifecycle.expires_at`。召回会忽略到达该时间戳
或之后的记录。错误用户、peer、project、session 或 surface scope 在 provider 应用前
被拒绝。

provider 与应用失败会保留一个空的基础上下文，不创建 user gate，不花 quota，
也不向外部 sink 投递。因此 host 可以在 turn admission 时调用该 capability，
而不会让 memory 可用性成为安全自主推进的前提。
