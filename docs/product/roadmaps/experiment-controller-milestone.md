# 实验控制器里程碑

> [English](experiment-controller-milestone.md)

只有当接入长程实验控制器能让工作好过裸 Codex App goal 模式时，LoopX 才应该接入它。这个里程碑不是"开始 watch 另一个仓库"。它是一个产品 gate：更好的实验上下文、更好的人类 reward 捕获，以及更简单的多项目操作。

本文有意保持通用且 public-safe。项目特定的 run id、本地路径、生产指标与私有结论属于私有 adapter 或 run 载荷。

## 何时接入

当以下三个 gate 全部为真时接入实验控制器：

- 项目有稳定的目标、当前实验假设、最新可比结果，以及无需暴露私有细节即可表达的下一门控条件。
- LoopX 能比普通 goal-mode 线程更好地跨 run 保留上下文：目标、活跃分支、实验路线、指标目标、已知失败模式、阻塞状态与最新建议动作都在 reload 后幸存。
- dashboard 或 status 导出给 operator 的多项目视图比 Codex App 线程列表更清晰：什么需要人类判断、什么可以交给 Codex 工作、什么在等待外部 evidence、什么不适合推进。

如果 adapter 只能镜像聊天摘要，如果当前实验结果不可比，或者如果下一个动作依赖无法安全总结的私有生产 evidence，就不要接入。

## 实验板

长窗口实验控制器应当有一个项目本地实验板。该板是 adapter 的当前 evidence 界面；它不是原始日志转储。

板应分开：

- 目标与主决策指标；
- 决策窗口与可比基线窗口；
- 护栏指标；
- 非目标与不安全捷径；
- 活跃任务与要关注什么；
- 已完成锚点与路线历史；
- 启动或计算配额；
- 下一个交接条件。

Adapter 应在板所命名的决定性 evidence 中锚定 goal 身份。Runtime 风险、仅训练集移动或不可比指标可以是护栏，但不应替换主 goal。

## 好过裸 Goal 模式

对比目标是默认 Codex App goal loop：单线程加本地聊天上下文。

LoopX 必须增加：

- **持久上下文**：每次 run 写入紧凑的 public-safe 索引，需要时再加一个私有载荷。下一个 controller tick 应当无需重读整个线程就知道最新实验状态。
- **显式 gate**：run record 说明下一个动作是 run、inspect、wait、ask user 还是 block。过期或不可比的结果不应看起来像进展。
- **Reward 捕获**：人类反馈被结构化为 reward 事件，而不是淹没在聊天里。operator 可以说出哪个结果、判断或路线选择是好的、坏的、意外的，或值得重复的。
- **跨项目排队**：一个界面可以按等待方、severity、最新 run 健康与交接状态比较多个 goal。
- **安全边界**：公开示例与 status 导出保持净化，而私有 adapter 可以保留更丰富的本地 evidence。

如果这些字段不可用，实验应留在常规 Codex App goal 模式，直到 adapter 赶上。

## Reward 信号模型

人类 reward 在被评判的决策附近施加时最有用。实验控制器 adapter 应支持这种形态的小型 reward 记录：

```json
{
  "recorded_at": "2026-06-01T00:00:00+00:00",
  "goal_id": "example-experiment-goal",
  "run_id": "2026-06-01T00-00-00Z",
  "decision": "continue_route",
  "reward": "positive",
  "reason_summary": "latest comparable metric beat the previous route and validation was aligned",
  "follow_up": "promote the route to the next longer-window check"
}
```

公开索引只保留紧凑、非敏感字段。私有载荷可以保留更丰富的 evidence。`loopx status` 只在 `human_reward` 下保留 `recorded_at`、`decision`、`reward`、`reason_summary` 与 `follow_up`，让 dashboard 可以显示存在一条人类 reward 信号及其评判的决策类别。

使用 `loopx reward` 把这个紧凑信号追加到已有 run：

