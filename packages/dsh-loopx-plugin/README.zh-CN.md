# DeepSeek Harness 版 LoopX

`dsh-loopx-plugin` 是一个独立版本化的 DSH 包,包含三行独立的 Loader:

- init 行自动安装或升级 LoopX CLI,把打包好的 workflow skills 安装到 `$DSH_AGENTS_HOME/skills`(默认 `~/.agents/skills`),并在 DSH 结束加载前校验原生的 `loopx` 入口。`/loopx-init` 保留为显式修复命令。
- 一个被动的同会话 Driver 只有当当前确切 Session 成功调用过确切的 `loopx` skill 后才具备资格。此后它会询问 LoopX 是否还能再跑一个 Turn,并把权威 heartbeat 任务排队到那个存活的 DSH Agent 中。
- 包根部的 Host 注册一个仅限回环的 `/loopx` Connection 通道,其 web Client 在 DSH 原生 GoalBar 与 Queue dock 行之间贡献一条紧凑的 GoalBar。它只为确切的一对存活的 `(goalId, loopxAgentId)` 绑定渲染。

安装插件并启动 DSH 只是加载并准备好这些能力;这既不会创建绑定,也不会激活 Driver。GoalBar 在浏览器行挂载时做一次有界读取,然后关注确切 Session 的 `step/end` 与 `turn/end` 边界。只有当权威绑定或活动 Goal 状态的不透明 revision 变化时才重新读取 LoopX;watch lease 也能检测该 Session 之外写入的变化。DSH Agent 状态事件只更新已有行,不产生 LoopX 业务读取。在一个确切 Session 包含有效的类型化 `loopx` 调用证据之前,其 Driver 不会发起任何 LoopX CLI、绑定、quota 或 heartbeat 调用,不创建定时器,也不排队后续任务。

该包不暴露 LoopX 模型工具、绑定 sidecar,也没有自己的 Goal/Todo 状态。模型使用已安装的 LoopX skills 并直接调用 LoopX CLI。LoopX 仍是 Goal、Agent、Todo、quota、激活与持久线程绑定数据的唯一权威。GoalBar 协议及其延迟原子性限制详见带版本号的 [DSH 原生 LoopX 设计](../../docs/plans/2026-08-20-dsh-native-skill-driver.md)。

## 安装

要求:Node.js 22.19+、`pnpm`、Python 3.11+ 并带 `pip`,以及首次启动 DSH 时(若机器上没有兼容的 LoopX CLI)需要网络访问。LoopX 本身刻意不作为前置依赖。初始化器优先使用显式指定的 `PYTHON_BIN`,否则依次检查 `python3`、`python3.14`、`python3.13`、`python3.12` 与 `python3.11`,保留第一个满足要求的解释器。如果必须安装或升级 LoopX,则写入 `$DSH_AGENTS_HOME/runtime/dsh-loopx-plugin`(默认 `~/.agents/runtime/dsh-loopx-plugin`)下的隔离副本,绝不改动系统 Python 环境。这对强制 PEP 668 的外部管理 Python 发行版同样有效;该插件不使用 `--break-system-packages`。
已发布的插件要求 LoopX 0.5.4 或更新版本。虽然 0.5.3 已携带 workflow-skill 文件,0.5.4 是第一个能在插件通过 Linux `pip --target` 管理运行时安装后发现这些文件的版本。
把预构建的发布版安装到 web profile:

```bash
dsh plugin --profile web add \
  "https://github.com/huangruiteng/loopx/releases/download/dsh-loopx-plugin-v0.1.1-beta.4/dsh-loopx-plugin-0.1.1-beta.4.tgz"
```

对于源码检出,等价的构建并安装路径是:

```bash
cd packages/dsh-loopx-plugin
./install.sh
```

在回环地址上启动 DSH(端口 `0` 让操作系统挑一个空闲端口)并打开打印出的 URL。插件会在 DSH 发布 Web URL 之前完成其幂等的 LoopX CLI 与 skill 引导。其类型化的 `loopxBootstrap` 服务在启动要么成功要么安全失败之前,对 Web 服务器与运行时行进行把关:

```bash
dsh --profile web --port 0
```

可以立即使用 `/loopx <task>`。如果自动初始化在 DSH 日志中报告了安全失败,修好所指出的 Python 或包管理器问题,然后运行一次 `/loopx-init` 重试;正常安装不需要该命令。

安装即 GoalBar 的选择加入:没有独立的远程端点,也没有按会话授予的权限。行的可见性保持隐藏,直到确切 DSH Session 拥有唯一的 LoopX 绑定。调用该 Session 已安装的 `loopx` skill 后,在该 Session 的 DSH shell 里运行最小权威回读(或用确切的 Session id 替换 `$DSH_SESSION_ID`):

