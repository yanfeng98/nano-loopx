# 复杂项目只读适配器


有些项目过于庞大,单个 goal tick 无法安全理解。它们可能有大量文档、TODO 系统、
报告、测试、外部同步界面与活跃分支。对这类项目,第一个 LoopX 适配器不应编辑
文件,而应构建只读图谱。

适配器的职责是回答:

- 当前 goal 是什么?
- 哪些文件或系统是权威?
- 哪些工作集群处于活动状态?
- 哪些验证面可以证明进展?
- 哪些对等任务范围可以安全并行运行?
- 哪个开放的 peer 应该 claim 或协调下一个任务包?

## 只读图谱的结构

只读适配器图谱应包含:

```json
{
  "goal_id": "complex-project-main-control",
  "classification": "read_only_map_ready",
  "recommended_action": "ask the operator to opt in before mutations",
  "authority_sources": [],
  "work_clusters": [],
  "validation_surfaces": [],
  "peer_task_scopes": [],
  "boundary_findings": [],
  "handoff_packet": {}
}
```

图谱是证据,不是命令。claim、gate 与操作员决策仍然决定接下来发生什么。

## 权威来源

列出定义项目真相的文件或系统。例如:

- 项目 TODO 或 issue 看板,
- 文档注册表,
- 设计文档,
- 当前 git 状态,
- 最近的运行报告,
- 测试或 CI 入口,
- 受管的外部文档清单(manifest)。

对文档密集型项目,优先使用显式权威注册表,而不是扁平的文档列表。注册表应指明
默认入口文档、主题权威、文档状态、冲突规则与更新规则。只读图谱在提出子 agent
工作之前应报告权威覆盖情况:

```json
{
  "authority_registry": {
    "path": "docs/meta/DOC_REGISTRY.yaml",
    "read_status": "read",
    "default_entry_count": 3,
    "default_entries_checked": 3,
    "default_entries_present": 3,
    "topic_authority_count": 24,
    "project_material_count": 6,
    "project_material_repository_count": 2,
    "project_material_owner_review_required_count": 1,
    "project_material_stale_count": 1,
    "project_material_current_authority_count": 1,
    "deprecated_source_count": 2,
    "conflict_risk": "low"
  }
}
```

这可以防止复杂项目被 agent 碰巧先读到的某个旧设计文档或诊断报告所驱动。
对多材料迁移工作,公开紧凑图谱应暴露材料角色、仓库链接、owner 评审缺口、过时
来源与当前权威的计数。把确切 URL、仓库根、产品配置与原始评审文本保留在项目
本地注册表或适配器载荷中。

每个来源应包含:

- `path` 或稳定标识符,
- `source_type`,
- `read_status`,
- `why_it_matters`,
- `privacy_level`:`public`、`project-local` 或 `private`。

## 工作集群

按完成工作所需的证据类型对活动工作进行分组:

- 文档或设计清理,
- benchmark 或 eval 工作,
- runtime 或适配器工作,
- 外部文档同步,
- PR 或 CI 工作,
- 治理或公开/私有边界工作。

当前优先的来源应写为当前判断,而不仅仅是按时间顺序的任务清单。最有用的形态是:
现在相信什么、为什么、什么会改变这一判断、下一个有界动作是什么。

每个集群应包含:

- 当前状态,
- 可能的 owner,
- 阻塞条件,
- 安全的下一步探测,
- 子 agent 是否可以独立检查它。

## 验证面

复杂项目很少只有一个通过/失败指标。有用的适配器会明确列举验证面:

| 工作类型 | 验证面 |
| --- | --- |
| 文档 | markdown 结构、链接、注册表条目、评审记录 |
| 外部同步 | 清单(manifest)、远程获取、评论/高亮保留 |
| Benchmark/eval | 运行 artifact、指标文件、trace、hidden/eval 划分 |
| 代码 | 单元测试、类型检查、集成 smoke 测试 |
| PR/CI | 分支状态、CI 检查、评审评论 |
| 公开发布 | 敏感信息扫描、README 快速开始、示例 |

## 子 Agent 范围

只读适配器应建议子范围,而不是自行启动:

```json
[
  {
    "id": "docs-map",
    "role": "explorer",
    "work_scope": ["docs/**", "README.md"],
    "write_allowed": false,
    "expected_output": "task clusters and authoritative docs"
  },
  {
    "id": "validation-map",
    "role": "validator",
    "work_scope": ["tests/**", "scripts/**", ".github/**"],
    "write_allowed": false,
    "expected_output": "available validation commands and coverage gaps"
  },
  {
    "id": "boundary-map",
    "role": "explorer",
    "work_scope": ["docs/**", "examples/**", "scripts/**"],
    "write_allowed": false,
    "expected_output": "public/private boundary risks"
  }
]
```

控制器可以在启动 agent 之前接受、编辑或拒绝这些范围。

## 交接包

交给合格 peer 或操作员的最终输出应简短:

- 当前分类,
- 一条建议动作,
- 活动工作集群,
- 建议的对等任务范围,
- 验证面,
- 硬保护,
- 检查过的文件,
- 残余风险。

不要把原始私有证据放进打算交给另一个线程或公开 artifact 的交接包。

## 升级路径

使用分阶段的适配器状态:

1. `planned`:goal 已在注册表中,尚未运行。
2. `read-only-map-ready`:适配器可以生成当前图谱。
3. `connected-read-only`:操作员已同意只读运行。
4. `selective-assist`:控制器可以请 LoopX 在显式写入范围内做有界编辑。

在 `planned` 阶段,`loopx read-only-map --dry-run` 允许以控制器 opt-in 预览方式
运行。它只读取注册表元数据、活动状态章节与有界文件清单,返回
`opt_in_required=true`,并且不追加任何运行。不带 `--dry-run` 运行仍然需要
`read-only-map-ready`、`connected-read-only` 或 `connected`。

预览还会返回 `residual_risks`,使用诸如
`planned_adapter_requires_controller_opt_in` 与
`project_local_goal_state_not_detected` 等稳定标签,以便目标控制器用同一套共享
风险词汇评审。对含多个 goal 的仓库,预览检查所选 goal 自己的
`.codex/goals/<goal-id>/` 目录。如果本地尚未接好侧旁路(side bypass),风险清单
就会包含 `project_goal_state_dir_not_detected:<goal-id>`,即使同一仓库中的主控制
goal 已经健康。

直接跳到编辑会带来本可避免的协调风险。
