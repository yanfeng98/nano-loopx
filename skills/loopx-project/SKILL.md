---
name: loopx-project
description: Use when connecting a repository or project goal document to LoopX, maintaining project-local goal state, refreshing stale dashboard status, syncing local projects into the shared global registry, or diagnosing LoopX CLI/PATH/status/history issues across multiple repos. For registering durable project materials such as Lark/wiki/design docs, prefer the narrower loopx-doc-registry skill.
---

# LoopX 项目工作流


当任务提到 LoopX、loopx、项目 goal 文档、多项目 dashboard/status、陈旧的
latest run、`.loopx/registry.json`、`.codex/goals`、`refresh-state`、
`sync-global` 或连接新仓库时，使用本技能。如果任务主要是读取、记住、记录、
索引或注册持久项目材料，先加载 `loopx-doc-registry` 并使用该更窄的工作流。

LoopX 有两层：

- **项目本地状态**：每个仓库拥有 `.loopx/registry.json` 与
  `.codex/goals/<goal-id>/ACTIVE_GOAL_STATE.md`。
- **共享本地控制面**：`~/.codex/loopx` 存储运行历史与
  `registry.global.json` 用于多项目状态。

不要把某项目的 registry 条目手动复制到另一个项目。本地 `connect` 与
`refresh-state` 应自动同步到共享全局 registry。

## 斜杠命令回退

当可见用户消息恰好是 LoopX 斜杠命令，或是以 LoopX 斜杠命令加参数开头时，
不要把它当作普通聊天。

可识别的项目本地 goal 启动命令：

- `/loopx <goal text>`
- `/loopx --capability-route issue-fix <goal text>`

可识别的仓库评审命令：

- `/loopx-pr-review`
- `/loopx-pr-review <time window or filter text>`

如果 `/loopx` 之后的文本以精确可选前缀 `--capability-route issue-fix` 开头，
只从 goal 文本中移除该前缀，作为显式 start-goal 路由开关传递。否则 `/loopx`
之后每个非空白字符都是 goal 文本。绝不从 issue/PR 措辞、URL 或语义相似性
推断产品 capability 路由。不要降低任一形式为状态或检查轮次。

`start-goal --project` 保留所请求的项目路由，包括链接的 git worktree，
使新任务不会继承更旧 worktree 的 goal。较低级的诊断命令包仍可能报告规范的
`canonical_project_alias` / `source_registry` 路由。不要手动把任一路由替换为
未公布的 bootstrap 命令。

从目标项目根，把 `/loopx` 后的文本作为显式 goal 启动目标传入，然后才计划或
写入项目状态：

```bash
loopx start-goal --guided --project . --goal-text "<GOAL_TEXT>"
```

仅当调用方提供了该精确显式路由开关时，才追加 `--capability-route issue-fix`。

已知时包含 `--goal-id <STABLE_GOAL_ID>`。Codex CLI 自动读取稳定的环境变量
`CODEX_THREAD_ID`；其他暴露稳定不透明线程 id 的宿主应在每次 `/loopx` 调用
时把它作为 `--thread-id <HOST_THREAD_ID>` 传入。如果该线程已绑定，在 start、
heartbeat、quota、refresh-state 与 Todo 命令中复用返回的
`--agent-id <REGISTERED_AGENT_ID>`。仅当当前会话已拥有该身份、线程绑定解析到它、
或用户显式要求接管那个精确 agent 的工作时，才包含
`--agent-id <REGISTERED_AGENT_ID>`。

当存在稳定线程 id 但没有绑定时，把它视为新的宿主会话，并遵循返回的新注册
默认值。仅当用户显式请求接管那个精确 agent 时才选择既有通道，然后用返回的
`bind-agent-thread` 命令绑定。没有线程 id 可用时，保留失败关闭的身份关卡，
绝不从 registry 顺序或唯一注册通道推断接管；仅当用户在该不可绑定宿主上显式
请求新鲜 onboarding 时传 `--new-peer`。选择一个新鲜公开安全的 id，预览并执行
`register-agent`，并要求 `--require-new --execute` 结果报告 `ok=true`、
`changed=true`、`written=true`、全局同步成功，且重新运行 `start-goal` 前有
核验过的注册回读。预览只是建议，绝不允许继续。如果 `start-goal --guided`
不可用，刷新本地 LoopX CLI 或用检出的 LoopX 仓库 CLI 做验证；不要把
`/loopx <goal text>` 静默降级为裸 `/loopx` 只读命令。仅当实现或调试低级宿主
交接包时才使用 `loopx bootstrap-command-pack --project . --goal-text "<GOAL_TEXT>"`。

如果已连接 goal 之后需要更宽或修正的写入边界，不要只为了改范围而重跑
`loopx bootstrap --force`。改用增量配置路径：

```bash
loopx configure-goal \
  --goal-id <STABLE_GOAL_ID> \
  --write-scope "<SAFE_WRITE_SCOPE>" \
  --execute
```

如果显式需要破坏性重连，传 `--preserve-todos` 与 `--force`，除非用户打算重建
活动状态文件并丢弃既有 todo 投影。

`/loopx <goal text>` 是显式 goal 启动意图：先生成简洁有序计划，然后按优先级
写入 todos，用 planner 顺序加 `todo add` 写入顺序作为同优先级平局裁决。对宽泛
或模糊的产品方向，使用小型公开安全计划集；对清晰的有界问题，使用最小充分有序
todo 计划，避免仅管理性填充。

全局管理斜杠命令（如 `/loopx-global-summary`、`/loopx-global-gates`、
`/loopx-global-todos` 与 `/loopx-global-risks`）不是项目 bootstrap 命令。
把它们路由到全局管理命令契约或状态摘要界面，而不是 `bootstrap-command-pack`。
遗留 `/loop-global-*` 形式可视为别名，但规范帮助与包应使用 `/loopx-global-*`。

