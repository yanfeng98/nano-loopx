# Pull Request Review

`pull-request-review` capability 帮助用户逐个审阅开放与最近合并的 pull requests:
把公开 GitHub PR 元数据变成引导式 review 队列。其命令 packet 仍以
`pr_review_command_v0` 版本化,并通过 `/loopx-pr-review` 与 `loopx pr-review`
暴露。

默认被审阅仓库是由 `gh` 解析的调用方当前 GitHub 项目,或显式 `--repo owner/repo`
目标。LoopX 自己的仓库可以用于 dogfood 与公开 fixtures,但命令不是
LoopX-repo 特定的。

默认命令是只读的。显式 `--observation-state-file` 只写其本地 public-safe
checkpoint。两种模式都不批准 reviews、不发 PR 评论、不 merge、不 push、不消耗
LoopX quota,也不完成 LoopX todos。

内置 `pull-request-review` capability 为同一命令添加可选自主观测。它复用现有
GitHub 扫描与归一化 review 队列;不引入第二个 crawler 或新的写 authority。

Capability 还拥有 review-depth 契约。共享的
`agent_response_contract.review_execution_contract` 定义必需证据、完成、
freshness、finding 与 verdict 规则。每个 PR 携带把那些规则绑定到一个确切 head 的
紧凑 `review_plan`,并标记 code-symbol 与 negative-walkthrough 适用性。Host
skills 路由并发布该 packet;它们不得维护第二份解释清单。

Codex agents 应为该 slash command 使用专用 `loopx-pr-review` skill。不要把
`/loopx-pr-review` 路由到更宽的 `loopx-project` workflow 或以 merge 为重点的
`loopx-pr-merge` skill。

## 命令

| 命令 | CLI 参考 | 意图 |
| --- | --- | --- |
| `/loopx-pr-review` | `loopx pr-review [--repo owner/repo] [--state open\|merged\|all] [--since ISO]` | 列出当前项目或显式仓库的 open 与 merged PRs,为每个 PR 提供具体的 main-regression 分析,并包含 agentloop 读取所选 PR body/diff 后填写的空五块模板。 |

Slash command 必须先运行 CLI。Agentloop 不得通过为每个 PR 手动调用
`gh pr view` / `gh pr list` 重建 review 窗口。CLI packet 的
`review_groups.unmerged`、`review_groups.merged` 与
`pull_requests[].review_template` 是权威队列。Packet 的 `evidence_commands` 用于
第二步:深入读取一个选中的 PR。第一遍使用 JSON 形式,使响应契约与每个 PR 的空
模板进入 model context:

```bash
loopx --format json pr-review --state all [--repo owner/repo] [--since ISO]
```

对于自主维护者 monitor,在忽略的本地 checkpoint 中持久化其紧凑游标,同时请求
完整开放队列:

```bash
loopx --format json pr-review --repo owner/repo --state open \
  --autonomous-observation \
  --observation-state-file .local/pr-review-monitor.json
```

同一命令在之后的 Codex 任务中复用该 checkpoint。其原子本地写不授予 GitHub、
Todo、push 或 merge authority。
`--previous-observation-json` 对无状态调用方仍可用,与
`--observation-state-file` 互斥:

```bash
loopx --format json pr-review --repo owner/repo --state open \
  --autonomous-observation \
  --previous-observation-json previous.json
```

在选中的候选被持久物化为 Todo 后,显式确认该投影:

```bash
loopx --format json pr-review --repo owner/repo --state open \
  --autonomous-observation \
  --observation-state-file .local/pr-review-monitor.json \
  --projected-exact-head 2768@0123456789abcdef0123456789abcdef01234567
```

只在候选的确切目标 key 持久物化为 Todo 后才提供 `--projected-exact-head`。
候选发出是预览,不是投影确认。没有该显式 ACK,重复的完整 poll 会重放同一候选,
使失败或中断的 Todo 写入不会搁浅 PR。该选项可重复,且只能确认先前候选或已持久化
投影游标。

