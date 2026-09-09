# Codex CLI TUI 优先的 LoopX Loop


状态：产品契约与实现目标。

LoopX 应该让 Codex CLI 易于采用，同时不夺走用户已经信任的交互式 TUI。目标不是"用隐藏 daemon 代替 Codex"。目标是：

1. 用户在项目仓库内打开 Codex CLI TUI。
2. 用户发送一条简短消息。
3. Codex 在不要求手工克隆仓库的情况下发现或安装 LoopX，保守地连接仓库，读取 gate/todo 状态，并报告下一个安全动作。
4. 设置 Turn 立即安装薄的 LoopX goal/heartbeat 正文，然后在更长交付工作之前停止。
5. 后续自动化可以在安全时转向同一个可见 session，而用户仍可观察、中断、评审或接管。

## 产品目标

最佳首次运行体验是一条 TUI 设置消息：

```text
Connect this repo to LoopX from this visible Codex CLI TUI. Do not clone the
LoopX repository for ordinary use. If `loopx` is not on PATH, install or repair
it from PyPI with Python 3.11+:
python3 -m pip install --upgrade loopx
loopx workflow-skills --install

Then run `loopx doctor`. Work only from this project root: if LoopX state
already exists, reuse it and do not create or overwrite a goal; if the project
is not connected, prefer `loopx connect`, and use `loopx bootstrap` only when
goal state clearly needs initialization. Ensure `.loopx/`, `.codex/goals/`,
and `.local/` are ignored. Keep me in this TUI, do not use hidden headless
execution. After the project is connected, generate the thin heartbeat prompt
and set the current Codex CLI goal to `/goal <thin task_body>`. Then stop and
report the goal id, current user gate, top agent todo, and next safe action.
```

这段文本应当是 Codex CLI 原生的设置路径：先设置，包括把薄 loop prompt 立即安装进 surface。在 Codex CLI 中 loop 是 `/goal <thin task_body>`。这条消息足以让终端 agent：

- 运行 `loopx doctor`；
- 在要求用户克隆 LoopX 仓库之前，用 PyPI 与打包 workflow-skill 安装器安装或修复缺失的本地 CLI；
- 在不创建或覆盖 goal 的情况下复用既有 LoopX 状态；
- 需要时连接仓库，只在明确需要初始化时使用 bootstrap；
- 确保 `.loopx/`、`.codex/goals/` 与 `.local/` 保持本地；
- 生成 `heartbeat-prompt --thin`；
- 把当前 Codex CLI goal 设置为 `/goal <thin task_body>`；
- 报告 goal id、user gate、首要 agent todo 与下一个安全动作；
- 在未被显式请求并验证交付之前，写回设置状态而不 spend 交付配额。

用户不应在看到价值之前就需要理解 registry 路径、runtime root、活跃状态文件、quota JSON 或 heartbeat prompt。

## Runtime 划分

| 层 | 拥有 | 不得做 |
| --- | --- | --- |
| Codex CLI TUI | 可见用户交互、本地工具执行、转向、评审、手动接管 | 在 LoopX 状态里隐藏用户决策 |
| LoopX | goal 状态、user gates、agent todos、claims、quota、写回、紧凑 evidence | 替换 Codex CLI runtime 或存储原始 transcripts |
| 本地驱动或 scheduler | wakeups、idle 检查、session 附着尝试、回退启动 | 注入到活跃用户 Turn 或绕过 gate |

LoopX 应当做控制面。Codex CLI 应当保持执行器与用户的实时控制台。

## 运行模式

### 1. TUI Bootstrap

这是第一个受支持的路径。用户在 Codex CLI TUI 中开始并粘贴一条 LoopX 设置请求。Agent 执行安装/连接，生成薄 heartbeat prompt，把当前 Codex CLI goal 设置为 `/goal <thin task_body>`，报告当前 gate/todo/next-action 快照，然后停止。它不应在描述完产品后就停，也不应为纯设置工作 spend 交付配额。

该模式完全保留 TUI，因为人类显式在那里启动了 loop。

当前原型：

```bash
loopx codex-cli-bootstrap-message --project . --goal-id <goal-id>
```

