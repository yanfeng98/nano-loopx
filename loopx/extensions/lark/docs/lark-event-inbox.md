# Lark 事件收件箱

> [English](lark-event-inbox.md)

LoopX 可以在不保持 agent 进程存活的情况下消费 Lark 反馈。该集成刻意把采集与
解读分开：

```text
Lark event stream
  -> host-managed collector
  -> .loopx/inbox/<channel>/*.json
  -> loopx lark-inbox drain
  -> loopx lark-inbox processing (optional reaction lifecycle)
  -> domain agent writes a todo, vision correction, artifact update, or rationale
  -> direct bot question: loopx lark-inbox reply (optional, configured sender only)
  -> unaddressed material: loopx lark-inbox material-review (effect/no-follow-up)
  -> loopx lark-inbox ack --message-id ... --execute
```

collector 是宿主基础设施。LoopX 可以校验本地私有 collector 配置、预览或显式安装
macOS `launchd` / Linux `systemd` 用户服务，并报告 supervisor 与事件总线健康。
安装的服务围绕 `lark-cli --profile <configured-profile> event consume` 运行一个
小型 LoopX collector 运行时，带上有界超时，因此 supervisor 下的 stdin EOF 无法
终止一个本应无界的消费者。当官方 npm 包暴露 Node 包装器时，LoopX 记录 Node 与
包装器的绝对路径，使 launchd 不依赖交互 shell 的 PATH。它在持久化前过滤，并按
Lark `event_id`/`message_id` 各写一条紧凑事件。直接提及（direct mentions）立即
持久化。对于没有直接提及的消息，运行时会回读当前消息及其直接父消息，且仅当父
消息发送者是配置 profile 的应用 id 时才标记为可行动。对他人、另一个应用或无法
校验的父消息的回复仍然被捕获，但不唤醒 agent。Agent 无需保持 websocket 打开。

### 可选的 Turn 起始 Agent 读取 hook

实时采集是首选入口，但长程 Agent 也可能需要在每个 LoopX Turn 开始时拉取有界的
provider 历史尾部。collector 配置可以 opt in 到 `turn_start_sync`。这不是仅后台
的同步：它是一个 pre-decision 能力 hook，顺序如下：

```text
turn-start hook
  -> 每条路由读取一页有界 provider 页
  -> commit 并回读 owner 私有 inbox 事件与游标
  -> 以一次幂等回应 ACK 每条新读取的待处理人类消息
  -> 在同一 CLI 调用中重算 quota inbox 紧迫性
  -> 当 hook 新读取到待处理消息时 agent_read_required=true
  -> 选定的 inbox 通道在普通工作前排空私有消息内容
  -> Agent 选择 steering / Goal replan / context capture /
     continue-current-work / no-follow-up
  -> 持久效果或 no-follow-up 回执 -> ACK
```

Core 拥有 provider-neutral hook 注册、输出预算、允许的 owner 私有写作用域、狭窄的
`provider_message_reaction` 外部写作用域、失败隔离与 `agent_read_required` 契约。
一个可能要求 Agent 阅读的 hook 还必须注册一个有界公开安全 `required_read`；通用
kernel 校验并去重它，随后实时决策把它镜像到两个交互通道，带
`ordering=before_work`。新的普通素材只通知，不替换选定的工作通道；未结算的持久
素材在下一 Turn 抢占时保留直接问题与已验证回复的即时回复通道优先级。
Lark extension 拥有该 drain 描述符、历史分页、provider 信封校验、私有游标与
inbox 回读。CLI 组合根在状态/quota 投影之前运行该 hook。原始内容只留存在本地
inbox 中，并通过注册的 drain 命令对 Agent 可见；它绝不进入公开 Goal 注册表、
hook 回执或 quota packet。

`empty`、`provider_contract_error`、权限失败与 provider 不可用之间的区分是强制
的。消息列表不匹配声明 provider schema 的成功信封会 fail closed，不能被当作空
inbox。Hook 失败与普通 Goal 状态隔离，但它在 `turn_start_capability_hook_dispatch`
中可见，且不声称已发生 Agent 阅读。

该 feature 默认关闭。仅在每条路由上以 `configured_chat_all` 与
`material_review.enabled=true` 启用它，使每条新接受消息进入 Agent 语义分流通道，
而不是被同步后忽略：

