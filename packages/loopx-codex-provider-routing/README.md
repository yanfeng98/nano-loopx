# LoopX Codex Provider Routing

这个可选 LoopX 扩展拥有单个 Codex App 使用 CPA 作为其多订阅、多 provider 数据面时的 public-safe 集成契约。它打包了配置编译、资格回读与升级规划,而不成为模型代理或凭据权威。

## 定位

本包是一个供给独立集成 provider 的**扩展**,不是内置 capability:

- Codex App 拥有任务设置、Turn 快照与会话存储;
- CPA 拥有凭据选择、在线路由、重试与流适配;
- 运营方拥有 OAuth/API 凭据、进程安装与私有的构建/回滚 receipt;
- LoopX 拥有这个带版本号的公开契约、受管理的扩展生命周期、public-safe 资格结果与升级关卡。

该扩展不声明任何权限,也不执行任何写入。它不读取 `HOME`、`CODEX_HOME`、auth 文件、进程表或网络端点。调用方必须在资格判定前把本地观察转换为无内容的快照 schema。

## 操作

`compile_catalog`
: 把无密钥的逻辑 profile 与路由编译为
  `codex_provider_routing_catalog_v1`。一个有界账户环可以支撑 Auto、
  Prefer A、Prefer B 与 Luna,而不必向用户展示多个环。
  路由亲和只是提示,必须在每次尝试时对照所需输入模态与服务层级重新验证。一个仅文本的终态兜底可以服务兼容的 Sol 请求,但不能接收图像历史;Luna 没有异构兜底尾部。一条路由可以声明一个 `fast_selector`;
  编译器随后发出一个 `fast/<route>` 兄弟行,其候选只限于具备 Fast 能力的 provider,默认层级为 `fast`。

`normalize_selector_request`
: 在 provider 别名映射之前解析原始 App 模型选择器。`fast/` 选择器被剥离为其底层路由,并把 wire 请求层级强制为 `priority`;普通选择器保留调用方的服务层级。如果保留的层级是 `priority`,候选接纳仍会切换为仅限具备 Fast 能力者,因此原生 Fast 入口无法到达 Ark。
  该操作不接受 prompt、auth 或请求体。调用方可以要求 `custom_tool_call`;只保留普通 `function_call` 条目的 provider 随后会在遍历前被移除,因此 Code Mode 会失败关闭而不是落到不兼容的兜底。缺失的 capability 元数据视为仅函数,包括 0.7.0 之前生成的目录;自定义 transport 支持必须在资格判定后显式声明。

`qualify_desktop_patch`
: 检查补丁后桌面运行时的 public-safe 构建后证据:一个带版本号的补丁锚点、每个已改动文件的 ASAR 完整性、存储在 bundle 元数据中的 ASAR 头摘要、代码签名、启动与 heartbeat 回读。它诊断升级漂移,但从不编辑或签名 App bundle。

`qualify_snapshot`
: 检查无内容的 App/CPA 回读:可见与隐藏路由、输入模态、显式 Fast 兄弟行、各行的默认层级、活动请求规范化(包括有效优先级接纳)、回环绑定、模态感知亲和、类型化路由遍历、持久设置 revision 与提交屏障。

`qualify_heartbeat_transport`
: 检查一次调度器注入的 heartbeat 的无内容宿主观察。heartbeat 信封必须以 `role=user` 作为用户输入进入 Turn。把它编码为工具结果,尤其是作为 `automation_update` 结果,会以稳定错误码失败,并把修复责任指派给 Codex App heartbeat transport 而不是 LoopX prompt 或模型 provider。该操作诊断边界;它不补丁、不重启也不修改 Codex App。

`qualify_host_control_recovery`
: 检查 CPA 对孤儿宿主控制输出的恢复的无内容观察。只有已确认的宿主名、无 `call_id`、无匹配模型调用且语义输出非空,才可以重新类型化为 `role=user` 消息。资格判定还要求证明下一个观察到的动作遵循了保留的指令;仅 HTTP 成功不能通过。未知、成对或空输出必须保持类型化 `409` 失败。

`qualify_quota_recovery`
: 把一次成功的账户 quota 重置与发生在它之前的 cooldown 观察排序。更新的重置必须使旧 cooldown 失效,并在兜底被接纳前触发一次有界账户探测;只有新的 quota 受限探测才能创建替代 cooldown。

`qualify_outage_recovery`
: 把 provider 范围的事故结束与它造成的陈旧原生 cooldown 及降级兜底亲和排序。比 cooldown 来源更新的恢复信号必须使 cooldown 失效,运行一次有界探测,并在原生能力请求被接纳前清除或重新验证兜底绑定。只有在探测仍报告事故时,文本流量才可以继续留在兜底上。

`qualify_tool_transport`
: 检查请求的工具条目类型能否在 provider 适配后存活,并检查宿主分发是否完成。特别是 Code Mode 的 `custom_tool_call` 不得降级为 `function_call {"input": ...}`。

`project_runtime_status`
: 把稳定的、与路由无关的宿主 ChatGPT 身份状态与无内容的 CPA 执行观察及符号化 A/B quota/活动量连接起来。它对照编译路由验证实际尝试链,推导剩余 quota,并且只在尝试了多个 provider 时报告兜底。它从不接受账户身份、auth 文件名或令牌。

