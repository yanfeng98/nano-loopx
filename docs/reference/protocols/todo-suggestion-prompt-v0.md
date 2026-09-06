# todo_suggestion_prompt_v0

`todo_suggestion_prompt_v0` 是一项 prompt 契约，用于请求用户当前的项目 agent 产出一小份候选 todo 决策队列。

在此路径中 LoopX 不分析仓库。LoopX 只提供受限的任务正文、候选 schema、晋级策略、来源 lane 与频率限制。项目 agent 读取当前仓库并返回 `suggested_todos`；在用户或主 controller 晋级其中某一项之前，这些候选都不是正式的 LoopX todo。

## 命令

```bash
loopx todo suggest --goal-id <goal-id> --from recent-repo --from loopx-deferred --limit 3
```

有用的触发时机：

- 连接后的 onboarding，项目已有有效 LoopX state 之后；
- 用户明确请求，如「接下来有什么值得做的？」；
- 检查 status/quota 后没有任何可运行的 agent todo；
- 自上次候选评审以来仓库有实质性变化；
- `quality-watch` 节奏的 Turn，其中 agent 应把最新信号与最后已知状态对比，且只返回新证据或仍未覆盖的证据所对应的候选。

不要在每个 heartbeat 都运行它。默认上限是 3，硬上限是 5。

## 候选形状

agent 的输出应使用 `suggested_todos` 列表。每项使用 `suggested_todo_candidate_v0`：

```json
{
  "schema_version": "suggested_todo_candidate_v0",
  "candidate_id": "suggested_todo_repo_smoke_gap",
  "title": "Add a smoke for the new setup path",
  "why_now": "Recent docs changed the setup flow, but no smoke covers the wording.",
  "evidence": ["README.md", "examples/project/project-prompt-smoke.py"],
  "first_safe_action": "Inspect the existing setup smoke and draft one failing assertion.",
  "requires_user_decision": false,
  "risk": "low",
  "value": "prevents onboarding regressions",
  "confidence": "medium",
  "suggested_owner_agent": "codex-main-control",
  "promotion_preview": "loopx todo add --goal-id <goal-id> --role agent --text '...'"
}
```

## 规则

- 候选生成默认只读。
- 候选不是用户 todo。
- `requires_user_decision=true` 仅用于 owner 选择、受保护访问、外部动作或私有物料批准。
- 证据薄弱或已被覆盖时，agent 可以返回空列表。
- 晋级在显式批准后使用 `loopx todo add`；本协议不写入 active state。