```json
{
  "schema_version": "lark_event_collector_config_v1",
  "enabled": true,
  "service_name": "loopx-project-context",
  "identity": "bot",
  "profile": "project-context-bot",
  "supervisor": "systemd",
  "consume_timeout": "30m",
  "turn_start_sync": {
    "enabled": true,
    "initial_lookback_seconds": 900,
    "overlap_seconds": 5,
    "page_size": 50
  },
  "routes": [
    {
      "route_key": "requirements-a",
      "chat_id": "oc_<local-private-chat-id>",
      "event_inbox_config": ".loopx/config/lark/requirements-a.json"
    }
  ]
}
```

每次完成的轮询从上次终点打开新前向窗口，带少量重叠。Inbox `message_id` 去重让
重叠重放安全。当一页报告 `has_more` 时，后续 Turn 在打开新窗口前先续用同一私有
页 token。初始回看限七天，重叠限五分钟，每条路由每个 Turn 至多读一页 50 条
消息。游标与 single-flight 锁身份组合公开安全 route key 与配置 profile、chat、
inbox 配置、inbox 路径与采集作用域的摘要。因此两个 Agent 作用域的 collector 可以
复用语义 route key，而不共享进度或永久拒绝对方的信源绑定；同一信源的重复注册
仍共享同一个 single-flight 边界。

只有直接 bot 提及是全部反馈契约时才使用 `addressed_only`。接受对 bot 消息的非
提及回复的评审或协作收件箱应使用 `configured_chat_all`：宿主 collector 按本地
私有 chat id 过滤、持久化该 chat 的每条消息，并在安排回复前通过消息回读校验
回复关系。整 chat 采集不是整 chat 激活；无关对话仍可供领域解读，但不被视为
面向 bot。

## 激活 provider

在为项目使用的 LoopX 运行时中一次性安装并显式激活捆绑 provider：

```bash
loopx extension install --bundled loopx-lark --execute --format json
```

配置的 `lark-inbox` 命令在 `loopx-lark` 缺失、禁用或不再匹配其 doctor 校验的
revision 时 fail closed。每个操作还要求其 manifest 权限：inbox 读/写、回复发送
或 collector 管理。`extension upgrade` 与 `extension rollback` 在切换前探测候选
revision。没有 Lark inbox 指针的 Goal 仍返回既有静默禁用 drain 投影，不需要该
extension，因此不使用 Lark 的项目不受影响。

Quota 与 Turn 规划也会在 extension 打开本地私有 profile/chat 配置之前解析
`lark.inbox.read`。缺失、禁用或过期的 extension 产生不可用的紧迫性投影，不读取
该配置，也不能安排 Lark 回复通道。兼容 CLI 在内部执行该组合；Agent 不传
provider、profile 或别名。

collector 服务是独立的宿主生命周期。禁用或切换 extension 会阻止其下一次
`collector-run` 启动，但不向已消费事件的进程发信号。禁用、升级或回滚 provider
时，停止或重启配置的 launchd 或 systemd 用户服务。

## 本地私有配置

收件箱是 opt-in。创建本地私有通用 Lark inbox 配置：

```json
{
  "schema_version": "lark_event_inbox_config_v0",
  "enabled": true,
  "inbox_dir": ".loopx/inbox/team-feedback",
  "capture_scope": "configured_chat_all",
  "material_review": {
    "enabled": true,
    "drain_limit": 20
  }
}
```

`inbox_dir` 必须保持在 `.loopx/inbox` 之下。目标 ids、成员 ids、profile 名称、
原始 provider 载荷与凭据留在本地私有配置或宿主状态中，不得进入公开 LoopX
packet。

`capture_scope` 为兼容默认 `addressed_only`。该模式下 drain 输出报告
`thread_complete=false` 与一个覆盖警告。对于 `configured_chat_all`，collector 的
jq filter 应只选择配置的 chat；不要添加内容级 `@bot` 谓词。Goal Topic 根是展示与
回复上下文，不是 `configured_chat_all` 的额外入口过滤器：同一配置 chat 中的新
话题与回复必须保持对绑定 Agent 可见。当多于一个整 chat Goal 路由对同一 Bot
目标可选时，路由 fail closed，而不是按迭代顺序选一个。

`material_review` 是一个独立、默认关闭的调度边界。它要求 `configured_chat_all`；
启用后，不需要 Bot 回复的捕获消息与规范化附件产生 `material_review_due`。
`drain_limit` 限 1–100，默认 20。直接问题、提及与已验证的 Bot 回复继续使用
`reply_due` 并优先，因此 material review 绝不授予出站回复权威。

