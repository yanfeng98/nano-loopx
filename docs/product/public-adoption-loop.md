# 公开采用 Loop

> [English](public-adoption-loop.md)

状态:文档优先的产品契约。

LoopX 需要一条公开路径,让人们尝试具体工作流并报告哪些有效,而无需维护者在路线被证明之前先安装 GitHub 模板。本笔记定义模板文案、分诊标签与小型指标,并可在 owner 批准该写入范围之后提升为 `.github` 模板。

## 何时使用

当某人想在公开仓库工作流上尝试 LoopX,且反馈可以在不涉及私有源、私有日志、凭据、原始转录、基准任务文本或生产 evidence 的情况下表达时,使用此 Loop。

适合的首次工作流:

- 修复或分诊一个公开 GitHub issue;
- 评审一个 PR 并把发现转化为有边界的后续 todo;
- 用评审包执行一个 PR 规模的隔夜重构;
- 当高优先级项被人为 gate 阻碍时保持进展推进。

不要将此 Loop 用于私有客户工作、生产运维、隐藏安全报告、排行榜提交,或任何用户无法分享公开安全摘要的仓库。

## Issue 模板文案

建议标题:

```text
Try LoopX on: <workflow name>
```

建议正文:

```markdown
## Workflow

Which LoopX workflow did you try?

- [ ] Public issue fix or triage
- [ ] PR review-to-fix loop
- [ ] Overnight PR-sized refactor
- [ ] Blocked-P0 safe fallback
- [ ] Other:

## Starting Point

- Repository:
- Public issue or PR:
- Command or entry point used:
- Expected output:

## Result

- What did LoopX produce?
- What validation ran?
- What still needed human judgment?
- Did the loop stop, wait, or continue safely?

## Public-Safe Evidence

Link only public artifacts: PR, issue, docs, compact review packet, or public
smoke output. Do not paste private logs, credentials, raw transcripts,
benchmark task text, or local paths.

## Value Signal

- Time saved or avoided rework:
- Quality signal:
- User attention required:
- Would you run this workflow again?
```

## 讨论模板文案

建议提示:

```markdown
What workflow should LoopX make easier next?

Please include:

- the repo scenario;
- the human decision that currently blocks automation;
- the smallest public-safe artifact that would prove value;
- the command or chat entry point you expected to use;
- any privacy, permission, or publication boundary.
```

此讨论表单用于产品信号,而非支持升级。如果用户需要具体修复,请把信号转化为带公开安全起点与预期输出的 issue。

## 分诊标签

从解释工作流与边界的标签开始,而不是承诺解决方案的标签:

| 标签 | 含义 |
| --- | --- |
| `adoption:try-loopx` | 用户在公开工作流上尝试 LoopX。 |
| `workflow:issue-fix` | 公开 issue 分诊、规划、校验或 PR 评审包。 |
| `workflow:pr-review` | 评审发现应转化为 todo、补丁或 owner 决策。 |
| `workflow:overnight-refactor` | 需要可恢复 state 与评审包的长程重构。 |
| `workflow:blocked-fallback` | 受阻的高优先级路由需要安全的低优先级进展。 |
| `signal:user-value` | 报告包含具体的价值或注意力成本信号。 |
| `gate:needs-owner` | 进一步动作前需要人类决策。 |
| `privacy:public-safe` | Evidence 可安全公开引用。 |
| `privacy:needs-redaction` | Evidence 在公开讨论前必须脱敏。 |
| `status:needs-repro` | 工作流看似合理,但缺少可复现的公开路径。 |

标签是分诊提示,不是权限。发布评论、打开 PR、发布截图或编辑 `.github` 模板仍需要常规的 owner 与边界检查。

## 轻量指标

以 issue 或讨论上的紧凑笔记形式跟踪指标:

- `workflow_type`:issue_fix、pr_review、overnight_refactor、blocked_fallback 或其他;
- `entry_point`:slash_command、codex_cli_tui、codex_app、claude_code 或 manual_cli;
- `artifact_produced`:todo_plan、patch_pr、review_packet、validation_summary、blocker_packet 或 none;
- `validation_state`:not_run、failed、passed、partial 或 not_applicable;
- `human_gate_count`:具体用户/控制器 gate 的整数计数;
- `attention_cost`:low、medium 或 high;
- `would_repeat`:yes、no 或 unsure。

指标笔记应足够短,无需打开原始日志即可阅读。如果某个案例成为 showcase 候选,通过
[Issue/PR solver 维护者接收包](use-cases/issue-pr/issue-pr-solver-maintainer-intake.md)
或其他公开安全 showcase 路线提升。

## 提升为 GitHub 模板

此文档优先契约刻意位于 `docs/**` 内。要把它提升为真实的 GitHub issue 或讨论模板,先在确切的 `.github` 路径记录一个 owner 批准的边界决策,然后添加保留相同公开/私有边界的最小模板文件。

在该批准存在之前,本文档是采用 Loop 文案的规范来源。

## 相关文档

- [发布就绪度](release-readiness.md)
- [Codex CLI 打包安装路径](runtimes/codex-cli/codex-cli-packaged-install.md)
- [Issue/PR solver 维护者接收包](use-cases/issue-pr/issue-pr-solver-maintainer-intake.md)
- [公开/私有边界](../public-private-boundary.md)
