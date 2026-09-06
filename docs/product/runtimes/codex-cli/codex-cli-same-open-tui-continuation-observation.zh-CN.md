# Codex CLI Same-Open-TUI 延续观察

> [English](codex-cli-same-open-tui-continuation-observation.md)

状态：已观察到 same-open-TUI 引导延续；调度式 same-TUI 自动化仍被阻塞。
记录时间：2026-06-21。

本说明记录一次来自实时 Codex CLI TUI session 的 public-safe 观察。它有意比新的 runtime packet 契约更窄。Evidence 关注的是交互式一条消息路径在同一个打开的 TUI 中保持可见，而不是调度器向隐藏或分离 session 注入未来 prompt。

## 问题

用户能否用一条 Codex CLI TUI 消息启动 LoopX，并在初始 LoopX guard 与转向步骤期间，让同一个可见 TUI 成为观察、转向、评审与接管的地方？

## 观察

可以，对交互式引导延续路径。

在观察到的 session 中：

- operator 从一个已经可见的 Codex CLI TUI 开始，并显式要求 LoopX 把该 TUI 保持为主要 surface；
- agent 在运行更长工作之前先显示当前 goal id、具体 user gate、首要 user todo、首要 agent todo 与下一个安全动作；
- 注册 agent 的 quota guard 最初返回一个 peer workspace 修复，而该修复以可见方式处理：把 shell 工作切换到独立的 peer worktree，而不是使用隐藏的 headless 执行；
- 同一个注册 agent quota guard 随后从独立 worktree 返回 `decision=run` 与 `effective_action=normal_run`；
- 随后的转向保持在同一个可见 TUI session 中，没有把 headless `codex exec` 切换为主要路径。

该观察没有读取原始 Codex transcript、session 文件、stdout 或 stderr 流、凭据、截图、本地私有资料或隐藏 TUI 缓冲。它没有修改隐藏 Codex session 状态。

## 结果

`same_open_tui_bootstrap_continuation_observed`：是。

这证明一条消息 TUI 引导之后，人工观察下的延续可以在第一个 guard、workspace 修复与转向决策期间保持在同一个打开的 TUI 中。

`scheduled_same_tui_attach_proven`：否。

当前验收 packet 在晋升后续自动化 same-TUI 转向 Turn 之前仍需要 public-safe 的 visible-session 证明夹具。本地 idle 标志单独不够，packet 在未提供证明夹具时正确返回 `visible_session_proof_required`。

## 产品决策

产品路径保持为：

1. 用户在项目仓库中打开 Codex CLI TUI；
2. 用户粘贴一条 LoopX 引导消息；
3. LoopX 显示紧凑控制面快照，并在 quota 允许时在同一 TUI 内执行一个有边界的可见片段；
4. 在 visible-session 证明与 runtime-idle evidence 通过之前，后续自动化保持阻塞；
5. `codex exec` 保持为显式 headless 回退，不是默认交互路径。

这让可信 TUI 保持台前，同时避免过早宣称 LoopX 能安全地向同一个打开 session 注入未来的调度式 Turn。

## 验证

本观察的 public-safe 验证命令：

```bash
loopx --format json --registry "$HOME/.codex/loopx/registry.global.json" \
  quota should-run --goal-id loopx-meta --agent-id codex-side-bypass
```

从独立 peer worktree 返回 `decision=run` 与 `effective_action=normal_run`。

```bash
loopx --format json codex-cli-visible-attach-acceptance \
  --project . \
  --goal-id loopx-meta \
  --agent-id codex-side-bypass \
  --observed-surface same_tui_visible_attach \
  --turn-state idle \
  --human-input-idle-seconds 30 \
  --min-human-input-idle-seconds 5 \
  --checked-before-prompt \
  --visible-to-user \
  --user-can-interrupt \
  --manual-takeover-available
```

没有证明夹具时返回 `decision=visible_session_proof_required`，这正是调度式 same-TUI 自动化的预期 blocker。
