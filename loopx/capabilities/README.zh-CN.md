# LoopX 产品能力

> [English](README.md)

LoopX capability 是一个稳定、provider-neutral 的契约,用于从 LoopX state
产出一个有界、可验证的调用方 outcome。它拥有领域 policy,归一化 provider
观测,验证结果,并向 Kernel 提出一个 typed transition。

每个内置 capability 都在本目录下的一个包中拥有自己的 canonical README、注册
元数据与实现。文档站点是这些包自有 Markdown 文件的构建期投影,不是第二份手工
维护的副本。目录仅仅存在并不会成为已发布 capability:注册元数据、真实入口点和
持久化的验证缺一不可。

这使它区别于周边边界:

- [Kernel](../../docs/architecture.md#runtime-responsibility-model) 拥有持久化的
  goal、todo、gate、quota、recovery 与 scheduling 事实;
- provider 执行一个有界的外部或本地操作,并返回 readback;
- [extension](../../docs/reference/extensions.md) 打包并运行一个可选 provider,
  不获取 Kernel authority;
- `shell`、`network` 等 host 声明描述的是运行时能力,不是产品 capability 或
  权限授予。

## 检查本版本能做什么

运行时 registry 才是权威。目录和文档仅仅存在并不会成为已发布 capability:

```bash
loopx capability list --format json
loopx capability show issue-fix --format json
```

`list` 报告已注册 capability 与 provider 就绪度。`show` 补充用户价值、成熟度、
入口命令、显式写边界、已实现协议与持久化验证。在启用高级路径或可选 provider
之前,请先使用这份 readback。

## 按 outcome 选择

下面选出的文档解释了已注册 capability 背后的人类使用路径。完整目录以及已安装
版本的确切可用性与成熟度,仍以 CLI 为准。

### 工程交付

| 你需要… | Capability 路径 |
| --- | --- |
| 通过 fail-closed 的证据生命周期,准备并校验本地不上传的 benchmark 实验 | [Benchmark Toolkit](benchmark_toolkit/README.md) |
| 把公开 issue 与 PR 信号转成带验证证据的聚焦、可审阅修复 | [issue-fix](issue_fix/README.md) capability([中文](issue_fix/README.zh-CN.md)) |
| 通过有界 review、安全修复与严格收据,校验确切的最终 diff | [Change Quality](change_quality/README.md) |
| 对照精确 head 证据与 typed 完成规则,审阅不断变化的公开 PR 队列 | [Pull Request Review](pr_review_queue/README.md) |
| 检测 source-head 漂移,并安全重建本地已审阅分支栈 | [Integration Branch](integration_branch/README.md) |
| 用 typed 计划为本地仓库变更把关,并在重启后保留被阻塞的未合并工作 | [Repository Change Window](repository_change_window/README.md) |

### 研究与决策连续性

| 你需要… | Capability 路径 |
| --- | --- |
| 在长程探索中保留问题、假设、实验、发现与组合前沿 | [Explore](explore/README.md)([中文版](explore/README.zh-CN.md)) |
| 在做出决策前区分当前证据、advisory 提案与已验证 outcome | [Decision Context](decision_context/README.md)([中文](decision_context/README.zh-CN.md)) |
| 在没有新的用户 prompt 时召回一个已收尾的自主 turn | [Agent Turn Recall](agent_turn_recall/README.md) |
| 增加可选、provider-neutral 的偏好召回,但不让 memory 成为状态权威 | [Semantic Preference](semantic_preference/README.md) |
| 保存 typed 反馈记忆,并评估有界召回/应用试点 | [Reward Memory](reward_memory/README.md)([中文](reward_memory/README.zh-CN.md)) |

### 运维与投影

| 你需要… | Capability 路径 |
| --- | --- |
| 把 release 自有的 skill 投递到选定的项目本地 host surface | [Project Skill Delivery](project_skill_delivery/README.md) |
| 用 source、archive、delivery 与 settlement 收据组合定时或进度触发的报告 | [Periodic Report](periodic_report/README.md) |
| 把公开/私有内容信号转成可审阅的 source、角度、草稿、反馈与发布 gate 包 | [Content Operations](content_ops/README.md) |
| 盘点、归档、迁移并重排 material store,而不丢失 raw source 权威 | [Material Lifecycle](material_lifecycle/README.md)([中文](material_lifecycle/README.zh-CN.md)) |
| 在调用方迁移到 outcome 自有能力期间,检查公开安全的外部价值采集兼容路径 | [Value Connectors](value_connectors/README.md) |
| 单向观察长程 harness 会话,读回完整性 receipt 与 stall/repetition/recovery 投影,且不授予运行时 authority | [Reliability Diagnostics](reliability_diagnostics/README.md)([中文](reliability_diagnostics/README.zh-CN.md)) |

## 贡献者导航与 ownership

每个已注册的内置 capability 包都包含一个 `catalog_entry.py`。该记录声明其稳定
id、命令、provider 边界、canonical 文档来源、发布路由、已实现协议与持久化验证。
根目录 [`catalog.py`](catalog.py) 只是组合包自有的条目;它不维护第二份
capability 到文档的映射。

请使用已安装版本的运行时 readback:

```bash
loopx capability list --format json
loopx capability show <capability-id> --format json
```

`show` 从用于构建文档站点的同一注册记录中报告 `canonical_doc`、
`documentation_route`、命令、写边界、协议、smokes 与 provider 就绪度。

共享 context-provider helper 等支撑包可以位于此 namespace 下而没有
`catalog_entry.py`;它们是内部模块,不是产品 capability。可选 provider 与
extension 投递的 capability 在所属 extension 包旁保留其文档,并使用同样的构建
投影,不获取 Kernel authority。

## 从 Capability 到 Provider

执行路径与控制路径刻意反向运行:

```text
Agent -> Capability -> Provider -> external system
Provider readback -> Capability transition proposal -> Kernel
```

从调用方 outcome 出发,而不是从 extension 名出发。内置 provider 可能已经实现了
该 capability。当需要可选实现时,检查其声明的权限与就绪度,然后使用
[Extensions and Capabilities](../../docs/reference/extensions.md) 中记录的显式
install、doctor、enable、disable、upgrade 与 rollback 生命周期。安装 extension
不会授予新的 authority。

## 架构规则:领域通道,而不是 Kernel 列

运维者界面可以把 LoopX 渲染成 agent 原生的 Kanban。Kernel 提供 claim、gate、
monitor、complete、supersede、quota、writeback 等通用生命周期算子。Capability
可以添加一个解释 provider 观测的领域通道,但不得创建并行的 todo 或 scheduling
authority。

例如,Issue Fix 可以投影 `feasibility -> patch -> checks -> review -> merge`,
而实验路径可以投影 `hypothesis -> execute -> evaluate -> promote/retire`。
这些标签来自 capability 自有的领域 state 与已接受的 Kernel transitions;它们
不是新的核心生命周期状态。如果某个领域 stage 会改变 permission、claim
资格、quota、用户 gate 或 terminal closure,capability 必须通过现有 Kernel
contract 提出 typed transition。

保持 Kernel 控制面代码通用。把场景特定的契约、实现模块、CLI 入口点、包文档与
smokes 放在它们服务的 capability 之下。跨 capability 的架构、Kernel 与
extension 契约,以及通用指南,仍留在 `docs/` 下。在存在包自有的 catalog entry、
canonical README、真实入口点与持久化 smoke 之前,不要注册新 capability。
未来想法在具备可执行证据之前,属于产品规划文档。
