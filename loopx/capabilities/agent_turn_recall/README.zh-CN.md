# Agent Turn Recall

> [English](README.md)

`agent-turn-recall` 在可能没有新用户 prompt 时,为一次自主 agent turn 准备
memory 指引。它组合现有 LoopX surface,而不是引入另一个 memory store:

- quota 与 Todo 投影选出当前工作;
- Agent Turn Recall 构建有界的情境与 query;
- Reward Memory 强制 corpus、identity、authority、freshness 与 lifecycle;
- 配置的 context provider 执行只读 retrieval。

该 capability 默认关闭。Goal 必须显式地为 agent 开启一个 Reward Memory
实验,并配置 `agent_workflow.turn_admission` surface。

## Turn 契约

`agent_turn_situation_v0` 包含 agent、goal、project、选中的 Todo、阶段、近期
outcome 与下一步意图。它记录 `user_prompt_included=false`;聊天文本不是后备输入。
这些 material 字段产生一个 `situation_fingerprint`。把该 fingerprint 与
host 提供的 `turn_instance_id` 组合,得到 `turn_recall_id`。

这给出两种有用身份:

- Todo、target、阶段或意图变化会改变 situation fingerprint;
- 新 turn 会改变 recall id 并重新召回,即使情境本身没有变化。

用同一个 recall id 重复执行可以复用一条被忽略的本地 receipt。Receipt 只保存
重建该 turn 指引所需的紧凑私有上下文;它从不保存 provider payload、凭据或
query 文本。

## 使用

不访问 provider 的预览:

```bash
# 把已用于 turn 路由的确切 packet 持久化到被忽略的本地 state。
loopx quota should-run ... --format json > .local/turn-quota.json

loopx agent-turn-recall \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --turn-instance-id <iso-turn-id> \
  --quota-decision-json .local/turn-quota.json \
  --format json
```

在 quota/Todo 选择之后召回:

```bash
loopx agent-turn-recall \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --turn-instance-id <iso-turn-id> \
  --quota-decision-json .local/turn-quota.json \
  --execute \
  --format json
```

该命令消费确切 quota packet,而不是重建 status。这让 turn admission 保持有界,
并确保召回 query 使用 host 正在遵循的同一个选中 Todo 与交互状态。当 host 拥有
安全 pipeline 时,可以用 `-` 从 stdin 读取 packet。

结果携带一条私有 `context.guidance` 列表供 agent 推理使用。它不是 action
authority。Agent 仍须遵守当前交互契约、capability gates、写作用域与用户 gate。

Retrieval 相关性与动作适用性仍然是两回事。召回指引是条件性私有上下文;agent
在行动前必须把它与确切 turn 情境及当前 authority 对比。

## Freshness 与失败

活跃 Reward Memory 记录可能带 `lifecycle.expires_at`。Retrieval 会忽略该时间戳
及之后的所有记录。错误的 user、peer、project、session 或 surface 作用域会在
provider 应用前被拒绝。

Provider 与应用失败会保留空的基础上下文,不创建用户 gate,不消耗 quota,也不
投递到外部 sink。因此 host 可以在 turn admission 时调用该 capability,而无需
把 memory 可用性变成安全自主推进的前提。
