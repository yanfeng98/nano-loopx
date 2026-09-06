# multi_agent_visible_launcher_v0
> [English](multi-agent-visible-launcher-v0.md)

`multi_agent_visible_launcher_v0` 是为一个共享 goal 启动若干可见本地 agent pane 的通用 LoopX 契约。它是 auto-research 等领域演示之下的可复用层：LoopX 拥有 goal 界面、lane 身份、quota/frontier/bootstrap guard、可见 host 控件与公开验收；领域 capability 只拥有角色语义与证据 writeback。

本契约有意位于两个既有界面之间：

- `local_agent_launch_plan_v1` 预览可启动什么，且只保持 `mode=dry_run`。
- 领域 capability（如 auto-research）提供角色 profile、前沿命令与证据包。

可见启动器可以规划或启动 panes，但不得成为 leader agent、隐藏 scheduler、提升权限或第二事实来源。

启动器还遵循 [multi_agent_three_layer_minimality_contract_v0](multi-agent-three-layer-minimality-v0.md)：面向用户的 recipe 与领域 preset 都保持薄，而通用内核拥有 runner/TUI/tick/todo/evidence/status 机制。

## 内核模块

可复用控制面内核位于 `demo/multi_agent/`。领域 capability 应依赖该包提供：

- `tui_multi_agent_runner_contract_v0`；
- `generic_multi_agent_role_profile_v0`；
- `multi_agent_three_layer_minimality_contract_v0`；
- pane 级 A2A prompt 规则；
- 仅工件机器 JSON 策略；
- 启动预览的紧凑人类状态；
- 作用域 LoopX 包装器、pane 级 A2A tick 与 Codex TUI exec 的运行时脚本。

`demo/visible_multi_agent_launcher.py` 中的 host 启动器只拥有 tmux 进程执行与 Codex TUI 验收。Auto-research、benchmark 演示与未来自定义团队不应重复 runner schema、角色 profile 规范化、attach/stop 语义、pane 级 tick 脚本或机器 JSON 包装器策略。

## 面向用户的 Spec

大多数调用方不应手写 `multi_agent_visible_launcher_v0` 包。他们应提供一个小型 `generic_multi_agent_launch_spec_v0` 角色 spec，并让 `loopx multi-agent launch --spec <file>` 把它展开成可见启动器包。

```json
{
  "schema_version": "generic_multi_agent_launch_spec_v0",
  "goal_id": "loopx-meta",
  "session_name": "loopx-custom-team",
  "default_reasoning_effort": "high",
  "roles": [
    {
      "lane_id": "planner",
      "agent_id": "codex-main-control",
      "role_id": "planner",
      "scope": "Plan the next bounded step from the shared goal surface.",
      "skill": {
        "name": "loopx-planner-worker",
        "source": "worker/SKILL.md"
      },
      "handoff_hints": [
        "Create or update a LoopX todo for critic when a plan needs review."
      ]
    },
    {
      "lane_id": "critic",
      "agent_id": "codex-side-bypass",
      "role_id": "critic",
      "scope": "Review the bounded step against the same todo and quota projection."
    }
  ]
}
```

Spec 有意保持小：

- `goal_id` 选择共享 LoopX 状态界面；
- 每个角色指名 `agent_id`、人类角色与 scope；
- `skill.source` 相对 spec 文件解析，并物化为该角色的 worker 局部 skill；
- `handoff_hints` 描述角色应如何使用 LoopX todos/证据传递工作，而不创建中央工作流引擎；
- `--execute` 启动可见 Codex TUI panes，而默认模式只预览包。

这使产品集成聚焦于角色设计与状态中介交接。生成的启动器包仍强制仅工件机器 JSON、交互式 Codex TUI 窗口、attach/stop 控件与公开边界字段。

## 所有权拆分

| 界面 | 拥有 | 不拥有 |
| --- | --- | --- |
| LoopX 控制面 | goal id、已注册 agent、todo claims、quota、gates、run 历史与公开/私有边界。 | 领域特定的研究、benchmark 或产品语义。 |
| 多 agent 可见启动器 | pane 布局、环境投影、可见启动命令、attach/stop/retry 控件、验收检查。 | Todo 真相、提升决策、隐藏会话注入或写权限。 |
| 领域 capability | lane 角色、前沿命令、角色 profile schema、领域工件/证据 writeback。 | 通用 host 进程生命周期、全局 quota 或跨领域启动器策略。 |
| Host shell 或 App | 显式本地执行后的实际 tmux/terminal/window 进程控制。 | 绕过 LoopX guard 或对用户隐藏工作的权限。 |

启动器是 host 便利界面。每个 pane 保持普通 LoopX agent lane，必须读取相同 goal 状态并通过自己的 guard。

## 包形状

