# Decision Scope v0

状态：面向作用域化用户/controller 决策的公开安全协议契约。

用户 gate 不是全局布尔值。用户或 controller 决策应说明仍需要哪些权限，agent 动作应说明它依赖哪些权限。LoopX 随后可以决定所选动作是否被阻塞、安全回退是否可以继续，或投影本身是否需要修复。

本契约把 interaction catalog 的 Decision Scope Model 变成面向机器的 schema。它不自行实现运行时迁移；CLI/state/status/quota 消费者应把该形状作为迁移目标。

## 字段

### `decision_scope`

附加到用户 todo、operator gate 或 controller 决策。

| 字段 | 必需 | 含义 |
| --- | --- | --- |
| `kind` | 是 | `private_read`、`write_scope`、`resource`、`production`、`public_claim`、`direction` 或 `other`。 |
| `granularity` | 是 | `action`、`lane`、`goal`、`project` 或 `global`。 |
| `scope_key` | 是 | 指名被阻塞权限、路径、lane、资源或决策的公开安全键。 |
| `decision_id` | 否 | 决策已存在时的稳定 todo/gate/run id。 |
| `expires_at` | 否 | 临时权限的可选 ISO 时间戳。 |
| `reason_summary` | 否 | 在 status/UI 中显示的公开安全单行原因。 |

### `required_decision_scopes`

附加到 agent todo、下一动作、交接包或候选运行时动作。每项使用与 `decision_scope` 相同的 `kind`、`granularity` 与 `scope_key` 字段。

当一个未解决的决策作用域匹配或支配其必需作用域之一时，动作即被 gate 覆盖。v0 中支配刻意保持小：

- 相同 `kind` 与相同 `scope_key`；
- 相同 `kind`，且在同一 goal/project 边界上具有更宽的 `granularity`；
- 仅当 owner/controller 记录时才使用显式 `scope_key="*"`。

关系模糊时，status/quota 必须修复投影或询问用户/controller；它不得从散文推断权限。

### Markdown 元数据紧凑形式

Todo 元数据把决策作用域存储为紧凑公开安全 token，而非内联 JSON：

```md
<!-- loopx:todo decision_scope=direction:action:benchmark_target_choice -->
<!-- loopx:todo required_decision_scopes=direction:action:benchmark_target_choice -->
```

token 格式为 `kind:granularity:scope_key`。`decision_scope` 在用户 gate 上是单数；`required_decision_scopes` 在 agent todo 上可含逗号分隔列表。Status/quota 在评估 gate 覆盖前把这些 token 规范化为 `decision_scope_v0` 对象。

### `safety_class`

附加到 agent 工作候选与所选动作。

| 值 | 含义 |
| --- | --- |
| `read_only` | 可在不修改的状态下检查公开/本地允许状态。 |
| `local_write` | 在当前写边界内修改仓库或 LoopX 状态。 |
| `external_run` | 启动或推进外部计算、benchmark、CI 或托管运行时工作。 |
| `protected_write` | 写受保护状态、生产系统、私有物料、公开提交或外部权限界面。 |

`safety_class` 不授予权限。它让 LoopX 选择正确的 gate 比较与通知行为。

## 最小形状

```json
{
  "schema_version": "decision_scope_v0",
  "user_todo": {
    "todo_id": "todo_user_123",
    "decision_scope": {
      "kind": "private_read",
      "granularity": "project",
      "scope_key": "private_authority_source",
      "reason_summary": "owner must approve reading private source material"
    }
  },
  "agent_todo": {
    "todo_id": "todo_agent_123",
    "required_decision_scopes": [
      {
        "kind": "private_read",
        "granularity": "project",
        "scope_key": "private_authority_source"
      }
    ],
    "required_write_scopes": ["docs/**"],
    "safety_class": "read_only"
  },
  "scope_relation": {
    "state": "gate_covers_action",
    "fallback_available": true,
    "user_channel": "notify_concrete_gate",
    "agent_channel": "execute_independent_fallback"
  }
}
```

## Status 与 Quota 规则

Status 与 quota 应按此顺序读取决策作用域：

1. 显式 `decision_scope`、`required_decision_scopes` 与 `safety_class`；
2. 结构化 todo 字段，如 `task_class`、`required_write_scopes` 与动作种类；
3. 遗留标题/正文文本的兼容推断；
4. 无自信关系时进行投影修复。

