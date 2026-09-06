# 集成指南


LoopX 应作为共享本地基座使用，而不是复制进每个项目。

## 本地基座

克隆或符号链接一份：

```bash
git clone <repo-url> ~/loopx
~/loopx/scripts/install-local.sh
loopx doctor
```

安装器把当前 checkout 发布为本地发布快照，并把该快照链接到 `~/.local/bin/loopx`。
它还安装一个 `loopx-canary` wrapper，为选定的灰度上线 goal controller 指向活
checkout。这让默认自动化保持稳定，同时允许一个 canary goal 在晋升前验证
prompt/运行时变更。安装器在 bin 目录缺失于 `PATH` 时把其加入当前 shell profile，
并在 `~/.codex/skills` 安装 `loopx-project` Codex skill 的快照，
使未来项目 Agent 使用同一连接工作流。在任何项目文件夹用 `loopx doctor` 检查
解析的命令路径、符号链接目标、发布快照、canary wrapper、已安装 skill 的
delivery-hint 状态、wrapper 脚本与 Python 导入健康。

## 全局 Skill 策略

LoopX 产品行为属于已安装的全局 Codex skills，而不是某个仓库的 `AGENTS.md`。
保持全局 skills 窄且版本化：它们应教 LoopX 连接、quota/state/todo writeback、
自修复与 todo succession 等通用产品契约。项目状态、benchmark 特定选择、私有材料
与一次性 operator 决策留在 registry、active state、run history 或项目文档。
当一个循环行为应改进每个未来 worker 时，更新仓库 skill 源并运行
`scripts/install-local.sh`；当它只适用于本仓库的贡献卫生时，留在 `AGENTS.md`。

灰度上线流程：

```bash
# 只为 canary goal controller 生成 heartbeat 任务体。
loopx-canary heartbeat-prompt \
  --brief \
  --cli-bin loopx-canary \
  --goal-id <CANARY_GOAL_ID>

# canary 观察看起来健康后，把 checkout 晋升为默认。
~/loopx/scripts/install-local.sh
loopx doctor
```

然后项目可以调用：

```bash
loopx --registry <private-registry> registry
loopx --registry <private-registry> history
loopx --registry <private-registry> status
loopx --registry <private-registry> check --scan-root <project-root>
loopx doctor
```

## Lark 或飞书回复卡片

把 LoopX 工作变成 Lark 或飞书回复的聊天网关应把消息渲染与消息发送分开。
实现归显式启用的 Lark extension 所有：`loopx.extensions.lark.presentation.message_card`；
核心不为 provider 拥有的展示代码保留兼容导入：

```python
from loopx.extensions.lark.presentation.message_card import build_lark_markdown_reply_card

card = build_lark_markdown_reply_card(
    "**Done**\n- Validated the bounded change",
    title="LoopX result",
    template="green",
)
```

Helper 只构建 JSON 兼容卡片内容并从 CLI 输出提取回复 `message_id`。
它不调用 Lark、飞书或任何外部写 API。网关可以在相关 LoopX gate 允许该写后，
把返回 payload 传给自己的已批准发送器。

## 一键项目连接

对新项目，从以下开始：

```bash
cd /path/to/project
loopx bootstrap \
  --goal-id project-goal \
  --objective "Improve this project through bounded, verified goal segments." \
  --goal-doc GOAL.md
```

`loopx connect` 是同一操作的别名。命令可安全重跑：默认它保留现有状态文件与现有
registry 条目。如果目标在连接后只需要额外写边界，优先增量迁移路径：

已经验证项目 bridge 的集成 provider 可以显式拥有一站式连接检查：

```bash
loopx connect \
  --goal-id project-goal \
  --no-onboarding-scan \
  --onboarding-connection-validation provider-prevalidated
```

默认保持 `agent`，它可能为通用 adapter 创建一个 `loopx check` onboarding Todo。
`provider-prevalidated` 在 registry 记录 provider 归属并省略该 Agent Todo；
它不运行验证、不授予工具、不扩大 provider 权威。只在调用方已验证连接时使用它。
仓库扫描与连接验证仍是独立控制。

```bash
loopx configure-goal \
  --goal-id project-goal \
  --write-scope "src/**" \
  --execute
```

只在刻意想替换 registry 条目或 active state 时传 `--force`。
如果需强制重连但想保留当前 todo 投影，加 `--preserve-todos`。

默认文件是：

```text
.loopx/registry.json
.codex/goals/<goal-id>/ACTIVE_GOAL_STATE.md
```

