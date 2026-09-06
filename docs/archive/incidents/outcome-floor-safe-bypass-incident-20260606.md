# Outcome Floor 安全绕过事件


日期:2026-06-06

读者对象:LoopX 维护者、heartbeat 提示词生成器所有者、quota 契约所有者、
dashboard/status 所有者,以及 connected-project 控制器作者。

## 摘要

LoopX 正确检测到一个 connected 交付目标低于交接 outcome floor,但导出的
`quota should-run` 契约让下一个动作很容易被误读。载荷返回了 `should_run=false`
和 `decision=skip`,同时又返回了 `safe_bypass_allowed=true`、
`safe_bypass_kind=outcome_floor_recovery` 和
`heartbeat_recommendation.recommended_mode=outcome_floor_recovery`。

执行者在一个已安装的自动化提示词中遵循了通用 skip 分支并停止,即使预期行为是
一个有界的恢复段:产出 ranker/跨域证据,或写回具体 blocker。

这既是执行者失败,也是 LoopX 契约失败。执行者本应尊重
`safe_bypass_kind=outcome_floor_recovery`,但 LoopX 也不应让 Codex 拥有的恢复
路径看起来像静默 skip。

## 产品背景

LoopX 是长程 agent 工作的控制 surface。它应管理目标、状态、gate、quota、
证据、停止条件和 operator 可见的当前真相,让用户不必阅读每条 agent 线程。

对于 heartbeat 自动化,定时器只唤醒执行者。LoopX 拥有控制面决策:

- 普通交付是否可以运行;
- 目标是否在等待所有者/operator;
- 目标是否在等待外部证据;
- 焦点等待通道(focus-wait lane)是否仍可通过安全绕过被 Codex 寻址;
- 下一个有用工作是否必须是对应结果规模的证据,而不是表面传播;
- 完成的 turn 何时允许追加 quota spend。

本事件的核心问题是:LoopX 在一个顶层布尔值里混入了两个不同的问题:

- "普通交付可以继续吗?" 答案:不能。
- "现在有可以运行的有界 Codex 恢复动作吗?" 答案:有。

导出的契约应把两个答案都显式化。

## 观察到的载荷形态

受影响的 `quota should-run` 载荷(`agent-harness-side-bypass`)包含这些字段:

```json
{
  "decision": "skip",
  "should_run": false,
  "state": "focus_wait",
  "blocked_action_scope": "delivery_outcome_floor",
  "safe_bypass_allowed": true,
  "safe_bypass_kind": "outcome_floor_recovery",
  "waiting_on": "codex",
  "heartbeat_recommendation": {
    "recommended_mode": "outcome_floor_recovery",
    "notify": "DONT_NOTIFY"
  },
  "quota": {
    "must_advance": ["ranker_or_cross_domain_evidence"],
    "avoid": [
      "clean_downstream_surface_propagation",
      "synthetic_only_test_chain"
    ]
  },
  "user_todo_summary": {
    "open_count": 0
  },
  "agent_todo_summary": {
    "open_count": 1
  }
}
```

预期动作不是静默 skip,而是:

1. 在目标边界内执行恰好一个受限的 `ranker_or_cross_domain_evidence` 恢复段,
   或写回阻止它的 blocker。
2. 避免 surface-only 的下游传播和 synthetic-only 测试链。
3. 验证并写回活动状态、todo、critic 与下一个动作。
4. 只在验证后的证据或验证后的 blocker 写回之后 spend 一次。

## 问题出在哪里

1. 对一个可操作的恢复分支来说,`decision=skip` 和 `should_run=false` 太醒目。
2. `safe_bypass_allowed=true` 存在,但语义上被置于载荷和一些已安装自动化提示词
   的次要位置。
3. 已安装的自动化有一条过时的通用规则:"`should_run=false` 意味着不做实现、
   adapter 工作、文件编辑、研究、探索或花费。" 该分支在 safe-bypass 分支之前
   运行。
4. 已安装的自动化还携带项目专属的过时策略,而不是把当前策略委托给活动状态和
   `goal_boundary`。
5. 直接用户回合有进展后,全局/最新运行投影仍然过时。项目活动状态已经移到
   全航线(full-airline)干净作用域后,它仍描述一个更旧的 `0/8 current plan
   task ids` blocker。
6. Dashboard/status 对 `focus_wait` 的措辞没有清楚区分"所有者阻塞的焦点等待"
   与"Codex 拥有的 outcome-floor 恢复"。

## 已应用的本地缓解

受影响的 Codex heartbeat 自动化被替换为以下命令生成的紧凑正文:

```bash
loopx-canary heartbeat-prompt \
  --compact \
  --cli-bin loopx-canary \
  --goal-id agent-harness-side-bypass \
  --active-state <ACTIVE_GOAL_STATE_PATH>
```

这一缓解从已安装自动化中移除了手写的通用 `should_run=false` 硬停分支。它不是
最终产品修复:Goal Harness 通用契约和生成器仍需下面的 P0 变更,避免其他已安装
自动化重复同样的歧义。

## 期望语义

LoopX 应把普通交付资格与可操作恢复资格分开。

推荐字段:

```json
{
  "should_run": true,
  "normal_delivery_allowed": false,
  "safe_bypass_allowed": true,
  "recovery_delivery_allowed": true,
  "effective_action": "outcome_floor_recovery",
  "decision": "safe_bypass_recovery",
  "requires_user_action": false,
  "waiting_on": "codex"
}
```

