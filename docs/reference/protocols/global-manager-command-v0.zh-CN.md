# global_manager_command_v0
> [English](global-manager-command-v0.md)

`global_manager_command_v0` 是 `/loopx-global-summary`、`/loopx-global-gates`、`/loopx-global-todos` 与 `/loopx-global-risks` 等操作员命令的读取优先协议。

产品目标是让用户作为经理跨越长程 agent 工作行动：询问最近一天进展、看到被阻塞决策、对比 agent lanes，并选择下一安全动作，而无需阅读每条线程。

本协议还不是通用聊天命令路由器。它定义 Codex hosts、CLI 包装器或 dashboard 命令面板的请求、允许来源、响应形状、隐私边界与动作阶梯。四个已实现的 global-manager CLI 包装器是：`loopx global-summary`（宽泛紧凑 `/loopx-global-summary` 摘要）、`loopx global-gates`（聚焦当前状态 gate 收件箱）、`loopx global-todos`（聚焦当前状态工作收件箱）与 `loopx global-risks`（聚焦当前状态风险收件箱）。

## 命令集

推荐首批命令：

| 命令 | 用户意图 | 默认来源窗口 |
| --- | --- | --- |
| `/loopx-global-summary <time range>` | 显示进展、已完成工作、活动 lanes 与下一决策。 | 24 小时 |
| `/loopx-global-gates` | 显示开放的用户/controller gates 及各自阻塞内容。 | 当前状态 |
| `/loopx-global-todos` | 显示顶层可运行、被阻塞、可推迟与评审 todos。 | 当前状态 |
| `/loopx-global-risks` | 显示过期 runs、公开/私有边界警告、失败检查与回滚候选。 | 24 小时 |
| `/loopx-pr-review` | 逐个走读当前项目或显式仓库的开放与已合并 GitHub PR，带动机、范围、检查、风险与评审提示。 | 当前开放 + 已合并 PR，可选 `--since` 限制 |
| `/loop-goal-summary <goal id>` | 下钻一个 goal，而不扫描无关项目。 | 24 小时 |

只有 `/loop-goal-summary` 在本协议下保持仅 host；`/loopx-global-risks` 使用规范 `loopx global-risks` CLI 包装器。

命令默认只读。它们可以建议后续动作，但不批准 gates、不提升建议 todos、不花费配额、不合并 PR、不暂停自动化、不运行破坏性操作。

迁移期间可以接受遗留 `/loop-global-*` 形式为别名，但 host 应把命令包与用户可见帮助规范化为 `/loopx-global-*` 名称。这些是 host/slash 别名，不是 CLI 命令名：未知命令与遗留 CLI 别名以帮助失效关闭，而不是回退到更宽 status 或 summary 转储。

| 遗留别名 | 规范命令 |
| --- | --- |
| `/loop-global-summary` | `/loopx-global-summary` |
| `/loop-global-gates` | `/loopx-global-gates` |
| `/loop-global-todos` | `/loopx-global-todos` |
| `/loop-global-risks` | `/loopx-global-risks` |

相关项目局部命令：`/loopx <goal text>` 由 [loopx_goal_command_v0](loopx-goal-command-v0.md) 覆盖。它不是 global manager 命令：它启动一个项目 goal、规划排序 todos、按序写入，然后进入配额关卡的自动化流程。

相关仓库评审命令：`/loopx-pr-review` 由 [pr_review_command_v0](../../../loopx/capabilities/pr_review_queue/README.md) 覆盖。它只读，帮助人类评审调用方当前项目或显式 `--repo owner/repo` 目标的开放与已合并 PR；它不批准、不评论、不合并、不花费配额。

## 请求形状

```json
{
  "schema_version": "global_manager_command_request_v0",
  "command": "/loopx-global-summary",
  "legacy_aliases": ["/loop-global-summary"],
  "time_range": "24h",
  "goal_filter": ["loopx-meta"],
  "agent_filter": ["codex-main-control", "codex-side-bypass"],
  "include": ["progress", "gates", "todos", "risks", "next_actions"],
  "privacy_mode": "public_safe_summary",
  "dry_run": true
}
```

