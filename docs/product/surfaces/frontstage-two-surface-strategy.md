# Frontstage 双 Surface 策略


> **已弃用的兼容 surface：** `/deprecated/frontstage/ops` 只保留用于有界诊断。旧 `/frontstage?mode=ops` 形态为书签兼容重定向到那里。Personal Workspace（`/`）是 operator 工作流、Goal 输出与里程碑报告的产品 owner。不得向遗留 Frontstage Ops board 添加新产品 capability。在其剩余夹具与 smoke 消费方迁移后的专门清理中移除兼容路由。

LoopX frontstage 工作有两个不同产品共享一些 dashboard 代码。把它们当作一个 surface 会让下一轮 UI 改造目标不清：公开 showcase 页面想要视觉叙事，而真实 operator 控制面想要密集、本地、有状态的检查。本说明是在更多大型 UI 变更之前保持这些职责分开的路由与验证契约。

## 决策

呈现系列有两个一等产品 surface 与一个已弃用的诊断兼容路由：

| Surface | 职责 | 主要路由 | Owner |
| --- | --- | --- | --- |
| 公开 showcase 与首页 | 通过 public-safe 案例、演示、动画与产品叙事解释 LoopX。 | `/frontstage`、托管的 `/frontstage/`、未来首页入口点。 | Product、外联与 frontstage showcase 工作。 |
| Personal Workspace | 帮助 operator 检查并对当前 Goals、Todos、runs、outputs、reports 与安全本地动作采取行动。 | `/` | Runtime、status 契约、dashboard 与控制面工作。 |
| 遗留 Ops 诊断 | 消费者迁移期间为旧投影调试保留有界兼容。 | `/deprecated/frontstage/ops?statusUrl=<relative-or-loopback>` | 已弃用；无新产品功能。 |

公开 surface 是 URL 可复制或托管时的默认。Ops surface 显式、本地；除非 loopback server 广告单独 capability（如 reward dry-run 或 append 预览），否则只读。

## 路由所有权

不带 `mode=ops` 的 `/frontstage` 属于公开 showcase surface。它必须忽略 `statusUrl`、渲染打包演示或 showcase 资料，并保持对 GitHub Pages、Lark 分享、截图与公开 demo 安全。

`/deprecated/frontstage/ops?statusUrl=...` 属于本地 ops 检查。`statusUrl` 必须是相对或 loopback。该路由可以从本地 `loopx serve-status` feed 读取 `goal_channel_projection_v0`，但它不是公开链接，不得用作托管展示资料。其实现位于
`apps/presentation/dashboard/src/views/deprecated/`；公开 `frontstage-page.tsx` 不得导入实时 status 查询层或保留 Ops 渲染分支。

`/` 是 operator 之家。它应当为共享 LoopX registry 回答首屏操作问题：当前 goal、具体 user gate、首要 user todo、首要 agent todo、quota 或 guard 判断，以及近期 evidence。`?view=ops` 仍是调试 status 契约、reward 预览与单个队列条目的详细工作台。

`/frontstage/developer` 是只读 contributor cockpit。它属于 frontstage developer-extension 泳道，而不是公开首页或实时 ops surface：它渲染静态公开契约、投影 diff、夹具规则、smoke 检查清单与组件示例，让贡献者无需在大 dashboard 页面里挖掘就能添加投影。

`view=share` 等兼容别名只能作为路由桥存在。它们不定义第三个产品 surface。

## 数据源

公开 showcase surface 可以读取：

- `docs/showcases/showcase-catalog.json`；
- `docs/showcases/` 下的公开案例页面；
- 公开 storyboard、动画原型与生成的静态 bundle；
- 揭示产品模型或净化案例的公开资产。

公开 showcase surface 不得读取：

- `.codex/goals`、`.loopx` 或 `registry.global.json`；
- 实时 `loopx status` 导出；
- loopback `serve-status` feed；
- 原始 run 日志、transcripts、benchmark 任务文本、轨迹、verifier 尾部、凭据、内部链接、本地路径或未发布项目 evidence。