把生成的设置消息复制进 Codex CLI TUI。它告诉 agent：需要时修复/安装 LoopX，保守连接仓库，生成薄 heartbeat 正文，把 Codex CLI goal 模式设置为 `/goal <thin task_body>`，为第一个快照运行 quota/status guard，遵守 `interaction_contract`，保留可见 TUI，并在更长工作之前停止。

免 transcript 首次运行冒烟 packet：

```bash
loopx codex-cli-tui-bootstrap-smoke-bundle --project . --goal-id <goal-id> --agent-id <agent-id>
```

该 packet 用于产品与发布验证，不是额外用户步骤。它检查 PyPI-first 安装修复路径、纯复制粘贴块、quota guard 命令与有界写回/spend 命令，而不启动 Codex、不读 transcript、不检查 session 文件、不改动 session，也不 spend quota。

第一个有用的 TUI 响应应当是控制面快照，而不是关于内部的长篇讲解：

- 当前 goal id；
- 具体 user gate，或"无"；
- 首要 user todo，或"无"；
- 首要 agent todo；
- 下一个安全动作。

Registry 路径、runtime root、JSON 载荷、本地驱动计划、clone/canary 设置与 visible-session 证明夹具都是后续诊断。首次用户看到当前 goal/gate/todo 状态之前不需要这些。

当前试点 packet：

```bash
loopx codex-cli-one-message-loop-pilot --project . --goal-id <goal-id> --agent-id <agent-id>
```

该命令不运行 Codex。它把第一条 TUI 粘贴消息与安全的 scheduler/执行器桥打包进一个可评审 packet：

- 首次 Turn：把一条 LoopX 消息粘贴进可见 Codex CLI TUI；
- 首响应：显示 goal id、具体 user gate 或没有、首要 user todo 或没有、首要 agent todo 与下一个安全动作；
- 首个工作片段：如果 guard 允许工作，认领或选择一个可运行的 agent todo，并在同一个可见 TUI Turn 中完成一个有边界的验证片段；
- 后续 scheduler：默认以 dry-run 模式使用 `codex-cli-local-scheduler-exec`；
- 桥副作用：要求新鲜 guard 加显式候选前缀或 blocker-writeback opt-in。

该试点是对用户体验的契约检查。它不是首次用户的先决条件；首次路径保持"粘贴一条消息并观察 TUI"。

### 2. Session-Attached 自动化

这是偏好的自动化目标。Scheduler 唤醒，运行 `quota should-run`，然后尝试向同一个 Codex CLI session 添加一次可见的 LoopX 转向 Turn。

有效附着需要：

- 稳定的 session 标识或恢复句柄；
- idle guard，避免自动化与人类输入的消息赛跑；
- 一条可见注入 prompt，说明 LoopX 现在为何转向；
- `interaction_contract.user_channel.action_required=true` 时的硬停止；
- 只在 session 产生验证过 evidence 之后写回与 spend。

如果 Codex CLI 无法暴露安全的 session 附着原语，LoopX 不应靠写隐藏状态伪造它。它应回退到透明模式。

当前探针：

```bash
loopx codex-cli-session-probe
```

该探针默认只有 help：它检查公开 Codex CLI 命令 surface，如 `codex --help`、`codex exec --help` 与 `codex resume --help`。它不读原始 transcripts、凭据、本地 session 文件，也不改动 Codex session。关键区分是刻意的：`exec` 或 `resume` 支持可以是有用的回退，但它不是 LoopX 能把可见 Turn 注入同一个打开 TUI 的 evidence。同 session 自动化需要显式的可见 attach/inject 原语加 idle guard。可见 `resume [PROMPT]` 或实验性 `remote-control` surface 比纯 headless 回退更强，但直到 LoopX 证明该 Turn 可见、有 idle guard、可中断且不与人类输入的 TUI 消息赛跑之前，它仍属于单独 spike。

当前 driver-plan 原型：

```bash
loopx codex-cli-visible-driver-plan --project . --goal-id <goal-id>
```

该命令把探针结果变成 dry-run 驱动计划。它不运行 Codex、不读原始 transcripts、不读 session 文件、不改动 Codex session，也不 spend LoopX quota。它的职责是在三种下一模式中选择：