```bash
loopx reward \
  --goal-id example-experiment-goal \
  --run-generated-at 2026-06-01T00:00:00+00:00 \
  --decision continue_route \
  --reward positive \
  --reason-summary "latest comparable metric beat the previous route and validation was aligned" \
  --follow-up "promote the route to the next longer-window check"
```

写入器追加一个索引覆盖层；它不重写私有 run 载荷。这让 operator 反馈贴近被评判的决策，同时保持 public/private evidence 边界。

Dry-run 与追加响应也携带协调字段。Codex 可以在真实追加后把中文 `active_state_summary` 复制进活跃状态，而 project agent 应当使用 `project_agent_visibility.history_command` 从 run 历史读取 reward。这避免让聊天文本、dashboard 复制包或活跃状态散文成为持久的 reward 来源。
当该活跃状态摘要应由 CLI 写入时，使用显式 `--write-active-state-summary` 标志；`--dry-run --write-active-state-summary` 同时预览覆盖层与状态编辑。

Dashboard 可以为选中的 goal 与最新 run 生成 `Reward CLI Draft`。该草稿应默认 `--dry-run`；在浏览器写入能强制执行相同的 local-only 边界与 public-safe 文本检查之前，operator 仍通过 CLI 记录判断。

对于由 `loopx serve-status` 支撑的本地 dashboard，草稿也可以通过 `POST /reward/dry-run` 往返。该端点校验选中的 goal/run 与紧凑 reward 文本，但总是返回 `appended=false`。

浏览器侧追加仍是单独的 opt-in 设计 gate。安全边界定义在
[dashboard-reward-write-boundary.md](../../reference/contracts/dashboard-reward-write-boundary.md)。

## Controller 就绪模型

就绪度不同于 reward。它回答"现在什么级别的 controller 接入是安全的？"

实验控制器 adapter 应当用紧凑字段总结就绪度：

```json
{
  "classification": "ready_for_read_only_not_decision",
  "read_only_observer_ready": true,
  "decision_advisor_ready": false,
  "write_controller_ready": false,
  "missing_gates": [
    "human_reward_capture",
    "aligned_eval_decision_evidence"
  ],
  "review_judgment": "safe for read-only observation, not route decisions",
  "next_handoff_condition": "record aligned eval evidence and one human reward event"
}
```

常见进阶是：

- 只读观察者：持久上下文与多项目可见性就位后即为安全。
- 决策顾问：可比 evidence 与人类 reward 记录之后即为安全。
- 写控制器：保持 opt-in；LoopX 不应从观察或建议就绪度暗示变更权限。

## 就绪检查清单

接入真实实验控制器之前，验证：

- `loopx status` 在无本地路径泄露的情况下暴露 goal、最新 run、契约健康与关注队列。
- Adapter 写出紧凑 run 历史，包含 `classification`、`recommended_action`、`health_check` 与 artifact 可用性。
- 最新 run 包含 controller 就绪度，使 operator 能看到该 goal 是仅观察、决策顾问就绪，还是仍缺 gate。
- 下一个动作分开"再跑一个实验""等待可比 evidence"与"请人评判权衡"。
- dashboard 可以把某个 goal 与无关 goal 并列显示，而不会垮塌为单线程视图。
- 可以写入 reward 事件并随后总结，而不把私有生产 evidence 复制进公开文件。

## 当前实现切片

当前公开切片是只读的实验控制器契约：

- 用于 `await_eval`、`inspect_result`、`design_next_experiment`、`needs_human_reward` 与 `blocked_by_safety` 的 adapter 分类词表；
- 紧凑的 controller 就绪度 schema 与 dashboard 面板；
- 紧凑 reward 事件 schema 与 status 导出字段；
- dashboard 徽章与 run 历史面板，显示最新 run 是否具有 controller 就绪度与 human reward；
- 通过 loopback status server 的 dashboard reward dry-run 校验；
- 示例净化 run 与 reward 文件。

私有项目可以通过写一个项目本地状态文件与一条紧凑 run 记录来 opt-in 该 adapter。只有以上就绪检查清单为真时，它们才应接入真实控制器。
