# Smoke 失败分类台账


本台账在改动运行时代码之前记录公开 smoke 套件失败。它的职责是把产品 bug 与过时的 smoke 假设、打包缺口和 runner 易用性问题区分开。

当 `loopx canary smoke-suite --suite full-public` 变红时使用此工作流:

1. 用默认安装的 `loopx` 发布快照复现。
2. 用源工作树的 `loopx-canary` 复现。
3. 按负责界面与疑似根因对每个失败的公开脚本分类。
4. 只有在脚本被分类后才修复产品代码。
5. 把基准 runner 执行与原始基准 evidence 保留在本台账之外;只记录公开脚本名、命令与紧凑的失败类别。

## 2026-07-03 高信号控制面批次

运行选择的真相源是 canary smoke-suite runner。一个完整的 `full-public` 运行已开始但超过了心跳尺度的有界批次,因此本条使用模块范围运行来覆盖已知的高信号红色簇:

```bash
loopx canary smoke-suite --suite full-public --module active-state --timeout-seconds 45 --no-progress
loopx canary smoke-suite --suite full-public --module blocker --timeout-seconds 45 --no-progress
loopx canary smoke-suite --suite full-public --module derived-state --timeout-seconds 45 --no-progress
loopx canary smoke-suite --suite full-public --module protocol-action --timeout-seconds 45 --no-progress
loopx canary smoke-suite --suite full-public --module session-runtime --timeout-seconds 45 --no-progress
```

同一模块集合用源工作树的 `loopx-canary` 重跑,以区分发布快照打包失败与源失败。

| 脚本 | 默认发布 | 源工作树 | 负责界面 | 分类 | 优先级 | 下一步修复 |
| --- | --- | --- | --- | --- | --- | --- |
| `examples/control_plane/active-state-interface-budget-smoke.py` | 红 | 绿 | release snapshot smoke 上下文 | 打包/runner 上下文缺口。安装的发布不是 git checkout,但 smoke 通过 shell 调用 `git ls-files`。 | P2 | 让 smoke 容忍发布快照,或只在 checkout 中运行 git 专属断言。 |
| `examples/session_runtime/session-runtime-control-plane-adapter-doc-smoke.py` | 红 | 绿 | 发布打包 / 文档依赖 | 打包缺口。安装的发布不包含 `docs/development/contributor-tasks.md`,而源 checkout 包含。 | P2 | 要么随发布快照安装贡献者任务文档,要么让 smoke 使用随附的发布文档。 |
| `examples/blocker-push-runtime-smoke.py` | 红 | 红 | 配额/状态 blocker-push 运行时 | 产品/契约回归。Blocker-push 路径现在包含 fixture 未接受的公开安全省略警告与投影元数据。 | P1 | 检查新警告字段是否有意为之;然后更新运行时契约或 fixture 期望。 |
| `examples/derived-state-boundary-smoke.py` | 红 | 红 | 状态/项目资产 todo 投影 | 产品/契约回归。有界派生 state 可见性计数与认领 todo 车道相对文档化投影预算发生了变化。 | P1 | 在广泛的配额/状态重构前,把 `project_asset_todo_summary` 与有界派生 state 契约调和。 |
| `examples/protocol/protocol-action-packet-router-comparison-smoke.py` | 红 | 红 | 协议动作包 / router 比较 | 契约或陈旧 fixture 不匹配。确定性比较不再在全部场景中保留所有必需事实/动作清晰度。 | P2 | 决定该冷路径比较是否仍是当前契约;若是,修复 router fixture 或包投影。 |

## Runner 发现

当前完整的 `full-public` 套件没有实际的心跳尺度墙钟上限。模块范围运行可用于开发,但完整套件在它成为默认自主 gate 之前需要以下其一:

- 带部分结果 JSON 的全局套件超时;
- 可恢复的模块/脚本批次计划;
- 或由 runner 自身生成的持久失败台账。

在那之前,自主产品能力 Turn 应使用模块范围的 `full-public` 运行进行分类,并把完整清扫保留给显式的发布就绪度检查。
