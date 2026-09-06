# content_ops_item_v0
> [English](content-ops-item-lifecycle-v0.md)

状态：provider-neutral 内容项生命周期契约 v0。

`content_ops_item_v0` 为现有 `content_ops` capability 提供针对文章、帖子、回复、转发与资料更新的稳定标识与转换契约。它是托管运维队列背后的状态层。它不是发布者，也不存储草稿正文。

## Item 边界

一项 item 存储：

- 稳定的 `item_id`、`item_kind` 与 channel；
- 正值 revision 加精确的 `sha256:` 内容摘要；
- 归本地/provider 存储所有的不透明 `content_ref` 与来源引用；
- 审批、投递意图、投递与回读回执；
- 接替血统与最后应用的 event 摘要。

公开记录从不存储帖子/文章正文、凭据、浏览器 profile、登录状态、媒体载荷、原始 timeline 或私有源映射。未知字段会导致验证失败，使适配器无法静默增加它们。

## 生命周期

```text
captured -> draft -> review_ready -> approved -> delivery_ready
    |          |          |             |             |
    +----------+----------+-------------+-------> published -> readback_verified
                         \-> skipped
                         \-> superseded
```

`delivery_ready` 是可选的。当无需调度意图时，provider 可以从 `approved` 直接写入投递回执。

支持的事件有：

- `revise`：递增 revision 并清除审批/生效状态；
- `submit_review`；
- `approve`：把一个 owner 授权的审批引用绑定到一个 revision、摘要、生效类型、可选账户与可选时间窗口；
- `set_delivery_intent`：选择一个 provider 而不执行效果；
- `record_delivery`：记录一个已经发生的 provider 效果；
- `verify_readback`：证明精确 URL 与摘要回读；
- `revoke_approval`、`skip` 与 `supersede`。

每个事件都提供 `expected_state` 与 `expected_revision`。转换在过期状态、过期 revision、摘要不匹配、provider/account 不匹配、审批过期或 event id 被变更复用时失效关闭。对最新事件的精确重试返回 `already_applied`。

## 权限

生命周期验证审批、意图、投递与回读指向同一 item revision。它不创建审批权限。调用方必须在持久化 `approve` 事件之前，从已授权的 LoopX 决策或 provider 自有回执解析 `approval_ref`。

同样，`record_delivery` 不调用 provider。X（通过 Ego Lite）、一个文档发布器或另一个 extension 在其自有权限下执行外部效果，并写回紧凑回执。每个 CLI 包都报告 `external_writes_performed=false`。

## CLI

创建紧凑 item：

```bash
loopx content-ops item-create \
  --item-id launch-post-v1 \
  --item-kind post \
  --channel x \
  --content-digest sha256:<digest> \
  --content-ref draft:launch-post-v1 \
  --created-at 2026-08-03T09:00:00+08:00 \
  --format json
```

从调用方自有的 JSON 应用一个事件：

```bash
loopx content-ops item-transition \
  --item-json item.json \
  --event-json event.json \
  --format json
```

该命令返回更新后的 item、一个只读投影与 `content_ops_item_transition_receipt_v0`。持久化仍由调用方所有，使私有队列得以保持忽略状态与 provider 特异性。

## 与 X 的关系

[x_public_channel_ops_v0](x-public-channel-ops-v0.md) 仍是 X 专属的来源、草稿、审批与结果协议。其记录可投影到本通用生命周期中，而账户日历、精确草稿与 Ego Lite 会话状态保持本地。