在选中候选于该确切 head 上有外部可验证 review 或 merge 就绪结果后,用显式
handled 游标推进队列:

```bash
loopx --format json pr-review --repo owner/repo --state open \
  --autonomous-observation \
  --observation-state-file .local/pr-review-monitor.json \
  --handled-exact-head 2768@0123456789abcdef0123456789abcdef01234567
```

`--handled-exact-head` 可重复,使用 `NUMBER@HEAD_OID`。Observation 在
`handled_exact_heads` 中持久化这些 public-safe 游标。候选发出本身不是完成 receipt:
调用方必须在 review-result readback 证明该确切 head 已处理后才添加游标。新提供的
游标必须匹配先前 packet 的候选或其 `projected_candidate_exact_heads` 之一;
调用方不能通过点名某 PR 为 handled 来跳过未选中的 PR。即使先前 head 已处理,
新 head 也是新候选。

`pending_candidate_exact_head` 在未变与不完整 polls 中保留最后一个已选但未处理
的确切 head。它只是调度游标;调用方仍按确切目标 key 去重 Todo 创建,且不得把
游标当作 review 已发生的证据。

`projected_candidate_exact_heads` 持久化每个持久 Todo 投影被显式确认但尚未完成
的候选。未变 poll 跳过那些已确认的确切 heads,在年龄公平的 review 序列中选择下
一个未投影、未处理的 PR。遗留 v0 observations 把发出当作投影;v1 刻意重放它们的
候选,因此过期发出游标不能搁浅未审阅 PRs。Todo 目标 key 去重保持该恢复幂等。
当每个可操作 PR 都已投影,`candidate` 为 `None`,`pending_candidate_exact_head`
保持最后一个待决游标。已投影确切 head 上的 material 转换仍重新选中该 head。

`review_backlog` 给 monitor 紧凑的工作负载 cadence 提示。它计数 open、非 draft
且确切 head 可操作、尚未记录在 `handled_exact_heads` 中的 PRs,并返回
`recommended_poll_interval_minutes`。只要还有一个未处理 PR,推荐为 `3`;当可操作
积压为空时降到 `15`。该提示仅是调度证据:它不授予 Todo、review、comment 或 merge
authority,调用方仍要在确切 head review readback 后用显式 handled 游标推进队列。

`pull_request_review_queue_observation_v1` 恰好有三个观测状态:

- `not_observed`:源或 packet 分片不完整。保留先前 baseline,不断言队列未变。
- `observed_unchanged`:完整观测有相同队列 fingerprint。未确认的 packet 候选被
  重放。调用方提供投影 ACK 后,packet 选择下一个未投影、未处理的积压 PR,使队列
  持续轮转。已确认的未处理候选保留在 `projected_candidate_exact_heads` 中,直到
  调用方提供其完成游标。
- `material_transition`:完整观测改变了确切 head、review 结论、check 状态、draft
  状态、mergeability 或开放队列成员。`REQUEST_CHANGES` 后的新 head 可以使用一个
  fast-feedback slot;仅 check 活动不抢占更老的 review-ready 工作。

Repository-scoped fingerprint 只包含紧凑公开 PR 元数据。持久化 `items` 携带 PR
编号、fingerprint、确切 head、决策与下一动作;它们从不携带 review 正文。
`REQUEST_CHANGES` 后的一次社区响应 head 可以走 fast-feedback lane,然后社区工作
按当前 head `review_ready_at` 的最旧优先。Author 自有 fallback reviews 跟在社区
工作之后,24 小时与 48 小时老化 lane 防止饥饿。`updatedAt` 不定义就绪度,因为
评论与 checks 不能让旧代码看似全新。已投影候选保持跳过,直到处理或其确切 head
material 变化。
它发出绑定其确切 head 的 `pull_request_review_todo_preview_v0`。Preview 可以路由
到初次 review、变更后重新 review 或 merge-readiness 资格判定。它不授予 Todo 写、
GitHub review/comment、push 或 merge authority;调用方必须对这些动作使用正常
LoopX Todo authority、`loopx-pr-review` 与 `loopx-pr-merge` policy。