仓库评审斜杠命令也不是项目 bootstrap 命令。如果可见请求以 `/loopx-pr-review`
开头，停止本项目 bootstrap 工作流并加载更窄的 `loopx-pr-review` 技能。
该技能拥有必需的第一条命令、包保留规则与每 PR 五块评审契约。不要从本更宽泛
的项目技能处理 `/loopx-pr-review`，也不要路由到 `loopx-pr-merge`，除非用户
之后要求批准、评论、合并、自行合并或管理员绕过特定 PR。

当请求要求盘点、排优先级、记录或持续监控跨几个 PR 或 MR 的交付项目时，
在项目 goal 事务确立后加载更窄的 `loopx-pr-program` 技能。
该技能拥有 provider-neutral 快照、分组 monitor 状态、材料变化检测与路线图投影。
把深度按变更评审保留在 `loopx-pr-review`，把 provider 变更留在单独授权的
工作流中。

当用户刚连接项目、收到 guided start 包或首次收到 bootstrap 命令包时，简要
告诉他们可用的命令，而不是假定他们会查看 CLI 帮助：

- `/loopx <goal text>`：通过先计划后写 todo 的流程启动具体 goal。
- `/loopx-global-summary`：读取全局进度摘要。
- `/loopx-global-gates`、`/loopx-global-todos`、`/loopx-global-risks`：检查
  管理级 gate、工作与风险。
- `/loopx-pr-review`：使用 `loopx-pr-review` 技能运行 `loopx pr-review`，
  逐个评审 unmerged/merged PR 分组。

命令行发现使用：

```bash
loopx slash-commands
```

## 注册项目权威与材料源

当项目 agent 发现未来 agent 可能用于路由、验证或冲突解决的持久设计文档、研究
笔记、benchmark 论文、所有者包、迁移报告或外部材料时，把其视为 doc-registry
技能触发点。先识别目标项目与 goal；不要仅因本 worker 找到就把材料注册进当前
元 goal。

对当前项目拥有的材料，先更新项目本地文档注册表或等价权威地图，然后在同一
项目的被忽略 `.loopx/registry.json` 中注册紧凑的脱敏源契约：

```bash
loopx register-authority-source --goal-id <STABLE_GOAL_ID> ...
```

对另一项目的 DOC_REGISTRY 风格地图，只导入紧凑权威摘要，而不是复制原始路径、
文档 id、URL、评论或源正文：

```bash
loopx import-doc-registry-authority --goal-id <STABLE_GOAL_ID> ...
```

注册后刷新状态或状态文件，使评审包、只读地图与 heartbeat worker 无需依赖
聊天记忆即可找到新权威。当目标项目不明确、源无法表示为公开安全元数据、或
下一步需要读取被 gate 的源正文时，停止并写入项目本地 todo 或 blocker。

## 面向所有者的 Explore 视图

把规范 Explore 拓扑与面向所有者的决策图视为同一证据源上的两种不同读模型：

- 规范 JSON、Mermaid 与 Nodes/Edges/Findings 表保留完整的公开安全节点身份、
  证据与谱系；
- 聚焦 status/tag 导出是有界证据子集，默认不是主管视图；
- 主管图对操作员决策应用语义压缩。它应展示决策契约、baseline/现任、决定性
  负向证据、活跃工作或容量、材料性风险、终态 gate 与下一决策。语义压缩可以
  收紧标签并移除真实重复，但必须保留材料性决策与证据节点及其谱系。

除非声明的展示契约证明导出已携带这些语义角色，否则绝不从完整或聚焦规范导出
直接覆盖主管白板。对周期同步，保留项目本地展示契约，含必需角色、稳定规范 id、
语义段落或链接子图，以及非身份守卫。默认基数策略是图增长：不要因图跨过
20 节点这样的通用计数就省略或合并材料性节点。硬 `max_nodes` 或 `max_edges`
限制仅作为显式 opt-in 展示政策有效，且需声明范围与溢出行为；没有该政策时，
把这些限制视为无界。

用目标渲染器渲染，运行重叠与文本溢出检查，检查实际预览，然后同步并验证远端
源或摘要。修复失败的可读性检查用重排布局、更短标签、更大框架或更多语义子图，
而不是删除材料性证据。如果任何检查仍失败，保留先前所有者视图；不要发布结构
有效但不可读的图。

此分离不把 quota、todo、launch、stop 或晋升权限转移到展示层。先在规范
Explore 状态中记录材料性实验迁移，然后刷新主管投影。

## 预检

在项目工作前一次性解析宿主命令。在原生 Windows PowerShell 7 上，把已安装的
`loopx.ps1` 目录保留在 Windows 用户 `PATH` 中并运行：

```powershell
loopx doctor
```

当当前 Windows 执行器不是 PowerShell 时，显式调用 PowerShell 7 保留同一入口：

```text
pwsh.exe -NoLogo -NoProfile -File "$HOME/.local/bin/loopx.ps1" doctor
```

如果 Windows 入口缺失，从 PowerShell 7 运行受信任检出安装器，然后启动新的宿主
进程以继承用户 `PATH`：

```powershell
pwsh -NoLogo -NoProfile -File .\scripts\install-windows.ps1 -Python (Get-Command python).Source -AddToUserPath
loopx doctor
```

在 POSIX 主机上使用现有 shell 入口：

```bash
export PATH="$HOME/.local/bin:$PATH"
loopx doctor
```

如果 `loopx` 不在 PATH 上：

```bash
install_script="$HOME/loopx/scripts/install-local.sh"
if [ -x "$install_script" ]; then
  "$install_script"
  export PATH="$HOME/.local/bin:$PATH"
fi
loopx doctor
```

如果仍失败，报告精确缺失部分，不要假装连接成功。

## 为用户诊断

当用户询问 LoopX 是否工作、项目能否自治、为何卡住，或说"诊断 LoopX"时，
不要把 shell 命令交给用户。自己运行诊断界面，然后从证据推理。

