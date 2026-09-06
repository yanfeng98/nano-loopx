# Issue/PR Solver Maintainer 摄入 Packet


本 packet 帮助 LoopX maintainer 决定外部或伙伴 issue/PR solver 是否应成为高价值证明锚点。Solver 可以在 LoopX 之外。LoopX 的职责是让 maintainer 决策、边界、evidence 与 showcase 路径显式。

该 packet 刻意在执行前。它不授权读取私有源码、生成 patch、推送分支、发布评论、发布 artifacts 或声称 benchmark 提升。它把 issue/PR solver 机会变成可评审的 LoopX 状态。

## 何时使用

在以下情况使用 `issue_pr_solver_maintainer_intake_v0`：

- maintainer 正在考虑把某仓库、issue 或 PR 当作公开证明锚点；
- 伙伴 solver 或宿主产品可能做实现工作；
- LoopX 需要跟踪 owner 路由、允许动作、evidence 与 showcase 毕业；
- 该机会还不是正常 agent todo，因为契合度、同意或边界不清晰。

不要把它用于普通本地 bug 修复、私有客户工作、benchmark 任务、生产事故，或任何 public/private 边界不清晰的仓库。

## Packet 形态

```yaml
issue_pr_solver_maintainer_intake_v0:
  candidate:
    repo_handle: "owner/repo or public-safe alias"
    issue_or_pr_handle: "optional public issue or PR id"
    source_status: public | needs_review | private | forbidden
    freshness: fresh | stale | unknown
  repo_fit:
    task_type: bug | docs | test | small_feature | triage | unknown
    expected_user_value: low | medium | high
    reproduction_clarity: clear | partial | missing
    maintainer_interest: confirmed | likely | unknown | rejected
    anchor_reason: "Why this is worth considering as a proof path."
  allowed_actions:
    observe: true
    triage: true
    reproduce: false
    draft_plan: false
    prepare_patch: false
    open_pr: false
    post_comment: false
  owner_routing:
    maintainer_contact: "public-safe handle or channel label"
    route_owner: "human | registered_peer | partner_solver | unknown"
    review_required_before: ["patch", "public_comment", "showcase"]
  evidence_boundary:
    allowed_evidence:
      - issue handle
      - patch summary
      - CI status
      - maintainer review outcome
    forbidden_evidence:
      - unredacted runtime material
      - unpublished source context
      - sensitive local paths
  stop_conditions:
    - source boundary unclear
    - maintainer interest rejected
    - patch would require protected write scope
    - validation cannot be represented compactly
  showcase_consent:
    status: not_requested | requested | approved | rejected
    allowed_surface: none | anonymized_card | public_case | launch_material
```

字段刻意小到能塞进管理卡。真实 adapter 可以存更多内部细节，但公开 LoopX 状态应只保留紧凑 handle、标签与 evidence 指针。

## 契合度检查清单

当多数回答为正面时，候选是好的公开锚点：

- issue 或 PR 公开且足够稳定，可以按 handle 引用；
- 任务小到足以进行有边界 solver 尝试；
- 预期用户价值容易解释；
- 复现或验证可以不经私有资料检查；
- maintainer 或仓库 owner 有清晰评审路由；
- 结果能产生可见信号：已合并 PR、带有用理由的拒绝 patch、已接受计划、CI 结果或已记录 blocker；
- 案例展示 LoopX 管理价值，而不只是原始 solver 能力。

当以下情况时，候选应保持为信号而非锚点：

- 它需要广泛仓库所有权或受保护生产动作；
- 它主要测试模型编码能力而没有长程控制面价值；
- owner 路由缺失；
- 唯一可能的 evidence 将是未脱敏 runtime 资料、私有轨迹或私有源码资料；
- showcase 同意未知，且案例无法安全匿名化。

## 允许动作梯级

允许动作应从窄开始并显式晋升：

| 级别 | 允许动作 | 晋升 evidence |
| --- | --- | --- |
| Observe | 记录公开 handle、labels、来源状态与新鲜度 | 来源边界清晰 |
| Triage | 分类任务类型、用户价值、owner 路由与首个验证 | Maintainer 契合度合理 |
| Reproduce | 运行或描述紧凑验证 surface | 验证可以保持 public-safe |
| Draft plan | 不改源码提议 patch scope 与风险 | Owner 评审路径存在 |
| Prepare patch | 在批准 workspace 创建本地 patch 或分支 | 写范围与评审 gate 获批准 |
| Open PR / comment | 外部发布 | 显式 maintainer 与发布 gates 获批准 |
| Showcase | 把成果变成卡或案例 | Showcase 同意获批准或匿名化安全 |

默认级别是 Observe。每个更高级别都必须作为 gate、todo 更新或评审事件可见。

## LoopX 写回

摄入可以产生几个正常 LoopX 对象：

- 未选中机会的 `signal_v0`；
- 选中证明路径的 `anchor_v0`；
- 用于分诊、验证或交接的 agent todo；
- 用于 maintainer 批准或同意的 user todo；
- 用于接受/拒绝候选决策的 `review_event_v0`；
- 用于 owner 纠正或路由变更的 `feedback_signal_v0`；
- 只在同意与边界检查后的 showcase 卡。

LoopX 不应把每个公开 issue 当作待办。Maintainer 选少数锚点；其余保持为可搜索信号或被归档。

## 验收标准

Maintainer 摄入成功当：

- repo/issue/PR handle、来源状态与新鲜度显式；
- 允许动作可见且默认从 Observe 开始；
- owner 路由命名谁必须评审 patch、评论或 showcase 步骤；
- evidence 边界说明什么可以存储或显示、什么不可以；
- 停止条件具体到 agent 无需猜测就能停止；
- showcase 同意与实现成功分离；
- 选中候选晋升为正常 LoopX todos、gates 或锚点，而不是只留在聊天里。

这让开源 PR 驱动增长对齐核心 LoopX 承诺：选高价值锚点、保持人类控制，并让 solver 工作凭 evidence 而非炒作可评审。