生成的 registry 条目还包含 `execution_profile`。这是项目的源码级 delivery 契约，
不是一次性的 heartbeat 提示：

```json
{
  "execution_profile": {
    "cadence": "bounded_progress_segment",
    "minimum_scale": "multi_surface_or_implementation",
    "must_include": [
      "coherent_artifact",
      "targeted_validation",
      "state_writeback"
    ],
    "spend_rule": "spend_only_after_artifact_validation_writeback",
    "outcome_floor": {
      "required_when": "after_surface_progress_streak",
      "surface_streak_threshold": 3,
      "outcome_markers": [
        "eval_metric",
        "experiment",
        "macro_evidence",
        "evidence_segment",
        "adapter_proof"
      ],
      "surface_only_hints": [
        "forecast",
        "runbook",
        "queue",
        "fields"
      ],
      "must_advance": [
        "primary_goal_outcome"
      ],
      "avoid": [
        "surface_only_progress_loop"
      ],
      "if_unavailable": "report_blocker_without_spend"
    },
    "degradation_policy": {
      "small_scale_streak_threshold": 2,
      "on_degradation": "require_blocker_or_expand_next_batch"
    }
  }
}
```

`loopx status`、`quota should-run` 与 `review-packet --handoff-only`
都通过 `project_asset` 读取同一 profile。当近期 follow-through 一直缩成
test-only、single-surface 或 unknown-scale 运行，handoff delivery 契约从
profile 生成：下一个 Agent 必须扩展到声明的最小 scale，
带真实 artifact、目标验证与状态写回，或在花配额前报告 blocker。
只在项目有刻意不同下限时才覆盖 profile；不要修补自动化提示来补偿薄连接契约。

## 一个仓库多个目标

一个仓库可以同时持有一条主 lane、一条侧绕过与其他独立目标。
用不同稳定 `goal_id` 连接每条 lane：

```bash
cd /path/to/project
loopx connect \
  --goal-id main-control \
  --objective "Run the main project control lane." \
  --adapter-kind read_only_project_map_v0 \
  --adapter-status connected-read-only

loopx connect \
  --goal-id side-bypass \
  --objective "Run the low-conflict side bypass lane." \
  --adapter-kind read_only_project_map_v0 \
  --adapter-status connected-read-only
```

两个条目住在同一本地 `.loopx/registry.json`，但每个目标必须在
`.codex/goals/<goal-id>/ACTIVE_GOAL_STATE.md` 下拥有自己的忽略 active state。
在两个目标 id 间共享同一 `state_file` 被视为 registry 健康错误，
因为它让一条 lane 覆盖或摘要另一条的状态。不要提交活动
`ACTIVE_GOAL_STATE.md`；需要公共示例时发布脱敏模板或紧凑投影。

在每个改状态的命令上使用 `--goal-id`：

```bash
loopx read-only-map --goal-id main-control
loopx read-only-map --goal-id side-bypass --dry-run
loopx quota should-run --goal-id side-bypass
```

`read-only-map` 对同仓库设置是 goal 感知的。除通用项目清单外，
它还报告所选目标是否有本地项目 registry、`.codex/goals/<goal-id>/` 状态目录与
声明的 active state 文件。缺失侧 lane 状态目录产生
`project_goal_state_dir_not_detected:<goal-id>` 加遗留
`project_local_goal_state_not_detected` 风险，而同仓库健康主 lane 不掩盖该问题。

如果提供 `--goal-doc`，文档路径记录为主要权威来源。接收的 Codex 在选择下一个
动作前应首先检查该文档。

如果另一个 Codex 会话应从项目文件夹与 goal 文档执行连接，
用 [new-project-codex-prompt.md](operations/new-project-codex-prompt.md) 作为
handoff 提示。

你可以生成该 handoff 提示：

```bash
loopx new-project-prompt \
  --project /path/to/project \
  --goal-doc /path/to/project/GOAL.md
```

如果已连接项目之后应通过循环 Codex App heartbeat 运行，生成 heartbeat 任务体，
而不是手抄 quota guard 与 spend 协议：

```bash
loopx heartbeat-prompt \
  --goal-id project-goal
```

对已连接目标省略 `--active-state`；CLI 从 registry goal `state_file` 解析
active state。只把 `--active-state` 保留为分离状态文件、迁移检查或兼容测试的
显式覆盖。

对即时 Codex App 自动化，当目标 Codex Agent 能自己检查 LoopX 状态与 CLI 输出时，
用薄形式作为本地机器默认调度器：

