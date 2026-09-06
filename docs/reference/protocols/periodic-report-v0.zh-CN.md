# Provider-neutral 周期报告 v0
> [English](periodic-report-v0.md)

## 产品激活

活动项目会话中的显式请求，如「生成本周项目报告」，是一次 provider 无关的本地生成的充分权限。LoopX 解析内置 `weekly-progress` profile（别名 `weekly` 与 `weekly-report`），其规范化 `periodic_report_profile_v0` 设置 `enabled: true`、绑定 `project_progress_v0`、Markdown 与 HTML，且既不声明调度也不声明 sink。该 profile 可以无副作用检查：

```bash
loopx periodic-report inspect-profile --preset weekly --format json
```

这不持久化项目激活、不创建 scheduler、不授予外部写入。当前会话拥有请求的日历窗口。选择内置 preset 时，激活包包含一个 `interaction_contract`，使这些会话生成默认值显式；通用 heartbeat prompt 不需要报告特定展开。

项目自有 `periodic_report_profile_v0` 是自定义或无人值守运维的高级选择契约。启用的自定义 profile 声明：

- provider-neutral 触发策略与可选 host 自有 RRULE/时区；
- 一个或多个领域源适配器绑定；
- 一个或多个渲染器绑定；
- 零个或多个必需、可选或禁用的 extension sink 绑定。

只有在报告必须按 RRULE 无人值守运行时才使用 host Automation。Automation 调度与项目 profile 必须一致；普通会话内生成不需要 Automation。外部投递仍需要显式 sink 绑定及其独立运行时权限/回读检查。

`periodic_report_activation_v0` 是无效果检查回执。它记录是否允许生成、规范化 profile 摘要与 portable/enhanced/durable extension 模式。它不执行源读取、调度变更、provider 查找、渲染、归档写入或消息投递。

### 受众策略与公告计划

自定义 profile 可以包含 `periodic_report_audience_policy_v0`。策略包含符号接收者、合格可见性集（默认为 primary）且无 provider 身份。每个接收者必须拥有一个或多个规范化领域 token，或声明一个或多个 `periodic_report_audience_routing_rule_v0` 对象。规则可以选择 `source_ids`、`section_ids`、`content_kinds`、`tags_any` 或 `domains_any`；该规则声明的每个选择器都必须匹配一个规范化项。项可以在既有 tags 与 content kind 之外携带 `domains`。

`periodic_report_announcement_plan_v0` 是精确规范化文档与受众策略之上的确定性、provider-neutral 投影。它记录所选符号接收者 id、匹配项引用、类型化匹配原因与策略/文档摘要。需要 owner 域交集或显式路由规则匹配。除非策略显式使该可见性合格，支持项被忽略。无关接收者被省略，标题或摘要文本从不推断相关性。

Lark 投递适配器一起接受文档与策略。预览返回计划而无身份解析或外部效果。Execute 请求注入的 Lark 身份适配器只渲染所选符号 id，前置那些 `<at>` 元素，然后使用既有发送与精确回读契约。无身份渲染器的所选接收者、不匹配的工件/文档摘要、或报告内容、标题与页脚中编写的提及标记，都在发送前失效关闭。这把相关性保留在核心契约中，把 provider 身份放在 extension 侧。

交付的执行路径是 `loopx periodic-report deliver-goal-channel`。其投递意图必须恰好包含两个有序 HTTPS 公告：托管报告条目，然后是 Lark 文档条目。它们作为两条独立幂等消息发送，每条都必须通过精确回读。每次写入前，provider 从冻结生成时间扫描完整 Goal Channel 历史，并复用精确的卡片、聊天与 Bot 发送者匹配。不完整的历史读取失败关闭；provider 的稳定一小时内幂等键覆盖剩余并发发送竞态。该命令不接受聊天、profile、App 身份或发送者覆盖。相反，Lark extension 解析当前 Goal 的 local-private Goal Channel 绑定，并要求 `mode=project_bot`、Bot 发送者身份、非默认 profile、精确 Bot App id 与显示名、以及启用的 Lark channel。发送前，它实时验证绑定 profile 认证为同一 Bot App 且可到达同一聊天。发送后，它从该聊天回读精确交互卡片，并要求 provider 原生消息发送者是 id 等于绑定的 Bot App id 的 `app`。仅重新验证 profile 不是发送者证明。缺失绑定、本地用户模式、身份漂移或不完整回读失效关闭；不存在环境默认或用户身份回退。

