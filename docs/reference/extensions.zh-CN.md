# 扩展与能力

> [English](extensions.md)

Capability 与扩展是 LoopX 中的独立维度:

- **capability** 描述 LoopX 能做什么,以及暴露给调用方的产品合同;
- **extension** 是一个可以提供一种或多种 capability 的交付单元,拥有自己的安装、启用、停用与升级生命周期。

内置 capability 与扩展提供的 capability 共享同一个 registry。实现目录不会仅仅因为位于 `loopx/capabilities/` 之下就成为 capability;注册是显式的。

```text
LoopX Core
|-- capability 合同
|-- 内置 capability 注册
`-- extension runtime
      |-- extension A -- 提供新 capability
      |-- extension B -- 实现核心 capability
      `-- extension C -- 保持禁用
```

## Runtime 职责

Capability 与扩展是代码与交付边界。在 runtime 中,保持四种职责彼此区分:

| 职责 | 合同 |
| --- | --- |
| Agent | 通过 host/runtime 与可用 capability 规划并执行一个有界动作。 |
| Provider | 调用外部系统并返回有界 observation、effect 结果或回读。 |
| Capability | 规范化 provider 输出,应用域策略与验证,并提议有限的转换。 |
| LoopX Kernel | 接受或拒绝该提议,并拥有持久的 todo、gate、monitor、写回、配额、恢复与调度状态。 |

正常流程是:

```text
Agent -> Capability -> Provider -> external system
Provider readback -> Capability transition proposal -> LoopX Kernel
```

### Agent 作用域的外部事件连接器

`loopx.extensions.external_connector_runtime` 定义交互式群消息与文档评论流共享的 provider-neutral 绑定。它把来源与 cursor 引用保留在 owner 本地,同时暴露一个无内容的 status 投影,包含来源种类、capture 策略、ingress 策略、响应策略、生命周期与声明的操作。

该合同把三个独立决策分开:

- capture:寻址事件、来自一个已配置来源的所有事件,或增量来源流;
- ingress:实时转向、同一会话的有序队列,或 Agent 作用域的异步 inbox;
- response:不响应、源线程响应、主题响应,或已配置的 mirror。

实时转向与会话队列绑定需要精确的一个 Agent session;异步 inbox 绑定需要一个 owner 本地 inbox。历史补齐需要 cursor 引用。具备响应能力的 provider 必须同时声明写入与回读支持。

确认(ACK)是独立的 fail-closed 决策。LoopX 只在已提交的持久 effect(包括显式无后续 effect)之后,以及在需要响应时验证过的 provider 回读之后,才允许 ACK 与 cursor 推进。对于有序的工作会话投递,已完成并持久化的会话 Turn 是最小的 effect receipt;异步 inbox 需要自己的已接受写回或显式无后续 receipt。原始事件主体、作者身份、来源引用、cursor 值与 provider payload 不进入 status 投影。

Agent 绑定的 Lark Goal Topic 路径是第一个调用方。旧的仅 Goal 绑定保持可读,而新的实时、排队与异步 Agent 绑定在持久化泛型 Connector 合同的同时保留其 provider 特定的路由数据。该 runtime 合同本身不是新的 capability registry 条目;provider 通过其现有扩展与 capability surface 宣传稳定的调用方结果。

对于异步来源,同一模块提供 owner 本地的增量 inbox runtime。provider 把一个有界 page 转换为 `agent_external_connector_event_v0` envelope,并用之前精确提交的 cursor 调用 capture 操作。Capture 对稳定事件 id 去重,应用声明的寻址/全来源过滤器,在私有存储中保留文档锚点与回复链引用,并分配重启安全的顺序。在该 page 的所有已接受事件结算之前,page cursor 保持待处理;完全被过滤的 page 可以立即建立检查点,因为它不包含已接受的 Agent 输入。

绑定的 Agent 按该顺序清空待处理事件。结算拒绝乱序事件并调用公共 ACK 决策,因此缺失的持久 effect 或必需的 provider 回读会使事件与 cursor 都保持待处理。只有成功的结算才把事件记录为已确认,而且只有捕获 page 的最后一个已接受事件才推进其 cursor。该状态持久提交后,已处理的私有事件主体被移除;其无内容身份仍可用于重放去重。Provider 失败以无内容的错误码存储。公开 inbox 投影只暴露待处理数量、最长等待时长、失败数量与新鲜度;事件 id、主体、锚点、回复链、来源引用与 cursor 值保持 owner 本地。

`loopx.extensions.external_connector_provider` 为文档评论添加 fail-closed 的 provider 调用边界。文档评论注册必须引用单独注册过的材料;评论流保持 `external_input_only`,不能自我提升为项目权限。精确的 provider 身份、scope、发布要求与官方 HTTPS 修复 URL 保留在 owner 本地的权限指南中。Status 只暴露无内容的就绪度与操作计数。指南必须与 Connector 持久化的精确要求匹配,并且当响应策略需要时,这些要求必须覆盖历史捕获以及响应写入与回读。