```bash
loopx heartbeat-prompt --thin \
  --goal-id project-goal
```

在评审完整契约后、当已安装提示应内联更多生命周期细节时，用紧凑形式：

```bash
loopx heartbeat-prompt --compact \
  --goal-id project-goal
```

如果已安装自动化仍需要更小，使用精简任务体：

```bash
loopx heartbeat-prompt --brief \
  --goal-id project-goal
```

把生成的任务体复制进 heartbeat 自动化。定时器只唤醒 Codex；任务体问 LoopX
该目标是否应在该 tick 花 delivery 计算。薄任务体让 Codex 线程保持可替换 worker：
每次唤醒都应重读 registry/全局 quota 真相、active state、status/run history、
repo 状态与项目信号，而不是依赖过期的长提示。紧凑任务体内联保留 quota、gate、
blocker-push、推荐、steering-audit、writeback、refresh 与 spend 生命周期，
而不用把完整审计提示复制进每 run 上下文。精简任务体用于应只携带预检/guard、
核心不变量与 spend 记账的已安装自动化，同时把细节分支委托回生成的契约。

Codex App 可见目标文本可以保持短，如
`按 ACTIVE_GOAL_STATE.md，基于 LoopX 体系，推进项目`。它只是给人类与执行者的
标签。循环自动化提示应使用上面生成的 heartbeat 任务体，使每个项目共享同一
quota、gate、steering-audit、writeback、refresh 与 spend 生命周期。
项目特定行为应住在 registry、active-state 区块、adapter 输出或窄边界规则。
不要为单个项目手工编辑一次性自动化提示分支；当一条生命周期规则通用有用时，
把它加入 `loopx heartbeat-prompt` 与其 smoke 契约。
quota guard 的 `heartbeat_recommendation` 覆盖常见上手情形：新连接的只读目标用
`run_first_read_only_map`，而已映射且无新指令、owner 证据、agent todo、过期来源或
安全 handoff 的目标用 `mapped_noop_if_unchanged`。
同一 guard 的 `execution_obligation` 是 worker 契约：当 `must_attempt_work=true`，
heartbeat 应尝试一个有界片段，即使 `heartbeat_recommendation.notify=DONT_NOTIFY`；
通知不是执行 gate。Quiet no-op 需要显式 `must_attempt_work=false` 契约，
如验证的 `mapped_noop_if_unchanged`。
该生命周期在验证与干净公共/私有边界扫描后把常规公共 commit、push 与 PR 创建
当作自主的；私有或公司内部材料、凭据、破坏性 git、生产动作与明确要求评审的
仓库规则仍在 gate 停下。

在大多数真实项目中这些文件应私有。如果它们包含当前工作状态或本地证据，
把它们加入 `.gitignore`：

```gitignore
.loopx/
.codex/goals/
```

## 项目 Adapter

项目 adapter 应薄且项目特定。它可以读取：

- 活跃目标状态，
- git status，
- 测试或实验状态，
- 廉价健康检查，
- 项目特定 guard。

它应输出：

- `classification`，
- 本地控制循环的确切一个 `recommended_action`，
- 相关警告，
- 硬 guard，
- 可选 run 日志路径。

`recommended_action` 默认是本地项目状态，不是公共产物：它可以包含私有项目引用，
如 todo id、分支名、本地别名或 operator 私有路由标签。它不得包含 AK/SK 值、
令牌、认证头、密码或内联凭据。公共/导出槽在渲染可分享面前必须脱敏或省略私有
路由引用。

默认应只读。启动作业、停止作业、同步文档或编辑生产状态需要显式用户批准。

Bootstrap 命令不创建领域 adapter。它创建最小 registry 与状态契约，
使第一个 adapter 可以刻意添加。

对大项目，在任何写之前优先只读 adapter 映射。映射应识别权威来源、工作簇、
验证面、提议的 peer 任务作用域、边界发现与简短 claim/决策 packet。见
[complex-project-readonly-adapter.md](integrations/complex-project-readonly-adapter.md)。

## Controller / Sub-Agent 协调

一些 Codex goal run 应使用多个子 worker。LoopX 应保持该任务作用域并行显式：

- 子 run 行动前声明 `work_scope`；
- 重叠写作用域需要任务协调者仲裁；
- 除非 registry 授予写作用域，子 worker 默认只读；
- 子最终报告包含变更文件、验证、残余风险与下一个 handoff；
- 临时任务协调者汇总被接受 bundle 证据，而 merge 与状态写回仍遵循显式
  任务/仓库策略。