```json
{
  "schema_version": "multi_agent_visible_launcher_v0",
  "mode": "dry_run | execute",
  "goal_id": "loopx-meta",
  "session_name": "loopx-visible-goal",
  "reasoning_contract": {
    "default_reasoning_effort": "high",
    "codex_cli_config_key": "model_reasoning_effort"
  },
  "shared_goal_surface": {
    "shared_goal_id": "loopx-meta",
    "shared_state_route": "LOOPX_REGISTRY_and_LOOPX_RUNTIME_ROOT",
    "shared_frontier": true,
    "lane_identity_source": "role_profile_plus_agent_scoped_quota",
    "all_lane_workspace_isolation": false,
    "mutation_isolation_policy": "only mutating attempts require a claimed worktree or equivalent execution boundary"
  },
  "interactive_tui_contract": {
    "schema_version": "multi_agent_visible_interactive_tui_contract_v0",
    "human_pane": [
      "codex_cli_tui",
      "role_prompt_inside_codex",
      "normal_user_typing",
      "normal_codex_tool_output",
      "takeover_controls"
    ],
    "machine_artifacts": [
      "quota.public.json",
      "frontier.public.json",
      "bootstrap-prompt.public.txt",
      "role_local_public_artifacts"
    ],
    "machine_json_policy": "file_or_explicit_machine_channel_only",
    "visible_json_policy": "not_printed_before_tui",
    "codex_surface": "interactive_cli_tui"
  },
  "lanes": [],
  "commands": {
    "start_script": [],
    "attach": "tmux attach -t loopx-visible-goal",
    "stop": "tmux kill-session -t loopx-visible-goal",
    "retry": "rerun the same packet after quota/frontier refresh"
  },
  "acceptance": {},
  "boundary": {}
}
```

必需顶层字段：

- `schema_version`：恰好为 `multi_agent_visible_launcher_v0`；
- `mode`：仅检查包为 `dry_run`，或本地 host 显式启动 panes 后为 `execute`；
- `goal_id` 与 `session_name`；
- `reasoning_contract`；
- `shared_goal_surface`；
- `interactive_tui_contract`；
- `lanes[]`；
- `commands.attach`、`commands.stop` 与 `commands.retry`；
- `acceptance`；
- `boundary`。

## 共享 Goal 界面

可见 lanes 共享目标 **goal 界面**，而不一定同一文件变更区。共享界面是：

- `LOOPX_REGISTRY` 选择的 registry；
- `LOOPX_RUNTIME_ROOT` 选择的运行时根；
- `goal_id`；
- agent 作用域 `quota should-run`；
- 该 goal 的 todo 投影、前沿投影与 run 历史；
- 公开安全证据与 rollout 事件投影。

`all_lane_workspace_isolation=false` 是正常 LoopX 多 agent 形状：agent 在一个 goal 界面上协作。隔离只应用于变更文件的 lane 或尝试，通常通过独立 git worktree、临时目录或等价执行边界。启动器必须把该策略显式化，而不是静默把每个 lane 移入无关状态。可见 Codex TUI pane 不得默认进入生成的演示局部 git worktree 或控制面仓库。默认它们应在调用方选择的工作区中启动，或在显式用户自有临时工作区中启动，使用户看到 agent 角色 TUI，而不是生成的 workspace trust 提示。

## Lane 形状

每个 lane 在 agent 启动前足够小以便检查：

```json
{
  "lane_id": "evidence-runner",
  "agent_id": "codex-side-bypass",
  "role_id": "evidence_runner",
  "responsibility": "Run one bounded evidence attempt.",
  "role_profile": {
    "schema_version": "domain_role_profile_v0"
  },
  "quota_guard": "loopx ... quota should-run --goal-id ... --agent-id ...",
  "frontier": "loopx ... <domain> frontier --goal-id ... --agent-id ...",
  "bootstrap_message": "loopx codex-cli-bootstrap-message ...",
  "visible_launch_command": "...",
  "reasoning_effort": "high",
  "lane_timeline": []
}
```

必需 lane 字段：

- `lane_id`、`agent_id`、`role_id` 与 `responsibility`；
- `role_profile` 或 `role_profile_ref`；
- `quota_guard`；
- `frontier`；
- `bootstrap_message`；
- `visible_launch_command` 或 host 等价命令引用；
- `reasoning_effort`；
- `lane_timeline`。

Pane 标题是装饰性的。角色 profile 加 agent 作用域 quota/frontier 包才是 lane 身份权威。

## 启动顺序

每个可见 lane 遵循相同通用启动顺序：

1. 把角色 profile、作用域 LoopX 包装器与 bootstrap prompt 准备为本地工件，而不打印原始 JSON 或 shell 标记流。
2. 使用 `codex -c model_reasoning_effort=<effort> -C "$LOOPX_PROJECT" "$PROMPT"` 为每个角色窗口启动一个全新交互式 Codex CLI TUI。
3. 让 Codex 角色通过 TUI 内的 pane 级 LoopX 包装器读取 quota/frontier/todo 状态。
4. 若 `interaction_contract.user_channel.action_required=true`、投递被禁止、quota 为 false、前沿矛盾、或角色会绕过 LoopX todo/evidence writeback，则在该 Codex 角色内停止。
5. 保持 pane 交互，使用户能像正常 Codex CLI 会话一样手动输入、中断、关闭或重试。

