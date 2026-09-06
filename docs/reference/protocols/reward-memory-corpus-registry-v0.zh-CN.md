# Reward Memory 语料注册表 v0
> [English](reward-memory-corpus-registry-v0.md)

阶段 1 把五个 Stage-0 reward-memory 类别变成 provider-neutral 的语料清单与健康契约。注册表是无状态读模型；它不镜像 provider 内容、不成为第二个记忆存储，也不授予 agent 写入或应用召回物料的权限。

```bash
loopx reward-memory corpus-registry --format json
loopx reward-memory health-check --case wrong-project --format json
```

## 语料声明

每个语料声明：

- `corpus_id`、Stage-0 `class_id`、`provider_id` 与 `owner_ref`；
- 权威 `source_of_truth`；
- 分开的读与写权限；
- workspace、project、module surface 与可选 user、peer 或 session scope；
- 新鲜度模式与可选来源修订或最大年龄；
- active、superseded 或 retired 生命周期及血统；
- 是否需要 index、结果回读与应用回执；
- writeback 触发、关闭策略与退役权限；
- 隐私可见性以及原始内容不存在的恒等式。

参考注册表通过七个语料家族覆盖全部五个类别：

| 语料家族 | 类别 | 来源与生命周期 |
| --- | --- | --- |
| `run_reward_overlays` | `run_bound_reward` | LoopX human-reward 事件 ledger；追加式的精确 goal/run overlay。 |
| `authority_policy_sources` | `hard_policy` | 显式或由已验证贡献者推导的策略内容，始终绑定到独立验证的用户/仓库/操作员权限 scope。 |
| `scoped_preferences` | `soft_preference` | Provider 管理、显式评审过的、针对模块自有界面的反馈。 |
| `execution_trajectories` | `procedural_experience` | 带修订戳的执行证据。 |
| `distilled_experiences` | `procedural_experience` | 经评审并可被 supersede 的程序性或架构性学习。 |
| `session_working_memory` | `working_context` | 会话/归档修订绑定的继续上下文。 |
| `fresh_execution_context` | `working_context` | 当前 registry、todo、checkout 与有界工具观察。 |

这些参考条目是声明性家族，不是对某个实时 provider 或语料已配置的声称。实时模块从 provider 自有清单构建 `registered` 包。现有语义偏好 provider 清单可以在不暴露其原始 scope URI 的情况下桥接；通用注册表只保留摘要与显式项目及 surface scope。

## 权限与维护

读与写权限保持分离。模块级读取不授予 provider 写入，provider 管理写入不授予仓库发布，二者都不授予补丁权限。语料维护遵循这些规则：

1. 清单归 provider 或权威源 owner 所有；
2. 写入只使用声明的写权限；
3. 使用前验证来源修订、归档修订或新鲜度窗口；
4. superseded 与 retired 语料留在紧凑血统中，但停止影响召回；
5. 项目或 surface 不匹配失效关闭；
6. 退役保留紧凑原因，绝不保留原始记忆内容。

策略内容可以从已验证 owner 或核心贡献者的 reward、偏好、经当前工件验证的经验、选择以及接受/拒绝结局推导。注册表只在 actor 身份与仓库/动作 scope 独立验证之后，把它记录为维护触发；推断不能创建新的写入、发布、生产、跨用户或跨仓库权限 scope，也不能捏造具体 gate 的当前状态。置信度有意缺席于健康提升路径，因为它无法扩大权限。

## 健康状态

`reward_memory_corpus_health_v0` 把清单、检索、回读与使用保持为不同观察。分类器采用下列优先级：

| 状态 | 含义 |
| --- | --- |
| `wrong_project` | 请求的项目与语料 scope 不同。 |
| `wrong_surface` | 消费模块表面未注册。 |
| `unavailable` | 无法联系 provider 或声明的语料缺失。 |
| `empty` | 语料存在且可读，但不含记录。 |
| `stale` | 生命周期、来源修订、归档修订或新鲜度证据不是当前。 |
| `index_unavailable` | 语料存在但所需派生 index 缺失。 |
| `retrieval_failed` | 有界查询失败或尚未运行。 |
| `readback_unverified` | 检索返回了，但所选结果未回读。 |
| `retrieval_verified` | 当前作用域内结果已回读，但没有应用回执。 |
| `applied_verified` | 已验证结果还带有紧凑应用回执。 |

输出总是保留各个 pipeline 字段：

- `provider_available`；
- `corpus_present` 与 `record_count`；
- `index_required` 与 `index_present`；
- `retrieval_query_succeeded`；
- `result_readback_verified`；
- `memory_applied_with_receipt`。

因此空语料不会被报告为不可用。已有 index 不证明内容语料存在。检索成功不证明结果已被展开并验证，已验证回读不证明记忆影响了工件。

矛盾观察导致验证失败：应用要求回读，回读要求检索，检索要求语料可用且存在。健康结果可以使记忆具备咨询使用的资格，但始终返回 `memory_patch_authority=false` 与 `external_write_authorized=false`。

## OpenViking 对齐

对于 OpenViking，AGFS 内容保持事实来源，向量 index 是派生的检索引用。偏好映射到作用域偏好，轨迹与经验映射到两个程序性语料家族，完成的 Working Memory 归档映射到会话工作上下文。Cases 仍是训练与评估 fixture，不注册为可执行记忆。

`fresh_execution_context` 语料家族是 LoopX 已完整 registry、active-state、todo/quota、checkout 与有界工具观察之上的清单视图。阶段 2 不新增另一个上下文存储或检索路径。

Account、user、peer、session、project、surface 与仓库修订仍是独立 scope 维度。特别是，项目-对等偏好语料不能仅仅因为 provider 返回高分匹配，就复用于另一个项目或 surface。

OpenViking 默认的类型配额召回目前允许一个经验语料存在，而经验配额为零。因此注册表绝不从语料或 index 存在性推导检索健康。

## 阶段边界

阶段 1 实现语料声明、语义偏好清单桥、维护恒等式与确定性健康分类。它不执行 provider 写入、不持久化第二个注册表、不读取原始记忆、不蒸馏候选、不启用跨模块召回、不提升发布。

阶段 2 拥有一个薄候选与激活决策接缝。它可以从已验证贡献者信号推导策略内容，但不创建权限、不增加第二个存储或 scheduler、不执行 provider 写入、不启用自动召回。Issue Fix 消耗同一通用接缝，而非平行设计。阶段 3 实现显式精确语料、模块表面召回与推理中介的应用回执；确定性代码仍限于 scope、权限、隐私、新鲜度与冲突 guard。阶段 4 拥有评估与发布关卡；阶段 5 拥有有界 dogfood 与操作员编辑或退役控制。