Provider 调用顺序是:权限评估、有界 page 读取、持久 inbox 捕获、Agent effect、带回读的 provider 响应,然后 ACK。Runtime 直到注册权限就绪才调用 page reader,在已提交 effect receipt 之前不调用响应写入器,直到 event 绑定响应 receipt 与 provider 回读成功才推进 cursor。具体的 provider adapter 提供 page reader 与响应写入器;LoopX 不拥有它们的凭据或原始 payload。

随附的 Lark 扩展通过 `lark-cli` 提供第一个具体的文档评论 adapter。它的 owner 本地 target 把一个安全的 Connector 来源引用绑定到私有文档 URL、profile 与 bot 或用户身份。adapter 探测精确的评论读取/创建 scope,用重启安全的私有 cursor 分页评论卡片与嵌套回复,并把稳定回复 id 映射为哈希后的 Connector 事件 id。完成的扫描从第一个评论 page 重新开始,因此旧卡片上的新回复仍然可发现;泛型 inbox 对已捕获或已确认的事件去重。由于 Lark 不为回复创建暴露 provider 幂等性,adapter 需要 owner 本地的 receipt 存储:写入前记录意图,崩溃后通过其不透明幂等标记恢复回复,回读前记录返回的回复 id,并在重试时复用该 receipt。评论列表快捷方式要求 `lark-cli` 1.0.69 或更新版本。公开 status 与 provider receipt 省略文档 URL、profile、原始 id、cursor 值、主体与子进程输出。

Lark adapter 刻意拒绝 `addressed_only`。正确的提及过滤需要显式的 provider 身份合同,而把已配置文档上的每条评论都视为 Agent 提及会静默削弱泛型 capture 策略。已配置来源与增量绑定仍然受支持。源线程响应绑定还会过滤已解决的和整文档评论卡片,而 Lark 回复 API 不允许对这些卡片回复。

`Provider` 是实现角色。当它实现 LoopX capability 时,它注册在该 capability 之下;独立的扩展 provider 也可以只暴露自己的有界命令。Provider 可以内置在 LoopX 中,也可以由扩展交付。`Extension` 不是第五个 runtime 角色:它拥有 provider 打包、安装、启用、升级与兼容性生命周期。它不拥有域转换策略或 Goal 状态。域状态与 receipt 是跨越这些边界的数据,不是独立参与者。

## 仓库布局

仓库为每个所有权边界使用一个路径:

```text
loopx/capabilities/<capability>/   面向调用方的合同与核心 providers
loopx/extensions/                  扩展生命周期与随附 providers
packages/<package-id>/             可独立安装的发行包
```

`loopx/extensions/` 是随 LoopX wheel 分发的 Python 包。`packages/` 是 monorepo 包根目录;其子目录有自己的打包元数据,不成为 LoopX wheel 的一部分。仓库根目录刻意没有 `extensions/` 目录。这个重复名称曾经模糊了路径代表可导入的 LoopX 代码还是可独立安装的制品。

该布局不合并 capability 与扩展。它们保持为独立轴,并通过 capability/provider registry 组合:capability 命名稳定的结果合同,扩展拥有 provider 交付与生命周期。

## 注册模型

每个已注册 capability 声明三个面向 provider 的字段:

- `origin`:`builtin` 或 `extension`;
- `visibility`:`public` 或 `internal`;
- `provider_id`:`loopx-core` 或扩展 manifest id。

内置 catalog 仍然是默认来源。扩展 manifest 声明 provider 与合同;每个 provider 是否已安装、已启用且 doctor 就绪,唯一来源是扩展 runtime 状态。重复的 capability 或 provider id 会 fail closed。内部注册对 registry 保持可用,但被从公开 catalog 中省略。

Catalog 发现不扫描任意目录,也不导入扩展 Python 代码。调用方可以在 catalog 读取时附加一个仅声明式的 manifest:

```bash
loopx capability list \
  --extension-manifest /path/to/extension.toml \
  --format json

loopx capability show lark-kanban \
  --extension-manifest /path/to/extension.toml \
  --format json
```

结果 provider 报告 `declared=true` 且 `installed=enabled=ready=false`。常规 CLI 读取也会从 `<runtime-root>/extensions/state.json` 组合已安装 provider,因此 catalog 与 runtime 分发看到相同的活跃 manifest 修订。`loopx extension` 只在 manifest、API、权限与 doctor 检查通过后,才注册一个已安装的子进程 entrypoint。它不下载包,也不授予新权限。

## Starter 与脚手架

通过同一个管理 surface 创建下一个独立扩展。该命令默认预览,只有 `--execute` 才写入:

```bash
loopx extension init loopx-example --format json
loopx extension init loopx-example --execute --format json
```

默认目标是 `packages/<extension-id>`。当 provider 在另一个包或仓库中开发时,使用 `--destination`。脚手架创建一个可独立安装的 Python 包、声明式 manifest、JSON stdin/stdout provider、带版本号的请求与响应 JSON Schema、无副作用的 doctor、示例请求与简短 README。生成的 provider 在任何工作之前拒绝缺失、不匹配或结构无效的请求合同。init receipt 明确标识该 starter 为 `standalone`,并把 `loopx extension run` 指定为其受管入口点。

