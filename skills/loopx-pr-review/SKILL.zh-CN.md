---
name: loopx-pr-review
description: Use for `/loopx-pr-review` or evidence-backed PR queue review. Run `loopx pr-review` first, execute the capability-owned review plan for each selected exact head, then publish full bilingual PR reviews (complete Chinese five-block review plus one concise English verdict) that match the verified findings. Use `loopx-pr-merge` for approval or merge actions.
---

# LoopX PR 评审

> [English](SKILL.md)

本技能是薄的宿主适配器。内置 `pull-request-review` capability 通过 CLI 包拥有
评审深度、证据要求、完整性与裁决政策。不要把这些规则复制到本技能中，也不要用
宿主特定检查清单替换它们。

## 路由

对 `/loopx-pr-review`、显式 PR 评审或按状态/时间窗口的评审队列使用本技能。
证据评审完成后，把批准、合并、自合并与管理员绕过路由到 `loopx-pr-merge`。

在临时 GitHub 读取前先运行 LoopX CLI：

```bash
loopx --format json pr-review --state all
```

仅翻译显式过滤条件：

- `--repo owner/repo`
- `--since ISO`
- `--state open|merged|all`
- `--limit N`

`today`、`open` 或 `merged` 这样的词是过滤条件，不是只返回一个表而不用
评审的许可。仅统计输出需要显式 opt-out，如 `只统计`、`只列出`、`stats only`
或 `不要 review`。

## 保留包

在打印紧凑投影前保存完整的首个 JSON 包。保留
`agent_response_contract.required_packet_fields_to_preserve` 命名的所有路径，
尤其是：

- `agent_response_contract.review_execution_contract`
- `result_completeness`
- `review_groups`
- `pull_requests[].review_plan`
- `pull_requests[].review_template`
- `pull_requests[].evidence_commands`

不要只通过 `jq` 管道处理唯一副本。当穷尽请求的
`result_completeness.complete=false` 时，在评审前用其 `recommended_limit` 重跑。

## 执行一个评审计划

先评审 `review_groups.unmerged`，再评审 `review_groups.merged`。对每个所选 PR：

1. 记录包的精确 head，运行其 `evidence_commands`，适用时外加聚焦的仓库原生
   验证。
2. 从共享执行契约填充 `review_plan.result_template`；把缺失证据保留为
   `unverified`。对 `default_off_isolation`，跨每个共享与自动加载界面运行其
   配对反事实，包括 skills、agent 指令、提示模板、帮助、schema、安装包与
   provider 指引。把安装、发现、provider 就绪、接受输入与 resolver 成功视为
   可用性而非激活；运行时 default-off 标志不能补偿已通过基线指令界面投影的
   capability 行为。对 scoped activation，在 capability 特定指引或效果前验证
   预期范围与每个必需主题。对 `authority_semantics`，把名称与 actor 权限匹配。
   绝不可从元数据或 CI 推断 `verified`。
3. 字面应用 `completion_gate`。如果适用要求缺失，不要制造详细裁决；说出证据
   缺口。
4. 通过 `review_template` 渲染验证结果。五个部分是输出结构，执行契约是证据
   权威。
5. 在裁决与发布前立即重读远端 head。如果它变化了，重新启动证据环节。

每个 PR 获得独立证据环节与独立卡片。队列表只是序言。对大型队列，完成较少的
完整卡片并点名剩余部分，而不是把每个评审压缩成元数据散文。

## 发布并回读

对打开的 PR，默认发布验证过的可执行发现，除非用户显式要求仅本地/干跑输出，
或发现包含不得公开发布的私有或安全敏感材料。

- 剩余 blocker：正式 `REQUEST_CHANGES`；对作者拥有的 PR，使用标题为
  `Request changes conclusion (author-owned PR; GitHub blocks formal self-review)`
  的 `COMMENTED` 评审。
- 无 blocker 的非阻塞发现：正式 `APPROVE`，而非裸评论。当 GitHub 账号是 PR
  作者且 GitHub 拒绝自批准时，把同一批准结论记录为标题为
  `Approval conclusion (author-owned PR; GitHub blocks formal self-approval)`
  的 `COMMENTED` 评审，使裁决保持公开且机器可见。
- 仅含 P2 建议的非阻塞发现：仍 `APPROVE`；把 P2 项保留在评审正文中，而不是
  降级裁决。
