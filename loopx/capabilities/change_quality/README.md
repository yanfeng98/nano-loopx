# Change Quality 资格判定


Change Quality Qualification 为 LoopX 管理的 goal 提供 provider-neutral 的最终
diff 审查契约。它默认关闭。项目通过 goal policy 激活,并选择两个独立控制项:

| Policy | 含义 |
| --- | --- |
| `safe_fix` | 在最终审查 receipt 之前,允许一轮有界修复 |
| `strict_receipt` | 在 premerge 时要求针对确切当前 diff 的通过 receipt |

`safe_fix` 授予有限的变更 authority;`strict_receipt` 不授予任何 authority。
项目可以在启用 capability 后启用两者、其一或都不启用。

## 配置 Goal

把 release 自有的 workflow 安装到每个应该发现它的已连接项目与 host:

```bash
loopx project-skill install \
  --project . \
  --skill loopx-change-quality \
  --surface codex \
  --execute
```

在那些 surface 上使用 `claude-code` 或 `opencode`。这控制发现,不控制激活。
应用前先预览 goal policy:

```bash
loopx configure-goal \
  --goal-id <goal-id> \
  --change-quality-enabled \
  --change-quality-safe-fix \
  --change-quality-strict-receipt

loopx configure-goal \
  --goal-id <goal-id> \
  --change-quality-enabled \
  --change-quality-safe-fix \
  --change-quality-strict-receipt \
  --execute
```

该 policy 缺席等价于三个值全为 false。

## 协议

1. `change-quality prepare` 对已提交、已暂存、未暂存与未跟踪内容,相对 base ref
   计算哈希。它发出 `change_quality_prepare_packet_v2`。
2. Packet 投影路径级仓库上下文:适用的指令文件、ownership 文件、构建 manifest、
   语言提示、变更 surface 根目录,以及 provider-neutral 校验计划。它不把指令文本、
   任务正文或 manifest 内容复制进控制面。
3. Host 或 model 以 simplify-first 方式审查该确切范围。它写一条有据可依的
   `reuse` 结论、一条有据可依的 `simplification` 结论、稀疏触发的 `risks[]` 与
   选中的 `validation[]`。Type/API 边界、配置、运行时 ownership、效率、
   错误/监督、测试/校验、文档/注释与安全/发布仍是护栏类别,但 Agent 不必为
   每一类都填一条 all-clear。结果使用 `change_quality_agent_result_v2`。
4. 如果 policy 允许,host 可以执行一轮有界 safe-fix pass。任何编辑都会使旧
   fingerprint 失效,所以 prepare 与最终审查会再次运行。
5. `change-quality record --execute` 把四个结果块对照当前 fingerprint 校验,
   从稀疏 risks 与 validation 结果派生护栏状态,并写一条紧凑的本地运行时
   receipt。失败的 validation、跳过的必需 validation 与未解决的 blocker risks
   fail closed。
6. `change-quality verify` 检查当前确切 scope 与 v2 协议。早期实验性 receipt
   schema 无效,必须重新资格判定。
7. `canary premerge --goal-id <goal-id>` 强制执行 `strict_receipt`。

```bash
loopx --format json change-quality prepare \
  --goal-id <goal-id> --repo-path .

loopx --format json change-quality record \
  --goal-id <goal-id> --repo-path . \
  --result-json <ignored-or-temporary-result.json> --execute

loopx --format json change-quality verify \
  --goal-id <goal-id> --repo-path .

loopx canary premerge --from-git-diff --goal-id <goal-id>
```

Receipts 位于 goal 运行时 state 下,而不是仓库中。它们保留两条主要结论、稀疏
risks、typed 校验证据与系统派生的护栏摘要。Evidence 引用是 typed 的,并与确切
变更路径、投影指令与 validators 交叉核对。Receipts 不保留 raw model transcripts、
凭据、私有上下文或 validator 日志。

## Provider 边界

