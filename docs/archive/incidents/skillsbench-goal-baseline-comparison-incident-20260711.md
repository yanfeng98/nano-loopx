# SkillsBench Goal 基线对比事件

> [English](skillsbench-goal-baseline-comparison-incident-20260711.md)

日期:2026-07-11

读者对象:LoopX benchmark 维护者、Codex Goal 集成所有者、reducer 所有者,
以及 benchmark 证据审阅者。

## 摘要

一次早期 SkillsBench 对比暗示:带 xhigh 推理的 Codex TUI `/goal` 得分低于裸
Codex CLI xhigh 基线。这一宽泛结论没有得到匹配实验的支持。观察到的聚合把历史
运行与不同的提示词投递、重试历史、runner 版本、可计数规则和失败重放选择混在
了一起。

调查发现了多个 benchmark-harness 缺陷,可能把有效结果变成不可计数失败、导入
无关历史行、或把一次稍后的传输告警归因到已完成官方得分之上。修复后,一个历史
Goal 零分在没有改变任务提示词和 Goal objective 的情况下变成了干净的官方通过。
匹配重跑也把几个所谓的 Goal 回归重现为同样的裸 CLI 失败。

一个案例仍显示出匹配后的分差,但其两条路由没有以等价的提示词投递收到任务。
在把该分差归于原生 `/goal` 生命周期之前,尝试了一次文件目标对等探针,但探针
在任务前就遇到容量失败,没有产生可计数结果。

本事件是 public-safe 的。它排除原始任务文本、轨迹、verifier 尾部、凭据、私有
启动材料和本地工件路径。

## 基线语义

裸 Codex 与原生 `/goal` 臂都是产品基线。它们不是案例本地的 LoopX 处理臂。
因此以下观察是预期的,绝不能当作"`/goal` 未能激活"的证据:

- 没有案例本地 LoopX 状态;
- 没有案例本地 LoopX todo;
- 没有 LoopX quota、status 或 spend 生命周期;
- 没有 `app_server_goal_followup` 控制器轮次;
- 没有转发进 LoopX 的 benchmark 奖励反馈。

原生 Goal 激活应改由 Codex Goal 生命周期本身确立:目标创建或更新、活动执行、
token 与耗时跟踪,以及终局完成或阻塞状态。

## 对比中的混杂因素

原始聚合不是因果 A/B 测试:

1. **提示词投递不同。** 裸 CLI 在初始请求中收到任务指令。TUI `/goal` 在激活后
   收到紧凑的稳定目标,并从 workspace 文件读取完整任务包。
2. **控制器行为不同。** 一些裸运行可能收到新的计划性 `codex exec` 后续。原生
   `/goal` 使用自己的生命周期。
3. **历史重试不同。** 规范性 Goal ledger 在失败案例修复重跑后保留最佳可计数
   结果,而历史 CLI 行来自不同尝试和 runner 代际。
4. **Runner 缺陷随时间不同。** 输出路径、依赖引导、mount 归属、sandbox 转发、
   ledger 追补与得分后传输行为在战役期间都发生了变化。
5. **聚合是选择在失败上的。** 只重放零分或不可计数的 Goal 案例可以改进
   best-of ledger,但不能估计 `/goal` 相对裸 CLI 的处理效应。

## 已落实的 Harness 修复

调查产生了以下公开修复:

| PR | Surface | 效果 |
| --- | --- | --- |
| #1825 | 结果路径 | 跨远程 workspace 归一化输出查找 |
| #1826 | 聚合与 ledger 一致性 | 防止 ledger 更新后读取过时聚合 |
| #1829 | 依赖引导 | 通过选定的虚拟环境调用 pip |
| #1830 | 失败归属 | 避免把任务面对的执行归类为纯 mount 失败 |
| #1831 | Launcher sandbox 转发 | 保留请求的 Codex sandbox 契约 |
| #1833 | Ledger 追补作用域 | 把匹配探针 ledger 与历史 Goal 行隔离 |
| #1834 | 得分后可计数性 | 在稍后的宿主传输告警后保留已完成的数字官方得分 |

PR #1834 改变了得分可计数性的优先级,并仍待独立审阅。审阅完成前不得把它当作
已合并行为。

