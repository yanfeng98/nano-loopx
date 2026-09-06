# RFC：Goal 用量、Token 与成本展示（v0）


- 状态：Draft
- 范围：核心 `usage_summary` 的 token / 成本 / 时长捕获与现有 dashboard 展示
- 决策类型：有界的公开契约变更加一层 provider-neutral 捕获

## 摘要

本 RFC 提议把每个 goal 的 LLM 用量——输入/输出/cache token、估算成本与 wall-time
时长——捕获进现有核心 `usage_summary` 聚合，并在现有 dashboard 中展示。改动引入
一个 provider-neutral 捕获接缝；它不增加第二个用量存储、新 dashboard 或成本感知
的运行时路由。

意图是让操作者按 goal 看到一次长程 run 实际消耗了什么——不只是它是否被允许运行
（当前 quota slot 核算），还有它花了多少。这补上了 `docs/quota-allocation.md` 留下的
缺口，该文档注明后续版本可能"用真实 runtime、token 开销或成本替换 slot"。

## 问题

`usage_summary` 明确是排除 token 计数的 run-history 代理。其代理说明写到它是
"run-history proxy; excludes token counts and raw thread logs"，公开的
`docs/status-data-contract.md` 重复了同样的排除。由此导致：

- Dashboard 可以显示发生了多少次 run、消耗了多少 quota slot，但无法显示一个 goal
  烧掉了多少 token 或花费几何。
- Token 与成本捕获已经存在，但只在 benchmark 路径上，且只接到一个 runtime
  （Codex）和一张外部定价表。它无法从 goal runtime 的主路径到达。
- 今天没有任何 goal runtime 上报 LLM 用量。claude、opencode 与 pi 的 goal 模式
  没有携带 token 遥测代码；opencode 与 pi 中的"token"标识符指调度器身份 token，
  不是 LLM 消耗。

修复所需的基础设施大多已存在（一个用量聚合、一个 JSON 状态 API、一个成熟
dashboard）。缺少的是把每个 runtime 的用量转换成一种归一化形态的捕获接缝，以及
接纳 token/成本数据进入公开聚合的契约变更。

## 目标

- 在核心 `usage_summary` 聚合中，按 goal run 捕获输入、输出与 cache token、估算
  成本与 wall-time 时长。
- 保持摄入 provider-neutral：一种 schema，每个 runtime 一个 adapter。
- 在现有 dashboard 中展示捕获的数据，不新增 dashboard 或第二个用量存储。
- 保留现有隐私边界：原始线程日志、prompt 与 completion 永不进入 `usage_summary`；
  只有聚合的数值用量进入。

## 非目标

- 成本感知的运行时路由或选择（后续工作；依赖本项）。
- 存储原始 prompt、completion、工具输出或记录文本。
- 新建 dashboard 或并行用量存储。
- 捕获逐 Turn 的细粒度遥测；本 RFC 先瞄准 run 级聚合。
- 削弱任何现有 gate、验证或 quota 不变式。

## 决策边界

本 RFC 变更一个公开契约，其余保持不变。

**变更。** `usage_summary` 成为*包含*聚合 token 计数、估算成本与时长的 run-history
代理。代理说明与 `docs/status-data-contract.md` 随之更新；历史性的"excludes token
counts"措辞被撤回。Token/成本/时长成为 `blank_usage_goal` 与 `totals` 块的
first-class 字段。

**不变。** 原始线程日志、prompt 与 completion 仍被排除在 `usage_summary` 之外。
原始内容的排除是隐私不变式，不是历史偶然，予以保留。

由于这改动了一个已记录的公开契约，实现必须在同一变更集内更新
`docs/status-data-contract.md`，并为新字段添加聚焦测试（目前 `usage_summary`
没有任何测试）。

## 捕获契约

在 `control_plane/quota/` 下添加一个 provider-neutral 捕获接缝，仿照已存在的
spend 与 slot 核算。

接缝的核心是一个函数：

```python
def collect_usage_for_run(run) -> UsageSample | None:
    """Return normalized usage for a run, or None if the runtime reports none."""
```

`UsageSample` 是一个归一化的、公开安全的形态：

```json
{
  "input_tokens": 12000,
  "output_tokens": 3400,
  "cache_tokens": 8000,
  "cost_usd": 0.21,
  "duration_ms": 184000,
  "provider": "codex",
  "model": "<model id>",
  "measured_at": "2026-08-11T14:55:00Z"
}
```

