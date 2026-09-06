# auto_research_role_profile_v0

`auto_research_role_profile_v0` 定义 LoopX auto-research worker 在加载任何角色特定 playbook 之前如何知道自己是谁。它桥接三个既有界面：

- 授予身份与权限的共享 LoopX 控制面；
- 定义在相位内如何行动的 worker 局部角色 playbook；
- 定义持久化本地规则的仓库或工作区 `AGENTS.md`。

该契约存在是因为 Arbor 与 LoopX 使用 skill 的方式不同。Arbor 可以把身份主要保留在 Coordinator / Executor 拓扑内，然后加载 skill 作为相位 playbook。LoopX 是去中心化的：几个 worker 可以在一个状态图上运行于独立 Codex 会话中，因此身份必须是显式控制面状态，而非从 skill 名或 pane 标题推断。

## 所有权拆分

| 界面 | 拥有 | 不拥有 |
| --- | --- | --- |
| LoopX 控制面 | `agent_id`、`role_id`、claim、capability token、相位、写边界、gate 状态与停止条件。 | 实现相位的详细推理清单。 |
| Worker 局部角色 playbook | 命令、清单、工件 schema 提醒、评审 prompt 与相位特定失败模式。 | 写入、提升、合并、发布或绕过关卡的权限。 |
| `AGENTS.md` | 仓库局部与工作区局部规则，如私有边界、PR 卫生、首屏评审、受保护路径与本地启动策略。 | 动态角色分配或当前前沿选择。 |
| Host 启动器 | 可见 pane、环境变量、attach/stop 控件与接管装置。 | 研究真相、提升决策或隐藏调度权限。 |

该拆分保持 playbook 有用，而不让它们成为第二身份来源。一个 worker 可以在不同角色中加载同一 `loopx-auto-research` playbook，但 profile 告诉它哪个小节适用、哪些写入被允许。

## Profile 形状

Profile 公开安全且足够小，可嵌入启动器包、前沿项、bootstrap prompt 或未来内核 API。

```json
{
  "schema_version": "auto_research_role_profile_v0",
  "goal_id": "loopx-auto-research-demo",
  "agent_id": "research-executor",
  "role_id": "research_executor",
  "display_name": "Research executor",
  "phase": "attempt_running",
  "capability_token": "research_executor",
  "todo_id": "todo_auto_research_demo_001",
  "hypothesis_id": "hyp_state_a2a_round",
  "allowed_actions": ["claim_attempt", "edit_allowed_scope", "run_dev_eval", "write_evidence"],
  "write_scope": ["solution.py", "experiments/**"],
  "protected_scope": ["task.py", "eval.py", "data/**"],
  "required_skill": "loopx-auto-research",
  "skill_section": "Research executor",
  "agents_overlay": ["workspace/AGENTS.md"],
  "stop_conditions": [
    "quota should-run returns false",
    "frontier is empty or claimed by another agent",
    "protected scope would be edited",
    "private material or credentials are required",
    "operator gate is projected"
  ],
  "handoff_outputs": [
    "research_evidence_event_v0",
    "branch_or_artifact_ref",
    "retry_or_retirement_rationale"
  ],
  "successor_todos": [
    {
      "after_action": "run_dev_eval",
      "when": "dev_supported_without_holdout",
      "target_agent_id": "research-executor",
      "target_role_id": "research_executor",
      "task_class": "advancement_task",
      "action_kind": "run_holdout_eval",
      "text": "Run held-out validation for the dev-supported hypothesis."
    }
  ],
  "continuation_policy": {
    "schema_version": "auto_research_continuation_policy_v0",
    "successor_source": "role_profile.successor_todos",
    "required_holdout_improvement_count": 2,
    "unmet_target_rule": "when the target is unmet and a successor condition is satisfied, create or link that successor",
    "no_followup_rule": "no-follow-up is valid only after target reached, projected blocker/gate, or evidence-backed retirement"
  }
}
```

必需字段：

- `goal_id`、`agent_id`、`role_id`、`phase` 与 `todo_id` 标识当前 worker 与工作项。
- `capability_token` 必须匹配 `auto_research_role_state_machine_v0` 中的一种 capability。
- `allowed_actions`、`write_scope`、`protected_scope` 与 `stop_conditions` 界定 worker 可做什么。
- `required_skill` 与 `skill_section` 在身份解析后把 worker 路由到正确的操作指南。

`hypothesis_id`、`agents_overlay`、`handoff_outputs`、`successor_todos` 与 `continuation_policy` 等可选字段让 profile 更顺手，但不授予权限。successor todo 声明是小型角色局部交接规则：worker 完成 `after_action` 且 `when` 条件满足时，pane 级 tick 可以为 `target_agent_id` 写入指名的 LoopX todo。它不是图级规划器，且必须仍通过 quota、todo 元数据与公开/私有边界检查，另一个 agent 才能运行它。`continuation_policy` 是 no-follow-up 的紧凑验收 guard：若目标未达成且角色声明的 successor 条件满足，worker 必须创建或链接该 successor，而不是关闭 lane。

## 解析顺序

每个可见 auto-research worker 应按此顺序解析其指令：

