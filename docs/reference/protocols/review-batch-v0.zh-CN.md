# Provider-neutral 评审批次 v0
> [English](review-batch-v0.md)

`review_batch_v0` 是受控人工评审的冷路径组合契约。它把已经规范化的候选包变成一个确定的决策界面。候选收集、仓库 API、聊天 API、评分策略与外部投递仍是采用方职责。

当多个来源需要一个稳定排序/限制、一份精确决策摘要和紧凑投递回执时使用它：

```bash
loopx review-batch compose --request-json request.json --format json
loopx review-batch bind-decisions \
  --batch-json batch.json \
  --decisions-json decisions.json \
  --format json
```

两个命令都是本地且无副作用的。它们不抓取候选项、不发布评论、不更新文档、不发送聊天消息，也不推断外部权限。

## 组合请求

`review_batch_request_v0` 包含：

- `batch_id` 与 `generated_at`；
- `policy.soft_limit`、`policy.hard_limit`、有序的稳定优先级原因码列表，以及采用方允许的决策值；
- 类型化的 `candidate_sources[]`，每个包含 `source_id`、`source_kind` 与规范化后的 `candidates[]`；
- 由外部适配器产出的可选紧凑 `sink_receipts[]`。

每个候选提供稳定 id 与来源引用、受限摘要、优先级层级与注册原因码、紧凑的证据状态/引用，以及一个提议动作或紧凑草稿。内核按层级、配置的原因顺序与稳定 candidate id 排序候选；它先应用硬限制，再应用软报告限制。

内核拒绝原始内容、日志、transcript、凭据、secret/token 字段与本地私有路径。采用方必须先规范化这些输入，再调用命令。

## 摘要与决策绑定

每个被选中的候选都会获得其在规范化身份、证据、优先级与提案之上的摘要。批次摘要把被选候选摘要的精确有序列表与策略绑定。`review_batch_decisions_v0` 必须重复批次摘要与每个已决策候选的摘要。`bind-decisions` 通过重算两层摘要来拒绝过期、被篡改、未知、重复或策略无效的决策，然后在不执行它们的情况下发出紧凑的 `review_batch_decision_receipt_v0`。

## 投递回执

sink 投递在内核之外运行。回执是 provider-neutral 的：

- `sink_id` 与 `sink_kind`；
- `status`：`preview`、`sent`、`failed` 或 `skipped`；
- 可选 `idempotency_key` 与 `receipt_ref`；
- `readback_verified`。

只有幂等性、回执引用与已验证回读全部存在时才接受 `sent`。内核不存储 provider 响应正文。

## 采用方边界

采用方可以获取 pull request、issue 评论草稿、文档或其他可评审项，但这些名称与策略不会进入本内核。它负责：

- 候选适配器与新鲜度检查；
- 映射到注册原因码的领域特定风险评分；
- 文档/聊天渲染与投递；
- 任何外部效果之前的权限检查；
- 只应用其精确摘要已成功绑定的决策。

这使得每日维护者报告、内容评审队列与运维决策简报共用同一份小型契约，而无需把某个 provider 或项目硬编码进 LoopX。
