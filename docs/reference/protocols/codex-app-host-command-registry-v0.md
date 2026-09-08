# codex_app_host_command_registry_v0

`codex_app_host_command_registry_v0` 定义 Codex App 之类的 host 如何在其成为普通 agent 聊天之前识别 LoopX slash 命令。Host 拥有解析、项目根解析、权限框架与结构化交接包。LoopX CLI 保持事实来源。

本契约位于以下之上：

- [loopx_goal_command_v0](loopx-goal-command-v0.md) 用于项目局部 `/loopx` 状态入口与 `/loopx <goal text>` 启动入口。
- [global_manager_command_v0](global-manager-command-v0.md) 用于只读 `/loopx-global-*` manager 命令。
- [pr_review_command_v0](../../../loopx/capabilities/pr_review_queue/README.md) 用于 `/loopx-pr-review` 评审队列命令。
- [host_integration_surface_v0](host-integration-surface-v0.md) 用于通用 host 生命周期读取与受控写入。

它不是 CLI 的替代、隐藏自动化 runner 或宽泛自然语言路由器。

## 命令注册表

Host registry 应暴露这一最小命令集：

| 命令 | 规范目标 | 默认权限 |
| --- | --- | --- |
| `/loopx` | `loopx bootstrap-command-pack --project .` | 读取/状态优先。 |
| `/loopx <goal text>` | `loopx start-goal --guided --project . --goal-text "<goal text>"` | 显式项目局部启动意图；todo writeback 后必须激活或关卡 host loop。 |
| `/loopx-global-summary` | `global_manager_command_v0` summary 请求 | 只读全局控制面摘要。 |
| `/loopx-global-gates` | `global_manager_command_v0` gates 请求 | 只读 gate 收件箱。 |
| `/loopx-global-todos` | `global_manager_command_v0` todos 请求 | 只读工作队列视图。 |
| `/loopx-global-risks` | `global_manager_command_v0` risks 请求 | 只读风险视图。 |
| `/loopx-pr-review` | `pr_review_command_v0` review 请求 | 必须先运行 PR 评审 CLI；不能作通用聊天摘要回答。 |

迁移期间可以接受遗留 `/loop-global-*` 形式，但 host 必须把包、帮助与用户可见标签规范化为 `/loopx-global-*`。不要添加额外摘要别名；`/loopx-global-summary` 是规范全局进展摘要。

注册表条目示例：

```json
{
  "schema_version": "codex_app_host_command_registry_v0",
  "host_kind": "codex_app",
  "commands": [
    {
      "command": "/loopx",
      "kind": "project_bootstrap_preview",
      "protocol": "loopx_goal_command_v0",
      "cli_baseline": "loopx bootstrap-command-pack --project .",
      "mutation_policy": "read_first"
    },
    {
      "command": "/loopx <goal text>",
      "kind": "project_task_start",
      "protocol": "loopx_goal_command_v0",
      "cli_baseline": "loopx start-goal --guided --project . --goal-text \"<goal text>\"",
      "mutation_policy": "explicit_goal_start"
    },
    {
      "command": "/loopx-global-summary",
      "kind": "global_manager_summary",
      "protocol": "global_manager_command_v0",
      "legacy_aliases": ["/loop-global-summary"],
      "mutation_policy": "read_only"
    },
    {
      "command": "/loopx-pr-review",
      "kind": "repo_pr_review",
      "protocol": "pr_review_command_v0",
      "cli_baseline": "loopx pr-review",
      "mutation_policy": "must_run_cli_first"
    }
  ],
  "unknown_command_policy": "fail_closed_with_slash_help"
}
```

不知道自己精确运行时类型的 host 应先调用 `loopx agent-onboard --list-agent-types`，然后传 `codex-app`、`codex-cli`、`opencode` 或 `claude-code` 之类的规范值。`codex` 这类歧义值无效，因为 Codex App heartbeat 自动化与 Codex CLI `/goal` 的激活流程不同。

## Host 解析规则

Host 应在 agent prompt 看到消息之前解析 LoopX slash 命令：