优先 agent 面向包：

```bash
loopx diagnose
```

已知目标 goal 时：

```bash
loopx diagnose --goal-id <STABLE_GOAL_ID>
```

`diagnose` 命令不是最终裁判。它返回紧凑 `status`、`quota should-run`、todo、
interaction-contract 与边界信号加推理清单。把这些信号作为证据，然后用你自己的
话回答：

- 项目当前能否自治；
- 什么证据支持该结论；
- 什么阻塞自主交付或 self-repair；
- 若投影了，精确的用户/控制器问题是什么；
- agent 下一步做什么。

只有你的推理确认用户 gate 不阻塞所选路径、quota 允许一次轮次、
`goal_boundary` 允许该工作、且存在具体 agent todo 或 recommended action 时，
才声称自主就绪。如果 `diagnose` 无法读取 status/quota，先修复安装、PATH、
registry 路径或项目连接；不要从聊天记忆推断就绪。

## 消耗自动计算前

在 heartbeat、计划 tick、长程适配器或自主项目 agent 消耗另一个交付轮次前，
问 LoopX 该 goal 是否够格：

```bash
loopx --format json --registry "$HOME/.codex/loopx/registry.global.json" quota should-run --goal-id <STABLE_GOAL_ID>
```

对已注册的多 agent goal，包含此 agent 身份：

```bash
loopx --format json --registry "$HOME/.codex/loopx/registry.global.json" quota should-run --goal-id <STABLE_GOAL_ID> --agent-id <REGISTERED_AGENT_ID>
```

如果已注册 goal 返回 `automation_prompt_upgrade.required=true`，把已安装的
自动化提示词视为陈旧，并用 `heartbeat-prompt --agent-id ... --agent-scope ...`
重新生成。

如果默认 `loopx` 负载与刚合并的源码检出或
`PYTHONPATH=<checkout> python3 -m loopx.cli ...` 交叉检查矛盾，暂停交付，
在信任 quota 前运行 `loopx doctor`。已安装命令通常是 release snapshot 包装器，
所以自行合并的修复可能需要用 `loopx update --execute --ref main` 或干净 main
检出的 `scripts/install-local.sh` 从最新可信 `origin/main` 刷新本地安装；
刷新后重跑默认 `loopx` 命令，且只在运行时负载匹配修复后的源码行为时消耗
quota。脏或非 main 检出默认仅用于 canary。只有检出已通过其晋升验证且默认替换
是有意写入后，才用 `LOOPX_PROMOTE_DEFAULT=1 scripts/install-local.sh`。

在原生 Windows 上，自动归档更新与回滚是失败关闭的。更新可信检出，重跑
`scripts/install-windows.ps1`，并在消耗 quota 前用 `loopx doctor --deep` 验证
新发布。

如果响应是 `state=operator_gate`，把它视为用户/控制器交互，而不是静默跳过。
存在时读取 `gate_prompt`、`operator_question`、`recommended_action`、
`next_handoff_condition`、`missing_gates` 与 `user_todo_summary` 和
`agent_todo_summary`，然后用中文询问具体 gate，除非同一未解决疑问已在最近的
可见线程中出现。重复公开 PR 合并批准 gate 前，对照当前紧凑 PR 生命周期状态
协调。当 todo 有合并范围决策（如 `direction:action:merge_pr_<number>`）且公开
PR URL 明确时，运行：

```bash
loopx issue-fix pr-gate-reconcile \
  --goal-id <STABLE_GOAL_ID> \
  --todo-id <USER_GATE_TODO_ID> \
  --url <PUBLIC_GITHUB_PR_URL> \
  --fetch-metadata \
  --execute
```

然后重跑 `quota should-run`。该命令只能完成匹配的 `user_gate`，且仅在紧凑公开
元数据报告 `MERGED` 或 `CLOSED` 后；它不记录正文、评论、日志、provider 负载或
外部写入。如果 URL 不明确或公开读取失败，保留该 gate 并展现精确的解析失败，
而不是声称所有者仍需批准一个已经终态的 PR。
仅当 `interaction_contract.user_channel.action_required=true` 或
`user_todo_summary.open_count > 0` 时，通知必须点出具体负载 todo(s)/问题，
绝不是只写"owner gate"；如果这些必需的用户面向项没有被投影，说
"具体 user todo 未投影，需修复 LoopX 状态投影"；绝不在这种情况下说
"no new user action"。当 `interaction_contract.user_channel.action_required=false`
且 `user_todo_summary.open_count=0` 时，允许"无用户待办/无需通知"或安静的
无通知结果；不要暗示状态投影 bug。提问期间不要运行 `agent_command`、适配器
工作、写控制、生产动作或被 gate 的路径。

存在时优先守卫的 `interaction_contract`。它是用户 / agent / LoopX CLI 切分的
当前机器可读协议：`interaction_contract.user_channel` 说明是否询问用户，
`agent_channel` 说明 Codex 是否必须尝试工作或可安静无操作，`cli_channel`
说明应用哪种 CLI 迁移与消耗政策。把 `execution_obligation`、
`heartbeat_recommendation`、`work_lane_contract` 与 `goal_boundary` 等更旧
字段视为该契约下的兼容/下钻字段，而非竞争真相源。

如果响应是 `should_run=false` 且不是 `safe_bypass_allowed=true`，本轮不要为
该 goal 运行实现或适配器工作。从 heartbeat 运行时，把其 `<current_time_iso>`
作为 `quota should-run --turn-instance-id <HEARTBEAT_TURN_ID>` 传入，
并在同 heartbeat 重试中复用该 id。这会在每次 heartbeat 提交一个幂等 receipt；
当 `effective_action=monitor_quiet_skip` 时，同一守卫也提交无消耗停滞观察并
返回后续决策。如守卫暴露，遵循 `autonomous_replan_required` /
`execution_obligation.must_attempt_work=true`。如果 `heartbeat_receipt.status=write_failed`，
用同一 turn id 重试，而不是手动追加另一轮询。否则仅当没有 operator gate 可问
时安静报告或记录公开安全的 `reason`。保持 heartbeat 自动化活跃：无变化的纯
monitor 轮询是保活无操作，不是自停信号。如果命令非零退出，失败关闭：在消耗
计算前运行 `loopx doctor` / `loopx status` 并修复状态收集。

