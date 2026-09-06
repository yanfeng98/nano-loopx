# Antigravity CLI Goal 模式

> [English](README.md)

LoopX 面向 [Antigravity CLI](https://antigravity.google/docs/cli/using/)(二进制
`agy`)的适配器——Google 的终端 coding agent。agy 原生自带 goal-mode host 的两半:
一个 goal 原语和一个会话内 scheduler,因此 LoopX 把 objective 绑定到 host 自己的
loop,而不是假装 agent 只是在自我驱动。

## 原生 Goal 原语(已在 agy 1.1.18 上 live 验证)

`/goal <task>` —— 内置命令,"运行直到指定 goal 完全完成"。host 注入一个
forced-continuation contract,持续审计工作,直到 model 输出 `<!-- GOAL_COMPLETE -->`
(用 `<!-- GOAL_CANCELLED -->` 取消)。现场证据:

- 交互式 TUI(tmux):`/goal Create the file … and verify …` 实际运行了
  "Initiating Goal Analysis",创建文件、自验内容并完成——文件以精确内容落盘。
- Headless print 模式:`agy -p '/goal just reply ok'` 返回的响应以
  `<!-- GOAL_COMPLETE -->` 结尾。
- 该机制内置于二进制当中(命令说明、forced-continuation system prompt、
  `GoalState` 持久化,以及两个 token)。

## 原生唤醒原语(已在 agy 1.1.18 上 live 验证)

- `schedule` 工具——`DurationSeconds` + `Prompt`(唤醒消息),通过
  `MaxIterations` 实现周期性唤醒,带提前终止条件的一次性 timer。现场探测:
  一个在 T 时刻以 "scheduled" 结尾的 turn,在 T+25s 收到 SYSTEM_MESSAGE 唤醒,
  会话自主作答——没有外部 driver,没有任何用户输入。
- 后台任务(`manage_task`)与异步 subagent(`invoke_subagent`/`send_message`)
  会唤醒一个存活会话;agent 消息进入会话 inbox(`manage_inbox`)。
- `hooks.json`(用户或插件)在工具事件上运行 `PostToolUse`/`Stop`/`PostInvocation`
  自动化。

## 这个 surface 是什么

Antigravity CLI 从固定的 `~/.gemini/antigravity-cli/skills` 根目录,用其文档化的
flat layout 发现全局 skills——每个 skill 一个 `<name>.md` 文件。LoopX 通过生成的
`/loopx` skill facade 触达 `agy` 会话,激活时用原生 `/goal <task_body>` 命令绑定
objective。

激活 packet 中明确写下了两个诚实限制:

- **Quota pacing 只是 advisory。** LoopX 不安装任何拦截原生 continuation 或
  唤醒的 AGY hook,因此 `quota should-run` 入口只是指示 agent 遵守的 facade
  建议——不是 host 强制执行的 gate。没有它,agy 也会继续原生运行。
- **一切随会话生死。** goal loop 与唤醒只在 CLI 会话存活期间生效——
  没有跨会话 daemon——因此它们武装的是存活会话的有界 segment,不是无人值守的
  host loop。

## 安装

```bash
loopx slash-commands --install --surface agy
```

把受管理的 LoopX skill facade(`loopx.md`、`loopx-global-*.md`、…)平铺写入
`~/.gemini/antigravity-cli/skills/`——即文档化的 agy layout。官方 CLI 未提供
home 覆盖机制,所以 LoopX 也不提供:安装只会落到那个确切路径。受管理文件带有
`loopx-managed-slash-command` 标记,重新运行 installer 即可刷新;用户自有文件
永远不会被覆盖。

## 使用

在已连接项目的 Antigravity CLI 会话中,调用 `loopx` skill(或输入
`/loopx <complex task>`)。facade 指示 agent 运行:

```bash
loopx start-goal --guided --project . --slash-command-arguments="<task>" --host-surface agy
```

todo 写回之后,用原生 `/goal <task_body>` 绑定生成的 heartbeat 任务体,之后的
每个 turn(以及每次 `schedule` 唤醒与 audit-continuation)都用 `quota should-run`
开始(advisory 指引;LoopX 不会拦截原生 host continuation),并且只在 quota 许可
更多工作时,才用原生 `schedule` 工具武装下一个有界唤醒。

## Layout

- `__init__.py` —— host 事实:install surface id、固定 skills 根目录解析、
  激活附加项(advisory quota pacing 与 continuation 边界),以及激活引用的
  原生 goal + wake 原语。
