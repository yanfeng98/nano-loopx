---
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
execution: code
product_contract_source: owner-confirmed-design
---

# DeepSeek Harness 原生 LoopX Skill、Driver 与 GoalBar

> [English](2026-08-20-dsh-native-skill-driver.md)

## 目标

为一个可见的 DeepSeek Harness（DSH）Session 提供一小块原生 LoopX 表面：

- 插件启动时，在其 Loader 行就绪之前安装或修复 LoopX CLI 与面向 DSH 的 LoopX Skills；
  `/loopx-init` 仍是修复入口；
- `loopx` Skill 教会模型使用权威的 LoopX CLI；
- 一个全局加载但保持被动（passive）的 Driver，只有在该确切 Session 成功调用过 `loopx` Skill
  之后才具备资格，随后通过该确切的 live DSH Agent 继续 quota 批准的工作；
- 一个紧凑的 GoalBar 投影出确切的 Goal 绑定、Agent lane 进度与生命周期状态，并通过 LoopX
  生命周期变更提供 Start/Pause。

LoopX 仍然是唯一的 durable Goal、Agent、Todo、binding、quota、receipt、生命周期、进度与
scheduler authority。DSH 仍然是模型、工具、inbox、同会话执行与 UI-transport authority。

## 放置位置

- Capability owner：现有的 LoopX host 集成与 workflow-skill 安装契约。
- Provider：`packages/` 下可选的 `dsh-loopx-plugin` 包。
- 交付形态：extension 包，不是新的内置 LoopX capability。
- 该包拥有一个 DSH 命令、同会话 Driver、loopback Host 服务与紧凑的 web GoalBar。Host 与
  Client 是 LoopX 之上的薄投影与交互层；它们不引入模型工具、第二套控制面或插件自有的
  durable 业务状态。
- 现有 `loopx/dsh_goal_mode` 仍保持为独立的外部/headless `deepseek-harness` Turn 适配器。

## 公开 Host 名称

- 外部/headless 连接器：`deepseek-harness`，保留其现有 `dsh` 兼容别名。
- 可见的同会话集成：`deepseek-harness-native`，别名 `dsh-native`。

新集成不得挪用现有的 `dsh` 别名。

## 自动初始化与 `/loopx-init` 修复契约

插件的 init 行会自动运行类型化初始化序列，并在该行就绪前等待其完成。启动失败被缩减为安全的
stage/kind 诊断，不会导致 DSH 启动失败，并保留 `/loopx-init` 作为全局修复命令。自动启动不会
排队任何 Agent 输入，也不会消耗模型调用。对于显式修复，settled 的原生 `CommandResult` 仍然
是权威；有界的模型可见状态提示不参与安装或重载决策。

init 行只在该成功或安全失败 settle 之后发布类型化的 `loopxBootstrap` 服务。插件 patch 将该
服务加入现有的 Web server 与 Web runtime 注入列表，把 DSH 打印出的 URL 变成 host 可见的
readiness 边界。失败值只包含安全的 stage 与 cause kind；它释放 DSH 启动，但不授予 LoopX
readiness，也不隐藏修复命令。

该命令不接受自由格式输入。非法输入在产生任何 followup 或 CLI 探测之前就返回 usage 错误。
一次确切的调用执行以下有界序列：

1. 排队一个插件自己撰写的 start followup，欢迎用户并说明正在检查或安装 CLI 与 DSH
   workflow skills。
2. 探测一个可用的 `loopx` 可执行文件与 DSH 原生 workflow-skill 安装能力。
3. 如果 CLI 缺失或不兼容，执行一次固定 argv 的私有安装：
   `<compatible-python> -m pip install --upgrade --target
   <agents-home>/runtime/dsh-loopx-plugin/site-packages 'loopx>=0.5.4'`，并在该 target
   旁边写入受管理的 launcher。显式的 `PYTHON_BIN` 优先；否则插件探测 `python3` 与指定的
   Python 3.11-3.14 可执行文件，然后保留选中的解释器与 launcher 用于 readback、
   Driver/GoalBar 调用与生成的 skill 命令。这不会改动外部管理的系统 Python，也不会使用
   `--break-system-packages`。包的依赖要求是 `loopx>=0.5.4`，这是第一个既包含
   workflow-skill 资源、又能在受管理 runtime 使用的 Linux `pip --target` 安装之后发现这些
   资源的发布契约。
