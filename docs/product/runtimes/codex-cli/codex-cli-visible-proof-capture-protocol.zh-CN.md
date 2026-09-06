# Codex CLI 可见证明捕获协议

> [English](codex-cli-visible-proof-capture-protocol.md)

状态：opt-in 证明捕获的 public-safe 协议。
主要路径：一条消息的 Codex CLI TUI bootstrap。

本协议把有希望的 Codex CLI `resume` / `remote-control` surface 变成 evidence，而不是 authority。只有 public-safe 证明显示该 Turn 可见、可中断、紧前有 idle guard，且独立于 transcripts、session 文件、stdout、stderr、凭据或隐藏 session 变更时，LoopX 才能晋升后续可见自动化。

## 何时使用

仅在以下全部为真时使用本协议：

- 用户已经从正常 Codex CLI TUI 流程开始，或显式 opt-in 了一次证明运行；
- `quota should-run` 允许这次 LoopX Turn；
- 测试 prompt public-safe，且不依赖私有仓库状态；
- 候选 surface 是 `visible_resume_prompt`、`remote_control_visible_prompt` 或 `same_tui_visible_attach` 之一；
- 目标是证明可见性，而不是交付生产工作。

如果任何条件缺失，保持一条消息的 TUI bootstrap 作为产品路径并记录 blocker，而不是尝试后续可见 Turn。

## 捕获 Packet

持久 packet 是两个 public-safe 夹具加验收结果。[Codex CLI Proof-Capture 演示](codex-cli-proof-capture-demo.md)中的公开演示 bundle 为可见 `resume` spike 与未来 same-TUI attach 证明都提供示例夹具。

### Visible-Session 证明夹具

```json
{
  "observed_surface": "visible_resume_prompt",
  "user_opt_in": true,
  "quota_guard": { "passed": true },
  "idle_guard": {
    "no_active_human_typing": true,
    "no_running_turn": true,
    "checked_before_prompt": true
  },
  "turn_visibility": {
    "visible_to_user": true,
    "prompt_public_safe": true
  },
  "interruptibility": {
    "user_can_interrupt": true,
    "manual_takeover_available": true
  },
  "boundary": {
    "reads_raw_transcripts": false,
    "reads_session_files": false,
    "reads_credentials": false,
    "mutates_hidden_session_state": false,
    "spends_quota_before_writeback": false
  },
  "writeback": { "compact_evidence_planned": true }
}
```

### Runtime-Idle 夹具

```json
{
  "observed_surface": "visible_resume_prompt",
  "idle_guard": {
    "no_active_human_typing": true,
    "no_running_turn": true,
    "checked_before_prompt": true
  },
  "turn_visibility": { "visible_to_user": true },
  "interruptibility": {
    "user_can_interrupt": true,
    "manual_takeover_available": true
  },
  "boundary": {
    "reads_raw_transcripts": false,
    "reads_session_files": false,
    "reads_stdout_stderr": false,
    "reads_credentials": false,
    "mutates_hidden_session_state": false
  }
}
```

夹具可以包含紧凑公开标签，如 `operator_initials`、`proof_started_at`、`proof_result` 或 `blocker`，但不得包含截图、来自私有工作的原始 prompt、原始模型输出、本地 session id、绝对本地路径、凭据、内部文档链接或命令输出正文。

## 流程

1. 选一个 public-safe 夹具仓库或演示 goal。
2. 用注册的 `agent_id` 运行 `quota should-run`；如果用户 channel 要求动作就停止。
3. 确认证明的显式用户 opt-in。用户必须知道该证明在测试可见性，而不是做生产工作。
4. 在候选 prompt 紧前捕获或生成新鲜 runtime-idle evidence。未知 turn state、近期输入或运行中的 Turn 都会 fail closed。
5. 只尝试带允许命令前缀的可见证明 prompt。Prompt 应说明 LoopX 在测试可见转向，且可以安全中断。
6. 只记录上述紧凑夹具布尔值与 public-safe 标签。
7. 校验夹具：

```bash
loopx codex-cli-visible-session-proof \
  --project . \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --proof-fixture visible-proof.public.json

loopx codex-cli-runtime-idle-detector \
  --project . \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --idle-fixture runtime-idle.public.json

loopx codex-cli-visible-attach-acceptance \
  --project . \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --proof-fixture visible-proof.public.json \
  --idle-fixture runtime-idle.public.json
```

8. 写回验收结果。只有在 blocker 或 evidence 写回且验证通过后才 spend quota。

## 晋升规则

`visible_resume_prompt` 与 `remote_control_visible_prompt` 可以证明有用的可见 spike，但它们不证明 same-open-TUI 自动化。它们保持实验状态，直到后续证明捕获 `same_tui_visible_attach`。

只有 `same_tui_visible_attach` 加通过的 runtime-idle 检测器才能把该路由晋升向 same-TUI 自动化驱动。即使如此，下一步也是单独接线任务：新鲜 quota guard、新鲜 idle guard、显式命令边界与紧凑写回。

## 停止条件

以下任一情况发生时停止并记录 blocker：

- 没有显式证明 opt-in；
- `interaction_contract.user_channel.action_required=true`；
- runtime-idle 状态未知、近期活跃或已在运行；
- 候选需要 transcript、session-file、stdout/stderr、凭据或隐藏 runtime 读取；
- 该路由写隐藏 Codex session 状态；
- prompt 不可见、不可中断或无法手动恢复；
- 命令前缀未被显式允许；
- 证明会暴露私有仓库名、task id、内部链接、本地路径、截图或原始 session 资料。

安全回退始终是保持一条消息的 TUI bootstrap 可见，并把精确 blocker 写入 LoopX。