请求规则：

- `privacy_mode` 默认为 `public_safe_summary`。
- `goal_filter` 与 `agent_filter` 收窄读取；省略过滤器指本地控制面可见的全部已注册 goals 或 agents。
- 对于 `loopx global-gates`，`--agent-id` 排除所选 agent 未注册的 goals；不可用的逐 goal quota 投影不能替代 agent 过滤。
- 对于 `loopx global-todos`，`--agent-id` 转发进每个逐 goal quota 读取，并在全局限制前应用。成功 quota 包必须确认精确 `agent_identity.agent_id` 匹配；默认 lane 包或失败 quota 读取不能满足过滤器。
- 对于 `loopx global-risks`，`--agent-id` 使用精确紧凑历史 goal 成员。全局风险保持可见，任何未解决的候选 goal 失效关闭，而不是被静默排除。
- `dry_run=true` 是默认，因为首个实现应是报告，而非执行器。
- 未知命令必须以帮助包失效关闭，而非宽泛状态转储。

## 来源读取

实现只可读取紧凑 LoopX 控制面界面：

- 全局 registry 与项目局部 registry 条目；
- `loopx status` / status JSON；
- `loopx quota plan` 与 `quota should-run` 摘要；
- active-state todo 投影；
- run 历史摘要；
- rollout 事件日志摘要；
- 显式 goal 下钻的评审包。

`loopx global-gates` 读取紧凑状态投影。Status 内部消费紧凑 run 历史状态构建其当前关注队列，但 gates 构建器不发出第二次历史读取，也不在响应中暴露历史项。

`loopx global-todos` 恰好读取一次 status，检查一个有界唯一关注队列 goal 集，并为每个检查过的 goal 构建至多一个权威 quota 包。Status 可以消费紧凑 run 历史投影，但 todos 构建器不发出第二次历史或存储读取。它只从所选 lane 与结构化 quota/todo 投影推导 todo 候选；不解析 active-state 散文。

`loopx global-risks` 恰好读取一次 status。它接受结构化契约诊断、全局 registry 发现、关注队列过期 run 警告，且只对显式 agent 过滤接受紧凑 run 历史协调。它不执行 quota 扇出，也不用展示受限 `agent_management_projection` 决定 goal 成员。

它们不得包含原始 transcript、原始 benchmark 日志、原始 connector 载荷、凭据、本地绝对路径或私有源正文。

## 响应形状

`global_manager_command_response_v0`：

```json
{
  "schema_version": "global_manager_command_response_v0",
  "request": {
    "command": "/loopx-global-summary",
    "time_range": "24h"
  },
  "generated_at": "2026-06-24T00:00:00Z",
  "summary": {
    "headline": "Three active goals advanced; one user decision is open.",
    "progress_count": 3,
    "open_gate_count": 1,
    "runnable_todo_count": 4,
    "risk_count": 2
  },
  "lanes": [
    {
      "goal_id": "loopx-meta",
      "agent_id": "codex-product-capability",
      "status": "eligible",
      "top_todo_id": "todo_example",
      "last_event_id": "event_example",
      "next_safe_action": "Review and merge the public-safe protocol PR."
    }
  ],
  "gates": [
    {
      "gate_id": "gate_example",
      "owner": "user",
      "blocks": ["todo_example"],
      "question": "Approve promoting the candidate todo?",
      "next_safe_action": "Wait for explicit approval."
    }
  ],
  "risks": [
    {
      "kind": "public_boundary_warning",
      "severity": "high",
      "evidence_refs": ["check_public_boundary"],
      "next_safe_action": "Run the public/private boundary scan before merge."
    }
  ],
  "actions": [
    {
      "action_id": "act_review_pr",
      "kind": "review",
      "requires_user_approval": false,
      "requires_executor_separation": true,
      "target_agent_id": "codex-reviewer",
      "preview": "Assign protocol review to the selected registered peer."
    }
  ],
  "omissions": [
    "Raw logs and private connector payloads were intentionally omitted."
  ]
}
```

聚焦 gate 响应遵循这些关系规则：

