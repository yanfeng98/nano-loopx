# 只读 Turn Journal 解释设计


## 目标

添加一个只读的 `interpret_turn_journal` lens，把现有的 fenced LoopX Turn journal 映射到
`EffectTurn`。该 lens 报告无效应回放（effect-free replay）是否合法，把身份与阶段顺序违规解释为
结构化数据，并在不执行或变更任何东西的情况下保留 terminal journal tombstones。

## 范围

本次变更将：

- 把 `interpret_turn_journal` 添加到 `loopx.control_plane.effect_program`；
- 在整个 journal trace 上比较 goal、owner 与 Turn-key 身份；
- 验证 `completed_phases` 是 `TRANSACTION_PHASES` 的有序前缀；
- 把 terminal 的 `committed`、`stopped` 与 `failed` journal 状态暴露为保留的 tombstone；
- 在不授权执行的情况下区分 `replay_legal` 与 `replay_blocked`；
- 添加聚焦语义测试并更新 Effect Interpreter Packet 参考文档。

本次变更不会添加 journal 加载器、executor、scheduler 路径、写操作、schema 迁移、模型调用、
quota 花费或第二套 settlement 账本。

## 归属与放置

- Capability 结果：把现有 Turn journal 读取为 Effect Program observation。
- Capability owner：现有的 Turn / Effect Program 契约。
- Provider：内置于 LoopX core；不涉及 extension provider。
- 实现位置：`loopx/control_plane/effect_program.py`，与 `interpret_quota_should_run_packet` 和
  `interpret_turn_result_packet` 并列。

最近且存在的 owner 就足够了，因为这只是对已经发布的 Turn 契约的另一个 packet lens。新的
capability 包、journal 适配器或解释器协议会引入结构却没有独立的调用方契约。

## 公开 API

```python
def interpret_turn_journal(
    journal: Mapping[str, Any],
    *,
    goal_id: str | None = None,
    agent_id: str | None = None,
    turn_key: str | None = None,
    capabilities: Sequence[str] = (),
) -> EffectTurn:
    ...
```

传入的身份参数是期望，不是 authority 授予。该函数读取传入的映射并返回 `EffectTurn`；
它不打开路径、获取锁、写入 journal，也不调用回放。

## 身份与阶段解释

该 lens 从现有 trace 位置读取身份：

- journal：`goal_id` 与 `turn_key`；
- 存储的 plan envelope：`goal_id` 与 `agent_id`；
- transaction plan：`turn_key`；
- 类型化 settlement identity：`goal_id` 与 `agent_id`；
- host result 与 receipt：任何存在的 `turn_key`。

一个身份维度上所有存在的值必须彼此一致，并在提供了相应显式期望时与之一致。缺失的必需
journal、envelope、transaction 或 settlement 身份以结构化 invalid identity 报告，而不是抛出
异常。可选的 host result 与 receipt 字段只在存在时才比较，因为进行中的 trace 可能尚未到达
这些阶段。

`completed_phases` 只有在其字符串值等于 `TRANSACTION_PHASES` 相同长度前缀的列表时才有效。
空列表是合法有序前缀，但它不会使进行中的 journal 有资格进行无效应回放。

## 回放与 Tombstone 语义

当以下条件满足时，无效应回放合法：

1. goal、owner 与 Turn-key 身份匹配；
2. 已完成阶段形成有序 transaction 前缀；且
3. journal 具有当前视为回放 tombstone 的 terminal 状态：
   `committed`、`stopped` 或 `failed`。

这描述了现有的默认回放边界。它不授权 `retry_failed=True` 恢复，后者仍归 executor 所有，
并且可能执行效应。

输入 journal 绝不被修改。Terminal 状态投影为 `tombstone_retained=True` 并保留原始
`journal_status`；不创建、删除或重写任何 tombstone。非 terminal 状态可见，但
`replay_legal=False`、`tombstone_retained=False`。

## EffectTurn 映射

`EffectRequest`：

- `kind="turn_journal"`；
- `source="turn_journal"`；
- 期望的 `goal_id`、`agent_id` 与 capabilities 保持可见；
- `context` 包含：
  - `replay_legal`；
  - `goal_matches`；
  - `owner_matches`；
  - `turn_key_matches`；
  - `phases_form_ordered_prefix`；
  - `journal_status`；
  - `tombstone_retained`；
  - 规范化的 `completed_phases`；
  - 有序的类型化违规值元组。

`EffectInterpretation`：

- `route="turn_journal_replay"`；
- `obligation="observe_fenced_replay"`；
- `interaction_mode="read_only"`。

`EffectObservation`：

- `decision` 是 `replay_legal` 或 `replay_blocked`；
- `should_run` 恒为 `False`，使该 lens 不会被误认为执行许可；
- `effective_action` 是 `observe_replay` 或 `block_replay`；
- `recommended_action` 给出紧凑、领域中立的 readback；
- `protocol_summary` 在不内嵌原始 journal 数据的情况下总结合法性。

`EffectNext` 为空。结构化的 `request.context["replay_legal"]` 字段（而不是 `should_run`）是
回放合法性信号。

## 结构化违规

实现将定义一个类型化 `StrEnum` 用于稳定的违规值，并把其字符串值投影到
`EffectRequest.context`。初始值覆盖：

- `goal_identity_missing`；
- `goal_mismatch`；
- `owner_identity_missing`；
- `owner_mismatch`；
- `turn_key_identity_missing`；
- `turn_key_mismatch`；
- `completed_phases_invalid`；
- `completed_phases_not_ordered_prefix`；
- `journal_not_terminal`；
- `journal_status_unsupported`。

违规按确定性顺序累积，使一个 trace 在单次读取中暴露所有独立问题。分类基于类型化字段与精确
相等，不使用子串启发式。

## 错误处理与兼容性

语义不匹配返回带 `decision="replay_blocked"` 的 `EffectTurn`。它们不抛出异常。该函数接受任何
`Mapping`；格式错误的嵌套值被视为缺失或无效的结构化字段。

现有 `EffectTurn` dataclasses 与现有解释器行为保持不变。没有 journal 或 Turn wire schema
变更。不使用新 lens 的调用方观察不到行为变化。

## 测试

聚焦测试将从 Turn transaction 契约推导期望，并覆盖：

1. 带匹配 trace 身份与有序阶段的 terminal journal；
2. owner、goal 与 Turn-key 不匹配累积为结构化违规；
3. 即使 journal 是 terminal，非前缀阶段序列也被阻止；
4. 保留的 `committed`、`stopped` 与 `failed` tombstone 状态；
5. 保持可观察但不可回放合法的非 terminal journal；
6. 格式错误或缺失的身份字段返回被阻止的结果而非抛出异常；
7. 输入不可变性与空的 `EffectNext` 字段。

验证将包括聚焦 pytest 覆盖、现有 fake-host Turn walkthrough、文档化的 `loopx check` 扫描，
以及仓库基于风险的 premerge canary 对最终 diff 的检查。
