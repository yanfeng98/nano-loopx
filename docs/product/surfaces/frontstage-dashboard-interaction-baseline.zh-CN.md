# Frontstage Dashboard 交互基线

> [English](frontstage-dashboard-interaction-baseline.md)

LoopX 历史上曾有两个 Frontstage 职责。公开 showcase 仍是产品 surface；旧 ops board 现在是弃用的诊断路由，而 Personal Workspace 拥有 operator 工作流。

Showcase surface 卖产品模型。Ops surface 让真实用户干活。它们可以共享 React 组件、图标、令牌与 public-safe 夹具，但不应共享数据默认值、信息密度或动效规则。

## Surface 拆分

| Surface | 路由姿态 | 主要职责 | 数据源 | 视觉规则 |
| --- | --- | --- | --- | --- |
| Showcase/首页 | 默认 `/frontstage` | 让产品显得显然且引人入胜 | `docs/showcases/showcase-catalog.json` 加净化分享夹具 | Case-first、凝练、带动效、public-safe |
| 遗留 Ops 诊断 | `/deprecated/frontstage/ops`（旧 `mode=ops` 重定向） | 旧消费者迁移期间保留有界检查 | 相对或 loopback `goal_channel_projection_v0` status feed | 密集、冷静、只读、可重复 |

默认托管或复制的链接必须打开 showcase surface。实时 registry 状态需要显式的弃用诊断路由与 loopback 或相对 status 源。新的 operator 功能归属 Personal Workspace。

## 产品方向

用 Multica 风格 agent workspace 方向作为密度与交互语法的产品基准：可见的 agent、已认领的工作、boards、时间线、搜索、过滤器、紧凑角色状态与可复用 workspace 原语。不要克隆其产品模型。LoopX 仍把 quota、status、todos、gates、leases、run 历史与 append-only evidence 当作控制面事实源。

当前技术栈是基线：

- React、Vite、TypeScript 与 TanStack Router，用于带 URL 支持过滤器的静态构建优先应用。
- 当行需要真正排序、分组与列控制时用 TanStack Table。
- Tailwind 加自有的 shadcn/Base UI 式原语，用于紧凑控件、徽章、面板、命令 surface 与可访问交互状态。
- lucide-react 用于按钮、泳道头部与不熟悉的控件。
- Zod 放在 status 边界，让公开夹具与本地实时 feed 大声失败，而不是渲染出含糊状态。

## Showcase 规则

Showcase surface 可以花哨，因为它不是 operator 驾驶舱。

- 以公开案例与异步 agent 运行模型开场。
- 用动效解释状态流动：安全工作的移动、gates 的保持、evidence 闭合 loop，以及多个 agent 泳道通过一个共享控制面汇合。
- 只渲染 public-safe showcase catalog 字段与净化分享夹具。
- 让本地 status 导出、内部项目 label、原始 task id、私有截图、benchmark 原始日志与机器路径远离此 surface。
- 把深入阅读链接到公开 GitHub showcase 页面。

## Ops 规则

Ops surface 应当像工作控制台，而不是落地页。

- 把 kernel 状态映射到
  [前端 kernel 到心智模型映射](frontend-kernel-mental-model-map.md) 中的五个用户概念：goal、下一步、blocker/权限、evidence 与继续状态。
- 保持首屏可扫读：goal 头部、决策框架、quota guard、user todo 泳道、agent todo 泳道、claims、gates、artifacts、source 警告与 run 时间线。
- 除非用户在搜索、调试或解决实时决策，否则避免把 `claim`、`scope`、`quota`、`run_history` 或 `handoff` 当作顶级用户词表。
- 优先行、条带、过滤器与紧凑窗格，而不是过大 hero 区。
- 保留 URL 支持的搜索与泳道过滤器，让一次评审可以复现精确的投影切片。
- 面板保持 8px 圆角或更小，避免嵌套卡片。
- 保持写操作离开该路由。浏览器写权限属于单独的本地 capability gate，而不是只读 frontstage 内部。
- 为重复使用优化：稳定尺寸、无水平溢出、响应式约束与 reduced-motion 回退。

## Frontstage/Status 充分性检查

在构建更宽的长程 LoopX UI 之前，frontstage/status 切片只有在证明三条流程时才充分：

- Todo-flow 评审：ops 模式渲染可搜索的 user 与 agent todo 泳道，带可复现的 URL 支持过滤器与可见结果计数。
- 人类 gate 动画：showcase 模式可以解释人类判断保持可见而安全 agent 泳道继续，带 reduced-motion 回退。
- 多泳道时间线：surface 可以区分人类决策、agent 工作与 evidence 写回，而不让浏览器 UI 成为事实源。

这些检查刻意比未来 operator 工作流更窄。它们证明现有 status 投影在新屏幕加入更丰富评审、feed 式分诊或多 agent 启动控件之前就能承载这个故事。

## 当前验收锚点

该路由当前暴露这些持久锚点：

- `data-frontstage-surface="showcase-homepage"` 用于公开 showcase 模式。
- `data-frontstage-surface="ops-control-plane"` 用于实时 ops 模式。
- `frontstage-ops-workspace-shell` 用于密集应用外壳。
- `frontstage-ops-command-strip` 用于搜索/过滤/结果计数控件。
- `frontstage-todo-search`、`frontstage-todo-lane-filter` 与 `frontstage-todo-result-count` 用于可评审的 todo 投影切片。
- `frontstage-management-surface-mock` 用于低保真 ops 投影，把 kernel 状态映射到 mission、team roster、ticket board、gate inbox、cadence/budget 与 evidence 时间线，而不引入并行状态模型。
- `frontstage-role-map`、`frontstage-active-claims`、`frontstage-open-gates`、`frontstage-artifacts` 与 `frontstage-timeline` 用于 operator workspace。
- `frontstage-budget-governance` 用于 ops budget、cadence、no-spend 控件与 evidence-link 契约。
- `frontstage-operator-state-legibility` 用于只读 ops board 上 outcome、lease、capability-wait 与 workspace-repair 的可读性。
- `frontstage-showcase-motion-beam` 与 `frontstage-state-flow-beam` 用于人类 gate 与状态流动画检查。
- `frontstage-self-iteration-timeline`、`frontstage-self-iteration-lane`、`frontstage-self-iteration-event`、`frontstage-self-iteration-dashed-bridge` 与 `frontstage-self-iteration-truth-contract` 用于公开三泳道自迭代时间线。
- `examples/fixtures/long-horizon-self-iteration-rollout.public.json` 用于带人类 gate、handoff、验证、推断显示桥覆盖与可见 frontstage 消费的 public-safe 多泳道 rollout 夹具。

`npm run smoke:frontstage-browser` 仍是该 surface 的视觉验收检查。它捕获桌面与移动截图、检查动画 showcase 轨道、验证 public/private 边界行为，并演练 ops 搜索、泳道过滤、goal 选择与 loopback 源拒绝。

`npm run smoke:frontstage-design-baseline` 保持本文档、路由锚点、CSS shell 类、包脚本与 README 入口点对齐。

`python3 examples/long-horizon-self-iteration-rollout-fixture-smoke.py` 保持公开夹具安全，并对 frontstage 时间线消费有用。
