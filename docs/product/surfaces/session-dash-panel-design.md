# Session Dash 面板设计


自动生成的单页控制面板，从 LoopX public-safe 投影跟踪 agent session 任务进展与结果统计。

## 问题

Operator 想要一个紧凑、可复制的 "fleet 现在在做什么" 网页视图：哪些 session（agent runtime）存在、每个拥有多少 goal、每个 goal 处于什么状态。现有 React dashboard 以交互方式覆盖了这一点，但它需要 Node 构建、dev server 与浏览器工具。Loopback 单页面板是快速本地检查的更轻 surface：从项目目录运行一条命令，在 agent 工作期间保持标签页打开。

该面板刻意**面向人类**。LoopX 的内部控制机制（decision frames、work-lane 契约、quota slot 数学、truth 契约、source-warning 诊断、lease/write-scope 记账）不被渲染：它们对 operator 是噪音，属于控制面而不是观察 surface。页面只显示回答"工作进展如何？"的信号：

1. **概览** — session、goal、active / needs-you / blocked / done 桶、打开 todos 与 run 计数（结果统计）。
2. **Sessions** — 每个 session 一张卡，含其状态、角色、goal 数量与其拥有的 goals。
3. **每 goal** — 状态徽章、todo 进度条（完成 vs 打开的 agent/user）、它在等什么、最新 run 时间/分类与下一动作。

## 决策

添加一个**实时单页面板**（`loopx dash`），从既有 public-safe 投影提供 fleet 快照：

1. 收集 dashboard 已经消费的相同输入：status 契约（`attention_queue.items[]`）、`run_history.goals[]`、todo 索引、agent-management 投影（sessions + 其 `goal_ids`）与 usage 摘要。
2. 通过只读 fleet 投影（`build_session_dash_projection`，schema `session_dash_projection_v1`）折叠它们，把 goals 分组到 sessions 下并计算概览桶。
3. 用一个小的无依赖渲染器渲染单个 HTML 页，复用 `loopx/presentation/renderers/goal_channel_html.py` 中的模式。
4. 由 loopback HTTP server（`loopx/dash_server.py`）提供，该 server 还暴露 `/panel` 片段与 `/status.json` 投影；页面通过轮询 `/panel` 原地自动刷新。
5. 为一次性静态 HTML 快照保留 `loopx dash generate`，成功前执行既有 public/private 边界扫描。

React dashboard 保持交互 surface；loopback 面板是快速观察 surface。它们共享同一投影与数据契约，所以面板不会漂移成第二套事实源。

## 仓库位置

| 关注点 | 位置 | 理由 |
| --- | --- | --- |
| 渲染器 | `loopx/presentation/renderers/session_dash_html.py` | 针对已构建载荷的纯渲染器，符合呈现 surface 布局。 |
| 投影组装 | `loopx/presentation/projections/session_dash.py` | 中间 public-safe 读模型（fleet 快照）。尽可能复用既有构建器；不重复契约解析。 |
| 生成命令 | `loopx/cli_commands/dash.py` + `loopx/dash_server.py` | Operator 面向 CLI 入口（`loopx dash` 提供、`dash generate` 导出）；与 `serve-status` 完全一样读取 status/quota/todos。 |
| 静态导出 | 复用边界扫描 + `loopx dash generate` | 既有 public/private 扫描器；需要时 manifest/revision receipt 留在静态站点管线。 |
| 文档 | `docs/product/surfaces/` + dashboard README | 与其他呈现 surface 同属一个文档家。 |
| 验证 | `examples/session-dash-panel-smoke.py` | Public-safe fixture smoke，无需实时状态。 |

这是呈现 surface，不是新 capability：它不拥有状态、quota、gates 或 authority。按 capability 放置指南，它留在呈现层并复用既有控制面契约。

## 数据契约（输入）

投影只消费 public-safe 投影：

- `loopx status` JSON，schema_version 2：`attention_queue.items[]`（每 goal waiting_on / recommended_action）、`run_history.goals[]`（goal 状态、生命周期阶段、最新 runs）、`todo_index.items[]`（每 goal role/status）、`agent_management_projection.agents[]`（sessions：state、role、`goal_ids`、下一动作、最后活动）与 `usage_summary.totals`（runs 24h/7d）。
- 仅 public-safe evidence 指针；绝不使用原始 transcripts、日志、凭据或本地路径。

