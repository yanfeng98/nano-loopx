# Agent-Reach Ops 信源地图


状态：connector 支撑的内容运营的公开安全现场模式（field pattern）。

这篇说明把 Agent-Reach value-explorer 实验变成更广 connector 信源地图中的一个
可复用 LoopX 信源 profile。它不是对 Agent-Reach 的硬依赖，也不授予发布许可。
它描述 LoopX Agent 如何把 Agent-Reach 用作信源路由器，然后由 LoopX 拥有证据、
gates、草稿、监控与交接状态。

Agent 无需先读本文才能行动。可执行入口是：

```bash
loopx value-connectors source-map --connector agent_reach_ops_source_map --format json
```

要获取当前所有浮出表面的 connector profiles，使用：

```bash
loopx value-connectors source-map --format json
```

## 何时使用

当 LoopX Agent 需要以下能力时使用该模式：

- 为一条帖子、回复、发布说明或面向贡献者的更新寻找公开信号；
- 比较一个想法是成熟类别、新兴词组，还是微弱噪声；
- 构建有信源支撑的草稿，而不把原始时间线、私聊、凭据或本地日志复制进
  LoopX 状态；
- 即使主人授予广泛发帖酌情权，也保持发布的可审计性。

不要用它做凭据收集、账号设置、私有时间线转储、批量外联、验证码绕过、交易、
付费数据或生产动作。

## 运行循环

每次 connector 支撑的内容运行都应遵循该序列：

```text
doctor -> route selection -> read-only source map -> maturity scoring
       -> ops brief -> draft packet -> publish/audit gate -> compact monitor
```

重要的规则是：Agent-Reach 是信源路由器，不是行动真相源。LoopX 保有紧凑的行动
契约：

- 读的是哪个信源；
- 边界是公开、登录只读、私有需审阅，还是禁止；
- 该信源支撑什么断言；
- 生成了什么草稿；
- 有什么发布权威；
- 随后有什么监控或停止条件。

## 路由选择

从以下命令开始：

```bash
agent-reach doctor --json
```

把 doctor 输出当作能力证据。只有当活跃后端可用且访问边界清晰时，一条路由才
可用。

建议的路由映射：

| 路由 | 典型后端 | 边界 | 安全用途 |
| --- | --- | --- | --- |
| GitHub | `gh CLI` | 登录只读 | repo/搜索元数据、公开 stars、描述、显式路由时的 issue/PR 元数据 |
| Web | Jina Reader | 公开免登录 | 公开文档与文章，仅少量引用 |
| RSS | feedparser | 公开免登录 | feed 标题、链接、时间戳、摘要 |
| V2EX | 公开 API | 公开免登录 | 作为社区信号的热门话题与公开回复，通常是监控级 |
| Bilibili | 公开搜索 API 或 `bili-cli` | 公开免登录 | 视频标题、作者、播放数、公开 URL |
| X/Reddit/Xiaohongshu/Facebook/Instagram | 平台 CLI 或 OpenCLI | 登录只读 | 仅只读的公开或账号可见元数据；没有单独的发布动作记录则不发帖 |

如果一条路由需要浏览器 cookies、平台登录、私人群组、DM、账号设置或原始正文
展开，就停在纯元数据并投影一个 gate。

## 证据卡片形态

Agent 应在起草前发出紧凑证据卡片：

```yaml
agent_reach_ops_signal_v0:
  channel: github | web | rss | v2ex | bilibili | x | reddit | xiaohongshu | other
  backend: gh CLI | Jina Reader | feedparser | V2EX API | Bilibili public search API | ...
  query: string
  title: string
  url: string | null
  summary: string
  boundary: public_no_login | logged_in_read | private_needs_review | forbidden
  operation: read
  observed_at: ISO-8601 timestamp
  confidence: doctor_status | source_metadata | source_body_reviewed
  maturity_score: 0 | 1 | 2 | 3
  maturity_reason: string
```

`operation` 必须是 `read`。创建 `external_write` 卡片的 connector 运行对该
source-map 阶段无效。

## 成熟度评分

刻意保持评分简单，让下一个 Agent 可以复用：