每个 runtime 注册一个读取自身用量来源并返回 `UsageSample`（或 `None`）的 adapter。
`build_usage_summary` 中的聚合循环为每次 run 询问接缝，把结果累加进新字段。
不上报任何数据的 runtime 不贡献任何东西；对这些 runtime，聚合优雅地退化为当前
行为。

Codex adapter 可以复用已在 benchmark 路径验证过的提取方式（扫描会话的 token-count
事件取得最终累计值），并把逻辑从其现有外部耦合中拆出。

## 成本计算

成本是唯一一项不是直接测量的字段；它由 token 与价格推导。两个选项：

1. **Runtime 上报成本（推荐）。** 每个 adapter 用其测得的 token 和它已知的价格
   （它已持有 model id）计算成本，并在 `UsageSample` 中返回 `cost_usd`。Core
   存储并聚合它。
2. **Core 计算成本。** Core 持有一张价格表，从 token 与模型推导成本。这样计算
   集中化，但引入了一张可能随 provider 变化而漂移的价格表。

本 RFC 推荐选项 1，因为由 core 维护的价格表会与 benchmark 路径已经依赖的外部表
重复并漂移，而且每个 runtime 已持有给自己的用量定价所需的 model id。最终选择是
评审中的未决问题。

无论哪个选项，`usage_summary` 只暴露聚合成本。不展示单位价格明细，以免泄露
provider 专属的商业条款。

## 数据分级

按照该 issue 的指引，token 计数、估算成本与时长被归类为**公开安全**，可以进入
公开 `usage_summary` 契约：

- 聚合 token 计数与成本揭示的是运维开销，而非内容。
- Wall-time 时长是运维元数据。
- Provider 与模型标识符是公开产品名。

它们**不**携带 prompt 内容、completion 文本、工具输出、凭证或任何可重建对话的
材料。原始线程日志的排除作为单独、更严格的不变式保留。

## 最小有用切片

第一个切片在一个 runtime 上端到端验证接缝：

1. 在 `control_plane/quota/` 下添加 `UsageSample` 形态与 `collect_usage_for_run`
   接缝。
2. 实现 Codex adapter（复用 benchmark 提取方式）。
3. 用 token/成本/时长字段扩展 `blank_usage_goal`、`totals` 块与
   `build_usage_summary` 循环；更新代理说明。
4. 在同一变更集中更新 `docs/status-data-contract.md`。
5. 在现有 dashboard 中展示新字段（不新增 dashboard）。
6. 添加 `tests/control_plane/quota/test_usage_summary.py`。

claude、opencode 与 pi goal 模式的 adapter 是显式后续工作，不在本切片范围内，
因为它们今天都不上报用量，且各需要自己的摄入机制（statusline hook、stdout 解析
或 bridge IPC）。该接缝的设计保证添加 adapter 无需重访聚合或契约。

## 验证

切片必须证明：

- 一次 Codex goal run 后，该 goal 的 `usage_summary` 携带非零 token/成本/时长；
- dashboard 渲染新字段；
- 不上报任何数据的 runtime 让聚合保持当前行为；
- 原始线程日志、prompt 与 completion 不进入 `usage_summary`（隐私回归检查）；
- `docs/status-data-contract.md` 中的公开契约与实现一致；
- `loopx check --scan-path` 报告无私有数据泄露。

## 未决问题

1. 成本计算位置——runtime 上报（推荐）对 core 计算。
2. 模型标识符是否需要在公开界面脱敏，还是聚合成本已足够、模型名视为公开。
3. claude、opencode 与 pi runtime 的摄入机制与顺序。
4. 是否添加专用 `/usage.json` 端点，还是继续通过现有 status 载荷展示（本 RFC
   采用后者）。
5. 时长捕获锚点——哪些 run 边界事件界定 wall-time。

## 公开参考

- [LoopX quota allocation](../../quota-allocation.md) — 注明后续版本可能用真实
  token 开销或成本替换 slot。
- [LoopX status data contract](../../status-data-contract.md) — 本 RFC 变更的公开契约。
- Issue #3085 — 本 RFC 遵循的功能请求与 maintainer 指引。

本 RFC 排除私有对话、内部链接、本地文件系统路径、凭证与原始记录。
