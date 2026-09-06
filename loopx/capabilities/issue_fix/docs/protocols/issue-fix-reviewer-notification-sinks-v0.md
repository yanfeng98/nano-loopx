# issue_fix_reviewer_notification_sinks_v0

> [English](issue-fix-reviewer-notification-sinks-v0.md)

`issue_fix_reviewer_notification_sinks_v0` 用有界的二级投递扩展 canonical GitHub
reviewer request。第一个适配器发送一条幂等的 Lark/飞书群消息,点名同一个
repository-grounded reviewer,然后回读该消息。Sink 不选择不同 reviewer,也从不
用自身替代 GitHub review 状态作为事实源。结果契约与适配器注入点是
provider-neutral;公开 CLI 目前只暴露有界的 `lark_chat` 适配器。

## 在流程中的位置

顺序固定:

1. `reviewer-plan` 从 repository-native 证据对候选排序;
2. `reviewer-request` 验证 author 排除,并通过正式请求或其仅权限 fallback 评论
   建立 canonical GitHub 覆盖;
3. 配置的二级 sinks 通知同一个已验证 reviewer;
4. `pr-lifecycle` 继续从 GitHub 派生 review 状态。

在无写预览模式下,sink 可以对照选中的 reviewer 校验其本地配置。在执行模式下,
除非 canonical GitHub 通知已验证,否则二级发送被跳过。二级失败单独报告,不抹掉
成功的 GitHub 请求。

## 可选 Reward Memory Gate

Reward Memory 是默认关闭、agent-scoped 实验。如果已连接 goal 启用它,且注册
caller 的实验包含确切的 `reviewer_artifact.summary` surface 并设
`automatic_recall=true`,reviewer request 规划会运行共享有界 hook,即使二级
sinks 缺席或有意暂停,也可以产生只读
`reviewer_artifact_reward_memory_preview`。配置的二级通知要求同一个
`issue_fix_reviewer_artifact_reward_memory_application_v0` packet 在发送前通过
其通知 gate。Caller 自备 `--agent-id`、简洁的 model 创作中文
`--reviewer-summary` 与紧凑 `--reviewer-summary-reasoning`;LoopX 从不推断或
冒充另一个 peer。

适配器复用 provider-neutral 的 Reward Memory core 与 goal 的本地 provider
binding。OpenViking 可能支撑该 binding,但它不是协议依赖或硬编码仓库。外部投递
前,gate 检查确切 surface、当前 PR 身份与 permalink、current-artifact 验证、
memory readback、归因 digests、应用状态与非空摘要。不同 PR 的 receipt 不能重放。

实验解析与读权威构建发生在 sink 路由之前。归一化 corpus 提供读权威种类,归一化
standing policy 提供 `authority_source_ref`。无 sink 预览可以读取配置的 provider,
但从不发送通知、物化通知生命周期行或执行外部写。Sink 配置只改变 application
receipt 是否成为投递的必需项。自动召回关闭时,该边界执行零 provider 调用。

这种更严格的行为局限于配置的二级效应。Canonical GitHub review request 或
仅权限 fallback 先执行,并且对 Reward Memory 保持 fail-open。缺失、过期或不可用
的记忆只以 `reward_memory_reviewer_artifact_unverified` 阻塞二级通知;它不会把
普通 Issue Fix 工作变成用户 gate,也不会压制 GitHub 请求。

独立 `reviewer_notification.before_send` surface 可以在配置的二级适配器运行之前
立即提供投递 policy。它执行一次有界自动召回,只接受一条单一不同的活跃
`hard_policy`,其 `content_summary` 是 schema 为
`issue_fix_reviewer_notification_delivery_policy_v0` 且 `delivery_policy` 有效的
紧凑 JSON 对象。应用 gate 验证确切 surface、当前 PR 身份、current-artifact
检查、结果 readback 与非空记忆归因。通过的回执优先于显式 sink policy;否则显式
sink policy 保持 fallback。两者都没有时,投递不受限制。Provider 失败、无匹配、
无效内容或冲突 policies 都 fail open,从不变成用户 gate。现有 sink 仍拥有队列
receipts、幂等性、外部发送与 readback。

## 本地私有输入

`--notification-sinks-json` 消费
`issue_fix_reviewer_notification_sinks_input_v0`。该文件刻意是本地 capability
packet,而不是公开 issue-fix 状态:

```json
{
  "schema_version": "issue_fix_reviewer_notification_sinks_input_v0",
  "receipts": [],
  "delivery_policy": {
    "timezone": "Asia/Shanghai",
    "allowed_local_time": {"start": "09:00", "end": "21:00"},
    "outside_window": "queue_without_send"
  },
  "sinks": [
    {
      "sink_kind": "lark_chat",
      "sink_instance_key": "project-review-lane",
      "identity_scope": "project_dedicated",
      "reader_profile": "project-user-profile",
      "reader_identity": "user",
      "sender_profile": "project-review-bot-profile",
      "sender_identity": "bot",
      "bot_display_name": "Project Review Bot",
      "destination_id": "<private-chat-id>",
      "reviewer_identities": {
        "@service-owner": {
          "member_id": "<private-member-id>",
          "display_name": "Service Owner"
        }
      }
    }
  ]
}
```