```bash
loopx --registry .loopx/registry.json --format json \
  resolve-agent-thread \
  --host-surface deepseek-harness-native \
  --thread-id "$DSH_SESSION_ID"
```

`status=bound` 且恰好一对匹配时,该行才被接纳;缺失或歧义的结果按失败关闭处理,不渲染任何内容。`Start` 恢复一个已停止的 Goal,并且只有当那个确切存活的 Session 已包含类型化的 `loopx` skill 激活证据时才要求 Driver 评估。它永远不会激活一个不活跃的 Session。`Pause` 停止 Goal,并且只撤销未来已排队/已调度的续接;它不会中断一个已认领或运行中的 Turn。

维护者可以用以下命令验证构建并打包的组件面:

```bash
pnpm build
pnpm smoke:artifact
pnpm smoke:profile
pnpm smoke:runtime
pnpm smoke:docker
```

runtime smoke 会创建一个隔离的临时 DSH profile。其真实 web 进程验证 profile 组合、就绪前的自动初始化、skill 目录立即可见、boot-manifest 发现、bundle 服务、Client 物化,以及回环 Connection 围栏。另外,用真实 Host Session fixture 打包一个受支持的 DSH Context、Connection 与 WebServer,覆盖同 Turn 绑定发现、lease-time 源协调、仅状态更新、待处理 watch 取消、成功动作,以及经真实 HTTP 载体进行 handler 清理。然后,把已服务的 Client 应用到 DSH 真实的 ClientModuleSystem 中,配合 VM 文档 harness;该层覆盖 slot 顺序与共存、Session 注入以及普通卸载/HMR 式清理,但它不是浏览器挂载的 React 交互。这些层并不替代 owner 评审过的打包浏览器 gate:那是一个独立的人工层,把已服务的 Client 挂载到真实 DSH URL,并演练 Client 到载体的 Start/Pause。聚焦的 Client 测试覆盖 Session 代际替换与旧请求取消,而不必在打包的 smoke 里重复那套矩阵。
Docker smoke 打包当前插件并构建当前 LoopX 发布候选 wheel,然后在干净的 Debian 容器中启动两者,配合受支持的 DSH 发布版。它验证 PEP 668 兼容的私有安装、管理 launcher、启动就绪与首会话 `loopx` skill 发现。它需要 Docker、`uv` 以及获取基础镜像所需的网络访问,并且从不打开浏览器或配置模型 provider。

## Shadow observer(默认关闭)

`src/observer.ts`,导出名为 `dsh-loopx-plugin/observer`,是 LoopX [Reliability Diagnostics](../../loopx/capabilities/reliability_diagnostics/README.md) capability 的 `dsh-session-events` provider:一个消费只读 harness 事件并追加紧凑、public-safe 信封及 observer 统计记录的 L1 shadow observer,写入 `<loopx-runtime-root>/reliability_diagnostics/<goal-id>.ndjson`。它与 Driver 是独立的 Cordis 行与 bundle,没有 Driver 或 Agent 注入,也没有共享的发送路径。它从不调用 `agent.send`、不触碰 inbox、不调用 LoopX CLI、不调度、不重试、不停止也不恢复任何东西。每个 hook 体与每次 flush 都是隔离的,因此 observer 失败会计入 receipt,而不是传导到 DSH。这是模块与 hook 隔离,不是操作系统进程隔离的主张。

在第一次追加之前,该 producer 应用与 Python 契约相同的递归本地路径、凭据类值与凭据字段防护。不安全的 event 令牌或 id 计为 `public_safety_violation`,永远不会进入 ledger 字节;CLI 摄取会独立地重新校验持久化的记录。

除非在 DSH 启动前声明好确切的一个 goal、一个 DSH session 与完整的 run 身份,否则它保持关闭:

```bash
export LOOPX_DSH_SHADOW_OBSERVER_GOAL_ID=<goal-id>
export LOOPX_DSH_SHADOW_OBSERVER_SESSION_ID=<session-id>
export LOOPX_DSH_SHADOW_OBSERVER_RUN_IDENTITY_JSON='{"worker_id":"<worker>","model_id":"<model>","task_id":"<task>","environment_id":"<environment>","tools_id":"<tools>","budget_id":"<budget>","adapter_revision":"<adapter-revision>","observer_revision":"<observer-revision>"}'
# 可选:LOOPX_DSH_SHADOW_OBSERVER_LEDGER_DIR、LOOPX_DSH_SHADOW_OBSERVER_BUFFER_BOUND(默认 256)
loopx reliability-diagnostics receipt --goal-id <goal-id> --format json
loopx reliability-diagnostics status  --goal-id <goal-id> --format json
```

