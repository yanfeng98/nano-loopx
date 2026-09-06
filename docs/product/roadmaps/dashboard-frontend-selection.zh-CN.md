# 仪表盘前端选型

> [English](dashboard-frontend-selection.md)

LoopX 应该保留无依赖的静态 HTML 渲染器作为诊断兜底，但产品 dashboard 应当使用真正的前端技术栈。

目标 UI 是针对 Agent goal 的本地控制面：状态泳道、run 历史、契约健康、controller 交接与下钻视图。它应该更接近观测或编排控制台，而不是一份生成的报告。

## 产品基准

有参考价值的产品大致围绕三类产品形态：

- Langfuse、LangSmith、Braintrust 等 AI 观测工具侧重 trace/session 检查、eval 对比、过滤器、分数汇总、prompt 关联，以及从生产到 eval 的闭环。
- Dagster、Temporal 等编排工具侧重 run 列表、run 详情页、事件历史、血缘、依赖图与可重放性。
- Grafana 等监控工具侧重可组合面板、dashboard 变量、转换、链接与可分享视图。
- Linear 等工作管理工具侧重优先级、周期容量、分诊队列，以及显式的暂停/恢复状态，而不是把算力分配藏进通知节奏里。
- Vercel、Linear 等现代开发者产品定下了视觉基线：克制的排版、锋利的面板、紧凑的行、平稳的对比度、出色的空状态，以及用状态色点缀而不是装饰性配色。
- Datadog、Grafana 等观测产品定下了密度基线：可复用组件、健康面板、过滤器、dashboard 链接与下钻，把首屏变成 operator 驾驶舱。
- Multica 在产品形态上是有用的近邻，而不是直接克隆对象：其公开仓库使用 Next.js web 应用、Go 后端、PostgreSQL/pgvector、本地 agent daemon、共享 UI 包、Base UI/shadcn 风格组件、TanStack Query/Table、可调整面板、命令菜单、agent board、agent 档案、runtimes、squad、任务时间线与可复用的 skill surface。LoopX 应该借用其密集的 agent-board 与 workspace 成员语法，同时把控制面的事实源留在 LoopX 的 status/quota/run 历史里，而不是聊天或 issue board 里。

对 LoopX 而言，常见教训不是"更多图表"。首屏需要面向行动的队列和可信的下钻：

- 一眼可读的健康与关注泳道，
- 计算配额泳道，显示哪些 goal 可用、被限流、在等待、已暂停或正在请求 burst，
- 把面向 agent 的状态翻译成评审、批准、等待与 reward-capture 决策的 human operator 视图，
- 可过滤的 goal 与 run 表格，
- 可 URL 寻址的状态过滤器，
- 带紧凑 JSON/Markdown 链接的 run 详情页，
- 面向 peer 任务协调与 child-worker evidence 的事件或时间线视图，
- 稍后为 goal 依赖与交接加入图视图。

## 决策

把官方 dashboard 建为 `apps/presentation/dashboard`，采用静态构建优先的前端：

- **Vite + React + TypeScript**，做一个 local-first 单页应用：能读取导出的 JSON，构建成静态 HTML/资源，之后可以调用小型本地 API。
- **shadcn/ui + Tailwind CSS + Radix primitives + lucide-react**，提供精美、可访问、自有化的组件系统与良好默认值。
- **TanStack Router**，用于类型化路由与 URL 支持的过滤器，如选中 goal、队列泳道、severity 与 run id。
- **TanStack Table**，用于关注队列、run 历史、契约发现与将来的 child-agent 表格。
- **TanStack Query**，等 dashboard 从本地 HTTP 端点读取而非只加载静态 JSON 之后再用。
- **Recharts（通过 shadcn chart 模式）**，用于第一轮趋势与汇总面板。
- **Zod**，用于在 UI 边界校验 `loopx --format json status` 载荷。
- **Vitest + Playwright**，用于组件与浏览器级检查。

这意味着"静态 HTML dashboard"不应永远是手写 HTML。Python 渲染器继续作为无依赖的诊断兜底。产品 dashboard 应当是基于 Vite 的静态构建，使用自有化的 shadcn 风格组件与类型化数据边界。

## 两个 Frontstage Surface

即使共用同一个 React 应用、视觉令牌与小组件，LoopX 也应该把两个产品 surface 分开。

**Public Showcase Frontstage** 是首页风格的 surface。它应该由 catalog 驱动、精美、有动效且凝练。其数据源是 `docs/showcases/showcase-catalog.json` 加上生成的 public-safe 夹具。它不得读取实时 registry 状态、本地 status 导出、内部项目 label、原始 task id、原始 benchmark 素材、来自私有工具的截图或机器特定路径。这个 surface 在视觉上可以更激进，因为它的职责是让新用户快速感受到产品价值。

**Personal Workspace** 是用户/operator 工作区。它应该更密集、更克制、更保守：goal 头部、quota guard、user todo 泳道、agent todo 泳道、claims、gates、artifacts、source 警告与 run 时间线。它只允许从相对或 loopback URL 读取实时状态，并且在显式启用单独的本地写能力之前保持只读。这个 surface 应追求正确性、可扫读性与重复使用。

不要为了方便模糊这两个 surface。托管或复制的公开链接应当落在 showcase 模式。遗留的实时诊断链接位于 `/deprecated/frontstage/ops`，需要安全的本地 status 源。共享 UI 原语没问题；共享实时数据默认值不行，新的 operator 功能必须进 Personal Workspace。

## 为什么选这套技术栈

对下一个里程碑而言，Vite 比 server-first 框架更合适。Goal Harness 是 local-first 的，dashboard 可以先作为读取 JSON 的静态构建。服务端渲染、认证与托管部署还不是产品需求。

