---
name: loopx-material
description: Operate an explicitly activated LoopX Material Lifecycle for a connected project. Use for material-store inventory, lossless migration, candidate/archive transitions, exact-read-backed ranking, ranked-entry rebuilds, bounded Explore intake, owner-gated apply, rollback, and audit. Do not use for ordinary one-off reading or research when the project has not activated Material Lifecycle.
---

# LoopX Material


对项目持久材料库的生命周期与权限使用本技能。源发现、领域特定评分与笔记撰写
可由项目技能提供；本技能拥有通用无损生命周期。

LoopX 提供本技能的规范源，但不把它安装到用户的全局 skill 目录。只在显式启用
Material Lifecycle 的已连接项目中安装受管副本：

```bash
loopx project-skill install \
  --project . \
  --skill loopx-material \
  --surface codex \
  --execute
```

对 Codex 之外的宿主使用 `--surface claude-code`；
重复该标志可在一个事务中安装多个宿主原生副本。受管副本位于
`.agents/skills/` 或 `.claude/skills/`，并通过同一 CLI
升级或移除。项目本地发现本身不激活 material-store 写入；所选 goal 仍需要
显式 Material Lifecycle 权限。

## 激活关卡

在变更 material store 之前：

1. 通过 `loopx start-goal --guided`、`loopx status` 或 `loopx diagnose`
   解析当前项目、`goal_id`、已注册 agent 与活跃 todo。
2. 运行 `loopx project-skill status --project . --skill loopx-material`，
   确认必需宿主界面是最新的。
3. 确认所选 todo 显式指向 `material_lifecycle`，或 goal 权限声明了活跃
   Material Lifecycle 配置及其源库。目录条目或项目本地 skill 不是激活。
4. 确认 goal 边界覆盖精确的私有适配器与权限路径。公开 LoopX 契约绝不授予
   对私有源内容的访问。
5. 运行 `loopx material-lifecycle architecture --format json`，保留其
   default-off、owner-gated、provider-neutral 边界。

如果项目本地 skill 缺失，预览显式项目安装；不要回退到全局副本。如果激活或
权限缺失，在源码变更前停止。创建一个有界 setup todo 或 owner gate；不要虚构
一个库，也不要把聊天历史当作权限。

## 所有权边界

保持这些职责分离：

- **项目源适配器**：定位并读取项目的私有源文件、数据库、文档或 provider。
- **研究/读者 skill**：召回候选、执行精确读取，并产生源质量与领域价值证据。
- **Decision Context**：提供修订绑定的目标、变更事实、冲突与被接受的决策。
- **Material Lifecycle**：拥有库存、迁移、生命周期迁移、ranked-entry 重建、
  rerank 提议、apply receipts 与回滚。
- **内容或笔记工作流**：消费所选材料并产生产物；它不自行重写
  candidate/archive/ranking 真相。

## 工作流

### 1. 快照与库存

在提议结构性变更前读取源权威。

- 记录源修订、字节/内容摘要、生命周期计数、解析错误、稳定材料引用与经核验的
  备份。
- 把原始内容、私有路径、URL、provider 负载与凭据排除在公开包与提交之外。
- 在核验的 cutover 与回滚演练都成功前保留原始源。

任何迁移、重建或 rerank 都不得从未核验的部分解析开始。

### 2. 规范化生命周期

在以下范围内使用稳定材料引用：

```text
candidate -> active -> archived
                 \-> carryover
archived -> active
```

每个迁移需要带修订的证据或决策引用。归档必须保留原始源引用与归档引用。
读取、总结或发布笔记不会隐式归档材料。

### 3. 提升精确读取证据

召回仅是建议。在材料影响排名或生命周期前：

1. 通过配置的 provider 或本地搜索取回候选；
2. 精确读取权威源；
3. 记录源修订与读取范围；
4. 拒绝陈旧、冲突、不可读或仅次要来源的声明；
5. 只把提升后的证据传入 Decision Context 或排名。

不要因当前列表感觉不完整就启动 Explore。Explore 只从具名证据缺口、有界查询
计划、预算与停止条件开始。

### 4. 落定候选排名

在报告候选接收完成前，对照当前 Decision Context 落定其排名：

- 恰好记录一个处置：`top_window`、`ranked_backlog` 或 `no_change`；
- 让项目适配器从精确读取证据、当前目标、重叠与产物可转化性分类价值，
  而非仅凭层级；
