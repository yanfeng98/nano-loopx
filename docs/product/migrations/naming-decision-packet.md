# 命名决策包


本包记录 LoopX 当前公开命名建议。它刻意轻量:项目仍然年轻,目标是避免过早的仓库重命名,同时给维护者一个清晰的品牌、类别与标语在首次接触对话中测试。

## 建议

保留仓库与产品名:

```text
LoopX
```

在首屏附近使用这个核心承诺:

```text
Always-on agent teams, governed by human judgment
```

在它旁边使用这个控制面类别词:

```text
Gate-aware human-in-the-loop control plane
```

当需要更多解释时,使用这个辅助类别/标语语言:

```text
dynamic goal control plane
```

公开故事应是:

> LoopX 是 agent Loop 周围的动态 goal 控制面。Codex、
> Claude Code、Cursor、终端 agent 与基准 runner 执行有界工作;LoopX 把静态
> goal 转化为长程 state:gate、todo、认领、范围、配额、evidence 与交接跨这些
> Loop 保持可见。

现在不要把仓库重命名为 `lifetime-loopx` 或
`dynamic-loopx`。在有更强证据表明用户记住另一个名字比 `LoopX` 更好之前,把
"dynamic goal control plane" 用作类别语言。

## 为何暂不重命名

`LoopX` 有两个优势:

- 它足够短,可以在对话中说出并适合命令名;
- 它在产品界面仍在变化时保持当前 CLI、文档、仓库、包与现有公开链接稳定。

这个名字并非完美独特。"Goal" 听起来像任务列表或 Codex goal-mode 功能,而 "Harness" 需要首屏解释控制面角色。但这可以用类别与对比文案处理:

```text
Not an agent runtime; the control plane around the runtime.
Not Codex goal mode; the dynamic goal state that survives across executor
loops.
```

现在重命名仓库会很嘈杂:它会在此刻制造链接变动,而项目尚未有足够公开证据证明新名字改善记忆、搜索与理解。

## 候选比较

| 候选 | 优势 | 劣势 | 决策 |
| --- | --- | --- | --- |
| `LoopX` | 简短、当前、命令友好、足够宽泛以涵盖工程与创作者/运维者场景。 | 需要类别文案来避免与 Codex goal mode 或 todo 应用混淆。 | 保留为品牌。 |
| `Lifetime LoopX` | 显式表达长程抱负。 | 作为仓库/包名太长、太笨重,且可能太抽象。 | 用作解释语言,而非品牌。 |
| `Dynamic LoopX` | 捕捉与静态 goal 提示及一次性自动化的对比。 | 作为仓库/包名仍长,没有控制面证据时 "dynamic" 会显得泛。 | 用作类别信号,而非品牌。 |
| `Goal Control Plane` | 直接命名类别。 | 太通用;品牌弱;在搜索或对话中不够独特。 | 仅偶尔解释时使用。 |
| `Agent Control Plane` | 对 agent 基建受众清晰。 | 夸大范围,暗指 LoopX 是运行时/编排器。 | 避免作主要框架。 |
| `Long-Horizon Control Plane` | 强调真实问题。 | 宽泛且技术化;与用户具体 goal 联系较弱。 | 长文文档有用时使用。 |
| `GoalOS` / `AgentOS` 风格名 | 令人难忘且产品化。 | 夸大平台范围并引发运行时预期。 | 暂时避免。 |

## 命名架构

使用三层:

1. **品牌**:`LoopX`
2. **核心承诺**:`Always-on agent teams, governed by human judgment`
3. **类别**:`Gate-aware human-in-the-loop control plane`
4. **辅助短语**:`dynamic goal control plane`

这让项目在保持稳定名称的同时,继续锤炼产品类别。

首屏堆栈示例:

```text
LoopX

Always-on agent teams, governed by human judgment.

Gate-aware human-in-the-loop control plane.

Dynamic goal control plane for long-running agents.
```

中文优先堆栈:

```text
LoopX

Always-on agent teams, governed by human judgment
Gate-aware human-in-the-loop control plane
Dynamic goal control plane for long-running agents
让多个 agent 昼夜接力，把人的判断留在控制面。

LoopX 不是替代 Codex goal/automation，而是给这些 executor loop
提供动态长期目标控制面。
```

## 何时使用各短语

命名产品、仓库、CLI、示例与 showcase 案例时使用 `LoopX`。

当首次接触界面需要比"state 管理"更强的产品承诺,而又不夸大自主生产控制时,使用 `Always-on agent teams, governed by human judgment`。

当首次接触读者需要立即获得技术类别时,使用 `Gate-aware human-in-the-loop control plane`。

当解释这比单个 agent 会话、单条终端命令或单次基准运行更大时,使用 `dynamic goal control plane`。只在时间跨度需要强调时,把 `lifetime-goal` 用作次要解释,而非主类别。

把 `Your agents keep the night shift. You keep the judgment.` 用作社交或演示标语,而非正式架构术语。

避免 `agent teammate`、`agent framework`、`autonomous platform` 或 `agent OS`,除非未来产品界面真正拥有这些能力。

## 任何重命名前的验证信号

除非至少一个轻量验证循环显示当前品牌才是瓶颈,否则不要从 `LoopX` 重命名。

一个好的验证循环:

1. 给五位新用户展示 README 或发布帖,不超过一分钟。
2. 请他们无提示回答三个问题:
   - LoopX 是在替代 Codex/Claude/Cursor,还是在包装它们?
   - 它解决长程 agent 工作中的什么问题?
   - 关掉页面后他们记得哪句短语?
3. 比较 `LoopX`、`dynamic goal control plane`、`lifetime-goal control plane` 与 `human-in-the-loop control plane` 的记忆度。
4. 只记录公开安全的聚合笔记:无原始聊天转录、个人姓名、截图、内部链接或私有项目上下文。
5. 仅在用户持续记得另一个名字更好,且也理解运行时与控制面之别时重命名。

在那之前,先改进首屏文案、showcase 与图表,再改品牌。

## 实用文案规则

- 首次提及时把品牌与类别配对:`LoopX, an always-on control plane for agent teams governed by human judgment`。
- 当用户把它与 Codex goal mode 混淆时,用执行器 Loop 拆分回答:Codex 做有界工作;LoopX 保留动态 goal state。
- 类别使用 "dynamic goal";仅当时间跨度需要强调时,在解释性段落使用 "lifetime-goal"。
- 为中文优先界面保留双语核心文案,但英文 README 正文以英文为主。
- 把命名声明视为外展语言。除非措辞成为稳定公开契约,否则不要添加断言精确营销文案的脆弱 smoke 测试。

## 当前决策

决策:保留 `LoopX`。

理由:这个名字可用、当前且紧凑;更锐利的工作是通过首屏文案、showcase 与控制面板让类别无可争议。

下次评审触发:仅在首次接触验证表明名字而非解释界面才是主要理解障碍后,重访命名。
