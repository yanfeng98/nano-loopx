# Lark 提供者（Provider）

> [English](README.md)

捆绑的 `loopx-lark` extension 提供可选的 Lark 执行与展示 providers。它不替代
LoopX 的 goal、todo、gate、quota、evidence 或恢复权威。

## 提供的能力

| 能力 | 结果 | 主要实现 |
| --- | --- | --- |
| `lark-event-inbox` | 收集、检视、回复并确认有界项目反馈 | [`event_inbox.py`](event_inbox.py)、[`event_collector.py`](event_collector.py) |
| `lark-reviewer-notification` | 通过项目专用 Lark 应用发送并校验评审者通知 | [`reviewer_notification.py`](reviewer_notification.py) |
| `lark-kanban-projection` | 把公开安全的 LoopX todo 与控制面投影渲染进 Lark Base | [`presentation/kanban.py`](presentation/kanban.py) |
| `lark-goal-channel` | 把一个已验证的 Lark 群组与投影表面绑定到一个 LoopX goal | [`goal_channel.py`](goal_channel.py)、[`goal_channel_setup.py`](goal_channel_setup.py) |
| `lark-explore-projection` | 把规范 Explore 结果投影进 Lark 表格、卡片与白板 | [`presentation/explore_results.py`](presentation/explore_results.py) |
| `lark-periodic-report-announcement` | 通过当前 Goal Channel 的已验证项目 Bot 投递周期报告，只提及其类型化受众计划选中的接收者 | [`periodic_report_delivery.py`](periodic_report_delivery.py) |
| `lark-miaoda-html-report` | 把已渲染的周期报告发布到 operator 选定的既有 Miaoda 应用 | [`presentation/periodic_report.py`](presentation/periodic_report.py) |

带提及的文本投递由 extension 的共享出站契约 [`outbound.py`](outbound.py) 拥有。
Inbox 回复与评审者通知使用相同的结构化 `<at ...>` 构造、provider dry-run 与精确
回读规则。可见的字面 `@Name`、成功的消息创建或匹配的展示文本都不是提及投递证据。
Provider 回读必须精确暴露发送时 `mentions[]` 请求的身份；缺失、多余、歧义或不同
身份都会 fail closed。需要通知语义的调用方必须使用这些 extension 表面，而不是
调用裸 `lark-cli` 发送命令。

对于收件箱配置的 Bot，用与回复相同的契约预览并校验一条主动顶层消息。多 chat
collector 需要其公开安全 `route_key`；单收件箱接受默认路由：

```bash
loopx lark-inbox send \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --route-key project-feedback \
  --text '<at open_id="ou_example">Example Reviewer</at> please review' \
  --provider-preflight

loopx lark-inbox send \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --route-key project-feedback \
  --text '<at open_id="ou_example">Example Reviewer</at> please review' \
  --execute
```

该命令只使用与选定 inbox 路由绑定的 owner 本地 profile 与 chat。它针对精确 chat
成员解析每个结构化身份、执行 provider dry-run、幂等发送，并回读创建的消息。它
不返回 profile、chat id、消息正文或原始 provider 载荷。安装与命令本身都不授予
新 Lark scope 或外部写入权威。

[事件收件箱指南](docs/lark-event-inbox.md) 记录了完整的 collector、处理、回复、
回应（reaction）与确认生命周期。
[Lark Kanban 集成指南](../../../docs/integrations/lark-kanban-control-plane-adapter.md)
记录投影配置与世系。

### 有界群历史补追

事件收件箱可以对账实时事件 collector 之前发送的消息。每次调用从一条配置的
`route_key` 读取一页升序内容，默认预览收件箱/游标迁移。`--execute` 先持久化并
回读每一条规范收件箱事件，再推进一个 owner 本地游标：

```bash
loopx lark-inbox history-catch-up \
  --project . \
  --config .loopx/config/lark-collector.json \
  --route-key project-feedback \
  --start 2026-08-01T00:00:00Z

loopx lark-inbox history-catch-up \
  --project . \
  --config .loopx/config/lark-collector.json \
  --route-key project-feedback \
  --start 2026-08-01T00:00:00Z \
  --execute
```

