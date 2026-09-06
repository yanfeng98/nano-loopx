# content_ops_surface_v0

状态：公开安全状态界面契约 v0。

`content_ops_surface_v0` 是紧凑的创作者/自媒体运维状态界面。它让 LoopX 记住来源状态、角度选择、草稿状态、反馈效果、发布关卡与可复用物料记忆，而不把 LoopX 变成发布器，也不存储原始平台/聊天物料。

该界面刻意是通用 LoopX 模型之上的元层：

- 来源记录可以提升进普通 LoopX agent 或用户 todos；
- 反馈记录可以成为偏好提示、边界修正、改写 todos 或发布决策；
- 发布记录是关卡，绝不意味着隐式发布许可；
- 投影是只读视图，必须从紧凑源记录重算。

## 记录

| 记录 | 必需用途 |
| --- | --- |
| `source_item_v0` | 带 `source_status`、`freshness`、条款说明、署名与允许引用/使用策略的紧凑观察。 |
| `angle_candidate_v0` | 链接到来源项的候选内容角度，带受众、主题、偏好契合、证据质量、决策与跳过时的拒绝原因。 |
| `draft_item_v0` | 带来源映射、偏好提示、验证界面与 `publish_gate_id` 的大纲/草稿/改写状态。 |
| `feedback_signal_v0` | 用户或操作员反馈，带类型化效果：偏好提示、来源边界修正、改写 todo 或发布决策。 |
| `publish_gate_v0` | 外部发布的人类批准状态。草稿存在绝不允许自动发布。 |
| `material_memory_v0` | 带署名、复用边界、被拒角度与偏好提示的持久化来源安全库条目。 |
| `connector_trial_v0` | 在 LoopX 摄取真实来源记录之前，浏览器、聊天、文档或平台 connector 的仅元数据试验计划。 |

## 来源状态

`source_item_v0.source_status` 应使用以下之一：

- `public`；
- `private_needs_review`；
- `synthetic_public_safe`；
- `unpublished`；
- `forbidden_for_public_surface`。

每个来源项还必须包括 `freshness` 与 `allowed_use`。v0 允许使用集是：

- `summarize_and_transform`；
- `metadata_only`；
- `do_not_quote`；
- `forbidden`。

这防止 connector 输出偶然变成原始证据。Browser、chat、platform 与 document connector 拥有原始检索；LoopX 只存储紧凑来源契约。

## Connector 试验

`connector_trial_v0` 让操作员开始测试真实 connector，而不把 LoopX 变成爬虫、发布器或私有归档读取器。试验只记录 connector 句柄、来源状态、新鲜度、允许使用、试验状态、提升目标与关卡。

首个 creator-ops 试验界面覆盖两条建议 connector 路由：

- 经 `ego-lite browser` 的 X：带 `access_mode=public_metadata_only` 的公开/条款感知信号摄取，不发帖、不转储登录关卡 timeline，只提升到紧凑 `source_item_v0` 记录。
- 经 `chatlog-alpha/chatview` 的微信：带 `access_mode=private_metadata_only` 的私有需评审物料摄取；LoopX 在 owner 显式批准来源使用前只存储仅元数据信号。

每个 connector 试验都必须设置 `external_write_allowed=false`。私有或仅元数据试验必须在来源正文使用、引用或发布前暴露用户 gate。

## 投影

`content_ops_surface_projection_v0` 是从紧凑界面派生的首屏状态视图。它应包括：

- `first_screen.waiting_on`：`user`、`operator` 或 `agent`；
- 来源评审、可草拟角度、反馈等待与发布决策的计数；
- 按状态、访问模式与 owner gate 的 connector 试验计数；
- 可提升进普通 LoopX todos 的 `todo_candidates`；
- 来源状态、草稿状态、反馈效果与发布关卡计数；
- 验证结果与公开/私有边界结果；
- 声明 `projection_is_writable=false` 的 `truth_contract`。

当操作员能回答以下问题时投影有用：

- 现在可以安全草拟什么；
- 哪个来源仍需评审；
- 哪个反馈改变了持久化偏好或边界；
- 哪个发布决策在等待；
- 发布受关卡时哪项侧工作可以继续。

## 边界规则

界面只有在以下条件满足时有效：

- 每个草稿有来源映射与发布 gate；
- 每个发布 gate 有 `approval_required=true` 与 `autopublish_allowed=false`；
- 原始私有物料、原始平台正文、凭据、本地路径与原始日志不在紧凑记录中；
- 私有或仅元数据来源在用户或 owner 评审改变来源状态前保持禁止引用；
- 外部发布、平台发布与生产动作保持在本契约之外。

## Fixture 与 Smoke

公开安全 fixture helper 实现在 `loopx/capabilities/content_ops/surface.py`。它提供：

- `build_content_ops_surface_fixture()`；
- `validate_content_ops_surface(surface)`；
- `project_content_ops_surface(surface)`；
- `build_content_ops_preview_packet()`。

CLI 预览是首个可运行 connector 试点入口点：

```bash
loopx content-ops preview --format json
```

