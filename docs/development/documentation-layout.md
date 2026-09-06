# 文档布局与迁移策略

> [English](documentation-layout.md)

LoopX 文档服务多类读者：试用产品的人、运行长程 goal 的操作者、修改控制面的贡献者，
以及检查协议或研究证据的 maintainer。本策略在把这些路径区分开来的同时，不隐藏有用材料，
也不为美观原因破坏稳定链接。

## 目标信息架构

| 路径 | 拥有 | 不拥有 |
| --- | --- | --- |
| `docs/guides/` | 任务导向的接入与操作者 walkthrough | 产品策略或机器合同 |
| `docs/concepts/` | 持久 LoopX 概念与心智模型的解释 | 分步操作 |
| `docs/operations/` | goal、todo、cadence、attention 与 authority 工作流 | provider 专属实现细节 |
| `docs/architecture/` | 系统边界、设计决策与 RFC | 当前 CLI 参考 |
| `docs/product/` | 产品方向、runtime 体验、表面与使用案例 | 协议定义 |
| `docs/integrations/` | runtime、host、协作与外部系统 adapter | 核心控制面语义 |
| `docs/reference/contracts/` | 稳定的人类可读合同 | 探索性提案 |
| `docs/reference/protocols/` | 版本化、面向实现的协议 | 叙事式产品方向 |
| `docs/development/` | 贡献者工作流、测试与仓库策略 | 终端用户接入 |
| `docs/showcases/` | 公开安全案例与可复现演示 | 原始私有证据 |
| `docs/research/` | 公开研究、benchmark 证据与 route packet | 稳定的第一线文档 |
| `docs/archive/` | 为历史价值保留的过时或陈旧记录 | 现行指南 |

`docs/` 根是兼容表面，不是新文件的默认去向。它应当承载文档首页和少量稳定、
高流量的锚点。新材料归入最窄的拥有目录。

## 覆盖地图

仓库目前在每个目标类别都有可用材料，但三个区域过载：

| 当前表面 | 当前问题 | 迁移处置 |
| --- | --- | --- |
| `docs/README.md` | 在一个长列表中混排接入、参考、产品方向、研究与治理 | 替换为简短的读者与任务路由；通过类目索引保留链接 |
| `docs/*.md` | 概念、合同、集成、操作与 roadmap 共享一个扁平命名空间 | 只保留已验证的稳定锚点；把低流量文件按属主迁移并修复入站链接 |
| `docs/product/*.md` | runtime 实验、产品基础、表面与使用案例相互穿插 | 归组到 `foundations/`、`runtimes/`、`surfaces/` 与 `use-cases/` |
| `docs/reference/protocols/*.md` | 版本化合同扁平且难以扫读 | 先按领域归组索引；迁移文件必须单独做协议路径兼容性评审 |
| `benchmark/` | 当前 benchmark 研究需要产品包之外的小型 RFC 关联家园 | 协议与公开安全实践留在此处；把过时 runner 归档到 `deprecate/benchmark-legacy/` |

这是一次保持覆盖的迁移。独特声明、公开证据与可用链接必须要么留在当前路径，
要么出现在新的 canonical 索引中。更短的落地页不是删除材料的许可。

## 稳定根锚点

第一步迁移保持这些高流量路径稳定：

- `docs/architecture.md`
- `docs/integration.md`
- `docs/state-interaction-model.md`
- `docs/status-data-contract.md`
- `docs/quota-allocation.md`
- `docs/heartbeat-automation-prompt.md`
- `docs/project-agent-todo-contract.md`
- `docs/public-private-boundary.md`

只有存在调用方已迁移的实证，或存在真实兼容机制时，才可重新考虑它们的位置。
GitHub 不提供透明的 Markdown 重定向，所以“更漂亮的目录树”不足以成为打破广链路径的理由。

## 迁移规则

1. **按属主迁移，而不是按文件名相似度。** 文档归属的未来变更评审地，而不是标题
   恰好配得上的地方。
2. **保留独特信息。** 为每个索引建立迁移前后覆盖图，让每一条仍然有效的声明与公开
   链接都可达。
3. **修复每个仓库调用方。** 在同一个变更中更新 Markdown 链接、示例、smoke、源码注释
   与生成的导航。
4. **显式对待外部兼容性。** 当一条路径属于公开接入、release note、协议文档或常见
   贡献者链接时，保持它稳定。不要为了让目录看起来空而留下几十个占位文件。
5. **索引保持精选。** 类目索引说明什么属于该处，并突出 canonical 入口。它不必重复
   每个历史文件名。
6. **把当前真相与证据分离。** 稳定指南链到证据；research packet 不会成为第一线
   操作指令。
7. **私有材料 fail closed。** 内部对话、个人署名、私有 URL、本地路径、凭据、原始
   转写与权限诊断不得进入公开文档。
8. **验证渲染后的路径。** 交付前检查相对链接、锚点、Mermaid 与变更落地页的首个
   可见章节。

## 分阶段迁移

### 阶段 1：导航与明显属主

- 为 architecture、concepts、operations、integrations 与 product 子域添加简短索引；
- 在 `docs/architecture/rfcs/` 下发布公开安全 RFC；
- 迁移属主明确、低流量的根文件；
- 按 foundation、runtime、surface 与 use case 归组产品文档；
- 保留稳定根锚点；
- 添加聚焦的相对链接校验。

### 阶段 2：协议发现

- 把协议索引按控制面、runtime 集成、领域能力、证据与发布/质量归组；
- 迁移任何版本化协议前，盘点代码与外部引用；
- 保持协议文件名与版本后缀稳定。

### 阶段 3：研究生命周期

- 为活动发现、可复用证据、带日期 packet 与归档决策提供主题索引；
- 保持带来源的 artifact 可检查；
- 归档过时 packet 但不重写历史。

## 放置清单

新增公开文档前，回答：

1. 谁期望在阅读后采取行动？
2. 它是指南、概念、产品决策、协议、证据，还是历史记录？
3. 哪个已有索引用作该读者与变更理由的属主？
4. 文档是否只包含公开安全的来源与示例？
5. 什么聚焦验证能证明链接与呈现仍然可用？

如果没有类目拥有该文档，在创建又一个顶层文件前先明确其目的。
