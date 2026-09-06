# Botmux Goal Channel runtime


LoopX 可以把现有的 [botmux](https://github.com/deepcoldy/botmux) bot 绑定到一个
Goal Channel。Botmux 负责 IM 投递、Lark 事件订阅、持久 agent 会话、流式卡片与
终端访问。LoopX 仍然是 goal 状态、todo、gate、配额、证据与已接受转移的唯一权威。

该集成不替代现有的 Lark Goal Channel 投影。两个界面互补:

```text
LoopX Goal Channel sync -> Lark status, Kanban, and gate notifications
Lark interaction -> botmux -> configured agent runtime -> LoopX command
```

通知或 botmux 投递回执只是观察结果,不会改变 LoopX 的规范状态。只有当配置的
agent runtime 显式调用一次经过验证的 LoopX 转移时,状态才会改变。

## 前置条件

- botmux 已安装并运行;
- 所选 botmux bot 能够调用已安装的 LoopX CLI 或受管 skill;
- 该 bot 被允许在选定的 Lark 群聊中发言;
- botmux 运行在拥有 LoopX 项目 checkout 的宿主上;
- bot 的 `defaultWorkingDir` 或选定群聊的 oncall `workingDir` 能解析到 LoopX
  项目根目录;
- botmux Dashboard 令牌存在于某个环境变量中。

LoopX 从不存储 Dashboard 令牌。本地私有 runtime 绑定只存储环境变量名。

## 配置

导出现有的 botmux Dashboard 令牌:

```bash
export BOTMUX_DASHBOARD_TOKEN='<local-private-token>'
```

先预览绑定:

```bash
loopx goal-channel runtime setup \
  --goal-id <goal-id> \
  --bot-id <botmux-lark-app-id> \
  --chat-id <lark-chat-id>
```

预览会探测 botmux 的存活状态,确认所选 bot 在线、位于选定群聊中且已绑定到
LoopX 项目目录,然后使用 botmux 的 dry-run 触发契约验证群聊路由。显式应用
本地私有绑定:

```bash
loopx goal-channel runtime setup \
  --goal-id <goal-id> \
  --bot-id <botmux-lark-app-id> \
  --chat-id <lark-chat-id> \
  --execute
```

绑定以 owner 专用权限写入项目注册表旁的
`.loopx/goal-channel-runtime.json`。它包含私有 provider 标识符,必须保持
被忽略且不被跟踪。

## 运维

在不改变 provider 状态的情况下验证就绪状态:

```bash
loopx goal-channel runtime doctor --goal-id <goal-id>
```

预览下一轮有界 Turn:

```bash
loopx goal-channel runtime trigger --goal-id <goal-id>
```

显式入队:

```bash
loopx goal-channel runtime trigger --goal-id <goal-id> --execute
```

默认指令要求配置的 agent runtime 使用其已安装的 LoopX CLI 或受管 skill,选择
活动的下一个动作,并在 Turn 停止之前完成 artifact、验证与状态写回。只有当 owner
需要不同的有界指令时才使用 `--instruction`。

默认语义 Turn key 由当前 goal 状态派生。重复执行同一命令不会派发新的 Turn。
主动进行无状态跟进之后,提供显式的新 key:

```bash
loopx goal-channel runtime trigger \
  --goal-id <goal-id> \
  --turn-key <owner-chosen-semantic-key> \
  --execute
```

读取 botmux 的类型化生命周期结果:

```bash
loopx goal-channel runtime status --goal-id <goal-id>
```

只有在需要把观察到的状态持久化到本地私有 LoopX 回执时才添加 `--execute`。

## 失败语义

- 首次可见群聊派发会在 provider 调用之前记录一条 `attempting` 回执。如果提交
  后连接失败,LoopX 报告 `botmux_dispatch_outcome_unknown`,不会盲目重试。
- 后续 Turn 复用已存储的 botmux 会话以及 botmux 原生的
  `turnIdempotencyKey`。
- `running`、`completed`、`failed` 与 `not_found` 只是 provider 观察。它们不会
  独立地完成、重新打开或以其他方式改变 LoopX goal。
- Lark 消息或 botmux 卡片只是投递证据,不是 LoopX 转移权威。

## 关闭或回滚

该集成是 opt-in 的,不会改动 botmux 配置。先预览,然后只关闭选定的 goal 绑定:

```bash
loopx goal-channel runtime disable --goal-id <goal-id>
loopx goal-channel runtime disable --goal-id <goal-id> --execute
```

关闭会清除所选 goal 的活动 botmux 会话指针,但不影响其他 goal 绑定与 botmux
守护进程。现有的 Goal Channel 状态/Kanban 同步保持独立。
