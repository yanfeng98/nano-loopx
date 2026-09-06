# content_ops_queue_projection_v0
> [English](content-ops-queue-v0.md)

状态：只读托管队列投影 v0。

`content_ops_queue_projection_v0` 是调用方自有 `content_ops_item_v0` 记录的队列界面。它不是发布者，从不存储草稿正文。输入 item 文件的顺序即优先级顺序。

## 边界

该投影仅由经校验的 item 记录推导：

- 稳定的 `item_id`、`item_kind`、channel、state、revision 与不透明 `content_ref`；
- 状态计数与终态计数；
- 首个可行动的非终态 item 作为 `next_action`；
- 不包含草稿正文、凭据、浏览器状态、媒体、私有源映射或本地路径。

## CLI

投影调用方自有的队列：

```bash
loopx content-ops queue-status \
  --item-json items/launch-post-v1.json \
  --item-json items/community-recap-v1.json \
  --queue-id loopx-x-operations \
  --generated-at 2026-08-10T02:00:00+08:00 \
  --format json
```

该命令报告 `external_reads_performed=false`、`external_writes_performed=false` 与 `autopublish_allowed=false`。

## 事实契约

`queue-status` 是只读投影。审批、投递与回读仍须经过 item 生命周期与精确的 owner 授权记录；队列界面本身没有发布权限。
