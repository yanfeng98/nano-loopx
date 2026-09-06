# 契约与权威边界

协议:`loopx_codex_provider_routing_extension_v0`

请求:`loopx_codex_provider_routing_request_v0`

响应:`loopx_codex_provider_routing_response_v0`

目录:`codex_provider_routing_catalog_v1`

运行时状态:`codex_provider_routing_runtime_status_v0`

集成候选:`codex_provider_integration_candidate_v0`

Heartbeat transport 资格判定:`codex_app_heartbeat_transport_qualification_v0`

桌面补丁资格判定:`codex_desktop_patch_qualification_v0`

Quota 恢复资格判定:`codex_quota_recovery_qualification_v0`

事故恢复资格判定:`codex_outage_recovery_qualification_v0`

Tool transport 资格判定:`codex_tool_transport_qualification_v0`

该 provider 每次调用恰好接受一个 public-safe 操作,并返回确定性的 JSON 结果。任何含有凭据形态键的输入都会在任何操作运行前失败。

该 provider 没有 Kernel 状态转换权威,也没有外部写权限。资格结果只是证据,不是编辑 Codex home、安装 CPA、更换模型、开始 Turn、轮换凭据或合并上游 PR 的许可。

Heartbeat 资格判定只接受符号化的、无内容的形态事实。对于携带 `heartbeat_xml` 信封的 `automation_heartbeat`,合规的投递方式是 `user_input` 且 `message_role=user`。`tool_output` 观察不合规,因为它改变了调度器事件的语义角色;provider 报告稳定错误码,并且从不推荐提示词或模型调优作为修复手段。App 检查、二进制改动与进程生命周期仍处于这个只读扩展之外。

集成候选操作与 LoopX 核心 `integration-branch` 组合使用,但不取代它。它只接受公开 Git ref、完整 commit SHA、符号化来源 ID、来源种类与变更 seam 标签。调用方必须同时提供当前观察与最后一次成功的同步 receipt。每个观察到的来源 head 必须等于其声明的确切 head,有序来源集必须覆盖每个必需的 seam。base 移动、来源移动或意外的集成 head 产生 `sync_required`;不执行任何 Git 效果。

在单独授权的核心同步之后,部署仍归运营方。返回的契约要求一个内容寻址的二进制、隔离的 smoke、字段级配置比较、目录/重试/运行时回读,以及一个保留的旧二进制/配置指针。任务/会话存储原地保留,绝不会作为候选维护的一部分被复制或删除。

运行时状态刻意有两个投影。`host_identity` 只记录运营方的 ChatGPT 身份被保留、但不被自定义 provider 投影;其 `route_binding` 恒为 `none`。`route_intent` 与 `execution` 分别报告请求的逻辑路由与 CPA 实际尝试的符号化 provider profile。对 B 的直接 Auto 命中不是兜底;只有在尝试了第二个候选后,兜底才为真。`route_intent.fast` 从选中的 `fast/` 路由 slug 推导。调用方只有在与那个 slug 一致时才可以包含冗余布尔。

账户观察可以包含符号化目录 profile id、就绪、有界的成功/失败计数器与百分比 quota 窗口。provider 推导 `remaining_percent`。邮箱地址、auth id/文件、凭据、私有路径、任务 id 与请求内容在公开边界上是被禁止的。

目录定义一个账户环,而不是每个可见路由一个环。Auto 与 Luna 通过亲和进入同一个环(冷任务则进入其第一个成员);Prefer A 与 Prefer B 选择不同的入口。该环最多遍历一次。路由之后可以追加一个终态兜底尾部,但尾部不是环成员,也绝不会被再次访问。显式 Ark 仍然是手动硬固定。

弹性路由在环遍历与亲和之前应用基线接纳过滤器:

1. 每个候选必须支持完整请求历史所需的全部模态;
2. 当选为 Fast 时,每个候选必须支持请求的服务层级。

当宿主要求特定的工具条目 transport 时,第三个过滤器生效。每个省略 `tool_transports` 的 profile,包括传统原生 Codex profile,都保守地默认为仅 `function_call`。adapter 只有在证明其保留了原始负载与条目类型后,才可以声明 `custom_tool_call`。因此,要求 `custom_tool_call` 的 Code Mode 请求不能静默落到未获资格或仅函数的 provider 上。独立的资格判定操作会比较请求与观察到的条目类型,并要求分发已完成。

亲和只能对剩余的合格环成员重排序。如果没有成员剩下,路由在首个可见输出或工具调用之前失败关闭。因此仅文本的兜底可以服务文本型 Auto 请求,但不能接收图像历史。Luna 没有异构兜底尾部。

Fast 被建模为对既有路由的选择器投影。一条路由可以声明一个 `fast_selector`;编译器发出 `fast/<route>`,把其候选过滤为具备 Fast 能力的 profile,并把其默认层级标记为 `fast`。`normalize_selector_request` 只消费原始选择器与可选的服务层级:Fast 行解析到底层路由并把 wire 层级强制为 `priority`,而普通行保留请求。保留的 `priority` 层级在候选接纳中仍被视为有效的 Fast 状态,因此显式兄弟行与原生 Fast 入口都只限于具备 Fast 能力的 provider。它从不接受 prompt 或请求体。Fast 请求不能落到不支持 Fast 的 provider 上。

已应用的 quota 重置会与创建 provider cooldown 的观察排序。当重置更新时,旧 cooldown 即为陈旧:CPA 必须在选择兜底前使其失效并探测该账户。新鲜探测要么成功,要么返回新的 quota 限额;只有后者才允许新的 cooldown 与兜底。该契约防止一个已重置账户直到过时的有效期结束前都无法可达。

观察到的 provider 事故结束按同样方式排序。由事故错误(例如所有原生 profile 上反复出现 4xx/5xx)创建的 cooldown,一旦观察到比其来源更新的恢复信号即为陈旧。CPA 必须使该 cooldown 失效、完成一次有界探测并重新验证任何降级的兜底亲和,然后才允许接纳需要原生能力的请求。兜底只有在探测仍报告事故时才可继续服务仅文本流量;原生能力请求必须失败关闭,而不是穿过未获资格的兜底绑定。

补丁后的桌面构建有独立的构建后关卡。补丁锚点必须在当前构建中唯一,每个被改变的 ASAR 成员必须有匹配的逐文件完整性,结果 ASAR 头摘要必须与 bundle 元数据匹配,运行时必须已签名且能启动,补丁后的 heartbeat 路径必须通过回读。整档哈希不能替代 Electron 的头与逐文件检查。provider 只消费布尔与计数;bundle 变更与签名仍是运营方效果。

Codex App 设置应用同样的证据规则。选择器标签不能证明正在运行的 Turn 采用了新模型。资格判定要求一个持久的设置 revision 以及与之匹配的 Turn receipt。无内容的运行时快照还必须报告每条弹性路由的入口、有序候选、终态尾部与最大循环次数;仅目录编译不能为一次部署判定资格。
