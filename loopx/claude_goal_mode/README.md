# LoopX Claude Code 适配器

> [English](README.md)

LoopX 是一个确定性（无 LLM）的控制面。在 Claude Code 上，**运行循环是 Claude
Code 原生的 `/loop`**；LoopX 提供控制面协议。我们**不**使用 `/goal`（它从
transcript 判断完成状态，与 LoopX 的确定性 gate 冲突）。

- **运行时** —— 原生 `/loop`，它执行项目的 `.claude/loop.md`。
- **控制面** —— LoopX MCP 工具 `should_run` / `claim_task` / `complete_task`
  （`should_run` 是每次 tick 的确定性 gate）。
- **安装** —— `/loopx` 命令写入 `.claude/loop.md` 并注册 goal/agent。它只**设置**
  一个 goal；真正的工作运行在原生的 `/loop` 下。
- **可选加固** —— 一个 opt-in 的 `PreToolUse` `should_run` gate（`--harden`）。

## 安装（opt-in）

该适配器**从不**由常规 LoopX 安装器安装。你显式启用它，除非你主动要求，否则
不会向 `~/.claude` 写任何东西。`install.py` **要求**显式 `--scope`；**project**
作用域更受推荐（它只触碰该项目的 `.claude/`），**user** 作用域会在安装时明确
告知，因为它影响你所有的 Claude Code 项目。

### A. 通过 LoopX 安装器（opt-in 环境变量，user 作用域）

```bash
LOOPX_INSTALL_CLAUDE=1 scripts/install-local.sh
```

安装 MCP server + `/loopx` 命令到 **user** 作用域。**没有 hooks。** 不设置
`LOOPX_INSTALL_CLAUDE=1` 时安装器完全跳过该适配器。

### B. 直接安装，带显式作用域（推荐 project）

```bash
# 仅本项目（推荐）
python3 loopx/claude_goal_mode/scripts/install.py --scope project --project /path/to/project

# 你所有 Claude Code 项目（安装时会明确告知）
python3 loopx/claude_goal_mode/scripts/install.py --scope user

# 预览，不写任何东西
python3 loopx/claude_goal_mode/scripts/install.py --scope project --project /path/to/project --dry-run
```

### 可选加固（`--harden`）

添加一个 opt-in、**project 作用域**的 `PreToolUse` gate（外加 statusline）。
它是一个确定性策略层，**不是沙箱**。默认关闭。goal 模式武装期间，每次工具调用
它会：

- 无条件**允许**只读工具（`Read` / `Glob` / `Grep` / …），先行于 gate 判断；
- 否则咨询 `should_run`，当 `should_run` 为 `false`（或探测不可达，fail-closed）
  **拒绝**该（非只读）工具；
- 当 `should_run` 为 `true`：**允许**路径在 `write_scope` 内的 `Edit` / `Write`，
  **拒绝**其外的；`Bash` 只按破坏性命令**黑名单**做 gate（其余全部允许）；**未知
  工具**交给 Claude Code 的正常权限流程。

因为 `Bash` 按黑名单 gate 而非限制在 `write_scope` 内，这**不是强隔离**——一个
坚决的 shell 命令仍可写到作用域外或联网。对不可信或高风险的工作，请在
容器/VM 中运行 Claude Code。在这个边界内，`/loop` 可以在不开 auto 模式的情况下
大幅无人值守运行。

```bash
python3 loopx/claude_goal_mode/scripts/install.py --scope project --project /path/to/project --harden
```

安装器**从不**删除既有权限规则：旧式 LoopX 凭据拒绝
（`Read(~/.ssh/**)` / `Read(~/.aws/**)`）会收到打印的手动清理建议，而不是被
移除。

### 一次性连接（设置 goal + project 作用域安装）

```bash
python3 loopx/claude_goal_mode/scripts/connect.py \
    --project /path/to/project --goal-id GOAL [--objective "..."] [--harden]
```

安装后**重启任何打开的 Claude Code 会话**，使命令与 MCP server 加载。

## 使用

```
/loopx <task>     # 为本项目设置一个 goal + 写入 .claude/loop.md
/loop             # 原生运行时驱动循环（或 `/loop 10m` 固定周期）
/loopx status     # goal objective、state 与 todos
/loopx off        # 移除 .claude/loop.md（原生 /loop 随后无物可运行）
```

## 卸载

```bash
claude mcp remove --scope <user|project> loopx        # MCP server
rm <scope>/.claude/commands/loopx.md                  # /loopx 命令
```

如果你运行过 `--harden`，请手动从 `<scope>/.claude/settings.json` 移除 loopx
`PreToolUse` 块（与 `statusLine`）——安装器从不替你编辑现有规则。

## 测试

```bash
python3 examples/claude-install-optin-smoke.py
```

证明正常安装不触碰 `~/.claude`、必须显式 `--scope`、project 作用域隔离、hooks
为 opt-in（`--harden`），且既有权限规则得到保留。