Markdown 文本推断是 lint，不是 gate 真相。遗留 `Next Action` 正则可能检测可疑措辞并创建投影缺口警告，但它不得覆盖显式 `interaction_contract`、结构化 todo 字段或一个开放可运行 agent todo。

LLM 辅助解读只适合冷路径编写 helper 或修复建议。它可以建议结构化决策作用域，但不得在运行时决定投递 gate、花费策略、写权限或安全回退。

## 批准消费生命周期

`loopx todo complete` 只为显式关联的 `user_gate` 解析权限：

1. 已完成的 todo 具有 `task_class=user_gate`、规范化 `decision_scope` 与 `unblocks_todo_id=<target>`；
2. 目标是 agent todo，其 `required_decision_scopes` 包含该 gate 覆盖的作用域；
3. 完成只移除已覆盖要求并保留每个未覆盖作用域；
4. 转换返回带已解析与剩余作用域的公开安全 `todo_decision_scope_resolution_v0` 回执。

当目标 todo 已经是 `open` 时（例如批准后立即发布），该消费同样适用。已完成的 `user_action` 仍可为兼容使用精确 unblock 关系，但它不消费决策权限。`todo supersede` 记录替换或拒绝；它绝不暗示批准，因此绝不消费必需作用域。

## 常驻批准回执

有些 owner 决策是运营策略，而非单动作关卡。LoopX 只有在以下条件全部成立时才把该决策投影为 `standing_decision_authority_v0`：

- 来源项是已完成的 `user_gate`，而非 `user_action`；
- 它携带规范化 `decision_scope` 与显式 `decision_outcome=approve|reject|cancel`；
- 其 granularity 是 `goal`、`project` 或 `global`；
- 它具有显式 `blocks_agent` 或 `global_gate=true` 所有权；并且
- 它没有 `unblocks_todo_id`，后者仍是单动作消费路径。

精确作用域与 owner 身份的最新回执胜出。`approve` 激活它；后续 `reject` 或 `cancel` 撤销它。归档压缩把常驻回执保留在活动 User Todo 小节中，使 status 与 quota 不会在普通完成工作被归档时丢失权限。

常驻回执不使工作隐含特权。所选 agent todo 仍须声明覆盖的 `required_decision_scope`；quota 在评估必需作用域一致性前把回执过滤到当前 agent lane。更新的开放 gate 仍可通过普通 gate 路由阻塞精确工作。聊天散文、已完成的 `user_action` 项、推断意图与无作用域的多 agent 决策从不授予常驻权限。

## 迁移阶段

1. **仅契约：** 文档化本 schema，保持当前行为不变。
2. **状态编写：** 教 todo/gate 写路径接受并保留 `decision_scope` 与 `required_decision_scopes`。`safety_class` 仍是后续编写字段。
3. **投影：** 在 status、quota、评审包与 frontstage 本地运维模式中暴露这些字段。
4. **热路径：** 让 status/quota 优先使用结构化作用域关系，而非文本推断。
5. **Lint 回退：** 保持正则与可选 LLM 建议作为投影缺口修复 helper，而非运行时权限。

## 失败语义

- 遗留状态缺结构化字段：回退到兼容 lint 并发出投影缺口修复提示。
- 结构化字段冲突：以具体 blocker 失效关闭。
- 用户 todo 需要动作但无具体载荷：报告「具体 user todo 未投影，需修复 LoopX 状态投影」。
- 动作声称无 gate 但需要受保护写入：阻塞并修复作用域。
- 安全回退存在于 gate 作用域之外：通知具体 gate、运行独立回退、验证、writeback 并花费一次。

## 验收检查

一个决策作用域实现在以下条件下可接受：

1. 无需手改 Markdown 即可编写结构化字段；
2. status 与 quota 暴露计算出的作用域关系；
3. 显式字段优先于标题/正文正则推断；
4. 歧义作用域失效关闭而非猜测；
5. 安全回退仅在其必需作用域独立时继续；并且
6. 完成精确关联的用户 gate 只消费其覆盖的必需作用域，而接替它则一个都不消费；
7. 宽泛的已完成用户 gate 只有通过显式、agent 兼容的常驻回执才可复用，后续 reject/cancel 会撤销它；
8. 压缩完成 todos 不会抹除活动常驻权限；并且
9. 遗留正则/LLM 辅助保持为冷路径修复信号，而非运行时 gate 真相。