1. 只在可见用户消息开头匹配精确命令 token。
2. 把遗留 `/loop-global-*` 别名规范化为 `/loopx-global-*`。
3. 把无尾随文本的 `/loopx` 视为 bootstrap/状态预览。
4. 把 `/loopx` 之后的文本视为显式任务文本。在交接包中保留精确用户任务文本，但为 CLI 显示安全引用它。
5. 把 `/loopx-pr-review` 路由到 PR 评审命令契约。不要通过项目 bootstrap 命令发送它。
6. 对未知 `/loopx-*` 命令失效关闭，返回 `loopx slash-commands` 帮助，而不是落入普通聊天。

Skill 级识别可以保持为回退，但首选产品路径是 host 解析。仅 prompt 识别对早期测试有用，但可能被会话历史污染，不应作为长期权威。

## 项目根与 Agent 身份

项目局部命令需要解析后的项目根。Host 可以使用当前工作区、所选文件或显式项目参数，但不得扫描无关家目录或从私有路径猜测。

必需字段：

| 字段 | 规则 |
| --- | --- |
| `project_root` | CLI 执行的绝对本地根；从公开包中省略。 |
| `project_root_label` | 公开安全标签，如仓库名或 `current workspace`。 |
| `goal_id` | 既有运行时状态 id 字段；为 CLI 兼容保留字段名，但向用户呈现为活动状态 id。 |
| `agent_id` | Host 为 agent 行动时的已注册 LoopX agent id。 |
| `thread_id` | 可选稳定不透明 host-thread token，用于解析持久化 thread-to-agent 绑定。 |
| `host_surface` | `chat_box`、`command_palette`、`codex_cli_tui` 或另一紧凑 host 标签。 |

Host 无法解析项目根时，`/loopx` 与 `/loopx <goal text>` 必须产生设置/帮助包，而非状态写入。可用时 global 命令仍可针对共享全局 registry 运行。

## 交接包

解析后，host 交给 agent 或 CLI 一个紧凑包：

```json
{
  "schema_version": "codex_app_host_command_handoff_v0",
  "command": "/loopx",
  "raw_command": "/loopx design an issue-fix workflow",
  "canonical_command": "/loopx <goal text>",
  "task_text": "design an issue-fix workflow",
  "host_surface": "chat_box",
  "project_root_label": "current workspace",
  "goal_id": "loopx-meta",
  "agent_id": "codex-product-capability",
  "thread_id": "opaque-host-thread-123",
  "protocol": "loopx_goal_command_v0",
  "cli_preview": "loopx start-goal --guided --project . --goal-text \"<goal text>\"",
  "authority": {
    "read_allowed": true,
    "project_local_write_allowed": true,
    "global_control_write_allowed": false,
    "production_action_allowed": false
  },
  "next_step": "run_guided_start_preview_then_plan_before_todo_write"
}
```

Codex App CLI 在省略 `--thread-id` 时读取 `CODEX_THREAD_ID`，包括 `codex-app-ssh` 远程会话。存在已注册 agent 时，无绑定的稳定线程 ID 返回要求选择一个既有 lane 的身份 gate；只有无已注册 lane 的 goal 或显式 `--new-peer` 才默认全新注册。选择既有 lane 是显式接管选择。选定的新身份或既有身份必须以 `loopx bind-agent-thread --execute` 持久化，且其来源/全局回读必须在 Todo writeback 前验证。同一 `(host_surface, goal_id, thread_id)` 中的后续 `/loopx` 调用复用该 agent ID，并把它贯穿 start、heartbeat、quota、refresh-state 与 Todo 命令。Host 无法提供稳定线程 ID 时，调用方必须继续使用显式 `--agent-id` 或带 `--new-peer` 的显式新会话意图；身份 gate 保持失效关闭。
线程 ID 只是不透明公开安全 token；原始 transcript、凭据与本地路径绝不持久化。

### 深链任务会合

