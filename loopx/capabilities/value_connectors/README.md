# Value Connectors 能力介绍


Value connectors 把外部渠道变成可复用的 LoopX 控制面输入。首条落地路径聚焦
公开 GitHub 元数据,因为它立即可用、不要求私有数据,用户本地安装 LoopX 后即可
运行。

## 快速开始

从仓库 checkout 安装 LoopX:

```bash
python3 -m pip install -e .
```

从未安装的 checkout 直接测试时,把下文中的 `loopx` 换成 `./scripts/loopx`,
让命令使用 checkout 代码,而不是 `PATH` 上旧的本地版本。

检查 connector 起步可用性:

```bash
loopx value-connectors install-check --format json
```

给新接入的 Agent 提供只读优先的 connector source map:

```bash
loopx value-connectors source-map --format json
```

检查 X/浏览器 connector profile:

```bash
loopx value-connectors install-check \
  --connector social_browser_x \
  --format json
```

在无网络访问的情况下探测公开 GitHub issue 或 PR:

```bash
loopx value-connectors github-public-probe \
  --url https://github.com/owner/repo/issues/1 \
  --format json
```

探测无正文的公开元数据:

```bash
loopx value-connectors github-public-probe \
  --url https://github.com/owner/repo/issues/1 \
  --fetch-metadata \
  --format json
```

监控经批准的 LoopX 评论后公开维护者是否回复:

```bash
loopx value-connectors github-reply-monitor \
  --issue-url https://github.com/owner/repo/issues/1 \
  --after-comment-url https://github.com/owner/repo/issues/1#issuecomment-123 \
  --fetch-metadata \
  --format json
```

该 probe 刻意只做元数据。它不读取 issue 正文、评论正文、时间线、原始 provider
载荷、认证材料或本地路径,也不能发评论、发消息、开账号或发布。reply monitor
遵循同样的边界:它只捕获评论作者、关联关系、时间戳与 URL 元数据,然后发出
`prepare_public_triage_note` 或 `wait_no_bump`。

## 所有权与兼容性

`value-connectors` 是既有 connector 命令与 packet schema 的兼容门面。它拥有
共享安装检查、信源映射与 gated 调用规划,但不拥有新的用户结果。每个 profile
声明服务调用方的结果能力;实现随被验证的 profile 逐个迁移过去,而这里 CLI 命令
保持稳定。

第一批完成的迁移是公开 GitHub probe/reply monitor 与 `social_browser_x` profile。
GitHub 实现与协议所有权位于 `issue-fix` 之下;social 信源、安装与 content-ops
试用契约位于 `content-ops` 之下。既有 `loopx value-connectors ...` 命令委托给
那些 provider。

## Connector Profiles

| Connector | 结果能力 | 绑定 | 用户现在可运行 | 外部写入行为 |
| --- | --- | --- | --- | --- |
| `github_public_channel` | `issue-fix` | migrated | 是 | 无 |
| `github_public_reply_monitor` | `issue-fix` | migrated | 是 | 无 |
| `content_ops_public_handle` | `content-ops` | native | public-handle 观测 | 无 |
| `social_browser_x` | `content-ops` | migrated | install-check、public-handle packet 与 gated plan | 需要精确 profile/发布/回复 gate |
| `agent_reach_ops_source_map` | `content-ops` | mapped | `loopx value-connectors source-map --connector agent_reach_ops_source_map --format json`; [profile 说明](docs/agent-reach-ops-source-map.md) | 每次外部写入都需要 publish/audit 记录 |
| `finance_market_snapshot` | 无 | 迁移至独立 extension | 仅迁移 packet;无 Finance 执行 | 无 |
| `botmail_identity` | `content-ops` | mapped | 仅 install-check | 需要精确发送 gate |
| `community_channel` | `content-ops` | mapped | install-check 与 plan | 需要精确账号/消息 gate |
| `community_discussion_public_sources` | `periodic-report` | extension 包 `loopx-community-discussion` | `loopx-community-discussion scan --owner <owner> --repo <repo> --format json` | 无(摘要投递是独立的精确 gated 外部写入) |

