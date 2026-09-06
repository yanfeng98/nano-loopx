# Issue/PR Solver 锚点协调

> [English](issue-pr-solver-anchor-coordination.md)

本说明定义 maintainer 摄入之后 LoopX 如何协调一个选中的公开 issue/PR solver 锚点。Solver 可以是伙伴工具、人类贡献者或未来 LoopX 管理的 worker。LoopX 的角色不是认领每个 issue。它的角色是保持锚点有价值、有边界、可度量，并且安全到足以成为产品 evidence。

在
[`issue_pr_solver_maintainer_intake_v0`](issue-pr-solver-maintainer-intake.md)
选中某个候选作为高价值锚点之后使用本说明。

## 为什么存在

Issue/PR 求解只有展示出超越原始编码能力时才是有用的证明路径。一个好锚点应显示 LoopX 能帮助 maintainer：

- 选择值得的仓库或 issue；
- 保持所有权与发布 gates 显式；
- 把零散的 solver 活动变成紧凑 evidence；
- 对照成本与人类注意力比较有用成果；
- 决定案例是否毕业进入 onboarding、showcase 或产品工作。

这使 issue/PR solver 泳道成为 LoopX 管理 surface 的次级价值证明：maintainer 可以看到发生了什么、花了什么成本、哪里需要人类判断，以及下一个锚点是否应改变。

## 协调 Packet

```yaml
issue_pr_solver_anchor_coordination_v0:
  anchor:
    anchor_id: "stable public-safe id"
    repo_handle: "owner/repo or public-safe alias"
    issue_or_pr_handle: "public issue or PR id"
    intake_ref: "issue_pr_solver_maintainer_intake_v0 handle"
    objective: "what useful maintainer outcome this anchor should test"
  owner_split:
    loopx_maintainer:
      owns:
        - anchor selection
        - boundary policy
        - metric board
        - showcase graduation
    partner_solver:
      owns:
        - solver execution proposal
        - implementation attempt when authorized
        - compact result handoff
    repo_maintainer:
      owns:
        - repository review decision
        - public comment or PR acceptance
        - merge or rejection outcome
    human_reviewer:
      owns:
        - value score
        - quality score
        - attention-cost feedback
  allowed_actions:
    current_level: observe | triage | reproduce | draft_plan | prepare_patch | publish | showcase
    next_gate: source_boundary | owner_route | validation | publish | showcase | none
  evidence_boundary:
    allowed:
      - public issue or PR handle
      - task label and owner route
      - compact reproduction result
      - patch summary
      - CI or review status
      - maintainer outcome
      - reviewer score
    forbidden:
      - private source context
      - credentials
      - unpublished maintainer messages
      - raw runtime traces
      - sensitive local paths
  metric_board:
    usefulness:
      selected_anchor_count: 0
      useful_outcome_count: 0
      accepted_or_advanced_count: 0
    quality:
      validation_passed_count: 0
      reviewer_quality_score: null
      boundary_incident_count: 0
    cost:
      token_or_runtime_cost: null
      human_attention_minutes: null
      iteration_count: 0
    learning:
      feedback_signal_count: 0
      next_anchor_change: "keep | narrow | broaden | stop"
  human_gates:
    - source boundary unclear
    - partner solver wants to write code
    - external comment or PR would be published
    - showcase consent is missing
    - reviewer score changes the next anchor strategy
  graduation:
    status: signal | selected_anchor | pilot_running | result_review | case_catalog | showcase | archived
    graduation_condition: "what must be true before the next status"
    stop_condition: "what makes this anchor no longer worth pursuing"
```

## 种子工作流

1. **收集信号。** 把原始候选当作可搜索信号，而不是 todos。来源可以包括 GitHub issues、maintainer 请求、伙伴 solver 建议、用户对话或 operator 说明。
2. **运行 maintainer 摄入。** 用摄入 packet 决定候选是否值得成为锚点。
3. **选一个小型锚点集。** 偏好一到三个带清晰用户价值、公开 evidence 与可达 owner 路由的锚点。
4. **设定允许动作级别。** 从 Observe 或 Triage 开始。只在下一个人类 gate 通过后晋升。
5. **交接给 solver。** 只给 solver 已批准的 handle、目标、允许动作、验证 surface 与停止条件。
6. **摄入紧凑 evidence。** 存储结果标签、验证状态、评审结果与成本信号。不存储私有 transcript 或原始 runtime 资料。
7. **像工作输出一样评审。** 人类评审者对价值、质量、成本与注意力评分。分数改变未来锚点选择。
8. **毕业或归档。** 有用的公开成果可以成为 case-catalog 条目或 showcase 卡。嘈杂或危险的锚点应归档，并让理由可见。