`reconcile_integration_candidate`
: 对照其最后同步 receipt 验证一个有序的多来源 CPA 候选。它证明确切的 base/source 指针、所需 runtime seam 覆盖以及是否需要协调,然后为 LoopX 核心 `integration-branch` 返回输入。它从不拉取、合并、推送、构建或部署。

`upgrade_plan`
: 从公开的当前与目标 ref 以及变更的 seam 生成一个有界的升级/回滚清单。它从不安装、切换或删除运行时。

## 受管理的用法

在同一激活的 Python 环境中运行这些命令:

```bash
python3 -m pip install packages/loopx-codex-provider-routing
loopx extension install \
  --manifest packages/loopx-codex-provider-routing/extension.toml \
  --execute \
  --format json
loopx extension doctor loopx-codex-provider-routing --execute --format json
loopx extension run loopx-codex-provider-routing \
  --input-json packages/loopx-codex-provider-routing/examples/request.json \
  --execute \
  --format json
loopx extension run loopx-codex-provider-routing \
  --input-json packages/loopx-codex-provider-routing/examples/normalize-request.json \
  --execute \
  --format json
loopx extension run loopx-codex-provider-routing \
  --input-json packages/loopx-codex-provider-routing/examples/heartbeat-transport.json \
  --execute \
  --format json
loopx extension run loopx-codex-provider-routing \
  --input-json packages/loopx-codex-provider-routing/examples/host-control-recovery.json \
  --execute \
  --format json
loopx extension run loopx-codex-provider-routing \
  --input-json packages/loopx-codex-provider-routing/examples/desktop-patch.json \
  --execute \
  --format json
loopx extension run loopx-codex-provider-routing \
  --input-json packages/loopx-codex-provider-routing/examples/quota-recovery.json \
  --execute \
  --format json
loopx extension run loopx-codex-provider-routing \
  --input-json packages/loopx-codex-provider-routing/examples/outage-recovery.json \
  --execute \
  --format json
loopx extension run loopx-codex-provider-routing \
  --input-json packages/loopx-codex-provider-routing/examples/tool-transport.json \
  --execute \
  --format json
loopx extension run loopx-codex-provider-routing \
  --input-json packages/loopx-codex-provider-routing/examples/integration-candidate.json \
  --execute \
  --format json
```

扩展运行时拥有 install/enable/disable/doctor 注册。包安装仍然是一个显式的包管理器动作;这两个操作都不会下载 CPA,也不会授予凭据。

## 脚本迁移边界

早期运营脚本分为三类:

| 脚本职责 | 扩展所有权 |
| --- | --- |
| 无密钥的 profile/catalog 编译器 | 迁入 `compile_catalog`,并以模态/服务层级资格加以强化 |
| Fast selector 目录生成与请求层级规范化 | 迁入 `compile_catalog` 加 `normalize_selector_request`;CPA adapter 保持为在线执行点 |
| Code Mode 工具形态接纳与回读 | 迁入 profile `tool_transports`、`normalize_selector_request` 与 `qualify_tool_transport`;不兼容的兜底在首个输出前失败 |
| App/CPA 模型回读断言 | 迁移为无内容的 `qualify_snapshot` 契约 |
| 补丁后桌面的 ASAR/签名/启动检查 | 迁移为 `qualify_desktop_patch`;有副作用的 bundle patcher 仍由运营方拥有 |
| quota 重置与缓存 cooldown 的协同 | 迁移为 `qualify_quota_recovery`;在线 cooldown 失效与探测仍归 CPA |
| provider 事故结束与陈旧原生 cooldown 及降级兜底亲和 | 迁移为 `qualify_outage_recovery`;在线失效、有界探测与绑定重新验证仍归 CPA |
| 有序 PR/patch 候选清单与漂移检测 | 迁移为 `reconcile_integration_candidate`;Git 组合仍由 LoopX 核心 `integration-branch` 拥有 |
| 升级矩阵、快照顺序与回滚触发器 | 迁移为 `upgrade_plan`;效果执行仍归运营方 |
| CPA 进程启动器、OAuth 登录/协调、Ark 密钥加载 | 排除;这些是 provider 运行时与凭据生命周期,不是 LoopX 状态 |
| 直接写 App 配置、私有快照与回滚副本 | 从 v0 排除;产品化前需要显式的权限化执行信封 |
| 原始日志/证据收集 | 排除;运营方 adapter 只能向 `project_runtime_status` 提交符号化、无内容的观察 |

完整的逐职责映射与无凭据配置引用见 [`REFERENCES.md`](REFERENCES.md)。

规范架构、资格矩阵与公开 PR 谱系见 [`RUNBOOK.md`](RUNBOOK.md)。可靠的 SSH 出站仍是共享的 LoopX 集成,因为它在 CPA 之外同样有用。

## 验证

```bash
python3 packages/loopx-codex-provider-routing/smoke/codex_provider_routing_smoke.py
python3 packages/loopx-codex-provider-routing/smoke/recovery_contracts_smoke.py
python3 -m pytest -q tests/extensions/test_colocated_extension_layout.py
loopx check --scan-path packages/loopx-codex-provider-routing
```

## 可选本地运营器

版本 0.9 增加了一个单独调用的 `loopx-cpa-operator` CLI,用于显式本地配置、账户登记、目录生成、进程监督与回读。它自带 A/B/C Sol/Astra 预设,同时保留受管理扩展的只读协议与原始 A/B 资格默认值。激活、确切目标边界、验证、回滚与禁用命令见 [Local CPA operator](OPERATOR.md)。
