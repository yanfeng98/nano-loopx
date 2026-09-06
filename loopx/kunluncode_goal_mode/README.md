# LoopX KunlunCode 适配器


KunlunCode 适配器是 LoopX 的头等宿主表面。它使用自己的项目绑定与注册 Agent
身份；它不读取 `.claude/loop.md`，也不作为 Claude Code 的 `cc` 通道执行。

## 命令边界

LoopX 与 KunlunCode 不共享一个命令命名空间：

- `loopx ...` 与 `loopx-kunluncode ...` 是由 LoopX 控制面拥有的 shell 命令；
- `/goal`、`/goal-pro`、`/plan` 与 `/mcp` 是 KunlunCode 原生 TUI slash 命令，
  携带 KunlunCode 会话状态；
- `should_run`、`list_todos`、`claim_task` 与 `complete_task` 是由模型调用的 MCP
  工具，不是用户键入的 slash 命令。

在 KunlunCode 原生 Goal 家族内，`/goal-pro` 保留 `/goal` 的持久 objective 生命周期，
并在完成前增加一个强制的独立校验器。它的 Strict/Arrangement 委派规则是该完成
gate 的执行机制，不是单独的 LoopX 生命周期。

`loopx-kunluncode run` 现在使用 KunlunCode 的机器可读 app-server。默认
`--mode goal-pro` 创建或恢复真实 Kunlun 线程，以 `strict` 模式调用
`thread/goal/set`，启动第一 Turn，让 KunlunCode 驱动原生自动延续，并且只在
`verification_passed` 后接受完成。`--mode goal` 选择不带严格校验器 gate 的原生
Arrangement 模式。两种模式都不把 slash 命令敲进 prompt；它们通过确定性 API
激活同一原生生命周期。

LoopX 保持外层控制器。它在宿主执行前选择并认领一个 todo，在忽略的本地状态日志中
记录不透明的原生线程/goal 身份，且只在原生终态被接受后执行交付/todo/quota
写回。原生运行期间，模型可见的 MCP `claim_task` 与 `complete_task` 工具，以及
面向绑定 Goal 的直接 LoopX 生命周期 CLI 写入，都 fail closed。因此模型不能在原生
校验器通过前提交 LoopX 状态。`--mode headless` 把早期的一 Turn MCP worker 保留为
显式兼容模式。

## 安装与连接

对于打包安装，正常安装 LoopX，让适配器通过 `uv` 配备其拥有的 MCP 环境：

```bash
python3 -m pip install --upgrade loopx
loopx-kunluncode install
loopx-kunluncode connect \
  --project . \
  --goal-id my-goal \
  --agent-id kunlun
```

配备者在源码 checkout 之外安装相同 LoopX 分发版本与 `mcp==1.28.1`。贡献者可以改用
一个 checkout 本地的 uv 管理环境：

```bash
uv venv .venv
uv pip install --python .venv/bin/python -e . 'mcp==1.28.1'
.venv/bin/loopx-kunluncode connect \
  --project . \
  --goal-id my-goal \
  --agent-id kunlun \
  --python .venv/bin/python
```

下文命令使用 `PATH` 上的打包 `loopx-kunluncode` 入口；checkout 用户可替换为
`.venv/bin/loopx-kunluncode`。

KunlunCode 目前即使项目或 overlay 设置包含 `mcp_servers`，也把 MCP 注册存储在
用户配置中。因此安装器创建一个显式命名的全局条目 `loopx-kunluncode`；项目与身份
选择仍来自当前工作目录与被忽略的 `.loopx/kunluncode.json` 绑定。

除非显式给出 `--replace`，安装器绝不覆盖同名外来条目。如果添加替换失败，它会
恢复基于命令的旧条目；无法安全重建的注册在移除前被拒绝。

回读连接：

```bash
kunluncode --cwd "$PWD" mcp test loopx-kunluncode
loopx-kunluncode status --project .
```

## 运行原生 Goal

添加一个有界任务并运行默认原生 Goal Pro 控制器：

```bash
loopx-kunluncode add --project . "Run the focused check and record the result"
loopx-kunluncode run --project . --permission-mode auto
```

原生事务是：

```text
LoopX should-run / 选定 todo / claim
  -> app-server initialize
  -> thread/start 或 thread/resume
  -> thread/goal/set(mode=strict)
  -> turn/start + 原生自动延续
  -> thread/goal/get(status=complete, verification_passed)
  -> LoopX refresh-state / todo complete / quota spend
```

默认 app-server 路径是非交互式的，因此默认权限模式是 `auto`；`ask` 以可操作错误
失败，而不是挂在批准请求上。这选择 KunlunCode 的权限行为，但不授予新的 LoopX
权威。`--controller-timeout-secs` 用于原生 Goal 总窗口，`--max-duration-secs`
用于 KunlunCode 的每 Turn 软预算，`--token-budget` 用于可选原生 Goal token 预算。

一起检视原生与 LoopX 状态：

```bash
loopx-kunluncode status --project .
.venv/bin/python examples/kunluncode-app-server-goal-pro-smoke.py --require
```

被忽略的 `.loopx/kunluncode-runtime.json` 日志只包含绑定身份、不透明原生 ids、
objective 摘要、紧凑终态与写回回执。若控制器被打断，重跑同一命令：它恢复同一
原生线程，或对已校验终态对账，而不重复已完成的 LoopX 写回阶段。

用 `--mode goal` 使用不带严格校验器的原生 `/goal` 语义。只在需要兼容时使用旧式
一 Turn MCP 生命周期：

```bash
loopx-kunluncode run --project . --mode goal
loopx-kunluncode run --project . --mode headless --permission-mode auto
```

## 禁用与移除

停止调用 `run` 即在不改变状态的情况下禁用执行。之后的原生运行恢复同一活跃日志。
移除宿主级 MCP 条目：

```bash
loopx-kunluncode uninstall
```

原生 app-server 模式不要求 MCP 写回，因此卸载 MCP 条目不会禁用原生执行。
只在项目不应再解析 KunlunCode 身份时移除 `.loopx/kunluncode.json`。只在
`.loopx/kunluncode-runtime.json` 的阶段为 `committed` 时删除它，或在你刻意放弃
记录的原生线程时删除。移除任一本地文件都不会删除 LoopX goals、todos、运行历史、
KunlunCode 持久化的线程或另一宿主的适配器。

## 权威与隐私边界

激活不授予仓库写入、发布、破坏性、凭据、外部 sink 或生产权威。选定 todo、
检查点化的 LoopX 写边界与 KunlunCode 权限模式仍然全部适用。原生终态证据是完成
gate，不是权威授予。控制器在其紧凑 refresh-state 写回期间抑制外部 sink 投递。
绑定、运行时日志、活跃 goal 状态与运行证据保持在被忽略的 `.loopx/` 或私有
LoopX 运行时之下，不得提交。