除非所有必需变量都有效,否则独立的 observer 行不注册任何 hook,也不写任何文件。启用后,它只消费 `session/created`、`session/event` 与 `session/disposed`;它跳过 `assistant/chunk`,只记录工具名、Turn 与 step 编号、类型化结束原因以及 id,绝不记录参数、输出、提示或路径。任何不属于确切配置 session 的事件都以 `identity_invalid` 拒绝。统计记录固定 worker/model/task/environment/tools/budget 以及 adapter 与 observer revision,声明来源覆盖,并证明计数守恒。序列缺口中断、有界缓冲丢弃、flush 尝试、声明的时钟不确定度以及空的 outbound 与 influence 字段,使该 run 的可准入性可以从 receipt 审计出来。

这是一个按 RFC P0 原型组件实现的事实验证适配器。它不确立 RFC 的 P0 出口:C0 保真度、合格的 C1 run 以及实测的 observer 开销仍然是独立的证据关卡。

## GoalBar 权威与隐私边界

`/loopx` 以 Connection authority `loopback` 注册。回环是网络可达性围栏,不是用户认证,Phase 1 不支持 LAN 或远程浏览器。浏览器只提供它被注入的 DSH Session id,以及在动作请求时最后验证过的 Goal/Agent 对。Host 从存活的 DSH Agent 重新推导 cwd 与线程身份,重新解析绑定,并且只执行固定的 LoopX argv。

wire allowlist 包含 id、激活、存活的 Agent 状态、满通道计数、游标、不透明源 revision 以及固定错误码。它排除 Todo 文本、Goal objective、quota、evidence、CLI 输出、异常消息、registry 路径、凭据与绑定候选。源 revision 仅仅是变更令牌,不是授权,也不是 compare-and-swap 防护。安装该包不授予模型工具权威,不创建也不修复绑定,并且自身不改变 LoopX 核心状态。

## 自动初始化与 `/loopx-init` 修复

当 DSH 加载该插件时,init 行运行相同的类型化初始化例程,并且只在它收敛后才发布 `loopxBootstrap` 就绪服务。插件的 profile 补丁让 DSH 的 Web 服务器与运行时依赖该服务,因此打印出的 URL 是一个真正的引导边界。安全失败在记录时不带原始子进程输出或本地路径,释放 Web 行而不是停止 DSH,并保留 `/loopx-init` 供显式重试。自动启动不创建 Agent 后续任务,也不产生模型调用。

修复命令不带参数。任何多余输入都会在任何模型工作或 CLI 探测之前返回用法错误。一次有效的调用会在确切接收方 Agent 上排队一个有界的 start 后续任务,然后探测当前 LoopX 安装。当 CLI 缺失或不具备 DSH 原生 skill 契约时,它恰好运行一次固定 argv 的 `pip install --upgrade --target <plugin-runtime> 'loopx>=0.5.4'`,在该 target 旁边写入一个小型管理 Python launcher,然后用同一个解释器与 launcher 安装并读回 skills。Driver 与 GoalBar 解析这个相同的管理运行时,包括在显式修复之后。它从不构造 shell 命令、不改动系统 Python 环境、不编辑 registry,也不重试安装变更。

除非命令被取消,它会为类型化的成功或失败结果排队第二个有界的后续任务。这些是普通的 Agent Turn,因此一次有效且未取消的调用通常会产生两次模型调用;取消只留下已排队的 start Turn,而无效输入不产生任何调用。这些 prompt 不授权任何工具、命令或另一次安装。后续任务投递是尽力而为,不重试。命令 UI 渲染的原生 `CommandResult` 保持权威:后续任务失败或模型回复不能改变安装结果,也不会重复其变更。

成功后,DSH 的 filesystem skill provider 使其目录失效并在不重启的情况下加载新建或更新的 skills。缺失或未知的 skill 状态仍然使初始化失败,而不是猜测为未变化。

初始化后,用任务文本调用 `loopx` skill。该 skill 使用确切的 DSH 管理 `$DSH_SESSION_ID`,传递 `--host-surface deepseek-harness-native`,并遵循 LoopX 返回的类型化命令。历史的外部连接器仍然是不同的 `deepseek-harness` / `dsh` surface。

## Driver 激活边界

激活按 Session 进行,而不是按插件、进程、Agent、Goal 或项目。Driver 只接受以下两类持久类型化 Session 事实之一:

- 一个来源恰为 `skill-invocation`、名字恰为 `loopx`、形式恰为 `instructions` 的 `user/message`;
- 一个名字恰为 `skill` 的模型 `tool/call`,其 JSON 对象参数中 `name` 恰为 `loopx`,并由 call id 与随后成功的 `tool/result` 配对。

skill 目录、普通散文、shell 文本、`/loopx-init`、插件撰写的 init 或 heartbeat 消息、一次失败、畸形、不匹配或已被取代的模型调用,以及 CLI、registry、Goal、绑定或项目文件的存在,都不激活 Driver。恢复只折叠当前 Session 内存中已有的类型化事件历史,不做任何外部探测。替换或清空一个 Session 会从替换后的历史重新计算;激活从不跨该边界继承,也没有插件自有的持久存储。

从旧插件版本升级而来的既有 Session,当其保留的历史中没有可识别的调用证据时保持不活跃。在每个应该自动继续的 Session 中调用一次已安装的 `loopx` skill。激活只记录意图:它不创建绑定、不选择 Goal 或 Agent、不消耗 quota,也不授予工具权威。激活后,已有的确切绑定、新鲜 quota、scheduler/heartbeat、reservation 与 pre-step 重新验证顺序保持权威。

## Driver 重试边界

DSH 的 LLM 重试插件负责 provider 请求重试。本 Driver 只重试安全固定 argv 的 LoopX 读取以及幂等的 `quota should-run` receipt,在首次尝试之外最多再重试两次。每次重试使用相同的 `--turn-instance-id`。类型化权威拒绝、不兼容 schema、取消与人工输入绝不重试。没有累积八次失败的熔断器,也没有插件自有的持久激活状态。这个小的进程内激活投影绑定到一个确切 Session,并且只从它的类型化事件历史重建。耗尽三次尝试就停止该次评估;它不会产生周期性错误重试 loop。只有类型化的 LoopX local-scheduler 计划才能调度另一次唤醒,并且它对未变化轮询的限制会得到执行。

对于一次被接纳的自动续接,那个确切的 turn id 也会被携带在 LoopX 自有的规范 heartbeat 体与类型化的 DSH 续接来源中。该来源只是用于 reservation 匹配的归属,不是权威。在工作进入模型 step 之前,Driver 重放同一个 receipt,LoopX guard 为该确切 id 返回类型化的结算计划。应负责任的工作通过该计划的单一确定性效果身份写回与消费;它不会回退到无绑定的通用消费命令。工作开始前发生的人工优先级、Pause、处置或失败的 pre-step 检查,不会捏造出写回、消费或 void receipt。

Driver 用 `resolve-agent-thread` 解析当前项目 registry,要求存活的 DSH session 恰好有一个 Goal/Agent 匹配,并在下游 pre-step 监听器之前和之后重新检查绑定与 quota。人工消息撤销一个未认领的自动 reservation;混合批次会拒绝自动消息并恢复人工工作。Driver 每次自动接纳最多排对一个 Driver 自有的后续任务。初始化消息使用独立的 `dsh-loopx-plugin/init-command` 来源,永远不会满足 Driver 的 reservation。

## 卸载

Phase 1 没有独立的 GoalBar 开关。从 web profile 中移除该插件以禁用所有包组件面,然后重启正在运行的 DSH 进程:

```bash
dsh plugin --profile web remove dsh-loopx-plugin
```

这会移除 GoalBar Host/Client 行、停止 Driver 并移除 `/loopx-init`;它不会移除 LoopX、其 registry、绑定、skills 或插件管理的运行时。只移除 LoopX 管理的 skills,运行:

```bash
loopx workflow-skills --uninstall \
  --skills-dir "${DSH_AGENTS_HOME:-$HOME/.agents}/skills"
```

在 DSH 停止且插件移除之后,可以独立删除隔离的 CLI 副本而不触碰 LoopX 状态:

```bash
DSH_LOOPX_RUNTIME="${DSH_AGENTS_HOME:-$HOME/.agents}/runtime/dsh-loopx-plugin"
test -f "$DSH_LOOPX_RUNTIME/loopx_cli.py" && rm -rf -- "$DSH_LOOPX_RUNTIME"
```

要在保留 LoopX 状态的同时回滚插件,移除它并安装之前保留的包 tarball,然后回读 profile。把占位值替换为升级前保留的旧 tarball 的确切路径:

```bash
RETAINED_PREVIOUS_DSH_LOOPX_TARBALL=/absolute/path/to/retained/previous-dsh-loopx-plugin.tgz
dsh plugin --profile web remove dsh-loopx-plugin
dsh plugin --profile web add "$RETAINED_PREVIOUS_DSH_LOOPX_TARBALL" --ignore-scripts
dsh --profile web --dump-config
```
