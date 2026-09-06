# 有界自动研究失败后继设计


**状态：** 方向已接受；实现前仍需书面 spec 评审。

## 变更契约

**目标：** 确保一个已退休的自动研究假设产生一个有界的下一控制面结果：一次单一的数据/测量
修复、一个新的 hypothesis-proposer todo、一个 extension 演进提案，或一条显式的研究 frontier
耗尽记录。

**验收证据：**

- 负面证据 fixture 不能以隐式的 no-follow-up 收尾。
- 一个已声明的数据/测量缺口为其假设血统至多创建一个修复 todo，并且绝不创建 monitor。
- 一个不可修复的退休通过现有 role-successor 生命周期创建一个 proposer successor todo。
- 一个修复后仍然失败的血统创建一个 proposer successor 或显式 `frontier_exhausted` 结果。
- 每个 terminal 研究评估在完成之前记录一次本地演进 review，使 Agent 不能在正面或负面结果
  之后静默停止。
- 一次可复现的产品契约违规可以创建一个有界的 extension 演进提案，无需等待用户发现该缺口。
- 所有结果投影保持 public-safe，且不依赖网络、scheduler、服务或新包依赖。

**不在范围内：**

- 自动发明研究假设、改变策略或放宽阈值。
- 通过 `continuous_monitor` todo 等待未来数据。
- 自动编辑、安装、启用、升级或发布 extension。
- 创建协调器、后台 Agent 或第二个研究数据库。

**期望的实现边界：**

- `demo/auto_research/` 拥有 completion 与 role-successor 语义。
- `examples/auto-research-*.py` 拥有聚焦的公开回归证明。
- `docs/reference/protocols/auto-research-*.md` 拥有公开契约。
- 后来的 extension 演进提案仍是普通 LoopX todo，不是新的 extension runtime。

## 问题

当前自动研究 read model 识别负面证据并推导出 `retirement_candidates`。其 completion 状态随后
变成 `retirement_review_required`。然而默认 evaluator/promoter 角色档案只为正面 dev/holdout
路径声明 successors。一次 retirement review 完成后，不要求任何确定性角色后继。

这允许 Agent 在一个有效的失败结果之后停止，即使失败中包含可复用的研究约束或暴露了一个有界
的后续问题。通用 autonomous-replan 机制能检测到重复无进展，但它不知道某个具体研究失败应当
修复测量、改变机制还是关闭问题。

## 放置理由

```text
capability_id: auto-research
provider_id: loopx-core
origin: builtin
placement: demo/auto_research/
reason: The existing capability already owns research evidence, completion
        status, worker roles, and role-declared successor todos. The new
        behavior refines that lifecycle; it is not a provider-neutral
        extension capability.
```

后来的 extension 演进信号不会创造新 extension。它是给人类或 Agent 所有的产品 todo 的
public-safe 提案。现有 extension runtime 只负责 provider 生命周期。

## 设计原则

1. **每个完成的研究结果都是演进输入。** 一次 terminal 评估必须留下 durable 约束、后继、
   产品缺口提案或显式耗尽决策。
2. **负面证据也是进展。** 一个退休的假设必须留下 durable 约束与可见的下一决策。
3. **数据修复是例外且是有界的。** 一个血统至多声明一次数据/测量修复。弱指标本身不构成
   数据缺口。
4. **不伪装成参数搜索。** 修复可以修补已声明的 source、unit、corporate-action、proxy、
   split 或测量缺陷。它不能为了“拯救”原结论而改变阈值、时间窗、资产或选择标准。
5. **不等待未来数据的 monitor。** 如果没有当前有界的动作，研究问题显式关闭。未来工作可以在
   材料可用时从新契约开始。
6. **不做假自动化。** 控制面创建 todo 并强制允许的结果。假设 proposer 仍然撰写实际的
   证据支撑提案；kernel 绝不发明研究内容。
7. **无外部依赖。** 所有决策都从现有 LoopX rollout 事件、todo 血统与本地 role-successor
   写入推导。

## Completion 演进 review

每个 terminal evaluator/promoter 动作（`supported`、`contradicted`、`retired`、`promoted`
或重试耗尽）必须在它的 source todo 完成前推导并追加一条 `research_evolution_review_v0`
记录。

```json
{
  "schema_version": "research_evolution_review_v0",
  "goal_id": "example-research",
  "source_todo_id": "todo_distance_cache",
  "hypothesis_id": "hyp_distance_cache",
  "terminal_outcome": "contradicted",
  "constraint_refs": ["research_constraint:distance_cache_regresses"],
  "product_gap": {
    "status": "none",
    "fingerprint": null
  },
  "next_outcome": "propose_failure_successor"
}
```

该 review 精确有一个 `next_outcome`：