shadcn/ui 优于笨重的全家桶组件库，因为 dashboard 需要强默认值，但仍应自持代码。LoopX 可以在不对抗封闭设计系统的情况下改造卡片、侧边栏、表格、命令菜单、图表与徽章。

视觉基线应向 Vercel/Linear 借鉴而不是通用 admin 模板：深色工具侧栏、安静的白或近黑工作表面、8px 卡片、在有用处使用等宽或表格数字的状态值、密集表格，以及少量状态色点缀。

TanStack Router 与 Table 契合数据形态。核心 UI 状态是过滤器、搜索参数、排序、选中行与稳定的下钻 URL，而不是营销页面。

Recharts 足够满足第一个 dashboard，因为眼前的可视化是计数、历史趋势与小型对比。只有任务尺度的 peer 关系需要专门图视图时，才应加入自定义图工作。

## 被否决的选项

- **继续扩展 Python 静态渲染器**：适合冒烟测试与离线诊断，但一旦过滤器、详情视图、响应式布局与可访问交互重要起来，就会难以维护。
- **直接使用 Grafana**：做指标 dashboard 很出色，但 LoopX 需要行动队列和 goal/run 语义，而不是通用数据源面板。
- **现在就用 Next.js**：框架很强，但对一个没有服务端认证或托管产品 surface 的本地静态控制面来说为时过早。
- **把 Material UI / Ant Design 作为主要系统**：高效，但默认值对一个紧凑的 agent 控制 dashboard 不够贴合，也更难做出自有感。
- **只用 Tailwind 构建**：视觉灵活，但更难达到可访问的菜单、对话框、标签页、表格、tooltip 与图表。
- **采用预制 admin 模板作为主要产品**：一开始很快，但通用 CRM/SaaS 观感会和 LoopX 的队列、run 历史、契约健康与 controller 交接模型冲突。

## UX 方向

dashboard 应当密集、冷静、可操作：

- 左侧导航：goal、queue、runs、契约健康与设置；
- 顶部控件：registry、runtime root、扫描范围与刷新状态；
- 首屏泳道：user/controller、Codex-ready、external-watch 与阻塞健康；
- 紧凑的配额条：计算配额、已消耗 agent turns 与下一个合格时间；
- 表格优先的下钻，而不是过大 hero 区；
- 低调配色加状态点缀，而不是单一色调的品牌渲染；
- 一开始就支持浅色与深色模式；
- 公开演示数据中不出现原始私有 evidence。

## 当前实现切片

第一个 dashboard 脚手架位于 `apps/presentation/dashboard`。它使用选定技术栈，并从 `examples/status.example.json` 渲染真实界面：

- 契约健康汇总，
- 契约健康详情（错误、警告与成功检查），
- 关注队列泳道，
- 可排序的队列表格，
- goal/run 计数器，
- 响应式桌面与移动布局，
- `npm run build` 验证。

保留 `examples/render-status-dashboard.py` 作为无法构建 React 应用的环境的低摩擦兜底。

首个产品路径 `/frontstage` 切片现在存在于 `apps/presentation/dashboard`：它把 `attention_queue.items[].goal_channel_projection` 渲染为只读 channel board，让单个 goal 像一条被管理的 workspace 泳道。它展示决策框架、quota guard、user todo 泳道、agent todo 泳道、active claims、打开中的 gates、紧凑时间线、source 警告、URL 支持的选中/过滤/搜索与 truth 契约。这条路由才是 Multica 式 agent-board 密度该出现的地方；现有的 Python/HTML 渲染器应保持为免构建的诊断兜底。接下来的切片应当是质量工作：视觉验收、更丰富的 public-safe 夹具与 operator onboarding 细节，而不是再来一个基础渲染器。ops board 现在能把 outcome、lease、capability-wait 与 workspace-repair 状态从本地演示夹具中清晰呈现，而不授予浏览器写权限。

持久交互基线记录在 `docs/product/surfaces/frontstage-dashboard-interaction-baseline.md`，包括 showcase/首页与 ops/控制面拆分。

## 查过的资料

- Langfuse observability docs: <https://langfuse.com/docs/observability/overview>
- Langfuse sessions docs: <https://langfuse.com/docs/sessions>
- LangSmith observability docs: <https://docs.langchain.com/langsmith/observability>
- LangSmith dashboards docs: <https://docs.langchain.com/langsmith/dashboards>
- Braintrust eval interpretation docs: <https://www.braintrust.dev/docs/guides/evals/interpret>
- Braintrust observability docs: <https://www.braintrust.dev/docs/observe>
- Grafana dashboards docs: <https://grafana.com/docs/grafana/latest/visualizations/dashboards/>
- Grafana dashboard variables docs: <https://grafana.com/docs/grafana/latest/visualizations/dashboards/variables/>
- Dagster docs: <https://docs.dagster.io/>
- Temporal docs: <https://docs.temporal.io/>
- Vite docs: <https://vite.dev/guide/why.html>
- shadcn/ui docs: <https://ui.shadcn.com/docs>
- TanStack Router docs: <https://tanstack.com/router/latest/docs/framework/react/guide/type-safety>
- TanStack Table docs: <https://tanstack.com/table/v7/docs/overview>
- Recharts docs: <https://recharts.github.io/>
- Vercel Geist design system: <https://vercel.com/geist/introduction>
- Linear changelog and interface direction: <https://linear.app/changelog>
- Datadog dashboard widgets docs: <https://docs.datadoghq.com/dashboards/widgets/>
- Multica public repo and README architecture section: <https://github.com/multica-ai/multica>
