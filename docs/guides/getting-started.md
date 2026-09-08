# 开始使用 LoopX


本指南承载原先放在仓库根 README 中的运维细节。根 README 现在是简短的产品落地页；
本页是安装、项目连接、诊断、heartbeat、dashboard 使用、开发检查与命令发现的
实操路径。

如果你初次接触 LoopX，从更短的[新手命令路径](newcomer-command-path.md)开始：
它把产品界面收敛到宿主 LoopX task 入口、项目连接与一条手动 CLI 快速开始。
本页保留完整的操作者与贡献者细节。

对于精选学习路径，先看[开发者手册](/loopx/docs/book/)，再进入完整指南。

## Codex App 与其他 Agent 设置

如果你已经在用 Codex、Claude Code、Cursor 或其他终端 Agent，在它已工作于项目根
的情况下粘贴以下内容：

非 Codex Agent 的兼容性检查：Agent 界面至少需要一个控制 hook 供 LoopX 驱动，
例如 shell/CLI 执行、goal/task 命令、自动化或 heartbeat hook，或它自己的
loop/scheduler。没有这些时，请改用手动 shell 命令；LoopX 可以保留项目状态，
但无法让 Agent 自动继续。

```text
Connect the current project to LoopX.
Do not clone the LoopX repository for ordinary use. If `loopx` is not on PATH,
install it from PyPI with Python 3.11+:
python3 -m pip install --upgrade loopx
loopx workflow-skills --install

Then run `loopx doctor`. Work only from the current project root:
1. If LoopX state already exists, reuse it and do not create or overwrite a
   goal or the active objective.
2. If the project is not connected, prefer `loopx connect`; use
   `loopx bootstrap` only when project state clearly needs initialization.
3. Ensure `.loopx/`, `.codex/goals/`, and `.local/` are ignored.
4. Set up the thin LoopX heartbeat for this surface. For Codex App, start the
   recurring automation at 3 minutes, then follow
   `quota should-run.scheduler_hint` for backoff and self-stop behavior.
5. Stop after setup and report the active state id, current user gate, top
   agent todo, and next safe action.

Do not commit `.loopx/`, `.codex/goals/`, `.local/`, live ACTIVE_GOAL_STATE
files, runtime registries, raw logs, credentials, or private local paths. Do
not start longer delivery work in this setup turn.
```

要获得更长的生成式交接 prompt，安装一次并运行：

```bash
loopx new-project-prompt \
  --project /path/to/your-project \
  --goal-doc /path/to/your-project/GOAL.md
```

该命令输出应粘贴进 Codex 或 Claude Code。它包含新项目的完整 guard、quota、todo
与 heartbeat 协议。

成功的样子：

- `loopx doctor` 通过；
- 项目有 `.loopx/registry.json`；
- 项目有 `.codex/goals/<goal-id>/ACTIVE_GOAL_STATE.md`；
- `loopx status` 显示 goal 与下一步应行动者；
- 本地 runtime 状态被忽略，不被提交。

## 命令 Skill 注册

安装器还为能发现用户安装 skills 的宿主界面注册 LoopX 命令家族：

- Codex CLI / App：`~/.codex/skills/loopx*` 下的显式 LoopX 命令 facade
  skills。Codex 目前不支持用户定义的原生顶级 `/loopx` slash command，因此通过
  `$loopx` 或 `/skills` 调用项目命令。主 `LoopX` 命令 facade 与 `LoopX Project`
  workflow skill 是两个独立条目：命令 facade 设置 `allow_implicit_invocation: false`，
  而 `loopx-project`、`loopx-pr-program`、`loopx-pr-review` 等更丰富的 workflow
  skills 保持正常隐式行为。
- Claude Code：`~/.claude/skills/loopx*` 下的轻量用户 skills，因此命令家族可以
  作为 Claude Code slash command 出现，而无需启用 opt-in MCP/hook adapter。
- OpenCode：`~/.config/opencode/commands/` 下的静态命令文件在重启后暴露原生
  `/loopx` slash command。可执行 goal bridge（受 LoopX quota 门控的定时空闲延续）
  需要显式 `--with-goal-bridge` 安装。包装的 goal runtime 将私有重启状态放在每个
  项目的 `.opencode/goals/` 下；使用持久 bridge 前将该目录加入项目忽略规则。
- OpenCode 2：同一批静态命令文件服务于 OpenCode 2，goal loop 通过持久的
  `loopx opencode2-goal-worker` 进程运行，该进程通过 OpenCode 2 HTTP API 驱动
  会话并拥有 loop 定时器，因此长 run 在 TUI 关闭后仍然存活。OpenCode 1 plugins
  不能在 OpenCode 2 下运行；见 `loopx/opencode2_goal_mode/README.md`。
- Pi：`.pi/extensions/loopx-goal.ts` 下的自包含 goal extension（其 loop core 在
  `.pi/extensions/pi-goal-loop-runtime.mjs`）在重启后暴露 `/loopx`，并通过
  `loopx_goal_activate` 运行 quota 门控 goal loop。它通过
  `loopx slash-commands --install --surface pi` 显式安装（传 `--pi-project <path>`
  可从其他目录指向另一项目）；私有绑定状态留在每个项目的 `.loopx/pi/` 下
  （已通过 `.loopx/` 纳入 gitignore）。

命令家族在各界面间相同，即使宿主专属入口不同：