显式的 reader/user binding 校验对已批准目的地的访问。Sender/bot binding 独立
验证专用 bot 身份,并在该 app 的 `open_id` namespace 中、执行发送加 readback 之
前验证映射的 reviewer 成员资格。任一 binding 都不依赖机器的活跃/默认 Lark
profile。旧 `bot_profile` 字段对显式手工配置仍被接受,但 goal-default 配置要求
两个 bindings。

执行模式在任何目的地读取或发送前,验证配置 reader 的用户凭据。不可用或未验证的
用户凭据返回无内容 blocker `reviewer_notification_reader_auth_required`,并执行
零外部写。这是现有 reader binding 的认证 gate,不是 reader 与 sender profiles
应该被折叠或重写的证据。运维者用 `lark-cli auth login` 恢复配置的 reader 用户
登录;LoopX 把 profile 名称与凭据细节留在公开结果之外。

发送前,LoopX 通过三个有界证据层去重一个 PR 通知:持久化的 PR-lifecycle
receipt、持久化 `configured_chat_all` inbox 中的精确 PR 链接匹配,以及配置 chat
的用户身份搜索。远程搜索是证据增强,不是动作 authority 边界:如果该用户 profile
缺少 `search:message`,LoopX 记录 `permission_fallback`,继续依赖持久化
receipt/inbox 证据,而不是投影用户 gate。成功的远程匹配以同一稳定 receipt 写回;
非权限的 provider 失败保持 fail-closed。

`delivery_policy` 可选且 provider-neutral。其有效来源顺序是:已验证的
`reviewer_notification.before_send` 应用,然后此显式 sink 值,然后无限制默认。
配置后,执行模式只在当前本地时间位于半开 `[start, end)` 窗口内才发送;支持跨夜
窗口。窗口之外,LoopX 不执行 provider 调用,返回 `queued_until_window`,附带紧凑
`issue_fix_reviewer_notification_queue_receipt_v1`。V1 receipt 还持久化
public-safe 摘要及其是否来自已验证 Reward Memory artifact,因此后续 drain 不会把
中文 reviewer 摘要退回 raw PR 标题。无效时区、时间或窗口外 policy 会 fail
closed。Preview 保持只读,从不转换为排队执行。执行路径使用可信调用时钟进行该
决策;公开 `--generated-at` artifact 字段不能把发送移入或移出投递窗口。

分组状态 monitor 用以下命令 drain 到期 receipts:

```bash
loopx issue-fix reviewer-notification-drain \
  --goal-id <goal-id> \
  --project <project> \
  --execute \
  --format json
```

这是刻意的队列 schema 切换:现有
`issue_fix_reviewer_notification_queue_receipt_v0` 行必须在启用分组 drain 前
手工迁移到 v1。运行时不保留 v0 兼容 reader,因为 v0 行缺少持久化的中文摘要,
无法满足当前 reviewer-message 契约。检测到 v0 行会以
`reviewer_notification_queue_v1_migration_required` fail closed;它从不被静默
当作空队列。

一次有界调用扫描 review-required 状态桶中的每个排队 PR;它不每个 PR 创建一个
`continuous_monitor`。每条消息前,LoopX 刷新紧凑实时 GitHub 状态,并为已关闭、
已合并、draft、已批准或 reviewer 集被完全覆盖的 PR 取消过期队列。发送仍是每个
消息一个 PR(且每个配置 sink 至多一条消息),并只在语义 readback 与 receipt
持久化后完成。如果只有部分排队 reviewer 已审阅,drain 只面向剩余 reviewers。
临时 CI 或分支状态变化保持队列完整,且 drain 总是复用 v1 receipt 中冻结的时区
与允许本地时间窗口。从当前配置移除的 sink 只取消其自己的过期 receipt;该 PR 的
其他配置 sinks 独立继续。

语义历史去重是 sink-scoped 的。单一 Lark sink 可以使用 goal 级
`feedback_inbox_config`;多个 Lark sinks 必须各自声明自己的
`feedback_inbox_config`。如果多 sink inbox 无法归因到单个 sink,drain 会 fail
closed 并保留队列,而不是压制另一 chat 的投递。有界执行还报告
`remaining_due_pr_count`,并在已验证或已取消工作与由投递窗口持有或留给下一
`--limit` 批次的到期行并存时,返回 `partial_drain`。

