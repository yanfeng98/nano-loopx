---
name: loopx-change-quality
description: Qualify the exact final diff for a LoopX-managed goal. Use when goal policy enables change_quality_qualification, before a non-trivial delivery or merge, and when producing or repairing an exact-scope quality receipt. The workflow is language-neutral, permits at most one policy-authorized safe-fix pass, and never grants merge or repository authority.
---

# LoopX 变更质量


仅当所选 goal 的 `change_quality_qualification.enabled` 策略为 true 时才使用
本技能。LoopX 拥有规范源，但不全局安装它。为相关宿主在已连接项目中安装受管
副本：

```bash
loopx project-skill install \
  --project . \
  --skill loopx-change-quality \
  --surface codex \
  --execute
```

对 Codex 之外的宿主使用 `--surface claude-code`。
Skill 发现不激活 capability；在 goal 策略启用前，产品行为保持默认关闭。

CLI 是契约权威。本技能提供宿主无关的评审工作流。仓库指令、测试、lint、类型
检查器与安全检查仍然是项目的质量 oracle。

## 准备精确范围

从仓库 worktree 运行：

```bash
loopx --format json change-quality prepare \
  --goal-id <goal-id> \
  --repo-path . \
  --base-ref origin/main
```

当包报告 `disabled` 或 `no_changes` 时停止。当报告 `review_required` 时，
只评审包中的文件与精确 fingerprint。判断变更前先读仓库本地指令。

当宿主依赖 skill 发现时，运行 `loopx project-skill status --project . --skill
loopx-change-quality`。如果受管副本缺失或过期，预览显式项目安装；不要回退到
全局副本。

## 评审规则

## 先简化

把评审预算花在简化上，再进行宽泛质量分析：

1. 复用既有 helper 或持久仓库规则，而不是复制行为或知识。
2. 在保持行为的前提下，移除冗余状态、参数、分支、间接层与投机抽象。
3. 当一个私有 helper 或包装器只有一到三行、最多两个生产调用方、不持有独立
   领域不变量、效果或错误边界时，挑战它。
4. 优先选择让归属与意图更清晰的最小内聚编辑。当前形状已直接内聚时，不要
   制造震荡。

写一条有证据的 `reuse` 结论与一条有证据的 `simplification` 结论。不要为
剩余每个透镜输出一行。这些维度是稀疏 `risks[]` 的 guardrail 类别：
仅当变更界面、仓库指令、原生校验器或提议的简化提出具体风险时才添加一项。
LoopX 从 `risks[]` 与 `validation[]` 推导每个 guardrail 的状态。

可用评审透镜有：

- **reuse：**复用既有 helper 与持久知识而非重复；
- **type/API boundary：**类型、schema、兼容窗口与调用方契约保持显式且内聚；
- **configuration：**配置保持单一来源、经验证，且无隐藏模式耦合；
- **runtime ownership：**生命周期、并发、状态与副作用位于正确边界；
- **quality/simplification：**移除或显式论证不必要的间接层、分支、重复与
  投机抽象；
- **efficiency：**考虑热点路径、重复工作、内存增长与无界循环；
- **error/supervision：**失败保持可观察且可操作，无静默回退或笼统异常处理；
- **test/validation：**测试与仓库原生校验器证明预期语义与重要负向路径；
- **documentation/comments：**名称、注释与文档描述当前契约，无陈旧或重复
  叙述；
- **security/release：**安全、隐私、权限、迁移与发布兼容性在变更边界处理。

包把路径级引用投影到适用的仓库指令、归属文件、构建 manifest、语言提示与变更
界面根。它还投影从结构化仓库任务声明发现的 provider-neutral 验证计划。这是
发现上下文，不是复制仓库内容：指令文本、任务正文与 manifest 内容仍留在
worktree 中。读取每个 `required_reads` 条目、检查每个候选的 `source_ref`，
并让宿主解析具名的 Poe、Hatch、Cargo 或包任务。绝不因为候选被发现就执行它。
未解析的 format、lint、typecheck 或测试类别需要评审者判断或仓库原生指令；
不要用猜的命令填补。把 `ignored_manifest_refs` 视为不可执行上下文，尤其是
fixture 与 vendored 项目。