该模式的最小 registry 字段是：

```json
{
  "parent_goal_id": null,
  "spawn_policy": {
    "mode": "multi_subagent",
    "allowed": true,
    "max_children": 3,
    "allowed_domains": ["docs-map", "validation-map"]
  },
  "coordination": {
    "agent_model": "peer_v1",
    "registered_agents": ["codex-main-control", "codex-side-bypass"],
    "write_scope": ["docs/**", "examples/**"],
    "requires_parent_approval": ["write", "publish", "production-action"]
  }
}
```

当 `spawn_policy.mode=multi_subagent` 时，status 暴露
`project_asset.orchestration`，quota 暴露 `goal_boundary.orchestration`。
这让所选执行模式对 dashboard 与 heartbeat 调度器可见，而不是依赖提示文本。

`spawn_policy` 只管理临时子容量。注册多个持久 peer 不会自动选举协调者，
也不会把其声明 lane 投影给另一个 peer。能激活持久 peer 运行时的 host 必须单独
用 `loopx configure-goal --goal-id <goal> --peer-task-coordinator <registered-agent>`
opt in，并在 quota 时报告 `--available-capability peer_agent_activation`。
用 `--clear-peer-task-coordinator` 清除选择；任一设置都扩大 Todo 归属或仓库权威。

这些字段是公共契约，不是运行时锁管理器。当前轻量运行时面使用 todo
`claimed_by` 作为 active-state CLI 锁下写入的软 owner。Claim id 必须列在
`coordination.registered_agents`；那些身份是对等 peer。任务声明、边界、能力、
typed 延续与仓库策略决定权威。写仓库的 peer 在所选任务要求时使用隔离 worktree。
小的 AGENTS 合格验证变更可以带显式证据 self-merge；更广或更高风险的工作用显式
`independent_handoff` 且 `action_kind=review`，需要执行者分离时可选择排除作者。
软声明不设过期。遗留 bootstrap 选项 `--claim-ttl-minutes` 被接受但忽略；
当具体争用情形需要 TTL、重叠检查、转移与 compare-and-swap 行为时，
使用可选 `loopx task-lease` CLI。硬租约仍按 `(goal_id, todo_id)` 键控，
因此同目标下的无关 todos 在作用域允许时仍可并行。

## 共享运行时

所有 adapter 应在以下位置保存紧凑 run history：

```text
~/.codex/loopx/goals/<goal-id>/runs/index.jsonl
```

这给 App、CLI、heartbeat 与未来 UI 一个检查目标历史的地方。

项目本地 registry 也应同步进共享全局 registry：

```text
~/.codex/loopx/registry.global.json
```

`loopx connect` 与 `loopx refresh-state` 自动完成。全局 registry 是本地私有的，
因为它包含项目路径，但它剥离原始权威来源细节并只保留多项目 status 所需信息。
如果命令在任何项目 registry 外运行，Goal Harness 在存在全局 registry 时回退到它。

只在诊断或恢复时使用显式同步命令：

```bash
loopx sync-global
```

如果 controller 更新 `ACTIVE_GOAL_STATE.md`、进度 ledger 或外部规划区块
而不运行项目 adapter，追加 state-only refresh run，使 status 与 dashboard
不继续显示较旧 adapter run：

```bash
loopx refresh-state --goal-id project-goal
```

命令读取注册的状态文件，在共享运行时根下写私有 JSON/Markdown 刷新 payload，
并追加紧凑 `state_refreshed` 索引记录。紧凑索引只应包含 public-safe 分类、动作、
健康检查与产物指针；原始证据属于项目本地状态文件或私有运行时 payload。
当省略 `--recommended-action` 时，命令从 active state 的 `## Next Action`
第一个 public-safe 条目派生紧凑动作，连接换行续行，并在该条目包含私有外观内容时
回退到通用刷新动作。
如果 `refresh-state` 文本字段被拒绝为私有外观，CLI 点名该字段，
并建议在该处使用紧凑 public-safe 别名/摘要，同时把原始本地路径、私有 URL、
任务正文与日志留在证据或私有 payload。
当状态刷新也是验证过进度产物的紧凑记录时，添加显式 delivery 提示，
使 handoff 就绪不必从分类名推断 scale：

```bash
loopx refresh-state \
  --goal-id project-goal \
  --classification dashboard_home_browser_smoke_regression \
  --delivery-batch-scale multi_surface \
  --delivery-outcome outcome_progress
```