如果响应是 `state=operator_gate` 且 `safe_bypass_allowed=true`，该 gate 只阻塞
被 gate 的交付路径。gate 已被提出后，你仍可读取活动状态并从 Priority Stack 做
一个有界安全绕行步骤，如只读 steering 分析、文档或另一个不依赖该 gate 的
P0/P1 事项。如果该安全绕行步骤实际消耗自动计算，验证它、写回
progress/critic/next action，可选刷新状态，并追加一次 quota 消耗事件。如果
`user_todo_summary.open_count > 0`，安全绕行报告必须包含这些既有打开的用户
todo，且不得说"no new user action"。如果 `agent_todo_summary.open_count > 0`，
把它用作项目 agent 的安全后续检查清单，而不是挖掘聊天历史或过长的 Next Action。

如果响应是 `safe_bypass_kind=outcome_floor_recovery` 或
`heartbeat_recommendation.recommended_mode=outcome_floor_recovery`，结果下限
阻塞仅表面交付，但允许一次有界恢复尝试：产出 `quota.must_advance` 点名的
必需 ranker/跨域证据产物，或写回阻止该产物的具体 blocker。避免
summary/queue/契约传播与仅合成的测试链。只在验证过的证据/blocker 写回后
精确消耗一次。

此守卫只是计算分配检查。它不授予写权限、不绕过 operator gate、不替代运行界
的人类奖励。Operator gate 阻塞被 gate 的交付路径，而不是无关的安全 steering
工作。
对够格当前 goal，依赖或兄弟 goal 的 todo 不得消耗整个够格轮次。
把这些 todo 记录或呈现为依赖 blocker，
但继续 steering 审计，并在当前 goal 存在时选择一个与 gate 无关的
P0/P1/P2 候选。仅当打开的用户/所有者 todo 属于当前 goal 的守卫负载或
项目资产并阻塞所选交付路径时，才在交付前停止。
常规公开仓库发布是边界决策，不是常设 operator gate：当活动状态允许该步骤、
验证通过且公共/私有边界扫描干净时，commit、push 与 PR 创建可以自治进行。
对私有或公司内部材料、凭据、破坏性 git 操作、生产动作或显式要求评审的仓库
规则停下。
为守卫使用共享全局 registry，使项目 agent 读到与 dashboard 相同的 operator
gate、用户 todo、agent todo 与 quota 状态。这不意味着所有项目工作都是全局的：
`todo add`、`refresh-state`、适配器运行与项目文件读取仍使用项目本地状态/registry，
然后把公开安全投影同步回全局控制面。如果两个项目共享一个 `goal_id`，
把它视为 registry 健康 bug 并修复 id/源映射。

如果 `should_run=true`，不要只继续最近的先前 TODO。读取活动状态的 Priority
Stack、最近进度与 critic，然后在选择工作前运行简短 steering 审计：有用时列出
跨不同 P0/P1/P2 通道的至少三个合理 next-action 候选；如果同一主题已消耗几个
近期交付切片，应用继续检查并说明为何继续仍胜出；把计算 quota 与专注 quota
分开；记录任何不应被遗忘的落选高价值候选。包含产品瓶颈透镜：询问核心 goal
当前是否被用户体验、agent 能力、证据质量、适配器就绪或优先级规则缺口
瓶颈化，当一个具体瓶颈候选应超过最近的本地 TODO 时提升它。然后从该审计中
恰好选择一个有界、可验证的步骤。

当你向用户讲述已连接 LoopX 计划、top-todo 列表、优先级栈或路由变更时，
把它视为写回触发点，而非聊天记忆。如果计划含有具体未来 P0/P1/P2 工作、
用户动作、路由决策或弃用，在最终响应前更新活动状态 todos / Next Action /
`refresh-state`，或显式说明该计划为何仅是推测且未写入。用 `loopx todo add` /
`todo update` 建立持久工作项；不要只把它们留在散文、评审文档或 Lark/聊天
回复中。

对已连接交付 goal，选择步骤前还要从 `quota should-run` 负载读取
`goal_boundary`。它携带 registry 的适配器状态、允许的写入范围、父批准范围、
守卫与停止条件。把它视为项目特定边界契约，使自动化提示词保持简短，而不是
重复长串每项目受保护范围列表。
读取 status 或 quota 路由时，仅当条目有项目资产支撑时才把 `attention_queue.items`
与 `project_asset` 用作当前权威。如果 `project_asset` 缺失，或源是遗留/原始
回退，不要从原始队列字段推断所有者、gate 或停止条件权威。

## 设置周期 Heartbeat

当用户或控制器需要已连接 goal 的周期宿主 heartbeat 时，优先生成器而非
手动复制 quota 生命周期：

```bash
loopx heartbeat-prompt --goal-id <STABLE_GOAL_ID>
```

当目标 Codex agent 能自己检查 LoopX 状态与 CLI 输出时，默认生成正文是薄的。
传 `--thin` 仍然受支持且显式：

```bash
loopx heartbeat-prompt --thin --goal-id <STABLE_GOAL_ID>
```

审阅完整生成契约后，当已安装提示词应内联携带更多生命周期细节时使用紧凑正文：

```bash
loopx heartbeat-prompt --compact --goal-id <STABLE_GOAL_ID>
```

如果已安装自动化正文仍需更小，使用 brief 正文：

```bash
loopx heartbeat-prompt --brief --goal-id <STABLE_GOAL_ID>
```