| 命令家族 | 宿主入口 | CLI 回退 |
| --- | --- | --- |
| 项目 goal 启动 | 宿主暴露原生 slash command 时的 `/loopx <goal text>`；使用显式 skills 的 Codex 界面中的 `$loopx <goal text>` 或 `LoopX` 命令 skill。 | `loopx start-goal --guided --project . --goal-text "<goal text>" --host-surface <exact-host>` |
| 全局管理器视图 | `/loopx-global-summary`、`/loopx-global-gates`、`/loopx-global-todos`、`/loopx-global-risks`。 | `loopx slash-commands`，然后运行列出的全局管理器命令获取所需视图。 |
| PR 评审队列 | `/loopx-pr-review`。 | `loopx pr-review` |

把 slash 或 skill 入口当作 UI 便利。CLI 始终是事实来源，恢复应使用 CLI 而不是
发明第二条状态路径。如果升级后命令消失，先检查并刷新已注册的命令文件：

升级后刷新这些文件，运行：

```bash
loopx slash-commands
loopx slash-commands --install
```

该命令更新 LoopX 拥有的文件，包括带已知遗留签名的旧 LoopX 生成文件。如果同名
文件没有 LoopX 管理标记或遗留签名，LoopX 保持不动并报告 `skipped_user_file`。

如果项目本地 goal 命令仍无法通过宿主调用，从项目根运行等效的引导启动预览：

```bash
loopx start-goal --guided --project . --goal-text "<goal text>" \
  --host-surface codex-cli-tui
```

这保留了 `/loopx <goal text>` 语义，同时把变更置于 Agent 控制之下：保留确切
任务文本，检查或连接状态，在 todo 写回前规划，刷新状态，激活正确宿主 loop，
运行 `quota should-run`，且仅在 guard 允许时继续。需要更底层交接包的宿主与插件
集成可以使用 `loopx bootstrap-command-pack --project . --goal-text "<goal text>"`。
全局管理器或 PR 评审命令使用 `loopx slash-commands` 打印当前规范命令列表与回退
CLI 形态。

对应宿主使用 `codex-app`、`codex-app-ssh`、`codex-cli-tui`、`opencode` 或
`opencode2`。当桌面 App 通过 SSH 附加到远程工作区且其自动化工具不可用时使用
`codex-app-ssh`；LoopX 将生成可见 `/goal` 任务。确切宿主未知时，省略
`--host-surface` 一次：LoopX 返回带精确重跑命令的只读选择 gate，且不写项目状态。
这防止升级把终端启动静默路由到桌面 App heartbeat。

## 本地状态备份

在进行有风险迁移、本地调度器变更或发布安装修复之前，预览状态归档：

```bash
loopx backup-state --project .
```

只在预览正确时写入归档：

```bash
loopx backup-state --project . --execute
```

备份默认写入 `~/.codex/loopx/backups`。它捕获共享 LoopX runtime root、Codex App
自动化、已安装的 `loopx-*` skills、当前项目状态，以及每个可达项目的 `.loopx`、
`.codex/goals`、`.claude/goals`、`.local/goals`、registry 声明的活动状态与从全局
registry 发现的 source registry。缺失或过期的项目路由在 manifest 中保持可见。
仅当刻意需要窄归档时使用 `--current-project-only`。把归档与 manifest 当作私有本地
恢复材料；不要提交或发布其内容。

预览报告的是**压缩前的逻辑源字节**，不是最终归档占用。完整 runtime 历史与项目
本地 goal 证据有意包含在内，使归档能支撑忠实回滚。分类明细显示哪个界面贡献了
字节，而重叠目标识别确切的恢复目标，例如同时被父项目目录覆盖的活动状态或
source-registry 文件。`--execute` 后，用 `archive_size_bytes` 与归档/逻辑比率判断
实际存储成本。

## Codex CLI TUI 设置

对 Codex CLI 用户，产品目标是：在 Codex TUI 启动，发送一条 LoopX 设置消息，
让 Agent 安装或复用 LoopX、连接项目，并在当前 gate/todo/next-action 报告处停止。
作为该设置的一部分，Agent 把当前 Codex goal 设为细心跳 prompt，让用户立即感到
Loop 在运行。此后，只要 CLI 暴露安全会话附加原语，自动化就应保持在该 TUI 可见
且可中断。首次运行路径不应要求你理解 registry 路径、runtime root、JSON 载荷、
会话文件或 heartbeat prompt 语法。

首次运行路径：

```text
Connect this repo to LoopX from this visible Codex CLI TUI. Do not clone the
LoopX repository for ordinary use. If `loopx` is not on PATH, install it from
PyPI with Python 3.11+:
python3 -m pip install --upgrade loopx
loopx workflow-skills --install

Then run `loopx doctor`. Work only from this project root: if LoopX state
already exists, reuse it and do not create or overwrite a goal or the active objective; if the project
is not connected, prefer `loopx connect`, and use `loopx bootstrap` only when
project state clearly needs initialization. Ensure `.loopx/`, `.codex/goals/`,
and `.local/` are ignored. Keep me in this TUI, do not use hidden headless
execution. After the project is connected, generate the thin heartbeat prompt
and set the current Codex CLI task body with `/goal <thin task_body>`. Then
stop and report the active state id, current user gate, top agent todo, and
next safe action.
```

