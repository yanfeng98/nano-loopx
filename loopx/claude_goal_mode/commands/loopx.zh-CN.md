---
description: loopx goal-mode setup (NOT Claude Code's built-in /goal). `/loopx <task>` sets up a goal + writes .claude/loop.md; drive the loop with native /loop. bare /loopx = arm; off | status.
argument-hint: <task to do>  |  (no args = arm)  |  off  |  status
allowed-tools: Bash(python3:*)
---

> [English](loopx.md)

运行 loopx 安装助手并读取其输出：

!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/goalmode_cmd.py" $ARGUMENTS`

输出是 loopx 控制面的 SETUP / 状态信息——它是**完整、面向用户**的结果。向用户
逐字展示它并**停止**。不要做任何工作、不要认领 todos、不要写文件、不要在这里
跑循环：真正的**工作**在用户键入 Claude Code 原生的 `/loop`（它执行
`.claude/loop.md`）时运行。不要把一个多行 `status` 详情块压缩成一行。

注意：这是 `/loopx`（loopx 控制面 SETUP），**不是**运行时，也**不是** Claude Code
内置的 `/goal`。运行循环是原生的 `/loop`；loopx 提供确定性的 `should_run` 协议。
