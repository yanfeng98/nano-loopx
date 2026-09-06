# 权威来源注册


`loopx register-authority-source` 为一个目标记录一个本地权威或材料来源，
而不存储原始来源引用。它适用于内部文档、私有仓库、owner 评审 packet 和验证快照
这些项目 Agent 需要 public-safe 投影而不是原始链接的场景。

命令写入所选来源注册表，通常是可被忽略的 `.loopx/registry.json`，
并可能把紧凑投影同步到共享全局 registry。公共仓库文件应只保留示例与契约。

## 注册表边界类别

LoopX 暴露一个注册表边界分类器：

```bash
loopx registry-boundary --path .loopx/registry.json --require-gitignored
```

在提交注册表相关工作前先运行它。它区分四个面：

| 边界 | 存储 | GitHub 策略 |
| --- | --- | --- |
| 项目本地私有注册表 | 一个仓库中的 `.loopx/registry.json` | 必须被忽略；不要 push |
| 共享全局-本地注册表 | `<runtime-root>/registry.global.json` | 仅本地控制面；不要 push |
| public-safe 投影 | 生成的、无原始引用的紧凑计数/角色 | 默认被忽略；不要把运行时注册表文件 push 到 GitHub |
| 公开示例 fixture | `examples/` 下手写的示例 | 仅在它是 fixture/契约而非活动状态时可跟踪 |

分类器报告 `classification`、`should_be_gitignored`、`github_push_allowed`、
`private_marker_count`、git 跟踪/忽略状态和任何边界风险。`loopx check` 也报告
活跃注册表边界，使发布时扫描能捕捉到意外被跟踪的本地注册表。

这个区分是刻意的：LoopX 提供注册表能力，LoopX 也应使用该能力来管理自己的
来源权威，但运行时注册表文件仍是状态，不是公共仓库产物。公共文档可以描述
schema、示例和紧凑计数；原始本地注册表、全局-本地注册表和生成的 public-safe
投影保持被忽略，除非它们被显式编写为示例 fixture。

## 最小命令

```bash
loopx register-authority-source \
  --goal-id example-goal \
  --source-id product-vision \
  --source-ref "https://example.invalid/private/doc" \
  --source-kind doc \
  --role current_authority \
  --freshness current \
  --owner-status owner_review_pending \
  --gate-status readable \
  --boundary private_redacted \
  --revision "rev-2026-06-07" \
  --conflict-rule "newer owner-approved source wins" \
  --topic product_vision \
  --dry-run
```

`--source-ref` 被哈希并脱敏。注册表存储 `source_ref_kind`、
`source_ref_sha256` 和 `source_ref_redacted=true`；不存储原始 URL、本地路径、
令牌或文档 id。

## 存储形状

本地注册表在 `authority_registry.project_materials[source_id]` 下接收一个紧凑材料条目：

```json
{
  "schema_version": "authority_source_registration_v0",
  "id": "product-vision",
  "role": "current_authority",
  "source_kind": "doc",
  "freshness": "current",
  "owner_status": "owner_review_pending",
  "gate_status": "readable",
  "boundary": "private_redacted",
  "revision": "rev-2026-06-07",
  "conflict_rule": "newer owner-approved source wins",
  "source_ref_kind": "url",
  "source_ref_sha256": "..."
}
```

同一紧凑来源被追加到 `authority_sources`，让本地 operator 能看到已注册来源。
全局同步通过现有 authority-registry 投影把它削减为摘要计数。

## 项目本地文档注册表机制

Doc registry 是通用的 LoopX 机制，不是 Agent-harness 特定的导入路径。
每个受管项目应在自己的项目本地注册表里拥有其权威面，通常是
`docs/meta/DOC_REGISTRY.yaml` 加上目标可被忽略的 `.loopx/registry.json`。
对没有受跟踪 `DOC_REGISTRY.yaml` 的已连接项目，可被忽略的
`.loopx/registry.json` 仍通过 `authority_registry.topic_authority` 和
`authority_registry.project_materials` 充当项目本地文档注册表面；
项目 Agent 不应把新的持久材料降级为仅记忆的笔记。

当项目 Agent 发现相关设计文档、研究笔记、benchmark 论文、owner packet、
迁移报告或外部材料时，默认顺序是：

