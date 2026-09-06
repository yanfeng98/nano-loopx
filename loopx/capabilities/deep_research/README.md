# Deep research(evidence-ledger 研究 Loop)


`/loopx-deepresearch` 把一个用户问题变成有界、可审计的研究会话:question、source、
claim 与 contradiction ledgers 位于 `.loopx/deepresearch/research.json`,packet
(`loopx deepresearch status`)拥有下一步研究什么以及何时停止,最终报告让每一条
citation 都可解析回一条已记录的 source。

## 与 auto-research 的边界

内置 `auto-research` capability 与本 capability 都做"有界研究",但拥有不同的
事实,不得轻易合并:

| | auto-research | deep-research(本能力) |
| --- | --- | --- |
| 工作单元 | 一个带 role-scoped workers 的 LoopX **goal** | 项目中的一个 **session ledger** |
| 状态权威 | goal todos、hypotheses、rollout events | `.loopx/deepresearch/` ledger |
| 推进方式 | worker contract + terminal 决策/审查 | packet expeditions + 停止条件 |
| 输出 | canonical evidence 中被提升/退役的 hypotheses | 可引用审计的 markdown 报告 |
| 适用场景 | LoopX 控制面内的开放探索 | 单个用户问题,需要可审计、带来源引用的答案 |

每个问题选一个;它们不共享状态,彼此也不能关闭对方的工作。

## 与 explore 的边界

`explore` capability 拥有 goal-scoped、public-safe、跨会话的知识拓扑(问题、
发现、证据关系)。deep-research 拥有私有的、session-scoped 事务式 ledger:

- deep-research 保留 raw source locator(URL 或本地路径,可能不适合发布)、
  claim 血缘、带 sides-with 判定结果的精确矛盾对、停止/关闭决策与引用报告。它
  独立工作——不需要 LoopX goal,也不需要 explore opt-in。
- explore 保留 canonical、可复用投影。任何未来桥接都是单向、幂等、
  public-safe 派生:explore 只接收净化后的不透明 evidence refs;它从不读取 raw
  deep-research ledger 或报告,从不双写研究状态,且 graph 节点解析从不关闭(或
  重新打开)研究 run。

简言之:deep-research 是 `.loopx/deepresearch/` 的唯一写入者,公开 surface
只会看到派生的、可重构投影。

一条 ledger 不变量横跨每个判定矛盾的 transition:任何 resolve——无论
`resolve-question` 内还是独立 `resolve-contradiction`——都不得推翻一个已被回答
问题引用为证据的 claim。Ledger 从不静默使已记录答案失效;迟到的获胜反证迫使
显式决策(站到被引用 claim 一边,或关闭 run 并在新 run 中重审该问题),而不是让
报告内部自相矛盾。

## 生命周期

`start` 打开一个 run;`close` 是显式 terminal transition;下一次 `start` 把已
关闭的 run(state + report)归档到 `.loopx/deepresearch/archive/<closed-at>/`
并开始新的。`start --new-run` 只自动关闭停止条件已触发的 run;活跃 run 总是需要
显式 `close` 在前。状态文件只能由这些 typed transitions 轮转——从不手工编辑。

## Layout

- 领域状态机与报告(capability owner):
  `loopx/capabilities/deep_research/runtime.py`
- CLI 适配器:`loopx/cli_commands/deepresearch.py`(`loopx deepresearch …`)
- Host 入口:由 `loopx slash-commands --install` 安装的 `/loopx-deepresearch`
  skill facade

记录的 claims 携带调用方声明 provenance:`--tool` 记录调用方声称产生了证据的
工具。CLI 记录该 provenance;它不证明工具确实运行了——执行 receipts 属于未来的
host/harness bridge,而不是本 ledger。
