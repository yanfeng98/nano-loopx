# Community Discussion Provider 契约

`community_discussion_scan_v0` 是围绕一个仓库的近期社区讨论的 provider-neutral、public-safe 快照。收集器发出类型化的 `discussion_fact_v0` 事实;消费者(周期性报告、社区漏斗、运营摘要)渲染或聚合事实,但不把缺失的 provider 重新解释为沉默。

## 所有权

| 组件面 | 所有者 | 职责 |
| --- | --- | --- |
| 契约 | `loopx-community-discussion` 扩展 | schema、事实类型、边界规则 |
| 观察 | GitHub REST/GraphQL + HN Algolia 收集器 | 带类型化值或警告的公开证据 |
| 渲染 | `loopx-community-discussion` | 确定性的 markdown 摘要 |
| 投递 | 运营方 | 精确把关的外部写入(Lark 等)绝不由本扩展执行 |

## 规则

- 事实以元数据为先:标题、来源 URL、作者、发布时间戳、相关性与 `dedupe_key`。原始 provider 载荷与完整帖子正文从不存储。
- 失败的 provider 表示为 `evidence.warnings` 条目加上幸存的事实,绝不表现为捏造的事实。
- GitHub 内部 `[Task]`/`[Benchmark]`/`[Sweep]`/`[Chore]` issue 作为非社区信号过滤。
- 维护者撰写的条目类型为 `maintainer_signal`;其他作者为 `external_discussion`,以便摘要优先展示用户的声音。
- 来自项目的公开推荐与组织的公开采纳声明类型为 `adoption_declaration`。它们是最具门槛采纳证据(有人自我表明是用户并公开倡导);摘要必须把它们排在被动信号与普通讨论之上。
- HN 收集关闭错别字容错,要求精确子串匹配,以排除众所周知的 Loopxo/Looptap/looped-music/CrowdStrike 噪声。
- 凭据绝不属于请求或响应包的一部分;GitHub 认证只来自进程环境。
- provider 在开始任何网络工作之前,拒绝 `schema_version` 不匹配的请求。

## 证据

每次扫描携带 `evidence.sources`、`evidence.rate_limit_remaining` 与 `evidence.warnings`,以便下游报告可以审计新鲜度与部分 provider 可用性。