- 要求高价值材料在 Top-N 或显式 ranked backlog 中获得核验成员资格；
- 要求 `no_change` 有理由，且仅用于标准价值或实质上重复的材料；
- 保持候选接收与排名为独立 receipts，且排名变化时保持独立权限修订；然后用
  intake-ranking 结算 receipt 连接它们；
- 在 ranked backlog 中保留被挤出的 Top-N 条目，并保留受保护锚点，
  除非变更的 Decision Context 或显式所有者权限移动它们。

如果排名 apply、回读、投影或回滚就绪失败，在将接收报告为完成前修复或回滚。

### 5. 重建 ranked entries

ranked entry 必须表示一个独立可排序的读取或动作单元，而不是展示桶。

- 默认每个 ranked entry 最多三个主材料。
- 当条目超限时，创建确定性子条目并独立排名。
- 不要将溢出藏在未排名的支撑索引中。
- 保留精确成员资格：每个所选材料在 ranking 集合中恰好出现一次。
- 保留稳定材料引用与规范源记录。
- 在可见 Top-N 之外保持显式 ranked backlog。

拆分是语义性的，不是机械性的。仅当材料共同支持一个决策或学习结果时才对它们
分组；对价值、紧迫性、读者动作或证据成熟度不同的材料分开。

### 6. 提议有界 rerank

从修订绑定 Decision Context 证据 rerank。

- 保护固定条目与项目声明的稳定前缀。
- 除非所有者明确批准结构重建，否则限制移动条目与排名位移。
- 区分排名移动、生命周期变化与新候选接收。
- 当证据不支持移动时发出无变化提议。
- 保持提议与 apply receipt 分离。

### 7. 构建可读投影

受管目录仍是权威，但操作员需要可读视图。从精确读取支撑的展示记录构建该视图：

- 保留连续排名与显式 ranked backlog；
- 每个条目最多三个主材料；
- 要求每个预期所选材料恰好出现一次；
- 把项目特定分类、摘要、判断、链接与语言保留在私有项目适配器中；
- 发出带修订、计数、摘要与验证的无内容 receipt；
- 绝不把可读 Markdown 视为排名或源权威。

LoopX 拥有验证、渲染与无内容 receipt 契约。项目适配器拥有源解析并提供
已提升的展示记录。一次性遗留解析与迁移脚本仍为项目本地。

### 8. 以无损关卡应用

先预览。仅当全部为真时才应用：

- 源与备份摘要仍与库存匹配；
- 解析错误为零或显式经所有者批准；
- 预期源/规范计数匹配；
- 排名覆盖与唯一成员资格精确；
- 受保护条目仍有效；
- compare-and-swap 修订匹配；
- 回滚已演练；
- 所有者关卡授权此精确计划。

应用后，回读目标并写入审计过的 receipt。任何不匹配时，恢复先前权威并记录
blocker。绝不只凭准备计划报告"迁移完成"。

## 项目适配器契约

项目特定 skill 或 `AGENTS.md` 可以定义：

- 源位置与私有 provider 设置；
- 主题分类与领域评分；
- 读取工具与源特定回退；
- 用户特定优先级；
- 笔记/归档目的地与公共/私有脱敏；
- 具体备份与恢复命令。

它应引用本技能，而非重复通用迁移、排名、重建、apply 或回滚规则。项目规则
可以收紧这些不变量，但不得削弱它们。

## 完成证据

完整的材料操作报告：

- 源与目标修订；
- 备份与源摘要核验；
- 解析与规范计数；
- 生命周期计数增量；
- 接收排名处置与价值分类；
- ranked-entry 计数与最大主成员数；
- 精确覆盖与重复计数；
- 提升/拒绝的精确读取证据；
- 提议与 apply receipt 引用；
- intake-ranking 结算 receipt 引用；
- 回滚结果；
- 下一个有界动作或显式无变化。

## 停止条件

在以下情况下不改变源而停止：

- 项目或 goal 不明确；
- 所选 goal 未显式激活 Material Lifecycle；
- 源权威、备份、修订或稳定 id 无法核验；
- 精确读取证据与提议的变更冲突；
- 溢出会被隐藏而非独立排名；
- 迁移会丢失字节、记录、引用或可恢复性；
- 必需的所有者关卡、写入范围或回滚路径缺失；
- 公开输出会暴露私有材料或凭据。