对带 `coordination.registered_agents` 的共享控制面 goal，始终在已安装自动化
提示词中包含注册身份与范围：

```bash
loopx heartbeat-prompt --thin --goal-id <STABLE_GOAL_ID> \
  --agent-id <REGISTERED_AGENT_ID> \
  --agent-scope "<THIS_AGENT_SCOPE>"
```

注册 agent 后，无范围的 `heartbeat-prompt` 调用失败关闭，使陈旧自动化暴露
升级错误，而不是无身份运行。

对已连接 goal，省略 `--active-state`；CLI 从 registry goal `state_file` 解析
活动状态，使已安装自动化不固定陈旧路径。仅对分离的状态文件、迁移检查或兼容
测试传 `--active-state <ACTIVE_GOAL_STATE_PATH>`。

把生成的任务正文复制到宿主 heartbeat 自动化中。thin 正文是可信本地
worker 的已安装默认：它保持自动化提示词项目无关，并告诉 Codex 每次唤醒重读
registry/global quota 真相、活动状态、status/run history、仓库状态与项目信号。
扩展审计源使用 `--full`。当上下文压力重要但已安装提示词仍应内联携带 quota、
gate、blocker-push、recommendation、steering-audit、writeback、refresh 与
spend 生命周期时，compact 正文有用。brief 正文在已安装提示词中只保留
preflight/guard、核心不变量与消耗记账，详细分支委托回生成的 compact/full
契约。
生成的守卫与消耗命令显式使用共享全局 registry，使项目 heartbeat 读到与
dashboard 相同的 operator gate 与用户 todo，无论当前仓库是哪个。完成的 heartbeat
交付通过 `quota spend-slot --source heartbeat --execute` 消耗，而不是通过自然语言
报告。Quota 槽默认分钟粒度：分钟 heartbeat 消耗 `--slots 1`，而更粗的固定间隔
自动化应消耗该完成轮次消耗的调度分钟数。

把项目特定行为排除在自动化提示词之外。在项目 registry、
`.codex/goals/<goal-id>/ACTIVE_GOAL_STATE.md`、适配器输出或窄公开/私有边界规则
中编码本地差异。如果生命周期规则跨项目有用，更新 `loopx heartbeat-prompt`
及其冒烟契约，而不是手工编辑某条 heartbeat 自动化。
对交付特定边界，优先 `quota should-run.goal_boundary` 中呈现的 registry 字段；
自动化提示词只需说明遵循该负载，并在有用工作落在其之外时停止。

当 LoopX 客户端/提示词契约变化时，在同一补丁中更新匹配的冒烟覆盖。接口预算与
回归约束属于轻量冒烟脚本，如 `examples/control_plane/heartbeat-prompt-smoke.py`、
`examples/control_plane/quota-plan-smoke.py` 或
`examples/control_plane/quota-contract-smoke.py`；更重的 Codex CLI 加 LoopX
端到端检查应保持显式或低频，而不是成为默认 heartbeat 路径。

quota 守卫返回 `execution_obligation` 与 `heartbeat_recommendation`。它还返回
`execution_obligation` 与 `scheduler_hint`，后者控制下次唤醒节奏与外部循环
无变化轮询自停；这是调度政策，不是交付权限。Codex CLI TUI 与 Claude Code 循环
应在应用其 `after_limit` 前从 `scheduler_hint` 运行最终 quota/replan 检查；
如果守护变化或返回 `run_now`，遵循新 quota 契约而不是停止。宿主 heartbeat
worker 应在可用时搜索/使用 `automation_update`。如果
`scheduler_hint.action=stop_until_explicit_resume` 且
`scheduler_hint.codex_cli.host_action=pause_or_delete_current_heartbeat`，
调用一次 `automation_update` 暂停当前 heartbeat（仅当宿主无法暂停时删除），
验证宿主结果，不消耗 quota，并结束该轮次。此终态宿主动作优先于 RRULE 处理且
不需要 scheduler ACK。否则仅当
`scheduler_hint.codex_cli.stateful_backoff.apply_needed=true` 且存在
`scheduler_hint.codex_cli.recommended_rrule` 时才使用 `automation_update`。
RRULE 更新成功后，用 `scheduler_hint.codex_cli.ack_hint.cli_args` 运行 `loopx`
（通常是 `quota scheduler-ack-current`，它会重读最新 scheduler hint，而不是
手工复制短生命周期重置 token）。每个 hint 与轮次最多尝试一次宿主更新。失败或
超时时，不要重试或 ACK；运行一次 `scheduler_hint.codex_cli.failure_hint.cli_args`。
该无消耗写回记录失败的目标/观察宿主对，使后续 heartbeat 抑制精确重复，直到
任一值变化。在观察到的宿主节奏下继续允许的交付。如果 `apply_needed=false` 但
`ack_needed=true`，匹配的宿主回读已证明 RRULE；跳过 `automation_update`，
直接运行绑定的 ack hint。LoopX 拥有重置/进展状态，并在期望 RRULE 已应用时
省略 `recommended_rrule`。
节奏变更、重置为初始更新、最终检查与自停变更不消耗 quota。
对唯一匹配的活跃宿主 heartbeat，`quota should-run` 自动协调已安装 RRULE
与 LoopX 的 ACK ledger。把 `stateful_backoff.host_observation.status=drift_detected`
视为节奏修复权威；陈旧或过早 ACK 不得抑制 `apply_needed`。
当回读匹配尚未绑定到调度器状态的 reset RRULE 时，ack hint 携带精确重置 token、
身份签名与 CLI 路由；缺失回读不得使用此捷径。
此回读仅节奏相关，绝不暴露自动化提示词或授予 LoopX 直接编辑宿主文件的
权限。

