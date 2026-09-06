# 本地 CPA 运营器

该包现在包含 `loopx-cpa-operator`,一个单独调用的本地 CLI。受管理扩展协议保持只读且无权限。安装或运行该协议不会启用运营器、发现凭据、启动 CPA、改动 App,或写入任务存储。

## 路由预设

运营器的 `abc-sol-astra` 预设使用既有的 `compile_catalog` 环契约。其凭据、App 目录、验证与观察共用同一组选择器定义。

| 可见选择器 | 候选顺序 | 终态行为 |
| --- | --- | --- |
| `auto/MODEL` | A → B → C | 报告耗尽;无模型替换 |
| `fast/auto/MODEL` | A → B → C | 请求原生 Fast;无模型替换 |
| `auto-with-ds/MODEL` | A → B → C → DeepSeek | 显式 Standard 文本兜底 |
| `gpt-5.6-luna` | A → B → C | 报告耗尽;无模型替换 |

Sol 与 Astra 各有两种 Standard Auto 选项与一个三账户 Fast Auto 选项。Luna 仍以三账户路由的形式可见:共七个选择器行。目录保留 18 个隐藏兼容行(裸 Sol/Astra 模型 id、Prefer A/B/C 及其 Fast 变体、手动 Ark 标识符),因此既有任务保持其元数据与路由 id。

旧版 Standard、裸 Sol/Astra 与 Prefer 别名现在都停留在 A/B/C 内。Auto OAuth 别名使用 `fork: true` 在 CPA 中保留原始模型 id;仅靠自别名无法保留它们。只有 `auto-with-ds/` 别名允许 Ark。既有任务不会被静默切换进去。四路由选择器不宣传 Fast;三账户选择器保留原生速度层级。含图像的历史会排除仅文本兜底。

偏好的旧版账户仍是入口,不是排他性固定。Auto 为会话稳定性保留合格订阅亲和;恢复后的更高优先级订阅不会强行夺走合格绑定。从三账户路由移除 Ark 别名,防止旧的退化绑定让这些路由停留在 DeepSeek。