启动器不得向既有隐藏会话注入 prompt、不得把原始控制面 JSON 打印为首屏，也不得在用户 gate 投影后继续 lane。

## 交互式 TUI 契约

每个可见 pane 的首屏是 Codex CLI TUI 本身。用户应感觉他们打开了几个普通 Codex agent（每角色一个），且可以输入任意一个。原始 quota、frontier、角色 profile、bootstrap prompt 与机器 JSON 属于公开安全工件或显式机器 channel，而非初始 tmux 视口。

必需运行时形状：

- 每角色一个 tmux 窗口；
- 默认无额外 frontier/status JSON 窗口；
- 每个角色窗口执行交互式 Codex CLI，而非 `codex exec`；
- TUI 前不出现预 Codex 字符流、标记 transcript、原始 JSON 转储或复制的角色 profile；
- 首个可见屏幕不应是生成的演示局部 worktree trust prompt；
- 角色 prompt 指示 Codex 使用 pane 级 LoopX 包装器做 quota/frontier/todo/evidence 工作；
- 用户可以通过普通 Codex CLI 控件与每个角色交互。

Codex 角色运行命令时，TUI 之后可以显示人类可读 LoopX 摘要。它不应把原始 JSON、凭据、私有日志、原始 transcript 或本地绝对工件路径转储进可见 pane。

## Host 控件

包必须暴露：

- `attach`：用户如何观察或接管整个会话；
- `stop`：用户如何杀掉整个会话；
- 使用正常终端控件的每 pane 中断路径；
- `retry`：安全重试形状，必须先重算 quota/frontier/bootstrap，而非重放过期隐藏状态；
- 每个 pane 被创建为交互式 Codex CLI TUI 角色且仍可 attach 或检查的可见验收证明。

Host 命令是公开安全命令形状。它们不得在提交的文档或 fixture 中包含凭据、认证头、原始 transcript 路径、私有文档 id 或本地绝对路径。

## 边界

必需边界字段：

```json
{
  "starts_visible_processes": false,
  "runs_agent_processes": false,
  "writes_loopx_state": false,
  "spends_loopx_quota": false,
  "reads_raw_transcripts": false,
  "reads_session_files": false,
  "reads_credentials": false,
  "hidden_prompt_injection": false,
  "shared_goal_surface": true,
  "all_lane_workspace_isolation": false,
  "public_safe_redaction": true
}
```

对于 `mode=dry_run`，进程与写入字段必须保持 false。对于 `mode=execute`，只有 host 真实启动可见 panes 时 `starts_visible_processes` 与 `runs_agent_processes` 才可变为 true；LoopX 状态写入与配额花费仍在验证 writeback 后通过普通 agent lane 发生，而非通过启动器包本身。

## 领域适配器职责

使用本契约的领域 capability 提供：

- 角色 profile schema 与角色特定允许动作；
- 前沿命令与阻塞原因形状；
- 领域证据或工件 writeback 命令；
- 领域特定验收标准；
- 需要时的公开安全演示 fixture 或确定性正种子。

领域 capability 不应拥有通用 attach/stop/retry、共享 goal 界面、高推理启动标志或 pane 存活检查。

## 验收检查

一个公开 fixture 或实现只有满足以下条件才符合本契约：

1. 包或协议指名 `multi_agent_visible_launcher_v0`；
2. 它区分 `local_agent_launch_plan_v1` 预览与可见启动；
3. 它说明启动器不是 leader agent、scheduler、提升权限或第二事实来源；
4. 它通过 registry、运行时根、goal id、agent 作用域 quota、todo/frontier 投影、run 历史与证据暴露共享 goal 界面；
5. 它要求每 lane 角色身份、quota guard、frontier、bootstrap 消息、高推理、lane 时间线与可见启动命令；
6. 它要求交互式 Codex CLI TUI 角色窗口具备 attach、stop、retry、pane 中断与可见验收证明；
7. 它有交互式 TUI 契约，把原始机器 JSON 保留在工件或显式机器 channel 中，而非在 Codex 启动前打印；
8. dry-run 模式不启动进程、不运行 agent、不写 LoopX 状态、不花费配额；
9. execute 模式仍只在验证后通过普通 LoopX writeback 写入状态与花费配额；
10. 它把工作区隔离保持在变更尝试的作用域，而非拆分共享 goal 界面；并且
11. 公开文档与 fixture 不包含原始 transcript、凭据、私有链接、内部项目名或本地绝对路径。