它返回带 fixture、投影、验证、connector 试验计数与显式布尔值的 `content_ops_preview_packet_v0`，证明没有发生外部读取、外部写入、私有源正文读取或自动发布动作。真实 connector 适配器在摄取任何公开平台元数据或私有仅元数据来源句柄前，应首先匹配该包形状。

在真实 connector 决定读取什么之前，通用探索规划器可以渲染所选来源 lane、访问/读取状态、路由、回退、证据质量、提升目标与 owner gates：

```bash
loopx content-ops exploration-plan --format json
```

它返回带 `exploration_plan_v0` fixture 的 `content_ops_exploration_plan_packet_v0`。这是从 CS-Notes 探索能力图选出的首个可复用原语：仓库 issues、公开社交信号、私有聊天元数据与实验结果计数器都可以在捕获源正文、响应载荷、本地路径或外部写入前表示为 lanes。私有或原始物料 lane 必须投影具体用户 gate，而非静默成为可读工作。

仓库 issue fix 工作可以把公开 issue lane 提升为具体摄取包：

```bash
loopx content-ops issue-fix-intake --format json
```

它返回带基于 `exploration_plan_v0` 的 `issue_fix_intake_v0` fixture 的 `content_ops_issue_fix_intake_packet_v0`。包建模公开 GitHub issue/PR 元数据、所选代码上下文路由、候选 agent todos、owner/user gate 投影与下一安全动作。它不执行外部读取、不存储 issue 正文或评论正文、不记录本地路径或私有仓库状态，也不授权外部 issue 评论、指派、合并或 automerge。若修复路径需要私有复现物料，包把它保持为条件用户 gate，同时允许仅元数据分类与聚焦 smoke 草拟继续。

迈向真实 issue-fix 工作流的下一步是模拟 GitHub 元数据适配器预览：

```bash
loopx content-ops issue-fix-metadata-preview \
  --url https://github.com/owner/repo/issues/123 \
  --metadata-json mocked-provider.json \
  --format json
```

它返回 `content_ops_issue_fix_metadata_preview_packet_v0`。默认路径不执行实时 GitHub 读取；它接受公开 issue/PR 引用或模拟 provider JSON，且只复制仓库、issue ref、state、labels、updated_at 与 comments_count 等白名单元数据字段。issue 正文、评论正文、timeline 事件或 provider 响应载荷等原始字段只表示为受限字段名。包还为 agent todo 发出 `loopx_todo_writeback_preview_v0` 候选，但不写入 todo，除非后续命令显式执行该 writeback。

实时公开元数据读取只作为显式选择提供：

```bash
loopx content-ops issue-fix-metadata-preview \
  --url https://github.com/owner/repo/issues/123 \
  --fetch-metadata \
  --format json
```

选择路径使用 `gh api --jq` 只发出包消费的无正文元数据字段。公开工件记录 `external_reads_performed: true` 与 `adapter_preview.live_read_performed: true`，但 issue 正文、评论正文、timeline 事件、原始 provider 响应、stdout/stderr、本地路径、todo 写入、外部评论、PR 创建、合并与发布动作保持在该工件之外。

元数据预览只是摄取界面。Issue-fix 产品路径应继续到可执行验收循环：

```bash
loopx issue-fix acceptance-fixture --format json
```

该命令返回带已验证修复工件的 `issue_fix_acceptance_loop_v0`：失败的 repro、最小补丁、通过的聚焦验证与 PR 评审就绪证据包。参见 [issue_fix_acceptance_loop_v0](issue-fix-acceptance-loop-v0.md)。

首个可复用公开 connector 适配器是公开句柄观察命令：

```bash
loopx content-ops observe-public-handle \
  --url https://x.com/OpenAI \
  --source-item-id source_x_openai_public_handle_20260623 \
  --format json
```

它返回带紧凑 `source_item_v0` 的 `content_ops_public_handle_observation_packet_v0`。默认它对公开 `https` URL 执行一次仅 HEAD 元数据读取，拒绝 localhost/私有地址/带凭据/带查询 URL，不跟随重定向、不读取响应内容、不发送 cookie、不登录、不外部写入、绝不授予自动发布许可。确定性测试与干路由可以使用 `--no-fetch` 在无外部读取的情况下构建相同包形状。

包还携带 `content_ops_connector_runtime_policy_v0`。一次针对 X 的实时浏览器 connector 试验表明，打开普通公开 profile 页面可能自动加载 timeline、帖子文本、媒体流、分析与互动数据。因此公开句柄元数据摄取的安全默认是 `head_only_metadata_probe`；浏览器打开不是默认元数据路径。可复用 X 研究、草稿与受限发布行为请使用 [x_public_channel_ops_v0](x-public-channel-ops-v0.md)。账户特定发布日历、精确帖子正文、提及与操作员 skills 属于被忽略的本地状态或用户本地 Codex skills，而非公开仓库。

私有 connector 在访问任何来源前使用 gate 投影命令：

```bash
loopx content-ops project-private-connector-gate \
  --connector-id chatlog_alpha_chatview \
  --connector-name chatlog-alpha/chatview \
  --surface wechat_private_archive \
  --proposed-source-item-id source_wechat_metadata_signal_001 \
  --format json
```