- `session_attached_visible_turn`：未来本地驱动可以尝试检测到的可见 attach 原语，但只在 quota guard 与 idle guard 之后。
- `visible_resume_or_remote_control_spike`：`resume [PROMPT]` 或 `remote-control` 存在，但它必须证明该 Turn 可见且可中断，LoopX 才会把它当作 session-attached 自动化。
- `tui_bootstrap_only`：要求用户从 Codex CLI TUI 内部开始。如果探针只暴露 `codex exec`，LoopX 仍留在此模式，因为默认 `/goal` 产品路径禁用了 headless 回退。

当前本地驱动规划器：

```bash
loopx codex-cli-local-driver-plan --project . --goal-id <goal-id> --agent-id <agent-id>
```

该命令是自动化设置的保守 MVP。它把 quota guard、visible-driver plan、TUI bootstrap 命令、headless 禁止边界与 idle-guard 要求组合进一个 dry-run packet。它不运行 Codex、不读 transcript、不读 session 文件、不改动 session，也不 spend quota。

当前本地 scheduler 执行 wrapper：

```bash
loopx codex-cli-local-scheduler-exec --project . --goal-id <goal-id> --agent-id <agent-id>
```

没有显式执行标志时，该命令仍是无执行 packet。对于之后的可见 Codex CLI Turn，它还须通过 `--observe-local-runtime ...` 或 `--idle-fixture <public-runtime-idle.json>` 接收 public-safe runtime idle evidence。Visible-session 证明说明该路由可见且可中断；runtime-idle 检测器说明这次精确的后续 Turn 没有与人类输入或已在运行的 Codex Turn 赛跑。缺失 runtime-idle evidence 产生精确 blocker，而不是候选命令。

带 runtime-idle evidence 与 `--guard-checked` 时，本地 scheduler 可以选择恰好一个 opt-in 副作用：

- `--execute-candidate --candidate-command-prefix <prefix>`：运行一个已验证的可见候选，其命令以允许的前缀开头。
- `--execute-blocker-writeback`：当 tick 表明证明缺失时，运行精确的 LoopX blocker 写回命令。

Wrapper 只报告是否运行、返回码、超时与选中的种类。它丢弃 stdout/stderr、不读 transcript、不检查 session 文件、不改动隐藏 Codex 状态，也不 spend Goal Harness quota。这使第一个可执行桥足够窄，可以在不把用户 TUI 变成不透明后台 daemon 的情况下测试。

当前可见本地驱动试点：

```bash
loopx codex-cli-visible-local-driver-pilot --project . --goal-id <goal-id> --agent-id <agent-id>
```

该命令仍不运行 Codex。它把第一条一条消息 TUI 启动绑定到后续 scheduler tick，并把返回用户契约显式化：

- 后续 Turn 必须对用户可见；
- 用户必须能中断或接管；
- resume、remote-control 或 same-TUI prompt 候选运行之前需要 public-safe 可见证明；
- 每个后续 tick 都需要 quota guard 与 idle guard；
- 候选执行仍需 `--guard-checked` 加允许的命令前缀；
- blocker 写回仍需 `--guard-checked`；
- 试点从不读 transcripts、session 文件、凭据、stdout 或 stderr，也从不由自身 spend quota。

当前 visible-session 证明 harness：

```bash
loopx codex-cli-visible-session-proof \
  --project . \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --proof-fixture visible-proof.public.json
```

证明夹具必须 public-safe。它记录用户 opt-in、quota guard、idle guard、Turn 可见性、可中断性、私有数据边界与紧凑写回规划的布尔值。通过该证明只意味着未来本地驱动可以在相同 guard 之后尝试该可见 surface；它不意味着 LoopX 可以读 transcripts、读 session 文件、改动隐藏 session 状态或绕过 user gates。

当前 runtime-idle 检测器：

```bash
loopx codex-cli-runtime-idle-detector \
  --project . \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --observe-local-runtime \
  --observed-surface visible_resume_prompt \
  --turn-state idle \
  --probe-human-input-idle \
  --checked-before-prompt \
  --visible-to-user \
  --user-can-interrupt \
  --manual-takeover-available
```

