# 呈现 Surface 布局

> [English](presentation-surface-layout.md)

LoopX 的面向人 surface 已经多到应当被视为一个统一的呈现层，而不是散落的前端、渲染器与连接器辅助。

呈现层是智能显示中间层：它读取 LoopX 的 public-safe 状态，折叠成可评审的投影，为人类渲染，并同步到外部显示 surface。它不决定 quota、不改动 todos、不绕过 gates，也不拥有连接器凭据。

## 仓库边界

| 层 | 规范路径 | 角色 |
| --- | --- | --- |
| 前端应用 | `apps/presentation/dashboard/` | 浏览器 surface，如 dashboard、frontstage 与 developer cockpit。 |
| 显示渲染器 | `loopx/presentation/renderers/` | 针对已构建载荷的纯渲染器，如 status Markdown。 |
| 显示 sink | `loopx/presentation/sinks/` | 外部显示输出，如 Lark/飞书卡片与 Base 表格。 |
| 显示投影 | `loopx/presentation/projections/` | 面向图、表、卡片或 feed 视图的中间 public-safe 读模型。 |
| Capability 门面 | `loopx/capabilities/*` | 当显示 sink 同时也是 capability 时的用户面向 capability 名与兼容导入。 |
| 控制面 | `loopx/control_plane/` 与状态 API | goals、todos、gates、claims、quota、evidence 与 replanning 的事实源。 |

## 与 Value Connector 的关系

Value connector 在带边界的计划与 gate 下把外部信号带进 LoopX。呈现 sink 把 LoopX 拥有的 public-safe 状态导出到人类显示。它们可以合作，但不该仅仅因为两者都提到外部产品就住在同一模块。

例如，GitHub 或 Lark value connector 可以产生紧凑信号。呈现层之后可以在 dashboard、图投影或 Lark Base 表格中显示该信号。Connector 仍拥有摄取与 authority 检查；呈现层拥有显示形态与 public/private 脱敏。

## Explore 拓扑结果的放置

Explore 有两个不同职责，不应作为一块整体移动：

- 探索 evidence 与拓扑事件：保留在 explore capability 或未来控制面 explore/read-model 边界下，因为这些数据喂给 vision、replan、后继 todos 与 user gates；
- 面向显示的图/表/卡片投影：当它们只重塑面向人类的 public-safe explore 状态时，放在 `loopx/presentation/projections/explore/` 下；
- 面向节点、边与发现的 Lark/飞书 Base 同步活在 Lark 扩展的 `loopx/extensions/lark/presentation/explore_results.py` 中；
- CLI 入口点：`loopx/cli_commands/explore.py`；
- 可选用户面向门面：如果该命令被打包为 capability pack，放在 `loopx/capabilities/explore/`。

这让 explore 保持为 replan 输入而不是退化成一块板，同时让显示 sink 与其它智能呈现工作相邻。
