# 本地 CPA 运营器

该包现在包含 `loopx-cpa-operator`,一个单独调用的本地 CLI。受管理扩展协议保持只读且无权限。安装或运行该协议不会启用运营器、发现凭据、启动 CPA、改动 App,或写入任务存储。

## 路由预设

运营器的 `abc-sol-astra` 预设使用既有的 `compile_catalog` 环契约。其凭据、App 目录、验证与观察共用同一组选择器定义。

| 入口 | Sol 与 Astra 候选顺序 | 终态兜底 |
| --- | --- | --- |
| Auto / Prefer A | A → B → C | Ark,用于符合条件的 Standard 文本请求 |
| Prefer B | B → C → A | Ark,用于符合条件的 Standard 文本请求 |
| Prefer C | C → A → B | Ark,用于符合条件的 Standard 文本请求 |
| Fast 变体 | 相同账户顺序 | 无 |
| Luna | A → B → C | 无 |

Sol 与 Astra 都暴露 Auto、Prefer A/B/C 与四个 Fast 兄弟行。加上 Luna 与四个已有的 Ark/兼容行,App 目录共有 21 行。裸的 Sol/Astra 标识符是兼容别名,不是选择器行。首选账户是入口,不是排他性固定。不合格、冷却中或已耗尽的账户可以被跳过。Auto 亲和只是一个提示,CPA 必须对照账户可用性、输入模态与服务层级重新验证。

Standard 路由保持既有的异构兜底,因此其模型标签会显式点名 Ark。图像历史、有效 priority 层级与不支持的 tool transport 不得被静默发送到仅文本/仅函数的 provider。Code Mode 需要 CPA 候选已获资格的 `custom_tool_call` 适配;仅靠扩展编译器无法强制 wire 能力。Fast/Luna 路由完全没有 Ark 别名。透明重试在首个可见输出或工具调用处结束。

被固定的 CPA 运行时仍然是唯一的在线路由器。运营器生成配置与元数据;它不重新实现请求重试。现有重试设置保持为 10 次 CPA 重试、最多 65 秒的建议等待、每次选择遍历一个账户环。外层 App 重试是独立的,可以开始另一个请求:一次环遍历**不是**总 Turn 时间的上限。账户 A 不再绕过冷却。新鲜 quota 重置与恢复探测仍是 CPA 的责任;缓存的 quota 观察不是永久禁用某个账户的许可。

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

`serve` 把自身进程替换为固定的 CPA 可执行文件;重启监督归服务管理器。`start`/`stop` 用于非托管进程。`stop` 拒绝向 launchd 托管或无关的进程发信号。对于 launchd,在变更其程序前先卸载具体配置的服务,然后再次加载。运营器本身不修改 LaunchAgents、App bundle 或 App 进程。变更模型目录后,只重启受影响的 App,并验证 21 行回读。模型注册不是账户资格的证明,也不证明模型调用成功;请另外执行一次有界的实时请求。

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