| 下一结果 | 含义 |
| --- | --- |
| `remediate_data_measurement` | 显式修复预算仍有剩余，且缺陷当前可以修复。 |
| `propose_failure_successor` | Proposer 必须撰写一个新的、改变机制的假设或显式耗尽。 |
| `extension_evolution_proposal` | 研究暴露了一个有界的产品或 extension 契约缺口。 |
| `constraint_recorded` | supported 或 promoted 的结果没有未解决的、安全范围内的后继；其方法约束仍是 durable 知识。 |
| `frontier_exhausted` | 不再有当前安全的机制、材料准备工作或产品缺口提案。 |

系统保证刻意关于**状态转换**，而不是生成的研究散文质量：它保证一个已完成的研究项不能在没有
演进 review 记录与五个可见结果之一的情况下静默关闭。Hypothesis-proposer lane 仍然负责新提出
假设的语义内容。

## 失败延续契约

引入一个紧凑投影与 durable 生命周期记录：`research_failure_continuation_v0`。

```json
{
  "schema_version": "research_failure_continuation_v0",
  "goal_id": "example-research",
  "hypothesis_id": "hyp_distance_cache",
  "source_todo_id": "todo_distance_cache",
  "failure_kind": "mechanism_contradicted",
  "failure_evidence_refs": ["research_evidence:hyp_distance_cache"],
  "remediation_attempt_count": 0,
  "remediation_attempt_limit": 1,
  "remediation_allowed": false,
  "monitor_allowed": false,
  "required_next_outcomes": [
    "propose_failure_successor",
    "frontier_exhausted"
  ]
}
```

该记录是 public-safe 的。它只记录紧凑 ids 与证据别名；不能包含原始 evaluator 日志、本地路径、
凭证、源码正文或 provider 载荷。

### 失败种类

| 失败种类 | 允许修复 | 必需下一结果 |
| --- | --- | --- |
| `mechanism_contradicted` | 否 | Proposer successor 或 frontier 耗尽。 |
| `overfit_or_nonreplication` | 否 | 带改变机制的 proposer successor，或 frontier 耗尽。 |
| `guardrail_or_protected_boundary` | 否 | 仅当存在安全新机制时才有 proposer successor；否则耗尽。 |
| `data_or_measurement_gap` | 是，一次 | 一次修复尝试，然后重新评估。 |
| `unrecoverable_data_gap` | 否 | 带不同当前可用信息集的 proposer successor，或耗尽。 |
| `retry_exhausted` | 否 | Proposer successor 或耗尽。 |

数据/测量缺口必须由 evaluator 以紧凑的 failure-evidence ref 与特定测量范围声明。kernel 不能
仅仅因为分数差或 holdout 失败来推断该分类。没有显式声明时，fail-closed 默认是
`mechanism_contradicted` 或现有的负面证据分类。

### 修复预算

修复计数从父假设血统与先前 `research_failure_continuation_v0` 记录计算，而不是从 Agent 重试
CLI 命令的次数计算。

- 计数 `0` 时，只对 `data_or_measurement_gap` 恰好允许一个 `remediate_data_measurement`
  successor。
- 计数 `1` 时，该血统的 `remediation_allowed=false` 永久生效。
- 一次修复保留原始研究目标、受保护范围与验收 gates。它只能修正已声明的测量范围。
- 其结果必须回到评估。第二次负面结果不能重开修复；它必须产生 proposer successor 或显式耗尽。

## 状态转换

```text
evaluated
  -> contradicted
  -> failure_continuation_required
       -> remediate_data_measurement      (only explicit gap and count=0)
          -> evaluated
       -> propose_failure_successor       (otherwise)
          -> hypothesis_proposed | frontier_exhausted
```

`continuous_monitor` 在此状态机中不是合法边。

### 完成规则

evaluator/promoter 只有在以下机器可见增量之一存在时才能完成一个 failure-review todo：

1. 一个带剩余修复预算、精确链接的 `remediate_data_measurement` successor；
2. 一个由 hypothesis-proposer lane 拥有、精确链接的 `propose_failure_successor` todo；或
3. 一条带紧凑 no-follow-up 理由的 durable `frontier_exhausted` 记录。

如果不存在任何一项，worker 报告 `failure_successor_required` 并保持 todo 打开。它不得使用
`no_followup=true`。

### Proposer Successor 要求

`propose_failure_successor` 是手动研究动作，不是自动思想生成器。proposer 必须精确选择一种
结果：

- **新假设：** 保留父假设与失败 refs，指明改变的机制或可用信息集，并说明为何该改变不是参数
  放宽。
- **Frontier 耗尽：** 记录不存在安全的、范围内且当前可执行的机制改变。这在没有 monitor 的
  情况下关闭问题。

新假设不能仅仅改变百分位切点、持有窗口、资产、时间片或排序阈值，却保留同一个失败的机制。

## 本地实现形态

### Read Model

`research_state.py` 从 retirement candidates 与现有 rollout 证据推导紧凑的失败延续摘要：

