# loopx_goal_command_v0

`loopx_goal_command_v0` 定义项目局部的 `/loopx` slash 命令：

| 命令 | 意图 | 变更策略 |
| --- | --- | --- |
| `/loopx` | 检查或预览项目连接。 | 读取优先；bootstrap/connect 写入前询问。 |
| `/loopx <goal text>` | 启动具体 goal、规划排序 todos、激活 host loop 并进入 LoopX 自动化流程。 | 显式调用可以写入项目局部 LoopX 状态与 todos，然后必须激活或关卡 host loop。 |

该命令刻意与 `/loopx-global-*` 分离：global 命令总结并管理跨项目的可见控制面状态，而 `/loopx <goal text>` 启动或继续一个项目 goal。

## Goal 启动流程

用户在 `/loopx` 后提供文本时，host 应：

1. 把文本视为启动此项目 goal 的显式用户意图。
2. 若不存在匹配 registry goal，则连接项目局部 LoopX 状态。
3. 在写入 todos 之前先规划。
4. 按精确计划顺序写入规划的 todos。
5. 运行 `refresh-state`。
6. 若 host loop 缺失、未知或过期，则激活它：
   - `codex-app`：根据生成的 `heartbeat-prompt` 任务正文创建或更新 Codex App heartbeat 自动化。
   - `codex-cli`：把可见 Codex CLI TUI 设为 `/goal <task_body>`。
   - `ark-managed-agent`：把生成的 `<task_body>` 作为原生 Goal 提交一次。Goal 运行时拥有继续与终态评估；不要用 LoopX Turn 包装其内部迭代，也不要在相位边界重提。
   - `claude-code`：用 `/loopx <task>` 武装 LoopX，然后运行原生 `/loop`。
   - `opencode`：从已安装的 LoopX OpenCode bridge 调用 `loopx_goal_activate`；bridge 通过 `quota should-run` 关卡空闲继续与定时器唤醒，且只在已验证终态 no-follow-up 时完成。
   - `pi`：从已安装的 LoopX Pi extension 调用 `loopx_goal_activate`；extension 通过 `quota should-run` 关卡已结算继续与定时器唤醒，且只在已验证终态 no-follow-up 时停止。
   - `manual` / `other-agent`：接入 `loopx agent-onboard` 描述的外部 loop 驱动器。
7. 若 host 不能修改该界面，报告精确可粘贴 gate，而不是声称自主设置完成。
8. 运行 `quota should-run`，然后只在配额契约允许时启动首个有界段落。

新 host 应使用以下命令发现精确 agent 类型：

```bash
loopx agent-onboard --list-agent-types
```

TraeX CLI 接入已移除：`traex-cli` 及其别名不再是可选 host，
`heartbeat-prompt --visible-goal-host` 参数与对应 Python 参数、专用渲染 API
也已撤除。旧调用会明确失败，不自动转成其他 Agent；既有 registry 与历史证据
不会被迁移或删除。需要继续工作时，显式选择上面列出的受支持宿主。

`codex` 这类歧义值必须失效关闭，因为 Codex App 自动化与 Codex CLI 使用不同 host-loop 激活路径。

Codex CLI 与 Ark Managed Agent 构成一个原生 Goal host 家族。它们共享稳定 `loopx_goal_prompt_v0` 正文、4,000 字符 host 预算、每次继续的 `quota should-run` 包、持久化 LoopX writeback 与非 heartbeat 配额记账。它们的继续 owner 仍是显式 host 契约：

| 原生 Goal host | 激活 | 继续与阻塞状态 owner |
| --- | --- | --- |
| Codex CLI | 设置可见 `/goal <task_body>`。 | 原生 Codex Goal；在未变化限制后可以调用 `update_goal(status=blocked)`，只有用户 `/goal resume` 重新激活它。 |
| Ark Managed Agent | 一次性提交同一 prompt 家族。 | Managed Agent Goal 运行时及其持久化 journal；LoopX 不得模拟 `/goal resume` 或盲目重提。 |

该家族是 prompt、quota 与状态边界抽象，不是声称所有 host 具有相同传输或生命周期 API。

可见 Goal 激活捕获任务正文生成时观察到的能力，但该初始列表对长程会话并非穷尽。因此动态能力指引属于 CLI 决策包，而非稳定 Goal prompt。当 `quota should-run` 发现可修复的运行时能力缺口时，`interaction_contract.cli_channel` 返回类型化 `runtime_capability_reentry_v0` 包。每个候选在其实时调用点成功观察后，其精确重新进入命令才可声明 `--available-capability`。

