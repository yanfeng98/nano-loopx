# 公共 / 私有边界

> [English](public-private-boundary.md)

LoopX 设计为公开的，但大多数有用的目标证据不是。

## 公共

以下内容可安全放在公共仓库：

- schemas，
- 运行时目录约定，
- 通用 CLI 代码，
- adapter 生命周期规则，
- peer 任务与临时 worker 生命周期状态，
- 通用协调规则，
- 验证命令，
- 脱敏示例，
- 高层设计说明。

## 私有

以下内容应留在项目本地的被忽略文件里：

- 本地绝对路径，
- 内部仓库名称，
- 原始日志与指标，
- 任务 id，
- 文档链接，
- 凭据与令牌，
- 来自私有工作的人名或团队名，
- 暴露当前用户上下文的活跃目标状态，
- 原始 sub-agent 提示与轨迹，
- 包含本地路径或私有产物的子 run 证据。

## 示例边界

使用描述私有材料形状的示例，而不复制材料本身。一个好的公共 fixture 应让贡献者
在了解契约、重跑验证、检查失败模式的同时，对原始私有 run 一无所知。

### Benchmark 轨迹

安全的公共摘要：

```json
{
  "case_id": "synthetic-benchmark-case",
  "adapter": "benchmark-native",
  "attempts": 2,
  "terminal_status": "blocked",
  "blocker_class": "missing-public-fixture",
  "validation": ["python3 examples/benchmark-candidate-source-boundary-smoke.py"]
}
```

不安全的公共轨迹：

```text
task text copied from a private benchmark, verifier tail, raw model transcript,
upload URL, host log path, or unreleased scoring artifact
```

### Active State

安全的公共 fixture：

```markdown
# ACTIVE_GOAL_STATE example

- Goal: Improve a synthetic fixture.
- User gate: Choose whether to publish the sanitized example.
- Agent todo: Run the public smoke and report the result.
- Evidence: `examples/example-smoke.py` passed.
```

不安全的公共状态：

```markdown
- Goal: Finish the user's current private project.
- Evidence: copied owner notes, private document URL, local runtime file, raw
  child-agent prompt, or private repository branch.
```

### 本地路径

安全的路径形状：

```text
<project-root>/examples/example-smoke.py
<runtime-root>/archived-goals/<goal-id>/
```

不安全的路径：

```text
a real workstation home directory, private mounted volume, local registry
database, or host-specific benchmark output directory
```

### 凭据

安全的凭据边界：

```json
{
  "provider": "example-provider",
  "credential_source": "environment",
  "credential_values_recorded": false,
  "missing_credential_blocker": "configure provider credentials locally"
}
```

不安全的凭据材料：

```text
token value, cookie, authorization header, private SSH key, session dump, or
redaction that still preserves enough characters to reconstruct the secret
```

### 紧凑产物

安全的紧凑产物：

```json
{
  "artifact_kind": "status_projection",
  "public_safe": true,
  "source_refs": ["synthetic-fixture"],
  "next_action": "rerun the public smoke after changing the fixture"
}
```

不安全的产物：

```text
raw uploaded files, screenshots with private data, unredacted logs, hidden
provider payloads, or a public artifact that points back to private storage
```

## Sub-Agent 数据

Sub-agent 编排增加泄漏风险，因为子提示往往包含比最终报告需要的更多上下文。
公共产物应保留：

- schema 名称，
- 角色名称，
- 脱敏的工作作用域示例，
- 生命周期状态，
- 通用 merge 规则。

项目私有状态应保留：

- 原始子提示，
- 原始轨迹，
- 本地任务证据，
- 非公开仓库名，
- 包含项目特定上下文时的确切命令输出。

Run 摘要只有在脱敏后才可发布。

## 实用规则

公共仓库应回答："loopx 如何工作？"

项目仓库应回答："这个具体目标现在在做什么？"

运行时根应回答："最近的 goal tick 发生了什么？"

真实 controller 状态属于被忽略的本地文件，如
`.codex/goals/<goal-id>/ACTIVE_GOAL_STATE.md`、
`.local/goals/<goal-id>/ACTIVE_GOAL_STATE.md` 或共享运行时根。公共仓库可以跟踪
脱敏模板、fixture 与紧凑投影，但不能跟踪 controller 每轮更新的活动文件。

`loopx check` 把它当作文件状态边界，而不只是路径名边界。未被 git 跟踪的本地
私有状态可以包含私有文档链接，因为它不是可发布产物。如果同一文件被 git 跟踪，
它就进入公共边界，像任何其他可发布文件一样被扫描。

刻意发布带私有文档链接的跟踪文件的项目，可以通过项目注册表 opt in：

```json
{
  "public_boundary": {
    "tracked_private_doc_urls": "allow"
  }
}
```

该策略只允许跟踪文件中的 `private_doc_url` 发现项。它不允许凭据、令牌、密码、
私有 IP、内部任务 id 或本地私有路径。

如果一个纯运行时目标已过期，归档其目录，而不是把私有 run payload 拷贝进公共笔记：

```bash
loopx archive-runtime --goal-id old-experiment-goal
loopx archive-runtime --goal-id old-experiment-goal --execute
```

第一个命令是 dry-run。第二个把本地运行时目录移到
`<runtime-root>/archived-goals/` 下；它不脱敏也不发布 payload。

## 私有安全试点清单

在私有项目成为 LoopX 试点前，在项目本地 active state 或 registry 里定义这个边界。
在读取私有证据、启动 adapter 或发布公共 fixture 之前先做这件事。

- Goal 身份：稳定 `goal_id`、public-safe objective、owner 模式，
  以及试点应回答的确切问题。
- 证据类别：列出来源角色，如设计权威、owner 评审、来源仓库、目标仓库、
  验证 dashboard 与历史笔记，而不点名私有 URL、仓库、人、团队或产品配置。
- 公共投影：决定哪些字段可以离开项目，如 role、freshness、缺失 gate、
  下一个动作、验证面、quota 状态与停止条件。
- 私有保留：把原始链接、路径、指标、日志、任务 id、评审文本、生成的配置
  与实现 diff 留在项目本地的被忽略状态或运行时根。
- 写作用域：说明首轮试点是只读、仅本地状态、仅公共 fixture，
  还是允许编辑项目文件。
- Gate 顺序：要求健康与边界扫描，然后 owner 或 controller 关卡，然后证据就绪，
  然后计算配额，然后 Codex 执行。
- 验证面：点名能证明试点投影有用的最小 public-safe 检查，如 `read-only-map`、
  `status`、review packet、dashboard 渲染或 fixture smoke。
- Handoff 规则：如果出现缺失 owner 行动，把它写成 user todo；
  如果出现安全的项目 Agent 后续，把它写成 agent todo。二者都不藏在 `Next Action` 里。
- 发布停止：除非产物本身通过公共/私有扫描且私有证据仍留在项目本地状态，
  否则不要提交或 push 试点产物。

来自私有试点的第一个公共产物通常应是脱敏 fixture 或 status schema。
第一个私有产物应是紧凑的项目本地状态更新，说明考虑了哪些私有来源，
以及它们为何适合或不适合投影。
