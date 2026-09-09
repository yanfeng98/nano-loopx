# Periodic report


`periodic-report` 是 LoopX 可复用的报告 capability。它给任何项目一个稳定的
report-run envelope,而把源语义、cadence、展示与目的地交给 profiles 与
adapters。

| Surface | 价值 |
| --- | --- |
| CLI | `loopx periodic-report inspect-profile --preset weekly`,自定义 `--profile-json <path>`、`evaluate-trigger`、`evaluate-runtime-trigger`、`compose-run`,以及可选 `archive-openviking` |
| 协议 | [`periodic_report_v0`](../../../docs/reference/protocols/periodic-report-v0.md) |
| Smokes | `python3 examples/periodic-report-smoke.py`、`periodic-report-profile-smoke.py`、`periodic-report-html-smoke.py`、`periodic-report-bindings-smoke.py` 与 `openviking-periodic-report-extension-smoke.py` |

## 生成本周报告

在活跃 LoopX 或 Codex 项目会话中,让 agent **生成这周的 project report**。
该显式请求让当前会话选择一次 provider-free 生成。Agent 解析内置
`weekly-progress` profile(短别名:`weekly` 与 `weekly-report`),收集当前项目的
public-safe LoopX 进度,并渲染匹配的 Markdown 与自包含 HTML artifacts。不需要项目
profile 文件、Automation、provider 或外部 sink。

Agent 可以用无副作用命令检查确切的内置 profile:

```bash
loopx periodic-report inspect-profile --preset weekly --format json
```

Receipt 必须同时报告 `active: true` 与 `generation_allowed: true`。其
`interaction_contract` 还说:显式用户请求即足够,不需要项目 profile 文件或
Automation,并且该模式不允许外部写。Agents 应遵循该 packet,而不是展开通用
heartbeat prompt。
Preset 绑定内置 `project_progress_v0` source 加 `markdown_v0` 与
`html_artifact_v0`,不声明 schedule,也不含 sink bindings。显式请求使用活跃会话的
本地日历上下文拥有报告窗口;它不创建周期性任务。

`project_progress_v0` 把 typed 事实组织成可复用层级:进度与 outcomes、能力演进、
风险与 blockers、下一步动作,以及折叠的支撑证据。它最多允许八个主条目,因此
交付 receipts 与运行时校验收缩为支撑,而不是挤占受众叙事。该层级受已验证的项目
weekly-report 展示启发,但没有任何 issue、pull-request 或 Issue Fix policy。

源请求可以携带 profile 自有的 `language`,作为类 BCP-47 标签。内置层级当前提供
英文与中文分段词汇(其他语言回退到英文),而项事实仍由调用方拥有。Orchestrator
必须把同一语言传入文档编辑输入;renderers 不推断也不重写业务分段语义。省略该
字段保留英文默认。

没有 issue-fix 特定的报告 capability。Issue Fix、release notes、research、
operations 与其他领域可以在其更丰富语义有用时提供 peer source adapters;内置
weekly profile 不要求任何之一。

## 自定义或调度

Capability 默认保持**不活跃于后台工作与外部写**。只有当项目需要自定义 sources、
renderers、受众 policy、时区/RRULE 或显式 sink bindings 时,才创建项目自有的
`periodic_report_profile_v0`。无人值守周期报告只使用宿主 Automation:
host 调度应匹配该自定义 profile 的 RRULE。暂停 Automation 或把 profile 设为
`enabled: false` 会停止该调度路径。

外部投递与归档是独立 opt-ins。普通会话内 weekly report 无 sink,不执行外部写。
但对于 machine/Goal `periodic_report` 订阅,`enabled: true` 加显式 `route_ref`
是在验证过的阶段边界投递报告的持久 authority。选中的 extension、运行时
capability、配置的 route、sender 身份与精确 readback 仍必须各自通过 fail-closed
gates。

Capability 有意为无副作用。它首先把调度或 material 进度事实求值成确定性 trigger
receipt,然后用稳定 run 与 sink 幂等性、typed 源快照、artifact 与 sink receipts、
显式 partial/unknown 结果与有界重试指引组成一个 run。它不执行 provider 读或写。