该检测器接受 public-safe 夹具或窄的本地观察 adapter。本地 adapter 可以对粗粒度平台 idle 计数器探测"近期无人类输入"，并要求显式可见 `--turn-state idle`；未知或运行中的 turn state fail closed。它刻意与 visible-session 证明分开：证明说"这条路可以创建可见、可中断的 Turn"；idle 检测器说"这次精确的后续 Turn 没有与人类输入或已在运行的 Codex Turn 赛跑"。在 LoopX 把后续可见 prompt 视为可执行之前，它必须证明没有活跃人类输入、没有运行中 Turn，也没有 transcript/session/stdout/stderr/凭据读取。

对于可复现测试或外部传感器，fixture 路径保持：

```bash
loopx codex-cli-runtime-idle-detector \
  --project . \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --idle-fixture runtime-idle.public.json
```

当前 same-TUI 验收 packet：

```bash
loopx codex-cli-visible-attach-acceptance \
  --project . \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --proof-fixture visible-proof.public.json \
  --idle-fixture runtime-idle.public.json
```

该 packet 是晋升 gate：之后 LoopX 才会把后续 Codex CLI 自动化视为安全的 same-TUI attach。它组合 help-only 探针、visible-session 证明与 runtime-idle 检测器。`remote-control` 或 `resume [PROMPT]` 可以作为可见 spike 候选通过，但除非证明 surface 是 `same_tui_visible_attach` 且 idle 检测器通过，否则不被接受为 same-TUI 自动化。如果证明或 idle evidence 任一缺失，packet 返回精确 blocker，并保持一条消息的设置引导作为主要路径。

第一个 public-safe 证明试点记录在
[Codex CLI 可见 Attach 证明试点](codex-cli-visible-attach-proof-pilot.md)：
当前 `resume` / `remote-control` evidence 有希望，但在可见 same-TUI 证明与 runtime-idle evidence 存在之前仍被阻塞。

可复现捕获路径定义在
[Codex CLI 可见证明捕获协议](codex-cli-visible-proof-capture-protocol.md)。
它把 `resume` / `remote-control` 当作证明目标，保持夹具 public-safe，并在任何后续可见 Turn 被晋升之前记录 blocker-first 停止条件。

### 3. Headless 禁止边界

`codex exec` 对调度式或 CI 式工作仍有用，但它在交互式用户中不是主要产品体验。默认 Codex CLI LoopX 设置-then-`/goal` 路径不暴露 headless 回退，即使作为 opt-in 也不暴露，因此首次运行 packet 不会意外把工作移入隐藏执行。

兼容性边界：

```bash
loopx codex-cli-exec-handoff --project . --goal-id <goal-id>
```

该命令不再打印可运行的 `codex exec` 交接脚本。它报告被禁止的边界，并指回 `codex-cli-bootstrap-message --message-only` 以在可见 TUI 内使用。它不运行 Codex、不读 transcript、不读凭据、不读 session 文件、不改动 session，也不 spend quota。

## Session-Attached Turn 算法

```text
1. 解析仓库、goal_id、注册 agent_id 与当前 Codex session。
2. 运行 `loopx quota should-run --goal-id <goal> --agent-id <agent>`。
3. 如果需要用户动作，只注入或显示具体 user gate。
4. 如果 `workspace_guard` 阻塞写仓库任务，在编辑前把当前 peer 移到合规 worktree。
5. 在当前 agent 认领的推进 todos 与可运行的未认领候选中选择；monitor todos 只是上下文，除非它们产生实质事件。
6. 在证明后向 idle TUI session 注入可见转向 prompt，或保持一条消息的设置引导作为用户路径。
7. 验证后运行 `refresh-state` 与 `quota spend-slot --execute`。
8. 验证失败时写紧凑 blocker，而不是 spend 成功散文。
```

实际 todo 选择仍是 agent 的转向决策。LoopX 投影可运行的候选；它不应过度指定模型的本地计划。

## 安全规则

- 不把原始 Codex transcripts、凭据、私有本地路径、原始日志或生产 artifacts 存进 LoopX 状态。
- 用户在活跃输入或上一个 Turn 仍在运行时，不向 session 注入自动化。
- 不代替用户回答 user gate。
- 不让写仓库 peer 从被 `workspace_guard` 拒绝的 workspace 编辑。
- 优先可见 TUI prompt，而非静默后台变更。
- 把 session 附着失败当作禁用边界决策，而不是丢失 LoopX loop 的理由。

