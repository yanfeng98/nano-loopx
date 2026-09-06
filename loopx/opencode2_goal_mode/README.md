# LoopX OpenCode 2 适配器

> [English](README.md)

OpenCode 2 交付新的进程内 plugin API，且 OpenCode 1 plugins 不在其下运行。LoopX
通过 OpenCode 2 HTTP API 驱动 OpenCode 2 会话，使用持久化进程外 goal worker，
而不是 plugin。

该 worker 拥有循环定时器，因此循环操作在 TUI 关闭、一次性 CLI 使用与客户端重启
后仍然存活。OpenCode 1 保留既有 goal 桥接；两个表面共享同一静态命令门面。

## 安装

静态命令门面（`/loopx`、`/loopx-global-*`、`/loopx-pr-review`）安装到共享
OpenCode 配置目录，同时服务 OpenCode 1 与 OpenCode 2：

```bash
loopx slash-commands --install
```

Worker 本身随 LoopX 交付，无需在 OpenCode 侧安装：

```bash
which opencode2
loopx opencode2-goal-worker --help
```

## 运行时

运行 `/loopx <task>`，启动 goal 时选择 `--host-surface opencode2`，然后从返回的
激活 packet 启动 worker：

```bash
loopx opencode2-goal-worker \
  --goal-id <goal_id> \
  --directory <project directory> \
  --task-body "<task body>" \
  [--agent-id <agent_id>] [--capability <name>]... \
  [--session-id <existing session>]
```

循环是：

```text
prompt session -> 等待 assistant Turn 完成
  -> loopx quota should-run（generic_cli profile，host poll 回执）
  -> run_now: 以 quota gated 延续 prompt 继续
  -> wait: 退避阶梯，安静等待期间不调用模型
  -> terminal_no_followup: 可见关闭通知，然后待机轮询
     （worker 保持附着，并在新工作出现时自动恢复，而不是在一个任务后暂停）
  -> unchanged-poll limit: 可见合成暂停通知，worker 退出
  -> goal_not_found: worker 退出；goal 不再注册
```

用户消息绝不暂停循环。模型回答消息，worker 照常经 quota 延续 gating。停滞会话、
Turn 等待预算、Turn 预算或时长预算仍会可见地暂停。

## 状态

Worker 状态是每 Goal 的私有 JSON 文件，位于 `$LOOPX_OPENCODE2_STATE_DIR`，默认为
`$XDG_STATE_HOME/loopx/opencode2`，使用 mode `0600`。带 pid 与心跳的锁文件防止
两个驱动运行同一 goal；崩溃 worker 的锁在陈旧窗口之后被接管。

`quota should-run --record-host-poll` 在 goal 状态文件旁写入紧凑回执。
`loopx global-risks` 标出期望继续但却在陈旧窗口内静默过久的回执，因此等待中途
死掉的 worker 可见，而不是无声停滞。

## 限制

- Turn 等待预算：每个 assistant Turn 120 分钟（超时后 worker 可见地暂停）。
- Turn 预算：10000 Turns；时长预算：30 天。两者都以可见合成通知停止循环。

OpenCode 2 API 处于 beta；worker 只通过 `opencode2 api` 使用稳定的 JSON session、
message、prompt 与 synthetic endpoints。
