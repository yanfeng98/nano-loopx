# 项目级奖励模型

> [English](project-level-reward-model.md)

LoopX 不应只用单一基准分数来说明长程 agent 的价值。基准对窄任务能力有用,但 Loop Agent 在项目内随时间的推移而工作:它吸收信号、完成工作、请求人工判断、花费 token,并为下一 Turn 留下 evidence。

本笔记定义一个保守的产品模型,用于比较这种项目级价值,而不声称通用基准提升。

## 核心公式

对于复杂的项目工作,LoopX 应把 agent 价值视为:

```text
project_reward = f(quantity, quality, token_cost, user_attention_cost)
```

该公式刻意面向产品。它不是模型训练奖励函数,也不是任务基准指标的替代品。它的职责是让 Loop Agent 可被人类运维者评审。

## 维度

### 数量

Agent 产生了什么。

可观察输入:

- 完成的 todo;
- 合并的 PR 或被接受的补丁;
- 已验证的文档、fixture 或演示;
- 解决的 gate 或阻碍;
- 写回运行历史的 evidence 包。

数量应计算有界交付物,而非聊天量。仅摘要的 Turn 不计为结果进展,除非摘要本身就是被请求的产物。

### 质量

输出是否有用且可信。

可观察或可评审的输入:

- 人工评审反馈:有用、没用、需要 evidence、范围外、太贵、私有/不安全;
- 校验强度:smoke 通过、具备证明产物、评审者接受、或阻碍被精确记录;
- 返工率:用户是否需要再次纠正同一失败模式;
- 边界质量:工作是否避开私有材料、原始日志、凭据与过度声称。

质量是智能管理界面必须帮助捕捉的维度。在有足够评审数据之前,使用粗标签如 `high`、`medium`、`low` 或 `blocked`,而不是假装精确。

### Token 成本

Agent 消耗了多少模型或执行器预算。

可观察输入:

- host 暴露模型 token 计数器时使用它;
- 作为回退的 LoopX 配额槽或运行时分钟;
- 达到已验证产物所需的执行器 Turn 数。

Token 成本应在跨不同运行时比较之前,先在一个项目或 host 集成内可比。

### 用户注意力成本

Agent 消耗了多少人工引导。

可观察输入:

- 打开的用户 gate 数;
- 重复或不清楚的提问数;
- 等待用户决策的时间;
- 可避免的纯状态更新的频率;
- agent 遵循预期路由前所需的纠正次数。

低注意力成本并不意味着"永不问用户"。好的 Loop Agent 在需要判断时提问,并避免让用户充当调度器。

## 绩效评审形态

项目级评审应在时间窗口内汇总一个车道或 Loop Agent:

```json
{
  "schema_version": "project_reward_review_v0",
  "goal_id": "loopx-meta",
  "agent_id": "codex-side-bypass",
  "window": "2026-06-22",
  "quantity": {
    "completed_todos": 3,
    "validated_artifacts": 2
  },
  "quality": {
    "label": "medium",
    "evidence": ["smoke_passed", "human_useful"],
    "risk": ["needs_more_user_feedback"]
  },
  "token_cost": {
    "label": "normal",
    "source": "quota_slots"
  },
  "user_attention_cost": {
    "label": "low",
    "asks": 1,
    "avoidable_reasks": 0
  },
  "review_summary": "Useful docs and dashboard progress; needs more outcome evidence before benchmark-level claims."
}
```

schema 应保持紧凑且可检查。它应引用源运行、todo、评审事件与校验产物,而不是复制原始转录或私有 evidence。

## 与基准的关系

基准结果仍然有用,尤其是单任务能力与受控比较。它们应在更广评审中作为一个 evidence 来源展示,而不是整个故事。

LoopX 应避免这些过度声称:

- "project_reward 改善了,因此模型总体上更好";
- "一个成功案例证明基准提升";
- "低 token 成本就是好的,即使质量低";
- "低用户注意力是好的,当 agent 悄然越过边界时";
- "许多完成的 todo 意味着高价值,而不需要人工评审或 evidence。"

相反,产品声明应更窄:

```text
LoopX makes long-running agent work reviewable by quantity, quality, cost, and
human attention, so operators can decide which Loop Agents deserve more trust.
```

## 产品界面

智能管理界面应在三个层面暴露此模型:

1. **评审流**:卡片级反馈,如有用、没用、需要 evidence、太贵、范围外或私有/不安全。
2. **车道快照**:一个 agent 车道的当前数量、质量标签、成本标签、注意力标签、阻碍与下一个预期。
3. **绩效评审**:在有界窗口内比较所选车道或锚点的周期汇总。

首次实现可以是只读的。打分与控制写入应保持分离:评审可以推荐 todo、gate 或重规划,但实际变更仍经过 LoopX 权威、配额与边界检查。

## 验收标准

此模型在以下条件满足时即可实现:

- status 或 dashboard 可以把数量、质量、token 成本与注意力成本显示为独立字段;
- 质量由显式评审事件或校验 evidence 驱动,而非来自聊天的隐藏推断;
- 基准分数可以作为 evidence 附加,而不成为唯一价值指标;
- 用户注意力成本可以区分好的用户 gate 与可避免的重复引导;
- 公开文档与 showcase 避免从这种项目级评审模型声称通用基准提升。