Packet 不要求特定 model、语言、框架或 skill host。其审查透镜命名工程 outcome
而不是工具。自定义 runner 可以提供项目 scoped 的 `loopx-change-quality` skill,
或从同一 LoopX revision 注入等价指令。全局 installer 刻意跳过项目 scoped skills。
项目仍拥有其 tests、lint、类型检查、安全检查、build 命令与仓库特定规则;LoopX
记录运行了哪些 oracle 及其结果,而不是假装一个通用检查器理解每种语言。

校验计划只从结构化 manifests 发现仓库声明的任务身份。初始适配器理解
`pyproject.toml` 中的 Poe 与 Hatch 任务名、`.cargo/config.toml` 中的 Cargo
aliases 与 `package.json` 中的 package scripts。每个候选携带类别、runner kind、
任务名与来源引用;script 正文留在仓库,执行仍由 host 决定。缺失的 format、lint、
typecheck 或 test 类别保持显式 unresolved,而不是用猜测命令填充。适用的
`AGENTS.md` 与 `CLAUDE.md` 文件被投影为必读项,而不是被当作 shell 输入解析。
fixture、testdata、vendor、third-party 或依赖目录下的 manifests 报告为被忽略的
引用,绝不提升为项目 oracle 候选。

Blocking finding 必须是具体的正确性、安全、隐私、契约或必需校验失败。主观风格
建议保持非阻塞。失败的 validator 即使 reviewer 忘了把它重复为 blocker finding,
也独立为不通过。

Turn 可以在一次有界执行中携带 packet 或 receipt 引用。它不拥有 policy 或执行。
权威的 merge 决策仍留在 `canary premerge`。

## 初始范围

本版本有意只资格判定一个最终 diff,至多一轮 safe-fix pass。它不递归审查 reviews,
不构建 model 层级,也不要求多个 agent 达成共识。语言与构建系统提示是发现输入,
不是硬编码 validator policy。初始矩阵为 Python、Rust 与 TypeScript 证明同一
输出契约,同时保留不同的 Poe、Cargo 与 package-script runner 身份。它不发明共享
compactor,也不静默执行任何任务。

语义标定使用五个公开控制面 PR,覆盖 registry 边界抽取、benchmark read-model
移动、可恢复 Turn 阶段、Vision replan 修复与 capability-envelope 传播。Replay
保持 benchmark 敏感的手工挂起独立于 receipt 成功,并证明只能报告一轮连贯的
safe-fix pass。V2 fixture 还直接演示输出预算变化:五个 case 不再携带五十行
手写 lens。这些 fixtures 标定审查行为;它们不是项目特定的生产 policy。

## Model 行为影子

Schema replay 证明 receipt 结构有效;它不证明 model 会识别可移除复杂度或避免
发明 churn。独立 `change_quality_shadow_matrix_v0` 因此配对:

- 五个最终的、已接受的公开 PR diff,应保持无推测性发现;以及
- 三个保持行为的 Python、Rust 与 TypeScript 变更,其测试仍通过,但实现增加了
  一次性 wrapper 或低价值 helper。

Live runner 使用同一 model 与确切 case 比较其历史 v0 与 simplify-first v1 影子
prompts;那些标签给影子实验版本编号,而不是给 receipt 协议。它评分结果 schema
有效性、主要 simplify 覆盖、simplify finding 精确度与召回、已接受 PR 上的误报、
化简决策、safe-fix 资格、已跟踪文件变更、输出 tokens 与延迟:

```bash
python3 scripts/qualify-change-quality-model-shadow.py \
  --repo-root . \
  --model gpt-5.6-sol \
  --reasoning-effort low
```

这是手动触发的低频资格判定,不是 PR smoke 或普通 premerge 步骤。Model actors
运行在一次性仓库中。Runner 只保留结果 digests、有界分数、usage 与延迟;prompts、
model 响应、stderr、命令日志与临时 worktrees 都被丢弃。通过的影子可以推荐
strict-receipt 提升,但 receipt 显式设置
`automatic_policy_mutation_allowed=false`。仓库 policy 仍通过其正常 owner 与控制面
路径改变。`--case-id` 运行仍是有用诊断,但只有覆盖当前声明的完整矩阵的运行才能
发出该提升推荐;当矩阵扩大时,旧 receipt 也随之失去资格。