- 失败候选 ids 与证据别名；
- 已记录时的显式数据/测量分类；
- 血统修复计数与剩余预算；
- 允许的后继动作；
- 显式 frontier 耗尽是否是唯一允许的收口方式。

`build_auto_research_completion_status()` 把负面路径从 `retirement_review_required` 改为
`failure_successor_required`，直到允许的增量可见。

### 角色档案与 Worker Runtime

evaluator/promoter 档案除了当前正面证据 successors 之外还声明失败 successors：

- 只有当摘要具有 `remediation_allowed=true` 时才创建 `remediate_data_measurement`；
- 否则为 `hypothesis-proposer` 创建 `propose_failure_successor`。

Worker runtime 复用 `apply_role_successor_todos()`。它必须在调用现有 todo-completion helper
之前创建链接的后继。这使行为保持本地化、幂等、quota 可见、并与当前 role-successor 生命周期
兼容。

Hypothesis proposer 档案把 `propose_failure_successor` 加入其允许动作，并声明上述三种允许
结果。不引入新的协调器或 scheduler。

### Durable 记录

延续决策通过现有 rollout-event 机制追加，使后续 worker 能重算预算与收口状态。对于同一 source
todo 与延续结果，记录必须幂等。

## Extension 演进提案（P1）

P1 增加一个独立的、有界的产品改进信号。它不是 P0 失败后继转换的一部分，也不能自动改变
extension。

Completion 演进 review 把可能的缺口归类到两个阈值之一：

| 缺口类别 | 提案阈值 |
| --- | --- |
| `reproducible_product_contract_violation` | 当聚焦的本地 fixture 证明已发布或可执行的 LoopX 契约被违反时，一个研究血统就够了。 |
| `repeated_extension_or_provider_gap` | 同一 public-safe fingerprint 必须在至少两个不同研究血统中出现。 |

合格的 fingerprints 是：

- 当前 extension 契约无法表达的重复数据/测量验证缺口；
- 本应更早 fail closed 的重复 provider 边界歧义；或
- 迫使手动用户干预的重复缺失控制面后继。

单一来源失败仍是研究约束，除非它们证明了第一行的产品契约违规。提案 todo 包含紧凑
fingerprint、来源证据 refs、受影响的 owner、有界的契约变更、显式非目标与聚焦验证目标。它
绝不安装、启用、升级、修改或发布 extension。

该规则覆盖当前缺口：文档化的研究状态机允许 `contradicted -> hypothesis_proposed`，但可执行
的 evaluator completion 没有匹配的后继规则。一个聚焦 fixture 可以复现这一不匹配，因此演进
review 可以从一个完成的研究血统主动创建自动研究产品改进提案。

## 测试计划

测试在实现之前编写，并练习真实本地函数与 todo 生命周期路径。

1. **负面证据需要增量。** 一个退休的假设产生 `failure_successor_required`；没有后继或耗尽
   的 evaluator completion 被拒绝。
2. **每个 terminal 结果都接收演进 review。** Supported、contradicted、promoted 与
   retry-exhausted fixtures 各自在其 source todo 能关闭前发出一个
   `research_evolution_review_v0`。
3. **默认负面路径创建 proposer 工作。** 一个被反驳的假设为已注册 proposer lane 创建一个
   链接的 `propose_failure_successor` todo，且没有 monitor。
4. **一次修复限制。** 一个显式声明的数据/测量缺口在计数零时创建一个修复 successor。该修复
   被记录后，第二次失败创建 proposer successor 而不是另一次修复。
5. **显式耗尽合法。** 一条 durable `frontier_exhausted` 记录允许 no-follow-up 且无 monitor，
   并在 frontier 中保持可见。
6. **参数放宽防护。** 缺乏改变机制或测量范围的后继提案被拒绝。
7. **单血统契约违规可以提议产品修复。** 一个展示文档化转换但缺少合法后继的 fixture 创建一个
   `extension_evolution_proposal`；一次性的数据中断不会。
8. **Public-safe 投影。** 失败延续与任何 P1 提案拒绝路径、URL、凭证、原始日志与 provider
   载荷。

## 文档变更

更新现有 auto-research lane、state 与 role-state-machine 协议，以描述：

- 失败后继之前的有界修复；
- 无 monitor 的失败收口；
- 退休后 proposer 的责任；以及
- 研究约束与重复缺口 extension 提案之间的区别。

本工作不涉及任何首屏产品表面的变更。

## 交付计划

1. **P0：** 添加失败延续 read model、role successors、durable 记录与聚焦回归 smoke。
2. **P1：** 添加重复缺口聚合与普通 extension 演进提案 todo 生成，不进行任何 provider 变更。
3. **P2：** 为完整生命周期更新公开协议与紧凑 smoke 覆盖。

每个批次都可以独立评审。P0 是第一个实现段，因为它直接防止负面研究证据之后的静默停止。