它返回带 `owner_gate`、仅元数据 `source_item_v0` 占位符与具体 `user_todo_projection` 的 `content_ops_private_connector_gate_packet_v0`。它不执行外部读取、不读私有源内容、不外部写入、不发布。唯一安全下一动作是呈现 owner 决策：批准仅元数据摄取、拒绝它、或请求更窄来源句柄。真实 chatlog-alpha/chatview 摄取必须保持在该 gate 之后。

私有 gate 包还携带 `content_ops_connector_runtime_policy_v0`。一次针对公开 ChatView 入口点的实时浏览器 connector 试验表明，默认 web app 路由可能自动加载 message-list 与 message-detail API 请求。因此 LoopX 在 owner 批准前不得浏览器打开该默认路由。批准前，运行时策略禁止 `/api/messages`、`/api/reports` 与 `/api/channel-state` 等路径；connector 工作限于存储紧凑 gate 包、呈现 owner 问题与仅 fixture smoke 覆盖。

owner 显式批准有界 ChatView 试验后，只把批准的计数与路径类别变成可见操作员卡片：

```bash
loopx content-ops project-chatview-report \
  --channel-count 2 \
  --recent-record-count 50 \
  --report-count 5 \
  --api-request-count 54 \
  --api-path-count /api/channels=1 \
  --api-path-count /api/messages=1 \
  --api-path-count /api/channel-state=1 \
  --api-path-count /api/reports=1 \
  --api-path-count /api/messages/:id=50 \
  --format json
```

它返回带 `content_ops_chatview_connector_report_v0` 操作员卡片的聚合兼容 `content_ops_private_connector_gate_packet_v0`。命令不打开 ChatView、不保存响应载荷、不发出源正文、不授权发布。其输出可以直接作为 `--private-gate-packet-json` 输入传给 `aggregate-packets`。

Connector 包随后可以聚合成紧凑状态界面：

```bash
loopx content-ops aggregate-packets \
  --public-packet-json public-handle-packet.json \
  --private-gate-packet-json private-connector-gate-packet.json \
  --surface-id content_ops_connector_packet_aggregation \
  --format json
```

它返回带生成 `content_ops_surface_v0`、其只读投影、验证详情与边界布尔值的 `content_ops_packet_aggregation_v0`。聚合不重新打开 connector URL、不读源正文、不读私有物料、不外部写入、不授权发布。公开包变成 `metadata_packet_collected` connector 试验，而私有 gate 包保持 `needs_owner_gate`；这防止投影在公开包已收集后再调度另一个元数据试验。

对于操作员可见端到端工件，生成 walkthrough 包：

```bash
loopx content-ops walkthrough-artifact \
  --public-handle-url https://x.com/OpenAI \
  --channel-count 2 \
  --recent-record-count 50 \
  --report-count 2 \
  --api-request-count 54 \
  --api-path-count /api/channels=1 \
  --api-path-count /api/messages=1 \
  --api-path-count /api/channel-state=1 \
  --api-path-count /api/reports=1 \
  --api-path-count /api/messages/:id=50 \
  --private-preview-item-count 12 \
  --theme-signal "market-risk watch" \
  --theme-signal "semiconductor earnings pressure" \
  --format json
```

它返回 `content_ops_walkthrough_artifact_v0`：公开来源卡片、ChatView 操作员卡片、聚合投影、链步骤、草稿 gate 与私有操作员预览摘要。预览摘要可以说本地检查了多少私有记录，并列操作员整理的标签主题，但不得持久化源内容、响应载荷、本地路径、凭据或发布权限。这是展示价值的公开安全工件形状：用户可以在当前操作员会话看到实时私有物料，而仓库只记录紧凑计数、标签、关卡与验证。

持久化 smoke 是：

```bash
python3 examples/content-ops-surface-fixture-smoke.py
python3 examples/content-ops-preview-cli-smoke.py
python3 examples/content-ops-public-handle-observation-smoke.py
python3 examples/content-ops-private-connector-gate-smoke.py
python3 examples/content-ops-packet-aggregation-smoke.py
python3 examples/content-ops-chatview-report-smoke.py
python3 examples/content-ops-walkthrough-artifact-smoke.py
```

Smoke 检查记录覆盖、来源/草稿/gate 引用、首屏投影字段、connector 元数据试验路由、todo 候选、无自动发布策略、公开/私有边界卫生与公开句柄适配器的无内容/无写入保证。它还验证私有 connector 摄取的每个私有源内容读取、聚合只把紧凑来源/gate 记录提升进状态界面之前投影了 owner gate 与运行时拒绝策略。ChatView 报告 smoke 验证真实试验形状操作员卡片保持仅元数据，且可以在无源正文或响应载荷的情况下聚合。Walkthrough smoke 验证最终操作员工件保持公开安全，同时仍显示具体来源到界面到草稿 gate 链。实时 X HEAD probe 只在显式设置 `LOOPX_LIVE_PUBLIC_HANDLE_SMOKE=1` 时可用。
