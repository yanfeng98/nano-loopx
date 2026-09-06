# 架构 RFC


架构 RFC 是公开的设计提案。每个 RFC 都应写明自身的决策边界、非目标、
最小有用实现切片与验收标准。RFC 可以描述未来工作；当前行为以实现与稳定的
参考契约为准。

新提案从 [RFC 模板](TEMPLATE.md) 开始。当大规模修订会把稳定设计、当前进度与
历史证据混在一起时，既有 RFC 应当采用它的维护契约。

[当前技术方向](../../project/technical-directions.md) 页面把 RFC 关联到战略项目、
贡献路径与晋升关卡。

## 如何阅读本索引

下面的各节是技术职责区，不是成熟度等级。每个主 RFC 只在其最接近的架构 owner
下出现一次，即使它也影响其他领域。

每个条目内，RFC 成熟度与交付成熟度仍是两件事：

- **RFC 状态** 记录 RFC 中写明的决策状态。即使某个有界切片已经交付，`Draft`
  工作的架构仍可能变化。
- **`main` 交付** 记录对照仓库审计过的实现状态。合入的实验不意味着整个 RFC
  已被接受，已接受的 RFC 也可能仍有后续采纳工作。
- **当前边界** 说明现在真正存在什么、仍被排除什么。它是导航辅助，不能替代
  稳定的协议文档。

RFC 内部也应保持同样的分离：

- 规范小节定义当前决策与验收契约；
- 带日期的执行流水账记录已交付切片与实验，但不静默修改契约；
- 决策日志记录显式批准以及它所修改的小节；
- 证据登记表把主张映射到可复现、可公开的安全证明。

不要把进度报告追加到规范性的交付计划里。长流水账移到关联的 `*-execution.md`
companion 文件。schema 缩减永远不是顺带清理：RFC 或 PR 必须逐个点名被删除的字段，
说明 producer/reader/writer 与兼容性研究，定义迁移与回滚，证明声称的语义等价性，
并记录显式的 maintainer 批准。

本索引最近一次对照 `main` 审计于 **2026-09-04**。RFC 状态、被提升的行为或
有意义的交付边界变化时，应更新相应条目。

## 控制面内核、状态与迁移

- [Agent Loop Effect Interpreter v0](agent-loop-effect-interpreter-v0.md)
  
  - **RFC 状态：** Accepted。
  - **`main` 交付：** 核心已实现；有界采纳继续。
  - **当前边界：** Effect 请求、解释、观察、结算与 typed Effect Program 基础
    已交付。Replan planning/ACK 保留在领域局部，直到出现第二个真实生命周期证明
    抽取的必要性。
- [TypeScript Control-Plane Migration v0](typescript-control-plane-migration-v0.md)
  
  - **RFC 状态：** Accepted；事务 payoff 阶段进行中。
  - **`main` 交付：** 实质性实现；活跃迁移中。
  - **当前边界：** Stage 1 与 2A 已完成。Stage 2B 正在整组语义事务上 cutover，
    并在 parity 与 differential gate 下退役 Python facade。