LoopX 接受从 Codex App 复制的任务链接。[Codex App 命令参考](https://learn.chatgpt.com/docs/reference/commands) 把 `codex://threads/<thread-id>` 记录为打开既有本地任务的规范形式。
LoopX 把该链接视为用于评审、交接与协调的 host-session 定位器，而非第二 agent 身份或权限授予。接收的 Codex 任务可以在不改变的条件下确认目标的既有项目局部 LoopX 绑定：

```bash
loopx resolve-agent-thread \
  --thread-link 'codex://threads/<thread-id>'
```

深链不编码任务的执行界面。无显式 `--host-surface` 时，LoopX 只搜索 Codex host 家族（`codex-app`、`codex-app-ssh` 与 `codex-cli-tui`）并报告匹配的界面。调用方可以传其中任一界面以缩小查找。`bound` 结果指名恰好一个 `goal_id` 与 `agent_id`。`missing` 结果只表示链接解析成功；它不授权接管，也不证明目标任务连接到本 LoopX 项目。`ambiguous` 与无效结果失效关闭。命令不存储任何内容，返回解析的定位器且 `authority=locator_only`。发送方仍必须通过正常引导启动流程注册并绑定自己的 agent lane，且两个任务必须显式陈述各自职责。深链不共享聊天上下文、权限、凭据、工作区访问、lease 或写 scope。并发写者仍需要独立 worktree 或等价隔离。确认唯一绑定后，暴露只读任务检查的 host 可以使用解析的 `thread_id` 检查或引用该任务。工具可用性与访问另行检查；检查不可用时，发送方必须显式转发所需上下文。

中文：在目标 Codex 任务菜单中选择"复制 -> 复制深度链接"，把 `codex://threads/<thread-id>` 连同双方分工发给另一个任务。接收方先运行上面的只读命令；只有返回 `bound` 且 `goal_id`、`agent_id` 与预期一致时，才把它视为已确认的 LoopX 会话绑定。`missing` 只表示链接格式有效但尚无本项目绑定。深度链接只负责定位，不同步权限、目录、对话上下文、lease 或写入范围；并行修改代码仍需独立 worktree。

同一项目上下文共享时，解析定位器还返回一个 provider-neutral `context_scope_ref`。显式启用的 Decision Context extension 可以把这个 scope 用作一次性 `recall-context` 参数做有界咨询召回，而不修改其持久化 profile。捆绑的 `loopx-obelisk` 包是可选 provider 之一；另一个 harness 适配器可以实现同一协议。Provider 输出保持瞬态且 fail-open。权威对齐优先于聊天，持久化结论仍归 Goal Todos、证据事件、已注册物料或受治理修订所有。

包可以渲染进 agent prompt、传给工具调用或直接用于运行 CLI。它不得在用户可见输出中包含原始 transcript、凭据、私有文档正文或本地绝对路径。

`loopx start-goal --guided` 默认为紧凑 command-pack 投影。热路径保留有序事务、规划契约、安全契约、goal 与 agent 身份、动作命令、host 激活契约与一个可执行冷路径命令。它不第二次嵌套完整 bootstrap 消息、slash-command 发现目录或重复的连接与下一步诊断。真正需要那些更低层字段的消费者可以重跑广告的命令或传 `--include-command-pack-detail`。两种模式在紧凑默认被提升前都必须产生相同 host-action 投影。

`start-goal --project <path>` 保留该精确项目路由。特别是，新风 linked worktree 不得静默继承共享其 Git common 目录的另一个 worktree 注册的 goal。当检查或修复既有连接时，更低层的 `bootstrap-command-pack` 仍允许把 linked worktree 解析到其规范注册来源。

`start-goal` 不在 Codex App 自动化、SSH 上的 Codex App、Codex CLI TUI 或 OpenCode 之间猜测。调用方应为精确当前 host 传 `--host-surface codex-app`、`codex-app-ssh`、`codex-cli-tui` 或 `opencode`。`codex-app-ssh` 意为桌面应用附着到远程工作区且无法暴露其自动化工具，因此可见 `/goal` 拥有继续。省略该选项时，命令返回带精确重跑命令的只读 `host_surface_selection` gate；它不得连接项目、写入 todos、激活 host 或花费配额。

## 权限边界

Host 命令解析不授予新 LoopX 权限。它只是把可见用户意图转成既有 CLI 生命周期：

- `/loopx` 可以读取状态与预览命令包。它在需要确认的写入前停止。
- `/loopx <goal text>` 是启动项目局部工作的显式意图：先规划、写入有序 todos、刷新状态、在缺失/过期时激活正确 host loop、运行 `quota should-run`，且只在 guard 允许时执行。
- Host loop 激活是运行时特定的：Codex App 使用 heartbeat 自动化，SSH 上的 Codex App 与 Codex CLI 使用可见 `/goal <task_body>`，Claude Code 使用原生 `/loop`，自定义 agent 必须通过 `loopx agent-onboard` 声明其 loop 驱动器。
- `/loopx-global-*` 命令只读，不得批准 gates、添加 todos、花费配额、合并 PR、外部发布或暂停/恢复 loops。
- `/loopx-pr-review` 必须先运行 PR 评审 CLI，然后按 `pr_review_command_v0` 响应契约评审 PR。它不是项目 bootstrap 命令，除了评审契约显式记录公开安全后续动作外不应修改项目状态。
- 破坏性 git、凭据、私有物料读取、生产动作与外部发布仍需显式用户/controller 批准。

## CLI 回退

每个 host 命令必须暴露确定性 CLI 回退：

```bash
loopx slash-commands
loopx slash-commands --install
loopx agent-onboard --list-agent-types
loopx agent-onboard --agent-type codex-cli --project .
loopx agent-onboard --agent-type codex-app-ssh --project .
loopx bootstrap-command-pack --project .
loopx start-goal --guided --project . --goal-text "<goal text>" --host-surface codex-cli-tui
loopx bootstrap-command-pack --project . --goal-text "<goal text>"
loopx pr-review
loopx global-summary
loopx --format json --registry "$HOME/.codex/loopx/registry.global.json" quota should-run --goal-id <goal-id> --agent-id <agent-id>
```

Host 命令解析不可用时，用户或 skill 回退仍可运行这些命令并保留相同 LoopX 状态机。Agent/手动任务启动优先 `loopx start-goal --guided`；实现或调试更低层 host 交接包时使用 `loopx bootstrap-command-pack --goal-text`。

## 用户层注册回退

在每个 host 暴露原生命令注册表之前，LoopX 把 slash-command 门面安装到当前 host 已支持的用户级发现位置：

- `~/.codex/skills/loopx*/SKILL.md` 用于通过 `$loopx` 或 `/skills` 显式调用 Codex 命令门面；主 `LoopX` 命令门面与 `LoopX Project` 工作流 skill 保持区分；
- `~/.claude/skills/loopx*/SKILL.md` 用于 Claude Code 基于 skill 的 slash 命令。

该回退不取代 host 解析。它现在给用户一个显式 Codex skill 入口点，同时保留上述相同 CLI 基线与权限边界。Codex 命令门面仅显式；更丰富的工作流 skill 保持可供隐式调用。安装器覆盖 LoopX 管理文件与已知遗留 LoopX 生成的命令文件，但跳过无 LoopX 管理标记或遗留签名的同名用户文件。

## 验收检查

一个 host 命令注册表实现在以下条件下可接受：

1. `/loopx` 与 `/loopx <goal text>` 路由到 `loopx_goal_command_v0`。
2. `/loopx-global-summary`、`/loopx-global-gates`、`/loopx-global-todos` 与 `/loopx-global-risks` 路由到 `global_manager_command_v0`。
3. `/loopx-pr-review` 路由到 `pr_review_command_v0` 且先运行 CLI。
4. 遗留 `/loop-global-*` 输入规范化为 `/loopx-global-*`。
5. 未知 `/loopx-*` 命令以 `loopx slash-commands` 帮助失效关闭。
6. 交接包包含项目根标签、可选活动状态 id、agent id、协议、权限与 CLI 回退，而不含公开本地绝对路径。
7. Host 解析被视为首选路径，而 skill 级识别只作为兼容回退。