## 匹配后的证据

匹配重跑收窄了表面回归集合:

| 案例 | Goal xhigh | 匹配裸 CLI xhigh | 受支持的结论 |
| --- | ---: | ---: | --- |
| `flink-query` | 0.0 | 0.0 | 历史裸通过未重现 |
| `pddl-airport-planning` | 0.0 | 0.0 | 两条路由到达相同的归一化 verifier 失败类 |
| `react-performance-debugging` | 0.0 | 0.0 | 历史裸通过未重现 |
| `multilingual-video-dubbing` | runner 修复后 1.0 | 不需要 | 历史 Goal 零分是 harness 工件 |
| `debug-trl-grpo` | 0.25 | 0.60 | 真实观察到的分差,但提示词投递尚未匹配 |

`debug-trl-grpo` 的轨迹在方案层面解释了得分差异:Goal 运行修复了一个缺陷就
停止,而裸运行在第一轮修复了两个计分缺陷。这一观察本身并未说明模型为何选择
不同范围。两条路由的初始指令通道仍然不同。

## 文件目标对等探针

该探针包装裸 `codex exec`,使其与 Goal 路由收到相同的紧凑目标,并在行动前读取
同一 workspace 任务包。这移除了已知最大的提示词投递差异,而不添加 LoopX 处理
状态。

第一个探针暴露了包装器协议错误,在任务执行前被丢弃。该错误修复后,一次直接的
反向隧道启动探针确认 Codex 可以创建线程并开始一个 turn,但订阅容量上限在任何
任务面对动作之前触发了。案例级重试重现了同样的任务前退出。两次尝试都没有到达
求解器或官方 verifier,因此都是不可计数的基础设施/容量结果。

因此 `debug-trl-grpo` 的对等问题保持开放。它应在容量可用后重跑,使用相同的
目标摘要且不更改官方任务或 verifier。在此之前,观察到的 0.25 对 0.60 差异是
不等价提示词投递下的案例级结果,不是原生 `/goal` 回归的证据。

## 责任归属

宽泛的得分回归论断主要是 benchmark 方法论与 harness 问题,而不是通用原生
`/goal` 缺陷的证据:

- **LoopX benchmark harness:** 若干设置、归属、ledger 与可计数性缺陷实质扭曲
  了观察结果。
- **实验设计:** 参与对比的路由没有提示词投递或重试历史对等性。
- **Agent 分析:** 早期解读错误地把缺失案例本地 LoopX 生命周期字段当作一个
  本就不应产生这些字段的基线的负面证据。
- **原生 Codex `/goal`:** 观察到 Goal 生命周期激活。一个剩余的案例级质量差异
  需要提示词对等重跑或一场新的匹配战役,才能归因于 `/goal`。

## 必需的对比契约

未来因果对比应使用全新、单次尝试的匹配战役:

```text
same case set and order
same Codex model and reasoning effort
same task packet and instruction channel
same sandbox and network policy
same wall-clock and token budget
same runner and reducer commit
same official verifier closeout contract
no best-of replacement across retries
infra failures excluded symmetrically
```

主要报告应包含配对案例差值与置信区间,而不只是各自的均值。失败案例修复重跑
应作为恢复 ledger 报告,而不是并入因果对比臂。

## 后续契约

### P0:完成可计数性审阅

独立审阅 #1834。具有任务面对活动的已完成数字官方 verifier 结果,即使之后发生
宿主传输告警,也应保持可计数;零活动的数字工件必须保持不可计数。

### P0:重放其余不可计数的 Goal 案例

reducer 契约接受后,以精确运行 ledger 隔离和必需的任务面对活动,重放剩余
不可计数的 Goal 案例。把设置、容量、认证和传输失败排除在得分聚合之外。

### P1:开展新的匹配战役

如果产品问题是 `/goal` 是改进还是损害方案质量,就按上述对比契约从干净案例集
运行两条路由。不要从修复后的 best-of 规范性 Goal ledger 回答该问题。

### P1:保留提示词对等证据

Benchmark 紧凑工件应为每条路由记录 public-safe 的提示词投递模式与目标摘要。
它们不应存储原始任务文本。