决定安静无操作前读取 `execution_obligation`：
`heartbeat_recommendation.notify` 只是用户通知政策，不是执行 gate。如果
`execution_obligation.must_attempt_work=true`，即使 `notify=DONT_NOTIFY` 也尝试
一个有界进度批次或片段；安静无操作需要
`execution_obligation.must_attempt_work=false` 且没有
`notify_user_on_open_todo=true` blocker-push 通知。新连接的只读 goal 应遵循
`recommended_mode=run_first_read_only_map`：运行一次真实
`loopx read-only-map --goal-id <STABLE_GOAL_ID>`，验证保存的
`read_only_project_map`，验证后精确消耗一次，需要时随后同步或刷新状态。
已映射 goal 应遵循 `recommended_mode=mapped_noop_if_unchanged`：没有新指令、
所有者证据、agent todo、陈旧源或安全交接时，返回安静无操作，不再一次干跑、
文件编辑或 quota 消耗。

生成的任务正文还携带无进展自我修复守卫。更重要的是，`quota should-run` 在
活动状态或公开运行历史显示重复 typed 无进展轮次时可能暴露硬
`autonomous_replan_obligation` / `execution_obligation.must_attempt_work=true`
契约。安静未来 monitor heartbeat receipts 只是活性证据；
`dead_monitor_repeat` 在其声明阈值把带具体 Todo 或目标身份的未变化到期/外部
monitor 执行计数。在另一次安静无操作前服从该机器契约：当边界清晰时，通过
实现、验证与写回运行一个有界 self-repair/replan 批次，然后消耗一次。当修复有
明显验证边界时不要停在第一个微小子步骤。仅在连续 2 个停滞轮次（同一修复路径
再卡 2 个够格轮次）后取消或暂停 heartbeat 自动化；用 `NOTIFY` 解释无进展循环，
并为该自取消轮次跳过 quota 消耗。
同一生成任务正文还在验证加干净公共/私有边界扫描后使常规公开 commit、push 与
PR 创建自治。不要为公开安全发布本身重新引入用户 gate。
它还尊重 `notify_user_on_open_todo=true`：focus-wait、waiting 或 external-evidence
通道中的打开用户 todo 应变成紧凑 blocker-push `NOTIFY`，最多三项，同时跳过该
blocker-push 轮次的交付工作与 quota 消耗。如果负载包含
`open_todo_notification_policy=repeat_until_resolved`，重复该 `NOTIFY` 直到
todo 完成、推迟或替换。当用户确认既有评审或动作已完成时，立即写回该精确 todo：
只用显式 typed 决策完成，否则在授予权限外取代陈旧 gate；然后刷新状态并重跑
quota，使继任者或自主 replan 浮现。当
`user_gate_notification_cooldown.notification_suppressed=true` 时，保留待处理
gate 但返回安静 `DONT_NOTIFY`；有界提醒窗口或材料性 gate/宿主变化重新打开
通知。其他 blocker-push 情况在最近已呈现同一 blocker 时仍可去重。
够格的仅 monitor 无迁移轮询保持用户 todo 在负载中可见，但在材料性迁移出现前
应安静。

保持 Codex CLI 可见 goal 文本简短，例如
`按 ACTIVE_GOAL_STATE.md，基于 LoopX 体系，推进项目`。不要用该简短文本作为
自动化正文。跨项目，自动化正文应是同一生成生命周期提示词，仅变化 `goal_id`、
`active_state` 与窄项目边界规则。当项目看似需要自定义自动分支时，先把它视为
LoopX 产品缺口，而不是把一次性控制逻辑粘进调度器的理由。

## 生成评审包

当项目 agent、控制器线程或本地 shell 需要当前操作员包时，优先 CLI 包而不是
让用户找 dashboard 复制按钮：

```bash
loopx review-packet --goal-id <STABLE_GOAL_ID>
```

机器可读检查时，把全局格式标志放在子命令前：

```bash
loopx --format json review-packet --goal-id <STABLE_GOAL_ID>
```

当人类/控制器决策已批准且唯一剩余步骤是传达目标 agent 指令时，使用最小交接
形式：

```bash
loopx review-packet --goal-id <STABLE_GOAL_ID> --handoff-only
```

此命令只读。它把当前状态打包成与 dashboard 相同的 Review Packet 形状；不追加
人类奖励、不追加 operator gate、不刷新状态、不授予写控制、不授权生产动作。
`--handoff-only` 只从 markdown 输出剥离人类决策包装；JSON 输出返回最小化交接
负载，用 `handoff_text` 替代完整操作员包。如果所选队列项是遗留/原始回退而非
项目资产支撑，不要把原始队列字段当作所有者、gate 或停止条件权威。

按顺序读取包：

- `人只需判断`：用户或控制器在 dashboard/operator 视图或可信本地 shell 中
  决定。目标项目 agent 不能自行批准此部分。
- `用户本地 Gate 记录草稿`：供用户/控制器预览。目标项目 agent 不得把此草稿
  当作自己的命令运行。
- `给项目 Agent`：仅当包的前进条件已满足时的可执行交接上下文。如果其停止
  条件触发，停止并报告精确 blocker，而不是继续。

## 连接新项目

1. 读取项目 goal 文档并窄范围检查仓库。
2. 提取稳定 `goal_id`、单行 `objective`、`domain`、权威源、验证界面、首个
   安全动作与公共/私有边界。
3. 从项目根运行 `connect`。goal 文档显式授权变更前优先只读：

```bash
loopx connect \
  --goal-id <STABLE_GOAL_ID> \
  --objective "<OBJECTIVE_FROM_GOAL_DOC>" \
  --domain <DOMAIN> \
  --goal-doc <GOAL_DOC_PATH> \
  --adapter-kind read_only_project_map_v0 \
  --adapter-status connected-read-only
```

`connect` 应创建或更新本地 registry/state，并把公开安全条目自动同步到
`~/.codex/loopx/registry.global.json`。

一个仓库可以承载多个同属项目 goal，如交付与低冲突验证通道。每个稳定
`goal_id` 运行一次 `connect`；保持一个共享 `.loopx/registry.json`，但每个 goal
使用一个活动状态：

