# Dashboard 预算治理合同

> [English](dashboard-budget-governance-contract.md)

状态:面向 LoopX ops dashboard 的公开安全 v0 合同。

LoopX 的预算与治理已经体现在内核对象中:配额、scheduler 提示、todo 所有权、gate、run history 与证据指针。Dashboard 合同把这些机器字段转化为运营者概念,但不会在浏览器侧建立第二个事实来源。

## 运营者概念

| 运营者概念 | 来源字段 | Dashboard 中的含义 |
| --- | --- | --- |
| 预算 | `quota.compute`, `quota.allowed_slots`, `quota.spent_slots`, `quota.state` | 该 Goal 在当前配额窗口内可以消耗多少自动 Agent 时间,以及现在是否可以运行。 |
| 节奏 | `scheduler_hint.codex_app`, `scheduler_hint.unchanged_poll`, `scheduler_hint.reset_policy`;`scheduler_hint.cold_path_detail.local_scheduler` 提供的可选用冷细节 | host 应该多久唤醒一次 Agent,何时启用退避,以及用户反馈或新工作何时重置间隔。 |
| 消耗规则 | `interaction_contract.cli_channel.spend_policy`, `scheduler_hint.unchanged_poll.spend_policy`, `work_lane_contract` | 哪些转换消耗配额,哪些生命周期检查不消耗。 |
| 人工控制 | user todos、operator gates、`local_dashboard_api`、未来的控制面 dry-run/apply 路径 | 人类可以批准、暂停、覆盖或恢复什么,以及浏览器是否被允许预览或应用变更。 |
| 证据 | todo ids、run ids、配额消耗事件、紧凑制品、源文件警告 | Dashboard 为什么相信当前的预算/治理状态,以及去哪里审计它。 |

Dashboard 应该用运营者语言表述这些概念,但下钻视图仍可显示精确的机器 token 以便调试。

## 控制语义

- **暂停自动工作:**以配额/控制面策略变更的方式呈现,而不是隐藏的浏览器标志。应用路径需要本地 loopback 明确启用与预览 id,或等效的 CLI 命令。
- **立即运行/覆盖节奏:**以一次全新的 `quota should-run` 开始;它不跳过 gate、claim、写入范围或 capability 检查。
- **重置节奏:**遵循 `scheduler_hint.reset_policy`。用户反馈、新增或重新分配的 todo、gate 解决以及实质性的状态转换,都会在退避恢复之前把 host 间隔重置为 profile 的初始值。
- **停止或最终检查 Loop:**Codex CLI TUI 与 Claude Code Loop 的最终检查、Loop 退出、节奏变化以及仅监听的静默轮询都是不消耗配额的转换,除非它们产生了经过验证的工作与写回。
- **消耗配额:**仅在持久写回之后:todo/状态/证据更新、`refresh-state`,然后一个 `quota spend-slot` 事件。

## Dashboard 投影

ops 前台可以渲染一个从 `goal_channel_projection_v0` 派生的紧凑 `Budget & Governance` 面板:

```json
{
  "quota": {
    "state": "eligible",
    "spent_slots": "2",
    "allowed_slots": "10",
    "scheduler_rrule": "FREQ=MINUTELY;INTERVAL=3",
    "scheduler_reset_token": "fixture-reset-token",
    "spend_policy": "spend after validated writeback",
    "pause_policy": "control-plane policy only",
    "override_policy": "fresh quota guard required",
    "latest_evidence_ref": "run:validated_progress_fixture"
  }
}
```

面板是只读的。它可以链接到 todo id、run 事件、本地 dry-run 能力和源文件警告,但不得直接修改项目事实。

## 验收锚点

- `frontstage-budget-governance` 从紧凑投影字段渲染预算、节奏、消耗规则、控制与证据。
- 文案说明节奏/最终检查/仅监听转换不消耗配额。
- 写入入口仍受 `local_dashboard_api` loopback 启用与预览锁定 API 的保护。
- 公开文档从 dashboard/状态文档索引链接本合同。

## 相关合同

- [配额分配](../../quota-allocation.md)
- [状态数据合同](../../status-data-contract.md)
- [长任务节奏策略](../../operations/long-task-cadence-policy.md)
- [Frontstage dashboard 交互基线](../../product/surfaces/frontstage-dashboard-interaction-baseline.md)
- [Runtime connector 目录](../../integrations/runtime-connector-catalog.md)