读取每个投影的指令引用，但不要把它的话术复制到结果中。用 typed `evidence_refs`
以 `path:`、`instruction:` 或 `validator:` 为 `reuse`、`simplification` 与每个
发出的风险提供依据。没有 guardrail 触发时保持 `risks[]` 为空。只记录被选择或
必需的 validator；失败的验证与跳过的必需验证各自独立地阻塞。

只在具体正确性、安全、隐私、契约或必需验证失败时使用 `blocker`。风格偏好与
投机重设计是 `warning` 或 `advisory`，绝不是 blocker。

此初版是单层的。评审一个最终 diff；不要递归评审评审、衍生质量 agent 层级，
或要求多个模型之间达成一致。

Guardrail 目录是评审指引，不是 Agent 输出清单，也不证明某个模型应用得好。
维护者单独针对公开 clean-PR 与种入的 Python、Rust 与 TypeScript shadow matrix
认定模型行为。
正常交付不会启动这一低频评估，模型 shadow 结果不能变更 goal 策略或授予合并
权限。

## 安全修复

`safe_fix` 与 `strict_receipt` 相互独立：

- `safe_fix=true` 最多允许一次有界修复环节。
- `strict_receipt=true` 在合并前要求精确范围证据，且不授予编辑权限。

当 `safe_fix` 为 false 时，报告风险而不修改文件。为 true 时，一次修复环节
可以在所选 todo 与 goal 边界内处理明确的简化机会或风险。不要使用破坏性 git、
扩大权限、改变产品意图、添加无关重构或掩盖失败的 validator。

任何编辑后重新运行 `prepare`。旧 fingerprint 失效。评审整个新的最终范围，
而不只是修复改动的那几行。

## 记录 receipt

写入符合包中 `change_quality_agent_result_v2` 模板的紧凑结果。除精确范围
元数据外，Agent 只写 `reuse`、`simplification`、稀疏 `risks[]` 与
`validation[]`。`simplification.safe_fix_applied` 记录允许的那一次修复环节。
跳过或失败的 validator 需要理由；失败验证或跳过必需验证使 receipt 不通过。
把原始 transcript、私有路径、凭据与无界日志排除在结果之外。

然后记录并回读精确 receipt：

```bash
loopx --format json change-quality record \
  --goal-id <goal-id> \
  --repo-path . \
  --base-ref origin/main \
  --result-json <ignored-or-temporary-result.json> \
  --execute

loopx --format json change-quality verify \
  --goal-id <goal-id> \
  --repo-path . \
  --base-ref origin/main
```

带未解决 blocker、失败 validator 或跳过必需 validator 的 receipt 不通过。
针对更早 fingerprint 的 receipt 不能为更晚 diff 认定资格。早期实验性 receipt
schema 无效，必须用当前协议重新认定。

## Premerge 强制

用 goal 身份运行权威合并 gate：

```bash
loopx canary premerge \
  --from-git-diff \
  --goal-id <goal-id>
```

Turn 可以作为一次有界事务传输 prepare 包或 receipt 引用。Turn 不拥有质量
策略，不能制造或豁免 receipt。`canary premerge` 仍然是强制权威。

## 完成证据

报告：

- 最终范围 fingerprint 与变更文件数；
- safe-fix 允许/应用情况与通过次数；
- blocker、warning 与 advisory 计数；
- 运行的项目验证及其真实结果；
- receipt id 与精确验证状态；
- premerge 状态、失败或跳过，以及人工挂起。

当严格策略要求 receipt 而 receipt 缺失、无效、过期或含未解决 blocker 时，
在交付前停止。