已验证的重新进入调用成为该决策的能力信封。LoopX 随后把相同的会话作用域能力标志投影进后续 refresh、spend、monitor 与 quota 命令。它绝不把那些观察持久化为常驻授予，而凭据等 owner 持有能力保持用户 gate。本契约由本地可见 Goal host 与 Ark Managed Agent Goal 模式共享，无需重新生成 prompt。

Agent 身份遵循同一失效关闭规则。`agent-onboard` 保留其全新注册路径，而 Codex App `start-goal --guided` 在省略 `--thread-id` 时消费环境中的 `CODEX_THREAD_ID`，且可用时必须复用匹配的稳定不透明线程绑定。当存在已注册 lane 时，带绑定的稳定线程 ID 不再当作全新 onboarding：`start-goal` 返回要求选择一个既有 lane 的身份 gate，而只有无已注册 lane 的 goal 或显式 `--new-peer` 才默认全新注册。既有身份是接管选择，绝非隐式自动选择；选择其中一个需要针对该精确 agent 的显式用户意图。存在已注册 lane 时，缺失线程 ID 遵循同一 gate，否则失效关闭，要求显式 `--agent-id`、lane 选择或带 `--new-peer` 的新会话意图。LoopX 以 `bind-agent-thread --execute` 持久化 `(host_surface, goal_id, thread_id) -> agent_id`；后续 `/loopx` 调用在 `start-goal`、heartbeat、quota、refresh-state 与 Todo 命令间复用该绑定身份。预览是咨询性的；todo writeback 需要验证注册与绑定回读。无稳定线程 id 时，调用方必须继续传显式已注册 `--agent-id` 或显式 `--new-peer`。任何受限路径都不得广告无作用域 heartbeat 或 quota 命令。

命令包预览仍只读。它描述命令与契约；slash 调用才授权项目局部状态写入。新用户界面还应显示命令包中的紧凑 slash 命令目录，或等价 `loopx slash-commands` CLI 帮助，使用户能发现 `/loopx`、`/loopx <goal text>` 与 `/loopx-global-*` 只读 manager 命令。

## 规划契约

规划器必须在任何 `todo add` 之前创建有序规划检查点，但形状取决于 goal 已有多清晰：

- `open_ended_product_direction`：宽泛或模糊的产品方向应产出 2-5 个公开安全 todo 项，使用户在 LoopX 开始工作前看到主要 lane、风险与执行顺序。
- `clear_bounded_problem`：有明确成功条件的具体任务应使用规划器规模的有序 todo 计划。模型应产出足够多且简洁的 todos 使方案显式，而不做任意项数上限或纯管理填充。

每个新项包括：

- `priority`：`P0`、`P1` 或 `P2`；
- `text`：以 `[P0]`、`[P1]` 或 `[P2]` 开头的简短复选框标题；
- `task_class`：通常为 `advancement_task`；
- `action_kind`：紧凑动作 token，如 `implement`、`test`、`review`、`document` 或 `investigate`。

除非首个有用步骤被具体用户 gate 阻塞，否则至少一个新项应为 `P0`。用户 todos 保留给 owner 决策、私有物料、凭据、破坏性 git 或生产授权。

## 优先级排序

优先级桶排序为 `P0`、`P1`、`P2`。同一桶内，规划器的列表顺序即相对优先级。

Host 必须在使用 `loopx todo add` 运行时保留该顺序。LoopX status 与 quota 投影已使用 todo index 作为同优先级决胜器，因此先写入的 `P0` 无需新等级字段即胜过后写入的 `P0`。

## 显式 Issue-Fix 能力路由

Goal 文本绝不选择产品 capability。要进入 issue-fix 路由，调用方必须对 `start-goal` 显式传 `--capability-route issue-fix`（或使用等价显式 host 开关）。Issue/PR 措辞、公开 URL 或字面字符串 `issue-fix` 都只是客观文本，不授予任何路由。

会话型 host 不得让模型从 goal 文本拆分该开关，然后重建单独 CLI 参数。它们生成的 `/loopx` 条目把完整可见参数字符串一次性经 `start-goal --slash-command-arguments` 传入；CLI 只消费前导的类型化路由开关，并把剩余部分当作 goal 文本。直接集成可以继续使用结构化 `--capability-route` 加 `--goal-text`。这两种输入形式互斥，畸形或不支持的领导路由开关在构建引导事务前失效关闭。

