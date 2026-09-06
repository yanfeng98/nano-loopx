# Codex CLI 可见 Attach 证明试点


状态：已记录 blocker，TUI bootstrap 保持为主要。
记录时间：2026-06-21。

本说明记录第一个 public-safe 证明试点：LoopX 在不把用户带离可见 TUI 的情况下转向一次后续 Codex CLI Turn。它使用 PR #383 中添加的 `codex-cli-visible-attach-acceptance` packet。

## 问题

LoopX 今天能否安全地向同一个打开的 Codex CLI TUI session 添加一次后续转向 Turn？

## 结果

还不能。

当前 Codex CLI help surface 暴露有希望的 `resume` / `remote-control` 风格 capability，所以仍值得探索。但可用的 help-only evidence 没有证明安全的 same-TUI attach 原语。验收 packet 返回：

- `decision`：`visible_session_proof_required`
- `accepted_for_same_tui_automation`：`False`
- `accepted_for_visible_later_turn`：`False`
- `driver_mode`：`visible_resume_or_remote_control_spike`
- blocker：`visible_session_proof_missing`

## 边界

该试点没有：

- 运行 Codex CLI 交付；
- 读取原始 transcripts；
- 读取 session 文件；
- 读取 stdout/stderr 流；
- 读取凭据；
- 改动 Codex session；
- 由自身 spend LoopX quota。

## 解读

`resume [PROMPT]` 与 `remote-control` 单独不够。它们可能可以作为可见 spike 使用，但在 public-safe 证明显示以下各项之前，LoopX 不应称它们为 same-TUI 自动化：

- 结果 Turn 对用户可见；
- 用户可以中断或接管；
- runtime idle 检测器在该 Turn 紧前通过；
- 该路由不要求 transcript/session-file 读取；
- 紧凑 evidence 或 blocker 会在 quota spend 之前写入。

在该证明存在之前，产品安全路径保持：

1. 从一条 Codex CLI TUI bootstrap 消息开始。
2. 保持后续自动化在无执行 packet 模式。
3. 只在显式 opt-in 时把 `codex exec` 用作 headless 回退。

## 下一步

只有当证明可以捕获为带用户 opt-in 与 runtime-idle evidence 的 public-safe 夹具时，才运行可见 `resume` / `remote-control` 证明。如果该证明不读私有 session 资料或与 TUI 赛跑就无法捕获，保持这个 blocker，并继续改进一条消息的 TUI bootstrap 路径。
