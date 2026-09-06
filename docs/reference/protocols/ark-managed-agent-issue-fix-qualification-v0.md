# Ark 托管 Agent Issue-Fix 资格 v0
> [English](ark-managed-agent-issue-fix-qualification-v0.md)

本协议为单个 LoopX goal prompt 提交给 Ark Managed Agent Goal host 时的 LoopX issue-fix 工作进行资格界定。它组合既有 issue-fix 与 host 契约；不引入另一个运行时或另一种 prompt 家族。

资格界定刻意分阶段进行。一个修复后的文件是有用证据，但它不证明 Goal host 到达了持久化终态。

## 证据阶段

| 阶段 | 所需证据 | 通过条件 |
| --- | --- | --- |
| 1. 收件与路由 | 公开安全的 issue 元数据与一个 `issue_fix_feasibility_v0` 包 | 恰好选择一条路由。`fix_pr` 路由需要有命名 repro、受限范围与命名验证。 |
| 2. Worker 修复 | Repro 前、最小补丁、聚焦验证后与变更文件摘要 | repro 在补丁前失败，验证在补丁后通过，且工件达到评审就绪状态而未声称任何外部写入。 |
| 3. 持久化 LoopX 关闭 | 已验证的 todo writeback 加显式 successor 或 `no_followup` | 所选 todo 已持久化关闭，且新的 `quota should-run` 不再要求 worker 重复修复。 |
| 4. Goal host 关闭 | Goal 评估与终态会话状态的 host 事件 | 评估在满意中结束，Goal 达成，会话在无 provider、evaluator 或传输错误的情况下返回空闲。 |
| 5. 评审交接 | 评审包与显式权限状态 | 包已达到评审就绪。PR 创建、评审请求、合并与发布在另行授权前保持 false。 |

阶段 1–3 界定 issue-fix worker 路径。阶段 1–4 端到端界定一次性 Goal host 路径。阶段 5 界定交接边界；它不授予发布权限。

## 判定规则

使用这些判定，而不是一个过载的成功位：

| 观察到结果 | Worker 判定 | Goal-host 判定 | 含义 |
| --- | --- | --- | --- |
| repro、补丁、验证与持久化 todo 关闭全部通过；Goal 评估在满意中结束 | pass | pass | 端到端 host 用例通过。 |
| Worker 证据通过；Goal evaluator 或 provider 在满意前失败 | pass | fail | 修复是真实的，但 host 用例未完成。诊断 evaluator/provider 边界。 |
| 代码有改动，但聚焦验证或持久化 writeback 缺失 | fail | not reached | 不要把看似合理的 diff 当作已完成的 issue fix。 |
| Goal 在没有已验证修复工件的情况下报告满意 | fail | invalid | evaluator 结果不充分，用例必须被拒绝。 |
| 评审包就绪但外部写入权限缺失 | pass | pass 或 not applicable | 停在草稿/评审交接处；不要发布。 |

`issue_fix_validated_fix_artifact_v0` 有意只承载 worker 证据。它不包含 Goal 终态字段。Goal 满意度必须来自 host 事件流或等价的 host 回读，绝不来自补丁的存在。

## 代表性矩阵

一次 L2 资格运行应覆盖多于一个 happy-path issue：

1. 一个有界的 issue，选择 `fix_pr`，本地复现、应用最小补丁并通过聚焦验证；
2. 一个诊断有用但修复证据不充分的 issue，路由到 `comment_only` 并保持外部关卡；
3. 一个既无安全修复亦无有用评论载荷的 issue，路由到 `triage_only` 且不编造后续动作；
4. 一次使用与云 host 相同生成 `task_body` 的一次性 Goal-host 运行，包括持久化 todo 关闭与终态 Goal 回读；以及
5. 一个评审就绪的交接，证明在没有权限的情况下未发生评论、PR、合并或发布动作。

确定性仓库 fixture 覆盖修复机制。阶段 4 仍至少需要一次已认证的 host 运行；仅 mock provider 或单个成功补丁无法关闭该要求。

## 当前实时发现

一次全新的 Goal-host 一致性重放从同一干净修订安装 CLI 与 workflow skill，然后提交一个生成的 task body。真实的 issue-fix worker 复现了 retry-delay 缺陷、应用了一行修复、通过全部四个聚焦测试、写出评审交接，并以显式 `no_followup` 关闭其 LoopX todo。

下一次配额读取返回 `terminal_no_followup`，且用户与 agent todo 来源完整、无验收缺口。随后一个状态感知的 Goal evaluator 观察到该持久化终态、发出满意评估，会话返回空闲。该运行完成了 14 次已认证的 provider 交换。因此正确分类是 `repair=pass, durable_closure=pass, goal_host=pass`；发布仍是一个独立的受关卡交接。

私有 prompt、凭据、provider 载荷、本地路径与原始 trace 有意排除在本公开协议之外。

## 持久化检查

运行聚焦契约：

```bash
python -m pytest -q tests/test_ark_managed_agent_issue_fix_matrix.py
```

该测试组合当前可行性、确定性修复、Goal-host 与评审交接契约。它还阻止验证修复工件静默获得或暗示 Goal 终态权限。