不要把第一个 packet 通过 `jq` 或另一个只保留 `.summary` 与 `.review_sequence`
的投影管道;那会丢掉 `agent_response_contract`、`review_groups`、
`pull_requests[].review_template`、`pull_requests[].review_plan` 与
`pull_requests[].evidence_commands`——正是让命令成为引导式 review 而非统计表的
字段。

## Capability 自有的 Review 执行

`pull_request_review_execution_contract_v2` 每个 packet 共享一次,避免为
100 项队列中的每个 PR 复制一个巨型 prompt。它要求这些 typed 证据组,然后才给出
verdict:

D
- 问题上下文与活跃 caller;
- 架构与 ownership 流;
- 仓库复用：按 caller outcome／资源搜索 base 与 exact-head 代码（包括未变的
    兄弟文件），而非只看新文件名。记录修订、查询、路径与候选 caller；比较
    scope／过滤器、排序／分页、权限／去敏与状态／重试 ownership。优先最近的
    既有 owner；用证据（而非绿色 CI 或无冲突共存）证明独立边界。对一个资源的
    替代视图，酌情验证 consumer 切换与并发更新。base 集成或 head 变更后重复对比；
- 跨生产、测试/fixtures、docs、生成输出与机械挪动的确切行级分类;
- 对改动代码的 PR 的 2-5 项确切 head 符号映射,包括 caller、state、branch、副作用、
  consumer 与失败 ownership;
- 正向与适用的负向执行走查;
- 绑定到变更不变量与失败案例的 validation;
- 最强回归路径、爆炸半径、恢复、最小修复与回归测试;
- 代码量必要性,以及最高价值的保持行为化简;
- 变更比例性:把原始问题的已验证频率、严重度、爆炸半径与恢复成本,与生产机制、
  新 state/contracts/CLI/callers、迁移与长期维护 surface 比较。正确性、绿色 CI
  与早前 findings 的解决不能覆盖 `disproportionate` 或 `not_yet_proven`
  blocker;
- 默认关闭隔离:对 opt-in 变更,追踪每个共享 schema、prompt、accepted-input、
  projection、scheduling 与效应 surface。包括已安装或自动加载的 skills、agent
  指令、prompt 模板、帮助、schemas、安装 bundles 与 provider 设置指引:当这些
  基线 surface 之一已经改变 model 或用户行为时,运行时 `default=false` 不足够。
  把安装、发现、provider 就绪度、accepted input 与 resolver 成功等可用性信号与
  激活 authority 分开。对 scoped capabilities,先证明预期 scope 与每个必需 subject
  已启用,然后投影 capability 特定的指引或效应,再运行配对反事实,证明禁用行为
  仍匹配变更前契约;
- authority 语义:使公开协议 ids 与符号匹配真实 actor 生命周期与 authority,区分
  短暂 sub-agents 与注册 peers 及持久多 agent 协调。

每个 material 扩展的重新 review 从原始问题重置比例性,并评估完整确切 head。
Reviewer 请求的添加本身不是向批准推进;当收益不证明累积机制时,reviewer 应请求
最小可行修复、删除、拆分或 hold。

每 PR 的 `pull_request_review_plan_v1` 记录确切目标、适用性、必需证据 ids 与
初始 `unverified` 的 `pull_request_review_result_v1` 骨架。元数据、标签、文件计数、
风险提示与绿色 CI 不能把证据升级为 `verified`。Stale-head verdict 被禁止。缺失
证据保持 `unverified` 并带原因,而不是被自信散文替换。

