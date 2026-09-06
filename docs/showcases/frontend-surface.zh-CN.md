# 案例展示前端界面

> [English](frontend-surface.md)

这篇说明定义了第一个可以消费 `docs/showcases/showcase-catalog.json` 的公开案例展示界面。它是产品说明界面,不是本地操作者仪表盘。

目标是在一个屏幕内帮助新用户理解 LoopX:

- Codex、Claude Code、Cursor 及类似工具执行 agent Loop。
- LoopX 让长程 goal 控制面在这些 Loop 之间保持可见:关卡、todos、所有权、安全兜底、运行历史、quota 与证据。
- 只有展示可复用控制面行为的案例才有用,而不只是"agent 做了工作"。

## 真相来源

前端应读取 `showcase-catalog.json`,而不是抓取 Markdown。案例页提供叙事语境;目录提供可渲染数据。

直接使用这些目录字段:

| 字段 | 前端用途 |
| --- | --- |
| `id`、`date`、`title` | 稳定的卡片标识与排序键。 |
| `status` | 徽标与渲染状态。 |
| `case_page` | 链接到叙事来源。 |
| `interactive_page` | 可选静态 HTML 案例工件;存在时使用托管 Pages 链接。 |
| `demo_command` | 可用时的"试试 demo"命令。 |
| `storyboard_path` | 无可运行 demo 时,链接到前端就绪的 storyboard。 |
| `feedback_contract_path` | 案例包含用户引导时,链接到反馈/来源状态规则。 |
| `domain`、`audience`、`pattern_tags` | 过滤与分组。 |
| `headline` | 主卡片文案。 |
| `problem` | LoopX 帮助之前的情形。 |
| `loopx_behavior` | 时间线或行为列表。 |
| `user_value` | 用白话表达的结果。 |
| `evidence_boundary` | 脱敏与声明边界抽屉。 |
| `frontend_card.visual_metaphor` | 建议的视觉处理方式。 |
| `frontend_card.primary_metric_hint` | 面向负责人/用户的轻量价值信号,而非实现琐事。 |
| `frontend_card.badges` | 紧凑芯片。 |
| `frontend_card.story_beats` | 用于案例详情证据序列的向后兼容字段。新文案应把它渲染成证据,而不是作者注记。 |
| `evidence_metrics` | 可选紧凑价值指标。使用结果或边界信号,例如可审查 commit、避免的用户等待、被阻止的关卡化动作、压缩区间或公开证据窗口。不要把原始文件数、smoke 数、面板数或其他实现界面琐事当作主要证明。 |
| `workload_signal.efficiency_model` | 可选证据面板,用于保守基线-实际效率建模。 |

## 首屏

首屏应解答反复出现的困惑:"这是在取代 Codex goal mode 吗?"

使用紧凑对比块:

| 界面 | 角色 |
| --- | --- |
| Codex goal / 自动化 / CLI Loop | 在 agent session 或调度的 Turn 内执行有界工作。 |
| LoopX | 跨 Turns、工具、agents、关卡、证据与 quota 保存 lifetime-goal 控制面。 |

面向中文优先素材的推荐标题栈:

```text
Always-on agent teams, governed by human judgment
Gate-aware human-in-the-loop control plane
让多个 agent 昼夜接力,把人的判断留在控制面。
```

推荐的英文说明:

```text
LoopX keeps goals, gates, todos, claims, scopes, safe fallback, run
history, quota, and evidence in one shared state layer: the gated route waits
clearly, while independent safe side work can keep moving with evidence.
```

## 案例卡片模型

每个案例卡片应展示:

- 标题;
- 状态徽标;
- 一行头条;
- 模式标签;
- 用户价值;
- 证据边界徽标;
- 仅当 `demo_command` 存在时展示 demo 命令。

当案例包含 `workload_signal.efficiency_model` 时,把它渲染为独立证据面板,而不是埋在散文里。面板应展示:

- 公共 Git 工作量,例如 commit 数;
- 实际公开证据窗口;
- 保守 AI 编码辅助基线区间;
- 单工程师与小型团队的压缩区间;
- 声明边界,尤其是该估算是否方向性、按成熟度调整、且仅基于公共 Git。

不要把它当作通用基准。它是案例特定的证据模型,帮助读者理解自我迭代案例不只是"一个 agent 写了文件"。

打磨后的 mock 还应暴露轻量目录控件:

- 由目录 `status` 值生成的分段状态过滤器;
- 一个覆盖标题、头条、领域、受众、标签、行为、用户价值与证据边界的搜索输入;
- 可见的结果计数,让界面感觉像产品视图,而不是静态 README 摘录。

不要渲染原始运行日志、截图、私有聊天摘录、任务 id 或内部文档链接。公开案例卡片应感觉像可复用产品模式,而不是一段转录。

## 详情故事模型

案例详情视图应是紧凑的证据序列:

1. **触发**:什么让长程 goal 难以管理。
2. **可见状态**:哪些 LoopX 对象让情形变得明确。
3. **Agent 动作**:哪个有界动作保持安全。
4. **人类角色**:用户做了什么、或不需要决定什么。
5. **证据**:哪些公开安全验证支撑该案例。

对于 `redacted_stub_pending_contributor_details`,坦率地展示缺失的证据。不要用推测性声明填补缺口。
对于 `public_safe_interactive_case`,优先把 `interactive_page` 工件当作前场 CTA,同时保留 `case_page` 作为配套叙事与证据边界说明。

## 状态渲染

| 状态 | 徽标 | 行为 |
| --- | --- | --- |
| `reproducible_synthetic_demo` | 可复现 | 展示 demo 命令并链接到合成 fixture。 |
| `public_evidence_case` | 公开证据 | 展示有 Git/文档/smoke 支撑的证据摘要。 |
| `redacted_stub_pending_contributor_details` | 脱敏 stub | 展示模式与缺失的公开证据。 |
| `public_safe_case_spec` | 案例规格 | 存在时展示叙事、storyboard 与反馈契约链接。 |
| `public_safe_interactive_case` | 交互式案例 | 链接托管 HTML 工件,并保持证据边界可见。 |

新状态应先加入目录 smoke,再出现在网站上。

## 公共边界

案例展示前端可以包含:

- 脱敏的领域标签;
- 可复用的控制面模式;
- 合成 demo;
- 紧凑的公共 Git 证据;
- 明确的证据边界。

它不得包含:

- 内部工具的原始截图;
- 私有文档、wiki 或聊天链接;
- 原始基准任务文本、轨迹、日志、verifier 尾部或任务 id;
- 凭据、认证材料或本地文件系统路径;
- 未公开的项目工件或用户特定的 active state。

## 首个实现切片

首个实现应是静态的、目录驱动的:

1. 加载 `showcase-catalog.json`。
2. 验证已知的 `schema_version`。
3. 从目录字段渲染对比块、过滤/搜索控件、案例网格与详情故事。
4. 链接回 Markdown 案例页,或在 `interactive_page` 存在时链接到托管静态 HTML。
5. 把 `docs/assets/control-plane-board.svg` 用作第一个共享视觉资产。
6. 在真实前端应用存在之前,把 `examples/showcase-frontstage-prototype.py` 用作无构建静态原型。
7. 运行 `python3 examples/showcase-catalog-smoke.py`、`python3 examples/showcase-frontstage-prototype-smoke.py` 与 `loopx check --scan-path docs/showcases --scan-path docs/assets`。

这让营销界面保持诚实:如果案例不在目录中,它就不会出现在公共案例展示前端上。