可选信源线程回复是另一个独立、默认关闭的边界。把显式非默认 bot profile 绑定到
同一本地私有 chat。`addressed_only` 收件箱可以回复精确捕获的信源消息，但仍保持
`thread_complete=false`，无法发现未提及的后续消息；完整协作线程请使用
`configured_chat_all`：

```json
{
  "schema_version": "lark_event_inbox_config_v0",
  "enabled": true,
  "inbox_dir": ".loopx/inbox/team-feedback",
  "capture_scope": "configured_chat_all",
  "reply": {
    "enabled": true,
    "sender_profile": "project-review-bot",
    "sender_identity": "bot",
    "bot_display_name": "Project Review Bot",
    "chat_id": "oc_<local-private-chat-id>",
    "processing_reaction_emoji": "OnIt"
  }
}
```

对每个启用回复的 Inbox，缺失 `reply.received_reaction_emoji` 默认值为 `Get`。把它
显式设为空字符串即禁用该 provider 写入。该回应与信源线程回复属于同一显式发送者
边界，但只有 Agent 的 Turn 起始 hook 可以创建它：实时采集持久化事件而不回应，
hook 在读取并确认仍待处理的人类消息后才写入回应。因此该回执表示"已读入 Agent
处理链"，而不是"collector 已存储事件"、"Bot 被提及"、"应回复"或"处理完成"。
提及、回复、问题与 material-review 分类仍是独立的调度与响应决策。

该 hook 独立于此可选 provider 写入，把首次读取记录在 owner 私有状态中。因此由
实时 collector 更早捕获的消息，即使回应被显式禁用，仍要求 Agent 阅读。失败的
回应从该持久待读集合重试，只要消息仍未结算，包括在有界历史游标已越过消息时间戳
之后。Provider 失败递增紧凑失败计数，但不丢弃 Inbox 事件，也不授予执行权威。
重放使用每次 Turn 起始分发一个聚合有界尝试预算。Collector 作用域的私有游标在
分发之间轮转路由优先级，而每条路由保留自己的私有轮转消息游标。公开回执只暴露
尝试与延迟计数，绝不暴露游标或消息身份。有持久 received/processing 回执的消息
无额外 provider 调用即被跳过。旧话题中的新回复有新的 provider 消息身份，因此
前向历史尾部独立于话题年龄与确认积压地捕获它。

`reply.processing_reaction_emoji` 可选，且要求一个不同的 received 回应。默认
`Get` 满足该要求；当读取确认被显式禁用时，processing 回应也必须禁用。两者都
配置时，宿主应在解读可行动条目之前立即运行 `lark-inbox processing`。LoopX 先加
processing 回应，再移除 received 回应。已验证的信源线程回复移除任何剩余生命周期
回应。如果 provider 无法删除回应，操作以可重试的清理状态失败，而不是声称完成。

回应 ids 只存储在配置 inbox 下的 owner 私有回执台账中。每次消息迁移以私有逐消息
锁序列化。prepared/created 操作回执在外部效果前后围住 provider 创建：常规回执
无法持久化的回应从已知回应 id 恢复而不再创建；id 被持久记录前结果变得不确定的
输出阻塞重放，而不是冒重复风险。LoopX 只删除通过配置 bot profile 写入所产生的
回应 ids；它绝不按 emoji 类型删除其他参与者的回应。格式错误的私有状态 fail
closed。

回复路径绝不使用机器默认 profile。任何发送前，它校验命名 profile 解析到预期 bot，
且该 bot 可以读取配置 chat。Profile/应用不匹配报
`lark_inbox_reply_sender_identity_mismatch`；无法访问配置 chat 的 profile 报
`lark_inbox_reply_sender_not_in_configured_chat`。两种失败都不回退到另一应用。
公开结果只含紧凑状态/回执字段，不含 profile、chat id、消息 id、回复文本或
provider 载荷。

## 宿主 collector 生命周期

在 Git 项目中，保持 collector 配置被忽略且未跟踪。非 Git 项目只能把它放在
`.loopx/config` 之下；父 Git 边界与该私有根之外的路径仍被拒绝。配置引用通用
inbox 配置，但拥有仅宿主的信息，如 chat id 与 supervisor：

