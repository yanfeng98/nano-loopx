---
name: loopx-doc-registry
description: Use when a connected LoopX project is asked to read, remember, record, index, register, or use a durable project material such as a Lark/wiki/design doc, research note, SOP, owner packet, migration report, benchmark paper, or external material source. Use even when the user does not mention LoopX or doc registry.
---

# LoopX 文档注册表


对持久项目材料使用本技能。目标是让未来的 agent 从项目权威界面找到材料，
而不只是从聊天或个人记忆中找到。

## 默认路线

1. 从当前仓库或用户命名的项目解析目标项目与稳定的 `goal_id`。优先使用
   `.loopx/registry.json` 与
   `.codex/goals/<goal-id>/ACTIVE_GOAL_STATE.md`。
2. 如果材料属于该项目，则注册到该项目自己的权威界面。不要仅因为当前 worker
   发现了它，就把它注册进 `loopx-meta`。
3. 如果项目有受跟踪的 `docs/meta/DOC_REGISTRY.yaml` 或等价物，先更新它。
   如果没有，则通过 `authority_registry.topic_authority` 与
   `authority_registry.project_materials` 把 `.loopx/registry.json` 用作
   项目本地文档注册表。
4. 用脱敏的源契约运行 `loopx register-authority-source`。
   原始 URL、doc id、本地私有路径、评论与源正文不得存储在公开文件中。
5. 刷新状态或状态文件，使 review packet、只读地图、dashboard 与 heartbeat
   worker 能找到该材料。

内存扩展只允许作为辅助性个人提醒。当项目已连接到 LoopX 时，它们不能替代
项目本地权威注册。

## 命令形状

从目标项目中执行：

```bash
loopx --registry .loopx/registry.json register-authority-source \
  --goal-id <goal-id> \
  --source-id <stable-source-id> \
  --source-ref "<raw-url-or-private-path-to-hash>" \
  --source-kind <doc|lark_doc|wiki|paper|owner_packet|migration_report> \
  --role <public-safe-role> \
  --freshness <current|historical|unknown> \
  --owner-status <public-safe-owner-status> \
  --gate-status <readable|needs_access|owner_review_pending> \
  --boundary private_redacted \
  --revision "<public-safe-revision-label>" \
  --conflict-rule "<public-safe-conflict-rule>" \
  --topic <topic-key>
```

当源分类或目标项目不明显时，先使用 `--dry-run`。

## 停止条件

在以下情况下停止，改为写入项目本地 todo 或 blocker，而不是注册：

- 目标项目或 goal 不明确；
- 材料无法表示为公开安全元数据；
- 注册需要读取未被请求或未获允许的私有内容；
- 源与更新的所有者批准材料冲突，且冲突规则不明确。