输入中发现的疑似原始键被记录为边界警告而不复制值，与 `goal_channel_projection` 行为一致。

## 投影形态

`schema_version: session_dash_projection_v1`，`mode: read_only`：

- `overview` — session/goal/run 计数、`goals_by_status` 桶（active / needs_user / blocked / done / other）、打开的 agent/user todos、完成的 todos、runs 24h/7d。
- `sessions[]` — 每个 agent runtime 一条：`session_id`、`role`、`state`、`next_action`、`last_activity_at`、`goal_count` 与 `goals[]`。
- `goals[]` — `goal_id`、`display_name`、`domain`、`status`、`status_bucket`、`waiting_on`、打开/完成 todo 计数、最新 run 时间 + 分类与 `next_action`。
- `unassigned_goals[]` — 未被任何 session 声明的 goals，避免有东西从 operator 视野默默消失。
- `focus_goal_id` — 传入 `--goal-id` 时，快照收窄到包含该 goal 的 sessions。

## 页面布局（单页）

单页按顺序渲染这些区块：

1. **Header**：面板标题、generated-at 时间、只读标记；设置 `--goal-id` 时的 focus 胶囊。
2. **概览条**：sessions、goals、active、needs-you、blocked、done、打开 todos、runs（24h）。
3. **Session 卡**：每 session 含其状态徽章、角色、goal 数量、最后活动与下一动作；下方是 goal 表，带状态徽章、todo 进度条、等待理由、最新 run 与下一动作。
4. **无 session 的 goals**（存在时）：为未被任何 session 声明的 goals 显示同样的 goal 表。

所有数据从上述投影渲染；页面不含写控件，也没有浏览器写权限。

## 命令 Surface

主要入口是实时 server：在项目 checkout 内运行 `loopx dash`，在浏览器打开打印的 loopback URL。单页跟踪 fleet 的 session 任务进展/状态，并通过重新获取 `/panel` 片段原地自刷新（默认每 10 秒），所以 operator 可以在 agent 工作期间保持标签页打开。

```bash
loopx dash                # serve the fleet panel at http://127.0.0.1:8767/
loopx dash --goal-id <id> # narrow the panel to one goal
loopx dash --port 9000 --refresh-seconds 5
```

路由：

- `GET /` — 带原地自刷新脚本的完整单页面板。
- `GET /panel` — 供刷新脚本使用的新鲜 `<main>` 片段。
- `GET /status.json` — 紧凑 session dash 投影 JSON。
- `GET /healthz` — 健康探针。

一次性静态快照仍可用：

```bash
loopx dash generate [--goal-id <id>] [--out dash.html]
```

- 不带 `--out`：把 HTML 打印到 stdout（或用 `--format json` 输出投影 + html 载荷）。
- 带 `--out`：写文件，并在报告成功前运行公开边界扫描。
- 该命令只读：从不变更 todos、quota、gates 或 registry。
- Server 只绑定 loopback（`127.0.0.1`）；它不暴露任何写路由。

## Public/Private 边界

- 输入只限于 status 契约与 public-safe 投影。
- 渲染器转义所有文本，绝不内联原始载荷值。
- 静态导出在成功前复用既有边界扫描器（绝对本地路径、私钥、凭据、token）。
- 负向夹具证明生成的页面拒绝私有资料；smoke 断言边界，而不是确切散文。

## 验证

`examples/session-dash-panel-smoke.py`（Python，无需浏览器）：

1. 构建 public-safe fleet 夹具（两个 goal，一个拥有第二个带完成 todos 的 goal 的 session）。
2. 渲染页面并断言只读标记、概览 + session 面板、session -> goal 分组、进度条、转义输出、实时刷新脚本与 `/panel` 片段形态。
3. 断言内部机制（decision frame、work lane、truth 契约、source warnings、leases）不在页面中。
4. 注入合成私有标记（`GH_FAKE_*` 风格），并断言它们不进入渲染页面 / 静态导出。

## 暂不覆盖

- 浏览器写控件：dashboard 仍是唯一可以提交 reward/控制面草稿的 surface，且只能通过显式 loopback capability gates。
- 新 capability 或 provider：没有。这是既有契约之上的渲染器 + CLI 呈现 surface。
- Fleet 面板内的 goal 级下钻：每 goal 的 channel 详情留在 React dashboard；loopback 面板是一瞥观察 surface。
