# LoopX OpenCode 适配器


LoopX 暴露两层独立的 OpenCode：一个静态命令门面与一个可选的执行 Goal 桥接。
普通命令安装绝不激活运行时桥接。

## 安装

默认的 `all` 表面只在 `~/.config/opencode/commands/` 下安装静态文件：

```bash
loopx slash-commands --install
```

显式启用 Goal 桥接：

```bash
loopx slash-commands --install --surface opencode --with-goal-bridge
```

在写任何 OpenCode 文件之前，桥接安装校验 `opencode.json`、`opencode.jsonc` 与
`package.json`。如果配置无效或直接注册了 `opencode-goal-plugin`，它 fail closed，
因为在该 LoopX 包装器旁加载该插件会启动两个独立的 goal 运行时。

预检成功后，安装器写入命令门面以及：

- `~/.config/opencode/plugins/loopx-goal.js`；
- `~/.config/opencode/loopx/goal-bridge-runtime.mjs`；
- `~/.config/opencode/package.json` 中固定版本的桥接依赖。

OpenCode 在启动时为配置目录依赖运行 `bun install`。桥接安装后重启 OpenCode，使它
安装这些依赖并加载本地 plugin。

## 运行时

运行 `/loopx <task>`，再用 `loopx_goal_activate` 激活返回的宿主 packet。运行时
流程是：

```text
OpenCode idle 事件 -> loopx quota should-run
  -> run_now: 继续一次
  -> wait: 安排有界本地复查，不调用模型
  -> user input: 回答它，恢复 goal，继续经 quota 做 gate
  -> unchanged-poll limit: 暂停可见 goal 并停止定时器
  -> terminal_no_followup: 待机轮询而非完成；新工作自动恢复 goal
```

用户消息与权限回复绝不暂停循环。桥接在回答用户消息期间停止定时唤醒，在下一个
idle 事件时探测 goal 恢复，并按通常方式继续 quota gated 操作。校验后的终态关闭
不再完成 goal：桥接让 goal 保持活跃待机，每五分钟复查一次 quota，因此完成一个
任务并不结束循环。

绑定是每会话私有 JSON 文件，位于 `$LOOPX_OPENCODE_STATE_DIR`，默认为
`$XDG_STATE_HOME/loopx/opencode`，使用 mode `0600`。OpenCode 的一次性 `opencode run`
进程不能拥有退出后的定时器；循环操作需要可见 TUI 或持久 OpenCode server。
OpenCode 2 改为运行持久 goal worker；见 `loopx/opencode2_goal_mode/README.md`。

Quota 探测携带 `--record-host-poll`，因此 LoopX 在 goal 状态文件旁写入紧凑 poll
回执，而 `loopx global-risks` 可以标出等待中途桥接死掉的循环。探测失败以有界
指数退避重试（3 分钟起，至 30），成功后重置。每会话锁文件防止两个 OpenCode 进程
同时评估同一会话。

用户消息在绑定中设置 `userMessagePending`，因此下一次 idle 评估先恢复包装的 goal
（它可能在上次用户输入时暂停），再继续 quota gating；显式暂停工具仍记录类型化
`lastPausedReason`，`/goal resume` 清除它。unchanged-poll limit 不再静默停止
定时器：桥接暂停可见的 OpenCode goal，使停止在会话与 LoopX 状态中都可见。

包装的 goal plugin 也把私有重启状态持久化在活跃项目的 `.opencode/goals/` 目录下。
把 `.opencode/goals/` 加入项目忽略规则，使 goal 文本、检查点与生命周期状态不能
进入公开 commit。

## 卸载

只移除静态命令门面：

```bash
loopx slash-commands --uninstall --surface opencode
```

移除静态门面与 LoopX 管理的桥接文件：

```bash
loopx slash-commands --uninstall --surface opencode --with-goal-bridge
```

桥接卸载保留 `package.json` 依赖，因为用户自有的本地 plugins 可能共享它们。