## 实现路线图

1. **Bootstrap prompt**：在 README 与 getting-started 文档中发布简明的 Codex CLI TUI 粘贴消息。
2. **无克隆安装修复**：让首次运行 agent 路径能从 GitHub 归档安装 CLI 与可复用 skills，同时为贡献者保留 clone-plus-canary 设置。
3. **Bootstrap 命令**：添加 LoopX 命令，为当前仓库打印定制的 Codex CLI bootstrap 消息。
4. **一条消息 loop 试点**：发布 `loopx codex-cli-one-message-loop-pilot`，把第一条 TUI 粘贴消息与后续 scheduler/执行器桥绑定进一个 public-safe packet。
5. **Session 探针**：记录当前 Codex CLI 是否暴露稳定 session id、恢复句柄或安全注入原语。当前实现是 `loopx codex-cli-session-probe`；它分离 headless 禁止的执行支持、可见 resume / remote-control spike surface 与真正的 same-open-TUI 可见注入。
6. **可见驱动计划**：用 `loopx codex-cli-visible-driver-plan` 生成 dry-run 计划，让下一个本地驱动知道是尝试可见 attach、跑 resume/remote-control 证明，还是保持一条消息的设置引导作为产品路径。
7. **本地驱动规划器**：发布 `loopx codex-cli-local-driver-plan` 作为 dry-run 命令，组合 quota、visible-driver、TUI bootstrap、headless 禁止边界与 idle-guard 要求。
8. **Visible-session 证明 harness**：在把 resume/remote-control 晋升进任何同 session 自动化路径之前，用 `loopx codex-cli-visible-session-proof` 验证 public-safe 观察。
9. **可见驱动运行 packet**：添加 `loopx codex-cli-visible-driver-run` 作为无执行 packet，决定下一个 Turn 需要可见证明、TUI bootstrap 还是已验证的 visible-session 候选。
10. **本地 scheduler tick**：添加 `loopx codex-cli-local-scheduler-tick` 作为第一个面向执行器的单发 packet。它要么发出外部命令候选，要么发出精确 blocker 写回命令，但自身不运行 Codex、不读 session 文件、也不写 LoopX 状态。可见候选要求 visible-session 证明与 runtime-idle 检测器批准；默认 `/goal` 路径的 headless 回退保持禁用。
11. **本地 scheduler 执行器 wrapper**：添加 `loopx codex-cli-local-scheduler-exec` 作为显式 opt-in 桥，只允许在 guard 确认、可见候选的 runtime-idle 批准与允许的命令前缀之后运行一个 tick 结果。
12. **可见本地驱动试点**：发布 `loopx codex-cli-visible-local-driver-pilot`，把一条消息的 TUI 启动、scheduler 执行器、可见证明、idle guard 与免 transcript 边界绑定进一个 public-safe packet。
13. **Runtime idle 检测器**：在可见后续 Turn 之前用 `loopx codex-cli-runtime-idle-detector` 验证 public-safe idle evidence；该命令现在支持夹具回放与窄的本地观察 adapter，可不读 transcripts、stdout/stderr、凭据或隐藏 session 文件就证明粗略人类输入 idle 加显式可见 turn-state。
14. **可见 attach 验收**：只晋升带通过 runtime-idle evidence 的已验证 `same_tui_visible_attach` 路由；在 `resume [PROMPT]` 与 `remote-control` 证明 same-TUI 语义之前，把它们当作可见 spike 候选。
15. **验证 harness**：添加 public-safe 夹具，证明驱动从不存储原始 transcript 文本，从不在写回前 spend quota。
16. **Claude Code 跟进**：仅在 Codex CLI 路径可信之后移植同一产品契约。

## 成功标准

- 首次用户可以用一条消息在 Codex CLI TUI 开始，无需先读 LoopX 文档就能看到当前 goal、user gate、agent todo 与下一个安全动作。
- 返回用户可以在 LoopX 自动化执行有界 Turn 时保持 TUI 打开，这些 Turn 可见、可中断、可评审。
- 当 session 附着不可用时，回退显式且安全，而不是假装同一个 TUI session 被保留了。
- LoopX 状态保持紧凑、public/private 安全，并与原始 Codex CLI transcript 存储独立。