D
使用 `--state all` 时,命令必须保留两个生命周期组。`--limit` 值按组应用,使忙碌
开放队列不能吞掉整个 packet、在窗口存在 merged PRs 时让 `review_groups.merged`
为空。默认每组 100 PRs。每个 packet 携带 `result_completeness`;穷举请求必须要求
`complete=true`,并在源扫描或 packet 分片被截断时用其 `recommended_limit` 重跑。
Live GitHub 读取应在构造分组 packet 前分开 fetch 开放与关闭/合并窗口。

`repository_reuse` 在每个适用计划中从 `unverified` 开始。其结论为
`reused`、`separation_justified`、`no_existing_candidate`、
`unjustified_duplication` 或 `not_yet_proven`。负向搜索必须说明其范围与
局限；空候选列表不证明不存在。无根据的重复或缺失证据需要 request-changes
结论。具有不同不变量或兼容性需求的相似代码可以合法地保持独立。普通 docs
保留既有 review 路径；纯 smoke 变更保留 `durable_smoke_value` 覆盖评审。
这是评审者执行的、由 packet 投影的合同，而不是自动仓库搜索或发布散文的语义
校验器。测试确立 packet 适用性与 verdict 策略，而非保证模型遵从。

Agent 响应不得停在队列表。对于 `/loopx-pr-review`,队列只是前言;最终答案应逐个
审阅选中的 PRs,包含五段:`动机`、`改动思路`、`具体改动`、`对主干的风险` 与
`我的整体评价`。仅统计/列表的响应只在该请求不带 review 时用户显式要求统计或
列表才有效。当可见消息以 `/loopx-pr-review` 开头时,`open`、`closed`、`merged`、
`today` 或时间窗口等词是 review 队列的过滤器,不是跳过 review 的许可。只为
`只统计`、`只列出`、`stats only`、`list only`、`不要 review` 或 `不用分析` 等
显式 opt-out 短语降级。

发布的 review 是全 PR 双语 review:一个完整的中文五段 review,覆盖每个变更
surface、关键符号、正负路径与 validation,外加一个简洁英文机器 verdict
(`APPROVE`、`REQUEST_CHANGES` 或 author 自有的 `COMMENTED` fallback)。中文
review 承载深度与证据;英文 verdict 承载机器可读状态与校验摘要。只有 findings
或只有 blockers 的正文不是完整 PR review。

每个完整 PR review 还必须包含整 PR 解释深度:per-file 责任映射、带确切 head
引用的 2-5 个关键符号解释、一次正向运行时走查、一次负向/fail-closed 走查、
per-surface validation,以及整 PR 的判断。

## 源读取

实现可以读取紧凑公开 PR surfaces:

- pull request 标题、编号、URL、分支、author、生命周期状态、merge 时间与
  review 决策;
- PR body 摘要;
- 变更文件列表与 diff 规模;
- status-check 汇总;
- merge-state 元数据;
- current-head commit 时间戳与用于派生 `review_ready_at`、验证独立确切 head
  结论的 review 元数据。

Raw review 正文只用于格式/确切 head 决策,不返回也不持久化。有效的最新结论点名
确切 head,包含全部五段中文以及行首 `English verdict: APPROVE` 或
`English verdict: REQUEST_CHANGES`,并让该 verdict 与正式 `APPROVED`/
`CHANGES_REQUESTED` 状态一致。因为 GitHub 阻止每个 self-review 状态转换,
author 自有结论使用 `COMMENTED` 加一个确切标题:
`Approval conclusion (author-owned PR; GitHub blocks formal self-approval)` 或
`Request changes conclusion (author-owned PR; GitHub blocks formal self-review)`。
紧凑结果以 `pull_request_review_conclusion_v0` 版本化,并报告 typed
invalid-reason codes。

它们不得包含 raw 日志、私有 connector payloads、凭据、本地绝对路径、私有源正文
或隐藏 CI artifacts。

## 响应形状

`loopx_pr_review_command_response_v0`:

```json
{
  "schema_version": "loopx_pr_review_command_response_v0",
  "request": {
    "schema_version": "loopx_pr_review_command_request_v0",
    "command": "/loopx-pr-review",
    "cli_command": "loopx pr-review [--repo owner/repo] [--state open|merged|all] [--since ISO]",
    "repository": "owner/repo",
    "limit": 100,
    "state_filter": "all",
    "since": "2026-06-28T00:00:00Z",
    "window": {"state_filter": "all", "since": "2026-06-28T00:00:00Z"},
    "source": "github_cli",
    "privacy_mode": "public_safe_github_metadata",
    "dry_run": true
  },
  "result_completeness": {
    "schema_version": "pr_review_result_completeness_v0",
    "complete": true,
    "truncated": false,
    "limit": 100,
    "source_scan_complete": true,
    "recommended_limit": null,
    "rerun_cli_args": []
  },
  "summary": {
    "headline": "8 PR(s) in review window: 3 open, 5 merged; 8 need review attention.",
    "total_pr_count": 8,
    "open_pr_count": 3,
    "merged_pr_count": 5,
    "review_attention_count": 8,
    "post_merge_review_count": 5,
    "draft_count": 0,
    "recommended_first_pr": {
      "rank": 1,
      "number": 773,
      "review_depth": "docs_and_smoke_review"
    }
  },
  "review_sequence": [
    {
      "rank": 1,
      "number": 773,
      "title": "docs: add newcomer command path",
      "url": "https://github.com/owner/repo/pull/773",
      "state": "OPEN",
      "review_depth": "docs_and_smoke_review",
      "risk_hint_level": "low",
      "main_risk_level": "low",
      "why_now": "Open and awaiting reviewer decision."
    }
  ],
  "review_groups": {
    "unmerged": {
      "schema_version": "pr_review_group_v0",
      "group_id": "unmerged",
      "title": "Unmerged PRs",
      "intent": "Review before merge: decide approve, request changes, defer, or wait for checks.",
      "count": 3,
      "pr_numbers": [773, 775, 771],
      "review_sequence": []
    },
    "merged": {
      "schema_version": "pr_review_group_v0",
      "group_id": "merged",
      "title": "Merged PRs",
      "intent": "Post-merge audit: check outcome, regression risk, and follow-up quality without blocking already-merged work.",
      "count": 5,
      "pr_numbers": [770],
      "review_sequence": []
    }
  },
  "pull_requests": [
    {
      "number": 773,
      "head_oid": "0123456789abcdef0123456789abcdef01234567",
      "review_template": {
        "schema_version": "pr_review_five_block_template_v0",
        "purpose": "Empty scaffold only; agentloop fills it after reading PR body and diff.",
        "sections": [
          {
            "label": "动机",
            "word_hint": "200-350字",
            "content": "",
            "agent_instruction": "解释旧行为、具体痛点、受影响的用户或调用方、目标结果与必要性；说明不合并会继续付出什么代价，以及需求来自活跃调用方还是未来设想。"
          },
          {
            "label": "改动思路",
            "word_hint": "250-450字",
            "content": "",
            "agent_instruction": "解释所选架构、改动前后的控制流或数据流、所有权边界、关键不变量和替代方案取舍；为不熟悉子系统的读者给出一条正向运行链路。"
          },
          {
            "label": "具体改动",
            "word_hint": "300-600字",
            "content": "",
            "agent_instruction": "把关键文件和符号映射到行为，覆盖接口、配置或状态、兼容路径、测试与文档；说明各部分如何协作，并给出一个具体输入到输出的例子。"
          },
          {
            "label": "对主干的风险",
            "word_hint": "250-500字",
            "content": "",
            "agent_instruction": "按严重度列出有文件或符号证据的发现，评估爆炸半径、兼容性、权限、默认副作用、失败与回滚、可观测性和缺失覆盖；策略或生命周期改动必须解释一条负向链路。"
          },
          {
            "label": "我的整体评价",
            "word_hint": "150-300字",
            "content": "",
            "agent_instruction": "权衡价值与复杂度，列出实际检查或运行的验证，注明审阅的 head SHA，并给出精确结论；若阻塞，说明最小修复和复审所需证据。"
          }
        ],
        "review_order": ["docs/guides/newcomer-command-path.md", "docs/README.md"],
        "output_hint": "Write for a reader unfamiliar with the PR: explain context, architecture, implementation, validation, necessity, and risk with concrete evidence. Follow each section's range as a depth signal, not filler."
      },
      "motivation": "Adds a newcomer command path...",
      "scale": {"changed_files": 3, "additions": 90, "deletions": 4},
      "areas": {"public_docs": 3},
      "checks": {"summary": "2 successful check(s)."},
      "metadata_risk_hint": {
        "schema_version": "pr_metadata_risk_hint_v0",
        "level": "low",
        "basis": ["areas=公开文档 3", "scale=3 files +90/-4", "checks=2 pass"],
        "disclaimer": "Metadata-only hint for queue ordering; agentloop must read the PR diff before judging main risk."
      },
      "main_regression_analysis": {
        "schema_version": "main_regression_analysis_v0",
        "risk_level": "low",
        "risk_summary": "低 main regression risk across 公开文档 3; 3 file(s), +90/-4; checks=2 pass.",
        "potential_regressions": [
          "Runtime regression risk is low, but public guidance or smoke expectations can drift from shipped behavior."
        ],
        "bug_risks": [
          "Docs-only or smoke-only changes can bless stale contracts if examples no longer match the real command path."
        ],
        "verification_focus": [
          "Run `git diff --check` and the touched smoke; compare command examples with current CLI help when syntax is involved."
        ],
        "post_merge_review": false
      },
      "risk_notes": [],
      "evidence_commands": [
        "gh pr view 773 --json title,body,files,commits,statusCheckRollup,headRefOid,updatedAt",
        "gh pr diff 773 --name-only",
        "gh pr diff 773 --patch",
        "gh pr view 773 --json headRefOid,updatedAt"
      ]
    }
  ],
  "agent_response_contract": {
    "schema_version": "pr_review_agent_response_contract_v0",
    "table_only_response_allowed": false,
    "slash_prefix_dominates_intent": true,
    "stats_only_requires_explicit_opt_out": true,
    "queue_table_role": "preface_only",
    "required_packet_fields_to_preserve": [
      "agent_response_contract",
      "agent_response_contract.review_execution_contract",
      "result_completeness",
      "review_groups",
      "pull_requests[].review_plan",
      "pull_requests[].review_template",
      "pull_requests[].evidence_commands"
    ],
    "required_final_sections": [
      "动机",
      "改动思路",
      "具体改动",
      "对主干的风险",
      "我的整体评价"
    ],
    "explanation_depth_contract": {
      "schema_version": "pr_review_explanation_depth_v0",
      "reader_profile": "A technically curious reader who may not know this PR or subsystem.",
      "evidence_layers": ["problem", "architecture", "implementation", "validation"],
      "freshness": "Record and recheck the remote head SHA before the verdict."
    }
  },
  "boundary": {
    "raw_logs_recorded": false,
    "credential_values_recorded": false,
    "absolute_paths_recorded": false
  }
}
```

