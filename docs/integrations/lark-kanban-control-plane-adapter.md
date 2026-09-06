# Lark Kanban 控制面适配器


状态:原型适配器契约 v0。

该适配器在飞书/Lark Base Kanban 看板中为 LoopX 长任务控制面建模。它刻意只是
同一套 LoopX 理念的薄投影:todo、claim、user gate、交接、证据与运行历史。它
不替代执行器 runtime、配额守卫或未来的 daemon 租约模型。

看板是状态跟踪器与 claim 界面,不是任务规划引擎。它承载关键协调事实,使长时
运行的 Codex 会话可以看到可用工作、claim 一行、恢复自己的行并写回证据。新工作
仍然属于 LoopX todo 生命周期:拆分、后继、取代与新发现的任务应使用
`loopx todo add`、`loopx todo complete --next-*`、`loopx todo supersede` 或
类型化规划入口(intake)创建,然后用 `sync-loopx-todos` 投影回 Lark。

## 认证边界

适配器把诸如 `base_token`、`table_id`、`view_id`、`record_id` 等 Lark 资源
标识符传给 `lark-cli`。这些标识符仍会出现在命令证据中,因为它们对操作与审计
看板有用;适配器不把它们当作 AK/SK 密钥。

认证保持在所选 `lark-cli` 身份及其本地认证存储内部。适配器生成的命令绝不能
包含应用认证材料,例如 AK/SK 或 app-secret 参数。命令运行器会在子进程启动之前
拒绝那些内联携带密钥的选项。请用 `lark-cli auth login/status` 管理认证,而不是
把认证材料扩展进 Kanban 配置或命令载荷。

## 映射

| LoopX 概念 | Lark Base 字段 |
| --- | --- |
| Todo | 一行任务。`Task` 是可见标题。 |
| Todo 状态 | `Status` 单选:`Todo`、`Claimed`、`Running`、`User Gate`、`Blocked`、`Review`、`Done`。 |
| Claim | `Claim` 单选加 `Claimed By` 文本。 |
| User gate | `Status=User Gate` 加 `User Gate` 中的具体问题。 |
| 交接 | `Handoff` 文本。 |
| 证据 | `Evidence` 文本。 |
| 运行历史 | `Run History` 紧凑追加式文本。 |
| 范围 | `Scope` 文本,v0 中仅为建议。 |
| 配额 | v0 中省略;原型假设没有配额限制。 |
| Worker 启动 | `Worker Command` 与 `Workdir`,由 heartbeat 消费。 |
| Issue-fix 结果 | 一行稳定的 `Work Item Type=Issue Fix`,携带 `Repository`、`Issue`、`Pull Request`、`Route`、`Stage`、`Validation`、`Outcome` 与有界多选 `Context Tags`。 |

Kanban 视图按 `Status` 分组,因此看板是面向操作员的控制面。Agent worker 使用
过滤后的 `Worker Queue` 视图。

Issue-fix 执行 todo 与 issue 结果刻意保持为不同行。todo 回答接下来应该发生什么;
结果行回答一个 issue 发生了什么,并且在 PR 生命周期变化中始终以仓库加 issue
为键。它是从现有 LoopX issue-fix 状态派生的读模型,不是第二个工作流账本。

## 操作员视图

面向人类的 Kanban 卡片应刻意保持小巧。卡片上只保留以下可见字段:

- `Task`
- `Claim`
- `Priority`
- `User Gate`
- `Evidence`
- `Status`

其他所有字段保留在记录详情与 `All Tasks` 网格中。这使首页轻量易扫读,同时为
agent、交接、审计与恢复保留完整任务上下文。

Issue 工作有两个专属视图,使它不会淹没在 todo 队列中:

- `Issue Fix Outcomes`:按 `Work Item Type=Issue Fix` 过滤的网格视图;
- `Issue Fix Kanban`:应用相同过滤、按 `Stage` 分组的 Kanban 视图。

它们的可见字段是 `Task`、`Repository`、`Issue`、`Pull Request`、`Route`、
`Stage`、`Validation`、`Outcome`、`Context Tags` 与 `Status`。上下文标签暴露稳定
的路由、阶段、复现、验证与聚焦变更信号,而不复制自由格式的证据。这使现有
todo Kanban 保持紧凑,同时让每个 issue 的状态与输出可直接扫读。

`lark-cli` 1.0.56 暴露了 `base +view-set-visible-fields`,因此
`lark-kanban setup` 可以直接写入这份紧凑 Kanban 卡片字段列表。用以下命令验证:

```bash
lark-cli base +record-list \
  --base-token <base> \
  --table-id <table> \
  --view-id Kanban \
  --offset 0 \
  --limit 10
```

返回的 `fields` 数组应即上面这份紧凑操作员集合。记录详情仍包含完整 schema。

