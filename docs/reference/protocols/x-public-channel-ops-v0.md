# x_public_channel_ops_v0

状态：公开安全 connector 与发布关卡协议 v0。

`x_public_channel_ops_v0` 定义 LoopX 如何在不存储原始平台物料、也不把本地操作员工作流变成公开仓库 skill 的情况下，支持公开 X/Twitter 研究、草稿准备与已批准发布。

本协议刻意保持通用。它不编码具体账户、发布日历、网红名单、发布文案、本地浏览器 profile 或私有来源库。

## 边界

LoopX 可以存储紧凑的 channel 操作记录：

- 来源句柄与公开 URL；
- 来源读取是仅元数据、公开内容读取还是受关卡；
- 帖子角度、来源映射、草稿状态、素材计划与批准状态；
- 外部写入结果指针，如发布后的公开帖子 URL。

LoopX 不得存储：

- 登录 cookie、浏览器 profile、凭据或会话工件；
- 原始 timeline、来自私有或登录关卡界面的原始帖子正文、原始回复、分析转储、媒体流或带私有状态的截图；
- 账户特定增长清单、私有操作员笔记或只对一个维护者有意义的精确发布时刻表；
- 尚未批准的帖子正文，就像它们是发布许可一样。

## 记录形状

### `x_source_observation_v0`

紧凑来源摄取记录。

必需字段：

- `source_id`；
- `source_url`；
- `source_status`：`public`、`public_metadata_only`、`login_gated_needs_owner_review` 或 `forbidden`；
- `read_mode`：`head_only_metadata`、`public_body_read`、`browser_observation` 或 `no_read`；
- `allowed_use`：`metadata_only`、`summarize_and_transform`、`do_not_quote` 或 `forbidden`；
- `terms_note`；
- `next_gate`。

对公开句柄默认为 `head_only_metadata`。浏览器观察不是默认，因为打开 X 页面可能自动加载 timeline、媒体、分析与互动数据。

### `x_draft_packet_v0`

不发送草稿包。

必需字段：

- `target_reader`；
- `angle_family`；
- `source_map`；
- `post_body`；
- `asset_plan`；
- `repo_or_product_link`；
- `mention_plan`；
- `timing_window`；
- `anti_spam_checks`；
- `publish_gate_id`。

包可以分发评审，但它不是发布许可。

### `x_publish_gate_v0`

显式人类批准记录。

必需字段：

- `gate_id`；
- `approval_required=true`；
- `autopublish_allowed=false`；
- `approved_body_hash`；
- `approved_assets`；
- `approved_time_window`；
- `approved_account_or_identity`；
- `revocation_check`；
- `stop_conditions`。

只有当前用户/controller 批准与精确正文、素材、账户身份与时间窗口匹配时，才可继续发布。

### `x_publish_result_v0`

已批准外部写入后的紧凑结果。

必需字段：

- `published`；
- 可见时的 `post_url`；
- `posted_at`；
- `account_identity_status`；
- `asset_upload_status`；
- `first_hour_monitor_plan`；
- 未发布时的 `blocker`。

不要存储 cookie、上传载荷、原始截图或互动转储。

## 发布时间策略

时机是建议，不是许可。当时机实质影响发布时，agent 应重新研究当前平台指引。

通用默认：

- 对于美国/欧洲开发者工具受众，当帖子应触及美东早晨与欧洲下午时，优先工作日 9:00-11:00 美东时间。
- 周二到周四通常比周五更强。
- 若限制在接下来的 24 小时，选择下一个可用的工作日 9:00-11:00 美东时隙，并留 30-60 分钟回复。
- 在 `x_draft_packet_v0.timing_window` 中记录时区转换。
- 若所选时间在首选窗口之外，将其标记为用户或业务约束，而非平台最优。

精确发布窗口是执行关卡，不是软 scheduler 提示：

- 用显式时区存储已批准窗口，例如 `2026-06-27 21:05-21:35 Asia/Shanghai`，加任何受众时间转换。
- 把 host 唤醒、RRULE 或 heartbeat 节奏当作重新检查关卡触发，而不是在批准窗口外发布的许可。
- 若 worker 在窗口前唤醒，它可以预检登录/账户/媒体状态，但不得提前发布。
- 若 worker 在窗口后唤醒，记录 `x_publish_result_v0` blocker 或本地 incident，请求新的精确批准，且不得以迟发「补上」。
- 不要依赖墙上时钟 RRULE，而不确认发布界面的 host 时区语义。

## 内容规则

对于 LoopX 发布或教育内容：

- 当主张是那样时，把类别命名为 `loop engineering`；
- 把「control plane」定义为 agent loop 周围的状态、关卡、证据、配额与交接，而非仅仅 dashboard 或前端；
- 当转化目标是仓库访问或安装时，强调 local-first 采用；
- 做开源主张时包含仓库/产品链接；
- 当一个强视觉有助读者理解机制时使用它；
- 少提人名，且只在帖子与其公开工作或当前对话相关时。

避免：

- 大量标记；
- 重复通用回复；
- 无依据的 benchmark、收入或客户主张；
- 私有截图或原始操作员状态；
- 从身份、登录状态或批准边界不确定的账户发布。

## Ego-Lite 浏览器使用

`ego-lite browser` 在已安装且用户已登录时可以用作用户控制的浏览器 channel。它是运行时 channel，不是持久化公开仓库依赖。

在用它处理 X 之前：

1. 验证请求动作在已批准的 `x_publish_gate_v0` 内。
2. 验证账户身份对该帖子可接受。
3. 只上传已批准素材。
4. 在 captcha、凭据、身份混淆、上传失败或帖子正文变更时停止。
5. 发布后只记录 `x_publish_result_v0` 紧凑字段。

## 反垃圾与回复策略

对于新账户或低信誉账户：

- 每条回复的第一段必须有目标特定证据；
- 请求必须具体且低压；
- 除非 owner 互动，否则一次回复后停止；
- 若公开评论或帖子被降权为垃圾，未经显式 owner 批准不得顶起、转发、编辑、删除或申诉。

公开潜在客户监控在 owner 批准正文读取之前，应优先仅元数据检查，如状态、评论数、降权状态、author association 与更新时间戳。

## 与 `content_ops_surface_v0` 的契合

本协议特化通用 content-ops 记录：

- `x_source_observation_v0` 是来源特定 `source_item_v0`；
- `x_draft_packet_v0` 是来源映射 `draft_item_v0`；
- `x_publish_gate_v0` 是 channel 特定 `publish_gate_v0`；
- `x_publish_result_v0` 是受关卡写入后的紧凑外部证据。

用本协议处理公开产品行为与可复用 connector 指导。把维护者特定社交媒体 skill、精确发布日历与账户操作笔记留在忽略的本地状态或用户本地 Codex skills 中。