生成的粘贴块是 App 上手体验的"先设置"改写，而不是 heartbeat body 本身。第一个
有用的响应应在更长交付工作之前显示当前状态 id、存在的具体用户 gate、任何顶层
用户 todo、顶层 agent todo 与下一个安全动作。除非用户明确要求在设置回合做交付，
否则设置回合不应为交付花费 quota。Agent 仍应在设置期间生成
`heartbeat-prompt --thin` 并把该 body 安装进界面：Codex CLI 得到
`/goal <thin task_body>`，而 Codex App 得到从 3 分钟开始并随后遵循
`scheduler_hint` 的 heartbeat 自动化 body。

一旦 `loopx` 安装完成，生成更严格的仓库专属设置消息：

```bash
loopx codex-cli-bootstrap-message --project . --goal-id <goal-id>
```

保持它作为优先交互路径：人在 Codex CLI TUI 中观看并引导，而 LoopX 拥有
quota/status/todos/gates/writeback。生成的包还显示无 clone 安装修复命令、bootstrap
后细 prompt 生成命令与无记录验证清单，这样新仓库路径无需接触原始 Codex 会话数据
即可评审。

如果用户只想要可粘贴的 TUI 文本，省略 wrapper：

```bash
loopx codex-cli-bootstrap-message --project . --goal-id <goal-id> --message-only
```

要在不运行 Codex 的情况下评审整个单消息 Loop 契约，生成试点包：

```bash
loopx codex-cli-one-message-loop-pilot --project . --goal-id <goal-id> --agent-id <agent-id>
```

该试点把首条 TUI 粘贴消息与后续 `codex-cli-local-scheduler-exec` bridge 联系起来。
它默认保持 dry-run，面向验证路径的操作者/贡献者，不是首次用户的先决条件。

要在不接触真实 Codex 会话的情况下评审回归用户本地驱动器 loop，生成可见
local-driver 试点包：

```bash
loopx codex-cli-visible-local-driver-pilot --project . --goal-id <goal-id> --agent-id <agent-id>
```

这保持首条消息 TUI 启动为主路径，然后把后续调度器 tick、可见证明、空闲 guard、
受限执行、阻塞写回与无记录边界建模为公开安全元数据。

后续 Turn 规则有意比首条消息更严格：只有公开安全可见证明、runtime 空闲证据、
新鲜 guard 与显式执行边界齐备后，LoopX 才能添加可见引导 Turn。没有该证明时，
驱动器应写入紧凑阻塞，或把单消息设置 bootstrap 保持为产品路径。

以下命令是设置路径可用后的可选自动化检查。要在不接触记录或会话文件的情况下
评估未来同会话自动化支持，运行：

```bash
loopx codex-cli-session-probe
```

要在不改变 Codex 会话的情况下把该探测转为 dry-run 驱动器决策，运行：

```bash
loopx codex-cli-visible-driver-plan --project . --goal-id <goal-id>
```

要用一个包查看完整本地自动化设置计划，包括 quota guard、visible-driver 决策、
TUI bootstrap 命令、无 headless 边界与 idle-guard 要求，运行：

```bash
loopx codex-cli-local-driver-plan --project . --goal-id <goal-id> --agent-id <agent-id>
```

这仍只限 dry-run。它不运行 Codex、不读记录、不读会话文件、不改变会话、不花费
quota。

当驱动器计划说 `resume [PROMPT]` 或 `remote-control` 可能支持可见同会话路径时，
先验证公开安全证明夹具再把该路径当作自动化：

```bash
loopx codex-cli-visible-session-proof \
  --project . \
  --goal-id <goal-id> \
  --agent-id <agent-id> \
  --proof-fixture visible-proof.public.json
```

夹具应只包含布尔值与公开安全标签，证明用户 opt-in、quota guard、idle guard、
可见 Turn、可中断性、不读记录或会话文件，以及紧凑写回规划。

默认的 Codex CLI"先设置后 `/goal`"产品路径不提供 headless 回退。为兼容性，旧
交接命令只报告禁用边界并指回 message-only TUI bootstrap：

```bash
loopx codex-cli-exec-handoff --project . --goal-id <goal-id>
```

参见 [Codex CLI TUI-first loop](../product/runtimes/codex-cli/codex-cli-tui-loop.md)
契约，了解 bootstrap、会话附加自动化与无 headless 边界。
[Codex CLI first-run rehearsal](../product/runtimes/codex-cli/codex-cli-first-run-rehearsal.md)
把最短用户路径留在同一个地方：无 clone 安装、单消息设置 bootstrap 与后续自动化的
证明捕获夹具。当前产品调度上，
[Codex CLI TUI continuation priority](../product/runtimes/codex-cli/codex-cli-tui-continuation-priority.md)
在两者都可运行时，让同 TUI 延续优先于 frontstage 或 showcase 打磨。

维护者可以用以下命令验证公开全新 clone 路径：

```bash
python3 examples/fresh-clone-quickstart-smoke.py
```

## 安装与升级

不 clone 仓库，从 PyPI 安装当前发布：

```bash
python3 -m pip install --upgrade loopx
loopx workflow-skills --install
loopx doctor
```

wheel 包含 CLI 与可复用 LoopX workflow skills。
`workflow-skills --install` 把这些 skills 落地到 `~/.codex/skills` 并写入 revision
readback。首次安装后重启宿主，让它重新加载它们。受管环境、宿主界面、回滚与归档
回退细节见[安装 LoopX](installing-loopx.md)。