`should_run` 应表示"现在存在一个 Codex 可动作的 turn"。普通交付通过
`normal_delivery_allowed=false` 单独保持阻塞。

建议的 decision 枚举:

- `run`
- `safe_bypass_recovery`
- `operator_gate_notify`
- `blocker_push_notify`
- `external_monitor_poll`
- `quota_skip`
- `throttled_skip`
- `blocked_health`

## 验收标准

1. 当 quota 载荷具有 `safe_bypass_kind=outcome_floor_recovery` 时,生成的
   heartbeat 提示词在普通交付之前处理该分支,即使 `should_run=true`。
2. `quota should-run` 暴露一个无歧义的机器字段,如 `effective_action=
   outcome_floor_recovery` 加 `should_run=true`,或 `recovery_delivery_allowed=
   true`。
3. Dashboard 首屏文案区分:
   - 所有者/operator 焦点等待;
   - 外部证据等待;
   - Codex 拥有的 outcome-floor 恢复;
   - 真正的静默 quota skip。
4. 已安装 heartbeat 提示词 smoke 覆盖该回归:具有 `should_run=true`、
   `normal_delivery_allowed=false`、`recovery_delivery_allowed=true` 和
   `safe_bypass_kind=outcome_floor_recovery` 的载荷必须在普通交付之前选择恢复。
5. 状态新鲜度可见。如果 `ACTIVE_GOAL_STATE.md` 比用于 `status` /
   `quota should-run` 的最新运行投影更新,载荷应暴露 `stale_status_warning=true`
   或等价物。
6. 已完成的直接用户回合工件可以被记录或刷新,使全局 registry/最新运行投影
   不再持续推荐一个被取代的 blocker。

## TODO

### P0:契约

- 给 `quota should-run` 添加显式 `effective_action`。
- 添加显式 `normal_delivery_allowed` 与 `recovery_delivery_allowed`,或等价的
  无歧义拆分。
- 当下一个预期动作是 Codex 拥有的安全绕过恢复段时,确保 `decision` 不是
  `skip`。
- 让 `should_run` 表示"存在 Codex 可动作的 turn";普通交付资格通过
  `normal_delivery_allowed` 单独暴露。

### P0:Heartbeat 提示词生成器

- 重新排序生成的 heartbeat 分支:
  1. `effective_action=outcome_floor_recovery` /
     `recovery_delivery_allowed=true`;
  2. operator/用户 gate 通知;
  3. 外部 monitor 分支;
  4. 通用 `should_run=false` 静默 skip;
  5. 普通交付。
- 为恢复形态添加生成提示词 smoke 用例:`should_run=true`、
  `normal_delivery_allowed=false` 与 `recovery_delivery_allowed=true`。
- 从已安装提示词中移除项目专属的过时策略。项目 steering 应位于 registry、
  活动状态、adapter 输出或 `goal_boundary` 中。

### P0:状态新鲜度

- 在 `status` 与 `quota should-run` 中比较当前活动状态的 `updated_at` 或文件
  mtime 与最新运行的 `generated_at`。
- 如果最新运行过时,暴露紧凑告警,并避免把过时的 `recommended_action` 当作
  当前权威呈现。
- 为"过时最新运行 vs 更新的活动状态写回"添加 smoke 覆盖。

### P1:直接用户回合写回

- 为不来源于 heartbeat spend 的直接用户回合工件提供 public-safe 的
  `record-run` / `refresh-state` 路径。
- 此类更新要求显式交付提示:`delivery_batch_scale`、`delivery_outcome`、
  分类、工件引用,以及当前 blocker/进展状态。
- 确保回合后的防护检查不能继续推荐被取代的 blocker。

### P1:Dashboard / Operator 视图

- 把 `focus_wait` UI 至少拆分为:
  - `focus_wait_owner_blocked`;
  - `focus_wait_external_evidence`;
  - `focus_wait_codex_recovery_allowed`。
- 当 `waiting_on=codex`、`user_todo_summary.open_count=0` 且
  `safe_bypass_allowed=true` 时,显示"需要 Codex 恢复动作",而不是"等待所有者"。

### P1:Spend 语义

- 在 CLI 与生成提示词中显式化 safe-bypass 恢复的 spend 规则:静默 skip、
  blocker-push、预检失败、dry-run、自我取消、重复记账或 surface-only 报告
  一律不花费;在验证后的证据或验证后的 blocker 写回之后 spend 一次。
- 添加一个 spend-slot smoke:接受带 `should_run=true` 与
  `normal_delivery_allowed=false` 的 safe-bypass 恢复记账,同时拒绝通用静默
  skip。

### P2:迁移 / 已安装自动化卫生

- 添加一个命令或 dashboard 检查,检测其 `should_run=false` 分支先于 safe-bypass
  处理的已安装自动化提示词。
- 添加 canary-rollout 助手,为选定的目标从 `heartbeat-prompt --brief
  --cli-bin loopx-canary` 重新生成已安装提示词。
- 当已安装自动化文本包含应位于活动状态或 `goal_boundary` 的过时项目策略时
  发出警告。

## 非目标

- 不放松 operator gate。
- 不允许普通交付绕过 outcome-floor 焦点等待。
- 不把 surface-only 报告变为可花费。
- 不把项目专属的侧旁绕过(side-bypass)策略变成全局规则。

目标不是"多运行"。目标是让控制面足够精确地表达真正的下一个动作:当 Codex
负责时项目 agent 可以继续,当用户负责时停下,并且只在验证后的工件或 blocker
写回之后 spend。
