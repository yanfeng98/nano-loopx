# issue_fix_reviewer_recommendation_v0


`issue_fix_reviewer_recommendation_v0` 是对 issue-fix 变更可能合适的 reviewer
(人或团队)排序的 public-safe 契约。它把 repository-native ownership 证据变成
可解释的推荐;它本身不指派 reviewer、不请求 review,也不授予发布 authority。
其默认下游 policy 是让单独授权的 `reviewer-request` 命令邀请排名最高的可请求
候选。

## 产品意图

长程 issue-to-PR agent 不应在产出正确 patch 后停下。它还应准备一条可信的
review 路由,帮助变更触达维护者。因此 reviewer 选择是 issue-fix 规划的一部分,
而外部 GitHub review request 仍是单独授权、已验证的写。

契约必须回答四个问题:

1. 哪些变更路径支撑这个候选?
2. 候选是否由仓库 policy、repository-declared 维护者映射、贡献历史或组合支撑?
3. 候选能否解析为可请求的 GitHub handle?
4. 哪个公开来源引用解释了路由,它有多新?
5. 请求 review 前还剩下什么人工或仓库 policy 检查?

## 证据顺序

首个实现使用这个保守的权威顺序:

1. 仓库第一个受支持 `CODEOWNERS` 文件的最后匹配规则:
   `.github/CODEOWNERS`、`CODEOWNERS`,然后 `docs/CODEOWNERS`;
2. caller 验证的仓库维护者映射,其最具体的路径路由点名 primary contact;
3. 每个确切变更路径的 author history;
4. 新路径没有可用 exact-path history 时,最近 module 目录的 author history;
5. 没有更具体路由适用、或 primary contact 被排除时,仓库声明的 fallback 或
   跨模块联系人。

`CODEOWNERS` 获得主导评分权重,因为它表达可执行的仓库 policy。维护者映射是比
纯熟悉度更强的路由证据,但仍保持 caller 验证与 freshness 限定,而不是
branch-protection authority。Git history 是 advisory 熟悉度证据:提交数或近期度
本身不能证明维护者 authority、当前可用性或审阅同意。

模式匹配器有意支持 `CODEOWNERS` 语法的常见确定性子集。Packet 报告
`codeowners_pattern_support: common_subset`;依赖更专门匹配语义的仓库必须对照
其原生平台 policy 验证推荐。

## CLI

不读取本地仓库的预览:

```bash
loopx issue-fix reviewer-plan \
  --repo-path /path/to/approved/repo \
  --repo owner/repo \
  --changed-file src/service.py \
  --exclude-reviewer @pull-request-author \
  --exclude-author-name "PR Author Git Name" \
  --identity-map-json verified-identities.json \
  --reviewer-sources-json reviewer-sources.json \
  --format json
```

只读取 caller 批准的本地 checkout,并从 base ref 派生变更路径:

```bash
loopx issue-fix reviewer-plan \
  --repo-path /path/to/approved/repo \
  --repo owner/repo \
  --base-ref origin/main \
  --exclude-reviewer @pull-request-author \
  --exclude-author-name "PR Author Git Name" \
  --reviewer-sources-json reviewer-sources.json \
  --execute \
  --format json
```

`--execute` 只授权本地仓库检查。它不授权网络访问、GitHub review request、
评论、push 或 merge。

## 输入契约

- `repo_path`:caller 批准的本地 git checkout;从不复制进输出;
- `repo`:紧凑的 public-safe 仓库标签;
- `changed_files`:可选的显式 repo-relative 路径;
- `base_ref`:未提供变更文件时使用的 diff 基准;
- `history_limit`:每路径的有界历史深度;
- `max_candidates`:有界结果计数;
- `exclude_reviewers`:不得被推荐的 GitHub handles,通常包括 PR author 与已知
  不可用身份;
- `exclude_author_names`:身份解析不可用时,被排除 handle 的 git display-name
  aliases;输出只保留计数;
- `identity_map_json`:可选的 public-safe、人工验证的 git display names 到
  GitHub handles 映射;raw 映射不保留,而解析后的 handle 与
  `caller_verified_github_identity` 证据可见;
- `reviewer_sources_json`:可选的 `issue_fix_reviewer_sources_input_v0` packet。
  每个源有稳定 id、`maintainer_map` kind、公开 HTTPS 或 repo-relative 引用、
  `authoritative|verified|advisory` trust、`current|stale|unknown` freshness、
  时区感知的 `observed_at` 与有界 routes。Routes 使用 `path_prefix`、
  `path_glob` 或 `repository_fallback`,并命名 primary 和/或 fallback GitHub
  handles;
- `execute`:是否允许读取本地仓库状态。

LoopX 不 fetch 也不复制链接页面。Caller 读取已批准的公开源,只提供紧凑路由映射,
并把源 URL 保留为 provenance。这让 GitHub maintainer-map issue、仓库文档或
checked-in ownership 文件,能通过一个 provider-neutral 契约使用,而不存储 raw
正文。

示例:

```json
{
  "schema_version": "issue_fix_reviewer_sources_input_v0",
  "sources": [
    {
      "source_id": "repository-maintainer-map",
      "source_kind": "maintainer_map",
      "reference": "https://github.com/owner/repo/issues/10",
      "trust": "verified",
      "freshness": "current",
      "observed_at": "2026-07-10T00:00:00Z",
      "routes": [
        {
          "route_id": "service-module",
          "match_kind": "path_prefix",
          "pattern": "src/service",
          "primary_reviewers": ["@service-owner"],
          "fallback_reviewers": ["@cross-module-owner"]
        },
        {
          "route_id": "repository-fallback",
          "match_kind": "repository_fallback",
          "primary_reviewers": [],
          "fallback_reviewers": ["@cross-module-owner"]
        }
      ]
    }
  ]
}
```

