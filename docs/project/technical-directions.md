# 当前技术方向

## Shared Goal Authority 与跨 Host 协作

本方向刻意不叫“共享元信息数据库”。NoKV 是位于 LoopX authority 之后、尚未晋级
的可选 provider candidate，而不是 authority 本身。Agent 不直接连接 NoKV。
Run history、status、quota、scheduler state、host session 与 evidence 继续由原有
边界负责。

下一项 qualification 必须先保持 provider-neutral：抽取紧凑的
command/precondition/receipt/outcome core，让 file-backed provider 通过相同的
`claim_work` 契约，并证明 target-scoped conflict 与 atomic original-receipt
replay。真实 NoKV qualification、renew/reclaim、distributed quota、认证、HA 与更
广泛的状态同步都是后续显式决策，不属于隐含 scope。

## 架构与研究孵化器

| 探索 | 阶段 | 当前入口 | 实现规则 |
| --- | --- | --- | --- |
| Effect Program 与 settlement algebra | Accepted / runtime hardening | [RFC](../architecture/rfcs/agent-loop-effect-interpreter-v0.md) | 改善共享 typed contract 与 negative coverage；明确 scheduler ownership 和 domain-local ACK 语义。 |
| TypeScript 控制面迁移 | Accepted / transaction-payoff 阶段 | [RFC](../architecture/rfcs/typescript-control-plane-migration-v0.md) | Cut over 完整 transaction，删除 Python 语义/facade 债务，并报告 bridge traffic 与迁移经济性；delivery/vision 决策保持 domain-local reducer，不泛化成 generic Effect Program step。 |
| 分层 Agent stride | Active research | #3203 | 引入 adaptive selection 前先验证 read-only 与 shadow evidence。 |
| 研究型探索控制面 | Draft / typed frontier | [RFC](../architecture/rfcs/research-exploration-control-plane-v0.md) | 保持 Explore、goal-frontier 和 execution authority 分离。 |
| Human Attention Wishlist | Draft / non-blocking sidecar | #3179 | 不改变 user gate、selected work、quota 或 notification authority。 |
| Goal artifact lifecycle projection | Draft / read model | [RFC](../architecture/rfcs/goal-artifact-lifecycle-projection-v0.md) | 先以 read-only 方式推导 milestone 与合法 next transition。 |
| 结果后 memory utility | Draft / research | #3214 | 只在 verified outcome 后归因；retrieval 与 model judgment 保持 advisory。 |
| Goal Channel 与 Agent IM/OpenViking 边界 | Draft / integration exploration | [RFC 索引](../architecture/rfcs/README.md) | delivery、durable control state 与 scoped context 分属不同 owner。 |

探索只有在具备真实 caller 或兼容契约、达成一致的最小切片和聚焦 qualification 后，
才进入 implementation-ready。不能只因 RFC 描述了未来可能性，就加入 speculative
module 或重复 authority。

## 贡献与治理闭环

1. 选择最接近的 direction tracker，阅读当前阶段与边界。
2. 在 [Contributor Task Board](../development/contributor-tasks.md)
   寻找有界任务；如果没有，
   用 contributor task 模板创建 issue，写明方向、目标 base branch、最小切片、
   non-goal 与验证方式。
3. 孵化工作必须说明 PR 面向 `main` 还是 integration branch。面向 `main` 的 PR
   不得悄悄依赖只存在于未晋级分支的契约。
4. Umbrella issue 用于方向讨论与决策；具体实现和 review 使用独立 issue 或 PR。

当跨方向问题适合实时讨论时，阶段性的
[开放战略 Review](../community/open-strategy-reviews.md)可以比较最多四个方向。
Review 只记录 disposition、owner、下一产物或证据要求及复核 trigger，不通过投票把
方向写入 `main`，也不改变 RFC stage 或直接授权实现。

阶段、owner、integration branch、promotion gate 或 scope 出现实质变化时，必须通过
PR 更新本文；如果 RFC index 或 task board 的路由也发生变化，应在同一 PR 更新。
合并后由 maintainer 更新置顶 Discussion；Discussion 不能覆盖仓库已合并事实。

四个 `direction/*` label 只负责路由，不代表成熟度或 authority。对 implementation
lead 的认可记录当前公开工作，不会静默授予仓库权限或 maintainer 身份。