`extension init` 刻意不注册 capability。它目前只生成完整的独立路径。`[[provides]]` 扩展需要真实的调用方合同与命令,而 `[[implements]]` 扩展需要现有的 capability 特定 resolver、策略检查、action/scope 映射与执行 envelope adapter。泛型脚手架无法安全推断那些权限语义。先添加 capability 集成 profile,再对照该 profile 脚手架化或编写 provider;不要添加可被发现但不可调用的 manifest 表。

该命令拒绝所有已存在的目标,包括空目录;没有强制或合并模式。它也不构建、安装、注册或启用生成的 provider。这些仍然是显式生命周期步骤,使包管理器与 LoopX 激活状态不会落后于一条命令:

从同一个已激活的 Python 环境运行所有三条命令。LoopX 通过其已安装的 console entrypoint 验证 provider,因此把包安装到不同环境会正确地以 `entrypoint_missing` 失败。

```bash
python3 -m pip install packages/loopx-example
loopx extension install \
  --manifest packages/loopx-example/extension.toml \
  --execute \
  --format json
loopx extension run loopx-example \
  --input-json packages/loopx-example/examples/request.json \
  --execute \
  --format json
```

把生成的响应视为可执行文档,而不是永久的域合同。在产品化 provider 之前,把 starter 的请求、响应、权限与 doctor 语义替换为有界的领域特定语义。

## Runtime 生命周期

生命周期是本地、显式的,并默认 dry-run:

```bash
# 检查随附的 OpenViking pilot,仅当 doctor 通过时才激活它。
loopx extension install \
  --bundled openviking-semantic-preference \
  --execute \
  --format json

loopx extension list --format json
loopx extension doctor openviking-semantic-preference --execute --format json
loopx extension disable openviking-semantic-preference --execute --format json
loopx extension enable openviking-semantic-preference --execute --format json

# 使用 lark-inbox 之前激活随附的 Lark 生命周期 provider。
loopx extension install --bundled loopx-lark --execute --format json
```

当安装、更新或回滚改变了活跃 LoopX release 后,作为一个有界的只读批次重新验证所有已启用扩展 runtime:

```bash
loopx extension doctor --all-enabled --execute --format json
```

本地安装器自动运行该批次。通过的 doctor 只刷新本地 runtime 身份证明;它不授予新的 provider 权限,也不执行任何连接器写入。失败的 provider 保持 fail closed,且批次会指明精确的修复命令。

对于单独分发的 provider,传入 `--manifest <extension.toml>`。`upgrade` 在改变活跃修订之前验证并探测新 manifest。`rollback` 在切回之前探测先前修订。失败的探测使当前修订保持不变。激活状态在私有的 LoopX runtime 根目录中包含经过验证的 manifest 快照与修订 id;不包含 provider 输出或凭据。

独立扩展使用与内置 capability 相同的受管命令形态:LoopX 接受有界请求,默认预览,只有 `--execute` 才执行,并返回结构化 receipt。v0 调用合同是:

```bash
loopx extension run <extension-id> --input-json <path-or-> [--execute]
```

活跃 manifest 固定可执行文件、参数、协议、权限、超时与修订。调用方通过 stdin 提供一个 JSON 对象,provider 必须通过 stdout 返回一个 JSON 对象。LoopX 不接受任意可执行路径或参数透传。`run` 永远不会安装缺失的扩展,并拒绝带 `[[provides]]`、`[[implements]]` 或任何已声明权限的扩展;这些 provider 通过其 capability 或域命令调用。扩展生命周期管理是共享的,但直接执行保留给零权限、仅 runtime 的独立扩展。直接 provider 二进制是实现与调试 surface,不是受支持的受管 API。

### Goal 绑定的外部 capability provider

拥有新域 capability 的扩展可以向其 `[[provides]]` 记录附加一个相对 JSON `integration_profile`。LoopX 在 manifest 安装期间读取、验证并快照该 profile;之后的调用只解析已启用、doctor 就绪的活跃修订。profile 是数据,不是导入或可执行路径。

```toml
[runtime]
protocol = "requirement_projection_provider_v0"
entrypoint = "example-requirement-provider"
required_permissions = ["requirement.read"]

[[provides]]
id = "requirement-delivery"
kind = "requirement_delivery"
title = "Requirement delivery"
visibility = "public"
integration_profile = "integration-profile.json"
```

```json
{
  "schema_version": "loopx_external_domain_capability_profile_v0",
  "capability_id": "requirement-delivery",
  "protocol": "requirement_projection_provider_v0",
  "operations": [
    {
      "id": "observe",
      "effect_class": "read_only",
      "required_permission": "requirement.read",
      "request_schema": "loopx_external_domain_capability_request_v0",
      "result_schema": "loopx_external_domain_capability_result_v0"
    }
  ]
}
```

