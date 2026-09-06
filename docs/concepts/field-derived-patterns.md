# 字段衍生的项目控制模式

> [English](field-derived-patterns.md)

LoopX 应该从反复出现的真实协作模式中成长，而不是只从抽象的功能点子出发。
本文记录已在文档密集型 Agent 基础设施工作、长窗口实验控制和多项目 Codex
协作中被证明有用的 public-safe 机制。

下面的示例刻意做了脱敏。项目特定的任务 id、私有路径、内部文档链接、生产日志和指标值，
应放在项目本地的 payload 里，而不是 LoopX 公共仓库。

## 1. 权威注册表

复杂的项目在需要更多自动化之前，先需要一层权威。当一个仓库有大量设计文档、
TODO 文件、本地镜像、实验报告和归档笔记时，第一个失败模式不是 Agent 读得不够多；
而是 Agent 把错误的来源当作当前真相。

一个有用的权威注册表会指明：

- 新 controller tick 的默认入口文档；
- 主题归属：哪个文件是当前优先级、系统设计、验证、外部同步或历史证据的权威；
- 项目材料与仓库链接：哪些外部文档、仓库根、dashboard、issue tracker 或评审面与目标相关；
- 来源角色与新鲜度：某个来源是当前权威、辅助参考、历史笔记、本地镜像，还是 owner 门控的证据来源；
- 文档状态：active、draft、diagnostic、external mirror、superseded、deprecated、archived；
- 冲突规则：当 TODO、设计文档、镜像和旧 run 报告说法不一致时，谁赢；
- 更新规则：什么时候改一个 canonical 文档也要求更新注册表。

LoopX 应把这当作一等公民的复杂项目机制：

```json
{
  "authority_registry": {
    "path": "docs/meta/DOC_REGISTRY.yaml",
    "default_entry_docs": [
      "docs/TODO.md",
      "docs/meta/DOC_REGISTRY.yaml",
      "docs/external_materials/MANIFEST.md"
    ],
    "topic_authority": {
      "current_priority": "docs/TODO.md",
      "runtime_architecture": "docs/SYSTEM_DESIGN.md",
      "external_sync": "docs/external_materials/MANIFEST.md"
    },
    "project_materials": {
      "migration_design": {
        "role": "current_authority",
        "source_kind": "external_doc",
        "freshness": "owner_review_required"
      },
      "target_repo": {
        "role": "implementation_surface",
        "source_kind": "repository",
        "freshness": "read_only_status_ok"
      }
    }
  }
}
```

对于 `read-only-map`，adapter 不应只是罗列文件。它应报告是否存在权威注册表、
检查了哪些默认入口、哪些主题有 canonical owner，以及是否有活跃来源与
deprecated 或 archived 来源冲突。

同样的模式也适用于非文档密集型 Agent 仓库。一个平台迁移或产品集成目标往往同时有
好几类材料：设计文档、owner 评审笔记、目标与来源仓库、迁移清单、dashboard 和验证记录。
LoopX 应把它们压缩成一个 public-safe 的材料注册表：暴露角色、新鲜度、缺失的 owner
证据和下一步行动，同时把私有 URL、仓库路径、产品配置和原始评审文本留在项目本地
payload 里。这让新项目 Agent 知道哪些来源是当前的，而不必把每个旧链接都灌进它
的上下文。

近期的公开试点应使用一个脱敏的复杂迁移 fixture。fixture 应建模关键的材料角色与
新鲜度状态，而不点名私有项目：当前设计权威、来源仓库、目标仓库、owner 评审面、
迁移清单、验证 dashboard 和已废弃的历史笔记。Status、dashboard 和 review packet
应只暴露角色、新鲜度、缺失的 owner 证据和下一步行动；私有 URL、repo 根、产品配置和
原始评审笔记留在项目本地 payload 里。

## 2. 当前信念 TODO

对于长跑项目，TODO 文件最有价值的时候，是它回答了三个问题：

