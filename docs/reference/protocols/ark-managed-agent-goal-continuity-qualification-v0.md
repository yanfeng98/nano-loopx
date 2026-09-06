# Ark 托管 Agent Goal 连续性资格 v0

本协议为 LoopX 由单个 Ark Managed Agent Goal activation 驱动时的暂停、会话替换与可恢复失败行为进行资格界定。它扩展一次性 host 契约；它不把 LoopX 变成 Goal 运行时，也不把 LoopX Turn 用作内部驱动器。

连续性不等同于保持一个 host 会话存活。有效的恢复从持久化 owner 重建工作，并把 host 会话视为执行信封。

## 状态 owner

| 状态 | 权威 owner | 恢复要求 |
| --- | --- | --- |
| 仓库变更与验证工件 | 项目工作区 | 先重新打开同一持久化工作区，或恢复显式工作区 checkpoint，再做更多工作。 |
| Goal 边界、todo 前沿、claim、evidence、quota 与 lease | LoopX registry、active state 与 event/runtime 存储 | 运行一次全新的 `quota should-run`；绝不从聊天记忆或旧 prompt 重建前沿。 |
| 已安装的 LoopX CLI 与 workflow skill | 一个固定的 installer 版本 | 读回一个 CLI/skill 修订。Codex 与 Managed Agent 仅在 installer 目标根目录上不同。 |
| Goal 评估阶段与终态结果 | Goal host 持久化 journal 与事件回读 | 在评估另一次完成之前先 rehydrate。磁盘上存在 journal 本身并不证明发生了 rehydrate。 |
| 继续、推迟或完成决策 | `quota should-run.scheduler_hint.goal_runtime_continuation` | 消费类型化的处置与推迟唤醒策略；从 Host 契约指定的同级 scheduler 字段读取原因与状态身份。绝不由 Goal prompt 或 evaluator 措辞推导唤醒行为。 |
| Host 会话 id 与内存中 transcript | Host 会话 | 非权威。它可能有助于定位事件，但其存续不是连续性要求。 |

## 恢复序列

在暂停、host 替换或模糊传输失败之后：

1. 重新打开预期工作区并验证其仓库身份；
2. 运行 installer/doctor 回读并拒绝混合的 CLI/skill 修订；
3. 读取当前 LoopX 状态并运行 `quota should-run`；
4. 消费 `goal_runtime_continuation_v0` 及同级 scheduler 原因与重置身份；立即继续、持久化推迟到身份改变或受检重新检查截止时间到来，或按指示完成 host Goal；
5. 对账所选 todo、claim 或 lease、evidence 与工作区 diff；
6. 在重试一个准入状态未知的 activation 之前检查 Goal host 事件；
7. 从 LoopX 状态重新生成当前 `task_body`，且仅当回读证明需要另一次 activation 时提交一次；并且
8. 在调用恢复完成之前，要求同时具备已验证的 LoopX writeback 与 Goal host 终态证据。

当持久化前沿未变时，重新生成的 prompt 可能在文本上完全一致。这是预期行为。在未作状态与配额读取的情况下复用旧 prompt 才是不行的。

## 重试决策

| 观察 | 动作 |
| --- | --- |
| 传输在 host 接受 Goal 之前失败，且回读证明不存在任何 Goal | 从当前状态重新生成，然后提交一次。 |
| 准入状态未知，或 host 事件显示评估/工作已开始 | 不要盲目重提。先读取 host 事件、工作区效果与 LoopX writeback。 |
| worker 写入了工件，但持久化 todo evidence 缺失 | 验证工件，然后修复 LoopX writeback，不要重跑已完成的副作用。 |
| LoopX todo 已关闭但 Goal 评估仍待处理 | 让 Goal 运行时恢复评估；不要重新打开已完成的 todo。 |
| Goal journal 无法 rehydrate 或与 host 事件矛盾 | 失效关闭，并为诊断保留工作区/前沿。 |

只有幂等读取才是安全的默认重试。可重试的网络错误不会使 Goal 提交或仓库变更幂等。

## 资格阶段

| 阶段 | 所需证据 | 当前确定性接缝 |
| --- | --- | --- |
| A. LoopX 前沿重建 | 替换进程选择同一 todo，并且在不使用不透明 host 会话句柄的情况下读取最新持久化 note/evidence。 | `test_fresh_host_reconstructs_frontier_from_durable_loopx_state` |
| B. 工作区重建 | 替换进程观察到预期的仓库身份、diff 与验证工件。 | 在代表性 issue-fix fixture 中演练。 |
| C. Goal 运行时 rehydrate | 重启后的 Goal host 重放其 journal，保留评估迭代，并在无重复评估或跟进的情况下到达下一个合法状态。 | 需要 host 重启测试；仅存在 prompt 或 journal 不够。 |
| D. 模糊失败恢复 | 已认证 canary 在已知持久化边界后中断、替换会话，并在无重复副作用的情况下到达一个终态结果。 | 声明完整 L3 连续性之前必须完成。 |

阶段 A 证明 LoopX 不依赖 host 内存。它不能证明阶段 C 或 D。完整连续性需要全部四个阶段。

安装遵循 [host-integration-surface-v0](host-integration-surface-v0.md#ark-managed-agent-host) 中的固定脚本契约。Onboarding 与 doctor 仍是回读界面，而不是替代 installer。

## 聚焦检查

```bash
python -m pytest -q tests/test_ark_managed_agent_host.py
```