持久的 Goal 绑定为一个精确的活跃 provider 修订启用有界操作。它是 Goal 作用域而不是 Turn 作用域,因此同一个工作 Agent session 可以复用已启用的只读 capability,而不会为每次 observation 创建受治理的 Turn。先预览绑定,再把它持久化到项目 registry 的 Goal 记录中:

```bash
loopx --registry .loopx/registry.json capability bind requirement-delivery \
  --goal-id example-goal \
  --operation observe

loopx --registry .loopx/registry.json capability bind requirement-delivery \
  --goal-id example-goal \
  --operation observe \
  --execute
```

LoopX 在创建绑定时解析已启用、doctor 就绪的 provider。持久化的 `goal.external_capability_bindings` 条目具有以下 typed 形状:

```json
{
  "schema_version": "loopx_goal_external_capability_binding_v0",
  "goal_id": "example-goal",
  "capability_id": "requirement-delivery",
  "operations": ["observe"],
  "provider": {
    "extension_id": "example-requirement-provider",
    "revision": "sha256:active-revision",
    "profile_digest": "sha256:integration-profile"
  }
}
```

通过解析持久 Goal 绑定来预览或执行只读操作:

```bash
loopx --registry .loopx/registry.json capability invoke requirement-delivery \
  --operation observe \
  --goal-id example-goal \
  --input-json provider-input.json

loopx --registry .loopx/registry.json capability invoke requirement-delivery \
  --operation observe \
  --goal-id example-goal \
  --input-json provider-input.json \
  --execute
```

输入对象包含 `context_refs` 加上一个有界的域 `input` 对象。LoopX 检查所请求的 capability 与操作是否已为 Goal 启用,以及 provider id、活跃修订与快照 profile 摘要是否仍然匹配。绑定摘要加有界输入推导出确定性的调用 id。受管 runtime 限制仍然适用。`--goal-binding-json` 仍作为兼容性与调试输入可用,但常规执行应从 `--goal-id` 解析绑定,使 LoopX registry 保持为任务的事实来源。

直接的 `capability invoke` 路由只接受只读操作:provider 结果不得包含域变更、转换提议、effect receipt、原始 payload、类凭据字段或看似私有的字符串。它不写 LoopX 状态,也不消耗配额。

集成 profile 也可以声明 `effect_class: external_write`,但该操作刻意不能通过直接调用使用。host adapter 必须调用 `loopx.extensions.governed_capability_execution` 中的治理物化生命周期:

外部写入操作除 `effect_class` 外还声明一个 typed `todo_contract`,包含一个或多个 lower-snake `action_kinds` 与有界 `target_key_prefixes`。

当长期运行的 provider 需要 LoopX 持续轮询其外部任务时,同一操作可以声明一个 `transition_contract`。这是权限允许清单,不是 provider 拥有的 Todo schema:

```json
{
  "proposal_kinds": [
    "continuous_monitor_upsert",
    "continuous_monitor_complete"
  ],
  "monitor_key_prefixes": ["example-provider:"],
  "monitor_action_kinds": ["poll_external_run"],
  "monitor_target_key_prefixes": ["external-run:"],
  "monitor_required_capabilities": ["network"]
}
```

profile 限制 provider 可能提议的每个 monitor 身份、动作、外部目标与必需 capability。超出这些边界的提议会在任何 LoopX 状态写入之前失败。provider 不接收 registry 路径,也从不直接调用 Todo API。

1. 为一个精确 Goal、Agent、Todo 与 `turn_instance_id` 获得 `quota should-run` 准入;所选开放 Agent Todo 的 `action_kind` 与 `target_key` 必须匹配操作 profile 的 `todo_contract`,因此已准入的 Turn 不能借用无关的 Goal 绑定写入 capability;
2. 调用 `start_governed_external_capability(...)`,它在分发前记录意图,并把结算 effect id 作为 provider 的稳定幂等 key;
3. 调用 `reconcile_governed_external_capability(...)`,直到 provider 返回终态 `loopx_external_effect_receipt_v0`;
4. 让 LoopX Kernel 通过常规 Todo API 物化已准入的 monitor upsert。`running` 结果只能创建或重定向其有界持续 monitor,因此外部操作或其结算未完成时,恢复条目保持可调度;
5. 提供 typed 写回与消耗回调。LoopX 复用共享 Turn 结算驱动,在持久写回中要求 effect receipt 摘要,并且在该写回提交之前从不消耗配额;
6. 只有在共享 Turn 结算提交之后,才让 Kernel 物化已准入的终态 monitor 完成。因此失败的写回或消耗会让 monitor 保持开放以支持恢复,而不是关闭唯一的重试通道。

