# 轨迹卫生 v0
> [English](trajectory-hygiene-v0.md)

LoopX 为审计与续跑保留控制面历史。该历史并非天然适合模型训练：配额记账、scheduler 确认、未变化的监控轮询与重复状态投影，其在长会话中的数量可能超过任务面对的动作数量。

`trajectory_hygiene_summary_v0` 是对现有紧凑 run index 的只读审计：

```bash
loopx history trajectory-hygiene --goal-id <goal-id> --limit 100
```

它报告 controller 事件密度、紧凑 controller 字符密度、非物化事件密度、重复的任务动作标签以及动作/结局归因覆盖。这些都是判断当前事件组合是否需要单独学习投影的代理指标，而非训练质量分数。

## 边界

该审计：

- 只读取公开安全的紧凑 run index；
- 不打开 run 工件、原始会话、原始轨迹、任务正文或 verifier 输出；
- 不改变 history、status、quota、todo、scheduler 或 state 语义；
- 始终报告 `seed_model_training_eligible=false`。

未来的学习投影应保留模型可见的任务上下文、assistant 动作、工具观测、人类决策与归因结局。controller 事件应继续留在审计 ledger 中，并通过稳定 id 关联到学习 Turn，而不是作为普通 user/model Turn 被重放。

原始审计轨迹对复现与事故分析仍然有用。它不得被静默改写为训练样本。
