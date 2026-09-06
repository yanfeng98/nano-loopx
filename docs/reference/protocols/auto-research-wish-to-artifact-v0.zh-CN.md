# Auto Research 从愿望到工件 v0
> [English](auto-research-wish-to-artifact-v0.md)

Auto Research 如今接受一个开放问题，并且已经可以产出假设、dev 与 held-out evidence、终态决策、独立评审与 Explore 发现。本协议围绕这些既有记录收拢交付契约。它不新增 scheduler、研究存储或 capability。

## 契约

`auto_research_delivery_contract_v0` 用以下内容包装现有 `research_contract_v0`：

- 一条原始公开安全愿望与一个稳定 `wish_id`；
- 假设与非目标；
- 必需工件声明；
- 绑定到精确 hypothesis id 的验收标准；
- 不成功结局的回退工件与重新进入条件。

规范化从完整规范化契约推导 `contract_revision`。记录契约不代表用户接受。从交付契约产出的 evidence 携带原子血统元组（`wish_id`、`contract_ref`、`contract_revision`）。三个字段都必须存在且精确匹配；部分或不匹配的血统会被排除在验证之外。每个愿望与修订只追加一条紧凑契约事件。旧版 `research_contract_v0` 包保留其既有事件形状并继续受支持。

## 回执

```bash
loopx auto-research artifact-receipt \
  --contract delivery-contract.public.json \
  --format json
```

该命令只读。它把当前契约修订、Auto Research evidence 图、终态决策、独立评审与工件引用折叠进 `auto_research_artifact_receipt_v0`。

聚合状态是下列之一：

| 状态 | 含义 |
| --- | --- |
| `verified` | 每个必需标准都有当前提升决策、必需评审和每个声明工件。 |
| `partial` | 某些标准或工件已验证，但完整交付契约仍未满足。 |
| `inconclusive` | 证据、终态决策或必需独立评审仍然缺失或冲突。 |
| `not_fulfilled` | 当前证据支持至少一个必需标准做出终态 retired 决策，并带任何所需独立评审。 |
| `stale` | 记录的 evidence 或终态决策属于更早的契约修订。 |

`not_fulfilled` 有意比一次不成功的尝试更强。一条失败命令、一次退化的 dev 结果或一个未解决的 retry 并不证明该愿望无法实现。

## 失败反馈

每个非 verified 回执都包括：

- `failure_kinds`：从当前证据、决策与评审状态推导的类型化原因；
- `unmet_criteria`：未满足的必需契约标准；
- `verified_boundary`：仍然已验证的标准；
- `missing_required_artifact_refs`：未观察到的声明必需工件；
- `fallback_artifact_refs`：实际观察到的声明回退工件；
- `reentry_conditions`：owner 编写的条件，加上精确到标准级别的修复提示。

回执不推断用户接受。它也不安装或提升 Skill、不修改 extension、不花费配额、不写入项目状态。`learning_disposition=candidate` 只表示一个已验证或终态不满足的结局具备参与后续治理性体验评审的资格。

## 过时

终态决策仍然绑定到假设证据修订。假设与 evidence 现在也携带交付 `contract_revision`。改变愿望假设、必需工件、验收标准或失败策略都会创建新契约修订。该新修订的回执不得把旧修订的证据复用为当前交付证明。

## 公共边界

交付契约与回执使用公开安全文本和不透明或相对工件引用。它们不包含原始日志、原始轨迹、凭据、私有物料或绝对本地路径。环境特定的重放状态仍归适配器所有；只有有界的公开证据引用可以进入本契约。