受治理的待处理意图消费者持久化规范化生成包，并写入一个可运行的 agent 自有投递 successor。消费前重新读取当前生效 `periodic_report` 订阅；带显式 `route_ref` 的 `enabled: true` 是该自动阶段边界投递的常驻权限。其 Goal、来源、有效修订与路由冻结进 `periodic_report_delivery_authority_v0`，并须在每次外部消息写入前仍匹配。禁用订阅或更改其有效修订/路由抑制排队动作，即使存在独立显式 Goal Channel 绑定。Successor 保持绑定到冻结生成摘要、当前 Goal、所需 provider 能力、配置的 Goal Channel、项目 Bot 身份与精确回读。这使外部动作在不做第二次每报告批准的情况下对 quota 可见，同时仍对路由或身份漂移失效关闭。

`periodic_report_project_progress_projection_v0` 是内置、领域无关的源输入。它把类型化项目事实分组为进展、能力演进、风险、下一动作与支持证据，至多八个主受众项。Issue Fix 在两个 schema 中都没有特殊地位。它可以与 release、research、operations 或另一领域在同一契约下注册对等源适配器。OpenViking 同样是在 sink extension 之后的可选归档/查询 provider；它不拥有触发、选择、渲染或投递。

`periodic_report_v0` 是一次有界报告运行的 LoopX 控制契约。它把周期窗口与 profile 绑定到类型化源快照、一个渲染工件回执、归档与投递回执、确定性幂等、显式 partial/unknown 状态与有界重试投影。

该 capability 还定义 `periodic_report_trigger_decision_v0`。调用方在收集或投递报告前评估紧凑 LoopX 或 provider 事实：

```bash
loopx periodic-report evaluate-trigger \
  --request-json periodic-report-trigger-request.json \
  --format json
```

```bash
loopx periodic-report compose-run \
  --request-json periodic-report-request.json \
  --format json
```

命令本地且无效果。源收集、渲染、归档写入、消息投递与回执回读都在本核心之外的适配器或 connector 中执行。

## 拆分相位契约

`periodic_report_v0` 还暴露一个拆分契约，用于必须把本地报告生成与 provider 可用性分开的 profile：

- `periodic_report_generation_bundle_v0` 包含规范化文档、一到八个工件与确定性 `periodic_report_generation_receipt_v0`。回执声明不需要 provider 或外部写入。
- `periodic_report_sink_binding_v0` 钉住 sink id、角色、依赖策略、capability id/版本、extension id/版本与 provider-neutral `periodic_report_sink_v0` 协议。
- `periodic_report_extension_readiness_v0` 对照观察到的 provider 回执验证那些绑定。它报告 `portable`、`enhanced` 或 `durable` 投递模式，绝不执行 provider 调用。
- `periodic_report_delivery_receipt_v0` 把 provider sink 结果绑定回生成与就绪回执。已发送 sink 只有在有幂等键、紧凑回执引用与验证精确回读时才被接受。

## Personal Workspace 发布投影

`periodic_report_workspace_projection_v0` 是 Personal Workspace 的内置只读 `milestone_report` 视图模型。它从与生成报告相同的类型化文档与进展事实冻结；浏览器不解析渲染的 Markdown，也不从指纹推断标题。其交互语义为 `attention_kind=progress`、`interaction=inform`、`delivery=surface` 与 `writable=false`。紧凑计数区分自上次已验证发布以来新增的事实与语义指纹改变的事实。

仅生成不暴露该投影。发布候选绑定其精确 SHA-256，Goal Channel sink 只在投递回读成功后把该绑定推进到发布 cursor。紧凑 `periodic_report_workspace_index_v0` 热路径包含身份、投递时间、前任血统与精确内容寻址详情引用，但不含报告散文。完整投影是仅回环冷读取，必须匹配当前发布 cursor。因此批准待定、仅生成、过期或摘要不匹配的投影失效关闭，而不是显示为已发布。

Personal Workspace 投影不生成、不批准、不发布、不确认或不编辑报告。周期报告 capability 仍是报告触发、文档、投递与发布 cursor 状态的唯一 owner。这是里程碑报告智能呈现 RFC 的有界实现，而非该 RFC 描述的通用跨 capability 编译器。

