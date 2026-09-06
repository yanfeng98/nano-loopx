# 什么是好的 Smoke


Smoke 是对已交付公开路径的一次轻量、可执行验证，用来证明该路径仍遵守稳定不变量。
它不能替代单元测试，也不应成为所有字段的快照或某次成功运行的档案。

## 从合同开始

只有当 smoke 至少保护以下一种表面时，才值得长期保留：已交付的 CLI 或跨模块运行时
行为、可复用的公开合同、公开/私有或权限边界、曾让自动化卡住的回归，或小型测试无法
覆盖的代表性端到端 fixture。

先写清不变量，再写脚本。纯规则的决策表和非法状态应放在 `tests/`；只有真实 CLI、
序列化、状态或进程边界能提供额外证据时，才增加 smoke。

## 审阅清单

| 问题 | 好的证据 | 风险信号 |
| --- | --- | --- |
| 语义 oracle 是什么？ | 期望结果来自独立审阅的规则或协议。 | 脚本把当前输出复制成期望值，或每次变更都刷新 golden。 |
| 验证了什么边界？ | 测试调用已交付入口并断言少量语义结果。 | 只调用内部 helper，却声称覆盖 CLI 或端到端行为。 |
| 结果是否确定？ | 合成 fixture、fake clock、显式状态和有界重试保证可重复。 | 墙钟速度、网络运气、provider 文本或进程顺序决定语义成败。 |
| 断言是否稳定？ | 断言状态转换、权限规则、边界决策或终止条件。 | 固化偶然字段顺序、过期文案、临时 builder 形状或输出 tail。 |
| fixture 是否公开安全？ | 稳定合成 id、reason code、digest 和脱敏 projection 已足够。 | 依赖原始任务、trajectory、日志、verifier 输出、凭证、私有链接或宿主路径。 |
| 是否有 owner 和运行频率？ | 本地聚焦运行，并归入合适的 PR、canary、daily 或 release 通道。 | 所有 smoke 都进入 PR-fast，或高风险表面只有 daily 覆盖且没有定向 profile。 |

墙钟限制可以保护明确的性能预算，但耗时不应决定状态转换或安全规则是否正确。此类
判断应使用 fake clock 或从语义推导的 fixture；真实 provider 检查应保持显式且低频。

## 优先验证语义压力

对于具有优先级或权限语义的规则，单一 happy path 通常不够。应增加最小的反例、
mutation 或 metamorphic case，使关键规则一旦被反转就会失败。例如：无关 gate 不应
改变选中的 agent，底层兼容字段不能覆盖最终 scheduler 权限，重复 receipt 不能重复
产生 effect。

只断言证明该不变量所需的字段。形状与脱敏检查仍有价值，但不能替代语义 oracle。

## 合并时不丢失覆盖

名称相似或 setup 相同，并不能证明两个 smoke 保护同一合同。删除或合并前：

1. 写一句话说明每个候选 smoke 拥有的不变量；
2. 指明其公开入口、反例、运行频率和定向 profile；
3. 把内容完全相同的重复和直接嵌套执行当作审阅候选，而不是自动删除指令；
4. 当共享 fixture 或 subprocess setup 能减少重复、且不合并不同语义断言时，抽取到现有
   canary harness；
5. 移除 smoke 到 smoke 的 wrapper 子进程调用，让每个受跟踪合同只运行一次且仍可独立
   选择；
6. 重跑聚焦条目以及 fleet/catalog 检查，证明清单没有覆盖缺口。

仓库中的 smoke-fleet health 工作 [#2259](https://github.com/huangruiteng/loopx/pull/2259)
确立了“只生成审阅候选”的规则；scheduler 清理 [#2265](https://github.com/huangruiteng/loopx/pull/2265)
移除了嵌套执行，同时保留独立 qualification profile；todo 清理
[#2115](https://github.com/huangruiteng/loopx/pull/2115) 展示了互补做法：共享 harness
基础设施，但保留每个 smoke 的合同。

不要仅因 integrated smoke 很慢就删除它。应先测量成本来自哪些阶段，并证明较小测试
覆盖同一端到端边界；只要它仍提供独有证据，就应保留。

## 公开安全 Fixture

使用临时仓库、fake transport、合成记录和紧凑 receipt。确定性地清理进程与临时状态，
不要把 stdout/stderr tail 提交进 fixture。Fake provider 可以验证序列化、脱敏和
fail-closed，但不能证明真实 provider 行为合格。

当 smoke 接触 benchmark、host、agent 或外部系统数据时，遵循
[公开/私有边界](../public-private-boundary.md)。

## 验证变更

先运行最小且有意义的检查，再根据风险扩大覆盖：

```bash
python examples/<area>/<focused>-smoke.py
loopx canary premerge --from-git-diff
loopx check --scan-path examples/ --scan-path tests/ --scan-path docs/development/
git diff --check
```

报告实际运行的命令、失败或跳过项、manual hold，以及为什么这些证据足以覆盖变更面。
完整 smoke 分层与发布门禁见 [Testing and quality](testing-and-quality.md)。