provider 可以返回 `running`,因此服务端任务可以比有界 provider 进程存活更久。start 与 reconcile 可以从 mode-0600 的 journal 分别重放。精确 provider 修订、请求摘要、Goal 绑定、结算标识、转换提议 receipt、provider effect receipt、写回 receipt 与配额 receipt 保持附加在同一次调用上。每个物化提议都立即建立检查点。Monitor upsert 属于结算前阶段;monitor 完成属于结算后阶段。任一 Todo 写入与其检查点之间的崩溃会通过提议的稳定 monitor key 与完成标识恢复,而不是重复工作。外部 effect 之后的崩溃会用同一幂等 key 重放,并重新对账 receipt,而不是开始无关操作。一个结算 effect id 恰好拥有一次物化调用:重试同一请求会重放它,而在同一 Turn receipt 下尝试不同操作或输入会在 provider 分发之前失败。新调用还要求 `should_run=true`;在可运行决策改变后,现有 journal 仍可用其精确 typed receipt 恢复。

转换提议刻意比任意 Goal 变更更窄。第一个版本只支持持续 monitor 的 upsert 与完成。它不能创建通用推进 Todo、变更 Goal、扩大 capability 权限、完成其他 Agent 的工作,或重新打开已完成的 monitor。Kernel 通过其已准入绑定 key 解析一个精确 monitor,应用常规所有权与完成规则,并返回内容有界的 receipt。

仅启用 Goal 永远不会授予写入权限。创建或更新绑定是显式 Goal 配置变更:它使用 preview/apply,但不创建 Turn,也不消耗 Turn 配额。只有当调用可能产生物化的外部或 LoopX 状态 effect 时,才进入 Turn 作用域。Goal 绑定是本地 typed 投影,不是安全令牌或远端签发者证明;服务认证与授权仍然是 provider 的责任。

泛型 runner 刻意无 effect,不授予任何操作 effect。manifest `permissions` 与 runtime `required_permissions` 必须都为空。任何需要读取、写入、发送、发布、管理或其他已声明权限的操作,都必须通过一个能在受管分发之前应用其域策略的 capability 或域命令进入。请求文件与 stdin 在读取时被设上限。Provider stdout 与 stderr 被并发排空,provider 在专用进程组中启动。超时或任一输出上限会终止整个进程组,因此后代进程不会在 LoopX 报告执行已停止后继续产生 effect。

有 effect 的 capability 分发使用 `loopx_extension_execution_envelope_v0`。在解析一个已启用、doctor 就绪的实现并检查域激活策略后,由 capability 命令(而不是调用方或 provider)创建这个最小 envelope。它绑定:

- 精确的 action;
- 结构化的 effect scope;
- 扩展 id 与活跃 manifest 修订;
- 排除所附 envelope 的精确 provider 请求摘要。

provider 在任何 effect 之前重复这一验证。调用方提供的 envelope、不同的请求、更宽的 scope、改变的 action 或不匹配的活跃修订都会 fail closed。capability id、协议与权限在 manifest 解析中保持权威,而不是在 envelope 中重复。envelope 是请求绑定,不是签发者身份证明、安全令牌,也不是服务端认证与授权的替代品。

`disable` 是可逆的,但 `enable` 从不信任早期的就绪结果:它重新运行配置的 doctor,并且只有在该探测成功后才修改启用位。成功的 doctor 把就绪度同时绑定到活跃 manifest 修订与内容寻址 runtime 身份。把未变更 release 移到新安装根目录、inode 或等效解释器路径会保留该身份;可执行文件、解释器或 Python 模块内容改变后会 fail closed,直到新的执行 doctor 成功。失败的执行 doctor 清除过期证明,而不切换修订。

已启用实现通过 capability id 与带版本协议解析,然后对照其声明权限、当前修订与当前 doctor 证明检查。调用方不需要把扩展 id 复制到常规配置中。禁用或过期的实现在 catalog 中保持可见,但不是分发候选。当多个已启用、doctor 就绪的扩展实现同一 capability/协议对时,解析 fail closed,直到调用方在迁移期间选择预期 provider。域配置可以添加有界 provider 参数,但不能替换 manifest 入口点、超时、协议或权限合同。

兼容性 delegate 使用相同的修订绑定就绪规则。每个已配置的 `loopx lark-inbox` 操作都会在进入进程内 provider 代码之前解析已启用的 `loopx-lark` provider、其当前 doctor 证明以及该操作所需的权限。因此禁用扩展会阻止新的 collector 启动、drain、ingest、回复与确认操作;升级与回滚影响新的调用,而不改变项目配置。扩展生命周期命令不会终止已在运行的 host 管理 collector 进程;改变活跃 provider 修订时,请单独停止或重启该 supervisor 服务。

Quota 与 Turn 组合应用相同的读取 gate。它们只在解析 `lark.inbox.read` 之后注入 Lark 扩展的紧急度投影器;provider 的 profile/chat schema 与私有配置读取保持在扩展中。如果扩展缺失、禁用或过期,紧急度不可用,也就不能激活 Lark 工作通道。这不会增加面向 Agent 的 CLI 参数。

## 呈现 Surface