四路由运营器需要带 [custom-tool namespace recovery](https://github.com/router-for-me/CLIProxyAPI/pull/5558) 的 CPA 构建。Chat Completions 以带 `input` 字符串的 functions 编码 custom tools。上游采纳情况在[维护者 issue](https://github.com/router-for-me/CLIProxyAPI/issues/5560) 中跟踪,因为该仓库限制直接翻译 PR。CPA 必须在流式与非流式响应中恢复 `custom_tool_call`、原始 input、namespace 与 call id。历史 custom 调用必须按与当前声明相同的限定名重放。缺失的 namespace 只能从唯一当前声明中恢复;精确名优先,歧义名绝不能猜。这修复的是传输而非模型行为:DeepSeek 仍可能选择较差的代码或错过 Code Mode 的输出指令。编码任务默认保持三订阅路由。显式 Ark 访问仍按 id 可用。

CPA 拥有在线重试与冷却。运营器保持 10 次 CPA 重试与最多 65 秒的建议等待。App 重试是独立的;单次环遍历不是总 Turn 时间的上限。不要为恢复一个账户而全局禁用冷却:它会反复命中已知耗尽的订阅。

如果上游账户比先前报告的 reset 更早恢复,CPA 仍可能缓存旧的冷却。确认恢复后,用 `reset-cooldown --slot b --execute`(见下方可运行命令)允许新尝试。这使用 CPA 的目标管理 API,不轮换 OAuth 令牌、不重启其他账户、不修改任务存储,也不声称配额已补充。它拒绝禁用 slot。用有界的实时请求与实际账户选择验证;成功的缓存重置本身不是健康检查。这个显式运营器操作不会安装后台轮询循环。


Fast 行设置一个选择器默认值,并且校验和固定的请求插件会在别名映射前强制 `service_tier=priority`。验证 provider 端请求,而不只是 App 的线程默认值:自定义 provider 的 App 可能报告 `default`。上游响应也可能报告 `default`;priority 请求并不承诺上游提供了加速层级。

## 配置与激活

在专用 Python 3.11+ 环境中安装:

```sh
python3 -m pip install packages/loopx-codex-provider-routing
loopx-cpa-operator --config /absolute/private/operator.json validate
loopx-cpa-operator --config /absolute/private/operator.json --execute validate
```

第一个命令生成无凭据计划,不执行任何写入或网络/进程操作。`--execute` 只授权这一次调用。提供一个 mode-0600 的 JSON 文件,带 `schema_version: "loopx_cpa_local_operator_v1"`,内容为:

- `paths`: `runtime_root`、`temporary_root`、`binary`、`plugin_directory`、`codex_binary`、`gpt_cache`、`astra_cache`、`ark_catalog`、`ark_profile_catalog`、`ark_env_file` 的显式绝对引用;可选 `login_source`;
- `binary_sha256`、`plugin_sha256`、`source_commit`:确切的评审产物固定;
- `port`:一个非特权本地 TCP 端口;`launchd_label`:自有服务 id;
- `ark_base_url`:一个无凭据 HTTPS 端点;
- `ark_model`、`ark_pro_model`:上游模型标识符。

把该文件保存在 Git 之外。提供引用,绝不放内联键或令牌。可写根目录必须是 Git 工作树之外的专用目录。slot 文件是配置的 auth 目录下的 basenames;路径遍历、重复与符号链接目标都会被拒绝。每个 receipt 都保持符号化且无凭据。API 密钥只由本地运营器读取,并放入私有的临时运行时配置。凭据、缓存、二进制、插件产物、日志、快照与服务管理器文件永远不会成为包资源或 LoopX 状态。

每个模型的 App 缓存就是它的元数据来源;Astra 不继承 Sol 的 prompt、上下文窗口或模型能力。Auto 保留既有 low-through-max effort 策略,而优选路由保留原生层级。CPA 必须刷新其模型定义:旧的 `-local-model` 目录可能遗漏新模型,即使 App 选择器已宣传它。运营器启用 CPA 的模型定义刷新,同时保持可执行文件/插件哈希固定。模型定义刷新与二进制升级是两个独立操作。

## 本预设之外的复用

该包的可复用路由边界是 `compile_catalog(source)` 与托管的[路由合同](CONTRACT.md):调用方提供符号化 profile、环、路由与能力声明。本运营器中的 A/B/C 与 Sol/Astra 名称是具体预设,不是该合同的要求。修改合同不会安装运行时或授予凭据访问。

工具身份恢复属于 CPA 的 Responses 翻译器,只依赖当前请求的工具声明,而不依赖账户 slot、模型名或特定兼容 provider。早期冷却恢复使用 CPA 的既有管理 API;本运营器在本地解析配置的符号化 slot 并发出免凭据回执。凭据获取、服务监督与实时可用性验证仍是显式的宿主动作。

## 命令

```sh
# 把显式配置的当前登录导入一个空置的符号化 slot。
loopx-cpa-operator --config /absolute/private/operator.json enroll --slot c
loopx-cpa-operator --config /absolute/private/operator.json --execute enroll --slot c

# 在更新任何路由元数据之前验证全部三个身份。
loopx-cpa-operator --config /absolute/private/operator.json --execute reconcile
loopx-cpa-operator --config /absolute/private/operator.json --execute write-catalog

# 进程监督:配置自有服务管理器来调用它。
loopx-cpa-operator --config /absolute/private/operator.json --execute serve

# 无内容的实时与隔离 App Server 回读。
loopx-cpa-operator --config /absolute/private/operator.json --execute status
loopx-cpa-operator --config /absolute/private/operator.json --execute validate
loopx-cpa-operator --config /absolute/private/operator.json --execute probe
loopx-cpa-operator --config /absolute/private/operator.json --execute route-status
```

登记会检查账户身份、令牌过期、空置 slot 与重复账户。它不触碰来源登录。随后的刷新归 CPA。如果另一个客户端并发轮换该登录并引发刷新冲突,请使用单独授权的 OAuth 登录。绝不复制任务数据库或 rollout。

`serve` 把自身进程替换为固定的 CPA 可执行文件;重启监督归服务管理器。`start`/`stop` 用于非托管进程。`stop` 拒绝向 launchd 托管或无关的进程发信号。对于 launchd,在变更其程序前先卸载具体配置的服务,然后再次加载。运营器本身不修改 LaunchAgents、App bundle 或 App 进程。变更模型目录后,只重启受影响的 App,并验证 7 可见/18 隐藏行回读。模型注册不是账户资格的证明,也不证明模型调用成功;请另外执行一次有界的实时请求。

## 早期配额恢复

```sh
# 先计划;执行命令只清除指定 slot 的 CPA 冷却。
loopx-cpa-operator --config /absolute/private/operator.json reset-cooldown --slot b
loopx-cpa-operator --config /absolute/private/operator.json --execute reset-cooldown --slot b
loopx-cpa-operator --config /absolute/private/operator.json --execute route-status
```

重置后运行一次有界的模型请求,然后再次检查 route-status。其成功必须识别出恢复的订阅;另一账户成功不是命名 slot 的证据。新的限额响应会重新启用冷却。

## 回滚与禁用

`reconcile`、`write-catalog` 与 `enroll` 会发出一个 `rollback_snapshot` 标识符。快照留在配置的私有状态目录中。恢复一个:

```sh
loopx-cpa-operator --config /absolute/private/operator.json rollback --snapshot-id SNAPSHOT_ID
loopx-cpa-operator --config /absolute/private/operator.json --execute rollback --snapshot-id SNAPSHOT_ID
```

完整性与目标检查先于写入。把路由元数据恢复到最新凭据上,而不是恢复陈旧的 OAuth 刷新令牌。快照之后新登记的凭据会被保留,但在回滚期间禁用。恢复进程配置或目录时,重启自有服务/App。运营器绝不删除凭据或改动任务存储。

要禁用,请卸载运营器自有的服务,或停止其非托管进程。从安装备份恢复之前服务程序与私有配置,或卸载专用环境。保留 auth/状态以备恢复。卸载受管理的只读扩展不会停止独立安装的运营器服务。

## 验证

```sh
python3 packages/loopx-codex-provider-routing/smoke/operator_smoke.py
python3 packages/loopx-codex-provider-routing/smoke/codex_provider_routing_smoke.py
```

离线测试只使用合成凭据与临时目录。它们覆盖默认关闭的隔离、slot/目标边界、Sol/Astra 对等性、环顺序、回滚完整性、令牌轮换与遗留 A/B 资格判定。`qualify_snapshot` 接受 `routing_preset: "abc-sol-astra"`;省略它则保持原有 A/B/Sol 契约,以供既有消费者使用。