只有前导 `--capability-route` 开关被解析。原始参数字符串中后续出现的同一文本是普通 goal 文本，不是错误。

`start-goal` 把该显式开关投影为类型化 `selected_capability_route`。这是仅引导选择，不是后续 Turn 权限。引导事务先把候选准入持久化在 capability 自有状态中。缺失证据投影 `evidence_required`；未解决的交叉引用、已关闭 PR 或维护者评论投影 `verification_required`。只有 `admitted` 的 `proceed` 候选进入可行性。最终复用与终态路由不同于待验证。Todo 只保留调度路由（`action_kind`）与稳定公开目标（`target_key`）；issue 事实、先前工作检查、仓库证据、复现、scope 与验证仍归 `issue_fix` 状态所有。

后续 Turn 通过 `quota should-run.selected_todo` 继续；它们不再次调用 `start-goal`，也不从过期 prompt 上下文推断准入。可运行可行性结果用 `capability_binding_ref` 把投影的 successor 绑定到持久化可行性行。路由的类型化 `implementation_admission.durable_execution_binding` 契约告诉 Host 如何解析该引用，并把 Todo 的精确 `action_kind` 与 `target_key` 与准入投影对比。

对于预绑定 Todos，Host 可以把精确动作与目标与当前可行性行对比。仅前缀匹配绝不是准入权限。这使 capability 选择、持久化 Todo 执行所有权与 Goal 继续保持为独立契约。

引导事务的 `command_cwd_source` 指向包中解析出的 `project`；host 从该精确根目录执行其项目相对命令。

在规划实现前，选择当前开放的公开 tracker issue。仓库 TODO/FIXME 条目、警告与偶然测试失败可能支持后续复现，但它们不是 issue 身份：

```bash
gh issue list \
  --repo "$(gh repo view --json nameWithOwner --jq .nameWithOwner)" \
  --state open \
  --limit 20 \
  --json number,title,url,labels
```

```bash
loopx issue-fix workflow-plan \
  --url <github-issue-or-pr-url> \
  --repo-path <approved-repo> \
  --repository-context-json <compact-context.json> \
  --fetch-candidate-evidence \
  --goal-id <goal-id> \
  --validation-label "<validation command>" \
  --format json
```

预览把公开元数据、仓库上下文、摄取分类、分支规划、验证标签、可行性检查点与 PR 评审就绪 blockers 映射进 `/loopx <goal text>`。仓库上下文把紧凑策略、架构、变更范围、复现与验证引用钉到一个修订；记忆与外部专家在仓库验证之前保持咨询性。内置公开 GitHub 收集器对关闭的 PR 引用、交叉引用与维护者评论元数据生成 issue 特定、完整、非截断回执，而不保留正文。精确关闭引用可以直接复用。交叉引用在检查其精确当前修订之前保持 `verification_required`；维护者评论投影内容读取 gate 加处置 successor。可选 `--candidate-resolution-json` 在它们反馈到当前源行之前把那些紧凑结局绑定到当前 PR head 或维护者评论 `updatedAt` 修订，使变更的来源修订失效关闭。有上限的聚合 PR 索引可以生成候选，但不能证明先前工作缺失。存在 `--goal-id` 时命令持久化预检回执。只有 `admitted` 的 `proceed` 决策可以启动新实现并进入可行性。待验证、最终复用与终态路由不得调用可行性。对于 `proceed` 候选，记录紧凑观察并让 LoopX 选择恰好一条实现路由。按优先级与规划器顺序写入投影的 successors：

```bash
loopx issue-fix feasibility \
  --url <github-issue-or-pr-url> \
  --reproduction-status <confirmed|planned|missing|blocked> \
  --scope-class <bounded|uncertain|oversized> \
  --repository-context-json <compact-context.json> \
  --goal-id <goal-id> \
  --format json
```

只写入投影的路由 successor 或 no-follow-up。用户 todos 或操作员 gate 必须覆盖私有复现物料、issue 正文/评论读取、外部 issue 评论、PR 创建、合并、发布、破坏性 git、生产动作与仓库策略批准。

## 停止条件

在以下情况停止并询问用户，而不是写入或执行：

- 形成公开安全 todo 前必须读取私有源物料；
- 需要凭据或 secret；
- 需要破坏性 git 或生产动作；
- host 无法执行 shell/CLI/工具调用或持久化 LoopX 状态；
- host 无法激活或暴露所需 host loop，且无法显示具体可粘贴 gate。