重试会从精确私有页 token 继续。已完成的窗口只有在其上覆盖边界仍然有效时才
免于再次 provider 读取而重放；后续调用会从之前结尾打开一个有界前向窗口，因此
既有群组或主题中的新消息不会困在旧的 `history_complete` 状态之后。调用方也可以
把一个已完成的历史窗口一次性扩展到更早起点；provider 只覆盖缺失的更早窗口，
并拒绝之后的信源/配置漂移。旧式 v0 游标保守迁移：它们可能重放已摄取的消息，
但绝不推进可能跳过未见历史的覆盖边界。返回的 link-evidence packet 包含 URL 以及
供 owner 本地 Agent 使用的消息与路由世系，但不含周围消息正文、发送者、chat id、
profile、游标或原始 provider 载荷。Inbox 与游标目录仅对 owner 开放，其状态文件
以 mode `0600` 写入。产品特定的 URL 分类与字段丰富策略仍由消费产品或私有 skill
负责。

游标绑定包含 route key、Bot profile、chat、inbox 配置、解析出的 inbox 目的地与
采集作用域。其中任何输入变化时，catch-up 在读取 provider 之前 fail closed，报
`Lark group-history cursor source binding changed`。恢复原路由即恢复，或者把
owner 本地的 `.loopx/inbox/.history/<route-key>.json` 游标移开，从显式 `--start`
重启；规范消息 ids 让 inbox 摄取保持幂等，而替换游标重建覆盖。

群历史读取使用配置的 Bot 身份，要求 Bot 是该群组成员、应用已发布，且具有
`im:message:readonly` 与 `im:chat:read`。权限错误 `230027` 以类型化
`group_history_permission_required` 返回；它绝不推进 inbox 或游标。

### 动态 collector 路由对账

已配置的收件箱可以不经手工重写完整 owner 本地 collector 文件而纳入 v1
多 chat collector。先预览路由，再显式应用：

```bash
loopx lark-inbox collector-route-reconcile \
  --project . \
  --config .loopx/config/lark-collector.json \
  --route-key project-feedback \
  --chat-id oc_<local-private-chat-id> \
  --event-inbox-config .loopx/config/lark/project-feedback.json

loopx lark-inbox collector-route-reconcile \
  --project . \
  --config .loopx/config/lark-collector.json \
  --route-key project-feedback \
  --chat-id oc_<local-private-chat-id> \
  --event-inbox-config .loopx/config/lark/project-feedback.json \
  --execute
```

该操作校验唯一的 route、chat、inbox-config 与 inbox-path 绑定；序列化并发写入；
通过原子替换写入；并回读精确绑定与配置摘要。重复同一请求是零写入的
`already_applied` 结果，而任何绑定漂移 fail closed。回执返回公开安全的
`route_key`，绝不返回 chat id、inbox 配置、本地路径、profile 或凭据。

配置回读并不能证明运行中的 collector 已加载新路由。因此每条成功的 plan/apply
回执保持 `runtime_reload_required=true`、`runtime_reload_performed=false` 与
`runtime_readback_verified=false`。部署 owner 必须重启或重装 collector，并独立
校验其运行时，才能把路由视为生效。移除路由仍是独立的 owner 授权生命周期操作；
这条增量命令绝不删除或重绑路由。

## 生命周期

显式安装捆绑 provider，然后回读其就绪状态：

```bash
loopx extension install --bundled loopx-lark --execute --format json
loopx extension doctor loopx-lark --execute --format json
loopx capability list --format json
```

禁用或回滚 provider，而不改变拥有它的 capabilities 或 Kernel 状态：

```bash
loopx extension disable loopx-lark --execute --format json
loopx extension rollback loopx-lark --execute --format json
```

对于 Miaoda，`loopx periodic-report publish-miaoda --request-json <path>` 先预览
一个类型化的托管投递意图。检查 profile 绑定的 sink、请求选定的应用与工件后再加
`--execute`。该命令把认证与外部发布/回读调用委托给 `lark-cli`；LoopX 不存储
凭据，也不把本地 HTML 生成当作托管投递。

对于 Lark 报告公告，Periodic Report profile 拥有符号接收者、领域与类型化路由
规则。核心在无 provider 身份的情况下编译相关性计划。Preview 不做身份查找或
发送；execute 只解析选定接收者并省略无关接收者。报告内容或卡片元数据中的裸
`<at>` 标记不能绕过该策略。Goal Channel 投递命令恰好接受两条有序 HTTPS 条目
（托管报告，然后 Lark 文档），发出两条相互幂等的消息，并为每次回读校验原生
发送者 App 与精确 chat。

