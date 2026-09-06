# issue_fix_workflow_contract_v0

> [English](issue-fix-workflow-contract-v0.md)

`issue_fix_workflow_contract_v0` 把现有 issue-fix surfaces 串成一套 GitHub
issue fix workflow。它是产品契约,不是新的状态存储:LoopX 仍使用元数据预览、
intake packets、LoopX todos、caller 批准的仓库分支、校验证据、review packets
与显式 gates 作为事实源。

## 用户故事

用户给 LoopX 一个公开 GitHub issue 或 PR 信号,以及一个已批准的本地仓库上下文。
LoopX 应分类 issue,把工作分解成 owner/user gates 与 agent todos,准备或认领
issue 分支,运行声明的校验,并发出 PR-review-ready packet。LoopX 不得读取 raw
issue 正文、raw 评论、私有复现材料,不得在没有显式 gate 时创建外部评论、开 PR、
merge、publish 或运行破坏性 git。

## 工作流阶段

1. **候选 preflight:**在投影 patch-planning 工作前,对账既有 issue-fix 领域
   状态、all-state closing PR 引用、交叉引用与维护者评论元数据。没有源证据时,
   准入是 `evidence_required`,最终路由缺失,候选不可运行。
   每个 PR 证据字段是 issue 特定的查询 receipt,携带 `repo`、`issue_ref`、
   `query_scope`、`complete`、`truncated` 与 `rows`。每个字段接受一个 receipt
   对象,而不是列表:`numeric_pr_evidence.query_scope` 是
   `issue_specific_all_states`,`semantic_pr_evidence.query_scope` 是
   `issue_specific_current_revision`,`maintainer_comment_evidence.query_scope`
   是 `issue_specific_comment_metadata`。空 rows 只对完整、非截断的 receipt
   有效。每个返回行必须可解析且 issue-scoped;格式错误行使 receipt 失效,而不是
   消失成假阴性。
   `--fetch-candidate-evidence` 调用有界的内置公开 GitHub collector;
   `--candidate-preflight-json` 仍是 provider-neutral 适配器/测试接缝。准入是
   `evidence_required`、`verification_required`、`admitted` 或 `terminal`;只有
   最终准入暴露 `proceed`、`reuse_existing_pr`、`comment_only` 或 `skip`。
   交叉引用、关闭 PRs 与维护者评论投影 typed successors,而不是伪装成最终
   `comment_only`。
   `issue_fix_candidate_resolution_v0` 是单个紧凑解析输入:每一行必须匹配当前
   源证据。PR 解析绑定确切 head revision,维护者评论解析绑定评论 `updatedAt`
   revision。因此变化的源使过期解析失效。评论内容留在 provider-content gate
   后面,只有其紧凑处置可以进入解析 receipt。
2. **元数据预览:**从公开 URL、紧凑引用、模拟元数据或 caller 批准的元数据
   fetch 构建 `github_issue_metadata_preview_v0`。允许的字段是 repo、issue 或
   PR 编号、状态、标题摘要、labels、更新时间戳、author association、评论计数与
   permalink。Body、comment、timeline、event、raw 与 provider 响应字段被 gate。
3. **Intake 分类:**构建带 issue class、code-context 路由候选、owner/user gate
   投影与有序 agent todo 候选的 `issue_fix_intake_v0`。第一屏必须点名
   `waiting_on`、最高 agent todo、存在时的最高 gate,以及下一个安全动作。
4. **仓库上下文:**从 pinned repository revision 加紧凑源 refs 构建
   `issue_fix_repository_context_v0`。当前权威或已验证的仓库证据可以为
   change scope、reproduction 与 validation 提供依据。陈旧记忆与外部专家保持
   advisory。上下文投影缺失读取,但不引入另一个生命周期状态、不授权外部写,
   也不覆盖 feasibility 路由。
5. **Workflow plan:**构建 `issue_fix_workflow_plan_packet_v0`,组合元数据预览、
   intake、分支 dry-run、校验标签、有序 LoopX todo 回写预览、解析路由候选、
   gate 预览、post-PR 生命周期 monitor 计划与 PR-review 就绪度 blockers。该
   阶段不写 todos。只有在存在 goal id 或显式 ledger 路径时,它才写候选 preflight
   receipt;`--no-write-domain-state` 使该 receipt 仅预览。
6. **Feasibility 检查点:**只在候选 preflight 返回 `proceed` 后,从紧凑
   public-safe agent 观测构建 `issue_fix_feasibility_v0`。决策必须恰好选择
   `fix_pr`、`comment_only` 或 `triage_only` 一条路由。`fix_pr` 要求有界 scope
   加命名的 reproduction 与 validation surfaces;计划中的 reproduction 在 patch
   工作前投影确认工作。带 goal id 时,紧凑决策默认写入 issue-fix 领域状态。
7. **LoopX todo 回写:**对非 proceed 候选,只写候选 preflight 投影的 successor
   或 no-follow-up。对 `proceed`,写 feasibility 投影的单一路由特定 successor。
   保留优先级与规划顺序。用户 todos 代表具体的外部写、私有材料、merge、
   publish 或仓库 policy gates。