`--delivery-batch-scale` 用于 `test_only`、`single_surface`、`multi_surface`
或 `implementation`。对 Agent 面向的 `refresh-state` 调用，
`single_segment` 与 `bounded_segment` 被接受为 `single_surface` 的输入别名；
记录的 run 仍存储 canonical `single_surface` 值。`--delivery-outcome`
是结构化枚举，不是分类字符串：

| 值 | 含义 |
| --- | --- |
| `surface_only` | 契约、文档、smoke、设置或准备移动了，但主要产品/用例结果没有。 |
| `outcome_gap` | 该 run 本应推进主要结果，但以具体 blocker 或缺失结果结束。 |
| `outcome_progress` | 主要结果已实质推进，但阶段未完全完成。 |
| `primary_goal_outcome` | 所选阶段主要结果完成、验证并写回。 |

这让 quota guard、review packet 与 dashboard 在一个连贯产物后保持真实，
而无需暴露原始证据。不要把这个决策编码进 `classification`；
classification 供人类索引，而 delivery outcome 是机器决策信号。

对新连接的只读项目，在构建自定义 adapter 前追加通用映射 run：

```bash
loopx read-only-map --goal-id project-goal
```

命令接受 adapter kind 为 `read_only_project_map_v0` 或兼容
`*_read_only_map_v0` 变体、且 adapter status 为已连接只读工作的目标。
它只检查 registry 元数据、active state 区块与有界文件存在性清单。
紧凑 run 索引记录 `classification=read_only_project_map`、本地控制面
`recommended_action`、产物可用性、映射计数与紧凑 `residual_risks`；
原始项目证据留在本地私有运行时 payload，而公共/导出槽在渲染可分享视图前
脱敏本地私有引用。

对计划中的高复杂度 adapter，`read-only-map --dry-run` 允许作为 opt-in 预览路径。
它返回 `opt_in_required=true` 且不追加任何内容，因此 controller 可在把 adapter
移到 `read-only-map-ready`、`connected-read-only` 或 `connected` 之前检查有界映射
形状。不带 `--dry-run` 运行同一命令直到该 opt-in 状态变化仍会失败。

在把 handoff 当作已批准前，把 operator 的回答记录为持久 gate 决策：

```bash
loopx operator-gate \
  --goal-id project-goal \
  --decision approve \
  --reason-summary "同意先执行 read-only map opt-in" \
  --dry-run
```

Dry-run 不写任何东西。真实追加创建 `operator_gate_approved`、
`operator_gate_rejected` 或 `operator_gate_deferred` 紧凑 run，带 JSON 与
Markdown 产物。批准使目标 Codex-ready 并暴露已批准的 `agent_command`；
拒绝/延迟保持目标 gate 并带记录理由。这把 operator gate 决策独立于
`human_reward` 记录，后者保留用于判断确切 run 或路线结局。

批准后，当唯余行动是转发目标项目 Agent 指令时，使用最小 handoff 形式：

```bash
loopx review-packet --goal-id project-goal --handoff-only
```

这仍是只读打包。它从 Markdown 输出剥离人类决策包装，
使接收 Agent 只看到目标 guard、转发条件、执行边界、停止条件与命令。
它不追加 gate 决策、刷新状态、花 quota、授予 write-control 或授权生产动作。

如果运行时目录属于不再在 registry 中的旧目标，在改动前先预览归档清理：

```bash
loopx archive-runtime --goal-id old-experiment-goal
```

命令默认 dry-run。评审后传 `--execute` 把目录移到
`<runtime-root>/archived-goals/`。仍在 registry 中的目标默认受保护；
归档一个需要显式 `--allow-registered` 标志。

## 人类奖励 Overlay

当 operator 判断一个 run 时，追加紧凑奖励 overlay，而不要手工编辑 run JSON：

```bash
loopx reward \
  --goal-id project-goal \
  --decision continue_route \
  --reward positive \
  --reason-summary "comparable validation improved and the route is worth extending" \
  --follow-up "promote to the next longer-window check"
```

默认命令把反馈附着到目标最新紧凑 run。传 `--run-generated-at <timestamp>`
定位更旧 run。Writer 把 JSONL overlay 追加到同一 `index.jsonl`；
它不改私有 run payload。`loopx status` 只导出紧凑 `human_reward` 字段，
所以原始证据应留在私有产物。

`loopx reward --dry-run` 与真实追加响应都包含两个协调字段：

- `active_state_summary`：operator 判断记录后 Codex 可复制进 active goal state
  的简短中文摘要。