可报告转换包括:到期的 cadence、已验证的 primary outcome、带 successor 或
terminal goal 的已验证 vision closure、material route 决策、primary-path blockers
与恢复,以及授权的手工运行。普通 todo 完成、unchanged monitors、状态刷新、
surface-only 事件与中间 vision checkpoints 被抑制。Profiles 可以启用 trigger
种类并设置最小间隔;紧急 outcome、closure、blocker 与 manual triggers 可以绕过
该间隔。并发的 material 事实被合并进一个报告,先前已覆盖的 trigger ids 被去重。

增量报告从精确的、readback 验证的发布游标推进,而不是从生成散文推进。游标保存
按每个事实稳定 `source_ref` 键控的累积 trigger ids 与语义 fingerprints。之后的
stage 只包含新事实与 fingerprint 变化的事实;变化的事实携带先前的状态与种类,
使编辑步骤可以渲染转换而不是重复旧条目。如果没有任何提供的事实是新的或变化的,
post-writeback producer 不发报告意图。本地生成与失败或部分投递从不推进该游标。
成功的 Goal Channel 投递记录前驱发布身份,供下一个报告使用。

启用的自定义 profile 还可以声明带 `window_seconds` 上界与
`stage_completion_required=true` 的 `trigger_policy.aggregation`。阶段完成
(Stage completion)复用现有 goal-vision、outcome-checkpoint 与 frontier-replan
事实:当前 vision
必须通过 evidence-linked material checkpoint 关闭,且 Goal 必须变为 terminal,或把
现有 `vision_successor_required` 转换持久地归入 successor vision 与其所拥有的
frontier。`evaluate-runtime-trigger` 只把该派生的成功路径 receipt 提升为
`bounded_segment_milestone`。

不需要 Todo 预声明或单独 Stage 生命周期。Todo 计数、流逝时间、普通完成与
blocker/stall/long-chain/monitor replans 保持上下文,从不单独产生报告。Producer
不执行 provider 调用或外部写;有资格的 receipt 继续走现有 `compose-run`、
renderer、持久订阅 authority 与 sink readback 边界。
CLI 在 goal、segment-window 与相关种类过滤之后,才流式输出 append-only 日志并
应用 4,096 行容量限制。格式错误的持久行与过大的相关窗口会 fail closed。

### 自动 post-writeback 意图

自动里程碑求值默认关闭。项目可以在其本地 registry 组合边界,把内置 weekly
profile 选入通用 post-writeback hook:

```json
{
  "control_plane": {
    "periodic_report": {
      "enabled": true,
      "profile_preset": "weekly"
    }
  }
}
```

在带完整 Goal/Agent/Todo/Turn/effect 身份提交的 `refresh-state` writeback 之后,
core 在主事务之外分发 TypeScript 验证过的 `post_writeback` hook。Capability 只
接收有界 stage-completion 投影与其 public-safe 进度快照,两者都在 writeback
边界捕获。它可以提议一个幂等 `periodic_report.trigger_evaluation` 意图。Core
在可重放 sidecar 中检查点该提议。瞬态失败被持久记录为 `retryable_failure`;
下一次精确重放推进其 attempt,并可以把它替换为 `intent_recorded` 或
`not_applicable`,而 terminal 重放返回原始 receipt,不再次调用 provider。禁用的
profiles、不完整的归集身份、普通 Todo 完成与通用 replan 不产生 provider 调用或
意图。

意图不是报告,也不授予生成、发布、connector、网络、凭据或 sink authority。
单独的受治理 executor 可以把它求值为正常 trigger 决策。消费时 LoopX 再次读取
当前有效订阅:禁用的订阅压制动作,而带显式 route 的启用订阅提供持久投递
authority。报告组成、Miaoda HTML、内容检查、provider 就绪度与群消息 readback
仍是之后独立的 gates。