- 正式用户 gate 来自交互契约或正式开放用户 gate todo，而非仅全部开放用户 todos 的计数；
- `blocks` 存在时使用 gate todo 的 `unblocks_todo_id`，然后已验证决策作用域关系，否则回退到 goal scope，而非从所选可运行 todo 猜测；
- `waiting_on=user_or_controller` 是路由元数据，不是新 gate-owner 枚举；gate owners 继续使用协议的用户、controller、已注册 agent 或外部系统 owner 类别。

### 聚焦全局 Todos 响应

`loopx global-todos` 保留 `global_manager_command_response_v0`。扁平 `todos` 列表中每个保留项及其对应就绪与评审组使用这种紧凑公开安全形状：

```json
{
  "todo_id": "todo-123",
  "goal_id": "goal-456",
  "role": "agent",
  "status": "open",
  "priority": "P1",
  "title": "Review the quota projection",
  "claimed_by": "codex-reviewer",
  "action_kind": "review_pr",
  "readiness": "runnable",
  "work_kind": "review",
  "next_safe_action": "Continue the selected quota-authorized todo."
}
```

聚焦响应包含：

- `/loopx-global-todos`、其 `/loop-global-todos` slash 别名与 `loopx global-todos` 的规范请求元数据；
- 唯一 `(goal_id, todo_id)` 行的扁平 `todos` 列表；
- 从保留扁平列表派生的 `groups.runnable`、`groups.deferred_ready`、`groups.blocked` 与 `groups.review`；
- 全局结果限制前的 `summary.matched_todo_count` 与之后的 `summary.returned_todo_count`；
- 全匹配 `runnable_count`、`deferred_ready_count`、`blocked_count` 与 `review_count`，加结果限制移除行时的 `truncated`；
- 更早有界 goal 扫描的 `goal_scan_limit` 与 `goal_scan_truncated`，这与结果截断不同；以及
- 有界、脱敏 `source_warnings`，而 `source_warning_count` 报告该警告列表封顶前观察到的所有警告。

就绪与工作种类正交。只有就绪分类项进入响应：`runnable` 要求 quota 所选 todo 与 `normal_delivery_allowed=true`；`blocked` 要求显式阻塞投影或正式验证的 todo 级 gate 关系；`deferred_ready` 要求结构化恢复就绪。`work_kind=review` 要求 `action_kind` 中含精确下划线分隔 `review` 或 `reviewer` token，绝不用标题或文本推断。因此评审计数与就绪计数重叠；不要把它们加到就绪计数上求总数。

投影不一致时，命令失效关闭到优先级 `blocked`、然后 `deferred_ready`、然后 `runnable`，并发出脱敏来源警告。它绝不把 goal 级 gate 回退映射到猜测 todo ID。Agent 过滤、规范化、分类与去重都在全局限制前发生。

全局与逐 goal 失败有不同信封。全局 status 来源不健康时，命令返回带公开安全错误的 `ok=false` 并非零退出；它不得看起来像一个成功的空收件箱。某 goal 的 quota 读取抛出或返回 `ok=false` 时，命令跳过该不可验证 goal、记录一条有界脱敏警告，并保留健康 goal 的结果。

### 聚焦全局风险响应

`loopx global-risks` 保留 `global_manager_command_response_v0`，且成功报告不健康状态时返回 `ok=true`。特别是 `status.ok=false` 仍是可报告风险数据，而 `summary.source_health_ok` 把来源健康与命令成功分开保存。成功与错误响应都携带顶层 `generated_at`。

规范请求使用 `/loopx-global-risks`、`/loop-global-risks` slash 别名、`loopx global-risks`、规范正 `Nh` 或 `Nd` `time_range`、四个 risk includes、`privacy_mode=public_safe_summary` 与 `dry_run=true`。每个保留行使用这种出现感知公开安全形状：

```json
{
  "goal_id": "goal-123",
  "category": "boundary_warning",
  "kind": "public_boundary_violation",
  "severity": "high",
  "summary": "A public boundary check failed.",
  "occurrence_id": "f42d9c9f6d497b35",
  "occurrence_count": 1,
  "evidence_refs": [
    "status.contract.error_diagnostics:public_boundary_violation:f42d9c9f6d497b35"
  ],
  "next_safe_action": "Inspect and remove the boundary violation before delivery.",
  "requires_user_approval": false
}
```