- 我们当前相信什么？
- 我们为什么相信它？
- 下一个有界的行动是什么？

这不同于按时间顺序的任务堆。历史工作要保持，但一旦它不再驱动下一个决策，
就应压缩进归档、诊断报告或附录。

LoopX 应把这一模式吸收进活跃目标状态与 read-only-map 摘要：

- `current_judgment`：紧凑的信念；
- `evidence_boundary`：什么支持它、什么不支持；
- `next_action`：一个有界的下一步；
- `deferred_or_archived`：保留可追溯性但不应驱动当前工作的旧行。

这让状态刷新变得有用。纯状态更新不是一条日志；它是给下一个 agent tick 和
dashboard 的一层新的当前信念面。

## 3. 有界衍生状态继承

LoopX 可以从结构化来源衍生状态，例如 active-state Markdown、todo 元数据注释、
权威注册表、JSON run 记录和 AST/源码检查。衍生状态只有比它汇总的材料更小、
更可审计时才有用。

一个衍生状态面应声明：

- canonical source：能重建完整视图的结构化字段、文件或命令；
- 继承规则：哪些来源字段被复制、压缩或刻意丢弃；
- 条目上限：热路径用 top-N 计数，外加一条完整列表的冷路径；
- 归档/裁剪规则：旧的已完成或已被替代的状态何时必须离开活跃投影；
- 投影语义：status、quota、dashboard 或 review packet 是只能展示衍生视图，
  还是可以按它调度。

模型创建的状态不得成为第二个真相源。如果 Agent 汇总了 todo、benchmark 用例、
实验或权威来源，该汇总要么指回一个可解析的来源，要么通过一个会添加结构化元数据的
LoopX 命令写入。无界列表应藏在明细指针后面，而不是塞进 heartbeat payload 或首屏
status。

## 4. 托管外部来源清单

很多真实项目依赖外部文档、评审面或产品讨论产物。它们不应被当作普通链接对待。

一个托管的外部来源清单应追踪：

- 本地镜像路径；
- 稳定的来源标识符；
- 来源 revision 或抓取时间戳；
- 角色：策略文档、项目 wiki、验证文档、协作笔记等；
- 同步方向，以及远端是否更新；
- 必须保留的未解决评论、高亮或 reviewer 可见标记；
- fetch-before-write 规则。

LoopX 不应盲目地把外部材料拷进公共 status。公开的紧凑记录应说明存在一个托管
外部来源，以及它是否够新。私有 payload 可以保留更丰富的证据。

这一模式预防两个常见失败：

- 因为本地镜像看起来更干净，就覆盖了 reviewer 可见的远端信号；
- 让一份过期的本地笔记成为当前项目权威。

## 5. 验证面映射

复杂项目很少有单一的验证命令。进度可以由不同的面来证明：

| 工作类型 | 验证面 |
| --- | --- |
| Docs | markdown 结构、链接、权威注册表、评审笔记 |
| External sync | 清单新鲜度、限定抓取、评论/高亮保留 |
| Benchmark/eval | run artifact、指标文件、trace、配对基线、声明边界 |
| Code | 单元测试、类型检查、集成冒烟 |
| PR/CI | 分支状态、CI 检查、评审评论 |
| Public release | 敏感项扫描、README 快速上手、示例 |

LoopX 应要求每个复杂项目映射在提出实现工作之前就指明验证面。这样 dashboard 只有在
下一步行动有可信的验证路径时，才显示"ready for Codex"。

## 6. 实验看板

长窗口实验项目需要实验看板，而不只是一份 run log。看板应区分：

- 目标与主决策指标；
- 决策窗口与可比较的基线窗口；
- 护栏指标；
- 非目标与不安全捷径；
- 活跃任务与需要关注的内容；
- 已完成的锚点与路线历史；
- launch 或计算配额；
- 下一个 handoff 条件。

最重要的教训是：把目标身份锚定在决定性证据上。如果真实目标是长窗口指标，
一个 runtime 缓存风险、仅训练侧的波动或一次失败任务，都不应成为目标身份。