## 指标板

不要为原始 issue 数或原始 PR 数优化。这些容易夸大，且不能证明长程 agent 可管理。

第一个有用的板应跟踪：

- **选中的锚点：** 多少候选通过 maintainer 摄入。
- **有用成果：** 已合并 PR、已接受计划、明确 maintainer 拒绝、已复现 bug、已验证 blocker 或产品洞察。
- **质量：** 验证结果、评审者分数，以及 solver 是否留在边界内。
- **成本：** token/runtime 成本、迭代次数与人类注意力分钟数。
- **学习：** 什么反馈改变了下一次锚点选择。

这与更广的 Loop Agent reward 模型一致：

```text
value = f(quantity, quality, token/runtime cost, human attention cost)
```

## 人类 Gates

每个锚点应暴露具体 gates，而不是泛化"owner gate"：

- **来源边界 gate：** issue、代码与 evidence 能否公开或紧凑处理？
- **Solver 自主 gate：** 伙伴 solver 能否从观察移动到复现、计划或准备代码？
- **发布 gate：** 是否允许任何人发评论、开 PR 或发布分支？
- **Showcase gate：** 成果能否在发布资料中被命名、匿名化或复用？
- **评审 gate：** 人类反馈是说继续、收窄、扩宽还是停止该锚点类别？

当 gate 阻塞进展时，把它写成带所需具体决策的 user todo。当 gate 解决时，把决策记录为紧凑 evidence。

## 毕业路径

锚点应经过显式状态：

| 状态 | 含义 | 下一条件 |
| --- | --- | --- |
| Signal | 候选存在，未选中 | maintainer 摄入说值得测试 |
| Selected anchor | 边界与 owner 路由合理 | 允许动作级别与 solver 交接就绪 |
| Pilot running | Solver 在批准动作内工作 | 紧凑结果或 blocker 到达 |
| Result review | 人类评审价值、质量、成本与注意力 | 记录分数与下一锚点决策 |
| Case catalog | 结果内部或公开可复用 | 同意与边界允许发布 |
| Showcase | 案例可以教 LoopX 的产品价值 | 公开卡或 demo 文案获批准 |
| Archived | 案例不再有用或不安全 | 理由对未来选择可见 |

毕业不是自动的。如果 evidence 是私有的、价值难以解释或人类注意力成本太高，已解决的 issue 仍可能无法通过 showcase 毕业。

## LoopX 写回

协调泳道应写入正常 LoopX 对象：

- 一个选中的 `anchor_v0` 或信号归档决策；
- 一个用于 solver 交接、evidence 摄入或 case-catalog 起草的 agent todo；
- 一个用于来源、发布或 showcase gates 的 user todo；
- 一个带价值、质量、成本与注意力反馈的 `review_event_v0`；
- 一个紧凑指标板更新；
- 只在同意后的 case-catalog 或 showcase todo。

对第一个仓库本地投影，活跃状态也可以包含一个紧凑 `## Issue Meta Surface` 区块。`loopx status` 把每个 public-safe 键值 bullet 提升到 `issue_meta_surface_v0`，并镜像到 `project_asset.issue_meta_surface` 下：

```md
## Issue Meta Surface

- anchor_id=issue_anchor_parser_bug repo=sample-org/sample-repo issue=#128 labels=bug,good-first-issue owner_route=repo_maintainer_review related_code=src/parser.py validation=unit_smoke promotion_target=agent_todo:todo_issue_fix status=selected_anchor freshness=fresh
```

这是 issue/PR 锚点选择的小状态面。它让 labels、owner 路由、相关代码提示、验证 surface 与晋升目标对 agent 与 dashboards 可见，而不存储 issue 正文、私有来源上下文、原始 solver 轨迹或发布权限。

这让开源 PR 驱动增长连接 LoopX 的核心承诺：长程 agent 工作应可选、有边界、可评审，并通过人类反馈改进。
