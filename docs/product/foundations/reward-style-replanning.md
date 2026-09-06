# 奖励风格重规划提示


LoopX 已记录精确到运行边界的 `human_reward` 叠加与运维者 gate。下一个产品问题不是"在用户聊天上训练"。它更小也更安全:当人类反复奖励、纠正或引导一个长程 agent 时,LoopX 应把这种显式反馈转化为紧凑的重规划提示,帮助下一个有界 Turn 选择更好的 todo。

本笔记定义公开安全的奖励风格学习的形状。它是设计契约,不是排名模型的实现。

## 产品目标

让人类反馈存活进重规划,而不变成隐藏的自主性。

重规划器应能回答:

- 用户最近奖励了哪种工作;
- 用户纠正了哪类重复行为;
- 哪些未来候选 todo 更可能有用;
- 自上一 Turn 以来什么反馈改变了计划;
- 提示在哪里停止,因为 gate、认领、范围、能力或边界有更高权威。

输出应改进候选排序与解释。它不得授予权限、批准 gate、认领 todo、花费配额、发布产物或读取私有材料。

## 输入

只有显式且紧凑的来源应喂给该车道:

- 附加到精确运行的 `human_reward` 叠加;
- 以公开安全 todo、阻碍、reward 原因或 refresh-state 笔记写回的用户纠正;
- 运行历史中已摘要的重复引导模式,如"仅表面进展 Loop"或"缺少校验 evidence";
- 通过 LoopX 命令记录的显式 owner 决策。

排除的输入:

- 原始聊天转录;
- 私有文档或内部链接;
- 原始基准日志、轨迹、verifier 尾部或生产痕迹;
- 推断的人格画像;
- 用户无法检查或纠正的隐藏偏好。

## 提示形态

未来实现可以把紧凑提示投影为 `replan_hint_v0` 记录:

```json
{
  "schema_version": "replan_hint_v0",
  "goal_id": "loopx-meta",
  "source_refs": [
    {"kind": "human_reward", "run_generated_at": "2026-06-20T04:16:49+08:00"},
    {"kind": "todo", "todo_id": "todo_abc123"}
  ],
  "hint_kind": "prefer_candidate",
  "summary": "Prefer bounded work that produces validated outcome evidence over surface-only docs churn.",
  "applies_to": {
    "task_class": "advancement_task",
    "action_kinds": ["outcome_evidence", "validated_writeback"]
  },
  "anti_pattern": "surface_only_progress_loop",
  "strength": "medium",
  "confidence": "explicit",
  "expires_after_days": 30,
  "hard_gate": false,
  "boundary": {
    "may_reorder_candidates": true,
    "may_override_user_gate": false,
    "may_override_claim": false,
    "may_override_scope": false,
    "may_override_capability_gate": false
  }
}
```

重要字段是 `hard_gate=false`。提示是排名影响,不是权限规则。

## 重规划使用

在引导审计期间,LoopX 可以把候选 todo 与激活提示结合:

1. 从当前 active state 与状态投影构建候选 todo。
2. 移除被用户 gate、缺失能力、worktree 护栏、必需认领、受保护写入范围或公开/私有边界阻碍的候选。
3. 只对剩余候选应用提示。
4. 用来源引用解释所选候选,例如:"选择它是因为最近反馈偏好在另一个仅文档传播步骤之前验证结果 evidence。"
5. 当提示改变排序时保留落选的高价值候选。

这让偏好学习从属于控制面。它可以帮助 agent 选择更好的工作,但无法让不安全或未授权的工作变得安全。

## 运维者界面

dashboard 或评审包应显示一个紧凑的"什么反馈变了"界面:

- 被奖励的行为;
- 被纠正的行为;
- 候选排序效果;
- 来源引用;
- 过期或衰减;
- 一键退休或编辑提示的路径。

非技术用户应看到普通语言效果,而非模型权重。例如:

```text
Your last correction deprioritized "status-only updates" when a validated
artifact can be produced. This turn will prefer a bounded implementation or
evidence writeback before another summary-only note.
```

## 隐私与边界规则

- 存储摘要,而非原始反馈正文。
- 保留对精确运行、todo 或 reward 叠加的来源引用。
- 优选短期提示并带衰减;旧反馈不应永远悄然支配新上下文。
- 默认不把无关项目合并进一个偏好画像。
- 不把推断偏好用作安全策略。
- 不在公开文档、fixture 数据或 showcase 示例中暴露私有材料。

## 首批实现切片

1. **只读提示预览**:从现有紧凑 `human_reward` 与 todo evidence 派生候选提示,而不写入它们。
2. **投影 smoke**:证明提示可以重排两个安全候选 todo,但不能覆盖用户 gate、认领、能力 gate 或对等方工作区护栏。
3. **Status/dashboard 投影**:最多显示三个带来源引用与到期时间的激活提示。
4. **运维者编辑路径**:允许用户通过显式本地写入命令退休或重写一个坏提示。

在这些切片存在之前,人类 reward 仍是持久真相源,重规划提示仍是产品设计笔记。