```json
{
  "schema_version": "lark_event_collector_config_v1",
  "enabled": true,
  "service_name": "loopx-lark-feedback",
  "event_key": "im.message.receive_v1",
  "identity": "bot",
  "profile": "project-review-bot",
  "supervisor": "launchd",
  "consume_timeout": "30m",
  "lark_cli_bin": "lark-cli",
  "routes": [
    {
      "route_key": "requirements-a",
      "chat_id": "oc_<local-private-chat-id-a>",
      "event_inbox_config": ".loopx/config/lark/requirements-a.json"
    },
    {
      "route_key": "requirements-b",
      "chat_id": "oc_<local-private-chat-id-b>",
      "event_inbox_config": ".loopx/config/lark/requirements-b.json"
    }
  ]
}
```

打包的生命周期只接受 `im.message.receive_v1`、bot 身份、隔离的 `loopx-` 服务名与
`configured_chat_all`。Config v1 要求每条路由唯一的小写公开安全 `route_key`，消费
一个 profile 绑定事件流，并把每个配置 chat 路由到独立的 inbox 配置与 inbox 路径。
缺失、不安全或重复的 route keys、重复 chat 路由、共享 inbox 路径、回复 chat
不匹配与路由 profile 分歧都会 fail closed。每个接受的事件持久化配置的 route key，
因此聚合 drain 给 Agent 稳定的需求上下文身份，而不暴露私有 chat id。缺失或不匹配
的持久化 route key 也 fail closed，而不是静默重分类旧消息。因此每个 inbox 保留
独立的 pending/processed 状态与信源上下文回复放置，而一个 Bot 可以服务于多个
chat 而无竞争消费者。v0 单 chat 形态仍被接受并规范化为一条路由。Plan、install、
run 与 status 输出只暴露路由与健康计数；它们绝不返回 profile 值、chat ids、本地
路径、生成的 jq 或凭据。

启用 collector 必须绑定显式非默认 Lark CLI profile。`profile` 省略时，LoopX 可
复用共享启用 inbox 回复 `sender_profile`；每条路由回复 profile 必须解析为同一
值。两者都出现时必须匹配。生成的服务把 profile 绑定 collector 配置传给 LoopX
运行时，运行时把 `--profile` 放在`event consume` 与消息回读调用之前。因此采集、
回复目标校验与可选回复不能静默使用不同应用身份。公开 plan/status packets 只暴露
是否绑定 profile 及绑定来源，绝不暴露其值。
当 CLI 使用自定义 `--runtime-root` 时，生成的服务在 `lark-inbox collector-run`
之前记录同一 root；因此 supervisor 重启解析到与安装时校验相同的 extension 激活
状态。

```bash
loopx lark-inbox collector-plan \
  --project . \
  --config .loopx/config/lark/collector.json

# 先预览；这不会写入任何内容，也不启动任何进程。
loopx lark-inbox collector-install \
  --project . \
  --config .loopx/config/lark/collector.json

# 显式写入用户服务并启动/重启它。
loopx lark-inbox collector-install \
  --project . \
  --config .loopx/config/lark/collector.json \
  --execute

# 只读的 supervisor、事件总线与真实事件证据检查。
loopx lark-inbox collector-status \
  --project . \
  --config .loopx/config/lark/collector.json \
  --probe-event-bus
```

缺失 `lark-cli` 产生非阻塞安装提示。回复目标校验还要求配置 bot 能读取所选 chat
中的消息。Bot 身份群历史补追要求应用 scopes `im:message.group_msg` 与
`im:message.group_msg.include_bot:read`；后者让 Bot 自己写的消息保留在 provider
结果中。在 inbox 摄取之前，实时采集与有界历史同步都把 provider 类型化的 `app`
发送者与配置 profile 校验得到的精确应用身份比较。精确自匹配计数后被跳过；其他
应用与未解析身份保持可见，因此身份查找失败不会静默丢失消息。当 Bot list-messages
历史路径报告 provider 错误 `230027` 时，LoopX 必须同时呈示两个 scopes 与一个绑定
所选 App id 的官方 API 页面。Operator 启用应用 scopes 并发布新 App 版本；这不是
用户 OAuth 登录。这些要求属于 list-messages 历史能力。精确按 id 的水合
（hydration）与实时事件投递是独立能力，必须保持各自的失败状态与权限证据。LoopX
不认证 bot、不复制应用凭据、不静默授予 provider 权限、也不静默安装包。服务安装
是本地宿主写入，因此要求显式 `--execute`。Status 区分 `healthy` 与
`real_event_evidence_present`：运行中的订阅者可以在第一条消息之前即 healthy，
而真实集成的验收仍要求一条安装后事件出现在 inbox 中。

