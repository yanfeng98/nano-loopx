# Dreaming 探索泳道


LoopX 最终应当支持一条独立的 dreaming / 探索泳道，服务于长程项目。这条泳道与正在积极交付工作的 project agent 不是一回事。它的职责是在低压力的后台时间里做跨 run 学习、选项发现与 refactor 警告。

## 为什么存在

Project agent 针对当前任务做了优化：

- 保留本地上下文，
- 执行下一个有边界的变更，
- 避免范围蔓延，
- 尊重活跃 worktree 与交付压力。

这让它们不适合做广泛探索。同一个正在落地修复的 agent 不应同时被要求自由地重新思考架构、寻找替代方案或提出大型 refactor。这些活动有价值，但它们需要一条拥有不同权限与输出规则的独立泳道。

近期 agent 平台与研究的信号指向同一方向：

- Anthropic 的 Managed Agents dreaming 功能把 dreaming 定义为对先前 session 与 memory store 的定时回顾，从中提取模式并整理 memory，让 agent 在 session 之间得到改善。
- Auto-Dreamer 把同样的想法表达为离线 memory consolidation：把快速的单 session 采集与较慢的跨 session 抽象、裁剪与替换分开。
- Agent-memory 综述把持续整合、可信反思、习得性遗忘与隐私治理列为自主 agent 的开放工程问题。

LoopX 应当采纳有用的形态，而不是炒作：dreaming 是一条受治理的后台泳道，用于整合与提案，而不是改写项目 truth 的自主许可。

## 优先级

优先级：**在 operator gate 与 reward loop 稳定之后列为 P1**。

这条泳道不应阻塞 v0.1 bootstrap、registry sync、status 契约、operator dashboard 或项目本地刷新。当多个真实项目接入、LoopX 积累的 run 历史足以让跨项目学习产生价值时，它才变得重要。

## 角色

dreaming / 探索 agent 可以扮演：

- **Explorer（探索者）**：搜索替代方案、比较设计、阅读相邻文档、审视进展缓慢的背景问题，并准备选项。
- **Memory consolidator（记忆整合者）**：把反复出现的 run 经验压缩为项目本地 playbook、建议的 skill 更新或活跃状态建议。
- **Refactor applicant（重构申请者）**：识别反复出现的本地修复何时暗示更大的 refactor，但把它作为申请提交评审，而不是直接做出变更。
- **Warning agent（警告 agent）**：标记忙碌 project agent 可能忽略掉的风险：重复状态、过期文档、不安全的 public/private 边界漂移、反复出现的验证失败，或不断累积的本地专用胶水。

## 权限

默认权限刻意收窄：

- 读取项目状态、run 历史、公开文档，并且只有在 owner 项目允许时才读显式私有的本地状态；
- 默认不修改项目文件；
- 不追加 human reward 或 controller opt-in；
- 未经 operator gate 不重写活跃项目 truth；
- 绝不把私有 evidence 发布到公开文档或示例中。

dreaming 的输出是提案、警告或候选 patch 方案。由 operator 或符合条件的 peer 决定它是否成为正常项目工作。

## 与 Replan 的关系

Dreaming 与自主 replan 都是控制面规划泳道。它们可以修复执行轨道、总结跨 run 模式、创建可评审选项。它们不得悄悄变成决定 project agent 如何解决当前实现问题的任务策略。

使用这条边界：

| 泳道 | 输出 authority | 典型输出 | 晋升路径 |
| --- | --- | --- | --- |
| Delivery agent policy（交付 agent 策略） | 在当前授权边界内执行。 | 实现方案、调试策略、验证选择、有边界 patch。 | 交付后写入已验证工作事件与活跃状态更新。 |
| Autonomous replan（自主 replan） | 执行停滞或过期时的有界控制面义务。 | Split/retire/add todo、请求 blocker 写回、询问 operator 决策、命名下一个验证命令与停止条件。 | 只在验证后写入控制面状态，或路由到 user/controller gate。 |
| Dreaming / exploration（dreaming / 探索） | 默认为建议性提案。 | Refactor 警告、memory consolidation、选项对比、归档建议、风险说明。 | 进入 operator/controller 评审，之后才能成为正常交付工作或活跃项目 truth。 |

任何规划输出的问题是：它是 `authority` 还是 `proposal`。Guard 与 freshness 输出可以像 authority 一样的控制信号；dreaming 输出是提案，除非后续 operator/controller 决策晋升它们。这让 LoopX 不会成为第二个脆弱的 agent，同时仍能维护长程执行轨道。

对于周期性自主 replan，保持所有权划分清晰：

| 层 | 职责 |
| --- | --- |
| LoopX | 从紧凑 run 历史、状态新鲜度、quota 与边界事实检测周期评审到期；发出义务、停止条件与紧凑指导词表；记录后续 replan 确认。 |
| Agent loop | 在 preflight 期间读取义务，把当前 Turn 路由进有边界的 replan 片段，向模型/执行器注入当前状态，运行经过验证的 todo 写入，并只在写回后 spend。 |
| 模型 / 执行器 | 语义上决定保留、拆分、新增、退役哪些工作，或升级为 user/controller 决策；解释权衡并选择下一个有界切片。 |