## Review 流程

Packet 应让 reviewer 按顺序走过 PRs:

1. 从 `review_groups.unmerged` 开始,处理仍可能影响 merge 决策的 PRs。
2. 然后使用 `review_groups.merged` 做 post-merge 审计与跟进质量。
3. 使用 `evidence_commands`、关键文件、变更文件规模与 checks 打开真实 PR body
   与 diff。
4. 对照 `agent_response_contract.review_execution_contract` 执行该 PR 的
   `review_plan`;让不可用证据保持显式 unverified。
5. 填充风险散文前,读取 `main_regression_analysis`。它是 CLI 对潜在 main
   regressions、bug risks 与聚焦验证的具体生成视图。
6. 通过空白五块模板渲染已验证的结构化结果:`动机`、`改动思路`、`具体改动`、
   `对主干的风险`、`我的整体评价`。把每段范围当作对不熟悉子系统的读者的深度
   信号,而不是填充。
7. 只把 `metadata_risk_hint` 当作队列排序元数据。不得把它复制为最终风险判断。
8. 重新检查确切 head,然后决定 `approve`、`request changes`、`defer` 或
   `merge after checks`。

只列出 `Open` 与 `Merged` PRs、规模与推荐下一个顺序的响应,对 `/loopx-pr-review`
是不完整的;读取证据后应继续进入每 PR 五块 review 卡。

