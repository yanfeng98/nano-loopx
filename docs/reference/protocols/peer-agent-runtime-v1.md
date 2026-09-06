# 对等 Agent 运行时 v1

## 目的

`peer_v1` 把持久化的 agent 等级从 LoopX 运行时决策中移除。已注册 agent 拥有平等的身份权限。工作所有权来自 todo claim、任务 lease、显式继续策略与有界的任务域赋值。

功能 profile 仍可描述能力或偏好 scope。它们不得授予某个身份对其他每个身份的隐式评审、合并、路由或重规划权限。

## 规范身份

一个对等身份包含：

```json
{
  "schema_version": "peer_agent_identity_v1",
  "agent_model": "peer_v1",
  "agent_id": "codex-alpha",
  "registered": true,
  "registered_agents": ["codex-alpha", "codex-beta"]
}
```

规范对等输出不得包含 `primary_agent`、`handoff_agent` 或携带等级的 `role` 字段，包括空值占位符。

## 工作所有权

1. 显式 todo `claimed_by` 或活动任务 lease 胜出。
2. 未认领 todo 必须在投递前被认领或 lease。
3. 显式 agent 作用域的重规划义务归属该 agent。
4. 无作用域的重规划义务通过对排序后的已注册 agent 集合哈希规范工作键，分配给恰好一个已注册对等方。
5. 注册顺序必须不改变确定性赋值。

确定性赋值是对单一工作项的协调。它不改变身份权限，不得作为 agent 等级持久化。

## 完成与评审

继续行为是任务策略：

- `independent_handoff`：除非选定显式对等方，否则留下未认领的 successor；
- `same_agent_non_delivery`：把 successor 留在完成策略对等方。

评审是一种 `action_kind`，不是继续类型。使用普通 `independent_handoff`；当任务必须保持开放给除作者以外的任何合格对等方时，把作者加入 `excluded_agents`。显式 `claimed_by` 绝不能指名被排除的对等方。

仓库合并权限仍由仓库的维护者策略治理。对等身份本身既不授予也不移除自合并权限。规范完成标志是 `--self-merged`。

## 工作区隔离

每个对等方都受同一工作区规则约束。`agent_workspace_guard_v1` 在所选 todo 声明写 scope、使用写类别 action kind，或 goal 策略明确要求隔离时，要求独立的 git worktree。只读观察与监控工作不因身份单独触发该 guard。

对于属于非 goal 仓库的任务，agent todo 可以声明 `task_repository` 作为免凭据规范身份，例如 `git:github.com/owner/repo`。随后 guard 要求一个 origin 与该身份匹配的 linked worktree。该字段只选择用于工作区隔离的仓库：它不是 agent scope、写 scope、权限授予，也不是 claim/lease 与 goal 边界检查的替代。无此字段时，goal 仓库保持权威。

## 任务域协调

当有界多 agent 编排被启用时，LoopX 哈希规范任务包并选择一个临时协调者。得到的 `task_orchestration_contract_v1`：

- 作用域限定为该任务包；
- 激活或恢复合格对等 lane；
- 只把已接受包证据的 writeback 责任交给协调者；
- 不使协调者成为持久化 leader。

## 迁移

对于旧 registry，先让 `quota should-run` 或 `upgrade-plan` 投影稳定迁移 id 与逐对等 heartbeat 命令。用该迁移 id 幂等地更新每个已安装 host 自动化，然后确认已完成的 host 更新：

```bash
loopx configure-goal \
  --goal-id <goal-id> \
  --ack-automation-prompt-migration <migration-id> \
  --execute
```

该确认验证当前迁移 id、创建带时间戳的 registry 备份、原子移除层级权限字段，并记录已完成的迁移。重复同一确认是 no-op，后续配额检查不再投影该已完成迁移。

完成标记对该迁移版本是最终的。如果过期的 v0.1 写者后来重新引入层级字段，对等运行时忽略该字段，不再用同一自动化迁移唤醒用户。Upgrade 诊断仍可暴露过期输入以供清理。

实现边界：遗留字段名、检测、profile 转换与完成簿记都位于隔离的 `legacy_migration` 模块中。`runtime_model` 只包含活动的 `peer_v1` 模型，不对 primary/side 身份概念分支。

回滚恢复返回的 `backup_path`，然后从该恢复的 registry 重新生成已安装的 host loop。Registry 恢复与 host-loop 重新生成是一次运维回滚。

## v0.2 切换关卡

对等运行时可以先在内部落地，早于公开 v0.2 切换，使其迁移可针对 v0.1 状态验证。v0.2 在以下条件满足前不可发布：

- 规范 fixture 与文档使用 `peer_v1`；
- heartbeat、quota、status、completion、workspace 与 orchestration 运行时不再执行层级分支；
- 旧层级字段只被迁移/历史读取器接受；
- 对等 agent canary profile 与完整 smoke 套件通过。

可选 supervisor 是此对等模型上的覆盖层，而非替代品。参见 [对等 Supervisor v0](peer-supervisor-v0.md)。