v0 实现可以在 `status` / `quota` 中同步计算周期评审触发器，因为那是确定性的控制面投影。如果评审变得更昂贵或更语义化，把它移到 server/dreaming 规划泳道作为建议性提案。Server 可以与交付观察并行运行该提案，但晋升与执行应通过正常 agent loop、`quota should-run` 与 goal-boundary 检查保持 client-serial。

## Run Record 形态

Dreaming run 应可见，但不应与交付 run 混在一起：

```json
{
  "goal_id": "example-project-main-control",
  "classification": "dreaming_exploration_proposal",
  "recommended_action": "review the proposed refactor warning in the operator gate",
  "operator_question": "Should this project open a refactor task for duplicate state handling?",
  "agent_command": null,
  "dreaming": {
    "lane": "exploration",
    "evidence_window": "last_20_runs",
    "proposal_type": "refactor_warning",
    "confidence": "medium",
    "requires_project_controller": true
  }
}
```

候选分类：

- `dreaming_exploration_proposal`
- `dreaming_memory_consolidation`
- `dreaming_refactor_warning`
- `dreaming_archive_suggestion`

这些通常应以 `waiting_on=user_or_controller` 配合 `operator_question` 进入，而不是 `waiting_on=codex`，因为该泳道默认是建议性的。

## UI 影响

dashboard 应以独立泳道或徽章显示 dreaming 输出：

```text
Goal
  Operator gate: 批准 / 拒绝 / 推迟提案
  Delivery lane: 最新 project-agent run
  Dreaming lane: refactor 警告或 memory consolidation 提案
```

这让 project-agent 工作保持干净，同时给用户一个集中评审更广泛学习与 refactor 请求的地方。

`loopx status` 应暴露提案加一个紧凑徽章：

```json
{
  "dreaming_proposal": {
    "schema_version": "dreaming_proposal_v0",
    "classification": "dreaming_exploration_proposal",
    "proposal_type": "refactor_warning",
    "advisory": true,
    "execution_allowed": false,
    "delivery_spend_allowed": false
  },
  "dreaming_lane_badge": {
    "schema_version": "dreaming_lane_badge_v0",
    "lane": "dreaming",
    "label": "Dreaming",
    "status": "dreaming_exploration_proposal",
    "proposal_type": "refactor_warning",
    "advisory": true,
    "interrupts_delivery": false,
    "review_required": true,
    "execution_allowed": false,
    "delivery_spend_allowed": false,
    "promoted_to_delivery": false
  }
}
```

徽章有意只携带路由事实，而不是完整说明。完整理由保留在 `dreaming_proposal` 与 run artifact 中，而 dashboard 与 heartbeat 消费方可以渲染独立 Dreaming 泳道，不会把建议性提案误认为交付工作。

## 首个实现切片

第一个有用的切片是文档与 status schema，而不是自主 agent：

1. 为 dreaming 分类与提案字段添加公开词表。
2. 让 `loopx status` 把 dreaming 提案呈现为 operator gates。
3. 添加一个本地命令或脚本，读取近期 run 历史并输出 dry-run 提案，而不写项目文件。
4. 只有在真实提案证明有用之后，才添加定时 heartbeat 或自动化。

本地入口点是：

```bash
loopx dreaming dry-run --goal-id <goal-id> --limit 20
```

该命令通过选定的 registry/runtime root 读取紧凑 run 历史，并返回一个建议性的 `run_record_preview`。它不追加 runtime 历史、不修改活跃状态、不授予 `agent_command`，也不 spend quota。该预览用于 operator/controller 评审，之后任何提案才会被晋升为普通交付工作。

## Server 管理的规划语义

未来的 LoopX server 可以调度 dreaming/规划工作，但 server 拥有的泳道保持与 CLI dry run 相同的 authority 边界：

```json
{
  "schema_version": "server_managed_planning_contract_v0",
  "lane": "dreaming_planning",
  "authority": "proposal_only_until_promoted",
  "may_rank_candidate_todos": true,
  "may_suggest_evidence_probes": true,
  "may_execute_protected_actions": false,
  "may_read_private_material": false,
  "may_mutate_active_state": false,
  "may_spend_delivery_quota": false,
  "promotion_required": true,
  "promotion_requirements": [
    "operator_or_controller_approval",
    "normal_quota_should_run_decision",
    "goal_boundary_write_scope_approval",
    "public_private_boundary_scan_for_public_artifacts"
  ]
}
```

Server 可以排序候选 todos、提出 evidence probes、发出 refactor 或 memory-consolidation 警告。在提案通过正常 operator、quota 与 goal-boundary 路径被晋升之前，它不得执行受保护动作、读取私有资料、修改活跃状态、追加交付历史或 spend 交付配额。这让 dreaming 对长程产品品味有用，同时防止它成为第二个隐藏 project agent。

验收标准：一个项目可以在不打断 project agent 的情况下收到 dreaming 提案，并且用户可以从 LoopX 批准、拒绝或推迟它。

## 参考

- Anthropic, "New in Claude Managed Agents: dreaming, outcomes, and
  multiagent orchestration":
  <https://claude.com/blog/new-in-claude-managed-agents>
- Auto-Dreamer: Learning Offline Memory Consolidation for Language Agents:
  <https://arxiv.org/abs/2605.20616>
- Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging
  Frontiers:
  <https://arxiv.org/abs/2603.07670>