| 分数 | 含义 | 示例信号 |
| --- | --- | --- |
| 0 | 噪声或不可用路由 | 无关的热门话题、路由缺失或信源过期 |
| 1 | 弱探索信号 | 精确短语出现，但采用度很低 |
| 2 | 新兴信号 | 反复使用、适度的 stars/回复/公开关注 |
| 3 | 成熟信号 | 强采用、大量 stars/views/回复，或多个独立信源 |

对于公开 GitHub 搜索，stars 可以是第一轮代理指标：

- `>= 1000`：成熟类别信号；
- `>= 100`：新兴类别信号；
- `>= 10`：可见但弱；
- `< 10`：仅当其他信源佐证才值得探索。

对于公开视频/社区信源，只能把关注度当作线索。不要把来自戏剧、谣言或账号风险
视频的未验证断言复制进 LoopX claims。

## Ops Brief

起草前先生成一份简短简报：

```yaml
ops_brief:
  source_batch: evidence-card file or packet id
  mature_signals:
    - claim:
      supporting_cards:
      why_it_matters_for_loopx:
  weak_signals:
    - claim:
      reason_to_monitor_instead_of_draft:
  recommended_angles:
    - audience:
      body_angle:
      evidence_refs:
  stop_conditions:
    - 账号边界不清晰
    - 信源只支持元数据，不支持正文引用
    - 帖子会重复未验证的平台戏剧
```

简报是交接点。另一个 Agent 应能仅凭它起草或评审，而不必读原始 connector 输出。

## Content-Ops 起草

草稿只有具备以下全部要素才有效：

- 命名的角度与目标读者；
- 带公开/私有状态的信源地图；
- 精确正文文本；
- 媒体计划；
- 帖子与 LoopX 相关时的 repo 或 docs 链接；
- 允许发布时的账号/渠道/时机记录；
- 停止条件与首次监控计划。

主人广泛许可可能允许 Agent 自行判断发布，但不会免除审计要求。发布记录仍需要
最终正文、活跃账号或渠道、信源引用、时间戳与后续监控边界。

## 可复用 Agent Prompt

在为创作者/运营工作接入新 LoopX Agent 时，首选指令是调用 CLI packet：

```text
从外部信号起草之前，先运行 `loopx value-connectors source-map --format json`。
选择一个只读信源 profile，发出紧凑 evidence cards，打分成熟度，并撰写 ops brief。
在任何注册、发送、发帖、回复、上传、生产动作、凭据读取或私有信源展开之前，
使用 `loopx value-connectors plan`。
```

较长的后备 prompt 是：

```text
在起草社交内容之前，先运行 connector 优先的信源映射。
除非单独的 LoopX gate 批准了发布动作，否则 Agent-Reach 路由只用于只读信号收集。
发出紧凑 evidence cards，打分成熟度，撰写 ops brief，并据 brief 起草。
若发布已获授权，发帖前记录精确的正文/账号/时间/source-map/停止条件。
若活跃账号或信源边界不清晰，停下并输出 no-send packet。
```

## 示例发现

一次使用 Agent-Reach 路由的 value-explorer 运行发现：

- `long-running AI agent`、`AI agent control plane` 与 `agent loop engineering`
  的成熟 GitHub 信号；
- 围绕 Claude Code 与 AI Agent 设置/教程内容的高 Bilibili 关注度；
- 当时这一精确 LoopX 角度的 V2EX 热门话题相关性较弱。

可复用结论是：

```text
Connector 支撑的 Agent 可以找到趋势。LoopX 应当让动作可评审：evidence cards、
gates、draft packets 与 monitors。
```

## 产品化边界

第一个稳定部分现已产品化为一个 packet：

- `loopx value-connectors source-map --connector agent_reach_ops_source_map ...`；

在至少两批成功批次证明卡片形态与信源边界之前，保持实时采集与发布工具本地化。
只产品化稳定的部分：

- `loopx content-ops draft --from-source-map ...`；
- `loopx content-ops publish-record --from-draft ...`；
- `loopx content-ops monitor --published-url ...`。

不要产品化原始 provider 载荷保留、平台特定 cookies 或发布捷径。