对 PyPI 安装，升级包然后从同一发行版刷新宿主材料：

```bash
python3 -m pip install --upgrade loopx
loopx workflow-skills --install
loopx slash-commands --install
loopx doctor
```

GitHub Pages 归档安装器仍作为回退可用。`loopx update` 现在投影活动安装 owner：
PyPI 环境保持包管理器拥有，归档快照保持 LoopX 拥有，活动源码 checkout 保持 Git
拥有。

## 贡献者安装

要开发 LoopX 本身或测试在线 canary wrapper 时，安装一个共享本地 checkout：

```bash
git clone https://github.com/huangruiteng/loopx ~/loopx
~/loopx/scripts/install-local.sh
loopx doctor
```

checkout 安装器创建：

- `~/.local/bin/loopx`，指向稳定本地发布快照；
- `~/.local/bin/loopx-canary`，指向在线 checkout；
- `~/.local/share/man/man1/loopx.1.gz`，使 shell profile 重载后 `man loopx`
  打开简短操作者手册；
- `~/.codex/skills` 下可复用的全局 LoopX Codex skills；
- 项目级 skills 的规范来源，它们不全局安装。

这些全局 skills 是可复用 LoopX 连接与控制面行为的预期产品界面。只应存在于所选
仓库的能力 workflows 改用受管项目 skills。项目专属状态与私有决策留在本地 registry
与活动 goal 文件中。

在把 checkout 晋升为默认本地发布前，先用 canary wrapper 运行一两个选定的
控制器。

## 全局 Skill 安装、更新、修复与清理

`scripts/install-local.sh` 管理三个可复用本地界面：

- `~/.local/bin` 下的 CLI wrappers；
- `~/.local/share/man` 下的本地手册页；
- `~/.codex/skills` 下的 LoopX Codex skills。

使用命名更新动作，让只读检查与变更可见：

```bash
loopx update check
loopx update plan
loopx update apply
```

在 PyPI 安装上，apply 使用拥有它的 pip 或 pipx 环境，然后刷新宿主材料与
readbacks。在归档安装上，它原子替换发布快照。该命令绝不 pull 或改写在线 checkout；
显式更新 Git 并重跑贡献者安装器。

对贡献者 checkout，重跑安装器从当前干净的 `origin/main` checkout 更新两个界面：

```bash
cd ~/loopx
git pull --ff-only
./scripts/install-local.sh
loopx doctor
```

安装器把默认晋升当作发布边界。干净 checkout 位于 `origin/main` 时自动晋升。
脏 checkout 或另一分支只更新 `loopx-canary`，而默认 CLI、已安装 skills 与手册
保持不动。验证该 checkout 后，显式晋升：

```bash
LOOPX_PROMOTE_DEFAULT=1 ./scripts/install-local.sh
```

发布 manifest 与 `loopx doctor` 记录晋升来自 trusted-main 路径、受信 GitHub 归档
还是显式覆盖。

在把在线 checkout 变成默认发布快照之前，用 `loopx-canary` 测试。`loopx doctor`
报告默认 wrapper 是否指向发布快照、canary wrapper 是否指向在线 checkout，以及
所需 skills 是否已安装。

如果某 Agent 说它找不到 LoopX，按此顺序修复：

1. 确保 `~/.local/bin` 在 `PATH` 上。
2. 在干净的 `origin/main` 上重跑 `~/loopx/scripts/install-local.sh`；从任何其他
   checkout 使用 `loopx-canary`，直到显式晋升。
3. 运行 `loopx doctor`。
4. 如果循环自动化过期，用
   `loopx heartbeat-prompt --thin --goal-id <goal-id> --agent-id <agent-id> --agent-scope "<scope>"`
   重新生成。

可复用 skills 有意只做狭窄工作：

| Skill | 用它做 | 不要用它做 |
| --- | --- | --- |
| `loopx-project` | 连接项目、读取 status/quota/history、诊断 LoopX、生成 heartbeat/review 包与刷新状态。 | 默认读取私有项目文档或取代 CLI 作为事实来源。 |
| `loopx-pr-program` | 协调多 PR/MR 交付项目、保留需求/依赖优先级、维护路线图与监控材料变更。 | 深度逐 PR 评审、provider 专属获取、批准、评论、重定向、关闭或 merge。 |
| `loopx-pr-review` | 运行 `/loopx-pr-review`、保留 `loopx pr-review` 包与引导逐 PR 五区块评审。 | 批准、评论、merge、自 merge 或管理员绕过 PR。 |
| `loopx-doc-registry` | 注册持久项目材料与脱敏的权威来源元数据。 | 把原始 doc 正文、内部 URL 或私有评论复制进公开仓库 docs。 |
| `loopx-benchmark` | 通过内置 `benchmark-toolkit` 契约运行、监控与分析 LoopX 管理的 benchmark 实验。 | 随意讨论 benchmark、普通微基准测试，或把 skill 发现当作 runner、凭证或私有证据权威。 |
| `loopx-material` | 运维一个显式激活项目的无损材料清单、生命周期、ranked-entry 重建、有界 rerank、owner 门控应用与回滚。 | 普通一次性阅读、项目专属来源发现，或只因项目 skill 可被发现就改动材料存储。 |
| `loopx-change-quality` | 评审一个确切最终 diff，可选应用一个有界安全修复，并记录策略强制 receipt。 | 在 goal 策略禁用时行动、递归评审评审者，或取代项目原生验证器。 |
| `loopx-self-repair` | 修复意外的控制面行为、过期投影、微小 Turn 或矛盾 guard 载荷。 | 降低 gate、在缺失权威周围猜测，或提交私有 runtime 状态。 |

