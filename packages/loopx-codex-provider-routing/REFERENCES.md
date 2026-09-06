# 运营脚本与配置迁移

这份清单记录了工作中的运营原型如何映射到公开扩展。它命名的是职责,而不是本地路径、宿主身份、端口、账户或私有 receipt。

## 脚本清单

| 原型职责 | 处理方式 | 公开所有者 |
| --- | --- | --- |
| 编译无密钥 profile、单遍账户环与逻辑模型路由 | 迁移并强化 | `contract.py::compile_catalog`;优选入口、终态兜底尾部、模态与 Fast 资格都是显式的 |
| 生成显式 Fast 兄弟行并注入 Fast 请求层级 | 迁移为 public-safe 编译器/规范化器契约 | `contract.py::compile_catalog` 加 `normalize_selector_request`;在线 CPA adapter/plugin 在别名映射前执行相同决策 |
| 把宿主身份与实际账户路由及 quota 分开投影 | 迁移 | `operator_observations.py` 归约本地观察;`contract.py::project_runtime_status` 保留公开边界 |
| 从缓存的模型条目生成 Codex 目录,启动隔离 App Server,调用 `model/list` | 迁移 | `operator_catalog.py` 使用显式缓存/二进制引用;`selectors.py` 共用现有环编译器 |
| 跨版本化锚点、ASAR 成员/头完整性、签名、启动与 heartbeat 回读验证补丁后的桌面运行时 | 迁移为只读资格判定 | `qualify_desktop_patch`;补丁、签名与进程生命周期仍归运营方的效果 |
| 在更新的成功 quota 重置后使 provider cooldown 失效 | 迁移为恢复排序契约 | `qualify_quota_recovery`;CPA 拥有在线失效与有界重新探测 |
| 在 provider 范围的事故结束后使事故 cooldown 失效并重新验证降级兜底亲和 | 迁移为恢复排序契约 | `qualify_outage_recovery`;CPA 拥有在线失效、有界探测与绑定重新验证 |
| 跨异构兜底保留 Code Mode 工具条目形态 | 迁移为接纳加资格判定 | profile `tool_transports`、`normalize_selector_request` 与 `qualify_tool_transport`;adapter 必须在声明支持之前证明自定义条目得到保留 |
| 对照确切 head 与必需 seam 协调有序的多 PR 候选 | 迁移为 public-safe 规划契约 | `reconcile_integration_candidate` 返回核心 `integration-branch` 输入;Git 效果仍处于扩展之外 |
| 准备/启动/serve/stop CPA;协调 OAuth slot;加载引用的凭据 | 迁移为显式本地 CLI | `operator.py`、`operator_runtime.py` 与 `operator_settings.py`;私有配置与凭据仍处于 Git 与只读扩展协议之外 |
| 快照 App/选择器配置、验证哈希并回滚选中的文件 | 规划契约已迁移 | `upgrade_plan` 拥有顺序、矩阵与回滚触发器;文件系统效果需要未来请求绑定的执行信封 |
| 扫描本地配置/auth 文件中的密钥模式 | 拆分 | `reject_private_material` 保护扩展输入/输出;扫描所有者本地文件仍是运营方 preflight |
| 生成故障转移证据行 | 已替换 | `upgrade_plan.required_checks` 与 `qualify_snapshot.checks` 是公开证据词表;原始证据目录被排除 |
| 读取 CC Switch SQLite 并启用其故障转移开关 | 已退役 | CPA 是唯一在线数据面;CC Switch 保持为引导/回滚工具,且不得重新获得路由权威 |
| Python 路由、事务、outbox 与 turn-lease 模拟器 | 仅参考原型 | 稳定规则移入 runbook、契约与 CPA 上游测试;LoopX 不再发布第二个路由器实现 |
| Provider 历史与 SSE 规范化原型 | 上游化,不做重复 | CLIProxyAPI PR #5410 取代已关闭的 PR #5220,成为实现所有者 |
| uTLS 连接实验 | 上游化,不做重复 | CLIProxyAPI PR #5261 是实现所有者 |
| 路由特定兜底环 | 上游化,不做重复 | CLIProxyAPI PR #5336 是实现所有者 |
| OpenAI 兼容的有界限速等待 | 上游化,不做重复 | CLIProxyAPI PR #5435 传播 `Retry-After`,只对显式 TPM 限额使用一分钟兜底,并保持通用 429 行为不变 |
| 无分隔符兼容 SSE 与可恢复的孤儿宿主输出 | 集成 public-safe 补丁,不做重复 | CPA 集成候选移除宿主工具身份,但把已确认的孤儿控制输出重新类型化为用户消息;资格判定必须证明指令被遵循,而未知、成对与空输出保持为类型化失败 |

## 配置引用

该包为每个操作保留无凭据示例,包括:

- [`examples/request.json`](examples/request.json):由一个账户环支撑的逻辑 profile 与模型路由,用于 `compile_catalog`;
- [`examples/normalize-request.json`](examples/normalize-request.json):一次强制 `priority` 但不接收请求体的 Fast 选择器规范化;
- [`examples/runtime-status.json`](examples/runtime-status.json):带符号化 quota/活动量观察的双重宿主与路由身份投影;
- [`examples/qualification-snapshot.json`](examples/qualification-snapshot.json):用于 `qualify_snapshot` 的无内容 App/CPA 回读;
- [`examples/upgrade-request.json`](examples/upgrade-request.json):用于 `upgrade_plan` 的确切公开 ref 与变更 seam。
- [`examples/integration-candidate.json`](examples/integration-candidate.json):用于 `reconcile_integration_candidate` 的有序来源 ref、确切 head、必需 seam 与最后同步观察。
- [`examples/desktop-patch.json`](examples/desktop-patch.json):构建后的 ASAR、签名、启动与 heartbeat 资格判定;
- [`examples/quota-recovery.json`](examples/quota-recovery.json):带界重新探测的重置/cooldown 排序;
- [`examples/outage-recovery.json`](examples/outage-recovery.json):事故结束排序,含陈旧 cooldown 失效、有界探测与亲和重新验证;
- [`examples/tool-transport.json`](examples/tool-transport.json):请求与观察到的工具条目 transport 以及分发结果。

[`templates/codex-app-config.toml`](templates/codex-app-config.toml) 与
[`templates/cpa-config.public.yaml`](templates/cpa-config.public.yaml) 保留了工作字段形态与重试/Fast 默认值。App 保持 30/30 外层恢复预算,而 OpenAI 兼容文本兜底多获得一轮 provider 轮询与 65 秒 cooldown 上限。它们包含占位符,省略了一切带凭据的 CPA 段。扩展从不填充这些占位符,也不把模板写入 Codex home。

## 本地运营器升格

有副作用的 adapter 现在是可选的 [本地运营器](OPERATOR.md),通过显式私有配置与逐命令 `--execute` 单独调用。受管理扩展保持只读。固定的目标 allowlist、dry-run receipt、快照、完整性检查与隔离回归测试伴随这次升格。宿主凭据、产物固定、服务管理器文件与私有证据仍归运营方;不发布任何本地原型路径。
