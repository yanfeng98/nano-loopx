# 新手命令路径


LoopX 给人的第一印象应该是"一条产品路径"，而不是"一个 CLI 目录"。对首次用户，
默认界面是：

1. 安装或修复 CLI。
2. 让 Agent 连接当前项目。
3. 使用宿主的 LoopX 命令入口开始有用工作。

完整命令集仍对操作者与贡献者开放，但它不应成为新手首先要理解的东西。

## 需要记住的两条命令

| 需要 | 使用 | 预期结果 |
| --- | --- | --- |
| 检查此项目是否已连接、有什么在等待。 | LoopX status 入口 | Agent 读取 LoopX 状态、gate、todo 与下一个安全动作，而不启动新的交付路径。 |
| 开始具体的长程工作。 | LoopX task 入口加 `<task text>` | Agent 先规划、写入有序 todo，然后一次推进一个有界、已验证的切片。 |

示例：

```text
$loopx fix the open PR review feedback and keep the patch reviewable
$loopx split this refactor into PR-sized slices and stop at unsafe gates
```

在当前的 Codex 界面中，用 `$loopx` 调用显式 `loopx` skill，或从 `/skills`
选择它。在暴露原生自定义 slash command 的宿主上，同样的任务文本可以写成
`/loopx <task text>`。

## 选择 Loop 驱动器

LoopX 保留客观状态、gate、todo、quota 与证据。它不替换运行下一 Agent Turn 的
App 或 CLI。选择与你已使用界面匹配的驱动器：

| 界面 | 从这里开始 | 靠什么持续推进 |
| --- | --- | --- |
| Codex App | 项目线程中的 `$loopx <task text>` 或 `/skills` -> `loopx` | App heartbeat 自动化。让 Agent 安装或刷新生成的 LoopX heartbeat body；从 bootstrap 节奏开始，然后跟随 `quota should-run.scheduler_hint`。 |
| Codex CLI | 从项目根运行 `codex`，然后粘贴 `loopx codex-cli-bootstrap-message --project .` 的输出 | 当前已验证的 Codex CLI 构建不加载用户安装的 `/loopx` 或 `/prompts:loopx` 命令。保持 executor 可见，然后设置生成的 `/goal <thin task_body>`。 |
| Claude Code | 安装 LoopX，然后 `/loopx <task text>` | 安装器注册轻量 slash-command skills。仅当 Claude Code 原生 `/loop` 应受 LoopX `should_run` 门控时，才启用 opt-in adapter。 |
| OpenCode | 安装 OpenCode 界面，然后 `/loopx <task text>` | 桥接层写入命令、plugin、runtime 与固定依赖。写入 todos 后调用 `loopx_goal_activate` 绑定 quota 门控的 goal loop。 |
| 其他 Agent 或 shell | `loopx start-goal --guided --project . --goal-text "<task text>" --host-surface <exact-host>` | 引导包预览 Agent 应执行的同一事务：检查或连接状态、规划 todos、刷新状态、激活宿主 loop、运行 quota，并在需要时 ack scheduler hint。如果界面没有 runner hook，LoopX 可以跟踪状态，但由用户手动驱动。 |

如果你已经拥有 Agent runner 或工作流主管，请改用
[把 LoopX 嵌入你的 Agent Runner](custom-agent-runner-integration.md)，而不是从
完整 CLI 目录重建生命周期。

## 一条 CLI 快速开始

当 Agent 需要手动 shell 路径，或你要在没有 Agent 驱动第一步的全新终端里配置时：

```bash
python3 -m pip install --upgrade loopx
loopx workflow-skills --install
loopx doctor
loopx slash-commands --install
loopx bootstrap-command-pack --project .
loopx start-goal --guided --project . --goal-text "<your first long-running task>" \
  --host-surface codex-cli-tui
```

命令包检查面向宿主的恢复包。引导启动包是第一条任务路径：把生成的事务粘贴进
Codex、Claude Code 或其他能从项目根运行 shell 命令的兼容 Agent。当真实宿主是
`codex-app`、`codex-cli-tui`、`claude-code` 或 `shell` 时，
使用对应值。宿主
不明确时，省略该标志一次并跟随返回的只读选择 gate；该预览不写项目状态。

## 多项目管理器命令

别把它们放进前两条命令里，但当一个用户有多个 LoopX 项目或 Agent lane 时展示：

| 需要 | 使用 |
| --- | --- |
| 查看跨项目进度摘要。 | `/loopx-global-summary` |
| 只看用户或 owner gate。 | `/loopx-global-gates` |
| 查看可运行的项目-Agent 工作。 | `/loopx-global-todos` |
| 查看风险与被阻塞 lane。 | `/loopx-global-risks` |

这些是管理器视图。它们应跨项目汇总并路由工作；它们不应取代项目本地的 LoopX
task 入口作为在一个仓库内开始有用工作的方式。

## 何时使用更多命令

| 如果你想…… | 先用这个界面 | 然后才考虑…… |
| --- | --- | --- |
| 开始项目本地工作 | 带 `<task text>` 的 LoopX task 入口 | 手动引导 Agent 时的 `loopx start-goal --guided --goal-text ...`；仅在实现或调试宿主交接时用 `loopx bootstrap-command-pack --goal-text ...`。 |
| 一次理解多个 LoopX 项目 | `/loopx-global-summary` | 需要聚焦管理器视图时的 `/loopx-global-gates`、`/loopx-global-todos` 或 `/loopx-global-risks`。 |
| 理解工作为何暂停 | `/loopx` | Agent 需要更深的证据包时的 `loopx diagnose --goal-id <goal-id>`。 |
| 评审交接或 gate | Agent 的 LoopX 状态摘要 | 获取可复制操作者包的 `loopx review-packet --goal-id <goal-id>`。 |
| 运维循环工作 | Codex App heartbeat 或可见的 Codex CLI 任务体 | 安装或修复 loop 时的 `loopx heartbeat-prompt --thin --goal-id <goal-id>`。 |
| 调试控制面 | 具体的错误或受限 todo | `loopx status`、`loopx history`、`loopx quota should-run` 或 `loopx check`。 |

## 参考边界

命令目录是参考材料。保持它有用，但让它位于产品路径之下：

- 新用户不需要先扫完每条命令再试用 LoopX。
- 公开示例应优先使用宿主的 LoopX task 入口，除非它们在教安装、调试或维护者流程。
- 贡献者仍可使用
  [开始使用](getting-started.md#command-reference) 中的完整命令参考。
- 已安装用户需要分组操作者参考时，可运行 `man loopx` 或 `loopx commands`，而不必
  走首次运行路径。