1. 先识别目标项目和 goal。不要因为当前 worker 发现了材料，就注册进
   `loopx-meta`。
2. 如果材料属于那个项目，先添加或更新项目自己的文档注册表 topic/source 条目。
3. 用 `register-authority-source` 把紧凑材料契约注册进同一项目的
   `.loopx/registry.json`，或用 `import-doc-registry-authority` 导入另一个项目
   文档注册表的脱敏摘要。
4. 只把紧凑计数与脱敏哈希同步进共享全局注册表；原始路径、文档 id、私有 URL、
   评论和来源正文留在项目本地/私有权威面。
5. 刷新 status 或 state，使未来的 review packet、read-only map 和 heartbeat
   worker 无需依赖聊天记忆就能找到新权威。记忆扩展可以复制该提醒，
   但只能在项目本地权威注册完成或已记录具体 blocker 之后。

当一个 goal 需要另一个项目的 DOC_REGISTRY 风格映射作为上下文时，用
`import-doc-registry-authority`。当 Agent 找到了一个应加入当前项目权威映射的
材料来源时，用 `register-authority-source`。两种情况中，当前项目都是其自身
文档注册表和冲突规则的 owner。

## 执行者 Skill 契约

项目执行者应把文档注册表注册当作 skill 触发的流程，而不是元项目副作用。
文档注册表 skill 触发是任何引入持久权威来源或研究材料的任务，未来 Agent
可能需要用它来路由工作、验证决策或解决冲突。在依赖聊天记忆前，把该材料注册到
目标项目自己的文档注册表。用户在已连接项目里说的"记住这个设计文档"，
即使不提到 LoopX，也是文档注册表触发。

最小执行者顺序是：

1. 从 LoopX state 解析目标 `goal_id` 和项目注册表。
2. 把材料分类为当前项目所有、另一个项目所有或超出作用域。
3. 对当前项目材料，先更新项目本地文档注册表，再运行 `register-authority-source`
   并带脱敏来源契约。
4. 对另一个项目的注册表，只运行 `import-doc-registry-authority` 导入紧凑计数、
   主题键和哈希引用。
5. 在花 heartbeat 配额前运行相关 smoke 或状态刷新。

当目标项目含糊、材料包含无法脱敏成元数据的私有内容、或下一步需要读取被 gate 的
来源正文时，停止而非注册。这些情况下，写一个点名缺失权威决策的项目本地 todo
或 blocker。

## 边界

- 原始私有来源引用永不存储。
- `role`、`freshness`、`owner_status`、`gate_status`、`revision` 和
  `conflict_rule` 等元数据字段必须是 public-safe 摘要。
- 写入前用 `--dry-run`。
- 当来源注册表在 operator 检查紧凑投影前应保持纯本地时，用 `--no-global-sync`。
- 不要把读取或摘要来源正文当作注册的一部分。该命令记录来源契约；
  后续项目特定工作决定一个来源可否被读取。

## 导入文档注册表

`loopx import-doc-registry-authority` 从 DOC_REGISTRY 风格 YAML 文件导入权威契约，
而不把原始文档正文或原始注册表路径拷进存储 payload。它只读取：

- `default_entry_docs`；
- `topic_authority`；
- `status_definitions`；
- `version` 和 `updated_at`。

原始 `DOC_REGISTRY.yaml` 路径被哈希为 `source_ref_sha256`。本地注册表接收一个
`doc_registry_authority_import_v0` 材料条目，带 `default_entry_count`、
`topic_authority_count`、`status_definition_count` 和供本地 operator 定位的小样本。
共享全局同步保持通常的紧凑权威/材料计数。

```bash
loopx import-doc-registry-authority \
  --goal-id example-goal \
  --source-id external-doc-registry \
  --doc-registry-path ../external-project/docs/meta/DOC_REGISTRY.yaml \
  --role external_doc_authority \
  --freshness current \
  --boundary private_redacted \
  --topic external_doc_registry \
  --import-topic-prefix external_ \
  --max-imported-topics 50 \
  --dry-run
```

小规模手工挑选的本地主题键用 `--topic`；只有当导入 goal 应通过自己的权威映射
路由一个有界的外部注册表主题集时，才用 `--import-topic-prefix`。