1. 从启动器包、前沿项或 bootstrap prompt 读取角色 profile。
2. 运行 `quota should-run --goal-id ... --agent-id ...` 并确认所选 todo 仍与 profile 匹配。
3. 读取当前角色/状态机契约中允许的转换。
4. 加载所需 skill 且只加载 `skill_section` 指名的小节。
5. 读取适用的 `AGENTS.md` overlay 以获取仓库与工作区规则。
6. 在 `allowed_actions` 与 `write_scope` 内行动，然后只写入列出的交接输出与角色声明的 successor todos。

若任何来源冲突，worker 按此顺序失效关闭：

1. 操作员 gate 或私有/安全边界；
2. 控制面 quota、claim、capability 或写 scope 不匹配；
3. 仓库 `AGENTS.md` 安全规则；
4. skill 清单不一致；
5. 启动器 pane 标签或装饰性 prompt 文本。

## Auto-Research 角色 Profile

v0 演示应暴露四个逻辑常开 profile。只有当合并职责在 profile 中显式且记录仍指名产生每个转换的角色时，host 才可以渲染更少 pane。

| Role id | Skill 小节 | 主要相位 | 写入 | 必须停止于 |
| --- | --- | --- | --- | --- |
| `research_curator` | Research curator | `contract_ready`、`promotion_gate` | `research_contract_v0`、owner gate todos、受保护边界笔记。 | 下一步会选择赢家、运行实验或发布无支持证据。 |
| `hypothesis_proposer` | Hypothesis proposer | `hypothesis_proposed`、`retired` | `research_hypothesis_v0`、successor todos、no-follow-up 理由。 | 新颖性需要启发想法的同一来源，或负面证据将被隐藏。 |
| `research_executor` | Research executor | `frontier_selected`、`attempt_running` | 分支引用、dev/holdout eval 证据、重试包、角色声明 successor todos。 | 需要受保护 scope 变更、提升决策或私有/原始工件。 |
| `evaluator_promoter` | Evaluator/promoter | `evidence_recorded`、`evaluated`、`promotion_gate` | Held-out 验证证据、评估摘要、提升/退役候选、gate todos。 | 证据仅为 dev 却会被呈现为已提升，或必需时 held-out 数据缺失。 |

Gate 管理人、综合叙述者与前沿保洁员等未来角色是拆分候选，不是必需 v0 pane。只有在演示证据表明某转换职责需要独立 owner 时才应引入。

## Worker 局部 Playbook 策略

使用一个包含角色小节的 worker 局部 `loopx-auto-research` playbook：

- `Research curator`
- `Hypothesis proposer`
- `Research executor`
- `Evaluator/promoter`
- `Visible takeover and stop controls`

这使每个可见 worker 保持一致，而不把 auto-research 暴露为普通项目 agent 的全局 LoopX skill。只有在可见运行显示单一角色路由 playbook 无法防止的反复混淆时，才拆分为角色特定 worker playbook。拆分决定应引用证据，如错误小节加载、未授权写入、隐藏负面证据或错过停止条件。

Playbook 正文不应发明当前工作。它应告诉 worker 读取角色 prompt/profile 上下文，并通过 Codex TUI 内的 pane 级 LoopX 包装器运行角色局部 quota/frontier 命令。这镜像 Arbor 有用的「在精确相位加载清单」行为，同时保留 LoopX 的去中心化身份模型。

## 演示启动器含义

可见 tmux 或终端启动器应静默物化 profile，并为每个角色启动一个全新交互式 Codex CLI TUI：

```bash
export LOOPX_GOAL_ID=loopx-auto-research-demo
export LOOPX_AGENT_ID=research-executor
export LOOPX_ROLE_ID=research_executor
export LOOPX_ROLE_PROFILE_REF=auto_research_role_profile_v0
exec codex -c model_reasoning_effort=high -C "$LOOPX_PROJECT" "$ROLE_PROMPT"
```

Pane 标题是装饰性的。Profile 与 quota/frontier 投影才是权威，但原始 profile/frontier JSON 应留在本地工件或显式机器 channel 中。启动器必须保持 attach、interrupt 与 stop 命令可见，使用户无需读隐藏日志即可接管。

## 验收检查

一个实现在以下条件下满足本契约：

- 启动器与前沿包为每个可见 worker 暴露 `auto_research_role_profile_v0`，而不在首屏打印原始 profile JSON；
- 每个 profile 指名 `agent_id`、`role_id`、`phase`、`capability_token`、`allowed_actions`、`write_scope`、`protected_scope`、`required_skill`、`skill_section` 与 `stop_conditions`；
- 默认演示使用四个逻辑 v0 角色身份，owner 接管是可见控制界面而非研究角色；
- 角色感知 skill 说明身份来自 profile 与 quota/frontier，而非 skill 本身；
- profile 与 skill 使 no-follow-up 取决于对继续目标的证据，而非仅一个成功提升候选；
- `AGENTS.md` overlay 可以添加更严格本地规则，但不能把角色权限扩大到控制面 profile 之外；
- 验证证明演示的可理解性或可中断性不需要 leader/coordinator pane。
