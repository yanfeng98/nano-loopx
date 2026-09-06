# Codex CLI TUI 延续优先级


状态：下一块 Codex CLI 产品切片的调度契约。

本说明存在的原因是：任何 peer 都可能漂向可见、易交付的 frontstage 工作，哪怕用户刚刚把产品优先级拨回 Codex CLI TUI 采用。Frontstage 与 showcase 工作是很重要的支撑 surface，但它们不得排在可运行的 Codex CLI TUI 延续任务之前。

## 产品优先级

近期产品承诺是：

1. 用户在项目仓库中打开 Codex CLI TUI；
2. 一条粘贴的 LoopX 消息启动 loop；
3. 只要 Codex 暴露安全的 attach 原语，LoopX 以后就可以通过同一个可见 TUI 转向或恢复工作；
4. 用户可以继续观察、中断、转向、评审或接管。

第一条消息已经文档化。下一个优先级是后半句：证明首次 TUI 引导之后的一次后续可见转向 Turn，或者记录阻止它的精确 blocker。

## 调度规则

当 LoopX 在可运行的产品化任务之间选择时：

- 当延续任务可运行且在范围内时，Codex CLI TUI 延续胜过 frontstage 打磨、showcase 文案或 dashboard 路由工作。
- 只有当 TUI 延续被缺失证明、缺失 CLI capability、用户决策或更高风险的 runtime 边界具体阻塞时，frontstage 与 showcase 工作才可以优先跑。
- 如果 Codex CLI TUI 延续任务可运行，而 LoopX 却选择 frontstage 工作，agent 应把该情形当作规划漂移，并在写代码之前运行 self-repair。

这不是永久的全局优先级。它是当前产品阶段的规则：最有价值的外部开发者路径是快速 Codex CLI 采用，同时不丢掉可信 TUI。

## 验收目标

下一块有用的 Codex CLI TUI 延续切片应为以下结果之一产出 public-safe evidence：

- `same_tui_continuation_proven`：一条后续 LoopX 转向 prompt 被加入同一个打开的 Codex CLI TUI session，带可见证明与 runtime idle evidence。
- `same_tui_continuation_blocked`：当前 Codex CLI surface 无法安全接受后续可见 Turn；blocker 说明缺失的原语，回退保持为手动粘贴或显式 `codex exec`。
- `same_tui_continuation_gated`：任务无法运行，因为它会要求原始 transcripts、session 文件、私有资料、凭据或生产动作。

Evidence 必须保持免 transcript。它可以使用 public-safe 夹具、布尔 capability 探针、可见窗口元数据与紧凑写回记录，但不得读取原始 Codex transcripts、session 文件、隐藏 TUI 缓冲、凭据或私有项目状态。

## Agent 提醒

如果 heartbeat、quota 摘要或已认领的推进泳道推荐 frontstage，而近期用户转向说 Codex CLI TUI 延续应该优先，agent 应：

1. 检查当前可运行的 todo 列表；
2. 如果可运行，优先选 Codex CLI TUI 延续 todo；
3. 如果不可运行，写回原因；
4. 然后才推进 frontstage 或 showcase 支撑工作。

这让华丽的演示 surface 对齐更重要的采用路径：LoopX 应该易于从开发者已经信任的 TUI 内部启动。
