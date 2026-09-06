# loopx-community-discussion

LoopX 的 public-safe 社区讨论扫描器。它从公开来源 — GitHub issue 与 discussion,以及精确匹配的 Hacker News Algolia — 收集紧凑的 `discussion_fact_v0` 事实,并冻结成 `community_discussion_scan_v0` 文档,供周期性报告、社区漏斗监控或运营摘要使用。

## 事实类型

- GitHub:`owner/repo` 中最近的 issue(过滤掉内部 `[Task]` 样式条目)以及最近更新的 50 个 discussion。维护者撰写的条目类型为 `maintainer_signal`;其他作者的条目均为 `external_discussion`。
- Hacker News:精确的 `loopx` 故事,加上 `loop engineering` 生态文章。关闭错别字容错,要求精确子串匹配,因为 Algolia 的默认模糊搜索会返回数千条无关的 Loopxo/Looptap/looped-music/CrowdStrike 命中。
- `adoption_declaration`:来自项目的公开推荐与组织的公开采纳声明。这是最高门槛的采纳信号 — 作者自我表明是用户并公开倡导 — 摘要投影把它排在第一位,高于被动信号与普通讨论。

## 摘要排序

信号按采纳成熟度排序,而不是按数量:公开采纳声明与推荐排第一,其后是生态文章、媒体报道与打包分发触达,再后是维护者信号,最后是普通外部讨论与未回答问题(早期参与)。

该 provider 以元数据为先:标题、来源 URL、作者、时间戳、相关性与去重键。它从不存储原始 provider 载荷、完整帖子正文、凭据、本地路径或私有上下文。

## 认证与边界

- 从环境读取 `GH_TOKEN` 或 `GITHUB_TOKEN`,用于 GitHub Discussions 收集与更高限流配额;请求包从不携带凭据。
- Hacker News Algolia 无需认证。
- 不捆绑 X 与 Reddit。X 需要已登录的浏览器会话(例如 ego-browser)或官方 XMCP provider,而 Reddit 的公开 JSON 端点当前返回登录墙/限流。两者都在同一 `discussion_fact_v0` 契约之后,保持为精确把关的外部 provider。
- 本扩展不执行任何外部写入。发送摘要(例如到 Lark)是一个独立的、由运营方拥有的精确把关投递步骤。

## 用法

受管理扩展调用(stdin 请求 → stdout 响应):

```bash
python3 -m pip install .
loopx extension install --manifest extension.toml --execute --format json
loopx extension run loopx-community-discussion --input-json examples/request.json --execute --format json
```

直接 CLI:

```bash
loopx-community-discussion --doctor
loopx-community-discussion scan --owner huangruiteng --repo loopx --days 14 --format json
loopx-community-discussion scan --owner huangruiteng --repo loopx --days 14 --format md
```

`schemas/fact.schema.json`、`schemas/scan.schema.json` 以及请求/响应 schema 是带版本号的 wire 契约。provider 在返回结果前会对照 `community_discussion_scan_v0` 验证自己的输出。

## 验证

```bash
python3 smoke/community_discussion_smoke.py                     # 离线契约 smoke
python3 smoke/community_discussion_smoke.py --live owner repo   # 可选在线检查
```