独立交付的扩展可以声明面向运营者的呈现 surface,而不必随附浏览器代码,也不必让 Core 理解 provider 的域。provider 拥有来源验证、`view_schema` 合同以及到该 schema 的映射。Core 拥有生命周期解析、修订绑定、持久化与公开安全 surface catalog。每个声明的 surface 用 `module:callable` 引用命名其验证器。发布进程在接受 provider view 之前加载该精确 callable;缺失或无法加载的验证器会 fail closed。Core 不会把任何单一域的 view 冻结进 core。Dashboard 的通用状态解析器只消费那个紧凑合同。内置 renderer 可以单独拥有 provider view schema,如 Finance renderer 对 `decision_research_dashboard_v0` 所做的那样。

Finance 价值发现扩展声明了第一个这样的 view,`decision_research_dashboard_v0`,一个只读的决策研究 view:

```toml
[[presentation_surfaces]]
id = "investment-research"
kind = "decision_research_dashboard"
title = "Investment Research"
view_schema = "decision_research_dashboard_v0"
view_validator = "loopx_finance_value_discovery.presentation_view:validate_decision_research_view"
visibility = "public-safe"
empty_state_title = "No validated research yet"
empty_state_detail = "Publish a validated projection."
```

声明是严格且有界的。Surface id 是稳定的 kebab-case 标识符。标题与空状态文本是纯文本,不含 markup、URL 或本地路径。声明本身不会让 surface 可见:扩展必须在活跃 manifest 修订上已安装、已启用且 doctor 就绪。

发布使用与独立扩展调用相同的受管、默认 dry-run 生命周期 gate:

```bash
loopx extension publish-projection \
  <extension-id> \
  <surface-id> \
  --input-json <validated-owner-input.json> \
  --format json

loopx extension publish-projection \
  <extension-id> \
  <surface-id> \
  --input-json <validated-owner-input.json> \
  --execute \
  --format json
```

预览解析活跃声明,但不运行 provider,也不写入文件。使用 `--execute` 时,LoopX 运行精确的就绪 provider,验证其 `extension_presentation_projection_v0`,从生命周期状态绑定扩展 id、活跃修订、surface 种类、schema 与可见性,然后原子写入一个 `extension_projection_surface_v0` envelope。receipt 包含标准 payload SHA-256,并确认精确回读。如果在发布过程中生命周期身份或声明发生变化,写入会 fail closed。

Status 收集从不执行 provider、不读取其 owner 输入,也不因扩展行而扩大 Dashboard 状态热路径。loopback 状态服务器提供一个冷路径 surface catalog 端点,只读取活跃 manifest 快照与持久化的有界 envelope。`ready` 或 `review_due` catalog 条目携带内容寻址的 `detail_ref`(扩展 id、surface id、修订与 payload SHA-256),而不是内联完整 provider view。需要该 view 的消费者使用单独广告的投影端点。该读取在返回 `public-safe` 投影之前会重新验证活跃扩展修订、声明的 surface、持久化 envelope 与 payload 哈希。由于端点没有已认证受众合同,投影读取拒绝 `owner-only` surface,而不是把 loopback 访问视为 owner 认证。可见性遵循以下矩阵:

| 生命周期或投影状态 | 冷路径 surface catalog | Dashboard |
| --- | --- | --- |
| 未安装、已禁用或 doctor 过期 | 无条目 | Tab 与首页摘要隐藏 |
| 就绪声明,无匹配活跃修订文件 | `empty` | 声明式空状态 |
| 有效的活跃修订 envelope | 带 `detail_ref` 的 `ready` | 只读 view 与摘要 |
| 超过 `review_due_at` 的有效 envelope | 带 `detail_ref` 的 `review_due` | 保留 view 并附评审警告 |
| 损坏的活跃修订 envelope | 无 `detail_ref` 的 `invalid` | 安全诊断,无部分内容 |
| 文件属于其他修订 | `empty` | 不回退到旧内容 |

禁用会隐藏 surface,但不删除其投影。重新启用并成功重新运行 doctor 会恢复匹配修订的投影。升级为审计连续性保留旧文件,但新修订在看到自己发布的 envelope 之前一直为 `empty`。回滚应用同一条精确修订规则。

呈现投影是展示接收端,不是权限。它们不能改变 Goal 状态、推广方法、提交交易或授予 provider 权限。Finance 研究 view 拒绝凭据、账户或订单字段、原始 provider/请求/响应主体、私有相对或绝对路径、敏感 URL 参数、非有限数字与无界文本。标准持久化只使用标准 JSON;`NaN` 与 infinity 在发布前 fail closed。Provider 必须输出紧凑引用与结论,而不是私有证据主体。Dashboard 路由同时用扩展 id 与 surface id 标识 surface,因此独立版本化的 provider 可以复用本地 surface id 而不冲突。`public-safe` surface 仍然通过公开/私有扫描;`owner-only` surface 描述运营者边界,永远不会是持久化机密或绕过该扫描的权限。

改变本合同后,运行公开的合成生命周期证明:

```bash
uv run --extra test python examples/extension-presentation-surface-smoke.py
```

## 面向 Agent 的放置决策

创建目录之前,LoopX 或执行中的 Agent 必须按顺序回答这些问题:

1. **正在添加或改变的是什么用户结果与调用方可见合同?** Capability id 描述结果,而不是传输。`connector`、`provider`、`adapter` 或 `sink` 这类名称通常描述扩展或内部机制,除非调用方把该机制作为独立产品合同使用并验证。如果现有 capability 已拥有该合同,把实现加入 `loopx/capabilities/<existing-capability>/`,而不是创建兄弟目录。
2. **LoopX core 是否必须始终随包分发并维护该实现?** 如果是,它可以是内置 capability。新的内置 capability 需要稳定 id、真实的入口点或协议调用位点、聚焦验证与 catalog 注册。
3. **实现是否需要独立的安装、启用、停用、升级、依赖、凭据或 provider 所有权?** 如果是,它就是扩展 provider。capability 仍然是合同;扩展 manifest 声明它提供该合同。
4. **这只是一切扩展共享的注册或生命周期机制吗?** 把该机制放在 `loopx/extensions/`,而不是 provider 包中。
5. **这只是一个内部辅助吗?** 把它放在距离其变更原因最近的模块中。不要注册 capability,也不要创建扩展。

回答完这些问题后,使用这张放置映射表:

| 变更 | 放置位置 |
| --- | --- |
| 现有内置 capability 行为 | `loopx/capabilities/<capability-id>/` |
| 内置 catalog 与注册合同 | `loopx/capabilities/catalog.py` 或 `registry.py` |
| 泛型扩展 runtime | `loopx/extensions/` |
| 同仓可选的扩展分发 | `packages/<package-id>/` |
| 单独分发的扩展/provider | owner 包或仓库 |
| 内部实现辅助 | 最近的持有模块 |

有些工作同时属于两条轴,但可选工作流不会仅仅因为用户可见就需要 capability。只有当 LoopX 调用方需要 provider-neutral 合同、catalog 身份与路由 surface 时才创建 capability。扩展拥有的命令与 packet 合同可以保持为独立扩展 runtime。Finance 价值发现就使用这种独立形态;在真实跨 provider 的 LoopX 合同出现之前,公开市场、文件与新闻收集可以留在这个扩展内。

`value-connectors` 是现有的兼容性 CLI 与协议 surface。不要把它用作新工作的公开 capability 持有者。在退役兼容性 surface 之前,把每个 profile 迁移到现有结果 capability(如 `issue-fix` 或 `content-ops`),或迁移到独立扩展(如 `loopx-finance-value-discovery`)。这让迁移保持行为不变,而不是用一个宽泛桶替换另一个宽泛桶。

编辑前,在活跃 todo 或 plan 中记录一条紧凑理由:

```text
capability_id: <existing-or-new-contract>
provider_id: loopx-core | <extension-id>
origin: builtin | extension
placement: <target-directory-or-package>
reason: <why the nearest existing owner is or is not sufficient>
```

独立扩展使用 `capability_id: none`。不要仅仅因为当前目录没有该特性名称,或因为 manifest 需要生命周期锚点,就创建新 capability 目录。不要仅仅因为涉及外部服务就创建扩展:当内置连接器与核心 release 与生命周期共享时,它仍然可以属于现有 capability。

## Manifest 合同

扩展 manifest 是声明式 TOML。独立扩展只需要可执行的 `[runtime]`。`[[provides]]` 记录向 catalog 添加新的 capability 合同。`[[implements]]` 把 provider runtime 绑定到现有 core 拥有的 capability,而不重复该 capability id。不要仅仅为了让 runtime 可安装就添加任一表。v0 runtime 暴露整数扩展 API 版本 `1`,接受 `>=1,<2` 这样的有界整数约束;不兼容的 manifest 会 fail closed。

```toml
schema_version = "loopx_extension_manifest_v0"
id = "loopx-lark"
version = "1.0.0"
requires_loopx_api = ">=1,<2"
permissions = ["read_status", "read_todos", "external_write"]

[runtime]
protocol = "lark_kanban_provider_v0"
python_module = "loopx.extensions.lark.provider"
doctor_args = ["--doctor"]
required_permissions = ["read_status", "read_todos"]
timeout_seconds = 30

[[provides]]
id = "lark-kanban"
kind = "projection_sink"
title = "Lark Kanban projection"
status = "active"
visibility = "public"
real_world_anchor = "operator-facing Lark Base projection"
user_value = "Project public-safe LoopX status and todo rows into Lark."
entry_command = "loopx lark-kanban sync"
next_real_step = "Validate one explicitly enabled owner-approved sink."
```

随附的 OpenViking pilot 改用 `[[implements]]`:

```toml
[runtime]
protocol = "semantic_preference_provider_v0"
entrypoint = "loopx-openviking-semantic-preference"
doctor_args = ["--doctor"]
required_permissions = ["semantic_preference.read"]

[[implements]]
capability_id = "semantic-preference"
protocol = "semantic_preference_provider_v0"
```