当一个交付 goal 横跨多个 PR 或 MR 且队列需要长期协调时，调用 `$loopx-pr-program`。
该 skill 接受 provider-neutral 快照、保留一个分组的 LoopX monitor，且仅对材料
变更更新路线图投影。运行 `loopx doctor` 读回已安装 skill，并用其捆绑的
`scripts/diff_snapshot.py --current <snapshot.json>` 命令验证首个基线。安装该 skill
不授予源码控制读或写权限，不安装 provider adapter；获取仍由授权宿主环境负责。
要禁用该 workflow，停止调用它并只移除 `~/.codex/skills/loopx-pr-program`；重跑
安装器恢复发布拥有的副本。

Auto-research 角色指引是 worker 本地的：可见 worker launcher 在投影角色 profile、
quota 包与 frontier 条目后拥有 `loopx-auto-research` playbook 本身。它不是作为
全局 LoopX skill 安装的。

保持三层分离：

- **全局 skill 行为**归 `skills/`，安装到 `~/.codex/skills`。
- **项目状态**归 `.loopx/`、`.codex/goals/` 与 `~/.codex/loopx`；除非有意提交
  脱敏夹具，否则保持本地。
- **仓库规则**归 `AGENTS.md`、`CONTRIBUTING.md` 与公开 docs。它们可以约束本仓库
  的贡献者与 Agent，但不应静默成为每个项目的全局 skill 策略。

`loopx-material` 与 `loopx-change-quality` 遵循**发布拥有来源、项目管理交付、
goal 限定激活**。全局安装器把它们放在 LoopX 发布中的规范来源，但不把任一 skill
发布到 `~/.codex/skills`。通用生命周期与宿主界面契约记录在
[Project Skill Delivery](../../loopx/capabilities/project_skill_delivery/README.md)。
仅为一个已连接项目启用发现：

```bash
loopx project-skill install \
  --project . \
  --skill loopx-material \
  --surface codex \
  --execute
loopx project-skill status \
  --project . \
  --skill loopx-material \
  --surface codex

# Install only when the goal enables change_quality_qualification.
loopx project-skill install \
  --project . \
  --skill loopx-change-quality \
  --surface codex \
  --execute
```

宿主原生项目根：

| 界面 | 受管项目根 |
| --- | --- |
| Codex | `.agents/skills/` |
| Claude Code | `.claude/skills/` |
| OpenCode | `.opencode/skills/` |