4. 再次解析得到的可执行文件；如果仍然不可用则失败。
5. 运行 `loopx workflow-skills --install --skills-dir ~/.agents/skills
   --host-surface deepseek-harness-native`。
6. 校验每个实际打包 skill 与 entry skill 的变更状态，并推导出类型化的 `skillsChanged`
   结果；缺失或未知状态在 `install_skills` 边界处 fail closed。
7. 运行只读的 workflow-skill 检查，并要求一个健康的受管理 readback。
8. 构造有界的权威 UI 结果。除非操作被取消，从同一类型化成功或失败事实排队一个 completion
   followup，然后返回原生结果。两个表面都不暴露原始 subprocess 输出或本地绝对路径。

一次有效且未取消的显式 `/loopx-init` 执行通常只增加两次模型调用：一次 start turn 与一次
result turn，初始化失败时也是如此。已取消的执行只留下已经排队的 start turn，非法输入不增加
模型调用。两个 followup 都指示模型不要调用工具、运行命令、重新安装或展开诊断。队列失败会
被安全记录，绝不重试，也不能改变原生结果或造成第二次安装变更。

当任一打包 skill 为 `created` 或 `updated`，或 entry skill 为 `created`、`updated` 或
`upgraded_legacy_managed` 时，`skillsChanged` 为 true。DSH 的 filesystem skill provider 会
使目录失效并对每个成功的变更热加载，无需重启。

健康的、兼容的 LoopX CLI 会被保留而不是升级。Subprocess 使用固定 argv、不经 shell、遵循
命令的 AbortSignal，并且绝不盲目重试。失败的包安装以可操作的命令错误返回。

初始化 followup 使用稳定的 `dsh-loopx-plugin/init-command` 插件 source，与
`dsh-loopx-plugin/driver` 不同。它们是普通竞争的插件输入，不是 Driver reservation；不会激活
Driver，也不会改变 Driver 的 admission authority 或命令屏障。

该命令不能安装定义了它自己的插件。`install.sh` 仍是源码 checkout 的插件 bootstrap，它告诉
用户启动 DSH 并使用 `/loopx`，不需要显式的初始化命令。当 DSH 配置了 `DSH_AGENTS_HOME` 时，
该命令使用其 `skills` 子目录；`~/.agents/skills` 是默认值。

## Workflow Skill 契约

扩展现有的 `workflow-skills` 命令，增加显式的 `deepseek-harness-native` host surface。
默认的 Codex 安装行为保持不变。

DSH 原生生成的 `loopx` entry 必须：

- 把完整的原始可见用户任务当作 `goalText`，不带 `/loopx` 命令层或语义路由外衣；
- 通过 DSH shell 工具调用 LoopX CLI，绝不通过插件模型工具；
- 传入 `--host-surface deepseek-harness-native` 与确切的不透明 `$DSH_SESSION_ID` 作为
  `--thread-id`；
- 严格遵循返回的 selection、registration、binding、Todo、quota 与 writeback 命令；
- 绝不猜测 Goal 或 Agent id，也绝不直接编辑 registry；
- 使用已安装的 `loopx-project` Skill 进行高级操作。

host 特定 entry 不能依赖 `$ARGUMENTS` 替换，因为 DSH 在保留原始用户消息的同时注入 Skill
instructions。`DSH_SESSION_ID` 是由活跃的 `agent.session.header.id` 推导出的 DSH 受管理
shell 事实；插件不会发明或持久化它。

## 绑定解析

复用现有的项目内 thread-to-Agent 绑定记录。只添加 Driver 所需的只读解析：

- 输入：project、`deepseek-harness-native` 与确切的 DSH Session id；
- 输出：无绑定、一个确切的 `{goal_id, agent_id}` 绑定，或类型化的歧义/不健康失败；
- 扫描已连接项目的 Goals，当多个绑定同时匹配时 fail closed；
- 绝不引入新的 sidecar、mirror、lease 文件或插件自有的 durable 绑定缓存。

Skill 拥有现有的显式 register/bind 命令编排。Driver 从不创建或更改身份绑定。

## 同会话 Driver

Driver 以 DSH 的目标轮次原生生命周期为模型，但消费 LoopX quota 而不是 `ctx.goals`。它的
服务随插件加载，从而可以观察类型化的 Session 事件，但加载、Agent 创建、Session 启动与
idle 状态都是被动的。激活前 Driver 只能折叠有界的内存内 Session 历史并清理本地工作；它不
执行任何 LoopX CLI、binding、quota、scheduler 或 heartbeat 调用，不创建 timer，也不排队
followup。