可选的 `packages/loopx-obelisk` 包遵循同一放置规则。它实现现有 `decision-context` capability 的建议 `ContextProvider` 端口;不注册第二个 session 上下文 capability。LoopX Core 把复制的 Codex 深链接解析为规范化的 `host-session:codex:<thread-id>` scope,扩展再把这个 scope 映射到 Obelisk 的公开只读查询 CLI。激活、验证与移除参见
[`decision_context_advisory_provider_v0`](protocols/decision-context-advisory-provider-v0.md)
与包 README。

随附的 periodic-report 归档使用同一所有权方向。它实现一个现有 capability 端口,而不是注册第二个 "OpenViking report" 产品 capability:

```toml
[runtime]
protocol = "periodic_report_sink_v0"
python_module = "loopx.extensions.openviking_periodic_report.provider"
required_permissions = ["openviking_context_write"]

[[implements]]
capability_id = "periodic-report"
protocol = "periodic_report_sink_v0"
```

它的 capability 特定激活包装器额外要求已启用的 `periodic_report_activation_v0`、匹配的未禁用 sink 绑定,以及观测到的 `openviking_context_write` runtime capability。那些项目与 Turn 事实不属于泛型扩展 manifest 或生命周期状态。

### Finance 价值发现示例

`packages/loopx-finance-value-discovery/` 是同仓、独立打包的独立工作流。其 manifest 只注册 `finance_value_discovery_extension_v0` runtime;它不创建 capability catalog 条目,也不创建 `value-connectors` 路由。显式安装且 doctor 探测成功后,通过受管扩展命令调用它:

```bash
loopx extension install \
  --manifest packages/loopx-finance-value-discovery/extension.toml \
  --execute
loopx extension run loopx-finance-value-discovery \
  --input-json packages/loopx-finance-value-discovery/examples/paypal-debeta-discovery.json \
  --execute \
  --format json
```

随附的 PayPal packet 保存一种可复用的去 beta 研究方法,而不是投资结论:从冻结的横截面筛选开始,保留同组对照,把结构性增长与利润池捕获区分开,要求稀释与终态风险证据,然后在最多选择一个后继者之前证伪候选。该 reducer 不执行实时读取,不给出目标价或建议,不能交易,也不能启动持续关注。

为升级兼容,已退役的 `value-connectors` Finance 选择器(包括旧式 `plan --connector-id finance_market_snapshot` 形式)保留为迁移墓碑。它们返回带有序扩展启动前置条件的 `value_connector_extension_migration_v0`;它们不执行 Finance,也不恢复 Finance capability。源码 checkout 可以在注册前安装同仓 provider 包。打包的 LoopX 用户仍然需要单独分发的 provider 制品,因此当该制品不可用时,Agent 必须停止,而不能声称自动安装。

Runtime 必需权限必须是 provider 声明权限的子集。声明任一权限都不授予权限:现有 LoopX Goal 边界、用户 gate 与外部写入授权仍然决定操作是否可以执行。扩展包是可信可执行代码,而不是操作系统沙箱;manifest 记录并约束受管路由,但不能让不受信任的 provider 变安全。

每个可执行 runtime 精确声明一个启动目标。单独安装的可执行文件(如 OpenViking provider)使用 `entrypoint`。随 LoopX Python 包分发的 provider 使用 `python_module`。模块 provider 以 `<current-loopx-python> -m <module>` 运行,其 doctor 证明同时绑定到该解释器与解析后的模块源码。这让干净的源码 checkout 与本地 LoopX release 可以激活随附 provider,而无需单独安装 console script;catalog 发现保持声明式且不导入模块。

## 范围边界

可执行 v0 runtime 刻意不会:

- 重命名或移动现有 capability 实现目录;
- 从 Python 包推断 capability;
- 下载、构建或安装扩展包;
- 启动服务、创建凭据或编辑 provider 配置;
- 在 catalog 发现期间导入扩展入口点;
- 让 manifest 权限绕过 LoopX 控制面权限。

这些边界让激活保持可逆、可审计,同时把包分发与服务设置留给显式的运营者所有工作流。

Provider 迁移遵循同一方向。Core 路由消费紧凑的 provider-neutral 读模型,而 provider 包拥有采集、传输、凭据与外部 effect。例如,配额通过注入的投影器读取 `operator_inbox_urgency_v0`。泛型解析器与读模型合同留在控制面;Lark schema、身份、目标、采集、回复传输与 provider 拥有的配置位于 `loopx/extensions/lark/` 之下。现有的 `loopx lark-inbox` 命令仍然是直接的兼容性 delegate,但它现在要求已安装、已启用、doctor 验证过的 `loopx-lark` 修订,并具有该操作声明的权限。provider 子进程目前只实现 doctor;在传输协议迁移之前,命令执行仍在进程内。以前的 `loopx.capabilities.lark` provider 导入被刻意移除,而不是保留为包装器。Lark Kanban 与 Explore 呈现 sink 位于 `loopx.extensions.lark.presentation`;其兼容性 CLI delegate 要求已安装、已启用、doctor 验证过的修订声明 `lark.projection_sink.use`。不需要额外的面向 Agent 的 CLI 参数。
