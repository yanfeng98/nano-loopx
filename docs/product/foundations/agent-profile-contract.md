# Agent 配置契约


`agent_profile_v1` 是对周期性 LoopX 对等方的可选注册表专属描述。它给提示生成与任务选择提供一个紧凑的能力与范围提示,而不分配持久排名。

每个注册身份拥有相同的运行时权威。Claim、任务租约、goal/写入边界、能力 gate、类型化延续策略与仓库策略决定对等方可做什么。配置不能让一个 agent 成为默认领导者、评审者、合并者或其他对等方工作的 owner。

## 分层

保持这些概念分离:

| 层 | 回答的问题 | 真相源 |
| --- | --- | --- |
| `agent_profile_v1` | 这个对等方通常对什么工作有用? | `coordination.agent_profiles` |
| `agent_member_v1` | 状态或评审包现在应展示什么? | 注册表、配额、todo 与运行历史 |
| `claimed_by` / `task_lease_v0` | 谁拥有这个精确 todo? | Active 状态 todo 元数据与租约记录 |
| 任务/仓库策略 | 此任务是否需要隔离、评审或合并 gate? | Todo 元数据、goal 边界与仓库策略 |

配置匹配是建议性的。它不得覆盖用户 gate、配额 state、必需能力、受保护写入范围、工作区护栏或其他对等方的认领或租约。

## 注册表形态

```json
{
  "coordination": {
    "agent_model": "peer_v1",
    "registered_agents": ["codex-runtime", "codex-product"],
    "agent_profiles": {
      "codex-runtime": {
        "schema_version": "agent_profile_v1",
        "agent_id": "codex-runtime",
        "profile_role": "runtime-validation",
        "scope_summary": "Runtime changes, integration checks, and release validation.",
        "default_task_classes": ["advancement_task"],
        "preferred_action_kinds": ["runtime_*", "validation_*"],
        "avoid_action_kinds": ["production_*"]
      },
      "codex-product": {
        "schema_version": "agent_profile_v1",
        "agent_id": "codex-product",
        "profile_role": "product-documentation",
        "scope_summary": "Product ergonomics, examples, documentation, and focused smokes.",
        "default_task_classes": ["advancement_task", "continuous_monitor"],
        "preferred_action_kinds": ["product_*", "docs_*", "smoke_*"],
        "avoid_action_kinds": ["production_*"]
      }
    }
  }
}
```

配置通过与其他 goal 协调设置相同的校验注册表路径写入:

```bash
loopx configure-goal --goal-id <goal-id> \
  --agent-profile-json '{"schema_version":"agent_profile_v1","agent_id":"codex-runtime","profile_role":"runtime-validation","preferred_action_kinds":["runtime_*"]}' \
  --execute
```

用 `--clear-agent-profile <agent-id>` 移除一个配置。命令在写入注册表之前拒绝未注册对等方、未知字段、层级角色、无效任务类别与不安全 action-kind glob。

`profile_role` 是人类可读的功能标签。它是建议性的,不得使用 `primary-agent` 或 `side-agent` 等层级标签。

不要把这些放进配置:

- 父级、领导者或默认评审者身份;
- 身份级合并权限;
- 身份级工作区隔离规则;
- 隐式交接目标。

这些规则随任务与仓库而异。把它们编码进身份会重建持久层级,并让同一对等方在换任务时行为错误。

## 提示生成

通用路径自动解析已注册配置:

```bash
loopx heartbeat-prompt --thin \
  --goal-id loopx-meta \
  --agent-id codex-product
```

提示可以包含配置的范围摘要、任务类别与动作偏好。它仍会告诉对等方认领或租约工作、遵循当前任务策略,并在交付前运行 `quota should-run`。`--agent-scope` 仍是用于分离校验或一次性自动化的显式临时覆盖。

如果已配置配置,但请求的已注册对等方没有配置,提示生成可以只用对等方身份继续。缺失建议元数据不是权威失败。

## 选择规则

配置支撑的选择可以:

1. 优先当前 agent 的认领,然后未认领的可执行 todo;
2. 把匹配的任务类别或动作类型排得更高;
3. 当有另一个可执行对等方或未认领任务可用时,避免不匹配的动作类型;
4. 当只剩其他对等方认领时,投影一个具体的重新分配请求。

偏好排名在现有认领桶内应用。当前对等方认领仍领先于未认领 todo,即使未认领 todo 是更好的配置匹配。显式的 active-next todo 也保持现有路由。没有有效配置时,候选排序不变。

选择随后必须执行能力 gate、任务租约、工作区护栏、写入范围与延续策略。配置偏好从不转移认领,也从不把其他对等方的工作变成可执行候选。

## 工作区、评审与完成

工作区隔离从所选任务与仓库策略派生。一个写仓库的任务可能需要对任何对等方使用独立 worktree;只读与仅 monitor 的任务不因身份标签而需要隔离。

完成也是任务范围内的:

- 直接验证完成使用仓库的正常合并策略;
- `independent_handoff` 创建非阻碍后继;
- `same_agent_non_delivery` 保持同一对等方延续。

评审是普通独立交接上的一个 `action_kind`。没有配置提供隐式评审者;`excluded_agents` 仅在任务需要执行者分离时可用。

## 投影

`agent_member_v1` 是只读观察,不是权威记录:

```json
{
  "schema_version": "agent_member_v1",
  "agent_id": "codex-product",
  "agent_model": "peer_v1",
  "profile_role": "product-documentation",
  "profile_role_is_advisory": true,
  "scope_summary": "Product ergonomics, examples, documentation, and focused smokes.",
  "current_claims": ["todo_abc123"],
  "handoff_assignment_status": "task_policy_selected"
}
```

Dashboard 可以渲染此投影。写入仍通过 LoopX todo、gate、租约、配额、reward 与 refresh 命令。

## 迁移

v0.1 到对等方迁移把 `agent_profile_v0` 视为遗留输入。在 host 更新其已安装自动化并确认稳定迁移 id 后,LoopX 原子地:

1. 移除 goal 级领导与默认交接字段;
2. 把 `registered_agents` 规范化到对等方 id;
3. 把配置升级为 `agent_profile_v1`;
4. 移除层级角色加身份级工作区、评审与交接策略;
5. 记录 `completed_migrations.peer_agent_runtime_v1`。

完成命令是幂等的。一旦标记写入,配额不再要求该迁移。