`quota should-run` 读取该确切 Goal 与 Agent 合格的 `intent_recorded` sidecars。
待决意图优先于 monitor-quiet 与 terminal no-follow-up 投影,返回一个 TypeScript
验证过的受治理命令。该命令可以渲染 provider-free 本地 HTML 与 Markdown、运行内容
检查、持久化归一化生成 bundle,并创建一个绑定冻结 generation digest 与当前有效
订阅的可运行投递 successor。精确重放不重新渲染或复制 Todo。投递请求携带该订阅的
Goal、source、有效 revision 与 route;Lark provider 在每次消息写入前立即重新
验证它。因此,普通 Todo/quota 选择可以继续进入 Miaoda 发布、Lark 文档创建与
Goal Channel 投递,而无需另一个按报告 owner gate。禁用订阅撤回转占的自动投递;
route、provider、sender-identity 或 readback 漂移仍然 fail closed。

项目特定的调度报告应分层为 profiles 与 adapters。例如,维护 profile 可以选择
本地时区与每周 cadence、收集仓库与讨论信号、渲染团队卡、归档 artifact,并投递给
配置的 channel。这些选择没有一个成为共享 core 或会话内 preset 的不变量。

## 受众相关性与 Lark 公告

自定义 profile 可以声明 `periodic_report_audience_policy_v0`。收件人使用稳定
符号 id,并必须声明至少一个自有领域或 typed 路由规则。报告条目可以携带归一化
`domains`;路由规则还可以选择显式 source ids、section ids、内容种类、tags 或
domains。一个规则中的每个声明选择器必须匹配同一个归一化条目。

`build_periodic_report_announcement_plan` 把这些事实编译成 provider-neutral
`periodic_report_announcement_plan_v0`。只有至少一个合格报告条目与自有领域相交
或匹配显式规则时,收件人才被提名。主条目默认合格;支撑证据被排除,除非 profile
选择纳入。无关收件人的默认是省略。Titles、summaries、署名提名文本、provider
身份与外部查找从不参与选择。

Lark 投递适配器可以在渲染 artifact 之外消费确切的归一化文档与 policy。Preview
不解析身份也不发送消息,返回公告计划。执行时,extension 只通过注入的 provider
适配器解析选中的符号 ids,并在报告前放置那些已验证 `<at>` 元素。无 renderer 的
匹配、文档/artifact digest 不匹配,或 artifact、title、footer 中嵌入 provider
mention 标记,会在发送前失败。因此 core 拥有相关性,而 Lark extension 拥有
provider 身份与线缆渲染。

捆绑的执行命令是 `periodic-report deliver-goal-channel`。它只从当前 Goal 的已启用
Goal Channel binding 派生目的地与 sender。只有已验证的 `project_bot` profile
有效;请求不能提供 chat id、profile、Bot App id、显示名或 sender 身份。意图相反
只提供恰好两个有序 HTTPS 条目——托管的报告与 Lark 文档。执行发送两条独立消息,
发送前验证绑定的 Bot 与 chat,然后要求两者的精确 interactive-card、chat 与
Bot-identity readback。缺失或漂移的身份或订阅 authority、任一消息缺失,或部分
readback 都在无用户/默认-Bot fallback 的情况下 fail closed。重试先从冻结生成时间
扫描完整 Goal Channel 历史,只复用精确 card、chat 与 Bot-sender 匹配。不完整历史
fail closed,而不是冒重复风险;稳定 provider 幂等 key 关闭并发发送竞态。

这是内置 capability,不是 extension:即使未安装 provider,调用方也需要 trigger、
幂等性、重试与 receipt 契约。可选或独立版本化的 collectors、renderers、archive
stores 与消息传输仍是实现 capability ports 的 extension providers(或内置
adapters),不拥有其生命周期。

`inspect-profile` 返回确定性 `periodic_report_activation_v0` receipt,从不启动
scheduler 或调用 provider。`--preset weekly` 解析内置会话 profile;
`--profile-json` 验证自定义项目 profile。自定义 profile 中省略 `enabled` 字段
视为 `false`,启用的 profiles 要求至少一个 source 与一个 renderer。可选 archive
extension 因此可以添加持久历史,而不让本地报告生成或另一个配置的投递 sink 依赖它。

公开 profiles fixture 覆盖内置可移植 weekly profile、默认禁用的项目、带可选
archive extension 的 cadence-based release 报告,以及带 extension 提供 source 的
milestone-only research 报告。这些是 peer 产品用途;没有一个改变 capability 身份
或 core schema。

## 生成与正式投递

可复用生命周期有两个独立真实的两阶段:

1. `build_periodic_report_generation_bundle` 冻结一个归一化文档、一个或多个渲染
   artifact,以及一个 provider-free 生成 receipt。缺失的 chat 或 archive provider
   不能使这些本地 artifact 失效。
2. 项目 profile 声明 sink bindings。LoopX 在调用方尝试正式投递前检查 pinned
   extension 版本、协议、capability 版本与 provider readback。Provider 结果随后
   归一化为带可重试 sink ids 与精确读取证据的单一投递 receipt。

每个 sink 依赖都是 profile 自有的、显式的:

- `required` 在其 provider 缺失、不兼容或未验证时 fail closed;
- `optional` 保留生成的报告,并记录降级或部分正式投递结果;
- `disabled` 不执行 provider 查找或写入。

这产生三种可移植运行模式。`portable` 无 providers 生成 artifacts,`enhanced`
添加可选 sinks,`durable` 要求一个或多个正式投递或归档 sinks。公开 fixture
`examples/fixtures/periodic-report-extension-modes.public.json` 演练全部三种,
而不点名项目或依赖 live provider。

`compose-run` 对已经同时拥有归档与投递 receipts 的调用方保持兼容 envelope。
新 profile 集成可以使用拆分的生成/就绪/投递 receipts,使 provider 特定 policy
不泄漏进 capability core。

## 可选 OpenViking 归档 extension

`openviking-periodic-report` 是实现 capability `periodic_report_sink_v0` 归档
port 的捆绑 **LoopX extension**。它不是 OpenViking extension,也不添加
OpenViking 运行时 ABI。依赖方向是:

```text
periodic-report capability
  -> openviking-periodic-report LoopX extension
     -> OpenViking public SDK read/write
```

通过正常 LoopX 生命周期安装:

```bash
loopx extension install --bundled openviking-periodic-report --execute --format json
```

除非以下三件事全部成立,否则激活 fail closed:

1. 归一化 `periodic_report_activation_v0` 说项目 profile 已启用;
2. 该 profile 把 `report.archive.write/v0` 绑定到
   `openviking-periodic-report@1.0.0`,带 `periodic_report_sink_v0` 与非禁用
   dependency policy;
3. 当前 run 已观测并声明 `--available-capability openviking_context_write`。

Extension manifest 权限不授予写 authority。它只让运行时证明:选中的、已启用、
doctor 验证的 revision,与调用方已经观测的 authority 兼容。Profile 可以把 sink
保持 `optional` 以获得增强体验,或标为 `required` 获得持久报告契约。

V0 provider 只接受 Markdown artifact。它先写 `report.md`,最后写 `manifest.json`;
精确回读的 manifest 是提交标记,包含稳定 bundle digest 与 result id。字节相同的
重试不执行写。不同字节的稳定 URI 会 fail closed。它不归档 HTML,不把完整报告
复制进 Agent Memory,不扫描报告历史,也不实现 `/reports`。

```bash
loopx periodic-report archive-openviking \
  --request-json periodic-report-openviking-request.json \
  --available-capability openviking_context_write \
  --openviking-url http://localhost:1933 \
  --execute \
  --format json
```

用 `--openviking-api-key-env` 命名环境变量;绝不把凭据放进报告 profile 或请求。
没有 `--openviking-url` 时,provider 使用公开内嵌 `OpenViking` client 与可选
`--openviking-path`;`--openviking-config` 显式选择其 `ov.conf`,使隔离 run
不必继承用户默认配置。OpenViking SDK 是可选环境依赖,extension doctor 在能导入
该公开 client surface 之前保持不可用。项目 profiles 拥有 archive 是否启用,以及
请求上下文提供的 Resource 根与 tags。通用 capability 继续拥有 trigger、生成、
投递事实与重试语义。

## 内置 Renderers