重复 `--surface` 可在一次事务中为多个宿主安装同一 skill。位置遵循
[Codex](https://developers.openai.com/codex/skills)、
[Claude Code](https://code.claude.com/docs/en/slash-commands#where-skills-live)
与 [OpenCode](https://opencode.ai/docs/skills/#place-files) 文档化的宿主发现契约。

安装项目 skill 不授予领域写权限；当前 goal/profile/todo 必须仍激活该能力。用
`loopx project-skill uninstall --project . --skill <skill-id> --surface codex
--execute` 移除受管副本。未受管或本地修改的副本 fail closed。

只断开当前项目与 LoopX 的连接时，从该项目根使用项目本地卸载命令。它默认 dry-run
预览，拒绝直接操作共享全局 registry：

```bash
loopx uninstall-project
loopx uninstall-project --goal-id <goal-id> --archive-state --execute
```

仅当全局条目的 `source_registry` 指回该项目时，`uninstall-project` 才把所选 goal
从 `.loopx/registry.json` 与共享全局 registry 中移除。它不卸载 LoopX CLI，不删除
其他项目的 runtime 历史。传 `--archive-state` 可把该项目
`.codex/goals/<goal-id>/` 目录移到 `.loopx/archived-project-state/` 下，而不是留在
原位。

手动清理可复用 LoopX CLI 与 skill 界面时，只移除你打算丢弃的部分：

```bash
rm -f ~/.local/bin/loopx ~/.local/bin/loopx-canary
rm -rf ~/.codex/skills/loopx-project \
       ~/.codex/skills/loopx-pr-program \
       ~/.codex/skills/loopx-pr-review \
       ~/.codex/skills/loopx-doc-registry \
       ~/.codex/skills/loopx-benchmark \
       ~/.codex/skills/loopx-self-repair
```

这不归档已连接项目状态或 runtime 历史。仅当你有意退役这些本地项目记录时才归档
或移除 `.loopx/`、`.codex/goals/` 与 `~/.codex/loopx`。

## 手动连接项目

从项目仓库：

```bash
cd /path/to/your-project
loopx bootstrap \
  --goal-id your-project-goal \
  --objective "Improve this project through bounded, verified goal segments." \
  --goal-doc GOAL.md
```

`connect` 是 `bootstrap` 的别名：

```bash
loopx connect --goal-id your-project-goal
```

这会创建或连接：

```text
your-project/
  .loopx/registry.json
  .codex/goals/your-project-goal/ACTIVE_GOAL_STATE.md

~/.codex/loopx/
  goals/<goal-id>/runs/
```

把在线目标状态与 registry 当作本地 runtime 数据。提交前把这些路径加入已连接项目的
`.gitignore`：

```gitignore
.loopx/
.codex/goals/
.opencode/goals/
goals/**/ACTIVE_GOAL_STATE.md
```

只提交脱敏的模板或示例，不要提交控制器的在线 `ACTIVE_GOAL_STATE.md`。

## 从你的 Agent 诊断

用户不应需要手动运行诊断命令。问你的 Codex、Claude Code、Cursor 或终端 Agent：

```text
Diagnose LoopX for this project end to end. Do not ask me to run shell
commands.

If `loopx` is missing, install or repair it first. Then run
`loopx diagnose` yourself, read the diagnostic packet, and use your own
reasoning to tell me:
- whether this project can currently self-drive;
- what evidence supports that answer;
- what is blocking it, if anything;
- the exact question I need to answer, if a user/controller gate exists;
- what you will do next.

Do not treat LoopX machine signals as the final verdict. They are
evidence for your diagnosis.
```

`loopx diagnose` 有意做成面向 Agent 的证据包。它收集紧凑 `status`、
`quota should-run`、todo、interaction-contract 与边界信号，然后给 Agent 一份推理
清单。诊断由 Agent 用自然语言完成。

要在连接真实仓库前试用 LoopX，创建一个一次性 demo goal：

```bash
export PATH="$HOME/.local/bin:$PATH"
loopx demo
```

预期首次运行信号：

- 输出包含 `ok: True`；
- 在 `/tmp/loopx-demo` 下创建了项目本地 registry 与活动目标状态；
- 可见一个用户 todo 与一个 agent todo；
- `refresh-state` 追加了一个紧凑 run；
- `quota should-run` 返回 `should_run=True` 与 `state=eligible`。

检查 demo：

```bash
cd /tmp/loopx-demo
loopx status
loopx quota should-run --goal-id demo-goal
loopx history --goal-id demo-goal
```

## 日常工作流

检查安装与 registry 健康：

```bash
loopx doctor
loopx registry
loopx check --scan-root .
```

读取状态与历史：

```bash
loopx status
loopx history --goal-id your-project-goal
```

添加显式工作：

```bash
loopx todo add \
  --goal-id your-project-goal \
  --role user \
  --text "Review the owner checklist."

loopx todo add \
  --goal-id your-project-goal \
  --role agent \
  --text "Summarize the safe read-only evidence." \
  --task-class advancement_task \
  --action-kind evidence_summary
```

完成一个 agent todo 并原子添加下一个可执行项：

```bash
loopx todo complete \
  --goal-id your-project-goal \
  --todo-id todo_ab12cd34ef56 \
  --evidence "Validated with examples/demo-cli-smoke.py" \
  --next-agent-todo "Run the next bounded validation slice." \
  --next-task-class advancement_task \
  --next-action-kind validation \
  --execute
```

在本地状态或 docs 变更后追加仅状态刷新：

```bash
loopx refresh-state --goal-id your-project-goal
```

为 Agent 生成紧凑交接包：

```bash
loopx review-packet --goal-id your-project-goal
```

记录操作者 gate 决策或 run 边界奖励：

```bash
loopx operator-gate \
  --goal-id your-project-goal \
  --decision approve \
  --reason-summary "Approve read-only map opt-in"

loopx reward \
  --goal-id your-project-goal \
  --decision continue_route \
  --reward positive \
  --reason-summary "validation improved and the route is worth extending"
```

### 恢复历史索引碰撞

历史写入器原子保留其 JSON/Markdown artifact 对。如果旧 runtime 报告遗留索引身份
碰撞，在改动索引前评审完整重建计划：

```bash
loopx --format json history rebuild-index-collisions \
  --goal-id your-project-goal | jq '.review_plan' > reviewed-plan.json
loopx history rebuild-index-collisions \
  --goal-id your-project-goal \
  --review-plan-json reviewed-plan.json \
  --execute
```

执行路径要求确切评审计划、保留重建前索引备份，并保留有歧义的遗留 artifact 而
不是猜测其 owner。截断的计划不可执行；先抬高 `--limit` 并评审完整摘要。

## Heartbeat 与 Quota

Quota 是计算资格，不是策略。它回答自动 Turn 现在能否运行，以及允许哪种 Turn。

```bash
loopx quota status
loopx quota plan
loopx quota should-run --goal-id your-project-goal
```

`quota plan` 报告的 `next_automatic_turn` 只是建议性调度提示：它选择最高计算的
合格 goal，而 operator-gated、focus-waiting、waiting、throttled、paused 与
health-blocked goals 留在合格 lane 之外。

`quota should-run` 返回 heartbeat 应遵循的机器契约：

- `should_run`：交付工作现在能否运行；
- `waiting_on`：user、controller、Codex、外部证据、health 或 quota；
- `work_lane_contract`：下一个可执行 lane 或 monitor/blocker lane；
- `execution_obligation`：Agent 是否必须尝试一个有界片段；
- 用户与 agent todo 摘要；
- 启用时的安全绕过或自修复提示；
- 精确花费策略。

Agent todo 摘要把 `first_executable_items` 与 `monitor_open_items` 分开：可执行项
驱动所选 goal 的主动作，而 monitor 项作为补充观察上下文保持可见，且只在产生
材料迁移或阻塞时花费计算。

Registry 条目可以暴露逐 goal `control_plane` 策略。例如
`control_plane.self_repair.enabled=true` 让 `quota should-run` 为可修复的控制面
停滞返回有界 `decision=self_repair` 契约；缺失策略时默认为关闭，因此其他 goal
保持正常 skip 或 wait 行为。

如果 `quota should-run` 返回 `gate_prompt` 或 `operator_question`，目标 heartbeat
应主动询问那个具体用户/控制器 gate。如果存在开放用户 todo，在它们保持开放时
不要把该 Turn 称为"无新用户动作"；其报告仍必须列出已有的开放用户 todos。

当 `safe_bypass_allowed=true` 时，heartbeat 仍可执行一个与受阻 gate 无关的有界
只读引导或分析步骤。完整分配契约见
[quota allocation](../quota-allocation.md)。

在自动 Turn 实际花费交付计算后，追加一个花费事件：

```bash
loopx quota spend-slot \
  --goal-id your-project-goal \
  --slots 1 \
  --source heartbeat \
  --execute
```

不要为安静的 `should_run=false` skip、preflight 失败或纯 dry-run 预览追加花费。

生成受 guard 的 Codex App heartbeat body。首次运行 Codex App 上手应在 3 分钟
bootstrap 节奏安装该 body，除非用户明确要求其他间隔；后续等待应遵循
`quota should-run.scheduler_hint`：

```bash
loopx heartbeat-prompt --thin --goal-id your-project-goal
```

对共享控制面 Agent，在自动化 prompt 中传入身份与范围，然后让 Agent 用注册的
`--claimed-by` id 软认领匹配 todos：

新上手默认使用新身份。当 `agent-onboard` 或带参数的 `start-goal --guided` 调用
没有 `--agent-id` 时，在写入 todos 前遵循其新 Agent 注册预览/应用命令。仅当用户
明确要求接管那个确切 Agent 时才复用现有 id；存在单个已注册 Agent 不是接管意图。
新路径使用 `--require-new`；其预览是建议性的。仅当执行结果报告 `ok=true`、
`changed=true`、`written=true`、成功全局同步与已验证 source/global 注册 readback
后才继续，这样过期预览或 id 碰撞不会变成隐式接管。

```bash
loopx register-agent --goal-id your-project-goal \
  --agent-id codex-main-control \
  --agent-id codex-side-bypass \
  --execute

loopx heartbeat-prompt --compact --goal-id your-project-goal \
  --agent-id codex-side-bypass \
  --agent-scope "control-plane coordination"
```

一旦设置 `coordination.registered_agents`，不带 `--agent-id` 调用
`heartbeat-prompt` 会 fail closed；这让过期的 Codex App 自动化暴露升级错误，而不是
在无身份或无范围的情况下静默运行。没有 `coordination.registered_agents` 的旧 goal
registry 在 scoped heartbeat 或 todo claim 点名 agent 时也 fail closed；先注册
agent 身份，而不是让 worker 发明 claim id。
对 hierarchy 时代的 registry，下一次 `quota should-run` 与 `upgrade-plan` 返回
稳定的 peer-runtime 迁移 id、每个已注册 peer 一条 heartbeat 命令，以及一条完成
命令。用该迁移 id 幂等更新已安装自动化，然后运行一次完成命令。重复同一完成
ack 是 no-op，之后的 quota 检查不再投影已完成的迁移。

`register-agent` 解析既有全局条目的 `source_registry`，写入项目本地事实来源，然后
同步共享全局投影。如果 `~/.codex/loopx/registry.global.json` 不可写，命令在改动
source registry 前失败并报告 `global_registry_write_denied` 健康错误。修复共享
runtime 权限，或从可写 LoopX runtime root 的宿主运行，然后重跑命令。仅当你有意
要显式纯本地连接时使用 `--no-global-sync`。

已注册 Agent 使用 `agent_model=peer_v1`：没有身份是持久 leader。Todo claim 或任务
lease 选择当前 owner。写仓库的 peer 在任务或 goal 策略要求时使用独立 worktree，
且 `workspace_guard` 在缺少该隔离时 fail closed。小的符合 AGENTS 的已验证变更可在
显式 LoopX 证据下自 merge。更高风险工作应创建独立后继或带 `action_kind=review`
的常规 `independent_handoff`；仅当必须强制执行者分离时使用 `excluded_agents`。

参见 [heartbeat automation prompt](../heartbeat-automation-prompt.md) 与
[project agent todo contract](../project-agent-todo-contract.md)。

## Dashboard

Dashboard 状态是实验性操作者预览。CLI 与 `loopx status` 仍是规范的日常工作流；
React dashboard 适合 demo、公开安全夹具与本地检查。

一条命令启动已安装的 Personal Workspace：

```bash
loopx dashboard
```

已安装命令用一个进程提供打包 UI、状态投影与 Agent Chat。默认打开浏览器；传
`--no-open` 做无界面启动并使用命令打印的 URL。默认端口下工作区 URL 是
`http://127.0.0.1:8767/chat/`。不需要单独的 `loopx serve-status` 进程。

用 `--no-open` 启动后的最小 readback：

```bash
curl -fsS http://127.0.0.1:8767/chat/ >/dev/null
curl -fsS http://127.0.0.1:8767/status.json
```

当另一客户端需要独立状态源、而不依赖已安装 Personal Workspace 时，
`serve-status` 仍可用：

```bash
loopx serve-status --global-registry --port 8766 --limit 80
```

在 macOS 上登录后保持全局源与构建的 dashboard 运行：

```bash
~/loopx/scripts/macos-dashboard-launchagent.sh install
~/loopx/scripts/macos-dashboard-launchagent.sh status
```

在深入原始日志之前，dashboard 应回答：

- 人需要判断什么；
- Codex 下一步能做什么；
- 什么在等待证据；
- 什么边界还不能跨越。

参见
[apps/presentation/dashboard/README.md](https://github.com/huangruiteng/loopx/blob/main/apps/presentation/dashboard/README.md)。

## 公开 / 私有边界

可安全发布：

- registry schema 与 runtime 布局；
- adapter 生命周期与通用控制面契约；
- 脱敏示例与 smoke 夹具；
- 通用验证命令。

保持私有：

- 真实本地路径；
- 任务 id 与内部文档链接；
- 生产日志与原始实验指标；
- 凭证与认证材料；
- 用户专属活动目标状态与本地 registries；
- 原始 Agent 会话或 benchmark 轨迹。

发布 docs 或示例前运行公开/私有扫描：

```bash
loopx check \
  --scan-path README.md \
  --scan-path docs/ \
  --scan-path examples/
```

参见 [public/private boundary](../public-private-boundary.md)。

## 开发

从仓库根运行聚焦 CLI 与契约 smokes：

```bash
python3 -m py_compile loopx/*.py
python3 examples/demo-cli-smoke.py
python3 examples/control_plane/todo-cli-smoke.py
python3 examples/control_plane/todo-lifecycle-cli-smoke.py
python3 examples/control_plane/quota-contract-smoke.py
python3 examples/control_plane/review-packet-cli-smoke.py
python3 examples/benchmark-candidate-source-boundary-smoke.py
python3 examples/benchmark-run-permission-policy-smoke.py
git diff --check
```

Dashboard 工作：

```bash
cd apps/presentation/dashboard
npm install
npm run build
npm run smoke:demo-readiness
```

发布晋升就绪检查：

```bash
python3 examples/canary/canary-promotion-readiness-smoke.py
loopx promotion-gate --format json
loopx upgrade-plan --format json
```

当 dashboard 源码存在时，就绪 smoke 要求其 npm 依赖，以免依赖跳过被记为通过。
仅当有意限定一个省略 dashboard 验证的发布边界时使用 `--dashboard-mode=skip`；
runtime 证据会记录该跳过。

## 文档地图

从这里开始：

- [Documentation index](https://github.com/huangruiteng/loopx/blob/main/docs/README.md)
- [Showcase catalog](../showcases/README.md)
- [State interaction model](../state-interaction-model.md)
- [Interaction pattern catalog](../concepts/interaction-pattern-catalog.md)
- [Integration guide](../integration.md)
- [Attention queue](../operations/attention-queue.md)
- [Project agent todo contract](../project-agent-todo-contract.md)
- [Quota allocation](../quota-allocation.md)
- [Heartbeat automation prompt](../heartbeat-automation-prompt.md)
- [Long-task cadence hint](../operations/long-task-cadence-policy.md)
- [Public/private boundary](../public-private-boundary.md)
- [Benchmark research workspace](https://github.com/huangruiteng/loopx/blob/main/benchmark/README.md)
- [Dashboard status contract](../status-data-contract.md)
- [Codex peer task orchestration](../integrations/codex-subagent-orchestration.md)
- [DeepSWE research practice](https://github.com/huangruiteng/loopx/blob/main/benchmark/deepswe/README.md)

## 命令参考 {#command-reference}

新用户应从[新手命令路径](newcomer-command-path.md)开始。下面的目录是已知在
调试或扩展哪条路径的操作者与贡献者的参考材料。

```text
bootstrap / connect     connect a project-local goal
new-project-prompt      generate a Codex prompt for project connection
demo                    create a disposable local demo goal
doctor                  diagnose installation and import health
update [check|plan|apply] inspect or apply through the active install owner
registry                inspect registered goals
registry-boundary       classify registry local/public boundary and push policy
status                  show first-screen operator status
diagnose                build an agent-facing diagnostic evidence packet
history                 read run history
refresh-state           append a state-only run
read-only-map           map a project without mutating files
operator-gate           record a human gate decision
reward                  append run-bound human reward
todo                    add, claim, complete, update, supersede, or archive todos
quota                   inspect or account for automatic agent turns
heartbeat-prompt        generate Codex App heartbeat task bodies
upgrade-plan            plan local default-upgrade heartbeat propagation
review-packet           package a CLI-visible handoff packet
serve-status            serve local status JSON for the dashboard
archive-runtime         archive obsolete runtime-only goal history
uninstall-project       disconnect the current project without removing other projects
sync-global             merge project registry into the global registry
check                   run contract and public/private boundary checks
```

分组 CLI 参考用 `loopx commands`，命令专属标志用 `loopx <command> --help`，
已安装操作者手册用 `man loopx`。

## 仓库质量守门

本仓库应保持新贡献者可读。把以下内容当作定期维护者检查：

- README 首屏先讲产品，再讲内部操作；
- 快速开始命令在干净 checkout 上仍可运行；
- 在线本地状态不被提交；
- 发布 docs 或示例前公开/私有扫描干净；
- README 链接的 docs 仍存在并描述当前 CLI 行为；
- smoke 命令覆盖最高风险控制面契约。