安装控制可发现性与 provider 生命周期。每个私有 chat、app、群组、Base、文档或
Miaoda 目标都留在被忽略的本地配置中。外部写入仍要求拥有它的 capability 的
精确权威、gate、revision、幂等性与回读契约。

## Document-Comment Connector provider

`document_comment_provider.py` 把一个 owner 配置的 Lark 文档适配到
provider-neutral Agent 外部 Connector 运行时。它把认证与 API 调用委托给
`lark-cli`，探测精确的评论读/创建 scopes，并把一页有界评论或嵌套回复转成 owner
本地 inbox 事件。该适配器要求 `lark-cli` 1.0.69 或更新版本以支持
`drive +list-comments`；更旧的二进制 fail closed，且必须在 Connector 就绪前
升级。该 provider 支持配置信源与增量采集。在调用方提供显式提及身份契约之前，
它拒绝 `addressed_only`；它绝不猜测每条文档评论都面向 Agent。

Lark 评论分页为评论卡片与回复分别持有游标。适配器把两个阶段都持久化在私有
Connector 游标中，并从第一页评论重启已完成的扫描，依靠稳定哈希事件 id 与通用
inbox 去重。支持回应的绑定还必须配置 owner 本地回复回执存储。回复创建写入待处理
回执、精确回读回复、再把回执标记为 verified；只有该 verified 回执才允许通用
运行时 ACK 事件。已解决与整文档评论卡片在信源线程响应绑定中被跳过，因为
provider 不允许对它们回复。

文档 URL、`lark-cli` profiles、provider 游标、评论/回复 ids、原始载荷与回复回执
保持 owner 本地。公开状态只报告权限就绪、操作计数、inbox 健康与无内容的失败
码。所需 provider scopes 是：历史/回读的 `docs:document.comment:read`，
回复的 `docs:document.comment:create`；启用 extension 并不授予任一 scope，
也不发布应用。

## 所有权边界

- Extension 拥有 Lark 认证检查、provider 分发、有界载荷转换、投递回执与回读。
- 结果 capabilities（如 Issue Fix、Explore、Periodic Report）拥有领域请求并
  解读 provider 回执。
- Kernel 独自接受持久的 todo、gate、quota、evidence 与恢复迁移。
- Lark 投影是 sink。它们绝不成为控制面真相源。

声明式 capability 与权限表面维护在 [`extension.toml`](extension.toml) 中。
Provider 就绪绝不授予新权限，也不静默启用外部写入。

## 创建 LoopX 机器人（推荐权限集）

每个新的 LoopX 企业自建应用（例如 Goal Channel 的发送 bot）应一次性申请
推荐权限集，而不是边用边补。清单见
[`bot_scopes.py`](bot_scopes.py)（`RECOMMENDED_BOT_SCOPES`），按用途分三档：

- 核心（Goal Channel / reviewer / kanban）：`im:message`、`im:chat:read`、
  `im:chat:create`、`im:chat:update`、`im:chat.members:read`、
  `im:chat.members:write_only`、`contact:user.base:readonly`、
  `contact:contact.base:readonly`、`application:application:self_manage`、
  `application:bot.basic_info:read`
- 收件箱（事件订阅与群历史，敏感需审核）：`im:message:readonly`、
  `im:message.group_msg`、`im:message.group_msg.include_bot:read`、
  `im:message.p2p_msg:readonly`
- 交互/文档 sink：`cardkit:card:read/write`、`docs:document.comment:read/create/delete`

拿到 App ID（`cli_xxx`）后，可在开发者后台一键批量申请：

```text
https://open.larkoffice.com/page/scope-apply?clientID=<app_id>&scopes=<scope1%2Cscope2...>
```

（`recommended_bot_scope_apply_url(app_id)` 会拼出完整 URL。）随后用
`lark-cli config init --app-id <app_id> --app-secret-stdin --name <profile> --brand lark`
注册 bot profile，再走 `loopx goal-channel setup`。敏感 scope 需企业管理员审核。