Profile 名称、`destination_id` 与 `member_id` 是执行输入。它们从不被复制进结果、
领域状态、todo、Kanban、PR 或公开日志。第一个契约要求命名、项目专用的 sender
profile 与预期 `bot_display_name`,每次发送前验证 live bot 身份,并拒绝
共享/默认或不匹配身份。这防止长程员工静默地以无关应用的身份发言。

身份映射在两侧都验证前是 advisory:GitHub handle 必须来自 live author-excluding
reviewer packet,messaging member 必须在已批准目的地解析。缺失或模糊映射在发送前
产生 `reviewer_notification_identity_unresolved`。

## Authority、幂等与验证

允许 canonical request 的同一个长久 reviewer-notification authority 可以允许
显式配置的二级 sink。`--execute` 是写断言;preview 从不调用 provider。

每个逻辑 `(repository, PR, sink instance, reviewer set)` 产生稳定 `sha256:`
幂等 key。Lark 适配器从该 digest 派生 provider-bounded key,而不暴露在人类可见
消息中。消息使用公开 PR 元数据指名 PR、可用时的关联 issue,以及修复的紧凑摘要。
完整验证过的 key 作为 receipt 返回。调用方只在现有 issue-fix 状态中存储该紧凑
receipt,并在重试时传回;匹配 receipt 返回 `already_notified`,不调用 provider。

对于已连接 goals,只注册 repo-relative 的本地私有指针:

```bash
loopx configure-goal \
  --goal-id example-goal \
  --issue-fix-reviewer-notification-config \
  .loopx/config/issue-fix/reviewer-notification-sinks.json \
  --execute
```

然后 `reviewer-request --goal-id example-goal --project ...` 自动发现配置。执行
模式在任何外部通知前加载 PR 现有 lifecycle 行,或从一次新的紧凑 GitHub lifecycle
读取自动物化它,把已验证的哈希 receipts 合并进私有输入,并把新已验证 receipts
或紧凑排队投递元数据写回同一行。重启保留排队项;之后成功的已验证发送移除匹配
队列项,同时保留稳定 receipt。窗口外的重试返回 `already_queued` 与原始队列
receipt,因此 provider 与本地状态都不变。重试因此保持幂等,无需第二个 ledger。
Live reviewer 路由对未发送工作是权威:已由 GitHub 覆盖的 reviewer 只能以该同一
reviewer 身份被通知,绝不被不同映射 sink 身份替换。每次 execute reconciliation
原子替换 PR 的未发送队列,在覆盖变化、review 完成或不再有当前 sink 身份时取消
过期目标。已验证 receipts 只增,从不被该队列替换取消。任何外部写前的 provider
失败保留匹配的当前队列项用于重试;写后未验证结果不会重新排队并冒重复发送风险。
Goal boundary/status 投影只暴露 capability 与指针已配置;从不暴露指针值或
profiles(`config_pointer_registered=true`)。

零退出码不足够。适配器要求发送响应中的 message id,用同一专用 bot profile
fetch 该消息,并验证 id 与 PR URL。结果区分 `preview_ready`、
`queued_until_window`、`already_queued`、`sent_verified`、`already_notified`、
`sent_unverified` 与 `gate_required`。权限或群成员错误成为具体
`lark_bot_group_access_required` gate。

## 专用 Bot 设置

对于 Lark sink,为项目 lane 提供一 app/bot 身份,只授予发送与群/成员解析所需的
scopes,publish app,并让目标群的 owner 或 admin 安装它。本地命名 CLI profile
显式选择 reader 与 sender 凭据。该契约从不回退到机器默认用户或 bot profile。

Setup gate 应该准确告诉 owner 修复哪个缺失不变量:

- 专用 app/bot 存在且具有预期的可见名称;
- bot capability 已启用且版本已发布;
- 发送与已批准 chat/member-read scopes 已授予;
- bot 是已批准目的地的成员;
- 每个 GitHub reviewer 映射到一个已验证的目的地成员。

## 公共安全边界

每个公开结果保持这些字段为 false:

- `private_destination_captured`
- `private_member_ids_captured`
- `private_bot_profile_captured`
- `raw_provider_payload_captured`

只有公开 PR URL、reviewer handles、sink kind、状态、紧凑 blocker 与哈希
receipts 可以离开适配器。凭据、raw member rosters、chat 标识符、消息标识符、
provider 错误与本地配置路径保持私有。

## 验证

运行:

```bash
python3 examples/issue-fix-reviewer-notification-sink-smoke.py
python3 examples/issue-fix-reviewer-request-smoke.py
```

Provider-neutral fixture 覆盖预览、专用身份执行、author 排除、身份解析 gates、
一次发送加 readback、稳定 receipt 重试、权限分类、未验证写入与公共安全脱敏。它
还覆盖正常与跨夜投递窗口、零调用排队与无效 policy fail-closed 行为。
Reviewer-request smoke 证明 sink 是真实 post-canonical callsite,而不是断开的
适配器,并验证跨生命周期重启的队列持久化/移除。