依赖策略是 `required`、`optional` 或 `disabled`。必需 sink 不可用时阻塞正式投递。可选 sink 降级而不使生成回执无效。禁用 sink 被跳过。与 profile 绑定不匹配的 provider 版本、协议或能力是 `incompatible`；无已验证就绪性的 provider 是 `unverified`。

捆绑的 `openviking-periodic-report` LoopX extension 是该端口的一个具体实现。其运行时协议是 `periodic_report_sink_v0`，manifest 权限与观察到的运行时能力都是 `openviking_context_write`，其 sink 能力是 `report.archive.write/v0`。运行时激活重算规范化 `periodic_report_activation_v0`；禁用或改动的回执、缺失或禁用的 sink 绑定、过期的 extension doctor 证明或缺失的观察运行时能力，都在任何 provider 写入前拒绝该调用。

`openviking_periodic_report_archive_request_v0` 携带激活回执、规范化文档、Markdown 工件、归档上下文与一个执行位。Provider 按提交顺序写入两个 OpenViking Resources：`report.md`，然后 `manifest.json`。后者记录 `openviking_periodic_report_archive_commit_v0`、包摘要、稳定结果 id 与 `manifest_written_last=true`。`sent` sink 结果要求两个 URI 的精确内容摘要回读。HTML 托管、历史查询与记忆蒸馏是已提交 Resource 的独立消费者，不属于该 provider 协议。

下面的旧 run 请求仍是兼容的完整投递信封。它仍要求归档与投递回执，而拆分契约使 provider 无关的生成真相在这些回执存在之前可用。

## 触发决策

`periodic_report_trigger_request_v0` 把 profile 与触发策略绑定到评估时间戳、可选上次报告回执与至多 64 个紧凑候选事实。内置种类：

- `cadence_due`：profile 自有调度说明报告窗口已到期；
- `vision_closed`：vision 转换已关闭、验收已验证，且 successor 已确立或 goal 终态；
- `primary_goal_outcome`：主投递结局已验证且有持久化 writeback；
- `bounded_segment_milestone`：证据链接的物化检查点关闭了当前 vision，且所得 successor 前沿或终态 Goal 已持久化结算，即使无关 Todos 仍开放；
- `material_decision`：批准的、拒绝的或取消的决策改变了执行路由且被持久化记录；
- `material_blocker`：新增或升级的 P0 blocker 停止主路径；
- `material_recovery`：已验证解决重新打开主路径；
- `manual`：显式授权的运行。

`surface_only`、`state_refreshed`、`todo_completed`、`monitor_unchanged` 与 `vision_checkpoint` 只被接受，以使决策回执能解释它们为何被抑制。它们自身从不触发报告。

决策按紧迫性对物化候选排序、合并并发事实，并派生稳定 `report_key`。触发身份从种类、来源引用与证据摘要派生；上次报告回执抑制它已覆盖的 id。Profile 自有最小间隔抑制非紧急更新，而授权的 manual 运行、验证的主结局、验证的 vision 关闭与主路径 blockers 可以绕过它。输出记录所选与合并 id、每个抑制原因、冷却状态与报告种类（`cadence_digest`、`milestone_update`、`exception_update` 或 `manual_update`）。

`bounded_segment_milestone` 从驱动自主 replan 的同一 goal-vision 与前沿事实派生，但它是更严格的成功路径结果。它要求满足的证据链接物化结局检查点、关闭的当前 vision、持久化 writeback 与以下继续结算之一：

- Goal 终态；或
- 活动 Goal 发出既有 `vision_successor_required` 转换，匹配的 replan 语义增量被接受，且 successor vision 加其自有前沿被持久化确立。

生产者按关闭的 vision 修订与前沿身份去重。普通 Todo 完成、Todo 计数阈值、流逝时间、设置工作与 blockers、继任缺口、长 Todo 链或 monitor 耗尽等通用 replan 原因只是证据或控制面上下文；它们从不证明阶段完成。不引入 Todo 声明或第二个 Stage 生命周期。剩余无关 Todos 不抑制另有有效的关闭 vision 里程碑。触发优先级为 40，映射为 `milestone_update`，并遵守普通 profile 冷却。

