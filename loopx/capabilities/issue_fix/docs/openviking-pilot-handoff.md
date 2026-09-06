# OpenViking 问题修复试点交接


本方案启动一个真实的 OpenViking issue-fix agent,而不把仓库记忆或专家 bot 当作
oracle。目标是可审阅的维护者 outcome:一个聚焦修复 PR、一条有用的公开评论草稿,
或一个有理有据的 triage 决策,随后跟进 CI 与 review 监控。

## 是什么让 VikingBot 具有仓库感知

VikingBot 不依赖特殊的 OpenViking 训练模型。它的仓库感知来自组合:

1. [ContextBuilder](https://github.com/volcengine/OpenViking/blob/main/bot/vikingbot/agent/context.py)
   为当前消息加载稳定的 bootstrap 文件、skills、peer profiles 与相关记忆。
2. [MemoryStore](https://github.com/volcengine/OpenViking/blob/main/bot/vikingbot/agent/memory.py)
   区分事实、案例、可复用经验与诊断路径,然后用有界配额检索它们。
3. [VikingBot 的 README](https://github.com/volcengine/OpenViking/blob/main/bot/README.md)
   暴露 OpenViking 的 read、search、grep、glob、resource-add 与 memory-commit
   工具,并描述写操作周围的经验召回。
4. 仓库自有源已经编码了重要的开发知识:
   [CONTRIBUTING.md](https://github.com/volcengine/OpenViking/blob/main/CONTRIBUTING.md)
   把组件映射到维护者,而
   [.pr_agent.toml](https://github.com/volcengine/OpenViking/blob/main/.pr_agent.toml)
   捕获 review 不变量与项目特定风险。

实际教训是复现这套组合,而不是复制一个巨大 prompt。LoopX issue-fix agent 应只
检索与当前 issue 相关的源,把它们固定到仓库 revision,并在 feasibility 领域状态
中保留其 provenance。

## 使用顺序

先仓库证据,后记忆,最后专家咨询:

1. 在当前 revision 下,读取仓库 policy、架构、附近代码、测试与近期相关修复。
2. 当它们能收窄路由、复现或校验选择时,从 OpenViking 检索紧凑的既往教训。对
   当前 checkout 验证每条检索到的声明。
3. 只有在架构、ownership、复现或校验仍不确定时,才向 VikingBot 提出有针对性的
   问题。存储紧凑结论与 source ref,而不是 raw 响应。打补丁前在本地验证结论。

专家回答从不提供发布 authority。外部评论、PR 创建、merge 与其他写操作保留其
现有 LoopX gates。

## 现有 Codex 记忆桥

OpenViking 已经附带一个
[OpenViking Codex Memory 插件](https://github.com/volcengine/OpenViking/tree/main/examples/codex-memory-plugin)。
它提供两个有用路径:

- 生命周期 hooks 在 `UserPromptSubmit` 时召回相关记忆,在 `Stop` 时追加新 turn,
  在 `PreCompact` 前提交,并在后续 `SessionStart` 事件中恢复被遗弃的会话;
- 本地 stdio MCP proxy 暴露 OpenViking 的 `search`、`store`、`read`、`list`、
  `grep`、`glob`、`forget`、`add_resource` 与 `health` 工具。

这是真实 Codex 试点最快的桥,但默认并不是只读的。其 hooks 可能把 transcripts
与紧凑的 tool-call/result 文本捕获进记忆系统。不要把它作为 LoopX 启动的一部分
静默启用。对于第一个 issue,优先针对仅公开的仓库 namespace 做显式 MCP
`search` 与 `read`。只有 owner 审查过 hooks 并批准记忆边界、workspace/peer
隔离与凭据来源后,才启用自动捕获。LoopX 仍只存储紧凑记忆 refs、trust、
freshness 与验证结果;OpenViking 拥有记忆正文与凭据。

## 立即启动

从一条有界怀疑 surface 与聚焦测试或复现路径的 issue 开始。从当前 checkout 准备
一个紧凑上下文文件:

```json
{
  "schema_version": "issue_fix_repository_context_input_v0",
  "repository_revision": "<current-commit>",
  "sources": [
    {
      "source_id": "contributing",
      "source_kind": "repository_policy",
      "reference": "CONTRIBUTING.md",
      "trust": "authoritative",
      "freshness": "current",
      "supports": ["change_scope", "ownership"]
    },
    {
      "source_id": "focused-tests",
      "source_kind": "test_surface",
      "reference": "<repo-relative-test-path>",
      "trust": "verified",
      "freshness": "current",
      "supports": ["reproduction", "validation"]
    }
  ]
}
```

然后运行现有 workflow 与 feasibility surfaces:

```bash
loopx issue-fix workflow-plan \
  --url <public-github-issue-url> \
  --repo-path <approved-openviking-checkout> \
  --repository-context-json repository-context.json \
  --validation-label "<focused-validation-label>" \
  --format json

loopx issue-fix feasibility \
  --url <public-github-issue-url> \
  --reproduction-status planned \
  --reproduction-label "<focused-repro-plan>" \
  --scope-class bounded \
  --validation-label "<focused-validation-label>" \
  --repository-context-json repository-context.json \
  --goal-id <pilot-goal-id> \
  --format json
```

Feasibility 命令默认把紧凑上下文投影写进常规 issue-fix 领域状态行。它不创建
第二个上下文 ledger 或另一个工作流状态。

## 短期

- 一次只跑一个 issue,走 `fix_pr`、`comment_only` 或 `triage_only`。
- 把每个上下文 packet 固定到 checkout revision。
- 在把仓库上下文视为强置信之前,要求有据可依的 change-scope、reproduction 与
  validation 证据。
- 优先使用显式 OpenViking MCP search/read 获取既往 issue 与校验教训;自动
  Codex 捕获保持为 owner 批准的 opt-in。
- 只为某个具体的未解决方面咨询 VikingBot,然后在本地验证。
- PR 存在后,让现有生命周期 monitor 负责 CI、review、stale branch、merge 与
  close 转换。

## 中期

- 通过显式 capability 与 authority 检查投影现有 Codex memory 插件的检索与写
  事件;在 LoopX 中保留紧凑 refs,而不是记忆正文。
- 在已验证 outcome 后添加受控 writeback。用仓库 revision、provenance、
  freshness 与取代关系存储蒸馏出的可复用事实。
- 为 VikingBot 添加只读专家 connector,带针对性问题、超时/失败行为与必须的
  仓库验证结果。
- 把 CI 失败、review 修正、被拒 PR 与 merged outcome 转成 successor todos 与
  可复用的 issue-fix 教训。

## 长期

- 构建 revision 感知的仓库知识,可以取代过时概念,并区分稳定架构与 issue 局部
  观测。
- 用可复现性、校验成本、维护者活跃度、预期范围与权限风险给 issue 排序。
- 在"有无累积仓库知识"的 agent 之间比较:首次有效复现时间、首次 review
  接受率、返工轮数与被搁置 PR 数。
- 为成熟的交换格式添加 import/export,而不把运行时决策耦合到文档布局。

## Open Knowledge Format

Google 宣布了
[Open Knowledge Format](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing),
一种可移植的 Markdown 与 YAML-frontmatter 知识包。当前
[OKF v0.1 规范](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
明确是草稿:概念身份基于路径,Markdown 链接构成图,`index.md` 与 `log.md`
支持渐进披露与历史。

这对 LoopX 作为仓库知识的交换与导出形式有帮助。它不替代检索、trust、
freshness、权限、issue 路由或领域状态转换。因此近期契约接受通用
`knowledge_bundle` 源 ref 并保持格式无关。只有当真实 producer 与 consumer
需要它、且草稿足够稳定值得兼容工作时,才添加具体 OKF importer。

## 试点成功信号

- 从 issue 进入到一个命名复现路径的时间;
- 带 grounded 校验证据的修复路由比例;
- 专家答案被仓库源验证或反驳的频率;
- PR review 轮次与 CI 恢复时间;
- 跨 issue 避免的重复仓库读取;
- 在陈旧记忆影响 patch 之前被发现;
- issue-fix loops 以 merge、有用评论或显式 no-follow-up 结束,而不是静默徘徊在
  monitor-only 漂移。