## 触发模型

直接从 Base 触发本地 agent 需要一个可到达的回调、本地 daemon bridge 或能够唤醒
边缘 worker 的产品端事件订阅。因此,当前 v0 原型使用 heartbeat:

1. Worker 轮询 `Worker Queue`。
2. Worker 选择一个 `Claim=Unclaimed` 的 `Todo` 行,或恢复自己的既有
   `Claimed`/`Running` 行。
3. Worker 写入 `Status=Claimed`、`Claim=Agent`、`Claimed By=<agent_id>`。
4. Worker 可以选择执行该行的 `Worker Command`。
5. Worker 写入紧凑的 `Evidence`、`Run History`、`Handoff`、`Last Error`、
   `Last Result Code` 与最终 `Status`。

这与云端到边缘的接入形态相符:云端看板是共享协调平面;受管 agent 包装器或
daemon 仍然负责启动并监督边缘执行器。原型命令为:

```bash
python3 -m loopx.cli lark-kanban heartbeat \
  --base-token <base-token> \
  --table-id <table-id> \
  --agent-id codex-kanban-worker \
  --execute-lark \
  --execute-worker \
  --allow-command-prefix "codex exec"
```

对可重复的本地验证,使用确定性的 worker 命令而不是 `codex exec`:

```bash
python3 -m loopx.cli lark-kanban heartbeat \
  --base-token <base-token> \
  --table-id <table-id> \
  --agent-id codex-kanban-worker \
  --execute-lark \
  --execute-worker \
  --allow-command-prefix "python3"
```

## 任务启动模型

Kanban claim 循环不应通过直接编辑 Base 来发明新行。当 worker 发现后续工作时,
应先对需求进行分类:

- 同切片续接:在评审之前把证据保留在当前行;
- 真实后继:用 `--next-agent-todo` 或 `--next-user-todo` 加显式
  `--next-user-task-class user_action|user_gate` 完成当前 LoopX todo;
- 替换或更窄的拆分:使用 `todo supersede --next-agent-todo`;
- 重策略的扇出:运行 `complex_request_intake_v0` 创建一个小的类型化 todo 批次。

该写回之后,`sync-loopx-todos` 更新状态跟踪器,并从现有 goal 域状态派生 issue-fix
结果行。这使任务身份、`todo_id`、gate、claim、issue/PR 生命周期状态与后继元数据
保留在 LoopX 中,同时让 Kanban 继续作为当前工作与交付输出的操作员可见跟踪器。

## 设置与复用

保存的 `.loopx/lark-kanban.json` 文件是可复用的目标绑定,不是自动化开关。常规
同步通过 `lark-kanban sync-loopx-todos` 保持用户驱动。Goal 可以显式启用
尽力而为的 heartbeat 刷新:

```bash
loopx configure-goal \
  --goal-id <goal-id> \
  --lark-kanban-heartbeat-sync \
  --execute
```

该 opt-in 不会创建看板、认证 Lark,也不会把 sink 投递变成 gate。它只在发生实质
性状态变化后,通过 `quota should-run.goal_boundary` 与
`interaction_contract.cli_channel` 投射一个 `post_writeback_actions` 条目;失败
保持非阻塞,且不能抢占可运行的 P0 工作。宿主自动化提示中不包含任何 Kanban
专用开关或命令。用 `--no-lark-kanban-heartbeat-sync` 关闭该行为。

推荐路径是 `setup`,默认使用用户身份。它预检 `lark-cli`、认证与所需的 Base
快捷方式,然后复用本地 `.loopx/lark-kanban.json` 看板配置,或创建新的 Base/表:

```bash
python3 -m loopx.cli lark-kanban doctor
lark-cli auth login --domain base --recommend
python3 -m loopx.cli lark-kanban setup --base-name "LoopX Kanban POC" --execute
python3 -m loopx.cli lark-kanban sync-loopx-todos --goal-id <goal-id> --execute
```

本地配置存储可复用的 Base 令牌、表 id、视图 id、身份与已同步的
`goal_id:todo_id -> record_id` 映射。该文件位于 `.loopx/` 下,该目录已被
gitignore。

对现有看板运行 `setup --execute` 也是 schema 对账路径。它列出当前字段,只创建
缺失字段,创建缺失的 issue-fix 视图,然后重新应用过滤、分组与可见字段配置。
现有 todo 行与稳定的结果 record id 会被复用。

要使用他人的共享看板,请存储其 URL 或 id:

```bash
python3 -m loopx.cli lark-kanban use --base-url "<shared-base-url>"
python3 -m loopx.cli lark-kanban config
python3 -m loopx.cli lark-kanban heartbeat --execute-lark
```