Ops 控制面 surface 可以读取：

- `loopx --format json status`；
- `loopx serve-status --global-registry` 或项目本地 `serve-status`；
- `goal_channel_projection_v0` 与其他版本化投影；
- 本地 server 显式暴露时的 run 绑定 reward 预览数据。

Ops surface 仍应默认只读。浏览器写入需要 loopback capability 标志、先 dry-run 验证与本地 CLI 等价契约。公开托管 bundle 不得包含那些 capability。

## 视觉自由度

公开 showcase surface 可以富有表现力。它可以使用 case-first 构图、动态泳道、动效、公开产品图像、生成的位图资产与强叙事层级。它应追求理解：LoopX 是什么、为什么长程 agent 工作需要控制面，以及哪些公开案例证明可复用行为。

Ops surface 应更安静、更密集。它应追求扫读、对比、重复动作、过期 daemon 修复与清晰本地边界。它仍可以精美，但装饰性动效不得掩盖 gate、quota、todo、claim 或 evidence 状态。

公开视觉实验不得依赖实时状态。Ops 组件除非有净化夹具与 public/private 边界检查，否则不得晋升到公开首页内容。

## 验证边界

公开 showcase 变更应验证：

- 用 `examples/showcase-catalog-smoke.py` 验证 catalog 形态与案例声明；
- 变更时验证静态原型或动画契约；
- 用 `npm run smoke:frontstage-share-bundle` 验证分享/导出隐私；
- 对变更 docs/examples 用 `loopx check` 做公开边界扫描。

本 fork 已移除 `.github/`（2026-09-07，`6a9bebc75`），因此原先第 4 条
`examples/frontstage-pages-workflow-smoke.py`（验证 Pages workflow 安全）随该
workflow 一起退役。

Ops 控制面变更应验证：

- status 契约解析与投影语义；
- 用 `npm run smoke:frontstage-route` 验证路由门控；
- `serve-status` 或 reward 预览 API 变化时的本地 server 行为；
- 仅 loopback status 源规则；
- 任何浏览器触发的 dry-run 或 append 路径的只读默认值与显式 capability 标志。

跨 surface 变更触及共享代码时必须证明两侧。最低检查是：showcase 模式忽略 `statusUrl`，ops 模式只接受相对或 loopback feed，且导出的公开 bundle 不携带实时 registry 状态。把 `examples/fixtures/frontstage-private-status-trap.public.json` 用作合成负向夹具：公开 showcase URL 与 share bundle 不得渲染其 `GH_FAKE_*` 标记，而显式 ops-mode statusUrl 加载可以在本地检查期间渲染它们。

## 分阶段路线图

阶段 0，当前基础：保持 `/frontstage` 默认公开 showcase 模式，保持 ops 模式显式，并让 operator 之家与托管 showcase 链接分开。

阶段 1，公开 showcase 打磨：从 `docs/showcases/showcase-catalog.json` 改进公开案例发现、首页入口、动画/叙事、share bundles 与视觉资产。不添加实时 status 依赖。

阶段 2，本地 ops 数据层：把 ops 视图提升为基于 `serve-status` 的 TanStack Query 层，带 schema 版本新鲜度检查、过期 daemon 修复文案、本地 capability 投影与相对或 loopback 源规则。

阶段 3，受控本地写辅助：只在本地 server 广告 capability 后添加浏览器辅助 dry-run 预览。写入保持仅 loopback、预览锁、CLI 等价与 opt-in。

阶段 4，可选分离：只有在共享代码开始使所有权、bundle 隐私或验证边界更难维护时，才拆分路由或包。在此之前，只要该契约持续执行，一个 dashboard 应用可以同时承载两个 surface。

## 非目标

本策略不授权远端实时 status 服务、公开 ops-mode URL、隐藏 session 读取、默认浏览器写权限，或没有公开 evidence 的营销声明。它也不改变 Codex CLI/TUI loop 优先级：TUI bootstrap 与可见延续规则仍是它们自己的产品契约。