```text
.codex/goals/<delivery-goal-id>/ACTIVE_GOAL_STATE.md
.codex/goals/<validation-goal-id>/ACTIVE_GOAL_STATE.md
```

不要为两个 goal id 复用同一个 `state_file`。`loopx registry` 把它视为健康
错误，且 `read-only-map` 检查所选 goal 自己的 `.codex/goals/<goal-id>/` 目录，
使一条健康通道不掩盖另一条通道缺失的状态。

如果 goal 状态或 registry 含私有证据，把 `.loopx/` 与 `.codex/goals/` 加到
该项目的 `.gitignore`。

对通用只读连接，创建首个非通用 map 运行：

```bash
loopx read-only-map --goal-id <STABLE_GOAL_ID>
```

它读取 registry 元数据、活动状态与有界项目文件清单，然后追加一个
`read_only_project_map` 运行。当 dashboard 否则会停留在 `state_refreshed` 或
`connected_without_run` 时，在编写项目特定适配器前使用它。

对计划的高复杂度适配器，在控制器 opt-in 前预览同一有界 map：

```bash
loopx read-only-map --goal-id <STABLE_GOAL_ID> --dry-run
```

如果适配器状态是 `planned`，只允许 `--dry-run` 预览，且结果应包含
`opt_in_required=true`。在用户或目标控制器把适配器移动到 `read-only-map-ready`、
`connected-read-only` 或 `connected` 前，不要追加真实 map。直接转达返回的
`residual_risks` 标签；不要虚构单独的任意风险摘要。

当用户或目标控制器回答 opt-in gate 时，在把命令交给另一项目 agent 前记录
该答案：

```bash
loopx operator-gate \
  --goal-id <STABLE_GOAL_ID> \
  --decision approve \
  --reason-summary "<PUBLIC_SAFE_CHINESE_REASON>" \
  --dry-run
```

使用 `approve`、`reject` 或 `defer`。干跑不写任何东西；真实追加创建
`operator_gate_*` 紧凑运行，使 `loopx status` 与 dashboard 能判断项目 agent 是否
可以运行已批准的命令。这不是人类奖励信号，也不授予写控制。

## 认定非平凡最终 Diff

在非平凡交付或合并前，检查当前 goal 配置。当 `change_quality_qualification.enabled`
为 true 时，加载 `loopx-change-quality` 并遵循其精确范围工作流：

```bash
loopx --format json change-quality prepare \
  --goal-id <STABLE_GOAL_ID> \
  --repo-path .
```

该政策保持两个决策分离：`safe_fix` 最多允许一次有界修复环节，而
`strict_receipt` 要求精确最终 diff 有通过 receipt。任何编辑使旧 fingerprint
失效。记录并验证最终 receipt，然后把 `--goal-id <STABLE_GOAL_ID>` 传给
`canary premerge`。

如果宿主无法加载 skills，把自包含 prepare 包用作评审契约。Turn 可以携带包或
receipt 引用，但它不拥有政策或强制。不要虚构 receipt、复用一个更旧 diff 的
receipt，或把主观风格建议变成 blocker。

## 非适配器工作后刷新状态

如果 agent 在未产生新适配器运行的情况下更新了 `ACTIVE_GOAL_STATE.md`、进度
ledger、规划文档或外部协调状态，追加一个仅状态刷新：

```bash
loopx refresh-state --goal-id <STABLE_GOAL_ID> --agent-id <REGISTERED_AGENT_ID>
```

对多 agent goal，保持通过 `quota should-run` 的同一 `--agent-id` envelope。
此默认是 agent 通道刷新。要更新 goal 级路由或持久 `## Next Action`，任何已注册
peer 可加 `--progress-scope goal`。

如果该刷新记录的是验证过的进度产物而非纯仅状态记录，包含公开安全分类与显式
交付提示，使 status、评审包与 quota 守卫不从分类名推断规模/结果：

```bash
loopx refresh-state \
  --goal-id <STABLE_GOAL_ID> \
  --classification <PUBLIC_SAFE_PROGRESS_CLASSIFICATION> \
  --delivery-batch-scale <ACTUAL_DELIVERY_BATCH_SCALE> \
  --delivery-outcome <ACTUAL_DELIVERY_OUTCOME> \
  --agent-id <REGISTERED_AGENT_ID> \
  --progress-scope goal
```

从当前验证过的轮次替换全部三个占位符。绝不因这些值会满足交付下限就默认或
提升较小/准备性轮次为 `multi_surface` / `outcome_progress`。

如果当前运行可能写入本地 LoopX 状态但其运行时边界禁止配置的外部 sink 写入，
保持 `explore_graph.enabled` 不变并加 `--suppress-external-sinks`。这保留规范
本地图投影、记录运行范围授权边界，并把 sink 摘要留给以后授权的刷新。不要
把 goal 级 Graph 设置视为外部写入边界的一次性变通。

把 `delivery_outcome` 用作机器 enum，而非散文：

- `surface_only`：docs、契约、冒烟、设置或准备移动了，但主要产品/用例结果
  没有。
- `outcome_gap`：该运行本应推进主要结果，却以具体 blocker 或缺失结果结束。
- `outcome_progress`：主要结果证据材料性推进，但所选阶段未完全完成。
- `primary_goal_outcome`：所选阶段的主要结果已完整、验证并写回。

不要依赖 `classification` 名称（如 `*_contract_v0_delivered`）承载此含义。
`classification` 是人类/历史标签；`delivery_outcome` 是 quota、status 与评审包
消费的控制面信号。

此修复陈旧 dashboard（最新运行仍显示旧 `ready_for_controller_opt_in` 或类似
状态）。它还自动把项目条目同步进全局 registry。如果不传 `--recommended-action`，
刷新运行应把 `## Next Action` 中的首个本地控制面条目发布为紧凑 dashboard 动作，
包括包装的续行。`recommended_action` 可以包含单个操作员需要的私有/本地路由
引用，但不得包含凭据、auth 头或内联机密；可共享/公开投影负责脱敏。