- `markdown_v0` 为文档与消息适配器产生紧凑线性 artifact。
- `html_artifact_v0` 产生自包含、零构建的编辑报告,带密集 outcome 行、响应式
  深链接分段导航、文本搜索、Markdown 复制与打印/PDF 控件。其默认
  `editorial_dense_v2` profile 接受 profile 自有的语言、期间标签与至多四个
  first-screen highlights。文档 builder 从 typed primary outcomes、risks 与 next
  actions 编译 hero 摘要;author 撰写的摘要被拒绝,因此过程叙述不能绕过内容
  层级。归一化条目可以声明 `visibility=primary|supporting` 与 `content_kind`;
  `runtime` 与 `delivery_receipt` 条目除非是支撑上下文否则被拒绝。生成元数据、
  源状态、digests 与支撑条目放在折叠附录中,而不是打断报告。Markdown renderer
  在标注附录中保留支撑条目,使复制与投递的文本保持完整。
  Renderer 无外部运行时依赖,并在渲染前转义所有源内容。

两个内置 renderers 消费完全相同的归一化文档。HTML artifact 记录配套 Markdown
digest,因此调用方可以证明可共享页面与线性消息/文档版本携带相同主内容。公开
fixture `examples/fixtures/periodic-report-editorial-dense.public.json` 演示可复用、
项目中性的报告。

## 捆绑 Miaoda HTML 投递

捆绑的 `loopx-lark` extension 为自包含 `html_artifact_v0` 输出提供 opt-in
`miaoda_html` 投递 sink。Sink 把已渲染 artifact 发布到投递请求选定的项目自有
现有 Miaoda HTML app;它不重建文档,也不选择受众。任何外部效应前,它检查单个
HTML、压缩归档与非压缩 payload 限制。发布后它保留 provider 的确切 release id,
并要求该 release 以 `finished` 状态回读,同时要求相同的 app id、发布的 URL 与
发布状态。Sink receipt 把三个证据层分开:

- `release_readback` 证明确切 provider release 达到其 terminal 发布状态。
  Capability 从请求的 release id 与 provider 状态重新计算;provider 提供的
  `verified` 标志不能覆盖不匹配;
- `access_scope_readback` 记录观测到的 scope 与登录要求,或当 provider 对纯
  HTML apps 不暴露该查询时为 typed `unsupported_by_app_type`。其他 provider
  查询失败保持为可重试 `unavailable` 证据状态,不抹掉已验证 release;
- `content_readback` 说明远程内容 digest 是否已验证。捆绑 provider 当前记录
  `unavailable`,因为 provider API 不暴露已发布字节或其 digest;在 provider 能
  提供真实 digest 证据之前,不接受推测性的 `verified` 状态。

因此 app id、在线 URL 或 finished release 证明的是投递生命周期,而不是与本地
artifact 字节级相同。

项目显式绑定 sink,使报告生成保持可移植、外部写默认禁用:

```json
{
  "sink_id": "miaoda_html_delivery",
  "sink_kind": "miaoda_html",
  "sink_role": "delivery",
  "dependency_policy": "optional",
  "capability": {
    "capability_id": "report.miaoda_html.publish",
    "capability_version": "v0"
  },
  "extension": {
    "extension_id": "loopx-lark",
    "extension_version": "1.5.0",
    "protocol": "periodic_report_sink_v0"
  }
}
```

项目或 host 仍拥有 app id、认证、执行决策与访问 policy。Preview 投递只执行校验,
从不调用注入的 publish 或 readback 效果。重复发布应复用同一 app id 与投递幂等
key,而不是每个报告都创建新 app。

公开 CLI 使该边界可执行。
`periodic_report_miaoda_delivery_request_v0` 包含完整归一化 profile、其
`periodic_report_generation_bundle_v0` 与一个 typed
`periodic_report_delivery_intent_v0`:

```json
{
  "schema_version": "periodic_report_miaoda_delivery_request_v0",
  "profile": { "schema_version": "periodic_report_profile_v0" },
  "generation_bundle": {
    "schema_version": "periodic_report_generation_bundle_v0"
  },
  "delivery_intent": {
    "schema_version": "periodic_report_delivery_intent_v0",
    "kind": "hosted",
    "sink_id": "miaoda_html_delivery",
    "sink_kind": "miaoda_html",
    "app_id": "app_example123",
    "idempotency_key": "weekly-report-2026-29"
  }
}
```

上面简写的 profile 与 generation 对象必须替换为完整归一化 receipts。先预览确切
请求:

```bash
loopx periodic-report publish-miaoda \
  --request-json periodic-report-miaoda-request.json \
  --format json
```

Preview 执行大小、profile、binding、extension 与 artifact 检查,但返回
`status=pending_execution` 与 `intent_satisfied=false`。因此本地 HTML 生成是有用
输出,不是托管报告请求已投递的证明。只在 operator 授权外部写后发布:

```bash
loopx periodic-report publish-miaoda \
  --request-json periodic-report-miaoda-request.json \
  --execute \
  --format json
```

命令解析已安装、启用、doctor 验证的 `loopx-lark` revision 及其
`lark.miaoda_html.publish` 权限。认证留在 `lark-cli` 内;请求不接受 token 或
凭据。Provider 发布临时 `index.html`,精确回读 app,并只在相同 app id 与在线
URL 一致、且发布返回的确切 release 回读为 `finished` 时设置
`intent_satisfied=true`。Access-scope readback 只是证据:app 类型特定的不支持
响应保持为 typed 边界,而不是当作猜测的 scope。命令不声称远程内容 digest 验证,
不创建 app,不改变 app 受众,也不改变其访问 scope。禁用或回滚捆绑 extension 可以
移除 provider,而不影响已生成的本地 artifacts。

## 默认编辑契约

可复用 renderer 刻意把受众内容与运维 receipts 分开:

- 可见正文:outcomes、evidence、摘要中表达的影响或风险、状态,以及存在时的具体
  下一步动作;
- 折叠支撑上下文:profile 身份、生成时间、源健康、快照 digests、renderer 血缘、
  运行时注释与投递 receipts;
- 默认省略:关于报告如何生成的叙述、工具使用评论、本地路径、raw 日志或不改变
  受众决策的 policy 说明。

Profiles 可以提供 `editorial.kicker`、`period_label`、`language` 与至多四个
highlights。它们不编写 `editorial.summary`。Builder 选择排名最高的 typed
`outcome` 或 `decision`、`risk` 与 `next_action` 标题,在无专用 next-action
条目时回退到 typed 条目的 `next_action` 字段。它把确切条目/字段血缘记录在
`periodic_report_editorial_orchestration_v0` 中。两个 renderers 都重新计算该
摘要,并拒绝过时或手工编辑的值。本地化 profile language 还选择内置报告控件、
compiler 标签与附录标签。条目可以使用至多四个有序 `details` 行把密集证据拆成
具名事实,外加 `tag_labels` 显示本地化标签而不改变 canonical tags。主摘要限制为
360 字符;primary `capability_change` 条目要求至少两个具名 details,使冗长机制
叙述不能回到一堵文本墙。Artifact 一致性、archive-provider canaries、幂等性、
digests、renderer 版本与投递 readback 属于支撑条目或 sink receipts。`source_ref`
只是导航源;冻结声明应由源快照 digest/ref 支撑,而不是开放式的实时 query。

源适配器仍通过指派 `content_kind` 与 `value_rank` 决定每个事实的含义;profiles
决定报告分段与受众。编排层只组合这些 typed 事实,从不提升 `runtime` 或
`delivery_receipt` 条目。Renderer 不猜测业务语义、不删除支撑事实,也不静默重写
弱报告;它验证编译契约,并在事实归一化后给所有项目一个可读默认。

HTML 生成与发布分开。静态站点、Lark HTML 或其他托管适配器可以发布 artifact 并
返回精确 readback receipt,但 renderer 既不选择目的地也不执行写。HTML host 应
发布生成的 artifact,而不重新渲染其归一化文档。应用另一展示的 host 必须保留
artifact 的 primary/supporting 可见性 policy,并在动态内容挂载后验证直接分段
哈希。项目 profiles 仍拥有语言、布局 policy、受众、cadence 与选择规则。

## Personal Workspace 回读

Goal Channel sink 验证投递并提交发布游标后,本地 status server 可以把最新报告
暴露为 typed、content-addressed 里程碑投影。其紧凑索引有意省略报告散文;完整
投影通过仅 loopback 的冷路径 fetch,并只在 generation id 与 digest 匹配当前发布
游标时被接受。待决投递工作与仅生成 artifact 保持不可见。视图仅作信息,没有
浏览器写 authority。
