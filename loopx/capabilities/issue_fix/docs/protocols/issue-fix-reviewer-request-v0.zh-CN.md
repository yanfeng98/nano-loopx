# issue_fix_reviewer_request_v0

> [English](issue-fix-reviewer-request-v0.md)

`issue_fix_reviewer_request_v0` 是在 issue-fix PR 存在后自动通知 reviewer 的
public-safe 执行契约。它把只读 reviewer 推荐转成有界的外部写,并证明正式请求
或其仅权限 fallback 评论在 pull request 上变得可见。

## 默认行为

默认策略是 `request_top_requestable_when_authorized`:

1. 读取实时 PR 元数据;
2. 排除 PR author、bots、显式排除的身份、已请求的 reviewers 与已审阅的人;
3. 从仓库 `CODEOWNERS`、caller 验证的公开维护者映射、确切变更路径贡献历史与
   最近 module 历史对剩余候选排序;
4. 请求拥有可解析 GitHub handle 的最高排名候选;
5. 当且仅当 GitHub 确认正式请求缺乏权限时,发布一条简洁 PR 评论,点名同一
   reviewer、关联 issue 与紧凑 PR 标题变更摘要;
6. 再次读取 PR,要求正式请求或 fallback 评论的语义 review 请求与公开 URL 可见;
7. 只有在该验证之后才继续 PR 生命周期监控。

可选 `--notification-sinks-json`,或通过 `configure-goal` 注册的 goal-default
本地私有配置,可以随后通过项目专用二级 channel 投递给同一已验证 reviewer。二级
投递是独立证据:它从不替代 GitHub review 状态,从不重排 reviewer,并且当其自身
设置被阻塞时不能抹掉成功的 canonical 请求。见
[issue_fix_reviewer_notification_sinks_v0](issue-fix-reviewer-notification-sinks-v0.md)。

默认上限是一位 reviewer。现有已请求或已完成 review 覆盖,以及已验证的 fallback
通知计入该上限,因此重复执行是幂等的,不会不断加人或重复 `@reviewer` 评论。
低置信度候选在其是最好、可请求、非 author 的 repository-native 候选时仍有资格;
置信度是证据质量,不是自动跳过规则。

## Authority 模型

Review 请求是外部写。`--execute` 断言 host 有活跃 `external_review_request`
authority scope;现有更宽的 `publish` authority 在 issue-fix gate 中同样满足该
动作。没有该 authority,命令可以从紧凑 PR 元数据准备请求预览,但不能写。

同一狭窄 authority 只在正式请求返回已确认权限拒绝(如 HTTP 403/404)时覆盖
一条 fallback 评论。它不授权任意评论、push、PR 创建、merge 或任何其他发布动作。
网络失败、未知 provider 错误与身份模糊从不触发 fallback。带有持久
reviewer-request authority 的长程 agent 应在 PR 创建后自动调用该命令,而不是
请人类执行例行通知。

## CLI

执行并验证默认请求:

```bash
loopx issue-fix reviewer-request \
  --url https://github.com/owner/repo/pull/123 \
  --repo-path /path/to/approved/repo \
  --base-ref origin/main \
  --identity-map-json verified-identities.json \
  --reviewer-sources-json reviewer-sources.json \
  --notification-sinks-json local-private-notification-sinks.json \
  --execute \
  --format json
```

对于已连接的长程 goal,一次注册本地私有指针,让正常 post-PR 调用发现它:

```bash
loopx configure-goal \
  --goal-id example-goal \
  --issue-fix-reviewer-notification-config \
  .loopx/config/issue-fix/reviewer-notification-sinks.json \
  --execute

loopx issue-fix reviewer-request \
  --goal-id example-goal \
  --project /path/to/approved/repo \
  --url https://github.com/owner/repo/pull/123 \
  --repo-path /path/to/approved/repo \
  --base-ref origin/main \
  --execute \
  --format json
```

Goal-default 执行模式在任何外部通知前加载现有 PR lifecycle 行,或从一次新的
紧凑 GitHub lifecycle 读取自动物化一个。然后只把已验证 `sha256:` 二级 receipts
持久化进该行。本地配置、profiles、目的地与成员映射不被复制。重启后重复调用返回
`already_notified`,没有另一次二级 provider 写。