这里的 `reference` 是证据血缘,不是抓取页面的指令。`path_prefix` 与 `path_glob`
routes 把人与变更文件绑定;`repository_fallback` 只在没有 scoped route 匹配时
提供低排名的跨模块 route。

变更路径必须非空且 repo-relative。预览模式不检查 `repo_path`,返回
`recommendation_status: preview_only`。

## 输出契约

Packet 使用 `schema_version: issue_fix_reviewer_recommendation_v0` 并包含:

- `recommendation_status`:`preview_only`、`candidates_ready`、
  `identity_resolution_required` 或 `no_candidates`;
- `changed_files` 与 `changed_file_count`,只使用 repo-relative 路径;
- 排序过的 `candidates`,带稳定候选 id、可选 GitHub handle、可请求性、分数、
  来源种类、reason codes、匹配路径、`CODEOWNERS` 模式、历史计数、recency 排名、
  路径覆盖、置信度、紧凑 `reviewer_source_evidence` 与去重 `source_refs`;
- `evidence_summary` 描述权威顺序与 fallbacks;
- `policy` 声明推荐不是指派、默认请求策略是
  `request_top_requestable_when_authorized`、默认上限是一位 reviewer,且需要
  external-review-request authority;
- public-safety 与副作用标志。

没有已验证 GitHub handle 的候选保持可见为熟悉度证据,但标记 `requestable: false`,
带 `github_identity_resolution_required`。Packet 从不暴露底层 commit email。

人类可以一次性解析模糊 display name。Caller 验证的 handle 随后变为可请求,并用
候选的原始仓库贡献证据重新排序;人工断言只解析身份,不捏造 ownership 或贡献
证据。

## 排序规则

- 每个匹配的 `CODEOWNERS` 路径添加一个主导 ownership 分数。
- 对每个维护者映射源,只使用最具体的匹配路径 route;仓库 fallback 只在没有
  scoped route 匹配时使用。
- 当前已验证的 primary contact 排名高于仅历史熟悉度,但低于匹配的 CODEOWNERS
  owner。Fallback contacts 权重较低。
- Trust 与 freshness 在源为 advisory、unknown 或 stale 时降低维护者映射权重;
  它们从不移除外部写 gate。
- 选定 base revision 上的 exact-path 与 module 历史,添加有界、recency 加权的
  熟悉度分数;feature-branch commits 不计。
- Git 历史中只发现的 bot 状身份被排除;显式仓库 ownership 规则保持权威。
- 多条变更路径的证据提高路径覆盖。
- 同时由 ownership policy 与历史支撑的候选获得高置信度;单一来源证据保持
  中或低。
- 被排除的 handles 在排序前移除。

分数只在这个 packet 内给证据排序。它们不得被解释为通用维护者排名或绩效指标。

## 必需边界

每个有效 packet 保留:

- `external_reads_performed: false`
- `external_writes_performed: false`
- `review_request_performed: false`
- `local_paths_captured: false`
- `raw_git_output_captured: false`
- `commit_emails_captured: false`
- `raw_reviewer_source_input_captured: false`
- `automatic_review_request_allowed: true`
- `automatic_request_policy: request_top_requestable_when_authorized`
- `external_review_request_authority_required: true`

`private_repo_state_read` 在预览中为 `false`,只有对 caller 批准 checkout 显式
`--execute` 后才为 `true`。Packet 中不应有任何 raw `CODEOWNERS` 文件、维护者映射
正文、raw git log、凭据、私有材料或运行时状态。公开来源引用与紧凑匹配路由证据
被保留,因为它们是审计线索。

## 人工与仓库 Policy Gate

任何外部 review request 前,host agent 或人工必须验证:

- PR author 与不可用 reviewers 已被排除;
- 仓库允许该请求,且任何 team handle 可请求;
- 每个声明的源是公开的、属于预期仓库上下文,并有诚实的 trust/freshness 标签;
- 推荐仍匹配最终 diff;
- ownership 不是仅从大量历史提交数推断的;
- 敏感或架构变更接受任何额外强制 review。

`loopx issue-fix reviewer-request` 在 fetch 实时 PR 元数据后消费同一证据。命令
必须记录独立的外部写决策,排除 live author 与现有 reviewers,并验证 provider
状态。本推荐 schema 绝不能被用作隐式 review-request authority。见
[issue_fix_reviewer_request_v0](issue-fix-reviewer-request-v0.md)。

## 计划中的扩展

未来版本可以添加带真实 callsites 的 repository-native 信号:

- 维护者可用性与显式 opt-out;
- 审阅响应与批准历史;
- 自动发现 checked-in reviewer-source packets;
- 生成或移动文件的语义模块映射;
- 风险类或敏感路径 reviewer 要求;
- stale review request 后的负载均衡与 fallback 升级;
- repository-host 对 teams 与非 noreply 作者的身份解析。

这些信号应扩展可解释证据 packet,而不是引入 OpenViking 特定适配器或独立
reviewer 状态机。

## 验证

运行:

```bash
python3 examples/issue-fix-reviewer-recommendation-smoke.py
```

Smoke 使用临时非项目特定仓库,验证 `CODEOWNERS`、最具体维护者映射 routes、
仓库 fallback、来源引用、trust/freshness、exact-path 历史、module fallback、
author 排除、CLI 执行、身份处理与无外部写边界。