响应包含：

- 规范化请求与顶层生成时间；
- `summary.source_health_ok`、全匹配与返回的风险与出现计数、类别计数、有界读取与截断事实、警告计数；
- 权威扁平 `risks` 列表；
- 划分扁平 `risks` 列表的 `groups.stale_runs`、`groups.boundary_warnings` 与 `groups.failing_checks`；
- 重叠的 `groups.rollback_candidates` 侧面（当前空），加 `summary.rollback_candidates_overlap_risks=false`；
- 封顶 `source_warnings` 列表、其未封顶计数与 `source_warnings_truncated`；以及
- 结构化省略与标准公开安全边界。

#### 结构化风险来源与分类

| 输出类别 | 接受来源 | 规则 |
| --- | --- | --- |
| `stale_run` | `attention_queue.items[].stale_latest_run_warning` | 要求精确 `kind=stale_latest_run_projection`；保留其结构化原因与有效时间戳。 |
| `boundary_warning` | `contract.error_diagnostics[]` | 接受精确码 `public_boundary_violation` 与 `registry_boundary_risk`。 |
| `failing_check` | 其余 `contract.error_diagnostics[]` | 保留结构化 scope、精确 goal id、码与脱敏消息。 |
| `failing_check` | `global_registry.findings[]` | 接受精确 `severity=high` 或 `severity=action`；信息性发现留在该聚焦收件箱之外。 |
| 仅 agent scope | `run_history.goals[].coordination.registered_agents` | 为显式 `--agent-id` 验证精确候选 goal 成员；该来源绝不创建风险行。 |
| `rollback_candidates` | 无当前接受来源 | 保持侧面为空，并把缺失正式生产者记录为省略。 |

结构化 `code` 值而非散文决定分类。契约诊断把来源 `severity=error` 映射到风险 `severity=high`；其他受支持严重级保持其稳定排序。作用于 goal 的契约诊断为每个精确 `goal_ids` 成员展开为一行，而全局行无 `goal_id` 且影响整个控制面。

稳定下一动作同样遵循结构化种类而非来源散文：

- `public_boundary_violation`：投递前检查并移除该违反；
- `registry_boundary_risk`：检查并修复 registry 边界投影；
- 其他契约诊断：检查并解决点名的契约检查；
- registry 发现：使用脱敏结构化建议或稳定检查并解决回退；以及
- `stale_latest_run_projection`：信任最新 run 路由前先运行 `refresh-state`。

出现身份是规范 JSON 对象上 SHA-256 摘要的前 16 个小写十六进制字符，该对象只含公开来源界面、原始来源列表索引、结构化种类、scope 与精确 goal id。它绝不对源散文、路径、凭据或脱敏移除的其他文本哈希。聚合只合并相同的类别、种类、goal id 与出现 id 行；它保留最高严重级并递增 `occurrence_count`。因此不同来源位置即使脱敏摘要相同也保持不同。

排序与读取严格有界。调用方至多收到 100 个结果，`source_scan_limit` 把每个接受来源的检查限制在 400 行。`source_rows_truncated` 与仅计数警告暴露任何有界来源扫描；匹配行与出现计数在结果限制前计算，组只从保留扁平列表派生。来源警告封顶为八条，而其摘要计数保持未封顶。

默认 `24h` 请求窗口为协议兼容保留，但首批接受来源描述当前状态。活动的过期状态不匹配永不因 `time_range` 老化掉，即使其有效最新 run 时间戳早于请求窗口。缺失或无效时间戳产生有界警告且只省略该显示字段；它们不隐藏活动风险，也不造成年龄猜测。

#### 精确 agent scope 与失败行为

无 `--agent-id` 时，命令不检查协调。有过滤器时，它按精确 id 索引至多 `source_scan_limit` 个紧凑历史 goal 行，只读取 `run_history.goals[].coordination.registered_agents`。全局行保持可见。goal 作用域行只在其精确、格式良好的历史行确认请求的 agent 缺席后才被排除；空已注册 agent 列表是有效验证缺席。