`migrated` 表示实现模块已由结果能力拥有。`native` 表示命令本来就位于那里。
`mapped` 记录预期所有者,而不假装实现已经移动。

`finance_market_snapshot` 仅被保留为升级迁移 id。它的 `source-map`、
`install-check` 与旧式 `plan --connector-id` packets 会把 Agent 指向独立打包的
`loopx-finance-value-discovery` extension,绝不执行 Finance 工作。参见
[迁移 packet](docs/finance-market-snapshot-probe.md)。不得再把旧 id 用于新集成。

## 为什么这不只是一个计划

`plan` 命令是安全层,但 `github-public-probe` 是真实的起步 connector。它让用户把
公开渠道 URL 转换为紧凑的 LoopX 元数据,再决定是否监控、起草回复、请求批准或
停止。

`social_browser_x` 有意多一层 gating。它依赖 ego-browser 提供已登录浏览器会话、
媒体上传、profile 维护、发帖与回复监控,但 LoopX 仍拥有可复用的控制面 packet:

- 把公开 handle 作为纯元数据信源条目观测;
- 在触碰浏览器之前规划账号/profile 工作;
- 对每次公开发帖、回复、图片、链接与提及要求精确批准;
- 记录一个资金、成本、需求或能力指标,加上一个 kill 条件;
- 把回复监控为紧凑信号,而不是复制原始时间线。

X public-handle packet 示例:

```bash
loopx content-ops observe-public-handle \
  --url https://x.com/loopxops \
  --source-item-id source_x_loopx_public_handle \
  --no-fetch \
  --format json
```

gated X 发布 plan 示例:

```bash
loopx value-connectors plan \
  --connector-id social_browser_x \
  --connector-kind browser_social_channel \
  --channel "X public post via ego-browser" \
  --stage external_write_request \
  --target-ref "one approved LoopX post" \
  --target-url https://x.com/loopxops \
  --external-write-requested \
  --money-metric "qualified workflow owner asks for LoopX setup help" \
  --success-metric "one audit, demo, or setup request" \
  --kill-condition "spam hiding, account-health degradation, or no workflow owner signal" \
  --format json
```

未来 connectors 应遵循同样的序列:

```text
install-check -> metadata probe -> value connector plan -> approval gate -> host connector execution
```

LoopX 拥有紧凑控制 packet 与价值指标。宿主产品或用户 connectors 拥有账号登录、
私有读取、外部发送与生产动作。

## Agent-Reach Ops Source Map

`loopx value-connectors source-map --format json` 让新接入的 Agent 无需阅读内部
文档即可拿到当前只读优先的 connector 目录。它包含已实现或经现场验证的信源
profile,例如公开 GitHub 元数据 probe、GitHub 回复监控、content-ops public
handles、浏览器类 X 研究,以及 Agent-Reach 信源路由。它还点名行动受限的 profile,
如 botmail 与社区回复,以免 Agent 把"可以发送"当成"可以自由读写"。

`agent_reach_ops_source_map` 是该 packet 中的一个 profile。Agent-Reach 被用作
信源路由器:先运行 `agent-reach doctor --json`,再从 GitHub、公开 web/RSS、V2EX
或 Bilibili 等可用路由收集只读信号。LoopX 存储紧凑 evidence cards、成熟度评分、
ops brief、草稿 packet、publish/audit 记录与监控状态。

该 profile 刻意信源优先、行动受限。广泛发帖的酌情权并不免除记录精确正文、
渠道/账号、时间、信源引用与停止条件的义务。参见
[Agent-Reach ops source-map profile](docs/agent-reach-ops-source-map.md)。

## 协议

参见 [`value_connector_plan_v0`](../../../docs/reference/protocols/value-connector-plan-v0.md)。