同样,声称运行了 `loopx pr-review` 却使用诸如
`loopx --format json pr-review ... | jq '.summary, .review_sequence'` 之类命令的
响应仍不完整:工具调用发生了,但契约/模板字段在 agent 规划答案前被丢弃。

## 验收检查

首个实现可接受的标准是:

- `loopx slash-commands` 暴露 `/loopx-pr-review`;
- `loopx pr-review` 返回 `loopx_pr_review_command_response_v0`;
- 默认 live 读取使用调用方当前的 `gh` 仓库,而 `--repo owner/repo` 可以审阅另一个
  GitHub 项目;
- `--state all` 在同一 packet 中包含 merged PRs,按生命周期组应用 `--limit`,
  并在请求窗口存在 merged PRs 时保持 `review_groups.merged` 非空;`--state open`
  保留旧 open-only review 队列;
- 默认 limit 为 100,穷举请求只在 `result_completeness.complete=true` 时进行;
  截断 packet 为下次读取提供更大的 `recommended_limit`;
- `--since` 可以限定隔夜或 release-window 审阅,而不依赖私有聊天记忆;
- 响应包含 review sequence、变更文件范围、状态检查、关键文件、风险注释、
  metadata-only 风险提示、具体 `main_regression_analysis`、证据命令、显式
  `review_groups.unmerged` / `review_groups.merged`,以及空白五块 review 模板;
- 共享 `pull_request_review_execution_contract_v2` 拥有 typed 证据、完成、
  fresh 度、findings-first 与 verdict policy,而每个 PR 有带 unverified 结果骨架
  的紧凑确切 head `pull_request_review_plan_v1`;
- packet 包含 `agent_response_contract.table_only_response_allowed=false` 与
  `agent_response_contract.required_packet_fields_to_preserve`,使
  slash-command agents 知道仅表格的聊天答案不完整;
- slash-command 目录把 `/loopx-pr-review` 标记为 `must_run_cli_first` 与
  `slash_prefix_dominates_intent`,并说明手动 `gh` 调用只是 CLI packet 选中
  PR 之后的逐 PR 深读命令;
- 每个 PR 包含 `review_template.sections`,覆盖 `动机`、`改动思路`、`具体改动`、
  `对主干的风险` 与 `我的整体评价`;
- 每个 review 模板段携带段特定深度范围,packet 的解释深度契约要求问题、架构、
  实现、校验、必要性与风险证据,而不是通用长答案;
- live packets 暴露并重新检查 `headRefOid`,使 review verdict 绑定到实际检查的
  远程 revision;
- 自主 packets 按当前 head `review_ready_at` 排序社区工作,把响应抢占限制为一个
  slot,age author 自有 fallbacks,并忽略仅 check 的优先级活动;
- `--observation-state-file` 原子跨 Codex 任务携带 observation 与 handled 游标,
  不返回本地路径,也不授予外部写;
- 模板段必须保持 `content` 为空,使 agentloop 在写 review 前读真实 PR;
- `metadata_risk_hint` 必须是 repository-generic,不得对 LoopX 文件或领域做
  特判;
- `main_regression_analysis` 必须 repository-generic,必须包含
  `potential_regressions`、`bug_risks` 与 `verification_focus`,且不得被空白
  模板替换;
- live GitHub 读取与 fixture-based smokes 共享同一 schema;
- 不记录 raw 日志、私有 payloads、凭据、本地路径或私有源正文。