候选无精确检查的历史行、超出扫描边界、或协调或已注册 agent 数据畸形时，命令必须以 `agent_scope_unavailable` 失效关闭。它不得通过 quota 健康、第二次历史读取、逐 goal 读取或 `agent_management_projection` 挽救或抑制该行。

命令失败比不健康状态更窄。状态收集异常、非对象 status 载荷、缺失或畸形必需投影容器、不可验证的显式 agent scope 返回带紧凑脱敏错误与非零 CLI 退出的 `ok=false`。省略的空来源列表字段是有效空源；同一字段存在但带非列表值则畸形。存在且格式良好的 `global_registry` 带 `global_registry.available=false` 是有效空源，贡献一条有界可用性警告，而非命令失败。

#### 回滚省略与权限

没有当前接受来源能证明回滚候选。边界警告与失败检查从不被猜测进该侧面。在正式生产者提供允许的回滚触发、受影响持久化 scope 与因果 todo/event/commit/PR/外部资源关联之前，该组保持为空，响应记录 `rollback_candidate_source_unavailable`。

Global-risks 响应是只读报告。它不授权回滚、历史重写、外部清理或合并。任何未来候选仍必须使用 `rollback_packet_v0` 并获得受保护或破坏性动作要求的每项批准；本命令绝不为了暗示该权限而在首版风险行上设置 `requires_user_approval=true`。

## 动作阶梯

响应可以包含动作，但每个动作必须声明其权限：

| 动作种类 | 默认权限 |
| --- | --- |
| `read_more` | Agent 可以运行另一个只读紧凑命令。 |
| `review` | 使用普通 claim 或独立交接；只在需要时声明执行者分离。 |
| `promote_todo` | `loopx todo add` 前需要用户/controller 批准。 |
| `ask_user` | 面向用户的问题；回答前阻塞路径不投递。 |
| `pause_or_resume` | 需要显式操作员批准。 |
| `merge_or_publish` | 需要仓库策略、干净验证与任何显式评审或操作员 gate。 |
| `rollback_or_history_rewrite` | 需要 `rollback_packet_v0` 与显式批准。 |

协议应清楚标明何时要求用户决策、何时要求显式对等评审、何时当前对等方可以安全继续。

## 隐私边界

每个响应必须包含或隐含这些边界事实：

```json
{
  "raw_logs_recorded": false,
  "raw_transcripts_recorded": false,
  "raw_connector_payloads_recorded": false,
  "credential_values_recorded": false,
  "absolute_paths_recorded": false,
  "private_source_bodies_recorded": false
}
```

若有用摘要需要私有物料，命令应返回关卡或省略，而非物料本身。

## 验收检查

第一个实现在以下条件下可接受：

- 命令响应默认只读；
- `loopx global-summary`、`loopx global-gates`、`loopx global-todos` 与 `loopx global-risks` 发出匹配的规范命令响应，而只有 goal summary 保持仅 host；
- 每个命令指名其紧凑 LoopX 来源界面；
- gates 指名 owner、正式相关被阻塞 todo 或 goal scope、问题与下一安全动作；
- global-risks 来源健康与成功报告分离，接受省略空来源列表与不可用全局 registry，且在畸形必需投影上失败；
- global-risks 类别组划分其有界出现感知扁平列表，且当前过期状态不匹配跨时间窗口保持可见；
- global-risks agent 过滤验证精确紧凑历史成员，任何候选 goal 无法验证时失效关闭；
- global-risks 不暴露猜测回滚候选，也不授予回滚或其他受保护权限；
- agent 过滤排除所选 agent 未注册的 goals；
- 未知命令与遗留 CLI 别名以帮助失效关闭；
- 动作声明批准与所有权要求；
- 风险携带公开安全证据引用；
- 不记录原始日志、transcript、凭据、本地路径或私有源正文；
- `python3 examples/project/global-manager-command-protocol-smoke.py` 通过。
