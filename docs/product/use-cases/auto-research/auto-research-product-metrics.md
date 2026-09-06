# Auto-Research 产品指标


本说明定义 LoopX 自动研究（auto research）的用户面向指标。这些不是实现计数器。它们应帮助 maintainer、研究负责人或 operator 回答一个产品问题：

> Agent 网络是否在受保护评估器下创造了有用研究进展，同时比手动 loop 用更少的人类协调成本？

事实源是 public-safe LoopX graph：`research_contract_v0`、todo claims、`research_hypothesis_v0`、`research_evidence_event_v0`、晋升/退役候选、user gates 与 rollout 事件。原始日志、私有路径、受保护评估器正文与本地 transcript 不是指标输入。

## 有意义的指标

| 指标 | 产品问题 | 主要来源 | 好的动向 |
| --- | --- | --- | --- |
| 首次评分尝试时间 | 系统多快把一个研究契约变成真实评估器反馈？ | dev split 上第一个 `eval_status=scored` 的 `research_evidence_event_v0` | 时间更短且不削弱边界检查 |
| 每个活跃日的有用假设 | Agent 网络产出了多少可复用搜索？ | 带已评分 evidence、已退役负向 evidence 或可恢复重试 evidence 的假设 | 更多有用假设，而不是更多原始尝试 |
| 留出提升 | 最佳候选是否在迭代 split 之外改进？ | 最佳留出指标与该契约基线与方向比较 | 干净受保护边界下的更高提升 |
| 负向 evidence 复用 | 失败方向是否省下了未来工作？ | 被后来假设引用、frontier 剪枝或 narrator 摘要引用的被反驳/退役假设 | 更显式地复用干净负向 evidence |
| 重试恢复率 | 未完成的尝试是否变成有用结果而不是消失？ | `needs_retry` evidence 后接 scored、retired 或明确 blocked 状态 | 更多重试带 evidence 闭合 |
| 所需人类晋升决策 | 结果可晋升前用户需要花多少判断？ | 晋升 gates、user todos、review packets、reward 覆盖层 | 更少含糊 gate；每个必需 gate 都具体 |

这些指标是 run 级与产品级。单个 k-NN showcase 可以突出留出提升与首次评分尝试时间。更长的自主研究 run 还应报告负向 evidence 复用、重试恢复与所需人类晋升决策。

## 指标定义

### 首次评分尝试时间

开始时间是 run 的首个持久来源记录：

- 可得时的 `research_contract_v0` 创建；
- 否则是该项目 goal 的首个 todo 支撑的 `research_hypothesis_v0`。

结束时间是该 run 最早的 `research_evidence_event_v0`，满足：

- `split=dev`；
- `eval_status=scored`；
- `protected_scope_clean=true`；
- `raw_logs_recorded=false`；
- `private_artifacts_recorded=false`。

这不是"首个命令时间"。只搭文件、打印 frontier 或在评估器之前失败的命令不是评分尝试。

### 每个活跃日的有用假设

一个假设留下以下可复用结果之一时有用：

- **被支持（Supported）：** dev evidence 在契约指标方向上改善。
- **可晋升（Promotable）：** dev 与留出 evidence 都改善，且边界干净。
- **干净退役（Retired cleanly）：** 回归、guardrail 失败或精确性失败被捕获为未来 agent 可见的负向 evidence。
- **可恢复重试（Resumable retry）：** 不确定尝试保留分支或 artifact 引用，并有清晰的重试/退役策略。

不要计数每个生成的念头。不要计数没有新 evidence 却重复同一机制的重复假设。

### 留出提升

留出提升是优化式自动研究最强的用户价值指标：

```text
held_out_lift = best_holdout_metric - baseline_metric
```

对 maximize 指标，正向提升是好的。对 minimize 指标，反转符号或报告相对减少。留出结果只有在以下配对时才值得作为产品成果：

- 匹配的 dev evidence；
- 干净的 editable/protected 边界；
- 研究契约要求的晋升策略；
- 对晋升了什么、没晋升什么的显式陈述。

### 负向 evidence 复用

负向 evidence 在防止重复浪费时有产品价值。只在后续状态使用它时才计数：

- 后来假设把退役的/被反驳的假设作为来源引用；
- frontier 投影剪枝或降权同一机制家族；
- 产品 narrator 解释一个可见分支为何退役；
- 重试策略因 evidence 已经决定性地选择退役而不是重新启动。

价值陈述应读作："两个破坏精确性的近似路径被退役，并从下一个 frontier 排除"，而不是"存在两行失败"。

### 重试恢复率

重试恢复率度量 LoopX 是否阻止未完成工作变成无声损失：

```text
retry_recovery_rate =
  needs_retry_attempts_closed_with_scored_or_retired_evidence
  / total_needs_retry_attempts
```

恢复的重试可以变成已评分 evidence、干净退役 evidence 或具体 blocker。它们不应停留为含糊的"以后再试"说明。

### 所需人类晋升决策

自动研究在晋升边界仍需要人类判断。产品指标不是"零人类"。而是人类决策是否小、具体、有价值：

- Gate 关乎晋升、私有边界、新颖性、成本还是发布？
- 问题是否具体到一次决策就能回答？
- Gate 是否解锁特定假设或结果？
- Agent 在等待时是否保留安全非 gate 工作？

同时报告数量与质量。一个干脆的晋升 gate 好过三个含糊的批准 ping。

## 不应作为产品指标的指标

避免大多只证明实现活动的指标：

- 触及的文件数；
- 文档页或 UI 面板数；
- smoke 测试数；
- 打印的 CLI 命令数；
- 生成的 agent 数；
- dashboard 行数。

这些可以是验证或工程健康信号。除非绑定研究结果、更短决策路径或更少重复工作，它们不是用户价值。

## 产品板形态

产品板应按此顺序呈现指标：

1. **Run 价值：** 最佳留出提升、已晋升假设与边界状态。
2. **搜索进展：** 每个活跃日有用假设与首次评分尝试时间。
3. **复用：** 已退役方向与负向 evidence 复用。
4. **恢复：** 重试恢复率与剩余重试 blockers。
5. **人类注意力：** 所需晋升决策与未解决 gates。

板可以在折叠下方显示实现健康，但不应以此开头。

## Public-Safe 提取

指标提取应只读取 public-safe 投影：

- 用 `research_evidence_graph_v0` 获取最佳 dev/留出指标、负向 evidence 与重试计数；
- 用 `decentralized_research_frontier_v0` 获取当前可运行、被阻塞、晋升与退役候选；
- 用 `research_evidence_graph_v0` 获取任何未来公开案例页输入；
- 用 `loopx_rollout_event_v0` 摘要获取时间戳与生命周期转变；
- 用压缩成 public-safe gate 标签与 todo id 之后的 user/operator gates。

不要解析原始评估器日志、原始 benchmark 轨迹、私有来源文档、本地文件系统路径或聊天 transcript 来计算产品指标。

## 验收检查

产品指标 packet 在以下情况可接受：

- 每个指标都命名可以重算它的来源记录类型；
- 留出提升与仅 dev 进展分开；
- 负向 evidence 只在被复用或对未来 frontier 选择可见时计数；
- 重试恢复区分 scored、retired、blocked 与仍打开尝试；
- 人类晋升决策是具体 gates，而不是泛化批准状态；
- 所有示例 public-safe，避免本地路径、凭据、私有链接、原始日志与受保护评估器细节。