注册一个收件箱或 v1 路由 collector 作为 Agent 拥有的 Goal 边界。后者在跨全部
配置 chat 暴露聚合、无内容的紧迫性的同时，保持一个权威与一个 Agent 通道：

```bash
loopx configure-goal \
  --goal-id <goal-id> \
  --lark-event-inbox-agent-id <context-assistant-agent-id> \
  --lark-event-inbox-config .loopx/config/lark/collector.json

# 检查预览后显式应用。
loopx configure-goal \
  --goal-id <goal-id> \
  --lark-event-inbox-agent-id <context-assistant-agent-id> \
  --lark-event-inbox-config .loopx/config/lark/collector.json \
  --execute

# 通过同一 Agent 通道排空所有配置 chat。每条条目保留路由特定的
# 信源上下文回复指引；消息作用域的后续命令精确解析一个隔离收件箱，否则 fail closed。
loopx lark-inbox drain \
  --goal-id <goal-id> \
  --agent-id <context-assistant-agent-id>
```

配置目录按需暴露该可选能力。Quota 投影 `enabled`、`config_pointer_registered`、
一个本地控制命令与无内容的紧迫性摘要；它绝不投影私有路径、消息 ids、发送者或
消息正文。摘要包含 pending/direct-question/direct-mention/verified-bot-reply
计数、路由 inbox 计数与最老待处理年龄。它不暴露路由 chat ids 或 profile 名称。
对配置 bot 所写消息的配置直接提及或已验证回复，在普通监控或推进工作之前成为高
优先级 `lark_event_inbox` 工作通道。生成的心跳体力行实际 Goal 边界
`drain_command`；`loopx --registry <invoked-registry> lark-inbox drain --goal-id
<goal-id>` 沿共享注册表的 `source_registry` 走到规范项目，再解析被忽略配置。因此
它从链接或独立 worktrees 中保持正确，而不把控制状态绑定到 `--project .`。禁用或
空 inbox 是安静零花费路径，所以不用 Lark 的项目保持默认行为。

## Drain 与确认

```bash
loopx lark-inbox drain \
  --project . \
  --config .loopx/config/lark/event-inbox.json

loopx lark-inbox processing \
  --project . \
  --config .loopx/config/lark/event-inbox.json \
  --message-id om_xxx

# 仅在检查预览后执行。
loopx lark-inbox processing \
  --project . \
  --config .loopx/config/lark/event-inbox.json \
  --message-id om_xxx \
  --execute

loopx lark-inbox ack \
  --project . \
  --config .loopx/config/lark/event-inbox.json \
  --message-id om_xxx \
  --execute
```

Drain 只读，返回有界本地私有消息内容。一条消息必须在其效果写回后才确认。重复
事件文件按 `message_id` 合并；重复确认幂等。`processing` 同样幂等：重试复用已
记录的 processing 回应，并完成任何未决 received 回应清理，而不创建另一个
processing 回应。

对于未点名素材，请使用专用结算命令而非回复。它接受事件绑定的已提交外部效果
回执，或显式 no-follow-up 理由。后者变成确定性 `no_follow_up` 效果回执；重复
执行返回 `already_settled` 而不重复 ACK。回执重放/冲突检查、台账提交与已处理
消息 ACK 共享每收件箱锁。台账保持台账优先，因此中断后的重试修复尚未写入的 ACK，
而不丢失并发回执或已处理消息更新。

```bash
loopx lark-inbox material-review \
  --project . \
  --config .loopx/config/lark/event-inbox.json \
  --message-id om_xxx \
  --no-follow-up 'Informational material already captured.'

loopx lark-inbox material-review \
  --project . \
  --config .loopx/config/lark/event-inbox.json \
  --message-id om_xxx \
  --no-follow-up 'Informational material already captured.' \
  --execute
```

紧迫性分类保持本地。在 `configured_chat_all` 下，provider 原生提及证据在事件
持久化前规范化为紧凑 `addressed_to_bot` 标志。只有该类型化标志或 provider 校验的
直接回复可以产生 Bot 回复紧迫性；有界问题信号只在点名（addressing）被证实后才
区分直接问题。群中其他地方的问题、对另一成员的 `@` 提及、Bot 名称散文或对人类
的回复仍是 material review，不变成 `reply_due`。没有类型化点名的旧持久事件也
fail closed 到 material review。Agent 在决定持久效果或回复前仍先 drain 并解读
信源事件；摘要是调度信号，不是语义权威。