8. **Caller 仓库分支:**只在 caller 提供已批准本地 git 仓库、base branch、issue
   分支 policy 与校验命令后,使用 `issue_fix_caller_repo_branch_packet_v0`。
   Dry-run 模式不得检查仓库。Execute 模式可以检查已批准仓库并创建或认领
   `codex/` issue 分支,但必须拒绝从脏状态切换分支。
9. **校验:**把聚焦校验记录为通过/失败、退出码与 public-safe 标签。校验
   stdout、stderr、本地路径与 raw git 输出保持在 packet 之外。已验证修复应在
   该复现路径可用时证明 failing-before 与 passing-after 证据。当 delivery 指名
   commit 并报告 `passed` 或 `completed` 时,回写必须在 caller 批准 checkout 中
   解析声明的仓库 revision 与 commit,证明 commit 祖先关系,并保留带匹配仓库
   fingerprint 与完整可恢复 branch、tag 或 remote ref 的
   `issue_fix_repository_commit_evidence_v0`。缺失或过期 commit 证明在状态变更前
   失败;遗留未证明行投影为 `unverified`,而不是 publication-ready。
10. **PR review packet:**只在分支、校验与 repo-relative 变更文件证据足以供
    人工审查时,发出 `issue_fix_pr_review_packet_v0`。其
    `issue_fix_pr_description_contract_v0` 保持 PR-review 的动机/思路/改动/
    校验/风险结构,代码变更要求紧凑关键代码或伪代码段,适用时要求修复后仓库
    CLI 或聚焦代码/测试复现。可选 infographics 限于复杂变更,不能替代文本证据。
    Issue 支持的变更在语义偏好重写之后添加一个功能引用块:完整修复针对默认
    分支用 `Fixes #N`,部分工作用 `Related to #N`。每个 issue 使用完整语法,并
    通过 GitHub `closingIssuesReferences` 验证 closing references。Packet 是
    review 证据,不是外部发布 authority。
11. **PR 生命周期 monitor:**PR 存在后,用 `issue_fix_pr_lifecycle_monitor_v0`
    把紧凑公开 PR 状态投影成 `runnable_successor`、`monitor_continuation`、
    `user_gate` 或 `no_followup` 之一。`MERGED`、`CLOSED` 等 terminal PR 状态
    优先于过期 review 元数据。失败的 checks、请求的 changes 与过期的 merge
    状态创建 runnable successors,而不是 `monitor_quiet_skip`。提供 `--goal-id`
    或 `--ledger-path` 时命令默认写入紧凑领域状态,`--no-write-domain-state`
    使其仅预览。持久化的 lifecycle 状态应携带显式 public-safe `issue_ref`;
    `#123`、`issue_123`、`issues/123` 等数字别名在写入前 canonicalize 为
    `issues_123`。Outcome 投影对遗留行应用同一规则,但不得从分支名、PR 标题或
    散文推断 issue。其 `issue_fix_pr_grouped_monitor_projection_v1` 把每个开放
    PR 分配到仓库生命周期状态桶。为每个非空桶物化至多一个
    `continuous_monitor`,状态变化时 upsert/移除 PR 成员,并完成空桶。绝不每个
    PR 创建一个 monitor。Material PR 工作保持为一次性推进 todo,reviewer 通知
    保持一个消息一个 PR。`pr-lifecycle --execute-transition --goal-id <goal>
    --claimed-by <agent>` 通过通用 todo API 执行该对账;`--monitor-cadence`
    控制调度,默认 `30m`。桶成员不变的安静重放是幂等的。之后的 cadence 推进由
    monitor poll lane 拥有,而不是重复的 PR lifecycle 执行。创建它的 issue-fix
    agent 保持为 monitor 跨 turn 的 `claimed_by` owner;另一个 peer 没有显式
    Todo lifecycle authority 不能更新、退役、重开或轮询该 monitor。
    带公开 PR URL 时,`--execute-transition` 自动 fetch 紧凑公开元数据,除非
    `--metadata-json` 提供确定性 fixture。
12. **Gate 处理:**暴露具体 gates,而不是静默阻塞。当那些 gates 不覆盖所选动作
    时,安全 metadata-only triage、公开代码搜索与聚焦 smoke 草稿可以继续。
13. **Outcome 投影:**用 `issue_fix_outcome_projection_v0` 从现有 feasibility
    行、仓库上下文、可选 `issue_fix_delivery_evidence_input_v0` 与可选 PR
    lifecycle 行派生一个稳定的面向运维者 case。该投影不写源状态,也不创建并行
    工作流状态机。它必须把未知投递证据保持显式,保留 terminal 输出,只派生有界
    public-safe `context_tags`,并保持通用投影 sinks 可消费。
    默认 goal 级 Kanban sync 在 upsert issue outcome 卡前,从所有 feasibility
    行与显式链接的 lifecycle 行派生
    `issue_fix_outcome_collection_projection_v0`。

## 公共安全边界

该工作流中的 packets 必须保留这些边界标志:

- `issue_body_captured: false`
- `comment_bodies_captured: false`
- `response_payload_captured` 或 `response_payloads_captured: false`
- `local_paths_captured: false`
- `external_writes_performed: false`
- `destructive_git_used: false`

`private_repo_state_read` 对 preview、intake、fixtures 与 caller-repo
dry-runs 为 `false`。只有在 caller 批准的 `caller-repo-branch --execute` 中才
可为 `true`,即使如此,本地路径、raw 校验输出、raw git 输出与凭据也不得被记录。

## Todo 与 Gate 形状

Issue-fix todo 计划应小而有序。对于清晰的有界 bug,使用最小充分计划,而不是
管理填充:

- `[P0] 从公开 metadata 与已批准代码上下文复现或分类 issue。`
- `[P0] 给选中的 issue 分支打补丁,并重新运行 caller 声明的校验。`
- `[P1] 用 repo-relative 变更文件、校验标签与剩余 gates 准备 PR review packet。`
- `[P2] 监控 PR lifecycle,把 CI、review、merge 或 stale-branch 变化投影为
  successor、gate、continuation 或 no-follow-up。`

当多个 todos 有相同优先级时,planner 顺序加 LoopX 写入顺序是决胜项。不要仅从
散文推断 gate:把它写成携带其阻塞的具体动作的用户 todo 或 operator gate。

解析路由必须保持显式。`fix_pr` 只在有聚焦 repro 或校验计划时适用。
`comment_only` 应产生 public-safe 维护者评论 packet,但仍需要显式外部写 gate。
`triage_only` 在 issue 缺乏足够公开证据支持有用 patch 或评论时有效。

## 领域状态

Issue-fix 领域状态是紧凑决策与长程 monitor 的项目本地读取模型:

```text
.loopx/domain-state/<goal-id>/issue_fix/candidate-preflight.jsonl
.loopx/domain-state/<goal-id>/issue_fix/feasibility.jsonl
.loopx/domain-state/<goal-id>/issue_fix/pr-lifecycle.jsonl
```

候选 preflight 与 feasibility 行以 `repo` 与 `issue_ref` 为键;PR lifecycle 行
以 `repo` 与 `pr_ref` 为键。它们可以存储紧凑观测、决策与 fingerprints。候选
preflight 保留决定 feasibility 是否合法的源 receipts 与先前处置。Feasibility
观测可以包含一个紧凑 `issue_fix_repository_context_v0` 投影,使其仓库 revision、
源 refs、覆盖、专家 policy 与记忆 policy 跨 turn 存活。领域状态不得存储 issue
正文、评论正文、raw provider payloads、raw 日志、本地路径、凭据或破坏性 git
输出。公开 packet 校验仍是行为契约;领域状态只是防止 agent 忘记其最新紧凑决策。

## 就绪标准

只有以下全部为 true 时,issue-fix workflow 才是 PR-review-ready:

- metadata/intake 保持无正文、无评论边界;
- 已接受的 todos 或 gates 被写入 LoopX 状态,而不是留在聊天里;
- issue 分支在 caller 批准仓库内创建或认领;
- 声明的校验运行并通过,或 packet 明确说 review 尚未就绪;
- 变更文件 repo-relative 且有界;
- 没有发生外部 issue 评论、PR 创建、merge、publish、生产动作或破坏性 git 动作。

`issue_fix_workflow_plan_packet_v0` 还投影带已接受顶层/源字段与最小示例的
`repository_context_input_contract`。Hosts 应从该契约构建 feasibility 输入,而
不是复制归一化 `issue_fix_repository_context_v0` 输出形状。

## 相关 Schemas

- `github_issue_metadata_preview_v0`
- `content_ops_issue_fix_metadata_preview_packet_v0`
- `content_ops_issue_fix_intake_packet_v0`
- `issue_fix_intake_v0`
- `issue_fix_workflow_plan_packet_v0`
- `issue_fix_candidate_preflight_v0`
- `issue_fix_candidate_resolution_v0`
- `issue_fix_candidate_successor_v0`
- `issue_fix_candidate_preflight_domain_state_projection_v0`
- `issue_fix_repository_context_input_v0`
- `issue_fix_repository_context_v0`
- `issue_fix_repository_context_effect_v0`
- `issue_fix_feasibility_v0`
- `issue_fix_feasibility_observation_v0`
- `issue_fix_feasibility_decision_v0`
- `issue_fix_feasibility_domain_state_projection_v0`
- `issue_fix_pr_lifecycle_monitor_v0`
- `issue_fix_pr_grouped_monitor_projection_v1`
- `issue_fix_pr_lifecycle_transition_v0`
- `issue_fix_pr_lifecycle_domain_state_projection_v0`
- `issue_fix_delivery_evidence_input_v0`
- `issue_fix_repository_commit_evidence_v0`
- `issue_fix_outcome_case_v0`
- `issue_fix_outcome_projection_v0`
- `issue_fix_outcome_collection_projection_v0`
- `loopx_todo_writeback_preview_v0`
- `issue_fix_caller_repo_branch_packet_v0`
- `issue_fix_validated_fix_artifact_v0`
- `issue_fix_pr_review_packet_v0`
