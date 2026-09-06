# Better Agent 三 Provider Workflow 审计 v0


## 决策

**并行运行 provider 特定检查，但任何共享树（shared-tree）实现都要串行化在父级评审
gate 之后。当一个专业 lane 不再贡献 provider 特定证据时，停止它。**

这是针对 [LoopX issue #670](https://github.com/huangruiteng/loopx/issues/670) 中提出的合成
workflow 的仅元数据审计设计。它不是一条证据，不能说明 Better Agent 的运行已经表现出重复
工作、陈旧状态或冲突变更。

## Workflow

[Better Agent](https://github.com/ofekron/better-agent) 描述了一个同时用于 Claude、Codex
与 Gemini 的本地工作区，支持 session 分叉、委派、并行执行与 headless SDK/CLI 控制。它的
维护者提出了这个合成任务：

1. 三个专业 lane 分别检查 Codex、Claude 与 Gemini 集成；
2. 每个 lane 返回发现与验证证据；
3. 父级把发现调和为一个共享实现；
4. 父级决定保留、停止还是串行化这些 lanes。

审计单元是一个父任务加上它的三个子 lanes。Prompt、消息体、凭证、原始日志与私有
session 内容不在范围内。

## 最低元数据

| 字段 | 用途 |
| --- | --- |
| `parent_run_id` 与 `lane_id` | 在不复制 session 内容的情况下保持血统明确。 |
| `provider` 与 `scope_summary` | 展示每个 lane 预期的独特贡献。 |
| `base_revision` 与 `observed_at` | 检测由陈旧共享树状态产生的发现。 |
| `inspected_paths` | 在不保留文件内容的情况下衡量探索重叠。 |
| `proposed_write_scopes` | 在写入开始前检测实现冲突。 |
| `validation_receipts` | 区分已检查的证据与叙述性的成功声明。 |
| `finding_keys` 与 `recommendation` | 在不存储完整 transcript 的情况下比较结论。 |
| `parent_decision` 与 `decision_reason_codes` | 保留 keep、stop 或 serialize 的结果。 |

路径列表应当相对仓库。Validation receipts 应当保留命令或检查标识、状态、revision 与
时间戳，但不保留原始输出。

## 信号

以下信号由元数据推导。它们不是从 Agent 置信度或通用“成功”标签推断的。

| 信号 | 证据 | 解读 |
| --- | --- | --- |
| 重复探索 | `inspected_paths` 与 `finding_keys` 高度重叠，且没有 provider 特定结果。 | 有一个 lane 可能是冗余的。 |
| 陈旧共享状态 | 评审某 lane 的建议时，它的 `base_revision` 与父级集成 revision 不同。 | 接受结果前先 rebase 或重新检查。 |
| 冲突实现 | 重叠的 `proposed_write_scopes` 加上不兼容的建议。 | 不要让 lanes 并行写入。 |
| 表面成功 | lane 本地检查通过，但没有父级集成 receipt 覆盖合并后的变更。 | workflow 尚未验证。 |
| 独特 provider 价值 | 一个 lane 发现了其他 lane 都没有覆盖的 provider 特定契约、失败或检查。 | 保持该 lane 活跃。 |

重叠是评审线索，不是自动停止。两个 lanes 可能为不同的 provider 契约检查同一个适配器。
父级必须记录第二个 lane 是否增加了独特证据。

## 决策规则

### 保留所有 lanes

当三个检查 lane 各自拥有不同的 provider 范围并持续增加独特发现或验证 receipts 时，保留它们。
路径重叠时的共享只读检查是允许的。

### 停止一个冗余 lane

当以下条件全部为真时停止一个 lane：

- 它当前范围与另一个存活 lane 实质重叠；
- 自上次父评审以来，它没有增加任何独特发现或验证 receipt；
- 停止它不会移除 provider 特定覆盖。

记录被停止的 lane、保留的 lane、重叠证据与父决策。除非存在 lane 时长或 token/cost 元数据，
否则不要估算节省的成本。

### 串行化实现

当任何 lane 提议重叠的写范围、基于陈旧基础 revision 工作，或建议与另一个 lane 不兼容的变更
时，串行化最终实现。父级先选择一个实现 todo 与一个基础 revision。其他 lanes 变成评审者或
validator；它们不再持续写入同一个共享树。

只有写范围不相交且父级记录了分界之后，实现才可以回到并行工作。

## 信任分级

1. **高：** 仓库 revisions、相对路径集合、todo 或 lease 身份、commit receipts 与可复现的
   验证状态。
2. **中：** 与高信任证据关联的紧凑 finding keys 与父级撰写的 reason codes。
3. **低：** 自由格式建议、自报告完成，或没有集成 receipt 的 lane 本地成功。

父决策应当为任何 stop 或 merge 选择引用高信任证据。低信任证据可以触发评审，但不能结束评审。

## 度量

只使用测量到的计数器：

- 从最后一次 lane receipt 到记录决策的父评审延迟；
- 因被证明冗余而停止的 lane 数量；
- 父评审点上的重复 inspected-path 数量；
- 实现前拦截到的重叠写范围冲突；
- 产生一个被接受 receipt 之前执行的集成验证重跑次数；
- 在显式停止决策后节省的 lane 分钟数或 provider 成本（当这些值可用时）。

如果审计缩短了真实的父决策，或在重复实现前拦到一个冲突，它就是有用的。它不能仅凭这个合成
设计声称节省。

## 契合与停止标准

如果 Better Agent 能在不包含 prompts、原始日志、凭证或私有 session 内容的情况下导出上述
最低元数据，就进行一次合成回放。当它产生一个可解释的父决策与一个集成验证 receipt 时，
回放通过。

如果该 workflow 不能独立于私有 traces 暴露基础 revisions、相对路径范围与验证 receipts，
就停止这条审计路线。如果三个 lanes 只是叙述性场景、没有任何有界合成运行能产生可观察元数据，
也停止。

## 下一个有界步骤

在一个一次性的公开 fixture 上运行一个合成 provider 对等任务。只捕获最低元数据，然后应用
上述规则。父级应当只选择一种结果：

- 保留所有检查 lanes，因为每个都增加了独特 provider 证据；
- 用测量到的重叠证据停止至少一个冗余 lane；或
- 把实现串行化在一个共享状态评审 gate 之后。

该回放不需要任何 issue 评论、Better Agent 中的仓库变更、生产访问或私有材料。