LoopX 应这样建模：

```json
{
  "experiment_board": {
    "path": ".codex/experiments/example-goal.md",
    "primary_metric": "primary decision metric",
    "decision_window": "aligned eval window",
    "guardrails": ["runtime stability", "secondary metrics"],
    "active_tasks_section": "Active Tasks",
    "route_history_section": "Config Notes And History"
  }
}
```

Adapter 在决定性证据可比较之前应显示 `waiting_on=external_evidence`。不应从
仅训练侧的护栏推断人类奖励或决策建议。

## 7. 关卡顺序

一些现场失败在 LoopX 以稳定顺序应用 gate 时会变得更简单：

1. 健康与公共/私有安全；
2. operator 关卡或项目 controller 的 opt-in；
3. 证据就绪；
4. 计算配额；
5. Codex 执行。

计算配额决定一个目标可以消耗多少自动 Agent 时间。它不授权写操作、生产动作或路线决策。
Operator 关卡和人类奖励仍是独立的持久事件。

## 8. Handoff Packet

一个好的 handoff packet 短到可以直接转发，又精确到避免重复摸索。它应包含：

- goal id 与当前分类；
- 一个推荐行动；
- 检查过的文件或面；
- 权威来源；
- 验证面；
- 硬护栏；
- 残余风险；
- 允许进入下一阶段的确切条件。

它不应包含原始私有证据。它也不应假装是用户批准。如果项目 Agent 需要许可才能跨过一个
gate，LoopX 应在该命令变成 Codex-ready 之前先记录一个 `operator_gate_*` run。

## 9. 并行工作声明

大型项目往往需要多个 Agent，但并行只有在声明明确时才管用：

- 已注册的 Agent 仍是平等的 peer；
- 声明与租约分配有界的只读探索、实现或验证工作；
- 写作用域应互不相交；
- 临时任务协调者可以接受 bundle 证据，但 merge、发布和生产的权威仍由仓库
  策略与 operator 关卡决定。

LoopX 应把提议的 peer 任务作用域记录在 read-only map 里，然后让合格 peer 声明它们，
或让 operator 编辑任务边界。

## 10. 需要阻止的反模式

LoopX 应主动阻止这些模式：

- 把聊天线程当作真相源；
- 只用自动化节奏表达项目优先级；
- 让偶然的 runtime 风险取代真实目标身份；
- 用仅训练侧或不可比较的证据当作路线赢家；
- 把日志追加进规划文档，而不是更新当前信念；
- 把私有链接、任务 id、工作区路径或原始日志拷进公共紧凑历史；
- 不检查远端评论或 reviewer 标记就覆盖托管外部来源；
- 不看目标的 P0/P1/P2 优先级栈，就让最后一个完成的切片选择下一个行动；
- 在记录使命令有效的 operator gate 之前，就把命令交给项目 Agent。

## 近期实现影响

这些现场模式意味着四个具体的 LoopX 面：

1. **权威/材料注册表支持**：`connect` 和 `read-only-map` 应接受或发现项目
   权威注册表，包括外部材料与仓库链接角色，然后发布紧凑的 public-safe 覆盖范围。
   第一个 fixture 应是脱敏的复杂迁移材料注册表，这样实现就有真实的、多材料
   控制问题的锚点，而不会泄漏项目细节。
2. **实验看板支持**：实验 adapter 应指明主指标、决策窗口、护栏、活跃任务
   区和路线历史区。
3. **验证面映射**：status 和 dashboard 应说明一个目标为何 ready、waiting 或
   blocked，用验证面而不是只给原始分类。
4. **Handoff packet 纪律**：每个跨线程 packet 都应短、public-safe 且有 gate；
   packet 是协作便利工具，不是持久批准。
5. **优先级栈下一个行动**：每个 controller tick 都应说明选中的下一个行动是
   P0、P1 还是 P2，以及它为何胜过相邻候选。