对复杂项目，不要把整个用户阅读队列塞进 `## Next Action`。把首个 Next Action
项保持为一条路由句，然后用 CLI 写显式复选框段落，而不是手工编辑段名：

```bash
loopx todo add \
  --goal-id <STABLE_GOAL_ID> \
  --role user \
  --text "Read the short review packet before approving delivery."

loopx todo add \
  --goal-id <STABLE_GOAL_ID> \
  --role agent \
  --text "Build the next read-only worksheet after the user decision is recorded."
```

CLI 在需要时创建规范段并避免精确重复 todo 文本。生成的 Markdown 形状是：

```md
## User Todo / Owner Review Reading Queue

- [ ] Read the short review packet.
- [ ] Record the owner decision in the worksheet.

## Agent Todo

- [ ] Build the next read-only worksheet after the user decision is recorded.
```

`loopx status` 把那些段提升到 `user_todos` 与 `agent_todos`。
Dashboard 用 `user_todos` 作首屏人类清单；项目 agent 应仅在 health、operator gate、
证据与 quota 允许执行后读取 `agent_todos`。

对非平凡功能工作，优先 todo 继任而不是额外生命周期状态。切片合并或验证时，
仅为 rollout、产品路径审计、docs、遥测、benchmark 证明或操作员决策创建下一个
具体 agent/user todo 后才完成当前 todo；如果确实没有跟进，在完成记录中写紧凑
无跟进理由。
等待普通人类评审的打开功能 PR 本身不阻塞进一步项目工作。用其验证过的 PR 证据
完成功能切片，用 `--next-user-todo ...` 与 `--next-user-task-class user_action`
推导评审提醒，并保留可运行 agent 继任者。为 PR 生命周期回读添加单独
`continuous_monitor`。仅对精确权限边界使用 `user_gate`，如把聚合实验分支合并进
`main`、发布、benchmark 启动、凭据或受保护生产动作。稳定实验集成分支可以收集
来自隔离 worktree 的功能 PR；把到 `main` 的聚合 PR 保留为最终评审 gate。
当下一 agent 切片尚不明确时，保持绑定的 `user_action` 可见而不把它变成 gate。
agent 前沿为空而有界无进展证据累积时，遵循 `autonomous_replan_required` 并
产出一个 typed 语义结果。如果投影前沿拥有具体目标，创建并认领该可运行 agent
todo，用 `--replan-obligation-id <exact-id>`、typed `--action-kind` 与稳定
`--target-key` 或 Explore 节点 ref 绑定到投影 `obligation_id`。原子 Todo 变更
是语义 receipt；不要加第二个修复 ACK。没有可执行目标时，用投影的 typed 语义或
覆盖支撑的终态写回，而不是创建任务只是重规划的 Todo。只有权威 typed 终态关闭
证据才能以显式无跟进替代该 Todo 写回。
`successor_todo_ids` 只记录谱系：链接继任者不会挂起打开的父级。把父级拆成显式
继任者时，决定父级是否仍有独立即时动作。没有时，用受支持的 `resume_when` 显式
推迟或完成它；不要仅从继任者链接推断聚合语义。把 `todo update` 响应中的
`parent_successor_advisory` 视为该决策的机器可读编写提醒，而不是新的持久
生命周期状态。

## 记录人类奖励

当用户对精确运行给出清晰奖励判断时，先验证 overlay 与活动状态写回：

```bash
loopx reward \
  --goal-id <STABLE_GOAL_ID> \
  --run-generated-at <RUN_GENERATED_AT> \
  --decision <DECISION_LABEL> \
  --reward positive \
  --reason-summary "<PUBLIC_SAFE_CHINESE_REASON>" \
  --follow-up "<PUBLIC_SAFE_NEXT_ACTION>" \
  --write-active-state-summary \
  --dry-run
```

仅当用户明确批准记录奖励后，再去掉 `--dry-run` 重跑。持久真相源仍是运行绑定
的 `human_reward` overlay。活动状态写回是供未来 agent 的 `Progress Ledger`
摘要；项目 agent 应通过返回的 `project_agent_visibility.history_command` 读取
奖励。

## 多项目状态

项目内：

```bash
loopx status
```

在保留全局健康字段的同时聚焦一个 goal 的状态投影，传 goal id：

```bash
loopx --format json status --goal-id <STABLE_GOAL_ID>
```

项目外，`loopx status` 应回退到：

```text
~/.codex/loopx/registry.global.json
```

仅诊断或恢复时使用显式同步：

```bash
loopx sync-global
```

如果 status 显示 `unregistered_runtime_goal`：

- 项目活跃时，运行 `loopx sync-global` 或从该项目的本地 registry 重连。
- 运行时记录过时时，预览 `loopx archive-runtime --goal-id <GOAL_ID>` 清理，
  仅在明确意图时执行清理。

## 验证

connect 或 refresh 后，运行最小有用集：

```bash
loopx registry
loopx status
loopx check --scan-path <PUBLIC_SAFE_FILE_OR_DIR>
```

对多项目 UI 更新，从全局 registry 刷新 dashboard 状态 JSON：

```bash
loopx --registry "$HOME/.codex/loopx/registry.global.json" \
  --format json status > <dashboard>/public/status.local.json
```

## 报告

用户评审时用中文报告：

- 变更文件及其是公开还是本地私有；
- 验证命令与结果；
- goal 在 dashboard 或 attention queue 中的呈现方式；
- 下一个安全动作；
- decision-advisor 或 write-controller 行为前的任何缺失 gate。

绝不在公开仓库 docs 或示例中包含凭据、私有 docs、原始内部链接、生产任务 id
或原始本地证据。