- `project_agent_visibility`：另一个项目 Agent 找到奖励的标准方式，
  包括 `loopx history --goal-id ... --limit 3` 命令。

Run 绑定的 `human_reward` overlay 保持真相源。Active state 只是人类可读指针与
下一动作摘要；dashboard Review Packet 只是即时 handoff 产物。

对显式用户纠正，向同一 run 绑定 overlay 添加紧凑教训，而不是创建单独记忆存储：

```bash
loopx reward \
  --goal-id project-goal \
  --decision route_correction \
  --reward mixed \
  --reason-summary "fix lifecycle counters before adding more benchmark cases" \
  --lesson-kind benchmark_protocol \
  --lesson-summary "Do not expand cases until lifecycle counters are validated" \
  --lesson-avoid "expand cases before lifecycle counters" \
  --lesson-prefer "validate lifecycle counters first" \
  --write-active-state-summary
```

教训是建议性的。`loopx status` 在 `human_reward` 下暴露它，
`loopx quota should-run` 在未来 `recommended_action` 似乎与教训矛盾时警告。
它不授权写、不启动 benchmark、不替代正式 todo/Next Action 更新。

Markdown 输出包含 `Write Effect` 区块，在详细奖励字段前汇总所选 run、
run-overlay 写或预览状态、active-state 写回状态与项目 Agent 历史查找。

当 operator 显式批准记录奖励时，Codex 可以用一次 CLI 调用闭合持久 loop：

```bash
loopx reward \
  --goal-id project-goal \
  --decision continue_route \
  --reward positive \
  --reason-summary "comparable validation improved and the route is worth extending" \
  --follow-up "promote to the next longer-window check" \
  --write-active-state-summary
```

状态写是 opt-in。用 `--dry-run --write-active-state-summary`，命令报告
`active_state_update.would_write=true` 但不追加奖励 overlay 也不编辑 active state。
不加 `--write-active-state-summary`，命令只记录 run 绑定奖励 overlay。

## 首屏 Status

用 `loopx status` 作为下一次 controller tick 或 UI 刷新的入口：

```bash
loopx --format json status
loopx status --scan-path README.md --scan-path docs/
```

默认契约扫描使用 LoopX 安装根，因此从私有项目目录运行 status 不会意外扫描本地
`.local` 状态。只有当路径意图 public-safe 时，才为项目传 `--scan-root` 或
`--scan-path`。

对 React dashboard，通过 loopback HTTP 提供同一 status 契约：

```bash
loopx serve-status --global-registry --port 8766 --limit 80
```

然后从 dashboard 源码控制加载 `http://127.0.0.1:8766/status.json`。
`--global-registry` 即使在项目 checkout 内启动服务器也保持多项目 dashboard 在
共享 registry 上。对项目本地调试，省略该标志或传显式项目 `--registry`。
命令默认绑定 `127.0.0.1`，用于本地 operator dashboard，
不用于公共托管。

同一 loopback server 暴露 `POST /reward/dry-run`，使 dashboard 验证所选
goal/run 奖励草稿。Dry-run 响应紧凑，不追加 `index.jsonl`；
它为确切 goal/run/reward payload 与当前原始 index 计数返回 `preview_id`。

直接 dashboard 奖励提交是显式 opt-in 能力。用 `--enable-reward-write-api`
启动 status server，只在 loopback 暴露 `POST /reward/append`。Dashboard 随后
可以提交 dry-run `preview_id`；成功追加写入一个 run 绑定 `human_reward` overlay
并刷新 status，使未来项目 Agent 通过 `loopx status` 或 `loopx history` 发现反馈。

Status 命令把契约健康与 run history 组合成 attention queue。每个队列条目说明
哪个目标需要关注、它在等谁、条目多严重，以及一个推荐动作。

对 dashboard、heartbeat 摘要或任何读取 JSON 输出的脚本，
使用 [status 数据契约](status-data-contract.md)。

Adapter 输出在进入紧凑索引前保持脱敏。Status 队列用于控制面显示，
不用作原始私有证据。

## 公共仓库 vs 项目仓库

通用代码放这里：

- registry 与 history 读取器，
- 契约检查器，
- 通用 schema 与文档，
- 脱敏 adapter 示例，
- peer 任务与临时 worker 生命周期示例。

项目仓库保留：

- 项目特定 adapter 代码，
- 活跃目标状态，
- 私有 registry，
- 领域特定健康检查。

这个拆分让许多本地项目共享一个稳定 LoopX 基座，
同时把真实证据与安全策略留在本地。