激活属于这一个确切的当前 Session，且只接受：

- 一个 `user/message` source，其 `kind: skill-invocation`、`name: loopx` 与
  `form: instructions` 都精确匹配；或
- 一个名为 `skill`（大写精确）的 `tool/call`，其参数解析为 exact `name: loopx` 的非数组
  JSON 对象，之后有一个由同一 call id 配对的成功 `tool/result`。

只有调用请求还不够。失败的、格式错误的、未配对的或被更替的模型调用都会 fail closed；
普通散文、skill 目录、shell 文本、`/loopx-init` 生命周期事件、插件撰写的 init 或 heartbeat
输入、已安装文件、CLI 存在性、registry、Goals 与已有绑定同样 fail closed。

Observation 与 Session 启动只会通过折叠该确切 Session 已有的类型化事件历史重建该资格投影。
替代或清空的 Session 不会继承前一个 Session 的激活。插件不存储 durable 激活记录，也不执行
迁移绑定扫描。没有可识别调用证据的较旧或已压缩 Session 保持未激活，直到在该 Session 中
至少调用一次已安装的 `loopx` Skill。

激活是意图而不是 authority。激活之后，在确切的 live Agent idle checkpoint，Driver：

1. 让位于普通的人或插件输入；
2. 从 LoopX 解析当前 Session 的绑定；
3. 使用已解析的 Goal/Agent 与一个稳定的 attempt identity 调用 `quota should-run`；
4. 停止、安排类型化的下一次唤醒，或向 LoopX 请求绑定到同一个确切 `turn_instance_id` 的
   canonical 薄任务体；
5. 在同一 Session 中为该自动 admission 至多排队一个 Driver 撰写的 `Agent.followup()`，
   并附上类型化的 LoopX continuation attribution；
6. 在排队的消息进入模型步骤之前，重新校验确切的 Agent、Session、reservation、竞争输入与
   绑定；
7. 要求该可问责任务执行 guard 投影出的类型化 settlement plan，其 writeback 与 spend 命令
   使用原始确切 turn identity 与确定性 effect id。

类型化的 DSH message source 是 durable attribution，用于把排队的消息与其 reservation
匹配。它不授予任何执行 authority：admission 与 settlement 仍需要匹配的 LoopX receipt 与
新鲜的 quota guard。

只有一个 Agent 本地的串行化求值与一个 pending 自动 reservation。自动 reservation 被 admission
前，人输入优先。插件重载、Agent 更替、Session 启动/fork、取消与命令执行都会使未 admission
的工作失效。Driver 不存储 durable 生命周期状态，也不暴露公开协调器。

进程内激活投影只为这一个 Session 接受一次求值。它不创建绑定、不选择 Goal 或 Agent、不花费
quota，也不授予工具 authority。durable 的精确绑定加上新鲜的 LoopX quota 仍然是 continuation
authority；激活之后，现有的 scheduler/heartbeat、reservation、串行化、人优先、取消与
pre-step 重新校验契约保持不变。

## Retry 归属

- DSH `dsh-llm-retry` 拥有 provider/model 请求重试。
- LoopX Driver 只负责它自己的 CLI 调用。
- Resolve 与 task-body 读取在首次尝试后最多可重试两次，仅限 timeout/transport 失败。
- `quota should-run` 只能以完全相同的确切 `turn_instance_id` 使用同一有界重试；LoopX 的
  heartbeat receipt 使该回放幂等。类型化的失败响应是权威的，不重试。
- 类型化的 permanent、identity、ambiguity、malformed-output、cancellation 与 unknown-write
  结果不重试。
- 有限重试预算耗尽后，Driver 停止该自动求值。它不维护八次失败的 breaker，也不维持无限重试
  循环。

## 插件安装器

保留现有的 `install.sh` 方法：

1. 校验 Node、pnpm、包名与包版本；
2. 安装锁定依赖并构建/打包 tarball；
3. 在 DSH `web` profile 中安装或更新 tarball；
4. 读回 profile，并按依赖顺序精确校验 `loopx-init` 命令行与 Driver 行；
5. 保留构建产物，并把启动 DSH 与使用 `/loopx` 打印为下一步动作。

安装器不再要求在安装插件之前 LoopX 已经存在。

## 从设计中显式移除的部分

