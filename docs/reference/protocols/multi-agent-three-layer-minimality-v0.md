# multi_agent_three_layer_minimality_contract_v0
> [English](multi-agent-three-layer-minimality-v0.md)

`multi_agent_three_layer_minimality_contract_v0` 定义 LoopX 多 agent 产品的可复用分层规则：

1. **用户层：** 声明意图与少量产品级选项。
2. **Preset 层：** 提供领域默认值、角色语义、交接提示与产品证据或指标适配器。
3. **内核层：** 拥有可复用的多 agent 机制。

目标不只是最小化用户的片段。preset 也必须保持轻薄，使 auto-research 可以成为未来多 agent 产品的可复用示例，而不是第二个产品特定 runner。

## 所有权

| 层 | 拥有 | 不得拥有 |
| --- | --- | --- |
| 用户 | 目标、轮数、可选角色覆盖、可选数据/评估入口点。 | Tmux/Codex TUI 启动、pane 级 tick 命令、quota/frontier 协议细节、worker 管道、逐 agent vision/replan 状态或机器 JSON 路由。 |
| Preset | 领域角色、交接提示、指标/证据循环与领域默认值。 | 通用 runner 生命周期、真实 Codex TUI pane、workspace/trust-safe 启动、pane 级 A2A tick、todo/evidence/status 协议、逐 agent vision 预算、replan 状态迁移或紧凑人类状态。 |
| 内核 | 多 agent runner、真实 Codex TUI pane、workspace/trust-safe 启动、pane 级 A2A tick、todo/evidence/status 协议、CLI 强制的逐 agent vision 预算、vision/replan 状态迁移、紧凑人类状态与默认角色 prompt 脚手架。 | 领域特定的研究、benchmark、支持或销售语义。 |

## 契约形状

可复用 helper 位于 `demo/multi_agent/contract.py`：

```python
build_three_layer_minimality_contract(
    product_id="customer-support",
    preset_id="support_triage_preset",
    user_intent_fields=["inbox", "rounds"],
    preset_responsibilities=["triage_roles", "handoff_hints"],
)
```

它返回：

```json
{
  "schema_version": "multi_agent_three_layer_minimality_contract_v0",
  "principle": "user_and_preset_stay_thin_kernel_owns_reusable_mechanics",
  "user_layer": {
    "owns": "intent"
  },
  "preset_layer": {
    "must_remain_reusable": true
  },
  "kernel_layer": {
    "cross_product_reuse_required": true
  }
}
```

## Auto-Research Preset

Auto-research 是通用内核之上的一个 preset。其 preset 层拥有研究角色、交接提示、指标/证据循环与领域默认值。它不拥有 runner、TUI pane、workspace/trust-safe 启动、pane 级 A2A tick、todo/evidence/status 协议、逐 agent vision 预算或 replan 状态迁移。

这保持公开承诺的真实性：一个小型 auto-research recipe 应证明其他产品也可以用各自轻薄 preset 复用同一内核。

## 公开行数声明

「几行 auto-research」的公开声明计数的是声明性 recipe 行，而非共享内核实现。

对于默认 auto-research 演示，有界声明是：

| 层 | 计数行 | 含义 |
| --- | ---: | --- |
| 用户 | 1 | `loopx auto-research start "<open question>" --execute` |
| Auto-research preset | 4 | 默认角色 spec：curator、mapper、runner、verifier |
| 通用内核 | 0 | 共享 runner、Codex TUI pane、固定唤醒 prompt、pane 级 tick、todo/evidence/status 协议 |

因此诚实的口号是：一行用户代码加一个四行 preset 就可以在共享 LoopX 内核上启动去中心化 A2A 研究 Loop。该口号不得声称 tmux 启动、Codex TUI 引导、quota/frontier、证据路由或状态投影在 auto-research preset 内部被重新实现。

## 开发者实现预算

同样拆分适用于源代码，而不只是命令示例。`demo/auto_research/preset.py` 读起来应像一个小型 preset：角色默认值、角色 profile、successor 声明、seed todo 措辞与围绕通用 helper 的薄包装。可复用的 A2A 证明字段，例如 `broadcaster_selects_todo=false`、`each_pane_reads_own_quota_frontier=true` 与 `leader_agent_required=false`，属于 `demo/multi_agent/recipe.py`。

这保持面向开发者的承诺真实：未来产品应能通过编写各自简短 preset 复制该模式，而不是导入 auto-research 内部实现。

## 集体轮数 Ledger

`multi_agent_collective_round_ledger_v0` 是多 agent 轮数的内核拥有证明界面。它记录预期 lane、每 lane quota/frontier/turn 结局、整合证据与角色声明的 successor todo。产品 preset 可以把领域指标包装到 ledger 上，但不应分叉其轮数定义或引入协调者来决定工作。

## 规范 Auto-Research Recipe

Auto-research 应保持足够小，使开发者能一眼看到整个产品特定 recipe：

```text
loopx auto-research start "<open question>" --execute
research-curator:research-curator:research_curator
hypothesis-proposer:hypothesis-proposer:hypothesis_proposer
research-executor:research-executor:research_executor
evaluator-promoter:evaluator-promoter:evaluator_promoter
```

这五行就是产品 recipe：一个用户问题加四个研究角色身份。固定去中心化唤醒 prompt、真实 Codex TUI pane、pane 级 quota/frontier tick、successor todo 协议与 `multi_agent_collective_round_ledger_v0` 证明仍是通用内核行为。

对于 KNN 演示，auto-research preset 可以声明研究指标与角色 successor 提示，但不得添加产品特定协调者、工作流 runner 或指标聚合器。必需证明是：四轮集体角色轮数、至少两项 held-out 指标改进、公开安全证据，以及一份说明哪些 lane 参与的通用集体轮数 ledger。

## 验收

一项变更只有满足以下条件才符合本契约：

- 用户 recipe 仍是少数意图字段，而非 runner 配置；
- preset 没有 host 进程生命周期或 pane 级 tick 实现；
- preset 没有逐 agent vision/replan 机制的产品特定分叉；
- 通用内核契约保持领域无关；
- 另一个多 agent 产品可以在不导入 auto-research 代码的情况下复用同一内核。
