# ZCode Goal 模式


[ZCode](https://zcode.z.ai/) 的 LoopX 适配器 —— 一个终端编码 agent，支持
[skills](https://zcode.z.ai/en/docs/skill)、[Goal Mode](https://zcode.z.ai/en/docs/goal)
与 [Automations](https://zcode.z.ai/en/docs/automations)。

## 该表面是什么

ZCode 从 `~/.zcode/skills/<skill-name>/SKILL.md` 发现用户 skills。虽然 ZCode
提供原生 Goal Mode 与 Automations，LoopX 目前通过受管的 `$loopx` skill 门面集成。
在该模式下，循环驱动是 agent 自己的、由 LoopX quota 管辖的 Turn 循环——每次延续
都经过 `quota should-run` 进入，一个停止决策结束会话循环。

与 ZCode 原生 Goal Mode 或 Automations 的直接机器绑定尚未集成，未来将通过专用
provider 契约支持。

## 安装

```bash
loopx slash-commands --install --surface zcode
```

把受管 LoopX skill 门面（`loopx`、`loopx-global-*`、…）写入
`ZCODE_HOME/skills`（默认 `~/.zcode/skills`；用 `ZCODE_HOME` 覆盖）。受管文件携带
`loopx-managed-slash-command` 标记，并在重跑安装器时刷新；用户自有文件绝不覆盖。

安装后，在 ZCode 中通过 设置 → Skills 刷新或回读已安装 skills。

## 使用

在已连接项目的 ZCode 会话中调用 `$loopx` skill（或键入 `/loopx <复杂任务>`）。
门面指示 agent 运行：

```bash
loopx start-goal --guided --project . --slash-command-arguments="<task>" --host-surface zcode
```

todo 写回后，把生成的心跳 task body 作为会话 objective，每个后续 Turn 都从
`quota should-run` 开始。

## 布局

- `__init__.py` —— 宿主事实：安装表面 id、skills 根解析，以及安装器与激活 packet
  使用的环境变量覆盖。