- `/loopx` 命令语法与语义 fallback；
- 面向模型的 `loopx_*` 工具；
- provider-neutral 的模型执行 Service 抽象；
- 协调器 registry 或 durable 的公开/私有协调器协议；
- sidecar 状态、插件自有的 durable 激活状态、激活 epoch 与失败抑制计数器；
- 自定义操作 receipts 与规划检查点；
- `switchConfirmation` 与插件自有的 Goal 切换；
- 代表模型散文执行的裸 CLI 或 registry 变更。

紧凑的 GoalBar 不被这些排除项移除。它只拥有进程内 waiters、动作串行化、watch 游标、
pending UI 状态与错误状态。绑定、生命周期与进度从 LoopX 重建；DSH Session 事件与 Agent 状态
只唤醒或更新 live transport 视图。

## 验证

聚焦验证必须覆盖：

- `/loopx-init` 的健康跳过、缺失 CLI 安装、不兼容 CLI 修复、包失败、Skill 失败与 readback
  失败，且至多一次安装变更；
- 自动启动在 readiness 前等待同一成功初始化，立即暴露 skills，隔离安全失败同时保留修复命令；
- 非法 init 参数不产生 followup 或探测；start/result 顺序；未取消成功或失败时两个 followup；
  取消时只有 start followup；followup 队列失败保留原生结果；
- 实际 `created`、`updated`、`unchanged` 与 `upgraded_legacy_managed` skill 状态投影、
  无需重启的热加载，以及不完整或未知状态 fail closed；
- init followup source 与 Driver reservation source 隔离、有界的安全消息，无原始 subprocess
  输出或本地绝对路径；
- DSH 原生生成的 Skill 文本、确切 host/session 标志，以及不依赖 `$ARGUMENTS`；
- 外部 `deepseek-harness`/`dsh` 兼容性；
- 零/一/歧义的 Session 绑定解析；
- 插件加载、Agent 创建、Session 启动、普通事件与重复 idle 转换在激活前保持零 runner 调用
  与零 timer；
- 确切用户与成功配对的模型 `loopx` Skill 激活、从类型化当前 Session 历史恢复、跨 Agent
  隔离、替代 Session 重算，以及 fail-closed 的否定调用形态；
- 没有可识别证据的旧式或压缩 Session 保持未激活，直到在每一个目标 Session 中至少调用一次
  `loopx`；
- 激活后的 idle admission、人输入优先、确切 reservation 检查、Agent 或 Session 更替、命令
  冲突、取消、等待调度，以及每次自动 admission 至多一个 Driver followup；
- 在 quota admission、heartbeat task、类型化 DSH source、两个 pre-step 检查、类型化
  settlement plan、durable writeback 与 quota spend 之间保持一致的一个确切 turn identity，
  且只有一个幂等 receipt、没有未绑定的 fallback spend；
- 有限 CLI 重试配合稳定 quota 幂等性，不安全结果不重试；
- Host/Client 重启后 GoalBar 重建、强制权威重读的 source 事件、不能创建业务状态的
  runtime-only 事件、陈旧绑定拒绝、串行化生命周期变更与变更后 readback；
- 内置 tarball 安装与真实 DSH profile readback 包含预期的 command、Driver、Host 与 Client
  面。

## 完成定义

- 用户安装插件、启动 DSH，无需单独的初始化命令或重启即可调用 `/loopx <task>`;
  `/loopx-init` 保持为有界的显式修复路径。
- 成功的 skill 创建、更新或受管理的 legacy-entry 升级通过 DSH 的 live skill 目录可见，
  无需重启。
- 通过 `loopx` Skill 处理的任务使用权威 CLI 调用，而不是插件 `/loopx` 命令、语义路由或
  模型工具。
- 未激活的 Session 不执行任何 LoopX 调用或 timer 工作；只有成功调用过的 `loopx` Skill 才会
  激活那个确切 Session。
- 一个激活的、已绑定的可见 DSH Session 只通过其确切的 live Agent 继续新鲜 quota 批准的
  工作，从 admission 到 durable writeback 与 spend 保持一个确切身份。
- 没有确切绑定时 GoalBar 保持隐藏，重启后从 LoopX 重建，并且绝不成其为
  Goal/Todo/生命周期 authority。
- 现有的外部 DSH Turn 模式保持兼容。
- 被否决的模型工具、绑定 sidecar 或 durable 插件状态设计不得残留在生产代码或公开指南中。