对于直接问题、显式 bot 提及或对配置 bot 的已验证回复，先写入请求的持久效果，
预览一条简洁回复，执行它，要求回读，然后才 ACK。新 Goal Topic inbox 配置使用
`reply.placement_policy=source_context`：顶层 chat 请求收到新的顶层 chat 回复，而
已处于话题内的事件收到该信源话题内的回复。没有该字段的既有配置保留旧式
`source_thread` 策略。`reply.editorial_style=bullet_points_preferred` 为结构化
回复投影 operator 提示；命令保留换行。

```bash
loopx lark-inbox reply \
  --project . \
  --config .loopx/config/lark/event-inbox.json \
  --message-id om_xxx \
  --text '已记录并修正。'

loopx lark-inbox reply \
  --project . \
  --config .loopx/config/lark/event-inbox.json \
  --message-id om_xxx \
  --text '已记录并修正。' \
  --execute
```

该命令使用由信源消息、解析放置与回复文本派生的幂等键，然后通过同一配置 profile
回读创建的消息。生命周期回应只在回读成功后移除。已发送但回应清理失败的回复返回
`sent_verified_cleanup_pending`；确认信源之前重试 `lark-inbox reaction-complete`：

```bash
loopx lark-inbox reaction-complete \
  --project . \
  --config .loopx/config/lark/event-inbox.json \
  --message-id om_xxx \
  --execute
```

普通闲聊保持不回复路径；启用该能力不授予评审者通知或其他出站权威。

对于包含 Lark `<at user_id="...">...</at>` 提及的文本回复，provider 回读可能以
`@_user_1` 之类的 token 替换标记，或在结构化提及元数据中保留 token 的同时把可见
正文呈现为 `@Display Name`。因此校验比较规范化可见文本模板，并要求每个提及解析
为发送时请求的身份。缺失、多余、歧义或不同解析的提及保持 `sent_unverified`；
仅显示名或原始标记相似不被接受。通知风格的字面 `@Name` 文本在任何 provider 调用
前被拒绝；请解析精确 chat 成员并提供结构化 `<at ...>` 节点。同一出站校验器用于
顶层评审者通知，因此回复与主动发送路径不能对"已投递提及"的定义不一致。两条路径
在发送前都做 provider dry-run，并校验创建的消息，而不是把消息 id 当作投递证明。

使用配置的主动发送表面，而不是原始 provider 命令：

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

`route_key` 在多 chat collector 下选择一条隔离的需求/chat 绑定，缺失或未知时
fail closed。顶层发送既不要求也不虚构信源消息，因此其校验放置始终为
`chat_root`；信源消息回复继续保留信源上下文放置与回应清理。

## 有界历史对账

实时事件订阅不回填 collector 启动前发送的消息，更早的 `addressed_only` collector
也已省略未点名回复。用 Lark CLI 抓取有界信源对话，把每条消息投影为
`lark_event_inbox_event_v0`，然后把 JSON 数组或 NDJSON 管道给通用导入器：

```bash
<bounded-lark-message-export> \
  | loopx lark-inbox ingest \
      --project . \
      --config .loopx/config/lark/event-inbox.json \
      --execute
```

Ingest 校验 ids 与 schema、按 `message_id` 去重、只写入配置的本地私有 inbox，并
返回计数而非消息内容。它不确认导入的消息；领域 agent 必须在 ACK 前写入每个可
行动效果。Provider 支撑的实时与历史入口也上报 `self_message_skipped_count`；
原始通用导入不能声称该校验，因为它们不拥有配置 Bot 身份。

评审者通知去重先使用持久生命周期回执，再使用持久化 `configured_chat_all` inbox
中的精确 PR 链接证据，最后对配置 chat 做有界用户身份搜索。缺失
`search:message` 权限降级到两个持久信源，不创建 user gate；其他 provider 读取
失败仍是阻塞项，因为无法安全确立"不存在"。

## 领域绑定

收件箱本身不知道消息为何重要。一个领域 capability 把通用事件流绑定到自己的解读
与写回规则。例如，issue-fix 可以把评审者群消息变成 PR 描述更新、Kanban 上下文、
视觉修正或显式 no-follow-up 理由。其他领域可以消费同一收件箱，而不采用任何
issue-fix schema 或生命周期。

对于 issue-fix，出站 GitHub 评审者请求与出站 Lark 通知仍是独立义务。Lark
inbox 只是入站反馈路径。