合格决策可以作为 `trigger_receipt` 嵌入 `periodic_report_run_request_v0`。其 `report_key` 与 `report_kind` 随后参与 run 身份，因此同一证据窗口上的里程碑更新与计划摘要不会冲突。

### 后写 hook 边界

可选的自动路径使用 provider-neutral TypeScript `post_writeback` capability-hook 契约。只有 Goal 的本地控制面配置显式启用周期报告 profile 时，CLI 组合根才注册 `periodic_report.runtime_trigger`。Core 只在主 `refresh-state` 持久化 writeback 与精确结算回读以完整 Goal、Agent、Todo、Turn 与 effect 身份成功后分发。尽力 rollout 事件日志不是分发权限。

Hook 输入只包含已提交回执身份、稳定状态修订与派生的 `periodic_report_stage_completion_receipt_v0`。其结果是带空写 scope 的幂等 `periodic_report.trigger_evaluation` 意图。Core 在 TypeScript 中验证注册、输入、结果与 sidecar 回执，然后把有界回执单独存储在主事务之外。终态重放跳过 provider 调用。瞬态 provider 或结果契约失败持久化带稳定分发引用与单调尝试计数的 `retryable_failure` 回执；精确重放可以把该回执原子推进为 `intent_recorded` 或 `not_applicable`。冲突与可选 hook 失败保持隔离，不能回滚主 writeback 或改变配额花费资格。

记录触发意图既不是报告生成也不是发布。后续受治理执行器必须评估该意图。组合、渲染与内容检查保持独立于外部投递；启用生效订阅提供常驻投递权限，而 extension 与精确 sink 回读保留效果权限。

## 请求与身份

`periodic_report_run_request_v0` 包含：

- `generated_at` 与带偏移的 `period_window.start_at` / `end_at`；
- 稳定 `profile_id`、`profile_version` 与可选不透明 `profile_ref`；
- 一个或多个 `source_snapshots[]`，含来源身份、类型化状态、紧凑摘要/引用/计数证据与可重试性；
- 一个指名渲染器与工件状态的 `artifact_receipt`；
- 至少一个 `archive` 与一个 `delivery` 回执；
- `retry_policy.attempt` 与 `max_attempts`。

它还可以包含合格 `periodic_report_trigger_decision_v0` 回执。

LoopX 从规范化窗口、profile、来源身份、渲染器身份与 sink 身份派生 `run_id` 与 run 级 `idempotency_key`。快照内容与尝试编号不改变该身份，因此重试不能创建第二个逻辑报告。调用方可以重复派生值；过期或不匹配值失效关闭。

每个 sink 收到从 run、sink 角色与 sink id 派生的确定性 sink 特定幂等键。`sent` 回执只有在有精确键、紧凑回执引用与验证回读时有效。

## 状态与重试语义

源状态是 `complete`、`partial`、`failed` 或 `unknown`。工件状态是 `pending`、`rendered`、`failed` 或 `unknown`。Sink 状态是 `pending`、`sent`、`failed`、`skipped` 或 `unknown`。

派生的 run 状态是以下之一：

- `pending`：渲染或某个 sink 未结算；
- `succeeded`：所有源 complete、工件已渲染、每个归档/投递 sink 已发送且有验证回读；
- `partial`：存在可用输出但某源 partial、某 sink 被跳过、或至少一个 sink 成功而另一个失败；
- `failed`：收集/渲染失败，或每个必需 sink 失败；
- `unknown`：源、工件或 sink 后置条件无法确定。

重试只允许终态非成功状态、在 `max_attempts` 之前、且至少一个未结算组件显式声明自己可重试。输出指名这些组件与精确下次尝试。

## 所有权边界

核心刻意不含项目、pull request、issue、工作日、时区、聊天、文档或 provider 策略。那些属于可复用适配器与项目 profile：

- 项目 profile 拥有节奏、时区、报告小节、受众与选择策略；
- 源适配器收集并规范化领域证据；
- 渲染器把规范化证据变成工件；
- 归档与投递 sink 执行受限写入并验证回读；
- 项目产品可以索引历史工件，而不改变 run 身份或投递真相。

