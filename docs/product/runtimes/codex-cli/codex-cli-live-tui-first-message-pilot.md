# Codex CLI 实时 TUI 首消息试点


状态：已记录 blocker；手动 TUI 引导保持为主要路径。
记录时间：2026-06-21。

本说明记录一次真实的 Codex CLI TUI 试点，针对一条消息的 LoopX 引导路径。试点只使用一次性的 public-safe 仓库，并把原始 TUI 输出、Codex transcript、session 文件、凭据与私有项目路径排除在仓库之外。

## 问题

LoopX 能否用生成的开始消息启动一个真实可见的 Codex CLI TUI，并证明 loop 启动、保持可观测、且用户仍能控制？

## 方法

试点使用一个带小 `README.md`、小 `GOAL.md` 与生成开始消息的临时公开仓库：

```bash
loopx codex-cli-bootstrap-message \
  --project /tmp/loopx-live-tui-pilot.<suffix> \
  --goal-id public-live-tui-pilot-goal \
  --agent-id codex-side-bypass \
  --message-only
```

本地 Codex CLI surface 是 `codex-cli 0.142.0-alpha.7`。其 help 暴露：

- `codex [OPTIONS] [PROMPT]`；
- `--no-alt-screen`；
- `--cd <DIR>`；
- `resume`；
- `remote-control`。

尝试了两个有界探针：

1. 在一次性仓库中运行 `codex doctor`。它在手动中断前没有产生有界输出。
2. 用 public-safe 生成消息做真实 TUI 启动：

   ```bash
   codex --no-alt-screen --ask-for-approval never --sandbox workspace-write \
     -C /tmp/loopx-live-tui-pilot.<suffix> \
     "$(cat loopx-start-message.txt)"
   ```

第二个探针启动 Codex CLI，但在有界捕获窗口内没有产生紧凑、机器可检查的首响应结果。进程之后仍然活跃，被精确的临时仓库进程匹配停止。

## 结果

尚未证明。

生成消息可以通过 `codex [PROMPT]` 启动真实 Codex CLI TUI，但当前自动化侧证据不足以声称 LoopX loop 成功启动。

观察到的 blockers：

- 没有有界的首响应或完成信号；
- 在紧凑结果可用之前，捕获输出超出自动化预算；
- TUI 进程在捕获窗口后仍保持活跃；
- 把生成消息作为 `[PROMPT]` 传递时，prompt 会暴露在进程命令行中，这只对此 public-safe 试点可以接受，不应成为真实项目仓库的默认路径。

决策：

`live_tui_first_message_blocked_by_bounded_visible_completion_missing`

## 产品影响

公开用户路径仍应为：

1. 用户在项目仓库中打开 Codex CLI TUI；
2. 用户粘贴一条 LoopX 开始消息；
3. Codex 保持可见 TUI 作为实时控制 surface。

在存在有界可见试点 adapter 之前，LoopX 不应把自动化 `codex [PROMPT]` 启动宣传为已验证的首次运行路径。

该 adapter 需要在无 raw transcript 或 session 文件读取的情况下证明全部这些：

- 注入或粘贴开始消息，而不通过进程参数泄露项目特定 prompt 文本；
- 观察到紧凑 public-safe 首响应标记；
- 停止或 idle 检查 TUI，而不与用户赛跑；
- 证明用户仍可以控制、评审、中断或接管；
- 在 quota spend 之前写入紧凑成功 evidence 或精确 blocker。

## 后续

在晋升实时 TUI 自动化之前，创建有界可见试点 adapter：

```text
[P0] Codex CLI 有界可见 pilot adapter：在宣称 live TUI 首消息成功之前，
定义并测试针对 Codex CLI TUI bootstrap 的最小 public-safe 首响应捕获与停止
协议；避免 raw transcripts、session 文件、凭据、私有路径与 argv prompt 泄露。
```

在此之前，保持无克隆安装器、生成的粘贴消息与免 transcript 冒烟 bundle 作为可靠的首次运行路径。

## 有界 Adapter 命令

后续 adapter 是 public-safe 且 packet-only：它校验紧凑首响应夹具加 runtime-idle evidence，但不启动 Codex、不读 transcript、不读 session 文件、不捕获 stdout/stderr，也不改动 TUI。

```bash
loopx codex-cli-bounded-visible-pilot-adapter \
  --project /tmp/loopx-live-tui-pilot.<suffix> \
  --goal-id public-live-tui-pilot-goal \
  --agent-id codex-side-bypass \
  --first-response-fixture public-first-response.json \
  --idle-fixture public-runtime-idle.json
```

首响应夹具必须证明可见 TUI 显示了 goal id、user gate 或没有、首要 user todo 或没有、选中的 agent todo 与下一个安全动作；还必须证明用户可以中断或接管、紧凑写回在 quota spend 之前已规划，以及 bootstrap prompt 没有作为 argv prompt 传递。如果任何一块缺失，试点保持为精确 blocker，而不是成功声明。

## 可见捕获计划

在真实用户可见彩排之前使用此 packet：

```bash
loopx codex-cli-visible-first-response-capture-plan \
  --project /tmp/loopx-live-tui-pilot.<suffix> \
  --goal-id public-live-tui-pilot-goal \
  --agent-id codex-side-bypass
```

它打印 copy-first 流程、停止条件与示例 `public-first-response.json` / `public-runtime-idle.json` 形态。用户仍从 Codex CLI TUI 开始并粘贴生成消息；packet 只告诉 operator 在运行有界 adapter 之前要记录哪些 public-safe 布尔值。它从不运行 Codex、不读终端输出、不读 session 文件，也不接受 argv prompt 路径作为成功 evidence。
