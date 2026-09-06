# Repo-Health Provider 契约

`repo_health_snapshot_v0` 是 GitHub 仓库健康的 provider-neutral、public-safe 快照。provider 从 GitHub REST API 收集类型化观察并冻结成一个文档;消费者(月度报告、社区漏斗监控器、内容素材)渲染或聚合该快照,但不把缺失的指标重新解释为零。

## 所有权

| 组件面 | 所有者 | 职责 |
| --- | --- | --- |
| 契约 | `loopx-repo-health` 扩展 | schema、冻结指标 id、边界规则 |
| 观察 | GitHub REST 收集器 | 带类型化值或 `null` 的公开证据 |
| 渲染 | `loopx-repo-health` | 确定性的 markdown 投影 |
| Revision | 人工所有者 | 指标语义变更前的批准 |

## 规则

- 所有指标值为非负整数或 `null`;失败的收集表示为警告加 `null`,绝不是捏造的数字。
- `latency.pr_merge_*` 与 `latency.first_response_*` 是有界样本;evidence 的 `warnings` 列表标明样本大小。
- `traffic_14d` 需要仓库访问权限;不可用的组件面变成零计数并带警告,以便消费者区分"无流量"与"无访问权限"。
- `traffic_14d.paths` 是 GitHub 返回的有界热门路径列表(`traffic/popular/paths`)。`traffic_14d.docs_views` 由这些路径按单条分类规则推导:README(`/readme...`)、`docs/` 树(包括 blob/tree 链接)与 `wiki/` 树。推导出的 `uniques` 值是各路径 uniques 之和,不跨路径去重。
- 凭据绝不属于请求或响应包的一部分;认证只来自进程环境。
- provider 在开始任何网络工作之前,拒绝 `schema_version` 不匹配的请求。

## 证据

每个快照携带 `evidence.sources`、`evidence.rate_limit_remaining` 与 `evidence.warnings`,以便下游报告可以审计新鲜度与采样。