内置呈现适配器包括线性 Markdown 与自包含 `html_artifact_v0` 渲染器。HTML 渲染器是零构建、单文件投影，带可选本地交互。其默认 `editorial_dense_v2` 呈现保持规范化主项事实可见、接受 profile 自有语言与至多四个首屏亮点、从类型化主项编译受众摘要，并把支持项、profile 身份、源健康、生成元数据与摘要移入折叠附录。项可以声明 `visibility=primary|supporting`；`runtime` 与 `delivery_receipt` content kind 必须是 supporting。线性 Markdown 工件把那些项保留在带标签附录中，使复制/导出保持完整而不打断主叙述。HTML 内嵌该 Markdown 渲染并记录其伴随工件摘要。受众项还可以携带至多四个有序 `details` 行用于可读事实分组，以及可选 `tag_labels` 用于本地化显示；规范 token 标签保持不变。托管或生成可共享 URL 仍是带自身幂等与回读回执的独立 sink 动作；它不是渲染器权限。捆绑 Lark extension 包含 `html_artifact_v0` 的可选 `miaoda_html` 投递 sink。它在任何外部效果前验证单个 HTML、压缩归档与未压缩载荷限制。成功回执要求请求所选 app id 与发布 URL 的精确回读，以及 `finished` 状态的精确发布 release。回执分离 `release_readback`、`access_scope_readback` 与 `content_readback`：访问 scope 对创意 HTML apps 可以是类型化 `unsupported_by_app_type` 结果，而其他查询失败保持可重试 `unavailable` 证据；捆绑 provider 把远程内容摘要验证标记为 `unavailable`，因为 provider API 不暴露已发布字节或摘要。App 存在、URL 相等与 release 完成必须不被提升为逐字节内容证明。回执规范化从请求的 release id 与 provider 状态重算精确 release 验证，而非信任 provider 布尔值。项目或 host 仍拥有 app 选择、认证、受众策略与 execute 决策。

`loopx periodic-report publish-miaoda` 是该 sink 的具体 CLI。其 `periodic_report_miaoda_delivery_request_v0` 必须携带完整规范化 profile、精确 `periodic_report_generation_bundle_v0` 与 `periodic_report_delivery_intent_v0`，后者 `kind=hosted`、`sink_kind=miaoda_html`、profile 绑定 sink id、操作员选择的既有 app id 与稳定幂等键。所选 profile 绑定必须使用 `report.miaoda_html.publish@v0`、`loopx-lark` 与 `periodic_report_sink_v0`；省略、禁用或类型不同的 sink 在 provider 执行前被拒绝。

无 `--execute` 时，命令不执行 provider 调用，返回带 `status=pending_execution`、`intent_satisfied=false` 与待处理投递回执的 `periodic_report_miaoda_delivery_result_v0`。带 `--execute` 时，它使用已认证 `lark-cli` 发布，并要求相同 app id、在线 URL 与 `finished` 状态发布 release 的精确回读。只有该验证生命周期结果把 `intent_satisfied=true`；访问 scope 与内容证明限制仍作为 sink 结果与规范化投递回执中的显式证据。生成包在任一情形下都可用，但本地 HTML 永不满足托管投递意图。命令不接受凭据、不创建 apps、不选择受众、不修改访问 scope、不发送聊天通知、不应用调度策略。

规范化文档的可选 `editorial` 输入按所有权拆分。项目 profile 拥有有界 `kicker`、`period_label`、`language` 与零到四个有序公开安全亮点。文档构建器拥有 `summary` 与其 `periodic_report_editorial_orchestration_v0` 回执。它确定性选择类型化主 `outcome`/`decision`、`risk` 与 `next_action` 标题，需要时回退到项的类型化 `next_action` 字段，记录精确项血统，并拒绝作者编写的摘要。两个内置渲染器在渲染前重算该值，因此不改变源事实而改摘要会失效关闭。主摘要限 360 字符，主 `capability_change` 项要求至少两个命名 details。

该编排是结构性的，不是语义猜测。源适配器拥有 `content_kind`；编译器绝不提升 `runtime` 或 `delivery_receipt` 项，未类型化/进展/capability-change 事实保留在正文中而不被拉入 hero。该对象用于受众结论，而非工件构建或 sink 状态。投递一致性、归档 provider 验证、摘要、canary、渲染器血统与精确回读保持为支持项或 sink 回执。

核心拒绝原始内容、消息、日志、transcript、凭据、secret 字段与私有路径。公开包只保留紧凑引用与摘要。