`sync-loopx-todos` 从 LoopX 注册表读取 goal 活动状态,并把开放的 user/agent
todo 以及派生的 issue-fix 结果行 upsert 到看板。user todo 成为 `User Gate`
卡片;被 claim 的 agent todo 成为 `Claimed`;被阻止/已完成的 todo 在被包含时映射
为 `Blocked`/`Done`。同步的 LoopX todo 刻意让 `Worker Command` 与 `Workdir`
保持为空,除非某任务行明确以 worker 启动行形式编写;共享看板绝不能接收原始
本地 checkout 或活动状态路径。

Issue 结果是派生的,不会单独持久化。每一条可行性行都会被投影;PR 生命周期行
只能通过显式匹配的 `repo` 与 `issue_ref` 丰富它。这避免了标题/分支猜测,并使
issue 网格与阶段 Kanban 成为默认同步路径的一部分。`--limit` 只约束活动 todo
行;它从不截断派生的 issue 结果来源投影。同步回执把这个拆分发布为
`limit_policy`,这样成功后不会在丢弃较新结果的情况下静默暗示完整性。

常规投影同步刻意是非破坏性的:在过滤、限长或更新的载荷中缺失的行绝不会被隐式
删除。当调用者拥有一个完整稳定的 `source_id` 命名空间时,可以请求显式的先预览
对账:

```bash
python3 -m loopx.cli lark-kanban sync-projection \
  --projection-file complete-projection.json \
  --include-done \
  --reconcile-source \
  --source-snapshot-complete

# 仅在审阅 source_reconcile.remote_orphans 与本地映射后运行。
python3 -m loopx.cli lark-kanban sync-projection \
  --projection-file complete-projection.json \
  --include-done \
  --reconcile-source \
  --source-snapshot-complete \
  --execute
```

对账拒绝:被 agent 过滤的输入、截断来源的行数限制、source-id 不匹配、遗漏 done
行以及不完整的远程分页。它只删除合成 todo id 属于该确切 goal 与来源命名空间的
远程记录,然后移除对应的或已缺失的过期本地 `goal_id:todo_id -> record_id` 映射。
幂等重试会计划零删除。

## CLI 界面

```bash
python3 -m loopx.cli lark-kanban schema --format json
python3 -m loopx.cli lark-kanban doctor
python3 -m loopx.cli lark-kanban setup --base-name "LoopX Kanban POC" --execute
python3 -m loopx.cli lark-kanban use --base-url "<shared-base-url>"
python3 -m loopx.cli lark-kanban config
python3 -m loopx.cli lark-kanban sync-loopx-todos --goal-id <goal-id> --execute
python3 -m loopx.cli lark-kanban sync-projection --projection-file <complete.json> --include-done --reconcile-source --source-snapshot-complete
python3 -m loopx.cli lark-kanban plan-create --base-name "LoopX Kanban POC"
python3 -m loopx.cli lark-kanban create-board --base-name "LoopX Kanban POC" --execute
python3 -m loopx.cli lark-kanban seed-task --base-token <base> --table-id <table> --execute
python3 -m loopx.cli lark-kanban seed-cases --base-token <base> --table-id <table> --execute
python3 -m loopx.cli lark-kanban heartbeat --base-token <base> --table-id <table> --execute-lark
```

除非显式执行标志被设置,否则 `setup`、`create-board`、`seed-task`、
`seed-cases`、`sync-loopx-todos` 与 `heartbeat` 都是 dry-run。worker 执行有自己的
gate `--execute-worker`,以及一个 allowlist gate `--allow-command-prefix`。

`seed-cases` 创建一个 UX 优化任务外加四个可行性用例:

- 一个 `notes.zaynjarvis.com` LoopX 架构/决策记录 lane;
- 一个带默认兜底的 P1/P2 human gate 超时 lane;
- 一个经由外部记忆的跨会话紧凑记忆 lane;
- 一个质量对 token 与注意力成本评估(quality-vs-token-and-attention-cost)
  eval lane。

## 评审边界

原型刻意让原始 agent 转录、凭证、本地私有路径与隐藏 benchmark 材料远离 Lark
行。`Evidence` 与 `Run History` 应包含紧凑的公开安全摘要或 artifact 指针。
`sync-loopx-todos` 绝不能从本地活动状态路径填充 `Workdir`。如果真实 worker 需要
存储详细日志或本地启动上下文,请把它们存在 worker 常规 trace 界面中,只写回
一个紧凑指针到 Base。

## 验证

运行 fixture smoke:

```bash
python3 examples/lark-kanban-control-plane-smoke.py
```

该 smoke 在不要求真实 Lark 凭证的情况下,验证 schema、看板命令计划、任务选择、
软 claim、worker 执行、证据写回、交接与 CLI fixture 路径。