- 已合并的 PR：仅对有新的可执行发现发布合并后审计评论；避免重复等价的
  exact-head 结果。

从审查过的精确 head 构建公开文本。移除本地路径、私有上下文、原始日志、凭据与
仅内部链接。回读已发布的评审，验证其状态与渲染正文，并返回其 URL。合并仍经
`loopx-pr-merge` 路由；`APPROVE` 不是合并权限。不要把公开 blocker 只留在
聊天中。

## 完整 PR 评审与双语格式

每个评审必须覆盖整个 PR，而不只是主要发现。读取完整 diff/checks，然后解释
动机、架构、变更文件/符号、正负路径、整个 diff 的风险、验证与总体判断。
仅发现或仅 blocker 的正文是不完整的。

发布两个产物：

1. **详细中文评审** — 独立的中文全文 PR 评审，带精确 head 与五个部分：
   `动机`、`改动思路`、`具体改动`、`对主干的风险`、`我的整体评价`。
   覆盖每个变更界面与关键符号，而不只是主要发现。
2. **英文简短结论** — 以精确的 `English verdict:` 开头，包含裁决、精确 head、
   关键发现与验证。

在中文部分覆盖整个 PR 之前不要发布。回读两个产物。

## 完整 PR 解读深度

完整评审是全文 PR 解读，不是清单或发现摘要。对每个所选 PR：

1. 读取每个变更文件，并把每个文件映射到其职责、输入、输出与关键符号。
2. 选择 2-5 个行为承载符号，解释前后行为、关键分支、调用方/被调用方、
   副作用与失败路径。
3. 从用户/宿主动作到可观察结果走一条正向路径。
4. 走一条负向路径（无效输入、权限、超时、损坏状态、私有边界或回滚），
   指出它在哪里失败关闭。
5. 在五个部分中覆盖所有变更界面：动机、改动思路、具体改动、主要风险、
   总体判断。
6. 按界面列出验证，并指出任何未独立验证的内容。
7. 对整个 PR 给出总体判断，而不只是主要发现。

只重复 PR 正文、只讨论一个 blocker 或遗漏整个文件/模块的评审不完整，必须
重做。

## 示例 / 演练 / 仅冒烟 PR

当评审计划标记 `smoke_or_example_only` 时，批准前 `durable_smoke_value`
证据是强制的。本质是对仓库与产品的真实、持久价值：可运行、确定性且公开安全
是必要但不充分。

1. 说出该产物守护的已交付行为、边界或维护成本。"演示了已经能工作的东西"
   不是持久价值。
2. 扫描既有覆盖（`rg -l '<behavior|module>' examples tests`）与同作者批次
   （`gh pr list ... --author <author>` / `gh search prs`）；
   把几分钟内打开的同形状批次标记为 PR farming。
3. 应用仓库冒烟政策：薄且持久、守护已交付行为或真实边界、压缩而非追加、
   把同形状演练合并为一个 PR 或聚焦测试。
4. 裁决：对重复、过大或无价值的脚手架用 `REQUEST_CHANGES`；在正文中命名
   合并或变薄的修复。
5. 重复违规者：在 REQUEST_CHANGES 警告之后，同一作者的进一步低价值同形状 PR
   升级为贡献限制建议（所有者阻止该账号继续提交 PR）；警告必须点名这一后果。

## 自主队列

对周期观察，保留一个被忽略的 checkpoint，并使用同一 capability：

```bash
loopx --format json pr-review --repo owner/repo --state open \
  --autonomous-observation --observation-state-file .local/pr-review-monitor.json \
  [--projected-exact-head NUMBER@HEAD_OID] [--handled-exact-head NUMBER@HEAD_OID]
```

把 `candidate` 视为预览，而非持久投影。遵循此顺序：持久 Todo target-key
回读 -> `--projected-exact-head` -> exact-head 评审/评论回读 ->
`--handled-exact-head`。在 Todo 存在前不得发送投影 ACK，在该 head 回读前也不得
发送 handled ACK。观察状态保持字面；checkpoint 不授予权限。无状态调用方可用
`--previous-observation-json` 代替。

## 失败

如果 `loopx pr-review` 不可用，修复 LoopX 安装或使用预期检出的 CLI。不要
手动重建队列并称其为成功的 `/loopx-pr-review` 运行。