提供紧凑、caller 批准的 PR 元数据(含 `author`、`comments`、`reviewRequests`、
`reviews` 与 `state`)做无外部写预览:

```bash
loopx issue-fix reviewer-request \
  --url https://github.com/owner/repo/pull/123 \
  --repo-path /path/to/approved/repo \
  --base-ref origin/main \
  --reviewer-sources-json reviewer-sources.json \
  --metadata-json pr-metadata.json \
  --format json
```

没有完整 PR 元数据的预览会 fail closed,因为无法验证 author 排除。执行模式在
live provider 响应省略 author 时应用同一规则。紧凑元数据 payload 从不被复制进
输出 packet。
`--identity-map-json` 可以在最强的贡献候选无法从公开 noreply 身份证据解析时,
携带人工验证的 git-display-name 到 GitHub handle 映射。映射解析身份,但不改变
底层 ownership 分数。
`--reviewer-sources-json` 传递 `reviewer-plan` 使用的同一个紧凑、public-safe
源 packet。来源引用解释排名;它们不授予写权威,也不绕过 live author/现有
reviewer 排除。

## 输出与转换

Packet 记录:

- 选中、正式请求与另行通知的 reviewer handles;
- external-read 与 external-write 动作是否执行;
- 请求是否执行并完全验证;
- 通知模式、fallback 执行/验证,以及使用 fallback 时的公开评论 URL;
- 推荐状态、public-safe 证据候选与 reviewer 源引用;
- 一个结构化转换。
- 可选的二级 sink 状态、验证与哈希 receipts,不包含私有目的地、成员或
  bot-profile 字段。
- sink 来自显式输入还是 goal 默认,以及已验证哈希 receipts 是否持久化在现有 PR
  lifecycle 状态中。
- 权威执行路径是否对账了未发送的二级队列、取消了哪些过期条目,而不暴露目的地
  数据。

成功的已验证请求发出 `issue_fix_reviewer_request_verified`,带
`monitor_continuation`。确认的权限拒绝后跟已验证评论,发出
`issue_fix_reviewer_comment_fallback_verified`。如果 review 已由请求、已完成
review、标记的 fallback 评论,或显式点名 reviewer 并请求 review 的 live 评论
覆盖,执行是安静的、无写的 monitor continuation,并返回现有评论 URL。二级 sinks
保持绑定到那个已覆盖 reviewer;未解决的 sink 身份跳过二级投递,而不是替换成
不同候选。任何先前排队、未发送的二级目标会被当前 execute reconciliation 原子
替换或取消。语义评论匹配归一化 handle 大小写,要求在 mention 附近有有界
review-request 短语,并忽略引用文本、代码块、普通讨论与仅标记元数据。缺失可请求
身份产生可运行的 identity-resolution successor。已关闭 PRs 产生结构化
no-follow-up。

两个通知路径的权限失败、网络/未知 provider 错误或写后验证失败,产生具体
blocker,同时为有界重试保留选中的 reviewer。命令从不只因写命令返回零而报告成功。

## 公共安全边界

每个 packet 保持这些字段为 false:

- `local_paths_captured`
- `raw_provider_payload_captured`
- `raw_git_output_captured`
- `commit_emails_captured`

它不存储凭据、本地路径、raw provider 响应、raw git log、issue 正文、评论正文、
transcript 或运行时状态。公开源 URL 与匹配路由元数据可以保留;链接的维护者映射
正文不被捕获。Fallback 评论只含公开 PR 上下文:reviewer handle、关联 issue
引用、紧凑 PR 标题变更摘要,以及指向 PR 描述中动机、验证与风险的指针。新评论
依赖语义去重,而不是发布幂等标记;遗留标记保持读兼容。仓库历史只从显式批准的
checkout 读取,并影响紧凑排名证据。

## 验证

运行:

```bash
python3 examples/issue-fix-reviewer-request-smoke.py
```

通用 fixture 验证 live-author 排除、top-candidate 选择、成功请求与 readback、
仅权限评论 fallback、fallback URL/语义验证、人类可读 issue/变更上下文、无重复
评论的幂等重试、对更早显式 review-request 评论的语义去重、普通 reviewer 讨论的
拒绝、未分类 provider blockers、公共安全边界与无写 CLI 预览。它还证明公开
maintainer-map 候选到达请求 packet,而不削弱外部写 gate。它不含 OpenViking
特定分支或候选。