- [Shared-goal Online Authority and Pluggable Coordination Provider v0](shared-goal-authority-state-provider-v0.md)
  [验证边界](shared-goal-authority-state-provider-v0-evidence.md))
  - **RFC 状态：** Draft，maintainer 评审中。
  - **`main` 交付：** 基础、provider 契约与本地晋升准备切片已实现。
  - **当前边界：** 可恢复的共享权威基础、文件后端参考路径、NoKV shadow/recovery
    证据、TypeScript store 契约、PostgreSQL candidate/conformance 覆盖，以及
    default-off 的本地 shadow/cutover 基础已合入 `main`
    ([#3529](https://github.com/huangruiteng/loopx/pull/3529)，
    [#3669](https://github.com/huangruiteng/loopx/pull/3669)，
    [#3798](https://github.com/huangruiteng/loopx/pull/3798))。尚无 provider-first
    的运行时晋升或远程共享权威服务交付。
- [Shared Goal Alignment and Governed Amendment Protocol v0](shared-goal-alignment-and-governed-amendment-v0.md)
  
  - **RFC 状态：** Draft，maintainer 评审中。
  - **`main` 交付：** 仅提案。
  - **当前边界：** 现有 peer lane、未认领工作、claims/leases、Agent 范围的
    Goal Vision/Replan 与 provider-neutral 权威是输入。只读共享对齐投影、自动修订
    策略、verifier 边界与规范 Goal 修订事务尚未交付。
- [Goal Artifact Lifecycle Projection v0](goal-artifact-lifecycle-projection-v0.md)
  
  - **RFC 状态：** Draft，maintainer 评审中。
  - **`main` 交付：** 仅提案。
  - **当前边界：** Milestone、阻塞 gate 与合法迁移已规定为只读投影；尚无规范
    生命周期投影交付。

## 规划、研究与自适应智能

- [Research Exploration Control Plane v0](research-exploration-control-plane-v0.md)
  
  - **RFC 状态：** Draft，maintainer 评审中。
  - **`main` 交付：** 部分实现。
  - **当前边界：** M2 的显式组合投影与 successor 绑定已合入
    [#3173](https://github.com/huangruiteng/loopx/pull/3173)。规范观察契约、
    共享写时 gate、模型选择与推断触发器尚未晋升。
- [Hierarchical Agent Stride Control v0](hierarchical-agent-stride-control-v0.md)
  
  - **RFC 状态：** Draft，研究提案。
  - **`main` 交付：** M1 观察切片已实现。
  - **当前边界：** 只读 stride 观察及其合成边界夹具已合入
    [#3207](https://github.com/huangruiteng/loopx/pull/3207) 与
    [#3290](https://github.com/huangruiteng/loopx/pull/3290)。自适应 effect、
    交付与权威 stride 选择仍停留在研究阶段。
- [Post-Outcome Memory Utility Attribution v0](post-outcome-memory-utility-attribution-v0.md)
  
  - **RFC 状态：** Draft，maintainer 评审中。
  - **`main` 交付：** Stage 1 已实现。
  - **当前边界：**
    [#3280](https://github.com/huangruiteng/loopx/pull/3280) 在不改变检索排序的
    前提下把 utility 观察绑定到已验证结果。Reducer/读投影、provider readback、
    排序影响与试点晋升仍未解决。
- [Obelisk Session Evidence Provider v0](obelisk-session-evidence-provider-v0.md)
  
  - **RFC 状态：** Draft 集成提案。
  - **`main` 交付：** 仅评估。
  - **当前边界：** default-off 的只读 evidence-provider 边界已记录。Obelisk 未被
    安装、晋升，也不对 Replan 结算、记忆或动作选择拥有权威。

## Runtime、能力与协同集成

- [Provider-Neutral Turn-Start Inbox Hook v0](provider-neutral-turn-start-inbox-hook-v0.md)
  - **RFC 状态：** 已在显式 provider 配置后实现。
  - **`main` 交付：** 已实现，opt-in。
  - **当前边界：** provider-neutral 的 turn-start 读取契约与 Lark ACK/replay 路径
    已合入
    [#3678](https://github.com/huangruiteng/loopx/pull/3678) 与
    [#3733](https://github.com/huangruiteng/loopx/pull/3733)；没有任何 provider 被
    隐式启用。
- [Provider-Neutral Post-Writeback Capability Hooks v0](provider-neutral-post-writeback-capability-hooks-v0.md)
  
  - **RFC 状态：** Draft，maintainer 评审中。
  - **`main` 交付：** 首个端到端纵向切片已实现。
  - **当前边界：** periodic-report producer、持久 intent 生命周期、终态 closeout
    dispatch、consumer 与已批准的 Goal Channel 投递已通过
    [#3691](https://github.com/huangruiteng/loopx/pull/3691)、
    [#3748](https://github.com/huangruiteng/loopx/pull/3748)、
    [#3749](https://github.com/huangruiteng/loopx/pull/3749) 与
    [#3755](https://github.com/huangruiteng/loopx/pull/3755) 交付。通用多能力晋升
    仍在评审中。
- [LoopX Desktop Execution Frontends v0](desktop-execution-frontends-v0.md)
  
  - **RFC 状态：** Draft。
  - **`main` 交付：** 支撑基础已实现。
  - **当前边界：** attached 与 managed runtime、桌面与 connector 部件存在，但统一
    execution-frontend/session-ownership 契约与跨 transport 收敛尚未作为单个交付
    产品边界被接受。
- [Goal Channel Collaboration v0](goal-channel-collaboration-v0.md)
  
  - **RFC 状态：** Draft。
  - **`main` 交付：** Lark 纵向切片已实现。
  - **当前边界：** 绑定 Goal 的 Lark 群组、Kanban、gate 通知、共享 target 与 Bot
    runtime 集成已交付。provider-neutral 多面模型仍是 Draft，交互传输细节由
    Desktop Frontends RFC 细化。
- [Agent IM, LoopX, and OpenViking Collaboration v0](agent-im-openviking-collaboration-v0.md)
  - **RFC 状态：** Draft。
  - **`main` 交付：** 仅提案。
  - **当前边界：** LoopX、IM 与 OpenViking 已有相邻实现，但这一三方 owner 的协同
    契约尚未作为集成路径交付。

## 操作者体验与可观测性

- [Per-Goal Usage, Token, and Cost Surfacing v0](goal-usage-token-cost-v0.md)
  - **RFC 状态：** Draft。
  - **`main` 交付：** 核心切片已实现。
  - **当前边界：** Codex usage 捕获、归一化聚合与 dashboard 展示已合入
    [#3117](https://github.com/huangruiteng/loopx/pull/3117)；更广的 runtime/provider
    覆盖与成本语义仍不完整。
- [Intelligent Review and Dynamic Presentation Surfaces v0](intelligent-review-presentation-surfaces-v0.md)
  
  - **RFC 状态：** Draft，maintainer 评审中。
  - **`main` 交付：** 仅提案。
  - **当前边界：** 现有 typed 提案、gate、规划投影、receipt 与直接可逆动作 UX 是
    输入。共享的 `action_review_plan_v0` 编译器与动态 card/report/wiki 展示契约
    尚未交付。
- [Human Attention Wishlist v0](human-attention-wishlist-v0.md)
  
  - **RFC 状态：** Draft，maintainer 评审中。
  - **`main` 交付：** 有意推迟。
  - **当前边界：** 该 RFC 仍是讨论契约。运行时工作被搁置，直到重复的真实使用在
    不削弱非阻塞权威边界的前提下证明存在第二种需求。

## Benchmark 与可靠性工程

- [Benchmark Study Upload and Dashboard Projection v0](benchmark-study-upload-dashboard-v0.md)
  - **RFC 状态：** Draft 集成提案。
  - **`main` 交付：** 仅提案。
  - **当前边界：** experiment-board 行与 benchmark 原生分数仍是唯一权威；study
    manifest、上传/readback envelope 与 campaign 到 run 的 dashboard 投影是
    提案，尚未实现。
- [Long-Horizon Harness Benchmark and Research Program v0](long-horizon-harness-benchmark-research-program-v0.md)
  
  - **RFC 状态：** Draft，研究项目。
  - **`main` 交付：** 活跃的研究与工程项目。
  - **当前边界：** ALE、LHTB 与 DeepSWE 构成外部效度组合；benchmark 基础与证据
    流程正在建设，但不把研究项目当作运行时协议。
- [Long-Running Agent Reliability Diagnostics and Governed Delivery v0](long-running-agent-reliability-diagnostics-governed-delivery-v0.md)
  
  - **RFC 状态：** Draft，产品方向与交付契约。
  - **`main` 交付：** 仅方向。
  - **当前边界：** observer-first 采纳路径、匹配 benchmark 资格与受治理交付包是
    提案；尚未晋升出统一产品契约。

RFC 不得包含内部对话、私有链接、本地文件系统路径、凭证、原始记录或非公开的组织
上下文。
