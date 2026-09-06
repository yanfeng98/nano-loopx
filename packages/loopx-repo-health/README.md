# loopx-repo-health

LoopX 的 public-safe GitHub 仓库健康快照 provider。它从 GitHub REST API 收集一组有界的公共仓库指标,并发出一个冻结的 `repo_health_snapshot_v0` 文档,供月度报告、社区漏斗监控与内容素材使用。

## 指标

- 计数:stars、forks、watchers、open issues、releases、contributors、采样的 PR 总数、采样的带评论 issue 总数。
- 流量(14 天窗口):仓库浏览量、克隆数、热门路径,以及推导的文档浏览量(需要仓库访问权限)。
- 延迟:PR merge p25/p75 与首次人工响应 p25/p75,由有界的近期样本计算。
- 近期 star 时间线:来自最新 stargazer 页面的按周桶统计。

每个指标都来自公开仓库数据。provider 从不接受或发出原始轨迹、基准证据、凭据或私有链接。

## 指标模型

快照组织为两组,让报告与摘要既能保持通俗语言,又能对齐 CHAOSS。

采纳与认知(易读,适合概要):

| 通俗说法 | 快照字段 | CHAOSS 对齐 |
| --- | --- | --- |
| 访问过仓库页面的人 | `traffic_14d.views.uniques` | activity/attention 代理 |
| 读过文档或 README 的人 | `traffic_14d.docs_views.uniques` | documentation activity 代理 |
| 克隆过仓库的人 | `traffic_14d.clones.uniques` | adoption/trial 代理 |
| stars / forks / watchers | `counts.stars/forks/watchers` | popularity/social proof |

社区健康(对齐 CHAOSS 工作组):

| 通俗说法 | 快照字段 | CHAOSS 对齐 |
| --- | --- | --- |
| 活跃贡献者数 | `counts.contributors` | bus factor 输入 |
| 首次人工响应时间 | `latency.first_response_*` | time-to-first-response |
| PR 合并周转 | `latency.pr_merge_*` | code review 延迟 |
| 发布节奏输入 | `counts.releases` | release frequency 输入 |

`traffic_14d.docs_views` 由 GitHub 返回的热门路径按一条分类规则推导:README、`docs/` 树(包括 blob/tree 链接)与 `wiki/` 树。其 `uniques` 是各路径 uniques 之和,不跨路径去重。消费者不得把缺失的指标重新解释为零;不可用的流量组件面报告为零并附带警告。

## 认证与边界

- 从环境读取 `GH_TOKEN` 或 `GITHUB_TOKEN`;请求包从不携带凭据。
- 大多数端点无需认证也能工作,但 GitHub 现在对 stargazers 列表要求认证,因此建议提供 token。
- 限流是 GitHub 的;收集器在 evidence 中报告 `rate_limit_remaining`,并在限流时快速失败并给出显式错误,而不是猜测。
- 延迟指标是样本,不是全历史百分位;快照在 `evidence.warnings` 中记录样本大小。

## 用法

受管理扩展调用(stdin 请求 → stdout 响应):

```bash
python3 -m pip install .
loopx extension install --manifest extension.toml --execute --format json
loopx extension run loopx-repo-health --input-json examples/request.json --execute --format json
```

直接 CLI:

```bash
loopx-repo-health --doctor
loopx-repo-health snapshot --owner huangruiteng --repo loopx --format json
loopx-repo-health snapshot --owner huangruiteng --repo loopx --format md
```

`schemas/request.schema.json` 与 `schemas/response.schema.json` 是带版本号的 wire 契约。provider 在返回结果前会对照 `repo_health_snapshot_v0` 验证自己的输出。

## 验证

```bash
python3 smoke/repo_health_snapshot_smoke.py            # 离线契约 smoke
python3 smoke/repo_health_snapshot_smoke.py --live owner repo   # 可选在线检查
```
